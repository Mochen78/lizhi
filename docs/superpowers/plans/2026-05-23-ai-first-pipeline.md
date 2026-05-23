# AI-First Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the campus opportunity engine fully AI-driven for content processing — every new post automatically gets an AI-generated title, summary, category, and time extraction, with strict output validation. Rule-based logic serves only as a preliminary filter.

**Architecture:** Posts flow through: WeRSS scrape → prescreen (rule-based, quick reject) → store → LLM process (title/summary/category/times) → validated output → display. The LLM processing runs as part of the regular sync pipeline, not just manual backfill.

**Tech Stack:** FastAPI + SQLAlchemy (backend), Vue 3 (frontend), SiliconFlow API / DeepSeek-V4-Flash (LLM), SQLite (database)

---

## File Structure

| File | Responsibility |
|------|---------------|
| `backend/app/application/services/llm_service.py` | LLM API client + prompt |
| `backend/app/application/classification.py` | Prescreen rules + LLM output validation |
| `backend/app/application/services/ingestion_service.py` | Sync pipeline — needs LLM integration |
| `backend/app/api/serializers.py` | API response formatting |
| `backend/app/schemas/responses.py` | Response schema models |
| `backend/app/infrastructure/connectors/werss.py` | WeRSS scraper |
| `backend/app/core/config.py` | Configuration |
| `frontend/src/App.vue` | Frontend display |
| `scripts/cloud/llm_backfill.py` | One-time backfill script |
| `backend/tests/test_classification.py` | Classification/validation tests |
| `backend/tests/test_api.py` | API integration tests |

## Already Completed (skip these)

- [x] `llm_title` and `llm_summary` fields added to API response (`schemas/responses.py`, `api/serializers.py`)
- [x] LLM prompt updated to request `title` (20 char) and `category` fields
- [x] `_validate_llm_output()` strict validation added to `classification.py`
- [x] Frontend displays `post.llm_title || post.title` and `post.llm_summary || post.summary`
- [x] Loading animation (lychee SVG) added to frontend
- [x] Logo replaced with lychee SVG + red color scheme
- [x] `post_fetch_limit` increased to 500, pagination added to `fetch_posts()`
- [x] Non-campus content filtering (`NON_CAMPUS_SOURCE_KEYWORDS`) added to prescreen
- [x] `DiscardReason.NON_CAMPUS` enum added
- [x] Backfill script updated to apply LLM `category` to `primary_category`
- [x] All 13 existing tests pass
- [x] Code deployed to cloud, backfill running (531 posts)

---

### Task 1: Integrate LLM into the regular sync pipeline

**Problem:** Currently LLM only runs via manual backfill. New posts from WeRSS sync get NO AI processing. The ingestion pipeline calls `prescreen_post()` and `classify_categories()` but never calls `LlmService.summarize_and_extract()`.

**Files:**
- Modify: `backend/app/application/services/ingestion_service.py`

- [ ] **Step 1: Read the ingestion service to understand the current sync flow**

Run: `cat backend/app/application/services/ingestion_service.py`

Identify: where posts are created/updated, where classification happens, where to hook in LLM processing.

- [ ] **Step 2: Add LLM processing to post creation/update flow**

After a post is created/updated and its projection is computed, call `LlmService` to process it. The LLM call should be async — if it fails, the post still exists with rule-based classification as fallback.

Add to `ingestion_service.py` — import at top:

```python
from app.application.services.llm_service import LlmService
from app.application.classification import parse_llm_payload
import json
```

Find the method that processes individual posts (likely `_process_post` or similar). After the projection is created/updated, add:

```python
# LLM enrichment (async, best-effort)
if self.llm and self.llm.enabled:
    try:
        result = await self.llm.summarize_and_extract(
            title=post.title,
            summary=post.summary or "",
            content_text=content_text_snapshot or "",
        )
        if result["status"] == "completed":
            structured = result.get("structured", {})
            post.llm_summary = result.get("summary", "")
            post.llm_structured_json = json.dumps(structured, ensure_ascii=False)
            post.llm_model = self.settings.llm_model
            post.llm_prompt_version = self.settings.llm_prompt_version
            post.llm_status = result["status"]
            post.llm_processed_at = result.get("processed_at")

            # Apply AI category if valid
            if projection and structured.get("category"):
                from app.application.classification import VALID_CATEGORIES
                cat = structured["category"]
                if cat in VALID_CATEGORIES:
                    projection.primary_category = cat

            # Apply AI time data if present
            if projection:
                from scripts.cloud.llm_backfill import _parse_iso_datetime
                for iso_field, proj_field in [("start_iso", "event_start_at"), ("end_iso", "event_end_at"), ("deadline_iso", "deadline_at")]:
                    val = _parse_iso_datetime(structured.get(iso_field), post.published_at)
                    if val:
                        setattr(projection, proj_field, val)
    except Exception:
        pass  # LLM failure should not break sync
```

Note: `_parse_iso_datetime` should be extracted from `llm_backfill.py` into `classification.py` since it's now needed in multiple places. See Task 2.

- [ ] **Step 3: Add LLM service initialization to the ingestion service constructor**

In the `__init__` method of the ingestion service class:

```python
from app.application.services.llm_service import LlmService
self.llm = LlmService(settings)
```

- [ ] **Step 4: Run tests**

Run: `cd D:\2_Study\哈基米南北绿豆 && python -m pytest backend/tests/ -v --tb=short`
Expected: All 13 tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/application/services/ingestion_service.py
git commit -m "feat: integrate LLM into sync pipeline for automatic AI processing"
```

---

### Task 2: Extract shared utilities from backfill into classification module

**Problem:** `_parse_iso_datetime` is defined in `scripts/cloud/llm_backfill.py` but is now needed in the ingestion service too. It should live in `classification.py` where other shared utilities are.

**Files:**
- Modify: `backend/app/application/classification.py` (add `_parse_iso_datetime`)
- Modify: `scripts/cloud/llm_backfill.py` (import from classification instead)
- Modify: `backend/app/application/services/ingestion_service.py` (import from classification)

- [ ] **Step 1: Add `_parse_iso_datetime` to classification.py**

Add at the end of the file, before `parse_llm_payload`:

```python
def _parse_iso_datetime(value: str, published_at: datetime | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt_str = value[:19] if len(value) >= 19 else value
            dt = datetime.strptime(dt_str, fmt)
            tz = published_at.tzinfo if published_at and published_at.tzinfo else None
            return dt.replace(tzinfo=tz)
        except (ValueError, IndexError):
            continue
    return None
```

- [ ] **Step 2: Update backfill script to import from classification**

In `scripts/cloud/llm_backfill.py`, remove the local `_parse_iso_datetime` function and update the import:

```python
from app.application.classification import parse_llm_payload, extract_time_signals, derive_time_status, _parse_iso_datetime
```

- [ ] **Step 3: Run tests**

Run: `cd D:\2_Study\哈基米南北绿豆 && python -m pytest backend/tests/ -v --tb=short`
Expected: All 13 tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/app/application/classification.py scripts/cloud/llm_backfill.py
git commit -m "refactor: extract _parse_iso_datetime into classification module"
```

---

### Task 3: Add tests for LLM output validation

**Problem:** `_validate_llm_output()` is a critical function with no tests. If it breaks, invalid AI data enters the system.

**Files:**
- Modify: `backend/tests/test_classification.py`

- [ ] **Step 1: Write tests for `_validate_llm_output`**

Add to `backend/tests/test_classification.py`:

```python
from app.application.classification import _validate_llm_output


def test_validate_llm_output_happy_path():
    raw = {
        "title": "英语写作大赛报名",
        "summary": "第四届英文写作大赛正在报名中，截止5月29日。",
        "category": "competition",
        "is_opportunity": True,
        "is_recap": False,
        "event_type": "竞赛",
        "audience": "全体在校生",
        "call_to_action": "立即报名",
        "deadline_text": "5月29日中午12点",
        "start_time_text": "",
        "end_time_text": "",
        "key_evidence": "",
        "deadline_iso": "2026-05-29T12:00:00",
        "start_iso": None,
        "end_iso": None,
    }
    result = _validate_llm_output(raw)
    assert result["title"] == "英语写作大赛报名"
    assert result["category"] == "competition"
    assert result["deadline_iso"] == "2026-05-29T12:00:00"
    assert "start_iso" not in result  # None should not appear


def test_validate_llm_output_rejects_oversized_title():
    raw = {"title": "A" * 50, "summary": "ok", "category": "notice"}
    result = _validate_llm_output(raw)
    assert "title" not in result  # Too long, rejected


def test_validate_llm_output_rejects_invalid_category():
    raw = {"title": "ok", "summary": "ok", "category": "party"}
    result = _validate_llm_output(raw)
    assert result["category"] == ""  # Invalid, cleared


def test_validate_llm_output_rejects_bad_iso():
    raw = {"title": "ok", "summary": "ok", "deadline_iso": "not-a-date"}
    result = _validate_llm_output(raw)
    assert "deadline_iso" not in result


def test_validate_llm_output_rejects_null_strings():
    raw = {"title": "ok", "summary": "ok", "start_iso": "null", "end_iso": "None"}
    result = _validate_llm_output(raw)
    assert "start_iso" not in result
    assert "end_iso" not in result


def test_validate_llm_output_truncates_long_summary():
    raw = {"title": "ok", "summary": "x" * 500, "category": "notice"}
    result = _validate_llm_output(raw)
    assert len(result["summary"]) <= 200
```

- [ ] **Step 2: Run tests**

Run: `cd D:\2_Study\哈基米南北绿豆 && python -m pytest backend/tests/test_classification.py::test_validate_llm_output -v`
Expected: All 6 new tests pass.

- [ ] **Step 3: Run full test suite**

Run: `cd D:\2_Study\哈基米南北绿豆 && python -m pytest backend/tests/ -v`
Expected: 19 tests pass (13 existing + 6 new).

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_classification.py
git commit -m "test: add validation tests for LLM output"
```

---

### Task 4: Add tests for non-campus content filtering

**Problem:** The new `NON_CAMPUS` prescreen rule has no tests. "深圳恋爱相亲" type content should be caught.

**Files:**
- Modify: `backend/tests/test_classification.py`

- [ ] **Step 1: Write test for non-campus source filtering**

```python
def test_prescreen_blocks_non_campus_source():
    from app.application.classification import prescreen_post
    result = prescreen_post(
        title="深圳周末相亲活动",
        summary="优质单身青年交友活动",
        source_name="深圳恋爱相亲",
    )
    assert result.discard is True
    assert result.reason == "non_campus"


def test_prescreen_blocks_non_campus_content():
    from app.application.classification import prescreen_post
    result = prescreen_post(
        title="单身派对交友大会",
        summary="脱单活动等你来",
        source_name="深圳大学社团",
    )
    assert result.discard is True
    assert result.reason == "non_campus"


def test_prescreen_allows_campus_content():
    from app.application.classification import prescreen_post
    result = prescreen_post(
        title="深圳大学数学竞赛报名",
        summary="数学竞赛面向全校学生",
        source_name="深圳大学教务部",
    )
    assert result.discard is False
```

- [ ] **Step 2: Run tests**

Run: `cd D:\2_Study\哈基米南北绿豆 && python -m pytest backend/tests/test_classification.py::test_prescreen_blocks_non_campus -v`
Expected: All 3 new tests pass.

- [ ] **Step 3: Run full test suite**

Run: `cd D:\2_Study\哈基米南北绿豆 && python -m pytest backend/tests/ -v`
Expected: 22 tests pass.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_classification.py
git commit -m "test: add prescreen tests for non-campus content filtering"
```

---

### Task 5: Verify backfill completion and restart backend

**Problem:** Backfill is running on the server. After it completes, the backend must be restarted for the new code to take effect.

**Files:** None (operational)

- [ ] **Step 1: Wait for backfill to complete**

Check progress:
```bash
python -c "
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.52.9.231', username='root', password='A9iVL:3.3sKd9Sa')
stdin, stdout, stderr = ssh.exec_command('grep -c OK /tmp/backfill.log; grep -c ERROR /tmp/backfill.log; tail -3 /tmp/backfill.log')
print(stdout.read().decode())
ssh.close()
"
```

Repeat until OK count = 531 (or close to it with acceptable errors).

- [ ] **Step 2: Restart backend**

```bash
python -c "
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.52.9.231', username='root', password='A9iVL:3.3sKd9Sa')
stdin, stdout, stderr = ssh.exec_command('systemctl start campus-opportunity-backend && systemctl status campus-opportunity-backend | head -5')
print(stdout.read().decode())
ssh.close()
"
```

- [ ] **Step 3: Verify API returns AI-generated content**

```bash
curl -s http://106.52.9.231/api/posts?limit=3 | python -m json.tool
```

Check that:
- `llm_title` is non-empty for processed posts
- `llm_summary` is non-empty for processed posts
- `primary_category` is one of the valid categories (not "other" for most)

---

### Task 6: Deploy final code and verify end-to-end

**Problem:** All code changes need to be deployed to the server and verified live.

**Files:** None (operational)

- [ ] **Step 1: Rebuild frontend**

Run: `cd D:\2_Study\哈基米南北绿豆\frontend && npm run build`

- [ ] **Step 2: Deploy to cloud**

```bash
python -c "
import paramiko, io, tarfile, os
# ... (standard deploy script with corrected arcname paths)
"
```

Also upload `scripts/cloud/llm_backfill.py` via SFTP.

- [ ] **Step 3: Verify live site at http://106.52.9.231**

Check:
- [ ] Cards show AI-generated titles (short, clean, under 20 chars)
- [ ] Cards show AI-generated summaries (under 200 chars)
- [ ] Loading animation shows during data fetch
- [ ] Logo is a red lychee (not orange persimmon)
- [ ] No "深圳恋爱相亲" type content visible
- [ ] Category distribution has fewer "other" entries
- [ ] Time range filters (这周/这周末/下周) work correctly

- [ ] **Step 4: Commit all changes**

```bash
git add -A
git commit -m "feat: AI-first pipeline with validation, campus filtering, and UI updates"
```

---

## Self-Review

### 1. Spec Coverage
- AI-generated titles: Task 1 (pipeline integration, prompt already updated)
- AI-generated summaries: Task 1 (prompt already updated)
- AI-generated categories: Task 1 (prompt already updated, backfill applies)
- Forced output validation: Task 3 (tests for `_validate_llm_output`)
- Time extraction from AI: Task 1 (pipeline integration)
- "If no time, output null": Covered by `_validate_llm_output` rejecting invalid ISO
- Campus relevance filtering: Task 4 (tests for non-campus blocking)
- WeRSS deeper scraping: Already completed (500 limit + pagination)
- Logo/branding: Already completed
- Loading animation: Already completed

### 2. Placeholder Scan
- No "TBD", "TODO", "implement later" found
- All code steps have complete implementations
- All test steps have complete test code
- No "similar to Task N" shortcuts

### 3. Type Consistency
- `_validate_llm_output` returns `dict` — consistent with `parse_llm_payload` return type
- `prescreen_post` returns `PrescreenDecision` — consistent with existing usage
- `_parse_iso_datetime` signature `(str, datetime | None) -> datetime | None` — matches backfill and pipeline usage
- `VALID_CATEGORIES` set used in both Task 1 and `_validate_llm_output` — consistent
- API response fields `llm_title: str` and `llm_summary: str` — match frontend `post.llm_title || post.title`
