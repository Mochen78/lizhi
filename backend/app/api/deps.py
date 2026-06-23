from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.orm import Session


async def get_db(request: Request) -> AsyncGenerator[Session, None]:
    db = request.app.state.session_factory()
    try:
        yield db
    finally:
        db.close()
