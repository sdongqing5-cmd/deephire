"""InterviewerScreening model - 面试官简历筛选记录模型"""

import enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.database import Base


class ScreeningResult(str, enum.Enum):
    """筛选结果枚举"""
    PASS = "pass"
    REJECT = "reject"


class InterviewerScreening(Base):
    """面试官简历筛选记录"""
    __tablename__ = "interviewer_screenings"

    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    interviewer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    interviewer_name = Column(String)

    # 筛选结果
    result = Column(Enum(ScreeningResult), nullable=True)  # pass（通过）, reject（淘汰）
    comments = Column(Text)  # 筛选意见（简单填写）

    # 筛选时间
    screened_at = Column(DateTime(timezone=True), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<InterviewerScreening(id={self.id}, application_id={self.application_id}, result={self.result})>"
