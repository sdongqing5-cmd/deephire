"""HR Interview API endpoints - HR初筛面试接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.interview import Interview, InterviewResult
from app.services.hr_interview_service import HRInterviewService

router = APIRouter()


# ==================== Pydantic Models ====================

class ScheduleHRInterviewRequest(BaseModel):
    """安排HR初筛面试请求"""
    application_id: str
    scheduled_at: datetime
    duration: int = 30
    location: Optional[str] = None
    scorecard_template_id: Optional[str] = None


class CompleteHRInterviewRequest(BaseModel):
    """完成HR初筛面试请求"""
    result: str  # pass, fail, hold
    feedback: str
    score: int
    evaluation_data: dict


class RescheduleInterviewRequest(BaseModel):
    """改期面试请求"""
    new_scheduled_at: datetime
    reason: str


class CancelInterviewRequest(BaseModel):
    """取消面试请求"""
    reason: str


class InterviewResponse(BaseModel):
    """面试记录响应"""
    id: str
    application_id: str
    interview_type: str
    title: Optional[str]
    interviewer_name: Optional[str]
    scheduled_at: datetime
    duration: int
    location: Optional[str]
    status: str
    result: Optional[str]
    score: Optional[int]
    feedback: Optional[str]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== API Endpoints ====================

@router.post("/schedule", response_model=dict)
async def schedule_hr_interview(
    request: ScheduleHRInterviewRequest,
    db: Session = Depends(get_db)
):
    """安排HR初筛面试"""
    try:
        # TODO: 获取当前用户ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        interview = await HRInterviewService.schedule_hr_interview(
            db=db,
            application_id=request.application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            scheduled_at=request.scheduled_at,
            duration=request.duration,
            location=request.location,
            scorecard_template_id=request.scorecard_template_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "application_id": interview.application_id,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/start", response_model=dict)
async def start_hr_interview(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """开始HR初筛面试"""
    try:
        # TODO: 获取当前用户ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        interview = await HRInterviewService.start_interview(
            db=db,
            interview_id=interview_id,
            hr_id=hr_id,
            hr_name=hr_name
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/complete", response_model=dict)
async def complete_hr_interview(
    interview_id: str,
    request: CompleteHRInterviewRequest,
    db: Session = Depends(get_db)
):
    """完成HR初筛面试并填写评价表"""
    try:
        # TODO: 获取当前用户ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        # 将字符串转换为枚举
        result = InterviewResult(request.result)

        interview = await HRInterviewService.complete_interview(
            db=db,
            interview_id=interview_id,
            hr_id=hr_id,
            hr_name=hr_name,
            result=result,
            feedback=request.feedback,
            score=request.score,
            evaluation_data=request.evaluation_data
        )

        # 获取应聘记录状态
        from app.models.application import Application
        application = db.query(Application).filter(
            Application.id == interview.application_id
        ).first()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "result": interview.result.value,
                "application_status": application.status.value if application else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_id}", response_model=dict)
async def get_hr_interview(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """获取HR初筛面试详情"""
    try:
        interview = HRInterviewService.get_by_id(db=db, interview_id=interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")

        return {
            "code": 0,
            "message": "success",
            "data": {
                "id": interview.id,
                "application_id": interview.application_id,
                "interview_type": interview.interview_type.value,
                "title": interview.title,
                "interviewer_name": interview.interviewer_name,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "duration": interview.duration,
                "location": interview.location,
                "status": interview.status.value,
                "result": interview.result.value if interview.result else None,
                "score": interview.score,
                "feedback": interview.feedback,
                "evaluation_data": interview.evaluation_data,
                "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/application/{application_id}", response_model=dict)
async def get_hr_interviews_by_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取应聘记录的所有HR初筛面试"""
    try:
        interviews = HRInterviewService.get_by_application(
            db=db,
            application_id=application_id
        )

        items = []
        for interview in interviews:
            items.append({
                "id": interview.id,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "status": interview.status.value,
                "result": interview.result.value if interview.result else None,
                "score": interview.score,
            })

        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": items
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/cancel", response_model=dict)
async def cancel_hr_interview(
    interview_id: str,
    request: CancelInterviewRequest,
    db: Session = Depends(get_db)
):
    """取消HR初筛面试"""
    try:
        interview = HRInterviewService.cancel_interview(
            db=db,
            interview_id=interview_id,
            reason=request.reason
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/reschedule", response_model=dict)
async def reschedule_hr_interview(
    interview_id: str,
    request: RescheduleInterviewRequest,
    db: Session = Depends(get_db)
):
    """改期HR初筛面试"""
    try:
        interview = HRInterviewService.reschedule_interview(
            db=db,
            interview_id=interview_id,
            new_scheduled_at=request.new_scheduled_at,
            reason=request.reason
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
