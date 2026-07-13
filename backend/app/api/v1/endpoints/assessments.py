"""Assessment API endpoints - 测评接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.services.assessment_service import AssessmentService

router = APIRouter()


# ==================== Pydantic Models ====================

class InviteAssessmentRequest(BaseModel):
    """邀请测评请求"""
    application_id: str
    assessment_type: str
    assessment_url: str
    valid_days: int = 7


class CompleteAssessmentRequest(BaseModel):
    """完成测评请求（测评系统回调）"""
    score: int
    result_data: dict
    report_url: Optional[str] = None


class FailAssessmentRequest(BaseModel):
    """测评未通过请求"""
    reason: str


class ResendInvitationRequest(BaseModel):
    """重新发送邀请请求"""
    extend_days: int = 7


# ==================== API Endpoints ====================

@router.post("/invite", response_model=dict)
async def invite_assessment(
    request: InviteAssessmentRequest,
    db: Session = Depends(get_db)
):
    """邀请候选人参加测评"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        assessment = await AssessmentService.invite_assessment(
            db=db,
            application_id=request.application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            assessment_type=request.assessment_type,
            assessment_url=request.assessment_url,
            valid_days=request.valid_days
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "assessment_id": assessment.id,
                "application_id": assessment.application_id,
                "assessment_type": assessment.assessment_type,
                "status": assessment.status.value,
                "invited_at": assessment.invited_at.isoformat(),
                "expires_at": assessment.expires_at.isoformat() if assessment.expires_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{assessment_id}/start", response_model=dict)
async def start_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """候选人开始测评"""
    try:
        assessment = await AssessmentService.start_assessment(
            db=db,
            assessment_id=assessment_id
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "assessment_id": assessment.id,
                "status": assessment.status.value,
                "started_at": assessment.started_at.isoformat() if assessment.started_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{assessment_id}/complete", response_model=dict)
async def complete_assessment(
    assessment_id: str,
    request: CompleteAssessmentRequest,
    db: Session = Depends(get_db)
):
    """完成测评（测评系统回调）"""
    try:
        assessment = await AssessmentService.complete_assessment(
            db=db,
            assessment_id=assessment_id,
            score=request.score,
            result_data=request.result_data,
            report_url=request.report_url
        )

        # 获取应聘记录状态
        from app.models.application import Application
        application = db.query(Application).filter(
            Application.id == assessment.application_id
        ).first()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "assessment_id": assessment.id,
                "status": assessment.status.value,
                "score": assessment.score,
                "application_status": application.status.value if application else None,
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{assessment_id}/fail", response_model=dict)
async def fail_assessment(
    assessment_id: str,
    request: FailAssessmentRequest,
    db: Session = Depends(get_db)
):
    """测评未通过"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        assessment = await AssessmentService.fail_assessment(
            db=db,
            assessment_id=assessment_id,
            hr_id=hr_id,
            hr_name=hr_name,
            reason=request.reason
        )

        # 获取应聘记录状态
        from app.models.application import Application
        application = db.query(Application).filter(
            Application.id == assessment.application_id
        ).first()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "assessment_id": assessment.id,
                "status": assessment.status.value,
                "application_status": application.status.value if application else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assessment_id}", response_model=dict)
async def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db)
):
    """获取测评详情"""
    try:
        assessment = AssessmentService.get_by_id(db=db, assessment_id=assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        return {
            "code": 0,
            "message": "success",
            "data": {
                "id": assessment.id,
                "application_id": assessment.application_id,
                "candidate_id": assessment.candidate_id,
                "assessment_type": assessment.assessment_type,
                "assessment_url": assessment.assessment_url,
                "status": assessment.status.value,
                "score": assessment.score,
                "result_data": assessment.result_data,
                "report_url": assessment.report_url,
                "invited_at": assessment.invited_at.isoformat() if assessment.invited_at else None,
                "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
                "expires_at": assessment.expires_at.isoformat() if assessment.expires_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/application/{application_id}", response_model=dict)
async def get_assessments_by_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取应聘记录的所有测评"""
    try:
        assessments = AssessmentService.get_by_application(
            db=db,
            application_id=application_id
        )

        items = []
        for assessment in assessments:
            items.append({
                "id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "status": assessment.status.value,
                "score": assessment.score,
                "invited_at": assessment.invited_at.isoformat() if assessment.invited_at else None,
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
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


@router.get("/candidate/{candidate_id}", response_model=dict)
async def get_assessments_by_candidate(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """获取候选人的所有测评"""
    try:
        assessments = AssessmentService.get_by_candidate(
            db=db,
            candidate_id=candidate_id
        )

        items = []
        for assessment in assessments:
            items.append({
                "id": assessment.id,
                "application_id": assessment.application_id,
                "assessment_type": assessment.assessment_type,
                "status": assessment.status.value,
                "score": assessment.score,
                "invited_at": assessment.invited_at.isoformat() if assessment.invited_at else None,
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
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


@router.post("/{assessment_id}/resend-invitation", response_model=dict)
async def resend_assessment_invitation(
    assessment_id: str,
    request: ResendInvitationRequest,
    db: Session = Depends(get_db)
):
    """重新发送测评邀请"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        assessment = await AssessmentService.resend_invitation(
            db=db,
            assessment_id=assessment_id,
            hr_id=hr_id,
            hr_name=hr_name,
            extend_days=request.extend_days
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "assessment_id": assessment.id,
                "status": assessment.status.value,
                "expires_at": assessment.expires_at.isoformat() if assessment.expires_at else None
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
