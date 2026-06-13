from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database.session import get_db
from app.services.resume_upload_service import ResumeUploadService
from app.services.storage.supabase_storage import SupabaseStorage
from app.schemas.resume_upload import ResumeUploadResponse, ResumeMetadata
import uuid

router = APIRouter()

# Mock user ID for Phase 3 (since auth is not implemented)
MOCK_USER_ID = UUID("00000000-0000-0000-0000-000000000000")

def get_upload_service(db: AsyncSession = Depends(get_db)):
    storage_service = SupabaseStorage()
    return ResumeUploadService(db, storage_service)

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    service: ResumeUploadService = Depends(get_upload_service)
):
    """
    Upload a resume file (PDF or DOCX).
    """
    # In a real app, user_id would come from the auth token
    # For now, we'll use a mock user ID or ensure a mock user exists
    return await service.upload_resume(MOCK_USER_ID, file)

@router.get("/list", response_model=List[ResumeMetadata])
async def list_resumes(
    service: ResumeUploadService = Depends(get_upload_service)
):
    """
    List all uploaded resumes for the current user.
    """
    return await service.get_resumes(MOCK_USER_ID)

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
