from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from ..config import get_settings


async def get_show_style_guide(show_id: str) -> str:
    """Fetch the style guide for a show from Postgres."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT style_guide FROM shows WHERE id = :show_id"),
            {"show_id": show_id},
        )
        row = result.fetchone()
    await engine.dispose()
    if row is None:
        return ""
    return str(row[0] or "")


async def get_host_profile(host_id: str) -> dict[str, Any]:
    """Fetch host name, personality prompt, and voice config from Postgres."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT name, personality_prompt, voice_id, voice_provider, temperature, model "
                "FROM hosts WHERE id = :host_id"
            ),
            {"host_id": host_id},
        )
        row = result.fetchone()
    await engine.dispose()
    if row is None:
        return {}
    return {
        "name": row[0],
        "personality_prompt": row[1],
        "voice_id": row[2],
        "voice_provider": row[3],
        "temperature": row[4],
        "model": row[5],
    }
