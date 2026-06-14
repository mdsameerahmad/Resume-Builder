from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class PDFGenerateRequest(BaseModel):
    optimized_resume_id: UUID

class PDFGenerateResponse(BaseModel):
    generated_resume_id: UUID
    page_count: int
    is_one_page: bool
    pdf_url: str
    html_url: str
    status: str = "success"
    created_at: datetime

class PDFDetailResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    optimized_resume_id: UUID
    pdf_url: str
    html_url: str
    page_count: int
    is_one_page: bool
    created_at: datetime

    class Config:
        from_attributes = True
