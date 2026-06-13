from app.database.base import Base
from sqlalchemy import Column, ForeignKey, Text, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    raw_jd = Column(Text, nullable=False)
    parsed_jd = Column(JSONB, nullable=True)
    job_title = Column(Text, nullable=True)
    industry = Column(Text, nullable=True)
    job_category = Column(Text, nullable=True)
    department = Column(Text, nullable=True)
    seniority_level = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
