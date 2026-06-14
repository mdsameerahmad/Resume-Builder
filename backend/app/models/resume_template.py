from app.database.base import Base
from sqlalchemy import Column, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

class ResumeTemplate(Base):
    __tablename__ = "resume_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_resumes.id"), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    template_html = Column(Text, nullable=False)
    template_css = Column(Text, nullable=True)
    layout_metadata = Column(JSONB, nullable=False)
    section_order = Column(JSONB, nullable=False)
    template_variables = Column(JSONB, nullable=False)
    hyperlinks = Column(JSONB, nullable=True) # LinkedIn, GitHub, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
