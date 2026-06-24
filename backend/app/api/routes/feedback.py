from __future__ import annotations

from datetime import timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.application.classification import effective_primary_category
from app.db.models import Post, PostCategory, PostFeedback, PostProjection
from app.schemas.responses import (
    FeedbackRecentItem,
    FeedbackRequest,
    FeedbackResponse,
    FeedbackCategorySummary,
)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

VALID_VOTES = {"useful", "useless", "feedback"}
VALID_REASONS = {
    "not_activity",
    "expired",
    "wrong_category",
    "other",
    "",
}


def _normalize_client_id(client_id: str) -> str:
    return client_id.strip()[:128]


def _resolve_categories(db: Session, post_ids: set[int]) -> dict[int, str]:
    """Map each post_id to its effective primary category code."""
    if not post_ids:
        return {}
    projections: dict[int, str] = {}
    for post_id, primary in db.execute(
        select(PostProjection.post_id, PostProjection.primary_category)
        .where(PostProjection.post_id.in_(post_ids))
    ).all():
        projections[post_id] = primary or ""
    cats_by_post: dict[int, list[str]] = {}
    for post_id, code in db.execute(
        select(PostCategory.post_id, PostCategory.category_code)
        .where(PostCategory.post_id.in_(post_ids))
    ).all():
        cats_by_post.setdefault(post_id, []).append(code)
    return {
        pid: effective_primary_category(str(projections.get(pid, "")), cats_by_post.get(pid, []))
        for pid in post_ids
    }


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    vote = (payload.vote or "").strip()
    if vote not in VALID_VOTES:
        return FeedbackResponse(received=False, vote=vote, source_name="")

    reason = (payload.reason or "").strip()
    if reason not in VALID_REASONS:
        reason = "other"

    post = db.query(Post).filter(Post.id == payload.post_id).first()
    source_id = post.source_id if post else None
    source_name = post.source_name_snapshot if post else ""

    feedback = PostFeedback(
        client_token=_normalize_client_id(payload.client_id),
        post_id=payload.post_id if post else None,
        source_id=source_id,
        source_name=source_name,
        vote=vote,
        reason=reason,
        comment=(payload.comment or "").strip()[:2000],
    )
    db.add(feedback)
    db.commit()
    return FeedbackResponse(received=True, vote=vote, source_name=source_name)


@router.delete("", response_model=FeedbackResponse)
async def delete_feedback(
    client_id: str = Query(..., min_length=1),
    post_id: int = Query(...),
    vote: str = Query(...),
    db: Session = Depends(get_db),
):
    """Remove a client's previous feedback record (used to undo a vote)."""
    normalized = _normalize_client_id(client_id)
    rows = (
        db.query(PostFeedback)
        .filter(
            PostFeedback.client_token == normalized,
            PostFeedback.post_id == post_id,
            PostFeedback.vote == vote,
        )
        .all()
    )
    for row in rows:
        db.delete(row)
    db.commit()
    return FeedbackResponse(received=True, vote=vote, source_name="")


@router.delete("/{feedback_id}", response_model=FeedbackResponse)
async def delete_feedback_by_id(feedback_id: int, db: Session = Depends(get_db)):
    """Manually delete a single feedback record by its primary key (admin)."""
    row = db.query(PostFeedback).filter(PostFeedback.id == feedback_id).first()
    if not row:
        return FeedbackResponse(received=False, vote="", source_name="")
    db.delete(row)
    db.commit()
    return FeedbackResponse(received=True, vote=row.vote, source_name=row.source_name)


@router.get("/summary", response_model=list[FeedbackCategorySummary])
async def feedback_summary(db: Session = Depends(get_db)):
    rows = db.query(PostFeedback).filter(PostFeedback.post_id.is_not(None)).all()
    post_ids = {row.post_id for row in rows}
    cat_map = _resolve_categories(db, post_ids)

    grouped: dict[str, FeedbackCategorySummary] = {}
    for row in rows:
        category = cat_map.get(row.post_id, "other")
        entry = grouped.setdefault(category, FeedbackCategorySummary(category=category))
        if row.vote == "useful":
            entry.useful += 1
        elif row.vote == "useless":
            entry.useless += 1
        elif row.vote == "feedback":
            entry.feedback += 1
        if row.reason:
            entry.reasons[row.reason] = entry.reasons.get(row.reason, 0) + 1

    order = {category: index for index, category in enumerate(
        ["campus_activity", "competition", "volunteer", "exam_certification", "recruitment", "lecture", "graduate_study", "other"]
    )}
    return sorted(
        grouped.values(),
        key=lambda item: order.get(item.category, 99),
    )


@router.get("/recent", response_model=list[FeedbackRecentItem])
async def feedback_recent(
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PostFeedback)
        .order_by(desc(PostFeedback.created_at), desc(PostFeedback.id))
        .limit(limit)
        .all()
    )
    post_ids = {row.post_id for row in rows if row.post_id is not None}
    post_map = {}
    if post_ids:
        for post in db.query(Post).filter(Post.id.in_(post_ids)).all():
            post_map[post.id] = post
    cat_map = _resolve_categories(db, post_ids)

    items = []
    for row in rows:
        post = post_map.get(row.post_id)
        created_at = row.created_at
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        items.append(
            FeedbackRecentItem(
                id=row.id,
                post_id=row.post_id,
                source_name=row.source_name,
                vote=row.vote,
                reason=row.reason,
                comment=row.comment,
                created_at=created_at,
                post_title=post.title if post else "",
                post_summary=(post.llm_summary or post.summary) if post else "",
                post_url=post.original_url if post else "",
                post_category=cat_map.get(row.post_id, "") if row.post_id else "",
            )
        )
    return items
