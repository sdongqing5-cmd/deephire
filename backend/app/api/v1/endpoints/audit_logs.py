"""Audit log query and CSV export endpoints."""

import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models import AuditLog

router = APIRouter()


def _require_hr(request: Request) -> dict:
    authorization = request.headers.get("Authorization", "")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(authorization[7:], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("role") != "hr":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="HR role required")
    return payload


def _query_logs(
    db: Session,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status_code: Optional[int] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
):
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if status_code:
        query = query.filter(AuditLog.status_code == status_code)
    if start_at:
        query = query.filter(AuditLog.created_at >= start_at)
    if end_at:
        query = query.filter(AuditLog.created_at <= end_at)
    return query.order_by(AuditLog.created_at.desc())


@router.get("")
def list_audit_logs(
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status_code: Optional[int] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    _require_hr(request)
    query = _query_logs(db, user_id, action, resource_type, status_code, start_at, end_at)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": [
            {
                "id": item.id,
                "request_id": item.request_id,
                "user_id": item.user_id,
                "user_email": item.user_email,
                "action": item.action,
                "resource_type": item.resource_type,
                "resource_id": item.resource_id,
                "method": item.method,
                "path": item.path,
                "status_code": item.status_code,
                "duration_ms": item.duration_ms,
                "ip_address": item.ip_address,
                "user_agent": item.user_agent,
                "details": item.details,
                "created_at": item.created_at,
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/export")
def export_audit_logs(
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    status_code: Optional[int] = None,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
):
    _require_hr(request)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["created_at", "request_id", "user_id", "user_email", "action", "method", "path", "status_code", "duration_ms", "ip_address"])
    for item in _query_logs(db, user_id, action, resource_type, status_code, start_at, end_at).yield_per(500):
        writer.writerow([item.created_at, item.request_id, item.user_id, item.user_email, item.action, item.method, item.path, item.status_code, item.duration_ms, item.ip_address])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit-logs.csv"})
