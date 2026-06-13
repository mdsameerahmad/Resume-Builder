import os
import uuid
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.uploaded_resume import UploadedResume
from app.services.storage.storage_service import StorageService
from app.schemas.resume_upload import ResumeUploadResponse
from loguru import logger
import magic

class ResumeUploadService:
    def __init__(self, db: AsyncSession, storage_service: StorageService):
        self.db = db
        self.storage_service = storage_service
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {".pdf", ".docx"}
        self.allowed_mimetypes = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

    async def validate_file(self, file: UploadFile):
        # Validate extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension: {ext}. Allowed: {', '.join(self.allowed_extensions)}"
            )

        # Validate size
        # To get size without reading entire file into memory
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large: {file_size / (1024 * 1024):.2f}MB. Max allowed: 10MB"
            )

        # Validate MIME type using magic
        content = await file.read(2048)
        await file.seek(0)
        mime_type = magic.from_buffer(content, mime=True)
        if mime_type not in self.allowed_mimetypes:
            logger.warning(f"Rejected file with MIME type: {mime_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file content type: {mime_type}"
            )
        
        return file_size, mime_type

    async def upload_resume(self, user_id: uuid.UUID, file: UploadFile) -> ResumeUploadResponse:
        logger.info(f"Starting upload for user {user_id}: {file.filename}")
        
        # 1. Validate
        file_size, mime_type = await self.validate_file(file)
        
        # 2. Generate unique filename
        ext = os.path.splitext(file.filename)[1].lower()
        stored_filename = f"{uuid.uuid4()}{ext}"
        
        # 3. Create database record (pending)
        db_resume = UploadedResume(
            user_id=user_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_type=mime_type,
            file_size=file_size,
            upload_status="pending"
        )
        self.db.add(db_resume)
        await self.db.commit()
        await self.db.refresh(db_resume)
        
        try:
            # 4. Upload to storage
            folder = f"{user_id}/original_resumes"
            storage_url = await self.storage_service.upload_file(
                file.file, 
                stored_filename, 
                folder=folder
            )
            
            # 5. Update database record (success)
            db_resume.storage_url = storage_url
            db_resume.upload_status = "uploaded"
            await self.db.commit()
            await self.db.refresh(db_resume)
            
            logger.info(f"Successfully uploaded resume {db_resume.id} for user {user_id}")
            
            return ResumeUploadResponse(
                resume_id=db_resume.id,
                original_filename=db_resume.original_filename,
                file_type=db_resume.file_type,
                file_size=db_resume.file_size,
                storage_url=db_resume.storage_url,
                status=db_resume.upload_status
            )
            
        except Exception as e:
            logger.error(f"Storage upload failed for {db_resume.id}: {e}")
            db_resume.upload_status = "failed"
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )

    async def get_resumes(self, user_id: uuid.UUID) -> List[UploadedResume]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(UploadedResume).where(UploadedResume.user_id == user_id)
        )
        return result.scalars().all()

    async def get_resume_by_id(self, resume_id: uuid.UUID) -> Optional[UploadedResume]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(UploadedResume).where(UploadedResume.id == resume_id)
        )
        return result.scalars().first()

    async def delete_resume(self, resume_id: uuid.UUID) -> bool:
        resume = await self.get_resume_by_id(resume_id)
        if not resume:
            return False
            
        # 1. Delete from storage
        if resume.storage_url:
            # Extract relative path from URL or reconstruct it
            # For simplicity, we know the path structure: {user_id}/original_resumes/{stored_filename}
            path = f"{resume.user_id}/original_resumes/{resume.stored_filename}"
            await self.storage_service.delete_file(path)
            
        # 2. Delete from database
        await self.db.delete(resume)
        await self.db.commit()
        return True
