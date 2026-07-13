"""Scorecard endpoints"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.db.database import get_db
from app.models.scorecard import Scorecard as ScorecardModel

router = APIRouter()


class ScorecardCreate(BaseModel):
    """Scorecard creation model"""
    interview_id: str
    interviewer_id: str
    technical_skills: int
    communication: int
    problem_solving: int
    cultural_fit: int
    strengths: List[str] = []
    weaknesses: List[str] = []
    notes: Optional[str] = None
    recommendation: str


class Scorecard(BaseModel):
    """Scorecard response model"""
    id: str
    interview_id: str
    interviewer_id: str
    technical_skills: int
    communication: int
    problem_solving: int
    cultural_fit: int
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    notes: Optional[str]
    recommendation: str

    class Config:
        from_attributes = True


@router.post("/", response_model=Scorecard)
async def create_scorecard(
    scorecard: ScorecardCreate,
    db: Session = Depends(get_db)
):
    """
    Create interview scorecard
    """
    # Calculate overall score
    overall_score = (
        scorecard.technical_skills +
        scorecard.communication +
        scorecard.problem_solving +
        scorecard.cultural_fit
    ) / 4.0

    db_scorecard = ScorecardModel(
        id=str(uuid.uuid4()),
        overall_score=overall_score,
        **scorecard.model_dump()
    )

    db.add(db_scorecard)
    db.commit()
    db.refresh(db_scorecard)

    return db_scorecard


@router.get("/interview/{interview_id}", response_model=List[Scorecard])
async def get_scorecards_by_interview(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all scorecards for an interview
    """
    scorecards = db.query(ScorecardModel).filter(
        ScorecardModel.interview_id == interview_id
    ).all()

    return scorecards
