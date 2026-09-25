"""System audit log model."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class AuditLog(Base):
    """Immutable record of API operations and security-relevant events."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    request_id = Column(String, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user_email = Column(String, index=True)
    action = Column(String, index=True, nullable=False)
    resource_type = Column(String, index=True)
    resource_id = Column(String, index=True)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Integer)
    ip_address = Column(String)
    user_agent = Column(Text)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
