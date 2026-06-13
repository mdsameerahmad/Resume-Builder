from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ResumeUploadResponse(BaseModel):
    resume_id: UUID
    original_filename: str
    file_type: str
    file_size: int
    storage_url: Optional[str]
    status: str

    class Config:
        from_attributes = True

class ResumeMetadata(BaseModel):
    id: UUID
    user_id: UUID
    original_filename: str
    file_type: str
    file_size: int
    storage_url: Optional[str]
    upload_status: str
    created_at: datetime

    class Config:
        from_attributes = True
