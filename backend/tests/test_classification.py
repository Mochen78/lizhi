from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.application.classification import (
    classify_categories,
    classify_content_type,
    compute_ranking_score,
    derive_display_level,
    derive_participation_status,
    derive_time_status,
    extract_time_signals,
    prescreen_post,
)
from app.domain.enums import ContentType, ParticipationStatus, TimeStatus, TimelinessLevel


def test_prescreen_recap_hits_with_multiple_signals():
    decision = prescreen_post(
        title="活动回顾 | 校园志愿服务精彩回顾",
        summary="让我们一起回顾本次活动的精彩瞬间",
        source_name="校园服务中心",
    )
    assert decision.discard is True
    assert decision.reason == "recap"


def test_prescreen_tutorial_blocks_even_with_action_word():
    decision = prescreen_post(
        title="报名教程：手把手教你如何进行申请",
        summary="第一步注册，第二步提交材料",
        source_name="学院通知",
    )
    assert decision.discard is True
    assert decision.reason == "tutorial"


def test_prescreen_garbled_hidden_source_blocks_noise():
    decision = prescreen_post(
        title="锟斤拷锟斤拷x9A@@",
        summary="",
        source_name="",
    )
    assert decision.discard is True
    assert decision.reason == "garbled_hidden_source"


def test_prescreen_does_not_block_normal_english_title():
    decision = prescreen_post(
        title="IEEE AI Hackathon Registration Opens",
        summary="Students may register before May 28.",
        source_name="College Innovation Center",
    )
    assert decision.discard is False


def test_classify_categories_matches_new_taxonomy():
    categories = classify_categories("创新创业比赛报名通知", "面向全校学生开放")
    assert "competition" in categories


def test_classify_content_type_actionable_for_opportunity():
    content_type = classify_content_type("讲座报名通知", "报名截止时间为5月28日")
    assert content_type == ContentType.ACTIONABLE


def test_extract_time_signals_and_status():
    published_at = datetime(2026, 5, 20, tzinfo=timezone.utc)
    signals = extract_time_signals(
        "讲座报名通知",
        "报名截止5月28日18:00，活动时间5月30日",
        "",
        published_at,
    )
    status, timeliness = derive_time_status(signals, now=datetime(2026, 5, 21, tzinfo=timezone.utc))
    assert signals.deadline_at is not None
    assert status == TimeStatus.UPCOMING
    assert timeliness == TimelinessLevel.NORMAL


def test_participation_and_display_for_actionable_content():
    participation = derive_participation_status(
        content_type=ContentType.ACTIONABLE,
        time_status=TimeStatus.UPCOMING,
        text="面向全校学生开放报名，截止本周五",
    )
    display_level = derive_display_level(ContentType.ACTIONABLE, TimelinessLevel.NORMAL)
    assert participation == ParticipationStatus.PARTICIPABLE
    assert display_level.value == "normal"


def test_compute_ranking_score_rewards_near_deadline():
    now = datetime.now(timezone.utc)
    score = compute_ranking_score(
        participation_status=ParticipationStatus.PARTICIPABLE,
        content_type=ContentType.ACTIONABLE,
        primary_category="competition",
        time_status=TimeStatus.UPCOMING,
        deadline_at=now + timedelta(days=2),
        published_at=now - timedelta(days=1),
        now=now,
    )
    assert score >= 170
