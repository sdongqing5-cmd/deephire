"""Application service - 应聘记录业务逻辑扩展"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import uuid

from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.user import User
from app.services.application_state_machine import ApplicationStateMachine


class ApplicationQueryService:
    """应聘记录查询服务"""

    @staticmethod
    def list_applications(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        job_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        status: Optional[ApplicationStatus] = None,
        hr_id: Optional[str] = None,
        recruiter_id: Optional[str] = None,
    ) -> List[dict]:
        """
        获取应聘记录列表（带候选人和职位信息）
        """
        query = db.query(
            Application,
            Candidate.name.label("candidate_name"),
            Candidate.phone.label("candidate_phone"),
            Candidate.email.label("candidate_email"),
            Job.title.label("job_title")
        ).join(
            Candidate, Application.candidate_id == Candidate.id
        ).join(
            Job, Application.job_id == Job.id
        )

        # 过滤条件
        if job_id:
            query = query.filter(Application.job_id == job_id)
        if candidate_id:
            query = query.filter(Application.candidate_id == candidate_id)
        if status:
            query = query.filter(Application.status == status)
        if hr_id:
            query = query.filter(Application.hr_id == hr_id)
        if recruiter_id:
            query = query.filter(Application.recruiter_id == recruiter_id)

        # 排序：最新的在前
        query = query.order_by(Application.applied_at.desc())

        results = query.offset(skip).limit(limit).all()

        # 转换为字典格式
        applications = []
        for app, cand_name, cand_phone, cand_email, job_title in results:
            applications.append({
                "id": app.id,
                "candidate_id": app.candidate_id,
                "candidate_name": cand_name,
                "candidate_phone": cand_phone,
                "candidate_email": cand_email,
                "job_id": app.job_id,
                "job_title": job_title,
                "status": app.status.value,
                "status_label": ApplicationQueryService._get_status_label(app.status),
                "source": app.source,
                "applied_at": app.applied_at,
                "last_status_change_at": app.last_status_change_at,
            })

        return applications

    @staticmethod
    def get_application_detail(db: Session, application_id: str) -> Optional[dict]:
        """获取应聘记录详情"""
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return None

        # 获取候选人信息
        candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()

        # 获取职位信息
        job = db.query(Job).filter(Job.id == app.job_id).first()

        # 获取HR和招聘专员信息
        hr = db.query(User).filter(User.id == app.hr_id).first() if app.hr_id else None
        recruiter = db.query(User).filter(User.id == app.recruiter_id).first() if app.recruiter_id else None

        # 获取状态历史
        status_history = db.query(ApplicationStatusHistory)\
            .filter(ApplicationStatusHistory.application_id == application_id)\
            .order_by(ApplicationStatusHistory.created_at.desc())\
            .all()

        return {
            "id": app.id,
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "phone": candidate.phone,
                "email": candidate.email,
                "current_company": candidate.current_company,
                "current_title": candidate.current_title,
                "years_of_experience": candidate.years_of_experience,
                "location": candidate.location,
            } if candidate else None,
            "job": {
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "category": job.category.value,
            } if job else None,
            "status": app.status.value,
            "status_label": ApplicationQueryService._get_status_label(app.status),
            "resume_url": app.resume_url,
            "resume_parsed_data": app.resume_parsed_data,
            "source": app.source,
            "hr_name": hr.name if hr else None,
            "recruiter_name": recruiter.name if recruiter else None,
            "applied_at": app.applied_at,
            "last_status_change_at": app.last_status_change_at,
            "is_locked": app.is_locked,
            "locked_by": app.locked_by,
            "status_history": [
                {
                    "from_status": h.from_status.value if h.from_status else None,
                    "to_status": h.to_status.value,
                    "reason": h.reason,
                    "operator_name": h.operator_name,
                    "created_at": h.created_at.isoformat(),
                }
                for h in status_history
            ]
        }

    @staticmethod
    def transition_status(
        db: Session,
        application_id: str,
        to_status: ApplicationStatus,
        operator_id: str,
        operator_name: str,
        reason: Optional[str] = None
    ) -> Optional[Application]:
        """
        转换应聘状态

        返回: 更新后的应聘记录，如果转换失败返回 None
        """
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            return None

        # 验证状态转换是否合法
        current_status = app.status
        allowed_transitions = ApplicationStateMachine.TRANSITIONS.get(current_status, [])

        if to_status not in allowed_transitions:
            raise ValueError(
                f"非法状态转换: {current_status.value} -> {to_status.value}"
            )

        # 更新状态
        app.status = to_status
        app.last_status_change_at = datetime.now()

        # 记录状态历史
        history = ApplicationStatusHistory(
            id=f"ash_{uuid.uuid4().hex[:12]}",
            application_id=application_id,
            from_status=current_status,
            to_status=to_status,
            reason=reason,
            operator_id=operator_id,
            operator_name=operator_name,
        )
        db.add(history)

        db.commit()
        db.refresh(app)

        return app

    @staticmethod
    def _get_status_label(status: ApplicationStatus) -> str:
        """获取状态中文标签"""
        labels = {
            ApplicationStatus.NEW: "新简历",
            ApplicationStatus.HR_SCREENING: "HR筛选中",
            ApplicationStatus.HR_REJECTED: "HR淘汰",
            ApplicationStatus.HR_INTERVIEW_SCHEDULED: "HR初筛面试已安排",
            ApplicationStatus.HR_INTERVIEWING: "HR初筛面试中",
            ApplicationStatus.HR_INTERVIEW_COMPLETED: "HR初筛面试完成",
            ApplicationStatus.HR_INTERVIEW_REJECTED: "HR初筛淘汰",
            ApplicationStatus.SENT_TO_INTERVIEWER: "已推送给面试官",
            ApplicationStatus.INTERVIEWER_HOLD: "面试官待定",
            ApplicationStatus.INTERVIEWER_REJECTED: "面试官淘汰",
            ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION: "待约面试",
            ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW: "候选人放弃面试",
            ApplicationStatus.INTERVIEW_TIME_CONFIRMING: "等待确认面试时间",
            ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED: "部门面试已安排",
            ApplicationStatus.DEPARTMENT_INTERVIEWING: "部门面试中",
            ApplicationStatus.DEPARTMENT_INTERVIEW_HOLD: "部门面试待定",
            ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED: "部门面试通过",
            ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED: "部门面试淘汰",
            ApplicationStatus.VERBAL_OFFER_ACCEPTED: "接受口头Offer",
            ApplicationStatus.OFFER_PENDING: "待发Offer",
            ApplicationStatus.OFFER_APPROVAL: "Offer审批中",
            ApplicationStatus.OFFER_APPROVAL_REJECTED: "Offer审批拒绝",
            ApplicationStatus.OFFER_SENT: "已发Offer",
            ApplicationStatus.OFFER_NOT_AGREED: "Offer没谈拢",
            ApplicationStatus.OFFER_ACCEPTED: "已接受Offer",
            ApplicationStatus.OFFER_REJECTED: "已拒绝Offer",
            ApplicationStatus.PENDING_ONBOARD: "待入职",
            ApplicationStatus.ONBOARD_CANCELLED: "取消入职",
            ApplicationStatus.ONBOARDED: "已入职",
        }
        return labels.get(status, status.value)
