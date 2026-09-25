"""Interview schemas - 面试相关的Pydantic模型"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.interview import InterviewType, InterviewStatus, InterviewResult


class InterviewCreate(BaseModel):
    """创建面试"""
    application_id: str
    job_id: str
    candidate_id: str
    interviewer_id: str
    interviewer_name: str
    interview_type: InterviewType
    title: Optional[str] = None
    scorecard_template_id: Optional[str] = None
    scheduled_at: datetime
    duration: int = 60  # 默认60分钟
    location: Optional[str] = None
    meeting_link: Optional[str] = None


class InterviewUpdate(BaseModel):
    """更新面试"""
    interviewer_id: Optional[str] = None
    interviewer_name: Optional[str] = None
    title: Optional[str] = None
    scorecard_template_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None


class InterviewEvaluation(BaseModel):
    """面试评价"""
    result: InterviewResult
    score: Optional[int] = None  # 评分 1-10
    feedback: Optional[str] = None  # 面试反馈


class InterviewResponse(BaseModel):
    """面试响应"""
    id: str
    application_id: str
    job_id: str
    candidate_id: str
    interview_type: InterviewType
    title: Optional[str]
    interviewer_id: str
    interviewer_name: str
    scorecard_template_id: Optional[str]
    scheduled_at: datetime
    duration: int
    location: Optional[str]
    meeting_link: Optional[str]
    status: InterviewStatus
    result: Optional[InterviewResult]
    feedback: Optional[str]
    score: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class InterviewListItem(BaseModel):
    """面试列表项"""
    id: str
    application_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    interview_type: InterviewType
    interviewer_name: str
    scheduled_at: datetime
    duration: int
    location: Optional[str]
    status: InterviewStatus
    result: Optional[InterviewResult]

    class Config:
        from_attributes = True


class InterviewDetail(BaseModel):
    """面试详情"""
    interview: InterviewResponse
    candidate: dict
    job: dict
    application_status: str
