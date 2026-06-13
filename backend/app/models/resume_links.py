from app.database.base import Base
from sqlalchemy import Column, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class ResumeLinks(Base):
    __tablename__ = "resume_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    email = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    linkedin = Column(Text, nullable=True)
    github = Column(Text, nullable=True)
    portfolio = Column(Text, nullable=True)
    leetcode = Column(Text, nullable=True)
    gfg = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
