from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class RelevantProjectSchema(BaseModel):
    title: str
    relevance_score: float

class RelevantExperienceSchema(BaseModel):
    company: str
    relevance_score: float

class GapAnalysisSchema(BaseModel):
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    relevant_projects: List[RelevantProjectSchema] = []
    relevant_experience: List[RelevantExperienceSchema] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    coverage_score: float = 0.0
    ats_score: float = 0.0
    optimization_recommendations: List[str] = []

class GapAnalysisRequest(BaseModel):
    resume_id: UUID
    job_id: UUID

class GapAnalysisResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_id: UUID
    user_id: UUID
    analysis: GapAnalysisSchema
    created_at: datetime

    class Config:
        from_attributes = True
