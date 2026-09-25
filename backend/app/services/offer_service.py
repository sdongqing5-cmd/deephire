"""Offer Service - Offer管理服务"""

from typing import Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.application_service import ApplicationService
from app.services.application_state_machine import ApplicationStateMachine


class OfferService:
    """Offer管理服务"""

    OFFER_STATUSES = [
        ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED,
        ApplicationStatus.ASSESSMENT_COMPLETED,
        ApplicationStatus.HR_REINTERVIEW_COMPLETED,
        ApplicationStatus.FINAL_INTERVIEW_COMPLETED,
        ApplicationStatus.VERBAL_OFFER_ACCEPTED,
        ApplicationStatus.OFFER_APPROVAL,
        ApplicationStatus.OFFER_APPROVAL_REJECTED,
        ApplicationStatus.OFFER_PENDING,
        ApplicationStatus.OFFER_SENT,
        ApplicationStatus.OFFER_NOT_AGREED,
        ApplicationStatus.OFFER_REJECTED,
        ApplicationStatus.OFFER_ACCEPTED,
    ]

    ONBOARDING_STATUSES = [
        ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.PENDING_ONBOARD,
        ApplicationStatus.ONBOARD_CANCELLED,
        ApplicationStatus.ONBOARDED,
    ]

    @staticmethod
    def _append_history(
        db: Session,
        application: Application,
        operator_id: str,
        operator_name: str,
        reason: str,
        to_status: Optional[ApplicationStatus] = None,
    ) -> ApplicationStatusHistory:
        """记录不一定改变主状态的业务操作。"""
        history = ApplicationStatusHistory(
            id=f"ash_{datetime.now().timestamp()}",
            application_id=application.id,
            from_status=application.status,
            to_status=to_status or application.status,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=reason,
        )
        db.add(history)
        application.last_status_change_at = datetime.now()
        db.commit()
        db.refresh(application)
        return history

    @staticmethod
    def list_by_module(
        db: Session,
        module: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """获取 Offer 或入职模块列表。"""
        statuses = OfferService.OFFER_STATUSES if module == "offer" else OfferService.ONBOARDING_STATUSES
        query = db.query(Application).filter(Application.status.in_(statuses))

        if status:
            query = query.filter(Application.status == ApplicationStatus(status))

        applications = (
            query.order_by(Application.last_status_change_at.desc().nullslast(), Application.applied_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        items = []
        for application in applications:
            candidate = db.query(Candidate).filter(Candidate.id == application.candidate_id).first()
            job = db.query(Job).filter(Job.id == application.job_id).first()
            latest_history = (
                db.query(ApplicationStatusHistory)
                .filter(ApplicationStatusHistory.application_id == application.id)
                .order_by(ApplicationStatusHistory.created_at.desc())
                .first()
            )
            items.append({
                "id": application.id,
                "candidate": {
                    "id": candidate.id if candidate else None,
                    "name": candidate.name if candidate else "未知",
                    "phone": candidate.phone if candidate else None,
                    "email": candidate.email if candidate else None,
                },
                "job": {
                    "id": job.id if job else None,
                    "title": job.title if job else "未知",
                    "location": job.location if job else None,
                },
                "status": application.status.value,
                "status_label": ApplicationStateMachine.get_status_label(application.status),
                "latest_action": latest_history.reason if latest_history else None,
                "offer_details": json.loads(application.offer_details) if application.offer_details else None,
                "onboarding_attachments": json.loads(application.onboarding_attachments) if application.onboarding_attachments else [],
                "updated_at": (
                    application.last_status_change_at.isoformat()
                    if application.last_status_change_at
                    else application.applied_at.isoformat() if application.applied_at else None
                ),
            })

        return items

    @staticmethod
    async def record_offer(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        offer_details: dict,
    ) -> Application:
        """录入 Offer 信息，并让候选人进入待发 Offer。"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        application.offer_details = json.dumps(offer_details, ensure_ascii=False)
        if application.status != ApplicationStatus.OFFER_PENDING:
            await ApplicationService.transition_status(
                db=db,
                application_id=application_id,
                to_status=ApplicationStatus.OFFER_PENDING,
                operator_id=hr_id,
                operator_name=hr_name,
                reason="录入Offer，进入待发Offer",
            )
        else:
            OfferService._append_history(db, application, hr_id, hr_name, "更新Offer录入信息")

        db.refresh(application)
        return application

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

        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_PENDING,
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
        signature_url: Optional[str] = None,
        operator_id: str = "2",
        operator_name: str = "Recruiter",
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
            operator_id=operator_id,
            operator_name=operator_name,
            reason=f"记录候选人反馈：接受Offer{f'，签署文件：{signature_url}' if signature_url else ''}"
        )

        db.refresh(application)
        return application

    @staticmethod
    async def candidate_decline_offer(
        db: Session,
        application_id: str,
        reason: Optional[str] = None,
        operator_id: str = "2",
        operator_name: str = "Recruiter",
    ) -> Application:
        """候选人拒绝offer"""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        # 转换状态
        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_REJECTED,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=f"记录候选人反馈：拒绝Offer，原因：{reason or '未提供原因'}"
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
    async def notify_information_collection(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        due_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Application:
        """通知候选人采集入职信息。"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        reason = "发送入职信息采集通知"
        if due_date:
            reason += f"，截止时间：{due_date.isoformat()}"
        if notes:
            reason += f"，备注：{notes}"

        OfferService._append_history(db, application, hr_id, hr_name, reason)
        return application

    @staticmethod
    async def reschedule_onboarding(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        expected_start_date: datetime,
        reason: Optional[str] = None,
    ) -> Application:
        """改期入职。"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        OfferService._append_history(
            db,
            application,
            hr_id,
            hr_name,
            f"改期入职，新入职日期：{expected_start_date.isoformat()}，原因：{reason or '未填写'}",
        )
        return application

    @staticmethod
    async def edit_offer(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        offer_details: dict,
    ) -> Application:
        """记录 Offer 编辑信息。"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        application.offer_details = json.dumps(offer_details, ensure_ascii=False)
        summary_fields = [
            offer_details.get("company"),
            offer_details.get("contract_entity"),
            offer_details.get("department"),
            offer_details.get("base_city"),
            offer_details.get("salary"),
            offer_details.get("start_date"),
        ]
        summary = " / ".join(str(value) for value in summary_fields if value)
        OfferService._append_history(
            db,
            application,
            hr_id,
            hr_name,
            f"Offer编辑：{summary or '已更新录用信息'}",
        )
        return application

    @staticmethod
    async def reject_at_offer_stage(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        reason: str,
    ) -> Application:
        """Offer阶段淘汰候选人，标记为 Offer 没谈拢。"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.OFFER_NOT_AGREED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"Offer没谈拢：{reason}",
        )
        db.refresh(application)
        return application

    @staticmethod
    async def add_onboarding_attachment(
        db: Session,
        application_id: str,
        hr_id: str,
        hr_name: str,
        attachment: dict,
    ) -> Application:
        """记录入职附件。"""
        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        attachments = json.loads(application.onboarding_attachments) if application.onboarding_attachments else []
        attachments.append({
            "name": attachment.get("name") or "入职附件",
            "url": attachment.get("url") or "",
            "uploaded_at": datetime.now().isoformat(),
        })
        application.onboarding_attachments = json.dumps(attachments, ensure_ascii=False)
        OfferService._append_history(
            db,
            application,
            hr_id,
            hr_name,
            f"上传入职附件：{attachments[-1]['name']}",
        )
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
            to_status=ApplicationStatus.ONBOARD_CANCELLED,
            operator_id=hr_id,
            operator_name=hr_name,
            reason=f"取消入职：{reason}"
        )

        db.refresh(application)
        return application
