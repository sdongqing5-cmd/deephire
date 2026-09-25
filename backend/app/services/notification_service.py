"""Notification service - 邮件模板和发送"""

from datetime import datetime
from email.message import EmailMessage
from typing import Optional
import smtplib
import uuid

from sqlalchemy.orm import Session

from app.models.notification import MailboxConfig, NotificationLog, NotificationTemplate


SMTP_HOSTS = {
    "163": ("smtp.163.com", 465),
    "qq": ("smtp.qq.com", 465),
    "gmail": ("smtp.gmail.com", 465),
}


DEFAULT_TEMPLATES = [
    ("candidate_onsite", "候选人现场面试通知", "candidate", "onsite", "面试邀请：{jobTitle}", "{candidateName}您好，请于{time}到{location}参加现场面试。"),
    ("candidate_video", "候选人视频面试通知", "candidate", "video", "视频面试邀请：{jobTitle}", "{candidateName}您好，请于{time}通过会议链接参加视频面试：{meetingLink}"),
    ("interviewer_onsite", "面试官现场面试通知", "interviewer", "onsite", "面试安排：{candidateName}", "请于{time}在{location}面试候选人{candidateName}，应聘职位：{jobTitle}。"),
    ("interviewer_video", "面试官视频面试通知", "interviewer", "video", "视频面试安排：{candidateName}", "请于{time}通过会议链接面试候选人{candidateName}：{meetingLink}"),
]


class NotificationService:
    """通知模板、邮箱配置和发送服务。"""

    @staticmethod
    def ensure_default_templates(db: Session) -> None:
        for template_id, name, audience, interview_type, subject, body in DEFAULT_TEMPLATES:
            exists = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
            if exists:
                continue
            db.add(NotificationTemplate(
                id=template_id,
                name=name,
                audience=audience,
                interview_type=interview_type,
                subject=subject,
                body=body,
            ))
        db.commit()

    @staticmethod
    def list_templates(db: Session, interview_type: Optional[str] = None) -> list[NotificationTemplate]:
        NotificationService.ensure_default_templates(db)
        query = db.query(NotificationTemplate).filter(NotificationTemplate.is_active == True)
        if interview_type:
            query = query.filter(NotificationTemplate.interview_type == interview_type)
        return query.order_by(NotificationTemplate.audience.asc(), NotificationTemplate.name.asc()).all()

    @staticmethod
    def upsert_template(db: Session, data: dict) -> NotificationTemplate:
        template_id = data.get("id") or f"tpl_{uuid.uuid4().hex[:12]}"
        template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
        if not template:
            template = NotificationTemplate(id=template_id)
            db.add(template)

        for field in ["name", "audience", "interview_type", "subject", "body"]:
            setattr(template, field, data[field])
        template.is_active = data.get("is_active", True)
        template.updated_at = datetime.now()
        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def save_mailbox(db: Session, provider: str, email: str, auth_code: str) -> MailboxConfig:
        db.query(MailboxConfig).update({MailboxConfig.is_active: False})
        mailbox = MailboxConfig(
            id=f"mail_{uuid.uuid4().hex[:12]}",
            provider=provider,
            email=email,
            auth_code=auth_code,
            is_active=True,
        )
        db.add(mailbox)
        db.commit()
        db.refresh(mailbox)
        return mailbox

    @staticmethod
    def get_active_mailbox(db: Session) -> Optional[MailboxConfig]:
        return db.query(MailboxConfig).filter(MailboxConfig.is_active == True).order_by(MailboxConfig.created_at.desc()).first()

    @staticmethod
    def render(template: NotificationTemplate, context: dict) -> tuple[str, str]:
        safe_context = {key: value or "" for key, value in context.items()}
        return template.subject.format_map(safe_context), template.body.format_map(safe_context)

    @staticmethod
    def _send_one(mailbox: MailboxConfig, to_email: str, subject: str, body: str) -> None:
        host, port = SMTP_HOSTS[mailbox.provider]
        message = EmailMessage()
        message["From"] = mailbox.email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP_SSL(host, port, timeout=20) as smtp:
            smtp.login(mailbox.email, mailbox.auth_code)
            smtp.send_message(message)

    @staticmethod
    def send_interview_notification(
        db: Session,
        candidate_template_id: str,
        interviewer_template_id: str,
        context: dict,
    ) -> NotificationLog:
        candidate_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == candidate_template_id).first()
        interviewer_template = db.query(NotificationTemplate).filter(NotificationTemplate.id == interviewer_template_id).first()
        if not candidate_template or not interviewer_template:
            raise ValueError("通知模板不存在")

        log = NotificationLog(
            id=f"ntf_{uuid.uuid4().hex[:12]}",
            candidate_email=context.get("candidateEmail"),
            interviewer_email=context.get("interviewerEmail"),
            candidate_template_id=candidate_template_id,
            interviewer_template_id=interviewer_template_id,
            interview_type=context.get("interviewType"),
            status="pending",
        )
        db.add(log)
        db.commit()

        mailbox = NotificationService.get_active_mailbox(db)
        if not mailbox:
            log.status = "failed"
            log.error_message = "未绑定发件邮箱"
            db.commit()
            db.refresh(log)
            return log

        try:
            candidate_subject, candidate_body = NotificationService.render(candidate_template, context)
            interviewer_subject, interviewer_body = NotificationService.render(interviewer_template, context)
            NotificationService._send_one(mailbox, context["candidateEmail"], candidate_subject, candidate_body)
            NotificationService._send_one(mailbox, context["interviewerEmail"], interviewer_subject, interviewer_body)
            log.status = "sent"
            log.sent_at = datetime.now()
        except Exception as exc:
            log.status = "failed"
            log.error_message = str(exc)

        db.commit()
        db.refresh(log)
        return log
