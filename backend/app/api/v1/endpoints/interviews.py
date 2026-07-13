"""Interview management endpoints"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.database import get_db
from app.models import Interview as InterviewModel

router = APIRouter()


class InterviewBase(BaseModel):
    """Interview base model"""
    candidate_id: str
    job_id: str
    interviewer_id: str
    scheduled_at: datetime
    duration_minutes: str = "60"
    type: str
    status: str = "scheduled"


class InterviewCreate(InterviewBase):
    """Interview creation model"""
    pass


class InterviewUpdate(BaseModel):
    """Interview update model"""
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    feedback: Optional[str] = None
    result: Optional[str] = None


class InterviewFeedback(BaseModel):
    """Interview feedback submission"""
    feedback: str
    result: str  # pass, pending, reject
    scores: Optional[dict] = None


class Interview(InterviewBase):
    """Interview response model"""
    id: str
    feedback: Optional[str] = None
    result: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[Interview])
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    interviewer_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    List interviews with pagination and filtering
    """
    query = db.query(InterviewModel)

    if interviewer_id:
        query = query.filter(InterviewModel.interviewer_id == interviewer_id)

    if status:
        query = query.filter(InterviewModel.status == status)

    interviews = query.order_by(InterviewModel.scheduled_at.desc()).offset(skip).limit(limit).all()
    return interviews


@router.get("/{interview_id}", response_model=Interview)
async def get_interview(interview_id: str, db: Session = Depends(get_db)):
    """
    Get interview details by ID
    """
    interview = db.query(InterviewModel).filter(InterviewModel.id == interview_id).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return interview


@router.post("/", response_model=Interview)
async def create_interview(interview: InterviewCreate, db: Session = Depends(get_db)):
    """
    Create a new interview
    """
    db_interview = InterviewModel(
        id=str(uuid.uuid4()),
        **interview.model_dump()
    )

    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)

    return db_interview


@router.put("/{interview_id}", response_model=Interview)
async def update_interview(
    interview_id: str,
    interview: InterviewUpdate,
    db: Session = Depends(get_db)
):
    """
    Update interview information
    """
    db_interview = db.query(InterviewModel).filter(InterviewModel.id == interview_id).first()

    if not db_interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    for key, value in interview.model_dump(exclude_unset=True).items():
        setattr(db_interview, key, value)

    db.commit()
    db.refresh(db_interview)

    return db_interview


@router.post("/{interview_id}/feedback")
async def submit_feedback(
    interview_id: str,
    feedback: InterviewFeedback,
    db: Session = Depends(get_db)
):
    """
    Submit interview feedback and result
    """
    db_interview = db.query(InterviewModel).filter(InterviewModel.id == interview_id).first()

    if not db_interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Update interview
    db_interview.feedback = feedback.feedback
    db_interview.result = feedback.result
    db_interview.status = "completed"

    db.commit()
    db.refresh(db_interview)

    return {
        "success": True,
        "message": "Feedback submitted successfully",
        "interview": db_interview
    }


@router.delete("/{interview_id}")
async def delete_interview(interview_id: str, db: Session = Depends(get_db)):
    """
    Delete an interview
    """
    db_interview = db.query(InterviewModel).filter(InterviewModel.id == interview_id).first()

    if not db_interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    db.delete(db_interview)
    db.commit()

    return {"message": "Interview deleted successfully"}

