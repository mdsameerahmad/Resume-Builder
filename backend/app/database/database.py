from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from loguru import logger
import asyncio
from sqlalchemy import create_engine, text

# Async Engine for PostgreSQL
# Use DATABASE_URL for the main application connection
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=10,  # Connection pooling
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    connect_args={
        "timeout": 10,  # Connection timeout
    }
)

# Async Session Local
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Direct Engine for Alembic migrations (if needed, using DIRECT_URL)
# Alembic typically needs a synchronous engine for its operations
# This is a common pattern when using async for the application
# and sync for migrations.
sync_engine = None
if settings.DIRECT_URL:
    sync_engine = create_engine(
        settings.DIRECT_URL,
        echo=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        connect_args={
        "connect_timeout": 10,
    }
    )
    SyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine,
        expire_on_commit=False,
    )

async def check_db_connection():
    """Checks the database connection."""
    try:
        async with async_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Database connection successful!")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Run connection check on startup
async def startup_db_check():
    await check_db_connection()

if __name__ == "__main__":
    # Example of how to run the connection check
    asyncio.run(startup_db_check())
