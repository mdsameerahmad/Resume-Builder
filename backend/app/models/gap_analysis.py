from app.database.base import Base
from sqlalchemy import Column, ForeignKey, Text, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

class GapAnalysis(Base):
    __tablename__ = "gap_analysis_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_resumes.id"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=False, index=True)
    
    matched_skills = Column(JSONB, nullable=True)
    missing_skills = Column(JSONB, nullable=True)
    matched_keywords = Column(JSONB, nullable=True)
    missing_keywords = Column(JSONB, nullable=True)
    relevant_projects = Column(JSONB, nullable=True)
    relevant_experience = Column(JSONB, nullable=True)
    strengths = Column(JSONB, nullable=True)
    weaknesses = Column(JSONB, nullable=True)
    
    coverage_score = Column(Float, default=0.0)
    ats_score = Column(Float, default=0.0)
    
    recommendations = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
