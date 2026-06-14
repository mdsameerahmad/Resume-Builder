from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import Base
from app.database.database import async_engine
from loguru import logger

async def init_db(db: AsyncSession):
    async with async_engine.begin() as conn:
        # Import all modules that define models so that Base.metadata knows about them
        # This is important for Alembic and for creating tables
        from app.models import user, master_resume, resume_links, job_description, generated_resume, ats_report, gap_analysis, optimized_resume  # noqa
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")
