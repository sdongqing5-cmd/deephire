"""Candidate schemas - 候选人相关的Pydantic模型"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CandidateBase(BaseModel):
    """候选人基础信息"""
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None


class CandidateCreate(CandidateBase):
    """创建候选人"""
    pass


class CandidateUpdate(BaseModel):
    """更新候选人"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    years_of_experience: Optional[int] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    status: Optional[str] = None


class CandidateResponse(CandidateBase):
    """候选人响应"""
    id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    latest_contacted_at: Optional[datetime]

    class Config:
        from_attributes = True


class CandidateListItem(BaseModel):
    """候选人列表项"""
    id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    current_company: Optional[str]
    current_title: Optional[str]
    years_of_experience: Optional[int]
    location: Optional[str]
    tags: Optional[List[str]]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
