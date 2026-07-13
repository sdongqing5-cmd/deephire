"""Assessment model - 测评记录模型"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class AssessmentStatus(str, enum.Enum):
    """测评状态"""
    INVITED = "invited"          # 已邀请
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 未通过
    EXPIRED = "expired"          # 已过期


class Assessment(Base):
    """测评记录"""
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), index=True)

    # 测评信息
    assessment_type = Column(String)  # 测评类型：商推、SHL等
    assessment_url = Column(Text)  # 测评链接

    # 状态
    status = Column(SQLEnum(AssessmentStatus), nullable=False, default=AssessmentStatus.INVITED, index=True)

    # 结果
    score = Column(Float)  # 得分
    result_data = Column(Text)  # 测评结果数据（JSON格式）
    report_url = Column(Text)  # 测评报告URL

    # 有效期
    valid_until = Column(DateTime(timezone=True))

    # 时间戳
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Assessment(id={self.id}, application_id={self.application_id}, type={self.assessment_type}, status={self.status})>"
