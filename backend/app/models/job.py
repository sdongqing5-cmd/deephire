"""Job model - 职位模型（完整版）"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class JobStatus(str, enum.Enum):
    """职位状态"""
    DRAFT = "draft"              # 草稿
    RECRUITING = "recruiting"    # 招聘中
    PAUSED = "paused"           # 已暂停
    CANCELLED = "cancelled"     # 已取消
    CLOSED = "closed"           # 已结束


class JobCategory(str, enum.Enum):
    """岗位类别"""
    TECHNOLOGY = "technology"    # 技术类
    PRODUCT = "product"         # 产品类
    SALES = "sales"             # 销售类
    MARKETING = "marketing"     # 市场类
    OPERATIONS = "operations"   # 运营类
    ADMIN = "admin"             # 行政类
    HR = "hr"                   # 人事类
    FINANCE = "finance"         # 财务类
    DESIGN = "design"           # 设计类
    OTHER = "other"             # 其他


class RecruitmentType(str, enum.Enum):
    """招聘类别"""
    SOCIAL = "social"           # 社会招聘
    CAMPUS = "campus"           # 校园招聘
    INTERNSHIP = "internship"   # 实习生招聘


class JobLevel(str, enum.Enum):
    """职位级别"""
    JUNIOR = "junior"                    # 初级
    INTERMEDIATE = "intermediate"        # 中级
    SENIOR = "senior"                   # 高级
    EXPERT = "expert"                   # 专家
    MANAGER = "manager"                 # 经理
    DIRECTOR = "director"               # 总监
    VP = "vp"                          # VP
    C_LEVEL = "c_level"                # C-Level


class Job(Base):
    """职位模型"""
    __tablename__ = "jobs"

    # 基础信息
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    department_id = Column(String, ForeignKey("departments.id"), index=True)
    location = Column(String, nullable=False)

    # 职位分类
    category = Column(SQLEnum(JobCategory), nullable=False, index=True)
    recruitment_type = Column(SQLEnum(RecruitmentType), nullable=False, default=RecruitmentType.SOCIAL, index=True)
    level = Column(SQLEnum(JobLevel))

    # 职位内容
    description = Column(Text)  # JD内容
    requirements = Column(Text)  # 任职要求（JSON格式存储列表）
    responsibilities = Column(Text)  # 工作职责（JSON格式）
    notes = Column(Text)  # 备注

    # 薪资范围
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String, default="CNY")

    # 招聘信息
    openings = Column(Integer, default=1)  # 招聘人数
    is_urgent = Column(Boolean, default=False, index=True)  # 是否加急
    valid_until = Column(DateTime(timezone=True))  # 有效期

    # 负责人
    hiring_manager_id = Column(String, ForeignKey("users.id"), index=True)  # 招聘负责人（HR）
    department_manager_id = Column(String, ForeignKey("users.id"))  # 部门负责人
    recruiter_id = Column(String, ForeignKey("users.id"))  # 招聘专员

    # 状态
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.DRAFT, index=True)

    # 统计信息
    view_count = Column(Integer, default=0)  # 浏览次数
    application_count = Column(Integer, default=0)  # 申请人数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))  # 发布时间
    closed_at = Column(DateTime(timezone=True))  # 关闭时间

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, status={self.status})>"
