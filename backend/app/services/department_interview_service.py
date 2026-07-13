"""Department Interview Service - 部门面试服务"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.interview import Interview, InterviewType, InterviewStatus, InterviewResult
from app.models.application import Application, ApplicationStatus
from app.services.application_service import ApplicationService


class DepartmentInterviewService:
    """部门面试服务"""

    @staticmethod
    async def schedule_interview(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        interviewer_id: str,
        interviewer_name: str,
        scheduled_at: datetime,
        duration: int = 60,
        location: Optional[str] = None,
        meeting_link: Optional[str] = None,
        scorecard_template_id: Optional[str] = None
    ) -> Interview:
        """安排部门面试"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 1. 创建面试记录
        interview = Interview(
            id=f"int_{datetime.now().timestamp()}",
            application_id=application_id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            interview_type=InterviewType.DEPARTMENT,
            title="部门面试",
            interviewer_id=interviewer_id,
            interviewer_name=interviewer_name,
            scorecard_template_id=scorecard_template_id,
            scheduled_at=scheduled_at,
            duration=duration,
            location=location,
            meeting_link=meeting_link,
            status=InterviewStatus.SCHEDULED
        )
        db.add(interview)

        # 2. 转换应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"安排部门面试，面试官：{interviewer_name}"
        )

        # 3. TODO: 发送通知
        # await NotificationService.notify_interview_scheduled(interview)

        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    async def start_interview(
        db: Session,
        interview_id: str,
        interviewer_id: str,
        interviewer_name: str
    ) -> Interview:
        """开始部门面试"""

        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # 验证权限
        if interview.interviewer_id != interviewer_id:
            raise ValueError("You are not authorized to start this interview")

        interview.status = InterviewStatus.IN_PROGRESS
        db.commit()

        # 更新应聘状态
        await ApplicationService.transition_status(
            db=db,
            application_id=interview.application_id,
            to_status=ApplicationStatus.DEPARTMENT_INTERVIEWING,
            operator_id=interviewer_id,
            operator_name=interviewer_name,
            reason="部门面试开始"
        )

        db.refresh(interview)
        return interview

    @staticmethod
    async def complete_interview(
        db: Session,
        interview_id: str,
        interviewer_id: str,
        interviewer_name: str,
        result: InterviewResult,
        feedback: str,
        score: int,
        evaluation_data: dict
    ) -> Interview:
        """完成部门面试并填写评价表"""

        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # 验证权限
        if interview.interviewer_id != interviewer_id:
            raise ValueError("You are not authorized to complete this interview")

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
                to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED,
                operator_id=interviewer_id,
                operator_name=interviewer_name,
                reason="部门面试通过"
            )
        elif result == InterviewResult.FAIL:
            await ApplicationService.transition_status(
                db=db,
                application_id=interview.application_id,
                to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
                operator_id=interviewer_id,
                operator_name=interviewer_name,
                reason="部门面试未通过"
            )
        else:  # HOLD
            # 保持当前状态，等待进一步决策
            pass

        db.refresh(interview)
        return interview

    @staticmethod
    def get_by_id(db: Session, interview_id: str) -> Optional[Interview]:
        """根据ID获取面试记录"""
        return db.query(Interview).filter(Interview.id == interview_id).first()

    @staticmethod
    def get_by_application(db: Session, application_id: str) -> list[Interview]:
        """根据应聘记录获取所有部门面试"""
        return db.query(Interview).filter(
            Interview.application_id == application_id,
            Interview.interview_type == InterviewType.DEPARTMENT
        ).order_by(Interview.scheduled_at.desc()).all()

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

        # TODO: 发送取消通知
        # await NotificationService.notify_interview_cancelled(interview, reason)

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
        # await NotificationService.notify_interview_rescheduled(interview, reason)

        db.refresh(interview)
        return interview

    @staticmethod
    def get_interviewer_schedule(
        db: Session,
        interviewer_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> list[Interview]:
        """获取面试官的面试日程"""
        return db.query(Interview).filter(
            Interview.interviewer_id == interviewer_id,
            Interview.interview_type == InterviewType.DEPARTMENT,
            Interview.scheduled_at >= start_date,
            Interview.scheduled_at <= end_date,
            Interview.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.RESCHEDULED])
        ).order_by(Interview.scheduled_at).all()
