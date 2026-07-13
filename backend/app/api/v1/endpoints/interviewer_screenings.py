"""Interviewer Screening API endpoints - 面试官筛选接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.interviewer_screening import InterviewerScreening, ScreeningResult
from app.services.interviewer_screening_service import InterviewerScreeningService

router = APIRouter()


# ==================== Pydantic Models ====================

class PushToInterviewerRequest(BaseModel):
    """推送给面试官请求"""
    interviewer_id: str
    interviewer_name: str
    comments: Optional[str] = None


class SubmitScreeningResultRequest(BaseModel):
    """提交筛选结果请求"""
    result: str  # pass, reject
    comments: str


class ScreeningResponse(BaseModel):
    """筛选记录响应"""
    id: str
    application_id: str
    interviewer_id: str
    interviewer_name: str
    result: Optional[str]
    comments: Optional[str]
    created_at: datetime
    screened_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== API Endpoints ====================

@router.post("/applications/{application_id}/push-to-interviewer", response_model=dict)
async def push_to_interviewer(
    application_id: str,
    request: PushToInterviewerRequest,
    db: Session = Depends(get_db)
):
    """HR推送简历给面试官筛选"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        screening = await InterviewerScreeningService.push_to_interviewer(
            db=db,
            application_id=application_id,
            interviewer_id=request.interviewer_id,
            interviewer_name=request.interviewer_name,
            hr_id=hr_id,
            hr_name=hr_name,
            comments=request.comments
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "screening_id": screening.id,
                "application_id": screening.application_id,
                "interviewer_name": screening.interviewer_name,
                "created_at": screening.created_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{screening_id}/submit", response_model=dict)
async def submit_screening_result(
    screening_id: str,
    request: SubmitScreeningResultRequest,
    db: Session = Depends(get_db)
):
    """面试官提交筛选结果"""
    try:
        # TODO: 获取当前面试官的ID和姓名
        interviewer_id = "current_user_id"
        interviewer_name = "当前用户"

        # 将字符串转换为枚举
        result = ScreeningResult(request.result)

        screening = await InterviewerScreeningService.submit_screening_result(
            db=db,
            screening_id=screening_id,
            interviewer_id=interviewer_id,
            interviewer_name=interviewer_name,
            result=result,
            comments=request.comments
        )

        # 获取应聘记录状态
        from app.models.application import Application
        application = db.query(Application).filter(
            Application.id == screening.application_id
        ).first()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "screening_id": screening.id,
                "result": screening.result.value,
                "application_status": application.status.value if application else None,
                "screened_at": screening.screened_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-pending", response_model=dict)
async def get_my_pending_screenings(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """获取我的待筛选简历列表"""
    try:
        # TODO: 获取当前面试官的ID
        interviewer_id = "current_user_id"

        items, total = InterviewerScreeningService.get_pending_screenings(
            db=db,
            interviewer_id=interviewer_id,
            limit=limit,
            offset=offset
        )

        # 构建响应数据
        screening_list = []
        for screening in items:
            # 获取应聘记录信息
            from app.models.application import Application
            application = db.query(Application).filter(
                Application.id == screening.application_id
            ).first()

            screening_list.append({
                "id": screening.id,
                "application_id": screening.application_id,
                "candidate_name": application.candidate.name if application and application.candidate else None,
                "job_title": application.job.title if application and application.job else None,
                "created_at": screening.created_at.isoformat(),
                "comments": screening.comments
            })

        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": screening_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{screening_id}", response_model=dict)
async def get_screening_detail(
    screening_id: str,
    db: Session = Depends(get_db)
):
    """获取筛选记录详情"""
    try:
        screening = InterviewerScreeningService.get_by_id(db=db, screening_id=screening_id)
        if not screening:
            raise HTTPException(status_code=404, detail="Screening not found")

        # 获取应聘记录信息
        from app.models.application import Application
        application = db.query(Application).filter(
            Application.id == screening.application_id
        ).first()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "id": screening.id,
                "application_id": screening.application_id,
                "interviewer_id": screening.interviewer_id,
                "interviewer_name": screening.interviewer_name,
                "result": screening.result.value if screening.result else None,
                "comments": screening.comments,
                "created_at": screening.created_at.isoformat(),
                "screened_at": screening.screened_at.isoformat() if screening.screened_at else None,
                "application": {
                    "candidate_name": application.candidate.name if application and application.candidate else None,
                    "job_title": application.job.title if application and application.job else None,
                    "status": application.status.value if application else None
                } if application else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/application/{application_id}", response_model=dict)
async def get_screenings_by_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取应聘记录的所有筛选记录"""
    try:
        screenings = InterviewerScreeningService.get_by_application(
            db=db,
            application_id=application_id
        )

        items = []
        for screening in screenings:
            items.append({
                "id": screening.id,
                "interviewer_name": screening.interviewer_name,
                "result": screening.result.value if screening.result else None,
                "comments": screening.comments,
                "created_at": screening.created_at.isoformat(),
                "screened_at": screening.screened_at.isoformat() if screening.screened_at else None
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


@router.get("/my-history", response_model=dict)
async def get_my_screening_history(
    result: Optional[str] = Query(None, description="Filter by result: pass, reject"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """获取我的筛选历史记录"""
    try:
        # TODO: 获取当前面试官的ID
        interviewer_id = "current_user_id"

        # 转换result参数
        result_enum = None
        if result:
            result_enum = ScreeningResult(result)

        items, total = InterviewerScreeningService.get_by_interviewer(
            db=db,
            interviewer_id=interviewer_id,
            result=result_enum,
            limit=limit,
            offset=offset
        )

        # 构建响应数据
        screening_list = []
        for screening in items:
            # 获取应聘记录信息
            from app.models.application import Application
            application = db.query(Application).filter(
                Application.id == screening.application_id
            ).first()

            screening_list.append({
                "id": screening.id,
                "application_id": screening.application_id,
                "candidate_name": application.candidate.name if application and application.candidate else None,
                "job_title": application.job.title if application and application.job else None,
                "result": screening.result.value if screening.result else None,
                "created_at": screening.created_at.isoformat(),
                "screened_at": screening.screened_at.isoformat() if screening.screened_at else None
            })

        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": screening_list,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
