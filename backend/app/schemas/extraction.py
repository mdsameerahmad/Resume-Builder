from pydantic import BaseModel
from uuid import UUID
from typing import Dict, List, Optional, Any
from datetime import datetime

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

class ExtractedLinks(BaseModel):
    linkedin: List[str] = []
    github: List[str] = []
    portfolio: List[str] = []
    leetcode: List[str] = []
    gfg: List[str] = []
    youtube: List[str] = []
    other_urls: List[str] = []

class ExtractionResponse(BaseModel):
    resume_id: UUID
    raw_text: str
    contact_info: ContactInfo
    links: ExtractedLinks
    metadata: Dict[str, Any]
    sections: List[str] = []
    status: str = "success"

class ExtractionMetadata(BaseModel):
    id: UUID
    resume_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
