from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal, SessionLocalCelery


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_jobs_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocalCelery() as session:
        yield session
