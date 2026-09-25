"""Headhunter models - 猎头推荐管理"""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func
from app.db.database import Base


class HeadhunterRecommendation(Base):
    """猎头推荐记录"""
    __tablename__ = "headhunter_recommendations"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_name = Column(String, nullable=False, index=True)
    phone = Column(String)
    email = Column(String)
    resume_url = Column(String)
    headhunter_name = Column(String)
    notes = Column(Text)
    status = Column(String, nullable=False, default="pending", index=True)  # pending, approved, rejected
    hr_feedback = Column(Text)
    reviewed_by = Column(String, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
