from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List
from loguru import logger

from app.database.session import get_db
from app.services.resume_optimizer import ResumeOptimizer
from app.models.optimized_resume import OptimizedResume
from app.schemas.optimized_resume import OptimizeRequest, OptimizeResponse, OptimizedResumeDetailResponse, OptimizedResumeSchema

router = APIRouter()

def get_optimizer_service(db: AsyncSession = Depends(get_db)):
    return ResumeOptimizer(db)

@router.post("/generate", response_model=OptimizeResponse)
async def generate_optimized_resume(
    request: OptimizeRequest,
    db: AsyncSession = Depends(get_db),
    service: ResumeOptimizer = Depends(get_optimizer_service)
):
    """
    Triggers the resume optimization pipeline.
    """
    try:
        # Dummy user_id for development
        dummy_user_id = UUID("00000000-0000-0000-0000-000000000000")
        
        optimized = await service.optimize_resume(request.resume_id, request.job_id, dummy_user_id)
        
        if not optimized:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not generate optimized resume. Ensure Resume, JD, and Gap Analysis exist."
            )
            
        return OptimizeResponse(
            optimized_resume_id=optimized.id,
            optimization_score=optimized.optimization_metadata.get("optimization_score", 0.0),
            created_at=optimized.created_at
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Resume Optimization API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{optimized_id}", response_model=OptimizedResumeDetailResponse)
async def get_optimized_resume(
    optimized_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a previously generated optimized resume.
    """
    result = await db.execute(select(OptimizedResume).where(OptimizedResume.id == optimized_id))
    optimized = result.scalars().first()
    
    if not optimized:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimized resume not found"
        )
        
    return OptimizedResumeDetailResponse(
        id=optimized.id,
        resume_id=optimized.resume_id,
        job_id=optimized.job_id,
        user_id=optimized.user_id,
        optimized_resume=OptimizedResumeSchema(**optimized.optimized_resume_json),
        created_at=optimized.created_at
    )
