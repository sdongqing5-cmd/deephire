"""Interview Confirmation Service - 面试时间确认服务"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import secrets
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview, InterviewType, InterviewStatus
from app.services.application_service import ApplicationService


class InterviewConfirmationService:
    """面试时间确认服务"""

    @staticmethod
    def generate_confirmation_token() -> str:
        """生成确认token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    async def send_confirmation_email(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        interview_time_options: List[dict]  # [{"time": datetime, "location": str}, ...]
    ) -> Application:
        """发送面试时间确认邮件"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 生成确认token
        token = InterviewConfirmationService.generate_confirmation_token()
        application.interview_confirmation_token = token
        application.interview_notification_sent_at = datetime.now()

        # 存储时间选项（JSON格式）
        import json
        application.interview_flow_config = json.dumps({
            "time_options": [
                {
                    "time": opt["time"].isoformat(),
                    "location": opt.get("location"),
                    "duration": opt.get("duration", 60)
                }
                for opt in interview_time_options
            ]
        })

        db.commit()

        # TODO: 发送邮件
        # await EmailService.send_interview_time_confirmation(
        #     application=application,
        #     time_options=interview_time_options,
        #     confirm_url=f"{settings.FRONTEND_URL}/interviews/confirm/{token}",
        #     decline_url=f"{settings.FRONTEND_URL}/interviews/decline/{token}"
        # )

        db.refresh(application)
        return application

    @staticmethod
    async def candidate_confirm(
        db: Session,
        token: str,
        selected_time: datetime,
        selected_location: Optional[str] = None
    ) -> Application:
        """候选人确认面试时间"""

        application = db.query(Application).filter(
            Application.interview_confirmation_token == token
        ).first()

        if not application:
            raise ValueError("无效的确认链接")

        # 检查token是否已使用
        if application.interview_confirmed_at:
            raise ValueError("该确认链接已使用")

        # 记录确认时间
        application.interview_confirmed_at = datetime.now()
        db.commit()

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application.id,
            to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED,
            operator_id="candidate",
            operator_name="候选人",
            reason=f"候选人确认面试时间：{selected_time.isoformat()}"
        )

        # 创建部门面试记录
        interview = Interview(
            id=f"int_{datetime.now().timestamp()}",
            application_id=application.id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            interview_type=InterviewType.DEPARTMENT,
            title="部门面试",
            scheduled_at=selected_time,
            duration=60,
            location=selected_location,
            status=InterviewStatus.SCHEDULED
        )
        db.add(interview)
        db.commit()

        # TODO: 发送通知给面试官和候选人
        # await NotificationService.notify_interview_scheduled(interview)

        db.refresh(application)
        return application

    @staticmethod
    async def candidate_decline(
        db: Session,
        token: str,
        reason: Optional[str] = None
    ) -> Application:
        """候选人拒绝面试"""

        application = db.query(Application).filter(
            Application.interview_confirmation_token == token
        ).first()

        if not application:
            raise ValueError("无效的确认链接")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application.id,
            to_status=ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
            operator_id="candidate",
            operator_name="候选人",
            reason=f"候选人拒绝面试：{reason or '未提供原因'}"
        )

        db.refresh(application)
        return application

    @staticmethod
    def get_confirmation_status(
        db: Session,
        application_id: str
    ) -> dict:
        """获取确认状态"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        import json
        time_options = []
        if application.interview_flow_config:
            try:
                config = json.loads(application.interview_flow_config)
                time_options = config.get("time_options", [])
            except:
                pass

        return {
            "token": application.interview_confirmation_token,
            "notification_sent_at": application.interview_notification_sent_at.isoformat() if application.interview_notification_sent_at else None,
            "confirmed_at": application.interview_confirmed_at.isoformat() if application.interview_confirmed_at else None,
            "time_options": time_options,
            "is_confirmed": application.interview_confirmed_at is not None
        }

    @staticmethod
    async def resend_confirmation_email(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str
    ) -> Application:
        """重新发送确认邮件"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        if not application.interview_confirmation_token:
            raise ValueError("No confirmation token found")

        # 更新发送时间
        application.interview_notification_sent_at = datetime.now()
        db.commit()

        # TODO: 重新发送邮件
        # await EmailService.send_interview_time_confirmation(...)

        db.refresh(application)
        return application
