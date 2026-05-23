"""Backfill LLM data for all existing posts.

Run on the remote server:
    cd /opt/campus-opportunity/current/backend
    .venv/bin/python -m scripts.cloud.llm_backfill
"""
import asyncio
import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.environ.get("BACKEND_ENV_PATH", "/etc/campus-opportunity/backend.env"))

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.application.services.llm_service import LlmService
from app.application.classification import parse_llm_payload, extract_time_signals, derive_time_status, parse_iso_datetime, VALID_CATEGORIES
from app.db.models import Post, PostProjection
from datetime import datetime, timezone



async def main():
    settings = Settings.from_env()
    llm = LlmService(settings)

    if not llm.enabled:
        print("LLM is not enabled. Check env config.")
        sys.exit(1)

    print(f"LLM enabled: model={settings.llm_model}, base_url={settings.llm_base_url}")

    engine = create_engine(settings.database_url, connect_args={"timeout": 60})

    with Session(engine) as db:
        posts = db.execute(
            select(Post).where(Post.llm_status != "completed")
        ).scalars().all()

        print(f"Posts to process: {len(posts)}")
        success = 0
        failed = 0

        for i, post in enumerate(posts):
            content_text = post.content_text_snapshot or ""
            if not content_text and post.content_html:
                from app.application.classification import html_to_text
                content_text = html_to_text(post.content_html)

            if not content_text:
                print(f"  [{i+1}/{len(posts)}] SKIP (no content): {post.title[:40]}")
                continue

            result = None
            for attempt in range(3):
                try:
                    result = await llm.summarize_and_extract(
                        title=post.title,
                        summary=post.summary,
                        content_text=content_text,
                    )
                    break
                except Exception as e:
                    if attempt < 2:
                        wait = 3 * (attempt + 1)
                        print(f"  [{i+1}/{len(posts)}] RETRY {attempt+1}: {type(e).__name__}, waiting {wait}s...")
                        await asyncio.sleep(wait)
                    else:
                        print(f"  [{i+1}/{len(posts)}] ERROR after 3 retries: {type(e).__name__}: {e}")
                        failed += 1
                        await asyncio.sleep(1)
            if result is None:
                continue

            if result["status"] != "completed":
                print(f"  [{i+1}/{len(posts)}] LLM failed: {result['status']}")
                failed += 1
                await asyncio.sleep(1)
                continue

            structured = result.get("structured", {})
            summary = result.get("summary", "")

            post.llm_summary = summary
            post.llm_structured_json = json.dumps(structured, ensure_ascii=False)
            post.llm_model = settings.llm_model
            post.llm_prompt_version = settings.llm_prompt_version
            post.llm_status = result["status"]
            post.llm_processed_at = result.get("processed_at")

            # Update projection with LLM time data and category
            projection = db.query(PostProjection).filter(PostProjection.post_id == post.id).first()
            if projection:
                llm_category = structured.get("category", "")
                if llm_category in VALID_CATEGORIES:
                    projection.primary_category = llm_category

                llm_start = parse_iso_datetime(structured.get("start_iso"), post.published_at)
                llm_end = parse_iso_datetime(structured.get("end_iso"), post.published_at)
                llm_deadline = parse_iso_datetime(structured.get("deadline_iso"), post.published_at)

                if llm_start:
                    projection.event_start_at = llm_start
                if llm_end:
                    projection.event_end_at = llm_end
                if llm_deadline:
                    projection.deadline_at = llm_deadline

                if llm_start or llm_end or llm_deadline:
                    from app.application.classification import TimeSignals
                    ts = TimeSignals(
                        event_start_at=projection.event_start_at,
                        event_end_at=projection.event_end_at,
                        deadline_at=projection.deadline_at,
                    )
                    time_status, timeliness_level = derive_time_status(ts)
                    projection.time_status = time_status.value
                    projection.timeliness_level = timeliness_level.value

            db.add(post)
            if projection:
                db.add(projection)
            db.commit()
            success += 1

            title_short = post.title[:40]
            print(f"  [{i+1}/{len(posts)}] OK: {title_short}")
            print(f"           summary={summary[:60]}...")

            await asyncio.sleep(1)

    engine.dispose()
    print(f"\nDone. Success: {success}, Failed: {failed}")


if __name__ == "__main__":
    asyncio.run(main())
