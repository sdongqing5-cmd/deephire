"""Interview management endpoints - 面试管理接口"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.interview import Interview, InterviewType, InterviewStatus, InterviewResult
from app.services.interview_service import InterviewService
from pydantic import BaseModel

from app.schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewEvaluation,
    InterviewResponse,
    InterviewListItem,
)

router = APIRouter()


class InterviewBatchRequest(BaseModel):
    interview_ids: List[str]


class UrgeInterviewRequest(InterviewBatchRequest):
    target: str = "candidate"


# TODO: 替换为真实的用户认证
def get_current_user() -> dict:
    """获取当前用户（临时实现）"""
    return {"id": "3", "name": "Interviewer", "role": "interviewer"}


@router.post("/", response_model=InterviewResponse, summary="创建面试")
async def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建面试安排

    - **application_id**: 应聘记录ID
    - **interviewer_id**: 面试官ID
    - **interview_type**: 面试类型（hr_initial/department/final）
    - **scheduled_at**: 面试时间
    - **duration**: 面试时长（分钟）
    """
    try:
        interview = await InterviewService.schedule_with_status_update(
            db=db,
            interview_data=interview_data,
            operator_id=current_user["id"],
            operator_name=current_user["name"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return interview


@router.get("/", summary="获取面试列表")
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    interviewer_id: Optional[str] = Query(None, description="面试官ID过滤"),
    candidate_id: Optional[str] = Query(None, description="候选人ID过滤"),
    job_id: Optional[str] = Query(None, description="职位ID过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    result: Optional[str] = Query(None, description="结果过滤"),
    interview_type: Optional[str] = Query(None, description="面试类型过滤"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
):
    """
    获取面试列表，支持多条件过滤

    默认按面试时间升序排列
    """
    # 转换枚举
    status_enum = InterviewStatus(status) if status else None
    result_enum = InterviewResult(result) if result else None
    type_enum = InterviewType(interview_type) if interview_type else None

    interviews = InterviewService.list_interviews(
        db=db,
        skip=skip,
        limit=limit,
        interviewer_id=interviewer_id,
        candidate_id=candidate_id,
        job_id=job_id,
        status=status_enum,
        result=result_enum,
        interview_type=type_enum,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "code": 0,
        "data": interviews
    }


@router.get("/today", summary="获取今日面试")
async def get_today_interviews(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取今日面试列表

    用于面试官查看今天的面试安排
    """
    interviews = InterviewService.get_today_interviews(
        db=db,
        interviewer_id=current_user["id"]
    )

    return {
        "code": 0,
        "data": interviews
    }


@router.get("/upcoming", summary="获取未来面试")
async def get_upcoming_interviews(
    days: int = Query(7, ge=1, le=30, description="未来天数"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取未来N天的面试列表

    默认查询未来7天
    """
    interviews = InterviewService.get_upcoming_interviews(
        db=db,
        interviewer_id=current_user["id"],
        days=days
    )

    return {
        "code": 0,
        "data": interviews
    }


@router.get("/{interview_id}", summary="获取面试详情")
async def get_interview(
    interview_id: str,
    db: Session = Depends(get_db),
):
    """获取面试详细信息（含候选人和职位信息）"""
    detail = InterviewService.get_interview_detail(db, interview_id)

    if not detail:
        raise HTTPException(status_code=404, detail="面试不存在")

    return {
        "code": 0,
        "data": detail
    }


@router.put("/{interview_id}", response_model=InterviewResponse, summary="更新面试信息")
async def update_interview(
    interview_id: str,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
):
    """
    更新面试信息

    支持更新面试时间、地点、面试官等
    """
    interview = InterviewService.update(db, interview_id, interview_data)

    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    return interview


@router.post("/{interview_id}/evaluate", response_model=InterviewResponse, summary="提交面试评价")
async def submit_evaluation(
    interview_id: str,
    evaluation: InterviewEvaluation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    提交面试评价

    - **result**: 面试结果（pass/fail/pending）
    - **score**: 评分（1-10）
    - **feedback**: 面试反馈
    """
    interview = await InterviewService.submit_evaluation(
        db,
        interview_id,
        evaluation,
        operator_id=current_user["id"],
        operator_name=current_user["name"],
    )

    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    return interview


@router.patch("/{interview_id}/status", summary="更新面试状态")
async def update_interview_status(
    interview_id: str,
    status: str = Query(..., description="新状态"),
    db: Session = Depends(get_db),
):
    """
    更新面试状态

    状态: scheduled/confirmed/in_progress/completed/cancelled/no_show
    """
    try:
        status_enum = InterviewStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的状态: {status}")

    interview = InterviewService.update_status(db, interview_id, status_enum)

    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    return {
        "code": 0,
        "message": "状态更新成功",
        "data": {
            "interview_id": interview.id,
            "status": interview.status.value,
        }
    }


@router.post("/{interview_id}/cancel", summary="取消面试")
async def cancel_interview(
    interview_id: str,
    reason: Optional[str] = Query(None, description="取消原因"),
    db: Session = Depends(get_db),
):
    """
    取消面试

    取消后状态变为 cancelled
    """
    interview = InterviewService.cancel_interview(db, interview_id, reason)

    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    return {
        "code": 0,
        "message": "面试已取消",
        "data": {
            "interview_id": interview.id,
            "status": interview.status.value,
        }
    }


@router.post("/{interview_id}/candidate-reply", summary="候选人确认或拒绝面试")
async def candidate_reply(
    interview_id: str,
    accepted: bool = Query(..., description="是否参加面试"),
    db: Session = Depends(get_db),
):
    """候选人点击参加/不参加面试通知后的状态回写。"""
    interview = InterviewService.mark_candidate_reply(db, interview_id, accepted)

    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    return {
        "code": 0,
        "message": "候选人答复已记录",
        "data": {
            "interview_id": interview.id,
            "status": interview.status.value,
        }
    }


@router.post("/batch-notify", summary="批量通知面试双方")
async def batch_notify(
    request: InterviewBatchRequest,
    db: Session = Depends(get_db),
):
    """批量标记面试通知已发送给候选人和面试官。"""
    notified_ids = InterviewService.send_notifications(db, request.interview_ids)
    return {
        "code": 0,
        "message": "通知已发送",
        "data": {
            "interview_ids": notified_ids,
        }
    }


@router.post("/batch-urge", summary="批量催促答复或反馈")
async def batch_urge(
    request: UrgeInterviewRequest,
    db: Session = Depends(get_db),
):
    """批量催促候选人答复或面试官反馈。"""
    if request.target not in {"candidate", "interviewer"}:
        raise HTTPException(status_code=400, detail="target 必须为 candidate 或 interviewer")

    urged_ids = InterviewService.urge_reply(db, request.interview_ids, request.target)
    return {
        "code": 0,
        "message": "催促已发送",
        "data": {
            "interview_ids": urged_ids,
        }
    }
