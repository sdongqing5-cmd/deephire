"""Offer API endpoints - Offer和入职管理接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.services.offer_service import OfferService

router = APIRouter()


# ==================== Pydantic Models ====================

class StartSalaryNegotiationRequest(BaseModel):
    """开始薪资谈判请求"""
    proposed_salary: int
    negotiation_notes: Optional[str] = None


class AcceptVerbalOfferRequest(BaseModel):
    """接受口头offer请求"""
    agreed_salary: int
    notes: Optional[str] = None


class SubmitOfferApprovalRequest(BaseModel):
    """提交offer审批请求"""
    offer_details: dict


class ApproveOfferRequest(BaseModel):
    """审批offer请求"""
    comments: Optional[str] = None


class RejectOfferApprovalRequest(BaseModel):
    """拒绝offer审批请求"""
    reason: str


class SendOfferRequest(BaseModel):
    """发送offer请求"""
    offer_letter_url: str
    valid_until: datetime


class CandidateAcceptOfferRequest(BaseModel):
    """候选人接受offer请求"""
    signature_url: Optional[str] = None


class CandidateDeclineOfferRequest(BaseModel):
    """候选人拒绝offer请求"""
    reason: Optional[str] = None


class PrepareOnboardingRequest(BaseModel):
    """准备入职请求"""
    expected_start_date: datetime


class CompleteOnboardingRequest(BaseModel):
    """完成入职请求"""
    actual_start_date: datetime


class CancelOnboardingRequest(BaseModel):
    """取消入职请求"""
    reason: str


# ==================== API Endpoints ====================

@router.post("/applications/{application_id}/start-salary-negotiation", response_model=dict)
async def start_salary_negotiation(
    application_id: str,
    request: StartSalaryNegotiationRequest,
    db: Session = Depends(get_db)
):
    """开始薪资谈判"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.start_salary_negotiation(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            proposed_salary=request.proposed_salary,
            negotiation_notes=request.negotiation_notes
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


@router.post("/applications/{application_id}/accept-verbal-offer", response_model=dict)
async def accept_verbal_offer(
    application_id: str,
    request: AcceptVerbalOfferRequest,
    db: Session = Depends(get_db)
):
    """候选人接受口头offer"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.accept_verbal_offer(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            agreed_salary=request.agreed_salary,
            notes=request.notes
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


@router.post("/applications/{application_id}/submit-offer-approval", response_model=dict)
async def submit_offer_approval(
    application_id: str,
    request: SubmitOfferApprovalRequest,
    db: Session = Depends(get_db)
):
    """提交offer审批"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.submit_offer_approval(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            offer_details=request.offer_details
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


@router.post("/applications/{application_id}/approve-offer", response_model=dict)
async def approve_offer(
    application_id: str,
    request: ApproveOfferRequest,
    db: Session = Depends(get_db)
):
    """审批通过offer"""
    try:
        # TODO: 获取当前审批人的ID和姓名
        approver_id = "current_user_id"
        approver_name = "当前用户"

        application = await OfferService.approve_offer(
            db=db,
            application_id=application_id,
            approver_id=approver_id,
            approver_name=approver_name,
            comments=request.comments
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


@router.post("/applications/{application_id}/reject-offer-approval", response_model=dict)
async def reject_offer_approval(
    application_id: str,
    request: RejectOfferApprovalRequest,
    db: Session = Depends(get_db)
):
    """审批拒绝offer"""
    try:
        # TODO: 获取当前审批人的ID和姓名
        approver_id = "current_user_id"
        approver_name = "当前用户"

        application = await OfferService.reject_offer_approval(
            db=db,
            application_id=application_id,
            approver_id=approver_id,
            approver_name=approver_name,
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


@router.post("/applications/{application_id}/send-offer", response_model=dict)
async def send_offer(
    application_id: str,
    request: SendOfferRequest,
    db: Session = Depends(get_db)
):
    """发送正式offer"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.send_offer(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            offer_letter_url=request.offer_letter_url,
            valid_until=request.valid_until
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


@router.post("/applications/{application_id}/candidate-accept-offer", response_model=dict)
async def candidate_accept_offer(
    application_id: str,
    request: CandidateAcceptOfferRequest,
    db: Session = Depends(get_db)
):
    """候选人接受offer（公开接口）"""
    try:
        application = await OfferService.candidate_accept_offer(
            db=db,
            application_id=application_id,
            signature_url=request.signature_url
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


@router.post("/applications/{application_id}/candidate-decline-offer", response_model=dict)
async def candidate_decline_offer(
    application_id: str,
    request: CandidateDeclineOfferRequest,
    db: Session = Depends(get_db)
):
    """候选人拒绝offer（公开接口）"""
    try:
        application = await OfferService.candidate_decline_offer(
            db=db,
            application_id=application_id,
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


@router.post("/applications/{application_id}/prepare-onboarding", response_model=dict)
async def prepare_onboarding(
    application_id: str,
    request: PrepareOnboardingRequest,
    db: Session = Depends(get_db)
):
    """准备入职"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.prepare_onboarding(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            expected_start_date=request.expected_start_date
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


@router.post("/applications/{application_id}/complete-onboarding", response_model=dict)
async def complete_onboarding(
    application_id: str,
    request: CompleteOnboardingRequest,
    db: Session = Depends(get_db)
):
    """完成入职"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.complete_onboarding(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            actual_start_date=request.actual_start_date
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


@router.post("/applications/{application_id}/cancel-onboarding", response_model=dict)
async def cancel_onboarding(
    application_id: str,
    request: CancelOnboardingRequest,
    db: Session = Depends(get_db)
):
    """取消入职"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = "current_user_id"
        hr_name = "当前用户"

        application = await OfferService.cancel_onboarding(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
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
