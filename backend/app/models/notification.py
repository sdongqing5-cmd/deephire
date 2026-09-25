"""Notification models - 通知模板、邮箱配置和发送日志"""

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.sql import func
from app.db.database import Base


class NotificationTemplate(Base):
    """面试通知模板"""
    __tablename__ = "notification_templates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    audience = Column(String, nullable=False, index=True)  # candidate, interviewer
    interview_type = Column(String, nullable=False, index=True)  # onsite, video
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MailboxConfig(Base):
    """发件邮箱配置"""
    __tablename__ = "mailbox_configs"

    id = Column(String, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # 163, qq, gmail
    email = Column(String, nullable=False)
    auth_code = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NotificationLog(Base):
    """通知发送日志"""
    __tablename__ = "notification_logs"

    id = Column(String, primary_key=True, index=True)
    candidate_email = Column(String)
    interviewer_email = Column(String)
    candidate_template_id = Column(String)
    interviewer_template_id = Column(String)
    interview_type = Column(String)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
