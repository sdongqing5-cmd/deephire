"""Department model - 部门模型"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Department(Base):
    """部门模型 - 支持树形组织架构"""
    __tablename__ = "departments"

    # 基础信息
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, index=True)  # 部门编码

    # 树形结构
    parent_id = Column(String, ForeignKey("departments.id"), index=True)
    level = Column(Integer, default=1)  # 部门层级：1-公司, 2-事业部, 3-部门, 4-小组
    path = Column(String)  # 部门路径，如：/1/2/3，便于查询子部门

    # 负责人
    manager_id = Column(String, ForeignKey("users.id"), index=True)

    # 描述信息
    description = Column(Text)

    # 状态
    is_active = Column(Boolean, default=True, index=True)

    # 统计信息
    employee_count = Column(Integer, default=0)  # 员工数量

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, level={self.level})>"
