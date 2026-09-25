"""Applications API endpoints - 应聘记录接口"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json
import re

from app.db.database import get_db
from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.models.candidate import Candidate
from app.models.job import Job
from app.services.resume_parser import clean_text_value, resume_parser
from app.services.application_service import ApplicationService
from app.services.application_state_machine import ApplicationStateMachine

router = APIRouter()

CURRENT_USER_ID = "1"
CURRENT_USER_NAME = "当前用户"


def resolve_candidate_display_name(candidate: Optional[Candidate], parsed_data: dict) -> str:
    """Prefer stored names unless they look like parser artifacts."""
    stored_name = clean_text_value(candidate.name if candidate else None)
    if stored_name and resume_parser.looks_like_name(stored_name):
        return stored_name

    parsed_name = clean_text_value(parsed_data.get("name"))
    if parsed_name and resume_parser.looks_like_name(parsed_name):
        return parsed_name

    resume_text = clean_text_value(parsed_data.get("resume_text"))
    if resume_text:
        lines = [
            cleaned
            for line in resume_text.splitlines()
            if (cleaned := clean_text_value(line))
        ]
        extracted_name = resume_parser.extract_name(
            lines,
            str(parsed_data.get("resume_url") or ""),
        )
        if resume_parser.looks_like_name(extracted_name):
            return extracted_name

    return stored_name or "未知"


def resolve_candidate_email(candidate: Optional[Candidate], parsed_data: dict) -> Optional[str]:
    raw_email = clean_text_value(candidate.email if candidate else None) or clean_text_value(parsed_data.get("email"))
    if not raw_email:
        return None

    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", raw_email)
    return match.group(0) if match else None


def resolve_candidate_experience_years(candidate: Optional[Candidate], parsed_data: dict) -> Optional[int]:
    resume_text = parsed_data.get("resume_text")
    if isinstance(resume_text, str):
        recalculated_years = resume_parser.extract_years_of_experience(resume_text)
        if recalculated_years is not None:
            return recalculated_years

    return candidate.years_of_experience if candidate else None


def resolve_candidate_current_experience(candidate: Optional[Candidate], parsed_data: dict) -> dict[str, Optional[str]]:
    resume_text = parsed_data.get("resume_text")
    if isinstance(resume_text, str):
        education_status = resume_parser.extract_education_status(resume_text)
        latest_experience = resume_parser.extract_latest_experience(resume_text)
        if education_status.get("is_currently_enrolled") and not latest_experience.get("is_current"):
            latest_experience = {
                "title": None,
                "company": None,
            }
        title = clean_text_value(latest_experience.get("title"))
        company = clean_text_value(latest_experience.get("company"))
        if title or company:
            return {
                "title": title,
                "company": company,
            }

    return {
        "title": clean_text_value(candidate.current_title if candidate else None),
        "company": clean_text_value(candidate.current_company if candidate else None),
    }


# ==================== Pydantic Models ====================

class ApplicationCreate(BaseModel):
    """创建应聘记录请求"""
    job_id: str
    candidate_name: Optional[str] = None
    candidate_phone: Optional[str] = None
    candidate_email: Optional[str] = None
    source: Optional[str] = "主动投递"


class ApplicationResponse(BaseModel):
    """应聘记录响应"""
    id: str
    candidate_id: str
    job_id: str
    status: str
    resume_url: Optional[str]
    source: Optional[str]
    hr_id: Optional[str]
    applied_at: datetime
    last_status_change_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApplicationDetailResponse(BaseModel):
    """应聘记录详情响应"""
    id: str
    candidate: dict
    job: dict
    status: str
    status_label: str
    resume_url: Optional[str]
    source: Optional[str]
    hr: Optional[dict]
    intention_contact: Optional[dict]
    applied_at: datetime
    last_status_change_at: Optional[datetime]


class DuplicateCheckRequest(BaseModel):
    """查重检查请求"""
    candidate_id: str
    job_id: str


class DuplicateCheckResponse(BaseModel):
    """查重检查响应"""
    is_duplicate: bool
    reason: Optional[str] = None
    existing_application: Optional[dict] = None
    active_applications: Optional[List[dict]] = None


class StatusTransitionRequest(BaseModel):
    """状态流转请求"""
    to_status: str
    reason: Optional[str] = None
    interviewer_evaluation: Optional[str] = None


class InterviewerEvaluationRequest(BaseModel):
    """面试官候选人评价请求"""
    evaluation: Optional[str] = None


class UndoRequest(BaseModel):
    reason: Optional[str] = "撤销上一步操作"


class TransferApplicationRequest(BaseModel):
    target_job_id: str
    reason: Optional[str] = None


class PhoneCommunicationRequest(BaseModel):
    """电话沟通请求"""
    result: str  # agreed, declined, no_answer
    notes: Optional[str] = None


class StatusHistoryResponse(BaseModel):
    """状态历史响应"""
    id: str
    from_status: Optional[str]
    to_status: str
    reason: Optional[str]
    operator_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== API Endpoints ====================

@router.post("/upload-resume", response_model=dict)
async def upload_resume(
    job_id: str = Form(...),
    candidate_name: Optional[str] = Form(None),
    candidate_phone: Optional[str] = Form(None),
    candidate_email: Optional[str] = Form(None),
    source: Optional[str] = Form("主动投递"),
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传简历到职位"""
    try:
        # TODO: 1. 解析简历
        # TODO: 2. 创建或更新候选人
        # TODO: 3. 查重检查
        # TODO: 4. 创建应聘记录
        # TODO: 5. 通知HR

        # 临时实现
        import uuid
        application_id = f"app_{uuid.uuid4().hex[:12]}"
        candidate_id = f"cand_{uuid.uuid4().hex[:12]}"

        # 创建候选人（简化版）
        candidate = Candidate(
            id=candidate_id,
            name=candidate_name or "未知",
            email=candidate_email,
            phone=candidate_phone,
            status="new"
        )
        db.add(candidate)

        # 创建应聘记录
        application = ApplicationService.create(
            db=db,
            application_id=application_id,
            candidate_id=candidate_id,
            job_id=job_id,
            source=source
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "candidate_id": candidate.id,
                "status": application.status.value,
                "duplicate_check": {
                    "is_duplicate": False
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(
    request: DuplicateCheckRequest,
    db: Session = Depends(get_db)
):
    """查重检查"""
    try:
        # 检查是否已投递该职位
        existing = ApplicationService.get_by_candidate_and_job(
            db=db,
            candidate_id=request.candidate_id,
            job_id=request.job_id
        )

        if existing:
            return DuplicateCheckResponse(
                is_duplicate=True,
                reason="已投递该职位",
                existing_application={
                    "id": existing.id,
                    "applied_at": existing.applied_at.isoformat(),
                    "status": existing.status.value
                }
            )

        # TODO: 检查是否在其他职位的有效流程中

        return DuplicateCheckResponse(is_duplicate=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=dict)
async def get_applications(
    status: Optional[str] = None,
    job_id: Optional[str] = None,
    hr_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取应聘记录列表"""
    try:
        query = db.query(Application)

        if status:
            query = query.filter(Application.status == status)
        if job_id:
            query = query.filter(Application.job_id == job_id)
        if hr_id:
            query = query.filter(Application.hr_id == hr_id)

        total = query.count()
        applications = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for app in applications:
            candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
            job = db.query(Job).filter(Job.id == app.job_id).first()
            parsed_data = {}
            if app.resume_parsed_data:
                try:
                    parsed_data = json.loads(app.resume_parsed_data)
                except json.JSONDecodeError:
                    parsed_data = {}
            current_experience = resolve_candidate_current_experience(candidate, parsed_data)

            items.append({
                "id": app.id,
                "candidate": {
                    "id": candidate.id if candidate else None,
                    "name": resolve_candidate_display_name(candidate, parsed_data),
                    "phone": candidate.phone if candidate else None,
                    "email": resolve_candidate_email(candidate, parsed_data),
                    "current_company": current_experience["company"],
                    "current_title": current_experience["title"],
                    "years_of_experience": resolve_candidate_experience_years(candidate, parsed_data),
                    "location": candidate.location if candidate else None,
                    "tags": candidate.tags if candidate else [],
                },
                "job": {
                    "id": job.id if job else None,
                    "title": job.title if job else "未知",
                },
                "status": app.status.value,
                "status_label": ApplicationStateMachine.get_status_label(app.status),
                "rejection_reason": app.rejection_reason,
                "interviewer_evaluation": app.interviewer_evaluation,
                "resume_url": app.resume_url,
                "resume_parsed_data": parsed_data,
                "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                "last_status_change_at": app.last_status_change_at.isoformat() if app.last_status_change_at else None,
            })

        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{application_id}/interviewer-evaluation", response_model=dict)
async def update_interviewer_evaluation(
    application_id: str,
    request: InterviewerEvaluationRequest,
    db: Session = Depends(get_db)
):
    """保存面试官对候选人的评价"""
    application = ApplicationService.get_by_id(db=db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.interviewer_evaluation = request.evaluation.strip() if request.evaluation else None
    db.commit()
    db.refresh(application)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "application_id": application.id,
            "interviewer_evaluation": application.interviewer_evaluation,
        }
    }


@router.get("/{application_id}", response_model=dict)
async def get_application(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取应聘记录详情"""
    try:
        application = ApplicationService.get_by_id(db=db, application_id=application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        candidate = db.query(Candidate).filter(Candidate.id == application.candidate_id).first()
        job = db.query(Job).filter(Job.id == application.job_id).first()
        parsed_data = {}
        if application.resume_parsed_data:
            try:
                parsed_data = json.loads(application.resume_parsed_data)
            except json.JSONDecodeError:
                parsed_data = {}
        current_experience = resolve_candidate_current_experience(candidate, parsed_data)

        return {
            "code": 0,
            "message": "success",
            "data": {
                "id": application.id,
                "candidate": {
                    "id": candidate.id if candidate else None,
                    "name": resolve_candidate_display_name(candidate, parsed_data),
                    "phone": candidate.phone if candidate else None,
                    "email": resolve_candidate_email(candidate, parsed_data),
                    "current_company": current_experience["company"],
                    "current_position": current_experience["title"],
                    "work_years": resolve_candidate_experience_years(candidate, parsed_data),
                },
                "job": {
                    "id": job.id if job else None,
                    "title": job.title if job else "未知",
                    "department": None,  # TODO: 关联department
                },
                "status": application.status.value,
                "status_label": ApplicationStateMachine.get_status_label(application.status),
                "rejection_reason": application.rejection_reason,
                "interviewer_evaluation": application.interviewer_evaluation,
                "available_transitions": [
                    {
                        "status": status.value,
                        "label": ApplicationStateMachine.get_status_label(status),
                    }
                    for status in ApplicationStateMachine.get_available_transitions(application.status)
                ],
                "resume_url": application.resume_url,
                "resume_parsed_data": parsed_data,
                "source": application.source,
                "hr": None,  # TODO: 关联hr user
                "intention_contact": {
                    "method": application.intention_contact_method,
                    "result": application.intention_contact_result,
                    "notes": application.intention_contact_notes,
                    "contacted_at": application.intention_contacted_at.isoformat() if application.intention_contacted_at else None,
                } if application.intention_contact_method else None,
                "applied_at": application.applied_at.isoformat() if application.applied_at else None,
                "last_status_change_at": application.last_status_change_at.isoformat() if application.last_status_change_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{application_id}/start-screening", response_model=dict)
async def start_screening(
    application_id: str,
    db: Session = Depends(get_db)
):
    """开始HR筛选"""
    try:
        operator_id = CURRENT_USER_ID
        operator_name = CURRENT_USER_NAME

        application = await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.HR_SCREENING,
            operator_id=operator_id,
            operator_name=operator_name,
            reason="HR开始筛选"
        )

        # 更新查看时间
        application.hr_viewed_at = datetime.now()
        db.commit()

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


@router.post("/{application_id}/phone-communication", response_model=dict)
async def phone_communication(
    application_id: str,
    request: PhoneCommunicationRequest,
    db: Session = Depends(get_db)
):
    """记录电话沟通结果"""
    try:
        application = ApplicationService.get_by_id(db=db, application_id=application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        operator_id = CURRENT_USER_ID

        # 记录沟通信息
        application.intention_contact_method = "manual"
        application.intention_contact_result = request.result
        application.intention_contact_notes = request.notes
        application.intention_contacted_at = datetime.now()
        application.intention_contacted_by = operator_id
        db.commit()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{application_id}/reject", response_model=dict)
async def reject_application(
    application_id: str,
    request: StatusTransitionRequest,
    db: Session = Depends(get_db)
):
    """HR淘汰"""
    try:
        operator_id = CURRENT_USER_ID
        operator_name = CURRENT_USER_NAME

        application = await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=ApplicationStatus.HR_REJECTED,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=request.reason
        )
        if request.interviewer_evaluation is not None:
            application.interviewer_evaluation = request.interviewer_evaluation
            db.commit()
            db.refresh(application)

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


@router.post("/{application_id}/transfer-job", response_model=dict)
async def transfer_application_to_job(
    application_id: str,
    request: TransferApplicationRequest,
    db: Session = Depends(get_db)
):
    """转推候选人到其他职位，创建新的应聘记录。"""
    try:
        source_application = ApplicationService.get_by_id(db=db, application_id=application_id)
        if not source_application:
            raise HTTPException(status_code=404, detail="Application not found")

        target_job = db.query(Job).filter(Job.id == request.target_job_id).first()
        if not target_job:
            raise HTTPException(status_code=404, detail="目标职位不存在")

        duplicate = ApplicationService.get_by_candidate_and_job(
            db=db,
            candidate_id=source_application.candidate_id,
            job_id=request.target_job_id,
        )
        if duplicate:
            raise HTTPException(status_code=400, detail="候选人已在目标职位流程中")

        import uuid
        new_application = ApplicationService.create(
            db=db,
            application_id=f"app_{uuid.uuid4().hex[:12]}",
            candidate_id=source_application.candidate_id,
            job_id=request.target_job_id,
            resume_url=source_application.resume_url,
            resume_parsed_data=source_application.resume_parsed_data,
            source=f"转推自 {source_application.job_id}",
            hr_id=source_application.hr_id,
        )
        history = ApplicationStatusHistory(
            id=f"ash_{datetime.now().timestamp()}",
            application_id=source_application.id,
            from_status=source_application.status,
            to_status=source_application.status,
            operator_id=CURRENT_USER_ID,
            operator_name=CURRENT_USER_NAME,
            reason=f"转推到职位：{target_job.title}。{request.reason or ''}".strip(),
        )
        db.add(history)
        db.commit()

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": new_application.id,
                "target_job_id": request.target_job_id,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}/status-history", response_model=dict)
async def get_status_history(
    application_id: str,
    db: Session = Depends(get_db)
):
    """获取状态历史"""
    try:
        history = ApplicationService.get_status_history(db=db, application_id=application_id)

        items = []
        for h in history:
            items.append({
                "id": h.id,
                "from_status": h.from_status.value if h.from_status else None,
                "to_status": h.to_status.value,
                "to_status_label": ApplicationStateMachine.get_status_label(h.to_status),
                "reason": h.reason,
                "operator_name": h.operator_name,
                "created_at": h.created_at.isoformat() if h.created_at else None,
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


@router.post("/{application_id}/transition-status", response_model=dict)
async def transition_status(
    application_id: str,
    request: StatusTransitionRequest,
    db: Session = Depends(get_db)
):
    """状态流转（通用接口）"""
    try:
        operator_id = CURRENT_USER_ID
        operator_name = CURRENT_USER_NAME

        # 将字符串转换为枚举
        to_status = ApplicationStatus(request.to_status)

        application = await ApplicationService.transition_status(
            db=db,
            application_id=application_id,
            to_status=to_status,
            operator_id=operator_id,
            operator_name=operator_name,
            reason=request.reason
        )

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "status_label": ApplicationStateMachine.get_status_label(application.status)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{application_id}/undo", response_model=dict)
async def undo_last_status_change(
    application_id: str,
    request: UndoRequest,
    db: Session = Depends(get_db)
):
    """撤销最近一次状态变更，回到上一状态"""
    try:
        application = ApplicationService.get_by_id(db=db, application_id=application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        latest_history = (
            db.query(ApplicationStatusHistory)
            .filter(ApplicationStatusHistory.application_id == application_id)
            .order_by(ApplicationStatusHistory.created_at.desc())
            .first()
        )
        if not latest_history or not latest_history.from_status:
            raise HTTPException(status_code=400, detail="没有可撤销的状态变更")

        previous_status = latest_history.from_status
        undo_history = ApplicationStatusHistory(
            id=f"ash_undo_{datetime.now().timestamp()}",
            application_id=application.id,
            from_status=application.status,
            to_status=previous_status,
            operator_id=CURRENT_USER_ID,
            operator_name=CURRENT_USER_NAME,
            reason=request.reason,
        )
        db.add(undo_history)
        if application.status == ApplicationStatus.INTERVIEWER_REJECTED and previous_status != ApplicationStatus.INTERVIEWER_REJECTED:
            application.rejection_reason = None
        application.status = previous_status
        application.last_status_change_at = datetime.now()
        db.commit()
        db.refresh(application)

        return {
            "code": 0,
            "message": "success",
            "data": {
                "application_id": application.id,
                "status": application.status.value,
                "status_label": ApplicationStateMachine.get_status_label(application.status),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
