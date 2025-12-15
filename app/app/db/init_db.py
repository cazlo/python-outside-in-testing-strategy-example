from sqlmodel.ext.asyncio.session import AsyncSession


async def init_db(db_session: AsyncSession) -> None:
    """
    Initialize database with any required seed data.
    Currently empty as we have no seed data requirements.
    """
    pass
