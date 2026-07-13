"""Interview Intention Service - 面试意向沟通服务"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationStatus
from app.services.application_service import ApplicationService


class InterviewIntentionService:
    """面试意向沟通服务"""

    @staticmethod
    async def initiate_contact(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        contact_method: str  # "ai_call" or "manual"
    ) -> Application:
        """发起面试意向沟通"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态到面试意向沟通
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION,
            operator_id=hr_id,
            operator_name=hr_name,
            reason="开始面试意向沟通"
        )

        # 记录沟通方式
        application.intention_contact_method = contact_method
        application.intention_contacted_at = datetime.now()
        application.intention_contacted_by = hr_id

        if contact_method == "ai_call":
            # TODO: 调用智能外呼服务
            # await AICallService.initiate_call(
            #     phone=application.candidate.phone,
            #     callback_url=f"/api/v1/applications/{application_id}/intention-callback"
            # )
            pass

        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    async def record_contact_result(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        result: str,  # "agreed", "declined", "no_answer"
        notes: Optional[str] = None
    ) -> Application:
        """记录沟通结果"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 更新沟通结果
        application.intention_contact_result = result
        application.intention_contact_notes = notes
        db.commit()

        # 根据结果转换状态
        if result == "agreed":
            # 候选人同意面试，进入时间确认环节
            await ApplicationService.transition_status(
                db=db,
                application_id=application_id,
                to_status=ApplicationStatus.INTERVIEW_TIME_CONFIRMING,
                operator_id=hr_id,
                operator_name=hr_name,
                reason="候选人同意面试"
            )
        elif result == "declined":
            # 候选人拒绝面试
            await ApplicationService.transition_status(
                db=db,
                application_id=application_id,
                to_status=ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
                operator_id=hr_id,
                operator_name=hr_name,
                reason="候选人拒绝面试"
            )
        elif result == "no_answer":
            # 无人接听，保持当前状态，可以稍后重试
            pass

        db.refresh(application)
        return application

    @staticmethod
    async def handle_ai_call_callback(
        db: Session,
        application_id: str,
        call_result: dict
    ) -> Application:
        """处理智能外呼回调"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 解析外呼结果
        result = call_result.get('result')  # "agreed", "declined", "no_answer"
        transcript = call_result.get('transcript')  # 通话记录

        # 更新沟通结果
        application.intention_contact_result = result
        application.intention_contact_notes = f"智能外呼结果：{transcript}"
        db.commit()

        # 根据结果转换状态
        if result == "agreed":
            await ApplicationService.transition_status(
                db=db,
                application_id=application_id,
                to_status=ApplicationStatus.INTERVIEW_TIME_CONFIRMING,
                operator_id="system",
                operator_name="智能外呼系统",
                reason="候选人同意面试（智能外呼）"
            )
        elif result == "declined":
            await ApplicationService.transition_status(
                db=db,
                application_id=application_id,
                to_status=ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
                operator_id="system",
                operator_name="智能外呼系统",
                reason="候选人拒绝面试（智能外呼）"
            )

        db.refresh(application)
        return application

    @staticmethod
    def get_contact_history(
        db: Session,
        application_id: str
    ) -> dict:
        """获取沟通历史"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        return {
            "contact_method": application.intention_contact_method,
            "contact_result": application.intention_contact_result,
            "contact_notes": application.intention_contact_notes,
            "contacted_at": application.intention_contacted_at.isoformat() if application.intention_contacted_at else None,
            "contacted_by": application.intention_contacted_by
        }
