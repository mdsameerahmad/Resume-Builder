from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.session import get_db
from app.services.master_resume_parser import MasterResumeParser
from app.schemas.master_resume import MasterResumeResponse, MasterResumeProfileSchema
from loguru import logger

router = APIRouter()

def get_parser_service(db: AsyncSession = Depends(get_db)):
    return MasterResumeParser(db)

@router.post("/parse/{resume_id}", response_model=MasterResumeResponse)
async def parse_resume_to_master(
    resume_id: UUID,
    service: MasterResumeParser = Depends(get_parser_service)
):
    """
    Generate a Master Resume Profile from extracted resume data using Gemini AI.
    """
    try:
        return await service.parse_to_master(resume_id)
    except Exception as e:
        logger.error(f"Parsing error for {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/master/{resume_id}", response_model=MasterResumeProfileSchema)
async def get_master_profile(
    resume_id: UUID,
    service: MasterResumeParser = Depends(get_parser_service)
):
    """
    Retrieve the Master Resume Profile for a specific resume.
    """
    profile = await service.get_master_profile(resume_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Master Resume Profile not found. Please run parsing first."
        )
    return profile
