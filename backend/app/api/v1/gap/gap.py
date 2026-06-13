from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database.session import get_db
from app.services.gap_analysis_service import GapAnalysisService
from app.models.gap_analysis import GapAnalysis
from app.schemas.gap_analysis import GapAnalysisRequest, GapAnalysisResponse, GapAnalysisSchema
from loguru import logger

router = APIRouter()

def get_gap_service(db: AsyncSession = Depends(get_db)):
    return GapAnalysisService(db)

@router.post("/analyze", response_model=GapAnalysisResponse)
async def analyze_gap(
    request: GapAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    service: GapAnalysisService = Depends(get_gap_service)
):
    """
    Performs gap analysis between a resume and a job description.
    """
    try:
        # Using dummy user_id for development
        dummy_user_id = UUID("00000000-0000-0000-0000-000000000000")
        
        report = await service.analyze_gap(request.resume_id, request.job_id, dummy_user_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume or Job Description not found"
            )
            
        analysis_schema = GapAnalysisSchema(
            matched_skills=report.matched_skills or [],
            missing_skills=report.missing_skills or [],
            matched_keywords=report.matched_keywords or [],
            missing_keywords=report.missing_keywords or [],
            relevant_projects=report.relevant_projects or [],
            relevant_experience=report.relevant_experience or [],
            strengths=report.strengths or [],
            weaknesses=report.weaknesses or [],
            coverage_score=report.coverage_score,
            ats_score=report.ats_score,
            optimization_recommendations=report.recommendations or []
        )
        
        return GapAnalysisResponse(
            id=report.id,
            resume_id=report.resume_id,
            job_id=report.job_id,
            user_id=report.user_id,
            analysis=analysis_schema,
            created_at=report.created_at
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Gap Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{report_id}", response_model=GapAnalysisResponse)
async def get_gap_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a previously generated gap analysis report.
    """
    result = await db.execute(select(GapAnalysis).where(GapAnalysis.id == report_id))
    report = result.scalars().first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gap Analysis report not found"
        )
        
    analysis_schema = GapAnalysisSchema(
        matched_skills=report.matched_skills or [],
        missing_skills=report.missing_skills or [],
        matched_keywords=report.matched_keywords or [],
        missing_keywords=report.missing_keywords or [],
        relevant_projects=report.relevant_projects or [],
        relevant_experience=report.relevant_experience or [],
        strengths=report.strengths or [],
        weaknesses=report.weaknesses or [],
        coverage_score=report.coverage_score,
        ats_score=report.ats_score,
        optimization_recommendations=report.recommendations or []
    )
    
    return GapAnalysisResponse(
        id=report.id,
        resume_id=report.resume_id,
        job_id=report.job_id,
        user_id=report.user_id,
        analysis=analysis_schema,
        created_at=report.created_at
    )
