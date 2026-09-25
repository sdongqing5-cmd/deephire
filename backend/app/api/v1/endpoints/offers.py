"""Offer API endpoints - Offer和入职管理接口"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import os
import uuid

from app.db.database import get_db
from app.services.offer_service import OfferService

router = APIRouter()

CURRENT_USER_ID = "2"
CURRENT_USER_NAME = "Recruiter"


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


class RecordOfferRequest(BaseModel):
    """录入offer请求"""
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
    template_name: Optional[str] = None
    cc_recipients: Optional[list[str]] = None


class EditOfferRequest(BaseModel):
    """编辑offer请求"""
    offer_details: dict


class CandidateAcceptOfferRequest(BaseModel):
    """候选人接受offer请求"""
    signature_url: Optional[str] = None


class CandidateDeclineOfferRequest(BaseModel):
    """候选人拒绝offer请求"""
    reason: Optional[str] = None


class RejectAtOfferStageRequest(BaseModel):
    """Offer阶段淘汰候选人"""
    reason: str


class PrepareOnboardingRequest(BaseModel):
    """准备入职请求"""
    expected_start_date: datetime


class CompleteOnboardingRequest(BaseModel):
    """完成入职请求"""
    actual_start_date: datetime


class OnboardingAttachmentRequest(BaseModel):
    """入职附件请求"""
    name: str
    url: str


class CancelOnboardingRequest(BaseModel):
    """取消入职请求"""
    reason: str


class NotifyInfoCollectionRequest(BaseModel):
    """通知采集入职信息请求"""
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class RescheduleOnboardingRequest(BaseModel):
    """改期入职请求"""
    expected_start_date: datetime
    reason: Optional[str] = None


# ==================== API Endpoints ====================

@router.get("", response_model=dict)
async def list_offer_applications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取Offer管理列表"""
    try:
        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": OfferService.list_by_module(
                    db=db,
                    module="offer",
                    status=status,
                    skip=skip,
                    limit=limit,
                )
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onboarding", response_model=dict)
async def list_onboarding_applications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取入职管理列表"""
    try:
        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": OfferService.list_by_module(
                    db=db,
                    module="onboarding",
                    status=status,
                    skip=skip,
                    limit=limit,
                )
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/applications/{application_id}/start-salary-negotiation", response_model=dict)
async def start_salary_negotiation(
    application_id: str,
    request: StartSalaryNegotiationRequest,
    db: Session = Depends(get_db)
):
    """开始薪资谈判"""
    try:
        # TODO: 获取当前HR的ID和姓名
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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


@router.post("/applications/{application_id}/record-offer", response_model=dict)
async def record_offer(
    application_id: str,
    request: RecordOfferRequest,
    db: Session = Depends(get_db)
):
    """录入Offer，并进入待发Offer。"""
    try:
        application = await OfferService.record_offer(
            db=db,
            application_id=application_id,
            hr_id=CURRENT_USER_ID,
            hr_name=CURRENT_USER_NAME,
            offer_details=request.offer_details,
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
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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
        approver_id = CURRENT_USER_ID
        approver_name = CURRENT_USER_NAME

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
        approver_id = CURRENT_USER_ID
        approver_name = CURRENT_USER_NAME

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
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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


@router.post("/applications/{application_id}/edit-offer", response_model=dict)
async def edit_offer(
    application_id: str,
    request: EditOfferRequest,
    db: Session = Depends(get_db)
):
    """Offer编辑"""
    try:
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

        application = await OfferService.edit_offer(
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
            signature_url=request.signature_url,
            operator_id=CURRENT_USER_ID,
            operator_name=CURRENT_USER_NAME,
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
            reason=request.reason,
            operator_id=CURRENT_USER_ID,
            operator_name=CURRENT_USER_NAME,
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


@router.post("/applications/{application_id}/reject-at-offer-stage", response_model=dict)
async def reject_at_offer_stage(
    application_id: str,
    request: RejectAtOfferStageRequest,
    db: Session = Depends(get_db)
):
    """Offer管理页淘汰候选人，状态为 Offer 没谈拢。"""
    try:
        application = await OfferService.reject_at_offer_stage(
            db=db,
            application_id=application_id,
            hr_id=CURRENT_USER_ID,
            hr_name=CURRENT_USER_NAME,
            reason=request.reason,
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
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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


@router.post("/applications/{application_id}/onboarding-attachment", response_model=dict)
async def add_onboarding_attachment(
    application_id: str,
    request: OnboardingAttachmentRequest,
    db: Session = Depends(get_db)
):
    """上传/记录入职附件。"""
    try:
        application = await OfferService.add_onboarding_attachment(
            db=db,
            application_id=application_id,
            hr_id=CURRENT_USER_ID,
            hr_name=CURRENT_USER_NAME,
            attachment=request.model_dump(),
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


@router.post("/applications/{application_id}/onboarding-attachment-upload", response_model=dict)
async def upload_onboarding_attachment(
    application_id: str,
    name: str = Form("入职附件"),
    attachment_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传入职附件文件并记录到应聘记录。"""
    try:
        upload_dir = os.path.join("uploads", "onboarding")
        os.makedirs(upload_dir, exist_ok=True)
        extension = os.path.splitext(attachment_file.filename or "")[1]
        filename = f"onboarding_{uuid.uuid4().hex[:12]}{extension}"
        file_path = os.path.join(upload_dir, filename)

        content = await attachment_file.read()
        with open(file_path, "wb") as handle:
            handle.write(content)

        application = await OfferService.add_onboarding_attachment(
            db=db,
            application_id=application_id,
            hr_id=CURRENT_USER_ID,
            hr_name=CURRENT_USER_NAME,
            attachment={
                "name": name or attachment_file.filename or "入职附件",
                "url": f"/uploads/onboarding/{filename}",
            },
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "url": f"/uploads/onboarding/{filename}",
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/applications/{application_id}/notify-info-collection", response_model=dict)
async def notify_info_collection(
    application_id: str,
    request: NotifyInfoCollectionRequest,
    db: Session = Depends(get_db)
):
    """通知候选人采集入职信息"""
    try:
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

        application = await OfferService.notify_information_collection(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            due_date=request.due_date,
            notes=request.notes,
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


@router.post("/applications/{application_id}/reschedule-onboarding", response_model=dict)
async def reschedule_onboarding(
    application_id: str,
    request: RescheduleOnboardingRequest,
    db: Session = Depends(get_db)
):
    """改期入职"""
    try:
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

        application = await OfferService.reschedule_onboarding(
            db=db,
            application_id=application_id,
            hr_id=hr_id,
            hr_name=hr_name,
            expected_start_date=request.expected_start_date,
            reason=request.reason,
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
        hr_id = CURRENT_USER_ID
        hr_name = CURRENT_USER_NAME

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
