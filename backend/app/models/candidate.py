"""Candidate model"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ARRAY
from sqlalchemy.sql import func
from app.db.database import Base


class Candidate(Base):
    """Candidate model"""
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)

    # Current position
    current_company = Column(String)
    current_title = Column(String)
    years_of_experience = Column(Integer)
    location = Column(String)

    # Status
    status = Column(String, nullable=False, default="new", index=True)
    # Status options: new, contacted, interested, interviewing, rejected, hired, archived

    # Additional info
    tags = Column(ARRAY(String), default=[])
    source = Column(String)  # Where the candidate came from
    resume_url = Column(String)

    # Metadata
    latest_contacted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Candidate(id={self.id}, name={self.name}, status={self.status})>"
