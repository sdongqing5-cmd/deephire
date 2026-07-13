"""Application Service - 应聘记录服务"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.services.application_state_machine import ApplicationStateMachine


class ApplicationService:
    """应聘记录服务"""

    @staticmethod
    async def transition_status(
        db: Session,
        application_id: str,
        to_status: ApplicationStatus,
        operator_id: str,
        operator_name: str,
        reason: Optional[str] = None
    ) -> Application:
        """状态流转"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 检查状态转换是否合法
        if not ApplicationStateMachine.can_transition(application.status, to_status):
            raise ValueError(
                f"不能从 {application.status} 转换到 {to_status}"
            )

        # 记录历史
        history = ApplicationStatusHistory(
            id=f"ash_{datetime.now().timestamp()}",
            application_id=application.id,
            from_status=application.status,
            to_status=to_status,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=reason
        )
        db.add(history)

        # 更新状态
        old_status = application.status
        application.status = to_status
        application.last_status_change_at = datetime.now()
        db.commit()
        db.refresh(application)

        # 触发后续操作
        await ApplicationService._handle_status_change(db, application, old_status, to_status)

        return application

    @staticmethod
    async def _handle_status_change(
        db: Session,
        application: Application,
        old_status: ApplicationStatus,
        new_status: ApplicationStatus
    ):
        """处理状态变更后的操作"""

        # HR初筛面试完成 → 推送给面试官
        if new_status == ApplicationStatus.SENT_TO_INTERVIEWER:
            # TODO: 发送通知给面试官
            pass

        # 面试意向沟通完成 → 发送面试确认邮件
        elif new_status == ApplicationStatus.INTERVIEW_TIME_CONFIRMING:
            # TODO: 发送邮件
            pass

        # 候选人确认面试时间 → 创建面试记录
        elif new_status == ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED:
            # TODO: 创建面试记录
            pass

    @staticmethod
    def get_by_id(db: Session, application_id: str) -> Optional[Application]:
        """根据ID获取应聘记录"""
        return db.query(Application).filter(Application.id == application_id).first()

    @staticmethod
    def get_by_candidate_and_job(
        db: Session,
        candidate_id: str,
        job_id: str
    ) -> Optional[Application]:
        """根据候选人和职位获取应聘记录"""
        return db.query(Application).filter(
            Application.candidate_id == candidate_id,
            Application.job_id == job_id
        ).first()

    @staticmethod
    def create(
        db: Session,
        application_id: str,
        candidate_id: str,
        job_id: str,
        resume_url: Optional[str] = None,
        resume_parsed_data: Optional[str] = None,
        source: Optional[str] = None,
        hr_id: Optional[str] = None
    ) -> Application:
        """创建应聘记录"""
        application = Application(
            id=application_id,
            candidate_id=candidate_id,
            job_id=job_id,
            status=ApplicationStatus.NEW,
            resume_url=resume_url,
            resume_parsed_data=resume_parsed_data,
            source=source,
            hr_id=hr_id,
            applied_at=datetime.now()
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def get_status_history(
        db: Session,
        application_id: str
    ) -> list[ApplicationStatusHistory]:
        """获取状态历史"""
        return db.query(ApplicationStatusHistory).filter(
            ApplicationStatusHistory.application_id == application_id
        ).order_by(ApplicationStatusHistory.created_at.desc()).all()
