"""Offer Service - Offer管理服务"""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationStatus
from app.services.application_service import ApplicationService


class OfferService:
    """Offer管理服务"""

    @staticmethod
    async def start_salary_negotiation(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        proposed_salary: int,
        negotiation_notes: Optional[str] = None
    ) -> Application:
        """开始薪资谈判"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.SALARY_NEGOTIATION,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"开始薪资谈判，提议薪资：{proposed_salary}"
        )

        # TODO: 记录薪资谈判信息到单独的表
        # 这里简化处理，实际应该有专门的salary_negotiations表

        db.refresh(application)
        return application

    @staticmethod
    async def accept_verbal_offer(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        agreed_salary: int,
        notes: Optional[str] = None
    ) -> Application:
        """候选人接受口头offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.VERBAL_OFFER_ACCEPTED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"接受口头offer，薪资：{agreed_salary}"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def submit_offer_approval(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        offer_details: dict
    ) -> Application:
        """提交offer审批"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_APPROVAL,
            operator_id=hr_id,
            operator_name=hr_name,
            reason="提交offer审批"
        )

        # TODO: 创建审批流程
        # await ApprovalService.create_offer_approval(application_id, offer_details)

        db.refresh(application)
        return application

    @staticmethod
    async def approve_offer(
        db: Session,
        application_id: str,
        approver_id: str,
        approver_name: str,
        comments: Optional[str] = None
    ) -> Application:
        """审批通过offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_APPROVED,
            operator_id=approver_id,
            operator_name=approver_name,
            reason=f"Offer审批通过：{comments or ''}"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def reject_offer_approval(
        db: Session,
        application_id: str,
        approver_id: str,
        approver_name: str,
        reason: str
    ) -> Application:
        """审批拒绝offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_APPROVAL_REJECTED,
            operator_id=approver_id,
            operator_name=approver_name,
            reason=f"Offer审批拒绝：{reason}"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def send_offer(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        offer_letter_url: str,
        valid_until: datetime
    ) -> Application:
        """发送正式offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_SENT,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"发送正式offer，有效期至：{valid_until.isoformat()}"
        )

        # TODO: 发送offer邮件
        # await EmailService.send_offer_letter(application, offer_letter_url, valid_until)

        db.refresh(application)
        return application

    @staticmethod
    async def candidate_accept_offer(
        db: Session,
        application_id: str,
        signature_url: Optional[str] = None
    ) -> Application:
        """候选人接受offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_ACCEPTED,
            operator_id="candidate",
            operator_name="候选人",
            reason="候选人接受offer"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def candidate_decline_offer(
        db: Session,
        application_id: str,
        reason: Optional[str] = None
    ) -> Application:
        """候选人拒绝offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_DECLINED,
            operator_id="candidate",
            operator_name="候选人",
            reason=f"候选人拒绝offer：{reason or '未提供原因'}"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def prepare_onboarding(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        expected_start_date: datetime
    ) -> Application:
        """准备入职"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.PENDING_ONBOARD,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"准备入职，预计入职日期：{expected_start_date.isoformat()}"
        )

        # TODO: 发送入职信息采集邮件
        # await EmailService.send_onboarding_info_collection(application)

        db.refresh(application)
        return application

    @staticmethod
    async def complete_onboarding(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        actual_start_date: datetime
    ) -> Application:
        """完成入职"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.ONBOARDED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"完成入职，实际入职日期：{actual_start_date.isoformat()}"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def cancel_onboarding(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        reason: str
    ) -> Application:
        """取消入职"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.ONBOARDING_CANCELLED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"取消入职：{reason}"
        )

        db.refresh(application)
        return application
