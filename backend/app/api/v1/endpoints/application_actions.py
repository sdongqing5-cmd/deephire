"""Application action endpoints - 应聘记录操作接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.application import Application, ApplicationStatus
from app.services.application_query_service import ApplicationQueryService

router = APIRouter()


# TODO: 替换为真实的用户认证
def get_current_user() -> dict:
    """获取当前用户（临时实现）"""
    return {"id": "1", "name": "HR Manager"}


class StatusTransitionRequest(BaseModel):
    """状态转换请求"""
    to_status: str
    reason: Optional[str] = None


class RejectRequest(BaseModel):
    """淘汰请求"""
    reason: Optional[str] = None


class PassRequest(BaseModel):
    """通过请求"""
    notes: Optional[str] = None


@router.get("/{application_id}", summary="获取应聘记录详情")
async def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db),
):
    """获取应聘记录的详细信息"""
    detail = ApplicationQueryService.get_application_detail(db, application_id)

    if not detail:
        raise HTTPException(status_code=404, detail="应聘记录不存在")

    return {
        "code": 0,
        "data": detail
    }


@router.post("/{application_id}/transition", summary="转换应聘状态")
async def transition_status(
    application_id: str,
    request: StatusTransitionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    转换应聘状态

    根据状态机规则转换状态
    """
    try:
        # 解析目标状态
        try:
            to_status = ApplicationStatus(request.to_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态: {request.to_status}")

        # 执行状态转换
        application = ApplicationQueryService.transition_status(
            db=db,
            application_id=application_id,
            to_status=to_status,
            operator_id=current_user["id"],
            operator_name=current_user["name"],
            reason=request.reason
        )

        if not application:
            raise HTTPException(status_code=404, detail="应聘记录不存在")

        return {
            "code": 0,
            "message": "状态转换成功",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "last_status_change_at": application.last_status_change_at.isoformat()
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/pass", summary="简历通过（进入下一阶段）")
async def pass_application(
    application_id: str,
    request: PassRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    简历通过，进入下一阶段

    根据当前状态自动判断下一阶段
    """
    # 获取当前应聘记录
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="应聘记录不存在")

    # 根据当前状态确定下一阶段
    current_status = app.status
    next_status_map = {
        ApplicationStatus.NEW: ApplicationStatus.HR_SCREENING,
        ApplicationStatus.HR_SCREENING: ApplicationStatus.HR_INTERVIEW_SCHEDULED,
        ApplicationStatus.HR_INTERVIEW_COMPLETED: ApplicationStatus.SENT_TO_INTERVIEWER,
        ApplicationStatus.INTERVIEW_TIME_CONFIRMING: ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED,
        ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED: ApplicationStatus.FINAL_INTERVIEW_SCHEDULED,
        ApplicationStatus.FINAL_INTERVIEW_COMPLETED: ApplicationStatus.OFFER_PENDING,
        ApplicationStatus.VERBAL_OFFER_ACCEPTED: ApplicationStatus.OFFER_PENDING,
        ApplicationStatus.OFFER_SENT: ApplicationStatus.OFFER_ACCEPTED,
        ApplicationStatus.OFFER_ACCEPTED: ApplicationStatus.PENDING_ONBOARD,
    }

    next_status = next_status_map.get(current_status)

    if not next_status:
        raise HTTPException(
            status_code=400,
            detail=f"当前状态 {current_status.value} 无法直接通过，请手动选择下一状态"
        )

    # 执行状态转换
    try:
        application = ApplicationQueryService.transition_status(
            db=db,
            application_id=application_id,
            to_status=next_status,
            operator_id=current_user["id"],
            operator_name=current_user["name"],
            reason=request.notes or "通过"
        )

        return {
            "code": 0,
            "message": "操作成功",
            "data": {
                "application_id": application.id,
                "from_status": current_status.value,
                "to_status": application.status.value,
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/reject", summary="淘汰候选人")
async def reject_application(
    application_id: str,
    request: RejectRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    淘汰候选人

    根据当前阶段设置为对应的淘汰状态
    """
    # 获取当前应聘记录
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="应聘记录不存在")

    # 根据当前状态确定淘汰状态
    current_status = app.status
    reject_status_map = {
        ApplicationStatus.NEW: ApplicationStatus.HR_REJECTED,
        ApplicationStatus.HR_SCREENING: ApplicationStatus.HR_REJECTED,
        ApplicationStatus.HR_INTERVIEW_SCHEDULED: ApplicationStatus.HR_INTERVIEW_REJECTED,
        ApplicationStatus.HR_INTERVIEWING: ApplicationStatus.HR_INTERVIEW_REJECTED,
        ApplicationStatus.HR_INTERVIEW_COMPLETED: ApplicationStatus.HR_INTERVIEW_REJECTED,
        ApplicationStatus.SENT_TO_INTERVIEWER: ApplicationStatus.INTERVIEWER_REJECTED,
        ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION: ApplicationStatus.INTERVIEWER_REJECTED,
        ApplicationStatus.INTERVIEW_TIME_CONFIRMING: ApplicationStatus.INTERVIEWER_REJECTED,
        ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED: ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
        ApplicationStatus.DEPARTMENT_INTERVIEWING: ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
        ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED: ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
        ApplicationStatus.ASSESSMENT_INVITED: ApplicationStatus.ASSESSMENT_FAILED,
        ApplicationStatus.ASSESSMENT_IN_PROGRESS: ApplicationStatus.ASSESSMENT_FAILED,
        ApplicationStatus.HR_REINTERVIEW_SCHEDULED: ApplicationStatus.HR_REINTERVIEW_REJECTED,
        ApplicationStatus.HR_REINTERVIEWING: ApplicationStatus.HR_REINTERVIEW_REJECTED,
        ApplicationStatus.FINAL_INTERVIEW_SCHEDULED: ApplicationStatus.FINAL_INTERVIEW_REJECTED,
        ApplicationStatus.FINAL_INTERVIEWING: ApplicationStatus.FINAL_INTERVIEW_REJECTED,
        ApplicationStatus.FINAL_INTERVIEW_COMPLETED: ApplicationStatus.FINAL_INTERVIEW_REJECTED,
        ApplicationStatus.OFFER_PENDING: ApplicationStatus.OFFER_NOT_AGREED,
        ApplicationStatus.OFFER_SENT: ApplicationStatus.OFFER_NOT_AGREED,
    }

    reject_status = reject_status_map.get(current_status)

    if not reject_status:
        raise HTTPException(
            status_code=400,
            detail=f"当前状态 {current_status.value} 无法淘汰"
        )

    # 执行状态转换
    try:
        application = ApplicationQueryService.transition_status(
            db=db,
            application_id=application_id,
            to_status=reject_status,
            operator_id=current_user["id"],
            operator_name=current_user["name"],
            reason=request.reason or "不符合要求"
        )

        return {
            "code": 0,
            "message": "已淘汰",
            "data": {
                "application_id": application.id,
                "from_status": current_status.value,
                "to_status": application.status.value,
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}/status-history", summary="获取状态历史")
async def get_status_history(
    application_id: str,
    db: Session = Depends(get_db),
):
    """获取应聘记录的状态变更历史"""
    detail = ApplicationQueryService.get_application_detail(db, application_id)

    if not detail:
        raise HTTPException(status_code=404, detail="应聘记录不存在")

    return {
        "code": 0,
        "data": detail.get("status_history", [])
    }
