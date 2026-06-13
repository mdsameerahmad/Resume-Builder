from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class JDBase(BaseModel):
    job_description: str

class JDAnalysisSchema(BaseModel):
    job_title: Optional[str] = ""
    industry: Optional[str] = ""
    job_category: Optional[str] = ""
    department: Optional[str] = ""
    seniority_level: Optional[str] = ""
    confidence_score: Optional[float] = 0.0
    experience_required: Optional[str] = ""
    education_required: Optional[str] = ""
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    technologies: List[str] = []
    responsibilities: List[str] = []
    ats_keywords: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []

class JDResponse(BaseModel):
    id: UUID
    user_id: UUID
    raw_jd: str
    parsed_jd: Optional[JDAnalysisSchema] = None
    job_title: Optional[str] = ""
    industry: Optional[str] = ""
    job_category: Optional[str] = ""
    department: Optional[str] = ""
    seniority_level: Optional[str] = ""
    confidence_score: Optional[float] = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

class JDAnalysisResponse(BaseModel):
    status: str
    job_id: UUID
    analysis: JDAnalysisSchema
