from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class ContactSchema(BaseModel):
    full_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    location: Optional[str] = ""

class LinksSchema(BaseModel):
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    leetcode: Optional[str] = ""
    gfg: Optional[str] = ""
    website: Optional[str] = ""

class ProjectSchema(BaseModel):
    title: Optional[str] = ""
    description: Optional[str] = ""
    technologies: List[str] = []
    achievements: List[str] = []

class ExperienceSchema(BaseModel):
    company: Optional[str] = ""
    role: Optional[str] = ""
    duration: Optional[str] = ""
    responsibilities: List[str] = []

class EducationSchema(BaseModel):
    institution: Optional[str] = ""
    degree: Optional[str] = ""
    cgpa: Optional[str] = ""
    year: Optional[str] = ""

class MasterResumeJSON(BaseModel):
    contact: ContactSchema = ContactSchema()
    links: LinksSchema = LinksSchema()
    professional_summary: Optional[str] = ""
    skills: List[str] = []
    projects: List[ProjectSchema] = []
    experience: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    certifications: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []

class MasterResumeResponse(BaseModel):
    status: str
    master_resume_id: UUID
    skills_count: int
    projects_count: int

class MasterResumeProfileSchema(BaseModel):
    id: UUID
    resume_id: UUID
    user_id: UUID
    master_resume_json: MasterResumeJSON
    parsing_status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
