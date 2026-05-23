from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _as_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    app_name: str = "Campus Feed Backend"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8002
    database_url: str = ""
    sync_interval_minutes: int = 10
    post_fetch_limit: int = 500
    source_fetch_limit: int = 200
    enable_scheduler: bool = True
    upstream_base_url: str = ""
    upstream_username: str = ""
    upstream_password: str = ""
    llm_enabled: bool = False
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    llm_timeout_seconds: int = 30
    llm_prompt_version: str = "iter1-v1"
    llm_max_input_chars: int = 6000

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(Path(__file__).resolve().parents[2] / ".env")
        default_db_path = Path(__file__).resolve().parents[3] / ".run" / "backend.db"
        return cls(
            host=os.getenv("BACKEND_HOST", "0.0.0.0"),
            port=int(os.getenv("BACKEND_PORT", "8002")),
            database_url=os.getenv("BACKEND_DATABASE_URL", f"sqlite:///{default_db_path.as_posix()}"),
            sync_interval_minutes=int(os.getenv("BACKEND_SYNC_INTERVAL_MINUTES", "10")),
            post_fetch_limit=int(os.getenv("BACKEND_POST_FETCH_LIMIT", "500")),
            source_fetch_limit=int(os.getenv("BACKEND_SOURCE_FETCH_LIMIT", "200")),
            enable_scheduler=_as_bool(os.getenv("BACKEND_ENABLE_SCHEDULER"), True),
            upstream_base_url=os.getenv("BACKEND_UPSTREAM_BASE_URL", ""),
            upstream_username=os.getenv("BACKEND_UPSTREAM_USERNAME", ""),
            upstream_password=os.getenv("BACKEND_UPSTREAM_PASSWORD", ""),
            llm_enabled=_as_bool(os.getenv("BACKEND_LLM_ENABLED"), False),
            llm_base_url=os.getenv("BACKEND_LLM_BASE_URL", ""),
            llm_api_key=os.getenv("BACKEND_LLM_API_KEY", ""),
            llm_model=os.getenv("BACKEND_LLM_MODEL", ""),
            llm_timeout_seconds=int(os.getenv("BACKEND_LLM_TIMEOUT_SECONDS", "30")),
            llm_prompt_version=os.getenv("BACKEND_LLM_PROMPT_VERSION", "iter1-v1"),
            llm_max_input_chars=int(os.getenv("BACKEND_LLM_MAX_INPUT_CHARS", "6000")),
        )
