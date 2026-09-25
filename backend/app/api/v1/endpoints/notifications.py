"""Notification endpoints - 通知管理接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.notification_service import NotificationService

router = APIRouter()


class TemplateRequest(BaseModel):
    id: Optional[str] = None
    name: str
    audience: str
    interview_type: str
    subject: str
    body: str
    is_active: bool = True


class MailboxRequest(BaseModel):
    provider: str
    email: str
    auth_code: str


class SendInterviewNotificationRequest(BaseModel):
    candidate_template_id: str
    interviewer_template_id: str
    context: dict


@router.get("/templates", response_model=dict)
async def list_templates(
    interview_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    templates = NotificationService.list_templates(db, interview_type)
    return {
        "code": 0,
        "data": [
            {
                "id": template.id,
                "name": template.name,
                "audience": template.audience,
                "interviewType": template.interview_type,
                "subject": template.subject,
                "body": template.body,
                "is_active": template.is_active,
            }
            for template in templates
        ],
    }


@router.post("/templates", response_model=dict)
async def save_template(
    request: TemplateRequest,
    db: Session = Depends(get_db),
):
    try:
        template = NotificationService.upsert_template(
            db,
            {
                **request.model_dump(),
                "interview_type": request.interview_type,
            },
        )
        return {"code": 0, "data": {"id": template.id}}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/mailbox", response_model=dict)
async def save_mailbox(
    request: MailboxRequest,
    db: Session = Depends(get_db),
):
    if request.provider not in {"163", "qq", "gmail"}:
        raise HTTPException(status_code=400, detail="邮箱服务只支持 163、qq、gmail")
    mailbox = NotificationService.save_mailbox(db, request.provider, request.email, request.auth_code)
    return {
        "code": 0,
        "data": {
            "id": mailbox.id,
            "provider": mailbox.provider,
            "email": mailbox.email,
        },
    }


@router.get("/mailbox", response_model=dict)
async def get_mailbox(db: Session = Depends(get_db)):
    mailbox = NotificationService.get_active_mailbox(db)
    return {
        "code": 0,
        "data": {
            "provider": mailbox.provider,
            "email": mailbox.email,
        } if mailbox else None,
    }


@router.post("/send-interview", response_model=dict)
async def send_interview_notification(
    request: SendInterviewNotificationRequest,
    db: Session = Depends(get_db),
):
    try:
        log = NotificationService.send_interview_notification(
            db=db,
            candidate_template_id=request.candidate_template_id,
            interviewer_template_id=request.interviewer_template_id,
            context=request.context,
        )
        return {
            "code": 0 if log.status == "sent" else 1,
            "message": "发送成功" if log.status == "sent" else log.error_message,
            "data": {
                "id": log.id,
                "status": log.status,
                "error_message": log.error_message,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
