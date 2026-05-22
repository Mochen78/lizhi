from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.serializers import serialize_post, serialize_post_detail
from app.schemas.responses import CategoryStatsResponse, PagedPostsResponse, PostDetailResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=PagedPostsResponse)
def list_posts(
    request: Request,
    category: str = Query(default=""),
    content_type: str = Query(default=""),
    participation_status: str = Query(default=""),
    time_status: str = Query(default=""),
    search: str = Query(default=""),
    source_id: int | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    show_all: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    items, total = request.app.state.query_service.list_posts(
        db,
        category=category,
        content_type=content_type,
        participation_status=participation_status,
        time_status=time_status,
        search=search,
        source_id=source_id,
        offset=offset,
        limit=limit,
        show_all=show_all,
    )
    return PagedPostsResponse(
        items=[serialize_post(item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/categories", response_model=CategoryStatsResponse)
def category_stats(request: Request, db: Session = Depends(get_db)):
    categories, content_type_stats, participation_stats, time_status_stats = request.app.state.query_service.get_category_stats(db)
    return CategoryStatsResponse(
        categories=categories,
        content_type_stats=content_type_stats,
        participation_stats=participation_stats,
        time_status_stats=time_status_stats,
    )


@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = request.app.state.query_service.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    return serialize_post_detail(post)
