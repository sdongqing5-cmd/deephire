"""Interview Confirmation API endpoints - 面试时间确认接口"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.services.interview_confirmation_service import InterviewConfirmationService

router = APIRouter()


# ==================== Pydantic Models ====================

class TimeOption(BaseModel):
    """时间选项"""
    time: datetime
    location: Optional[str] = None
    duration: Optional[int] = 60


class SendConfirmationEmailRequest(BaseModel):
    """发送确认邮件请求"""
    interview_time_options: List[TimeOption]


class CandidateConfirmRequest(BaseModel):
    """候选人确认请求"""
    token: str
    selected_time: datetime
    selected_location: Optional[str] = None


class CandidateDeclineRequest(BaseModel):
    """候选人拒绝请求"""
    token: str
    reason: Optional[str] = None


# ==================== API Endpoints ====================

@router.post("/applications/{application_id}/send-confirmation-email", response_model=dict)
async def send_confirmation_email(
    application_id: str,
    request: SendConfirmationEmailRequest,
    db: Session = Depends(get_db)
):
    """发送面试时间确认邮件"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        # 转换时间选项
        time_options = [
            {
                "time": opt.time,
                "location": opt.location,
                "duration": opt.duration
            }
            for opt in request.interview_time_options
        ]

        application = await InterviewConfirmationService.send_confirmation_email(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            interview_time_options=time_options
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "token": application.interview_confirmation_token,
                "notification_sent_at": application.interview_notification_sent_at.isoformat() if application.interview_notification_sent_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interviews/confirm", response_model=dict)
async def candidate_confirm_interview(
    request: CandidateConfirmRequest,
    db: Session = Depends(get_db)
):
    """候选人确认面试时间（公开接口，无需认证）"""
    try:
        application = await InterviewConfirmationService.candidate_confirm(
            db=db,
            token=request.token,
            selected_time=request.selected_time,
            selected_location=request.selected_location
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "confirmed_at": application.interview_confirmed_at.isoformat() if application.interview_confirmed_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interviews/decline", response_model=dict)
async def candidate_decline_interview(
    request: CandidateDeclineRequest,
    db: Session = Depends(get_db)
):
    """候选人拒绝面试（公开接口，无需认证）"""
    try:
        application = await InterviewConfirmationService.candidate_decline(
            db=db,
            token=request.token,
            reason=request.reason
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications/{application_id}/confirmation-status", response_model=dict)
async def get_confirmation_status(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取面试时间确认状态"""
    try:
        status = InterviewConfirmationService.get_confirmation_status(
            db=db,
            application_id=application_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": status
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/resend-confirmation-email", response_model=dict)
async def resend_confirmation_email(
    application_id: str,
    db: Session = Depends(get_db)
):
    """重新发送确认邮件"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await InterviewConfirmationService.resend_confirmation_email(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "notification_sent_at": application.interview_notification_sent_at.isoformat() if application.interview_notification_sent_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
