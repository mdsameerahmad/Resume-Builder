from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database.session import get_db
from app.services.jd_analyzer import JDAnalyzer
from app.models.job_description import JobDescription
from app.schemas.job_description import JDBase, JDAnalysisResponse, JDResponse
from loguru import logger

from app.models.user import User

router = APIRouter()

def get_analyzer_service(db: AsyncSession = Depends(get_db)):
    return JDAnalyzer(db)

async def ensure_mock_user(db: AsyncSession) -> UUID:
    """Ensures a mock user exists for development purposes."""
    mock_id = UUID("00000000-0000-0000-0000-000000000000")
    result = await db.execute(select(User).where(User.id == mock_id))
    user = result.scalars().first()
    if not user:
        user = User(
            id=mock_id,
            email="mock@example.com",
            password_hash="mock",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created mock user: {mock_id}")
    return mock_id

@router.post("/analyze", response_model=JDAnalysisResponse)
async def analyze_job_description(
    jd_data: JDBase,
    db: AsyncSession = Depends(get_db),
    service: JDAnalyzer = Depends(get_analyzer_service)
):
    """
    Analyzes a raw Job Description and returns structured ATS metadata.
    """
    try:
        # Ensure dummy user exists for foreign key constraint
        user_id = await ensure_mock_user(db)
        
        # Analyze and store JD
        response = await service.analyze_jd(jd_data.job_description, user_id)
        
        return response
    except Exception as e:
        logger.error(f"JD Analysis error: {e}")
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{job_id}", response_model=JDResponse)
async def get_parsed_jd(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a previously analyzed Job Description.
    """
    result = await db.execute(select(JobDescription).where(JobDescription.id == job_id))
    jd = result.scalars().first()
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job Description not found"
        )
    return jd

@router.get("/user/all", response_model=List[JDResponse])
async def get_all_user_jds(
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves all Job Descriptions for the current user.
    """
    dummy_user_id = UUID("00000000-0000-0000-0000-000000000000")
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == dummy_user_id)
        .order_by(JobDescription.created_at.desc())
    )
    return result.scalars().all()
