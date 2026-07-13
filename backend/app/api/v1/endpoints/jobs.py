"""Job management endpoints - 职位管理接口"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.job import Job, JobStatus, JobCategory, RecruitmentType
from app.services.job_service import JobService
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListItem,
    JobStatusUpdate,
)

router = APIRouter()


# TODO: 替换为真实的用户认证
def get_current_user_id() -> str:
    """获取当前用户ID（临时实现）"""
    return "1"  # 默认返回HR用户ID


@router.post("/", response_model=JobResponse, summary="创建职位")
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    创建新职位

    - **title**: 职位标题
    - **department_id**: 所属部门ID
    - **location**: 工作地点
    - **category**: 岗位类别
    - **recruitment_type**: 招聘类别（社招/校招/实习）
    - **hiring_manager_id**: 招聘负责人ID
    """
    job = JobService.create(db, job_data, current_user_id)
    return job


@router.get("/", response_model=List[JobListItem], summary="获取职位列表")
async def list_jobs(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    status: Optional[JobStatus] = Query(None, description="职位状态过滤"),
    category: Optional[JobCategory] = Query(None, description="岗位类别过滤"),
    recruitment_type: Optional[RecruitmentType] = Query(None, description="招聘类别过滤"),
    is_urgent: Optional[bool] = Query(None, description="是否加急过滤"),
    hiring_manager_id: Optional[str] = Query(None, description="招聘负责人ID过滤"),
    db: Session = Depends(get_db),
):
    """
    获取职位列表，支持分页和多条件过滤

    默认按加急优先、创建时间倒序排列
    """
    jobs = JobService.list_jobs(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        category=category,
        recruitment_type=recruitment_type,
        is_urgent=is_urgent,
        hiring_manager_id=hiring_manager_id,
    )
    return jobs


@router.get("/{job_id}", response_model=JobResponse, summary="获取职位详情")
async def get_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    根据ID获取职位详情

    自动增加浏览次数
    """
    job = JobService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    # 增加浏览次数
    JobService.increment_view_count(db, job_id)

    return job


@router.put("/{job_id}", response_model=JobResponse, summary="更新职位信息")
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    更新职位信息

    支持部分字段更新
    """
    job = JobService.update(db, job_id, job_data, current_user_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    return job


@router.patch("/{job_id}/status", response_model=JobResponse, summary="更新职位状态")
async def update_job_status(
    job_id: str,
    status_data: JobStatusUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    更新职位状态

    状态转换：
    - draft → recruiting（发布招聘）
    - recruiting → paused（暂停招聘）
    - paused → recruiting（恢复招聘）
    - recruiting/paused → closed（结束招聘）
    - any → cancelled（取消招聘）
    """
    job = JobService.update_status(
        db=db,
        job_id=job_id,
        new_status=status_data.status,
        operator_id=current_user_id,
        reason=status_data.reason
    )

    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    return job


@router.delete("/{job_id}", summary="删除职位")
async def delete_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    删除职位（软删除，实际是设置为已取消状态）
    """
    success = JobService.delete(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="职位不存在")

    return {"code": 0, "message": "删除成功"}


@router.get("/{job_id}/status-history", summary="获取职位状态历史")
async def get_job_status_history(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    获取职位的状态变更历史记录
    """
    job = JobService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    history = JobService.get_status_history(db, job_id)

    return {
        "code": 0,
        "data": [
            {
                "id": h.id,
                "from_status": h.from_status.value if h.from_status else None,
                "to_status": h.to_status.value,
                "reason": h.reason,
                "operator_id": h.operator_id,
                "created_at": h.created_at.isoformat(),
            }
            for h in history
        ]
    }
