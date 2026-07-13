"""Interview model - 面试记录模型（V2完整版）"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class InterviewType(str, enum.Enum):
    """面试类型"""
    HR_INITIAL = "hr_initial"          # HR初筛面试
    DEPARTMENT = "department"          # 部门面试
    HR_REINTERVIEW = "hr_reinterview"  # HR复试
    FINAL = "final"                    # 终面


class InterviewStatus(str, enum.Enum):
    """面试状态"""
    SCHEDULED = "scheduled"      # 已安排
    CONFIRMED = "confirmed"      # 候选人已确认
    DECLINED = "declined"        # 候选人拒绝
    CANCELLED = "cancelled"      # 已取消
    RESCHEDULED = "rescheduled"  # 已改期
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    NO_SHOW = "no_show"         # 候选人未到


class InterviewResult(str, enum.Enum):
    """面试结果"""
    PENDING = "pending"          # 待评价
    PASS = "pass"               # 通过
    FAIL = "fail"               # 未通过
    HOLD = "hold"               # 待定


class Interview(Base):
    """面试记录"""
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), index=True)

    # 🆕 面试类型
    interview_type = Column(SQLEnum(InterviewType), nullable=False, index=True)

    # 面试信息
    title = Column(String)  # 面试主题

    # 面试官
    interviewer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    interviewer_name = Column(String)

    # 评价表 (暂时不使用外键，等 scorecard_templates 表创建后再添加)
    scorecard_template_id = Column(String)

    # 时间地点
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    duration = Column(Integer, default=60)  # 面试时长（分钟）
    location = Column(String)  # 面试地点
    meeting_link = Column(String)  # 线上面试链接

    # 状态和结果
    status = Column(SQLEnum(InterviewStatus), nullable=False, default=InterviewStatus.SCHEDULED, index=True)
    result = Column(SQLEnum(InterviewResult), default=InterviewResult.PENDING)

    # 评价
    feedback = Column(Text)  # 面试反馈
    score = Column(Integer)  # 评分
    evaluation_data = Column(Text)  # 评价表数据（JSON）

    # 通知
    notification_sent_to_candidate = Column(Boolean, default=False)
    notification_sent_to_interviewer = Column(Boolean, default=False)
    candidate_confirmed_at = Column(DateTime(timezone=True))

    # 时间戳
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Interview(id={self.id}, type={self.interview_type}, status={self.status}, result={self.result})>"
