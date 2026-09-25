"""Persistence helpers for system audit events."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog


def record_audit_event(db: Session, **values: Any) -> AuditLog:
    event = AuditLog(id=str(uuid.uuid4()), **values)
    db.add(event)
    db.commit()
    return event
