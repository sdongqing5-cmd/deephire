"""Headhunter service - 猎头职位池和推荐审核"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app.models.headhunter import HeadhunterRecommendation
from app.models.job import Job, JobStatus


class HeadhunterService:
    """猎头协作服务。"""

    @staticmethod
    def list_open_jobs(db: Session) -> list[Job]:
        return (
            db.query(Job)
            .filter(
                Job.status == JobStatus.RECRUITING,
                Job.is_third_party_headhunter_enabled == True,
            )
            .order_by(Job.created_at.desc())
            .all()
        )

    @staticmethod
    def create_recommendation(db: Session, data: dict) -> HeadhunterRecommendation:
        job = db.query(Job).filter(Job.id == data["job_id"]).first()
        if not job:
            raise ValueError("职位不存在")
        if not job.is_third_party_headhunter_enabled:
            raise ValueError("该职位未开启第三方猎头")

        recommendation = HeadhunterRecommendation(
            id=f"rec_{uuid.uuid4().hex[:12]}",
            job_id=data["job_id"],
            candidate_name=data["candidate_name"],
            phone=data.get("phone"),
            email=data.get("email"),
            resume_url=data.get("resume_url"),
            headhunter_name=data.get("headhunter_name"),
            notes=data.get("notes"),
            status="pending",
        )
        db.add(recommendation)
        db.commit()
        db.refresh(recommendation)
        return recommendation

    @staticmethod
    def list_recommendations(db: Session, status: Optional[str] = None) -> list[dict]:
        query = db.query(HeadhunterRecommendation, Job.title.label("job_title")).join(
            Job, HeadhunterRecommendation.job_id == Job.id
        )
        if status:
            query = query.filter(HeadhunterRecommendation.status == status)

        rows = query.order_by(HeadhunterRecommendation.created_at.desc()).all()
        return [
            {
                "id": rec.id,
                "job_id": rec.job_id,
                "job_title": job_title,
                "candidate_name": rec.candidate_name,
                "phone": rec.phone,
                "email": rec.email,
                "resume_url": rec.resume_url,
                "headhunter_name": rec.headhunter_name,
                "notes": rec.notes,
                "status": rec.status,
                "hr_feedback": rec.hr_feedback,
                "reviewed_at": rec.reviewed_at.isoformat() if rec.reviewed_at else None,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
            }
            for rec, job_title in rows
        ]

    @staticmethod
    def review_recommendation(
        db: Session,
        recommendation_id: str,
        status: str,
        feedback: Optional[str],
        reviewer_id: str,
    ) -> HeadhunterRecommendation:
        if status not in {"approved", "rejected"}:
            raise ValueError("审核状态必须为 approved 或 rejected")

        recommendation = db.query(HeadhunterRecommendation).filter(
            HeadhunterRecommendation.id == recommendation_id
        ).first()
        if not recommendation:
            raise ValueError("推荐记录不存在")

        recommendation.status = status
        recommendation.hr_feedback = feedback
        recommendation.reviewed_by = reviewer_id
        recommendation.reviewed_at = datetime.now()
        db.commit()
        db.refresh(recommendation)
        return recommendation
