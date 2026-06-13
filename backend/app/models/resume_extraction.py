from app.database.base import Base
from sqlalchemy import Column, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

class ResumeExtraction(Base):
    __tablename__ = "resume_extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_resumes.id"), nullable=False, unique=True, index=True)
    raw_text = Column(Text, nullable=False)
    extracted_links = Column(JSONB, nullable=True)  # {linkedin: "", github: "", ...}
    contact_info = Column(JSONB, nullable=True)    # {name: "", email: "", phone: "", location: ""}
    metadata_info = Column(JSONB, nullable=True)   # {page_count: 1, file_type: "pdf", ...}
    sections = Column(JSONB, nullable=True)        # List of detected sections
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
