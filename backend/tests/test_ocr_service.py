from __future__ import annotations

from app.application.services.ocr_service import (
    OCR_ACTION_GENERAL_ACCURATE,
    OCR_ACTION_RECOGNIZE_AGENT,
    OCR_TEXT_MARKER,
    OCR_STATUS_FAILED,
    OCR_STATUS_SKIPPED_LIMIT,
    OCR_STATUS_SUCCESS,
    OcrService,
    _extract_recognize_agent_lines,
    append_ocr_text,
    extract_image_urls_from_raw_post,
)
from app.core.config import Settings
from app.db.models import OcrImageCache, OcrUsageLog
from app.db.session import build_session_factory


class StubOcrClient:
    def __init__(self, text_by_url: dict[str, str]):
        self.text_by_url = text_by_url
        self.urls: list[str] = []
        self.actions: list[str] = []

    def recognize_image_url(self, image_url: str, *, action: str | None = None) -> str:
        self.urls.append(image_url)
        self.actions.append(action or "")
        return self.text_by_url.get(image_url, "")


class FailingOcrClient:
    def __init__(self):
        self.urls: list[str] = []
        self.actions: list[str] = []

    def recognize_image_url(self, image_url: str, *, action: str | None = None) -> str:
        self.urls.append(image_url)
        self.actions.append(action or "")
        raise RuntimeError("provider failed")


def test_extract_image_urls_from_wechat_html():
    raw_post = {
        "url": "https://mp.weixin.qq.com/s/test",
        "content_html": """
        <section>
          <img data-src="//mmbiz.qpic.cn/mmbiz_png/a/0?wx_fmt=png" />
          <img src="https://example.com/static/post.jpg" />
          <img src="data:image/png;base64,abc" />
        </section>
        """,
    }

    urls = extract_image_urls_from_raw_post(raw_post)

    assert urls == [
        "https://mmbiz.qpic.cn/mmbiz_png/a/0?wx_fmt=png",
        "https://example.com/static/post.jpg",
    ]


def test_ocr_service_appends_text_only_for_short_image_posts():
    settings = Settings(ocr_enabled=True, ocr_min_text_length=20, ocr_max_images_per_post=1)
    image_url = "https://example.com/post.jpg"
    client = StubOcrClient({image_url: "志愿者招募 报名入口"})
    service = OcrService(settings, client=client)
    raw_post = {"content_html": f'<section><img src="{image_url}" /></section>'}

    result = service.maybe_append_ocr_text(raw_post, "短文")

    assert client.urls == [image_url]
    assert result.processed_count == 1
    assert OCR_TEXT_MARKER in result.content_text
    assert "志愿者招募" in result.content_text


def test_ocr_service_skips_long_text_even_with_images():
    settings = Settings(ocr_enabled=True, ocr_min_text_length=5)
    client = StubOcrClient({"https://example.com/post.jpg": "不应调用"})
    service = OcrService(settings, client=client)
    raw_post = {"content_html": '<img src="https://example.com/post.jpg" />'}

    result = service.maybe_append_ocr_text(raw_post, "这是一段足够长的正文")

    assert client.urls == []
    assert result.content_text == "这是一段足够长的正文"


def test_append_ocr_text_keeps_source_marker():
    content_text = append_ocr_text("", "讲座论坛 报名方式")

    assert content_text.startswith(OCR_TEXT_MARKER)
    assert "讲座论坛" in content_text


def test_ocr_service_reuses_cached_image_text(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-cache.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
    )
    _, session_factory = build_session_factory(settings)
    image_url = "https://example.com/post.jpg"
    raw_post = {"id": "P001", "content_html": f'<img src="{image_url}" />'}

    first_client = StubOcrClient({image_url: "社团招新报名"})
    first_service = OcrService(settings, client=first_client, session_factory=session_factory)
    first = first_service.maybe_append_ocr_text(raw_post, "")

    second_client = StubOcrClient({image_url: "不应再次调用"})
    second_service = OcrService(settings, client=second_client, session_factory=session_factory)
    second = second_service.maybe_append_ocr_text(raw_post, "")

    assert first_client.urls == [image_url]
    assert second_client.urls == []
    assert "社团招新报名" in first.content_text
    assert "社团招新报名" in second.content_text

    db = session_factory()
    try:
        assert db.query(OcrImageCache).count() == 1
        assert db.query(OcrUsageLog).count() == 1
        assert db.query(OcrImageCache).one().status == OCR_STATUS_SUCCESS
    finally:
        db.close()


def test_ocr_service_monthly_limit_skips_extra_images_without_text_warning(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-limit.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
        ocr_max_images_per_post=2,
        ocr_monthly_limit=1,
        ocr_fallback_monthly_limit=0,
    )
    _, session_factory = build_session_factory(settings)
    first_url = "https://example.com/one.jpg"
    second_url = "https://example.com/two.jpg"
    raw_post = {"content_html": f'<img src="{first_url}" /><img src="{second_url}" />'}
    client = StubOcrClient({first_url: "第一张图文字", second_url: "第二张图文字"})
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text(raw_post, "")

    assert client.urls == [first_url]
    assert "第一张图文字" in result.content_text
    assert "第二张图文字" not in result.content_text
    assert "monthly OCR limit reached" not in result.content_text
    assert OCR_STATUS_SKIPPED_LIMIT not in result.content_text

    db = session_factory()
    try:
        assert db.query(OcrUsageLog).count() == 1
        statuses = sorted(row.status for row in db.query(OcrImageCache).all())
        assert statuses == [OCR_STATUS_SKIPPED_LIMIT, OCR_STATUS_SUCCESS]
    finally:
        db.close()


def test_ocr_service_failed_attempt_can_consume_monthly_limit_without_error_text(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-fail.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
        ocr_max_images_per_post=2,
        ocr_monthly_limit=1,
        ocr_fallback_monthly_limit=0,
        ocr_count_failed_attempts=True,
    )
    _, session_factory = build_session_factory(settings)
    first_url = "https://example.com/one.jpg"
    second_url = "https://example.com/two.jpg"
    raw_post = {"content_html": f'<img src="{first_url}" /><img src="{second_url}" />'}
    client = FailingOcrClient()
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text(raw_post, "")

    assert client.urls == [first_url]
    assert result.content_text == ""
    assert "provider failed" not in result.content_text

    db = session_factory()
    try:
        assert db.query(OcrUsageLog).count() == 1
        statuses = sorted(row.status for row in db.query(OcrImageCache).all())
        assert statuses == [OCR_STATUS_FAILED, OCR_STATUS_SKIPPED_LIMIT]
    finally:
        db.close()


def test_ocr_service_blocks_unsupported_action(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-action.db').as_posix()}",
        ocr_enabled=True,
        ocr_action="GeneralBasicOCR",
        ocr_min_text_length=20,
    )
    _, session_factory = build_session_factory(settings)
    image_url = "https://example.com/post.jpg"
    client = StubOcrClient({image_url: "不应调用"})
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text({"content_html": f'<img src="{image_url}" />'}, "")

    assert client.urls == []
    assert result.content_text == ""


def test_recognize_agent_response_parser_extracts_full_text_lines():
    payload = {
        "Response": [
            {
                "TextDetections": [
                    {"DetectedText": "舞台招募"},
                    {"DetectedText": "截止日期：2026.3.20"},
                ]
            }
        ],
        "RequestId": "test",
    }

    assert _extract_recognize_agent_lines(payload) == ["舞台招募", "截止日期：2026.3.20"]


def test_ocr_service_switches_to_fallback_when_primary_limit_reached(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-fallback.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
        ocr_max_images_per_post=2,
        ocr_monthly_limit=1,
        ocr_fallback_monthly_limit=1,
        ocr_action=OCR_ACTION_GENERAL_ACCURATE,
        ocr_fallback_action=OCR_ACTION_RECOGNIZE_AGENT,
    )
    _, session_factory = build_session_factory(settings)
    first_url = "https://example.com/one.jpg"
    second_url = "https://example.com/two.jpg"
    raw_post = {"content_html": f'<img src="{first_url}" /><img src="{second_url}" />'}
    client = StubOcrClient({first_url: "第一张图文字", second_url: "第二张图文字"})
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text(raw_post, "")

    assert client.urls == [first_url, second_url]
    assert client.actions == [OCR_ACTION_GENERAL_ACCURATE, OCR_ACTION_RECOGNIZE_AGENT]
    assert "第一张图文字" in result.content_text
    assert "第二张图文字" in result.content_text

    db = session_factory()
    try:
        usage = sorted((row.ocr_action, row.status) for row in db.query(OcrUsageLog).all())
        assert usage == [
            (OCR_ACTION_GENERAL_ACCURATE, OCR_STATUS_SUCCESS),
            (OCR_ACTION_RECOGNIZE_AGENT, OCR_STATUS_SUCCESS),
        ]
    finally:
        db.close()


def test_ocr_service_reuses_cache_across_actions(tmp_path):
    from hashlib import sha256

    from app.application.services.ocr_service import current_ocr_month_key, hash_image_url

    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-xcache.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
        ocr_monthly_limit=1,
        ocr_fallback_monthly_limit=1,
        ocr_action=OCR_ACTION_GENERAL_ACCURATE,
        ocr_fallback_action=OCR_ACTION_RECOGNIZE_AGENT,
    )
    _, session_factory = build_session_factory(settings)
    image_url = "https://example.com/post.jpg"
    raw_post = {"id": "P010", "content_html": f'<img src="{image_url}" />'}

    # Seed a SUCCESS cache row under the primary model directly, and exhaust the
    # primary quota so a cache miss would otherwise route to the fallback model.
    month_key = current_ocr_month_key()
    db = session_factory()
    try:
        db.add(
            OcrImageCache(
                image_url_hash=hash_image_url(image_url),
                image_url=image_url,
                ocr_action=OCR_ACTION_GENERAL_ACCURATE,
                status=OCR_STATUS_SUCCESS,
                ocr_text="已被主模型识别",
                month_key=month_key,
                upstream_post_id="P010",
            )
        )
        db.add(
            OcrUsageLog(
                image_url_hash=sha256(b"other").hexdigest(),
                image_url="https://example.com/other.jpg",
                ocr_action=OCR_ACTION_GENERAL_ACCURATE,
                status=OCR_STATUS_SUCCESS,
                month_key=month_key,
                upstream_post_id="",
            )
        )
        db.commit()
    finally:
        db.close()

    client = StubOcrClient({image_url: "不应调用备用模型"})
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text(raw_post, "")

    assert client.urls == []
    assert "已被主模型识别" in result.content_text
    assert "不应调用备用模型" not in result.content_text


def test_ocr_service_skips_when_both_models_exhausted(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-both.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
        ocr_max_images_per_post=2,
        ocr_monthly_limit=0,
        ocr_fallback_monthly_limit=0,
        ocr_action=OCR_ACTION_GENERAL_ACCURATE,
        ocr_fallback_action=OCR_ACTION_RECOGNIZE_AGENT,
    )
    _, session_factory = build_session_factory(settings)
    first_url = "https://example.com/one.jpg"
    second_url = "https://example.com/two.jpg"
    raw_post = {"content_html": f'<img src="{first_url}" /><img src="{second_url}" />'}
    client = StubOcrClient({first_url: "第一张图文字", second_url: "第二张图文字"})
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text(raw_post, "")

    assert client.urls == []
    assert result.content_text == ""

    db = session_factory()
    try:
        statuses = sorted(row.status for row in db.query(OcrImageCache).all())
        assert statuses == [OCR_STATUS_SKIPPED_LIMIT, OCR_STATUS_SKIPPED_LIMIT]
        assert db.query(OcrUsageLog).count() == 0
    finally:
        db.close()


def test_ocr_service_disabled_fallback_uses_primary_only(tmp_path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'ocr-nofb.db').as_posix()}",
        ocr_enabled=True,
        ocr_min_text_length=20,
        ocr_max_images_per_post=2,
        ocr_monthly_limit=1,
        ocr_fallback_action="",
        ocr_action=OCR_ACTION_GENERAL_ACCURATE,
    )
    _, session_factory = build_session_factory(settings)
    first_url = "https://example.com/one.jpg"
    second_url = "https://example.com/two.jpg"
    raw_post = {"content_html": f'<img src="{first_url}" /><img src="{second_url}" />'}
    client = StubOcrClient({first_url: "第一张图文字", second_url: "第二张图文字"})
    service = OcrService(settings, client=client, session_factory=session_factory)

    result = service.maybe_append_ocr_text(raw_post, "")

    assert client.urls == [first_url]
    assert client.actions == [OCR_ACTION_GENERAL_ACCURATE]
    assert "第一张图文字" in result.content_text
    assert "第二张图文字" not in result.content_text
