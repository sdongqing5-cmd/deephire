"""Candidate management endpoints - 候选人管理接口"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.candidate import Candidate
from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.services.candidate_service import CandidateService
from app.services.resume_parser import PLACEHOLDER_VALUES, resume_parser
from app.services.job_service import JobService
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListItem,
)
from app.schemas.application import ResumeUploadResponse
import uuid
from datetime import datetime
import json

router = APIRouter()


# TODO: 替换为真实的用户认证
def get_current_user_id() -> str:
    """获取当前用户ID（临时实现）"""
    return "1"


def normalize_optional_text(value: Optional[str]) -> Optional[str]:
    """Treat blank form values as missing values."""
    if value is None:
        return None

    normalized = str(value).strip()
    if normalized.lower() in PLACEHOLDER_VALUES:
        return None
    return normalized or None


def normalize_optional_email(value: Optional[str]) -> Optional[str]:
    normalized = normalize_optional_text(value)
    if not normalized or "@" not in normalized:
        return None
    return normalized


def normalize_optional_int(value) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@router.post("/upload-resume", response_model=ResumeUploadResponse, summary="上传简历到职位")
async def upload_resume(
    job_id: str = Form(..., description="职位ID"),
    resume_file: UploadFile = File(..., description="简历文件（PDF或DOCX）"),
    candidate_name: Optional[str] = Form(None, description="候选人姓名"),
    candidate_phone: Optional[str] = Form(None, description="候选人电话"),
    candidate_email: Optional[str] = Form(None, description="候选人邮箱"),
    source: Optional[str] = Form("主动投递", description="简历来源"),
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    上传简历到具体职位

    流程：
    1. 验证职位是否存在
    2. 解析简历文件（提取信息）
    3. 查重检查
    4. 创建或更新候选人
    5. 创建应聘记录
    """
    candidate_name = normalize_optional_text(candidate_name)
    candidate_phone = normalize_optional_text(candidate_phone)
    candidate_email = normalize_optional_text(candidate_email)
    source = normalize_optional_text(source) or "主动投递"

    # 1. 验证职位
    job = JobService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    # 2. 解析简历。解析失败时不创建候选人，也不返回“上传成功”。
    try:
        file_content = await resume_file.read()
        file_extension = resume_file.filename.split('.')[-1].lower()

        if file_extension not in ['pdf', 'docx']:
            raise HTTPException(status_code=400, detail="仅支持 PDF 和 DOCX 格式")

        parsed_data = resume_parser.parse_resume(file_content, resume_file.filename)
        if candidate_name:
            parsed_data["name"] = candidate_name
        if candidate_phone:
            parsed_data["phone"] = candidate_phone
        if candidate_email:
            parsed_data["email"] = candidate_email
        parsed_data["name"] = normalize_optional_text(parsed_data.get("name")) or "未知候选人"
        parsed_data["phone"] = normalize_optional_text(parsed_data.get("phone"))
        parsed_data["email"] = normalize_optional_email(parsed_data.get("email"))
        parsed_data["current_company"] = normalize_optional_text(parsed_data.get("current_company"))
        parsed_data["current_title"] = normalize_optional_text(parsed_data.get("current_title"))
        parsed_data["location"] = normalize_optional_text(parsed_data.get("location"))
        parsed_data["years_of_experience"] = normalize_optional_int(parsed_data.get("years_of_experience"))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")

    contact_phone = candidate_phone or parsed_data.get("phone")
    contact_email = candidate_email or parsed_data.get("email")
    existing_contact_candidate = CandidateService.find_by_contact(
        db=db,
        phone=contact_phone,
        email=contact_email,
    )
    if existing_contact_candidate:
        existing_application_count = CandidateService.get_application_count(
            db,
            existing_contact_candidate.id,
        )
        if existing_application_count == 0:
            db.delete(existing_contact_candidate)
            db.commit()
        else:
            return ResumeUploadResponse(
                application_id="",
                candidate_id=existing_contact_candidate.id,
                job_id=job_id,
                status="duplicate",
                resume_url=None,
                parsed_data=parsed_data,
                is_duplicate=True,
                duplicate_reason="简历已存在，请先删除候选人及对应简历后再重新上传",
            )

    existing_candidate = None

    # 3. 查重检查。使用表单联系方式和解析出的联系方式，避免解析到已有邮箱时撞唯一索引。
    is_duplicate, duplicate_reason, existing_candidate = CandidateService.check_duplicate(
        db=db,
        phone=contact_phone,
        email=contact_email,
        job_id=job_id
    )

    if is_duplicate:
        return ResumeUploadResponse(
            application_id="",
            candidate_id=existing_candidate.id if existing_candidate else "",
            job_id=job_id,
            status="duplicate",
            resume_url=None,
            parsed_data=parsed_data,
            is_duplicate=True,
            duplicate_reason=duplicate_reason,
        )

    # 4. 创建或更新候选人
    if existing_candidate:
        candidate = existing_candidate
    else:
        candidate_create = CandidateCreate(
            name=parsed_data.get("name") or "未知候选人",
            phone=contact_phone,
            email=contact_email,
            current_company=parsed_data.get("current_company"),
            current_title=parsed_data.get("current_title"),
            years_of_experience=parsed_data.get("years_of_experience"),
            location=parsed_data.get("location"),
            tags=parsed_data.get("skills") or [],
            source=source,
        )
        candidate = CandidateService.create(db, candidate_create)

    # 5. 创建应聘记录
    application_id = f"app_{uuid.uuid4().hex[:12]}"
    resume_url = parsed_data.get("resume_url")

    application = Application(
        id=application_id,
        candidate_id=candidate.id,
        job_id=job_id,
        status=ApplicationStatus.NEW,
        resume_url=resume_url,
        resume_parsed_data=json.dumps(parsed_data, ensure_ascii=False),
        source=source,
        hr_id=current_user_id,
        applied_at=datetime.now(),
    )
    db.add(application)
    JobService.increment_application_count(db, job_id)
    db.commit()

    return ResumeUploadResponse(
        application_id=application.id,
        candidate_id=candidate.id,
        job_id=job_id,
        status=application.status.value,
        resume_url=resume_url,
        parsed_data=parsed_data,
        is_duplicate=False,
        duplicate_reason=None,
    )


@router.get("/", response_model=List[CandidateListItem], summary="获取候选人列表")
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取候选人列表，支持分页和多条件过滤"""
    candidates = CandidateService.list_candidates(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        source=source,
        location=location,
        search_query=search,
    )
    return candidates


@router.get("/{candidate_id}", response_model=CandidateResponse, summary="获取候选人详情")
async def get_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
):
    """获取候选人详细信息"""
    candidate = CandidateService.get_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse, summary="更新候选人信息")
async def update_candidate(
    candidate_id: str,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db),
):
    """更新候选人信息"""
    candidate = CandidateService.update(db, candidate_id, candidate_data)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")
    return candidate


@router.delete("/{candidate_id}", summary="删除候选人及其简历记录")
async def delete_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
):
    """删除候选人，以及该候选人的所有应聘记录和状态历史。"""
    candidate = CandidateService.get_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    applications = db.query(Application).filter(Application.candidate_id == candidate_id).all()
    application_ids = [application.id for application in applications]

    if application_ids:
        db.query(ApplicationStatusHistory).filter(
            ApplicationStatusHistory.application_id.in_(application_ids)
        ).delete(synchronize_session=False)
        db.query(Application).filter(
            Application.id.in_(application_ids)
        ).delete(synchronize_session=False)

    db.delete(candidate)
    db.commit()

    return {"code": 0, "message": "删除成功"}


@router.get("/{candidate_id}/applications", summary="获取候选人的应聘记录")
async def get_candidate_applications(
    candidate_id: str,
    db: Session = Depends(get_db),
):
    """获取候选人的所有应聘记录（X次应聘）"""
    candidate = CandidateService.get_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="候选人不存在")

    applications = CandidateService.get_applications(db, candidate_id)

    return {
        "code": 0,
        "data": {
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "application_count": len(applications),
            "applications": [
                {
                    "id": app.id,
                    "job_id": app.job_id,
                    "status": app.status.value,
                    "applied_at": app.applied_at.isoformat(),
                }
                for app in applications
            ]
        }
    }
