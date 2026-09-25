"""Job schemas - 职位相关的Pydantic模型"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.job import JobStatus, JobCategory, RecruitmentType, JobLevel


class JobBase(BaseModel):
    """职位基础信息"""
    title: str = Field(..., description="职位标题")
    department_id: str = Field(..., description="所属部门ID")
    location: str = Field(..., description="工作地点")
    category: JobCategory = Field(..., description="岗位类别")
    recruitment_type: RecruitmentType = Field(default=RecruitmentType.SOCIAL, description="招聘类别")
    level: Optional[JobLevel] = Field(None, description="职位级别")
    description: Optional[str] = Field(None, description="职位描述/JD")
    requirements: Optional[str] = Field(None, description="任职要求")
    responsibilities: Optional[str] = Field(None, description="工作职责")
    notes: Optional[str] = Field(None, description="备注")
    salary_min: Optional[int] = Field(None, description="最低薪资")
    salary_max: Optional[int] = Field(None, description="最高薪资")
    openings: int = Field(default=1, description="招聘人数")
    is_urgent: bool = Field(default=False, description="是否加急")
    is_third_party_headhunter_enabled: bool = Field(default=False, description="是否开启第三方猎头")
    interview_flow_config: Optional[str] = Field(None, description="面试工作流配置JSON")
    valid_until: Optional[datetime] = Field(None, description="职位有效期")
    hiring_manager_id: str = Field(..., description="招聘负责人ID")
    department_manager_id: Optional[str] = Field(None, description="部门负责人ID")


class JobCreate(JobBase):
    """创建职位"""
    pass


class JobUpdate(BaseModel):
    """更新职位"""
    title: Optional[str] = None
    department_id: Optional[str] = None
    location: Optional[str] = None
    category: Optional[JobCategory] = None
    recruitment_type: Optional[RecruitmentType] = None
    level: Optional[JobLevel] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    notes: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    openings: Optional[int] = None
    is_urgent: Optional[bool] = None
    is_third_party_headhunter_enabled: Optional[bool] = None
    interview_flow_config: Optional[str] = None
    valid_until: Optional[datetime] = None
    hiring_manager_id: Optional[str] = None
    department_manager_id: Optional[str] = None


class JobResponse(JobBase):
    """职位响应"""
    id: str
    status: JobStatus
    view_count: int
    application_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    """职位列表项"""
    id: str
    title: str
    department_id: str
    location: str
    category: JobCategory
    recruitment_type: RecruitmentType
    status: JobStatus
    openings: int
    is_urgent: bool
    is_third_party_headhunter_enabled: bool
    interview_flow_config: Optional[str]
    application_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobStatusUpdate(BaseModel):
    """职位状态更新"""
    status: JobStatus
    reason: Optional[str] = Field(None, description="状态变更原因")
