"""HR Interview Service - HR初筛面试服务"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.interview import Interview, InterviewType, InterviewStatus, InterviewResult
from app.models.application import Application, ApplicationStatus
from app.services.application_service import ApplicationService


class HRInterviewService:
    """HR初筛面试服务"""

    @staticmethod
    async def schedule_hr_interview(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        scheduled_at: datetime,
        duration: int = 30,
        location: Optional[str] = None,
        scorecard_template_id: Optional[str] = None
    ) -> Interview:
        """HR给自己安排初筛面试"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 1. 创建面试记录
        interview = Interview(
            id=f"int_{datetime.now().timestamp()}",
            application_id=application_id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            interview_type=InterviewType.HR_INITIAL,
            title="HR初筛面试",
            interviewer_id=hr_id,
            interviewer_name=hr_name,
            scorecard_template_id=scorecard_template_id,
            scheduled_at=scheduled_at,
            duration=duration,
            location=location,
            status=InterviewStatus.SCHEDULED
        )
        db.add(interview)

        # 2. 转换应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.HR_INTERVIEW_SCHEDULED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason="HR安排初筛面试"
        )

        # 3. TODO: 发送通知给候选人
        # await EmailService.send_interview_invitation(interview)

        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    async def start_interview(
        db: Session,
        interview_id: str,
        hr_id: str,
        hr_name: str
    ) -> Interview:
        """开始HR初筛面试"""

        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        interview.status = InterviewStatus.IN_PROGRESS
        db.commit()

        # 更新应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=interview.application_id,
            to_status=ApplicationStatus.HR_INTERVIEWING,
            operator_id=hr_id,
            operator_name=hr_name,
            reason="HR初筛面试开始"
        )

        db.refresh(interview)
        return interview

    @staticmethod
    async def complete_interview(
        db: Session,
        interview_id: str,
        hr_id: str,
        hr_name: str,
        result: InterviewResult,
        feedback: str,
        score: int,
        evaluation_data: dict
    ) -> Interview:
        """完成HR初筛面试并填写评价表"""

        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # 1. 更新面试记录
        interview.status = InterviewStatus.COMPLETED
        interview.result = result
        interview.feedback = feedback
        interview.score = score
        interview.evaluation_data = str(evaluation_data)  # JSON格式
        interview.completed_at = datetime.now()
        db.commit()

        # 2. 更新应聘状态
        if result == InterviewResult.PASS:
            await ApplicationService.transition_status(
                db=db,
                application_id=interview.application_id,
                to_status=ApplicationStatus.HR_INTERVIEW_COMPLETED,
                operator_id=hr_id,
                operator_name=hr_name,
                reason="HR初筛面试通过"
            )
        else:
            await ApplicationService.transition_status(
                db=db,
                application_id=interview.application_id,
                to_status=ApplicationStatus.HR_INTERVIEW_REJECTED,
                operator_id=hr_id,
                operator_name=hr_name,
                reason="HR初筛面试未通过"
            )

        db.refresh(interview)
        return interview

    @staticmethod
    def get_by_id(db: Session, interview_id: str) -> Optional[Interview]:
        """根据ID获取面试记录"""
        return db.query(Interview).filter(Interview.id == interview_id).first()

    @staticmethod
    def get_by_application(db: Session, application_id: str) -> list[Interview]:
        """根据应聘记录获取所有面试"""
        return db.query(Interview).filter(
            Interview.application_id == application_id,
            Interview.interview_type == InterviewType.HR_INITIAL
        ).all()

    @staticmethod
    def cancel_interview(
        db: Session,
        interview_id: str,
        reason: str
    ) -> Interview:
        """取消面试"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        interview.status = InterviewStatus.CANCELLED
        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def reschedule_interview(
        db: Session,
        interview_id: str,
        new_scheduled_at: datetime,
        reason: str
    ) -> Interview:
        """改期面试"""
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        interview.scheduled_at = new_scheduled_at
        interview.status = InterviewStatus.RESCHEDULED
        db.commit()

        # TODO: 发送改期通知

        db.refresh(interview)
        return interview
