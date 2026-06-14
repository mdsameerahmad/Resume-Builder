from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.database.session import get_db
from app.services.resume_upload_service import ResumeUploadService
from app.services.storage.supabase_storage import SupabaseStorage
from app.schemas.resume_upload import ResumeUploadResponse, ResumeMetadata
from app.models.user import User
from loguru import logger
import uuid

router = APIRouter()

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

def get_upload_service(db: AsyncSession = Depends(get_db)):
    storage_service = SupabaseStorage()
    return ResumeUploadService(db, storage_service)

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    service: ResumeUploadService = Depends(get_upload_service)
):
    """
    Upload a resume file (PDF or DOCX).
    """
    user_id = await ensure_mock_user(db)
    return await service.upload_resume(user_id, file)

@router.get("/list", response_model=List[ResumeMetadata])
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    service: ResumeUploadService = Depends(get_upload_service)
):
    """
    List all uploaded resumes for the current user.
    """
    user_id = await ensure_mock_user(db)
    return await service.get_resumes(user_id)

@router.get("/{resume_id}", response_model=ResumeMetadata)
async def get_resume(
    resume_id: UUID,
    service: ResumeUploadService = Depends(get_upload_service)
):
    """
    Get metadata for a specific resume.
    """
    resume = await service.get_resume_by_id(resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    service: ResumeUploadService = Depends(get_upload_service)
):
    """
    Delete an uploaded resume.
    """
    success = await service.delete_resume(resume_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return None
