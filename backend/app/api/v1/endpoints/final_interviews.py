"""Final Interview API endpoints - HR复试和终面接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.interview import Interview, InterviewResult, InterviewType
from app.services.final_interview_service import FinalInterviewService

router = APIRouter()


# ==================== Pydantic Models ====================

class ScheduleHRReinterviewRequest(BaseModel):
    """安排HR复试请求"""
    application_id: str
    scheduled_at: datetime
    duration: int = 30
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    scorecard_template_id: Optional[str] = None


class ScheduleFinalInterviewRequest(BaseModel):
    """安排终面请求"""
    application_id: str
    interviewer_id: str
    interviewer_name: str
    scheduled_at: datetime
    duration: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    scorecard_template_id: Optional[str] = None


class CompleteInterviewRequest(BaseModel):
    """完成面试请求"""
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


# ==================== API Endpoints ====================

@router.post("/hr-reinterview/schedule", response_model=dict)
async def schedule_hr_reinterview(
    request: ScheduleHRReinterviewRequest,
    db: Session = Depends(get_db)
):
    """安排HR复试"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        interview = await FinalInterviewService.schedule_hr_reinterview(
            db=db,
            application_id=request.application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            scheduled_at=request.scheduled_at,
            duration=request.duration,
            location=request.location,
            meeting_link=request.meeting_link,
            scorecard_template_id=request.scorecard_template_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "application_id": interview.application_id,
                "interview_type": interview.interview_type.value,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/final-interview/schedule", response_model=dict)
async def schedule_final_interview(
    request: ScheduleFinalInterviewRequest,
    db: Session = Depends(get_db)
):
    """安排终面"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        interview = await FinalInterviewService.schedule_final_interview(
            db=db,
            application_id=request.application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            interviewer_id=request.interviewer_id,
            interviewer_name=request.interviewer_name,
            scheduled_at=request.scheduled_at,
            duration=request.duration,
            location=request.location,
            meeting_link=request.meeting_link,
            scorecard_template_id=request.scorecard_template_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "application_id": interview.application_id,
                "interview_type": interview.interview_type.value,
                "interviewer_name": interview.interviewer_name,
                "scheduled_at": interview.scheduled_at.isoformat(),
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/start", response_model=dict)
async def start_interview(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """开始面试（HR复试或终面）"""
    try:
        # TODO: 获取当前面试官的ID和姓名
        interviewer_id = "current_user_id"
        interviewer_name = "当前用户"

        interview = await FinalInterviewService.start_interview(
            db=db,
            interview_id=interview_id,
            interviewer_id=interviewer_id,
            interviewer_name=interviewer_name
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "interview_id": interview.id,
                "interview_type": interview.interview_type.value,
                "status": interview.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interview_id}/complete", response_model=dict)
async def complete_interview(
    interview_id: str,
    request: CompleteInterviewRequest,
    db: Session = Depends(get_db)
):
    """完成面试并填写评价表"""
    try:
        # TODO: 获取当前面试官的ID和姓名
        interviewer_id = "current_user_id"
        interviewer_name = "当前用户"

        # 将字符串转换为枚举
        result = InterviewResult(request.result)

        interview = await FinalInterviewService.complete_interview(
            db=db,
            interview_id=interview_id,
            interviewer_id=interviewer_id,
            interviewer_name=interviewer_name,
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
                "interview_type": interview.interview_type.value,
                "result": interview.result.value,
                "application_status": application.status.value if application else None,
                "completed_at": interview.completed_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_id}", response_model=dict)
async def get_interview(
    interview_id: str,
    db: Session = Depends(get_db)
):
    """获取面试详情"""
    try:
        interview = FinalInterviewService.get_by_id(db=db, interview_id=interview_id)
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
                "meeting_link": interview.meeting_link,
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
async def get_interviews_by_application(
    application_id: str,
    interview_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取应聘记录的面试（HR复试和终面）"""
    try:
        # 转换interview_type
        type_enum = None
        if interview_type:
            type_enum = InterviewType(interview_type)

        interviews = FinalInterviewService.get_by_application(
            db=db,
            application_id=application_id,
            interview_type=type_enum
        )

        items = []
        for interview in interviews:
            items.append({
                "id": interview.id,
                "interview_type": interview.interview_type.value,
                "interviewer_name": interview.interviewer_name,
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
async def cancel_interview(
    interview_id: str,
    request: CancelInterviewRequest,
    db: Session = Depends(get_db)
):
    """取消面试"""
    try:
        interview = FinalInterviewService.cancel_interview(
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
async def reschedule_interview(
    interview_id: str,
    request: RescheduleInterviewRequest,
    db: Session = Depends(get_db)
):
    """改期面试"""
    try:
        interview = FinalInterviewService.reschedule_interview(
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
