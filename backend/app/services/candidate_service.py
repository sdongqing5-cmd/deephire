"""Candidate service - 候选人业务逻辑"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from app.models.candidate import Candidate
from app.models.application import Application
from app.schemas.candidate import CandidateCreate, CandidateUpdate


class CandidateService:
    """候选人服务"""

    @staticmethod
    def create(db: Session, candidate_data: CandidateCreate) -> Candidate:
        """创建候选人"""
        candidate_id = f"cand_{uuid.uuid4().hex[:12]}"

        candidate = Candidate(
            id=candidate_id,
            name=candidate_data.name,
            phone=candidate_data.phone,
            email=candidate_data.email,
            current_company=candidate_data.current_company,
            current_title=candidate_data.current_title,
            years_of_experience=candidate_data.years_of_experience,
            location=candidate_data.location,
            tags=candidate_data.tags or [],
            source=candidate_data.source,
            status="new",
        )

        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        return candidate

    @staticmethod
    def get_by_id(db: Session, candidate_id: str) -> Optional[Candidate]:
        """根据ID获取候选人"""
        return db.query(Candidate).filter(Candidate.id == candidate_id).first()

    @staticmethod
    def find_by_contact(
        db: Session,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[Candidate]:
        """根据联系方式查找候选人（用于查重）"""
        if not phone and not email:
            return None

        query = db.query(Candidate)
        conditions = []

        if phone:
            conditions.append(Candidate.phone == phone)
        if email:
            conditions.append(Candidate.email == email)

        return query.filter(or_(*conditions)).first()

    @staticmethod
    def list_candidates(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        source: Optional[str] = None,
        location: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Candidate]:
        """获取候选人列表"""
        query = db.query(Candidate)

        # 过滤条件
        if status:
            query = query.filter(Candidate.status == status)
        if source:
            query = query.filter(Candidate.source == source)
        if location:
            query = query.filter(Candidate.location.ilike(f"%{location}%"))
        if search_query:
            query = query.filter(
                or_(
                    Candidate.name.ilike(f"%{search_query}%"),
                    Candidate.email.ilike(f"%{search_query}%"),
                    Candidate.phone.ilike(f"%{search_query}%"),
                    Candidate.current_company.ilike(f"%{search_query}%"),
                )
            )

        # 排序：最新创建的在前
        query = query.order_by(Candidate.created_at.desc())

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session,
        candidate_id: str,
        candidate_data: CandidateUpdate
    ) -> Optional[Candidate]:
        """更新候选人信息"""
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return None

        # 更新字段
        update_data = candidate_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)

        db.commit()
        db.refresh(candidate)

        return candidate

    @staticmethod
    def get_application_count(db: Session, candidate_id: str) -> int:
        """获取候选人的应聘次数"""
        return db.query(Application).filter(
            Application.candidate_id == candidate_id
        ).count()

    @staticmethod
    def get_applications(db: Session, candidate_id: str) -> List[Application]:
        """获取候选人的所有应聘记录"""
        return db.query(Application)\
            .filter(Application.candidate_id == candidate_id)\
            .order_by(Application.applied_at.desc())\
            .all()

    @staticmethod
    def check_duplicate(
        db: Session,
        phone: Optional[str],
        email: Optional[str],
        job_id: str
    ) -> tuple[bool, Optional[str], Optional[Candidate]]:
        """
        检查是否重复应聘

        返回: (是否重复, 重复原因, 已存在的候选人)
        """
        # 1. 根据联系方式查找候选人
        existing_candidate = CandidateService.find_by_contact(db, phone, email)

        if not existing_candidate:
            return False, None, None

        # 2. 检查是否已经应聘过该职位
        existing_application = db.query(Application).filter(
            Application.candidate_id == existing_candidate.id,
            Application.job_id == job_id
        ).first()

        if existing_application:
            # 检查状态是否允许重新应聘
            non_reapply_statuses = [
                "new", "hr_screening", "hr_interview_scheduled",
                "hr_interviewing", "sent_to_interviewer",
                "interview_intention_communication", "interview_time_confirming",
                "department_interview_scheduled", "department_interviewing",
                "assessment_in_progress", "final_interview_scheduled",
                "final_interviewing", "salary_negotiation",
                "offer_pending", "offer_sent", "offer_accepted",
                "pending_onboard"
            ]

            if existing_application.status.value in non_reapply_statuses:
                return True, f"该候选人已在流程中（状态：{existing_application.status.value}）", existing_candidate

        # 3. 候选人存在但可以重新应聘
        return False, None, existing_candidate
