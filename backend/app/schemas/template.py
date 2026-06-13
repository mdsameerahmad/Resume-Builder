from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime

class TemplateCreateResponse(BaseModel):
    status: str
    template_id: UUID
    resume_id: UUID

class TemplateMetadataSchema(BaseModel):
    page: Dict[str, Any]
    fonts: List[str]
    font_sizes: List[float]
    colors: List[str]
    margins: Dict[str, float]

class ResumeTemplateSchema(BaseModel):
    id: UUID
    resume_id: UUID
    user_id: UUID
    template_html: str
    layout_metadata: Dict[str, Any]
    section_order: List[str]
    template_variables: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
