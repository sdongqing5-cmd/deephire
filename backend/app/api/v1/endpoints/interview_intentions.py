"""Interview Intention API endpoints - 面试意向沟通接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.services.interview_intention_service import InterviewIntentionService

router = APIRouter()


# ==================== Pydantic Models ====================

class InitiateContactRequest(BaseModel):
    """发起沟通请求"""
    contact_method: str  # "ai_call" or "manual"


class RecordContactResultRequest(BaseModel):
    """记录沟通结果请求"""
    result: str  # "agreed", "declined", "no_answer"
    notes: Optional[str] = None


class AICallCallbackRequest(BaseModel):
    """智能外呼回调请求"""
    result: str  # "agreed", "declined", "no_answer"
    transcript: Optional[str] = None
    call_duration: Optional[int] = None
    call_time: Optional[datetime] = None


# ==================== API Endpoints ====================

@router.post("/applications/{application_id}/initiate-intention-contact", response_model=dict)
async def initiate_intention_contact(
    application_id: str,
    request: InitiateContactRequest,
    db: Session = Depends(get_db)
):
    """发起面试意向沟通"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        # 验证contact_method
        if request.contact_method not in ["ai_call", "manual"]:
            raise HTTPException(status_code=400, detail="Invalid contact_method")

        application = await InterviewIntentionService.initiate_contact(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            contact_method=request.contact_method
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "contact_method": application.intention_contact_method,
                "contacted_at": application.intention_contacted_at.isoformat() if application.intention_contacted_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/record-intention-result", response_model=dict)
async def record_intention_result(
    application_id: str,
    request: RecordContactResultRequest,
    db: Session = Depends(get_db)
):
    """记录面试意向沟通结果"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        # 验证result
        if request.result not in ["agreed", "declined", "no_answer"]:
            raise HTTPException(status_code=400, detail="Invalid result")

        application = await InterviewIntentionService.record_contact_result(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            result=request.result,
            notes=request.notes
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "contact_result": application.intention_contact_result,
                "contact_notes": application.intention_contact_notes
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/intention-callback", response_model=dict)
async def handle_intention_callback(
    application_id: str,
    request: AICallCallbackRequest,
    db: Session = Depends(get_db)
):
    """处理智能外呼回调"""
    try:
        # 验证result
        if request.result not in ["agreed", "declined", "no_answer"]:
            raise HTTPException(status_code=400, detail="Invalid result")

        call_result = {
            "result": request.result,
            "transcript": request.transcript,
            "call_duration": request.call_duration,
            "call_time": request.call_time.isoformat() if request.call_time else None
        }

        application = await InterviewIntentionService.handle_ai_call_callback(
            db=db,
            application_id=application_id,
            call_result=call_result
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "contact_result": application.intention_contact_result
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applications/{application_id}/intention-history", response_model=dict)
async def get_intention_history(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取面试意向沟通历史"""
    try:
        history = InterviewIntentionService.get_contact_history(
            db=db,
            application_id=application_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": history
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
