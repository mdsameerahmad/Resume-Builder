from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.session import get_db
from app.services.resume_extraction_service import ResumeExtractionService
from app.schemas.extraction import ExtractionResponse
from loguru import logger

router = APIRouter()

def get_extraction_service(db: AsyncSession = Depends(get_db)):
    return ResumeExtractionService(db)

@router.post("/extract/{resume_id}", response_model=ExtractionResponse)
async def extract_resume(
    resume_id: UUID,
    service: ResumeExtractionService = Depends(get_extraction_service)
):
    """
    Extract raw text, links, contact info, and metadata from an uploaded resume.
    """
    try:
        return await service.extract_resume(resume_id)
    except Exception as e:
        logger.error(f"Extraction error for {resume_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/extraction/{resume_id}", response_model=ExtractionResponse)
async def get_extraction(
    resume_id: UUID,
    service: ResumeExtractionService = Depends(get_extraction_service)
):
    """
    Retrieve previously extracted content for a resume.
    """
    extraction = await service.get_extraction(resume_id)
    if not extraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extraction results not found for this resume. Please run extraction first."
        )
    
    # Map model to schema
    return ExtractionResponse(
        resume_id=extraction.resume_id,
        raw_text=extraction.raw_text,
        contact_info=extraction.contact_info,
        links=extraction.extracted_links,
        metadata=extraction.metadata_info,
        sections=extraction.sections
    )
