"""Scorecard model for interview evaluation"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class Scorecard(Base):
    """Interview scorecard model"""
    __tablename__ = "scorecards"

    id = Column(String, primary_key=True, index=True)
    interview_id = Column(String, ForeignKey("interviews.id"), nullable=False, index=True)
    interviewer_id = Column(String, nullable=False)

    # Scoring dimensions
    technical_skills = Column(Integer)  # 1-5
    communication = Column(Integer)  # 1-5
    problem_solving = Column(Integer)  # 1-5
    cultural_fit = Column(Integer)  # 1-5
    overall_score = Column(Float)  # Average

    # Detailed feedback
    strengths = Column(JSON)  # List of strengths
    weaknesses = Column(JSON)  # List of weaknesses
    notes = Column(String)

    # Recommendation
    recommendation = Column(String)  # strong_yes, yes, maybe, no, strong_no

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Scorecard(id={self.id}, interview_id={self.interview_id}, overall={self.overall_score})>"
