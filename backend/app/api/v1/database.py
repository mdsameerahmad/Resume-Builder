from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.database.database import check_db_connection
from app.database.init_db import init_db as initialize_db
from loguru import logger

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def database_health_check():
    """
    Verify database connectivity.
    """
    if await check_db_connection():
        return {"database": "connected", "status": "healthy"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )

@router.post("/init", status_code=status.HTTP_200_OK)
async def initialize_database(db: AsyncSession = Depends(get_db)):
    """
    Initialize all database tables.
    """
    try:
        await initialize_db(db)
        return {"message": "Database tables initialized successfully."}
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize database: {e}"
        )
