"""Interview service - 面试业务逻辑"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import uuid

from app.models.interview import Interview, InterviewType, InterviewStatus, InterviewResult
from app.models.application import Application
from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewEvaluation


class InterviewService:
    """面试服务"""

    @staticmethod
    def create(db: Session, interview_data: InterviewCreate) -> Interview:
        """创建面试"""
        interview_id = f"int_{uuid.uuid4().hex[:12]}"

        interview = Interview(
            id=interview_id,
            application_id=interview_data.application_id,
            job_id=interview_data.job_id,
            candidate_id=interview_data.candidate_id,
            interview_type=interview_data.interview_type,
            title=interview_data.title,
            interviewer_id=interview_data.interviewer_id,
            interviewer_name=interview_data.interviewer_name,
            scheduled_at=interview_data.scheduled_at,
            duration=interview_data.duration,
            location=interview_data.location,
            meeting_link=interview_data.meeting_link,
            status=InterviewStatus.SCHEDULED,
            result=InterviewResult.PENDING,
        )

        db.add(interview)
        db.commit()
        db.refresh(interview)

        return interview

    @staticmethod
    def get_by_id(db: Session, interview_id: str) -> Optional[Interview]:
        """根据ID获取面试"""
        return db.query(Interview).filter(Interview.id == interview_id).first()

    @staticmethod
    def list_interviews(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        interviewer_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        job_id: Optional[str] = None,
        application_id: Optional[str] = None,
        status: Optional[InterviewStatus] = None,
        interview_type: Optional[InterviewType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[dict]:
        """
        获取面试列表（带候选人和职位信息）
        """
        query = db.query(
            Interview,
            Candidate.name.label("candidate_name"),
            Job.title.label("job_title")
        ).join(
            Candidate, Interview.candidate_id == Candidate.id
        ).join(
            Job, Interview.job_id == Job.id
        )

        # 过滤条件
        if interviewer_id:
            query = query.filter(Interview.interviewer_id == interviewer_id)
        if candidate_id:
            query = query.filter(Interview.candidate_id == candidate_id)
        if job_id:
            query = query.filter(Interview.job_id == job_id)
        if application_id:
            query = query.filter(Interview.application_id == application_id)
        if status:
            query = query.filter(Interview.status == status)
        if interview_type:
            query = query.filter(Interview.interview_type == interview_type)
        if date_from:
            query = query.filter(Interview.scheduled_at >= date_from)
        if date_to:
            query = query.filter(Interview.scheduled_at <= date_to)

        # 排序：按面试时间
        query = query.order_by(Interview.scheduled_at.asc())

        results = query.offset(skip).limit(limit).all()

        # 转换为字典格式
        interviews = []
        for interview, cand_name, job_title in results:
            interviews.append({
                "id": interview.id,
                "application_id": interview.application_id,
                "candidate_id": interview.candidate_id,
                "candidate_name": cand_name,
                "job_id": interview.job_id,
                "job_title": job_title,
                "interview_type": interview.interview_type,
                "interviewer_name": interview.interviewer_name,
                "scheduled_at": interview.scheduled_at,
                "duration": interview.duration,
                "location": interview.location,
                "status": interview.status,
                "result": interview.result,
            })

        return interviews

    @staticmethod
    def get_today_interviews(db: Session, interviewer_id: str) -> List[dict]:
        """获取今日面试"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        return InterviewService.list_interviews(
            db=db,
            interviewer_id=interviewer_id,
            date_from=today_start,
            date_to=today_end,
            status=InterviewStatus.SCHEDULED
        )

    @staticmethod
    def get_upcoming_interviews(
        db: Session,
        interviewer_id: str,
        days: int = 7
    ) -> List[dict]:
        """获取未来N天的面试"""
        now = datetime.now()
        future = now + timedelta(days=days)

        return InterviewService.list_interviews(
            db=db,
            interviewer_id=interviewer_id,
            date_from=now,
            date_to=future,
            status=InterviewStatus.SCHEDULED
        )

    @staticmethod
    def update(
        db: Session,
        interview_id: str,
        interview_data: InterviewUpdate
    ) -> Optional[Interview]:
        """更新面试信息"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return None

        # 更新字段
        update_data = interview_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interview, field, value)

        db.commit()
        db.refresh(interview)

        return interview

    @staticmethod
    def update_status(
        db: Session,
        interview_id: str,
        new_status: InterviewStatus
    ) -> Optional[Interview]:
        """更新面试状态"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return None

        interview.status = new_status

        # 如果是完成状态，记录完成时间
        if new_status == InterviewStatus.COMPLETED:
            interview.completed_at = datetime.now()

        db.commit()
        db.refresh(interview)

        return interview

    @staticmethod
    def submit_evaluation(
        db: Session,
        interview_id: str,
        evaluation: InterviewEvaluation
    ) -> Optional[Interview]:
        """提交面试评价"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return None

        # 更新评价
        interview.result = evaluation.result
        interview.score = evaluation.score
        interview.feedback = evaluation.feedback
        interview.status = InterviewStatus.COMPLETED
        interview.completed_at = datetime.now()

        db.commit()
        db.refresh(interview)

        return interview

    @staticmethod
    def get_interview_detail(db: Session, interview_id: str) -> Optional[dict]:
        """获取面试详情（含候选人和职位信息）"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return None

        # 获取候选人信息
        candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()

        # 获取职位信息
        job = db.query(Job).filter(Job.id == interview.job_id).first()

        # 获取应聘记录
        application = db.query(Application).filter(Application.id == interview.application_id).first()

        return {
            "interview": {
                "id": interview.id,
                "application_id": interview.application_id,
                "job_id": interview.job_id,
                "candidate_id": interview.candidate_id,
                "interview_type": interview.interview_type.value,
                "title": interview.title,
                "interviewer_id": interview.interviewer_id,
                "interviewer_name": interview.interviewer_name,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "duration": interview.duration,
                "location": interview.location,
                "meeting_link": interview.meeting_link,
                "status": interview.status.value,
                "result": interview.result.value if interview.result else None,
                "feedback": interview.feedback,
                "score": interview.score,
                "created_at": interview.created_at.isoformat(),
                "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            },
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "phone": candidate.phone,
                "email": candidate.email,
                "current_company": candidate.current_company,
                "current_title": candidate.current_title,
                "years_of_experience": candidate.years_of_experience,
            } if candidate else None,
            "job": {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "category": job.category.value,
            } if job else None,
            "application_status": application.status.value if application else None,
        }

    @staticmethod
    def cancel_interview(db: Session, interview_id: str, reason: Optional[str] = None) -> Optional[Interview]:
        """取消面试"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            return None

        interview.status = InterviewStatus.CANCELLED
        if reason:
            interview.feedback = f"取消原因: {reason}"

        db.commit()
        db.refresh(interview)

        return interview
