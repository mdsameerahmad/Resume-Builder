from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class OptimizationMetadataSchema(BaseModel):
    ats_keywords_used: List[str] = []
    projects_prioritized: List[str] = []
    optimization_score: float = 0.0

class OptimizedResumeSchema(BaseModel):
    contact: Dict[str, Any] = {}
    links: Dict[str, Any] = {}
    summary: str = ""
    skills: List[str] = []
    projects: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    achievements: List[str] = []
    optimization_metadata: OptimizationMetadataSchema = Field(default_factory=OptimizationMetadataSchema)

class OptimizeRequest(BaseModel):
    resume_id: UUID
    job_id: UUID

class OptimizeResponse(BaseModel):
    optimized_resume_id: UUID
    optimization_score: float
    status: str = "success"
    created_at: datetime

class OptimizedResumeDetailResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    user_id: UUID
    optimized_resume: OptimizedResumeSchema
    created_at: datetime

    class Config:
        from_attributes = True
