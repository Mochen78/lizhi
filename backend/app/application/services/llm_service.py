from __future__ import annotations

import json
from datetime import datetime, timezone

import httpx

from app.application.classification import parse_llm_payload
from app.core.config import Settings
from app.domain.enums import LlmStatus


class LlmService:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return bool(
            self.settings.llm_enabled
            and self.settings.llm_base_url
            and self.settings.llm_api_key
            and self.settings.llm_model
        )

    async def summarize_and_extract(self, *, title: str, summary: str, content_text: str) -> dict:
        if not self.enabled:
            return {
                "summary": "",
                "structured": {},
                "status": LlmStatus.NOT_REQUESTED.value,
                "model": "",
                "processed_at": None,
            }

        prompt = (
            "你是校园机会内容抽取助手。"
            "请只输出 JSON，对以下文章生成用于列表浏览的简短摘要，并抽取候选结构化字段。"
            "不要做最终业务判断，不要输出解释。"
            'JSON 字段固定为: summary,is_opportunity,is_recap,event_type,audience,call_to_action,deadline_text,start_time_text,end_time_text,key_evidence。'
        )
        user_input = json.dumps(
            {
                "title": title,
                "summary": summary,
                "content_text": content_text[: self.settings.llm_max_input_chars],
            },
            ensure_ascii=False,
        )
        headers = {
            "Authorization": f"Bearer {self.settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(base_url=self.settings.llm_base_url, timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post("/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        content = ""
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content") or ""
        structured = parse_llm_payload(content)
        return {
            "summary": str(structured.get("summary") or ""),
            "structured": structured,
            "status": LlmStatus.COMPLETED.value if structured else LlmStatus.FAILED.value,
            "model": self.settings.llm_model,
            "processed_at": datetime.now(timezone.utc),
        }
