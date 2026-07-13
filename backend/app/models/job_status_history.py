"""Job status history model - 职位状态历史"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.job import JobStatus


class JobStatusHistory(Base):
    """职位状态历史记录"""
    __tablename__ = "job_status_history"

    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)

    # 状态变更
    from_status = Column(SQLEnum(JobStatus))
    to_status = Column(SQLEnum(JobStatus), nullable=False)

    # 变更信息
    reason = Column(Text)  # 状态变更原因
    operator_id = Column(String, ForeignKey("users.id"))  # 操作人
    operator_name = Column(String)  # 操作人姓名（冗余字段，便于查询）

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<JobStatusHistory(job_id={self.job_id}, {self.from_status}->{self.to_status})>"
