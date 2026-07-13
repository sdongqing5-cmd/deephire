"""Application model - 应聘记录模型（V2完整版）"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    """应聘状态 - 完整生命周期"""

    # ==================== 简历阶段 ====================
    NEW = "new"                                    # 新简历
    HR_SCREENING = "hr_screening"                  # HR筛选中（含电话沟通确认意向）
    HR_REJECTED = "hr_rejected"                    # HR淘汰

    # ==================== HR初筛面试阶段 ====================
    HR_INTERVIEW_SCHEDULED = "hr_interview_scheduled"      # HR初筛面试已安排
    HR_INTERVIEWING = "hr_interviewing"                    # HR初筛面试进行中
    HR_INTERVIEW_COMPLETED = "hr_interview_completed"      # HR初筛面试已完成
    HR_INTERVIEW_REJECTED = "hr_interview_rejected"        # HR初筛面试淘汰

    # ==================== 面试官筛选阶段 ====================
    SENT_TO_INTERVIEWER = "sent_to_interviewer"           # 推送给面试官（面试官筛选简历）
    INTERVIEWER_REJECTED = "interviewer_rejected"          # 面试官淘汰

    # ==================== 面试意向沟通阶段 ====================
    INTERVIEW_INTENTION_COMMUNICATION = "interview_intention_communication"  # 面试意向沟通中
    CANDIDATE_DECLINED_INTERVIEW = "candidate_declined_interview"            # 候选人放弃面试

    # ==================== 面试时间确认阶段 ====================
    INTERVIEW_TIME_CONFIRMING = "interview_time_confirming"  # 等待候选人确认面试时间

    # ==================== 部门面试阶段 ====================
    DEPARTMENT_INTERVIEW_SCHEDULED = "department_interview_scheduled"  # 部门面试已安排
    DEPARTMENT_INTERVIEWING = "department_interviewing"                # 部门面试进行中
    DEPARTMENT_INTERVIEW_COMPLETED = "department_interview_completed"  # 部门面试已完成
    DEPARTMENT_INTERVIEW_REJECTED = "department_interview_rejected"    # 部门面试淘汰

    # ==================== 测评阶段（可选）====================
    ASSESSMENT_INVITED = "assessment_invited"              # 测评邀请已发送
    ASSESSMENT_IN_PROGRESS = "assessment_in_progress"      # 测评进行中
    ASSESSMENT_COMPLETED = "assessment_completed"          # 测评已完成
    ASSESSMENT_FAILED = "assessment_failed"                # 测评未通过

    # ==================== HR复试阶段（可选）====================
    HR_REINTERVIEW_SCHEDULED = "hr_reinterview_scheduled"  # HR复试已安排
    HR_REINTERVIEWING = "hr_reinterviewing"                # HR复试进行中
    HR_REINTERVIEW_COMPLETED = "hr_reinterview_completed"  # HR复试已完成
    HR_REINTERVIEW_REJECTED = "hr_reinterview_rejected"    # HR复试淘汰

    # ==================== 终面阶段 ====================
    FINAL_INTERVIEW_SCHEDULED = "final_interview_scheduled"  # 终面已安排
    FINAL_INTERVIEWING = "final_interviewing"                # 终面进行中
    FINAL_INTERVIEW_COMPLETED = "final_interview_completed"  # 终面已完成
    FINAL_INTERVIEW_REJECTED = "final_interview_rejected"    # 终面淘汰

    # ==================== Offer阶段 ====================
    SALARY_NEGOTIATION = "salary_negotiation"              # 谈薪中
    SALARY_REJECTED = "salary_rejected"                    # 谈薪失败
    VERBAL_OFFER_ACCEPTED = "verbal_offer_accepted"        # 接受口头Offer
    OFFER_APPROVAL = "offer_approval"                      # Offer审批中
    OFFER_APPROVAL_REJECTED = "offer_approval_rejected"    # Offer审批拒绝
    OFFER_PENDING = "offer_pending"                        # 待发Offer
    OFFER_SENT = "offer_sent"                              # 已发Offer
    OFFER_REJECTED = "offer_rejected"                      # 已拒绝Offer
    OFFER_ACCEPTED = "offer_accepted"                      # 已接受Offer

    # ==================== 入职阶段 ====================
    PENDING_ONBOARD = "pending_onboard"                    # 待入职
    ONBOARD_CANCELLED = "onboard_cancelled"                # 取消入职
    ONBOARDED = "onboarded"                                # 已入职

    # ==================== 其他 ====================
    CANDIDATE_WITHDRAWN = "candidate_withdrawn"            # 候选人主动退出


class Application(Base):
    """应聘记录 - 核心表"""
    __tablename__ = "applications"

    # ==================== 基本信息 ====================
    id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)

    # ==================== 状态 ====================
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW, index=True)

    # ==================== 简历信息 ====================
    resume_url = Column(String)  # 简历文件URL
    resume_parsed_data = Column(Text)  # 解析后的简历数据（JSON）

    # ==================== 来源 ====================
    source = Column(String)  # 简历来源：主动投递、内推、猎头等

    # ==================== 负责人 ====================
    hr_id = Column(String, ForeignKey("users.id"), index=True)  # 负责HR
    recruiter_id = Column(String, ForeignKey("users.id"))  # 招聘专员

    # ==================== 锁定信息 ====================
    is_locked = Column(Boolean, default=False, index=True)  # 是否锁定
    locked_by = Column(String, ForeignKey("users.id"))  # 锁定人
    locked_at = Column(DateTime(timezone=True))  # 锁定时间

    # ==================== 应聘次数统计 ====================
    application_count = Column(Integer, default=1)  # 该候选人应聘该职位的次数

    # ==================== 🆕 面试意向沟通 ====================
    intention_contact_method = Column(String)  # 联系方式：ai_call（智能外呼）, manual（人工联系）
    intention_contact_result = Column(String)  # 沟通结果：agreed（同意）, declined（拒绝）, no_answer（未接听）
    intention_contact_notes = Column(Text)  # 沟通备注
    intention_contacted_at = Column(DateTime(timezone=True))  # 沟通时间
    intention_contacted_by = Column(String, ForeignKey("users.id"))  # 沟通人

    # ==================== 🆕 面试时间确认 ====================
    interview_notification_sent_at = Column(DateTime(timezone=True))  # 面试通知发送时间
    interview_confirmed_at = Column(DateTime(timezone=True))  # 候选人确认时间
    interview_confirmation_token = Column(String)  # 确认token（用于邮件链接）

    # ==================== 面试流程配置 ====================
    interview_flow_config = Column(Text)  # 面试流程配置（JSON格式）
    # 示例：{"has_assessment": true, "has_hr_reinterview": false}

    # ==================== 时间戳 ====================
    applied_at = Column(DateTime(timezone=True), server_default=func.now())  # 投递时间
    hr_viewed_at = Column(DateTime(timezone=True))  # HR查看时间
    last_status_change_at = Column(DateTime(timezone=True))  # 最后状态变更时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Application(id={self.id}, candidate_id={self.candidate_id}, job_id={self.job_id}, status={self.status})>"


class ApplicationStatusHistory(Base):
    """应聘状态历史"""
    __tablename__ = "application_status_history"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)

    from_status = Column(SQLEnum(ApplicationStatus))
    to_status = Column(SQLEnum(ApplicationStatus), nullable=False)

    reason = Column(Text)  # 状态变更原因
    operator_id = Column(String, ForeignKey("users.id"))
    operator_name = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ApplicationStatusHistory(id={self.id}, application_id={self.application_id}, from={self.from_status}, to={self.to_status})>"
