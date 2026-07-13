"""Application schemas - 应聘记录相关的Pydantic模型"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    """简历上传响应"""
    application_id: str
    candidate_id: str
    job_id: str
    status: str
    resume_url: Optional[str]
    parsed_data: Optional[Dict[str, Any]]
    is_duplicate: bool
    duplicate_reason: Optional[str]


class ApplicationListItem(BaseModel):
    """应聘记录列表项"""
    id: str
    candidate_id: str
    candidate_name: str
    candidate_phone: Optional[str]
    candidate_email: Optional[str]
    job_id: str
    job_title: str
    status: str
    status_label: str
    source: Optional[str]
    applied_at: datetime
    last_status_change_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApplicationDetail(BaseModel):
    """应聘记录详情"""
    id: str
    candidate: Dict[str, Any]
    job: Dict[str, Any]
    status: str
    status_label: str
    resume_url: Optional[str]
    resume_parsed_data: Optional[Dict[str, Any]]
    source: Optional[str]
    hr_name: Optional[str]
    recruiter_name: Optional[str]
    applied_at: datetime
    last_status_change_at: Optional[datetime]
    is_locked: bool
    locked_by: Optional[str]
    status_history: Optional[list]
