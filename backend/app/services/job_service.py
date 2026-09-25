"""Job service - 职位业务逻辑"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid

from app.models.job import Job, JobStatus, JobCategory, RecruitmentType
from app.models.job_status_history import JobStatusHistory
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    """职位服务"""

    @staticmethod
    def create(db: Session, job_data: JobCreate, created_by: str) -> Job:
        """创建职位"""
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        job = Job(
            id=job_id,
            title=job_data.title,
            department_id=job_data.department_id,
            location=job_data.location,
            category=job_data.category,
            recruitment_type=job_data.recruitment_type,
            level=job_data.level,
            description=job_data.description,
            requirements=job_data.requirements,
            responsibilities=job_data.responsibilities,
            notes=job_data.notes,
            salary_min=job_data.salary_min,
            salary_max=job_data.salary_max,
            openings=job_data.openings,
            is_urgent=job_data.is_urgent,
            is_third_party_headhunter_enabled=job_data.is_third_party_headhunter_enabled,
            interview_flow_config=job_data.interview_flow_config,
            valid_until=job_data.valid_until,
            hiring_manager_id=job_data.hiring_manager_id,
            department_manager_id=job_data.department_manager_id,
            status=JobStatus.DRAFT,
        )

        db.add(job)

        # 记录状态历史
        history = JobStatusHistory(
            id=f"jsh_{uuid.uuid4().hex[:12]}",
            job_id=job_id,
            to_status=JobStatus.DRAFT,
            operator_id=created_by,
            reason="创建职位"
        )
        db.add(history)

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_by_id(db: Session, job_id: str) -> Optional[Job]:
        """根据ID获取职位"""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def list_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[JobStatus] = None,
        category: Optional[JobCategory] = None,
        recruitment_type: Optional[RecruitmentType] = None,
        is_urgent: Optional[bool] = None,
        hiring_manager_id: Optional[str] = None,
    ) -> List[Job]:
        """获取职位列表"""
        query = db.query(Job)

        # 过滤条件
        if status:
            query = query.filter(Job.status == status)
        if category:
            query = query.filter(Job.category == category)
        if recruitment_type:
            query = query.filter(Job.recruitment_type == recruitment_type)
        if is_urgent is not None:
            query = query.filter(Job.is_urgent == is_urgent)
        if hiring_manager_id:
            query = query.filter(Job.hiring_manager_id == hiring_manager_id)

        # 排序：加急优先，然后按创建时间倒序
        query = query.order_by(Job.is_urgent.desc(), Job.created_at.desc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, job_id: str, job_data: JobUpdate, updated_by: str) -> Optional[Job]:
        """更新职位信息"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        # 更新字段
        update_data = job_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        job.updated_at = datetime.now()

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def update_status(
        db: Session,
        job_id: str,
        new_status: JobStatus,
        operator_id: str,
        reason: Optional[str] = None
    ) -> Optional[Job]:
        """更新职位状态"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        old_status = job.status
        job.status = new_status
        job.updated_at = datetime.now()

        # 特殊状态处理
        if new_status == JobStatus.RECRUITING and not job.published_at:
            job.published_at = datetime.now()
        elif new_status == JobStatus.CLOSED:
            job.closed_at = datetime.now()

        # 记录状态变更历史
        history = JobStatusHistory(
            id=f"jsh_{uuid.uuid4().hex[:12]}",
            job_id=job_id,
            from_status=old_status,
            to_status=new_status,
            operator_id=operator_id,
            reason=reason
        )
        db.add(history)

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def delete(db: Session, job_id: str) -> bool:
        """删除职位（软删除，实际是改为已取消状态）"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False

        job.status = JobStatus.CANCELLED
        job.updated_at = datetime.now()

        db.commit()
        return True

    @staticmethod
    def get_status_history(db: Session, job_id: str) -> List[JobStatusHistory]:
        """获取职位状态历史"""
        return db.query(JobStatusHistory)\
            .filter(JobStatusHistory.job_id == job_id)\
            .order_by(JobStatusHistory.created_at.desc())\
            .all()

    @staticmethod
    def increment_view_count(db: Session, job_id: str) -> None:
        """增加浏览次数"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.view_count += 1
            db.commit()

    @staticmethod
    def increment_application_count(db: Session, job_id: str) -> None:
        """增加应聘人数"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.application_count += 1
            db.commit()
