"""Headhunter management endpoints - 猎头管理接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.headhunter_service import HeadhunterService

router = APIRouter()


class RecommendationCreateRequest(BaseModel):
    job_id: str
    candidate_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    resume_url: Optional[str] = None
    headhunter_name: Optional[str] = None
    notes: Optional[str] = None


class RecommendationReviewRequest(BaseModel):
    status: str
    feedback: Optional[str] = None


@router.get("/jobs", response_model=dict)
async def list_headhunter_jobs(db: Session = Depends(get_db)):
    jobs = HeadhunterService.list_open_jobs(db)
    return {
        "code": 0,
        "data": [
            {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "openings": job.openings,
                "status": job.status.value,
                "is_third_party_headhunter_enabled": job.is_third_party_headhunter_enabled,
            }
            for job in jobs
        ],
    }


@router.get("/recommendations", response_model=dict)
async def list_recommendations(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return {
        "code": 0,
        "data": HeadhunterService.list_recommendations(db, status=status),
    }


@router.post("/recommendations", response_model=dict)
async def create_recommendation(
    request: RecommendationCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        recommendation = HeadhunterService.create_recommendation(db, request.model_dump())
        return {
            "code": 0,
            "data": {
                "id": recommendation.id,
                "status": recommendation.status,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/recommendations/{recommendation_id}/review", response_model=dict)
async def review_recommendation(
    recommendation_id: str,
    request: RecommendationReviewRequest,
    db: Session = Depends(get_db),
):
    try:
        recommendation = HeadhunterService.review_recommendation(
            db=db,
            recommendation_id=recommendation_id,
            status=request.status,
            feedback=request.feedback,
            reviewer_id="1",
        )
        return {
            "code": 0,
            "data": {
                "id": recommendation.id,
                "status": recommendation.status,
                "hr_feedback": recommendation.hr_feedback,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
