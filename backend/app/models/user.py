"""User model"""

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    HR = "hr"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    PLATFORM_ADMIN = "platform_admin"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)

    # Organization structure
    department_id = Column(String, ForeignKey("departments.id"), index=True)
    title = Column(String)
    manager_id = Column(String, ForeignKey("users.id"), index=True)
    employee_no = Column(String, unique=True, index=True)
    status = Column(String, nullable=False, default="active", index=True)

    department = relationship(
        "Department",
        foreign_keys=[department_id],
        back_populates="employees",
    )
    manager = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[manager_id],
        back_populates="direct_reports",
    )
    direct_reports = relationship(
        "User",
        foreign_keys=[manager_id],
        back_populates="manager",
    )
    managed_department = relationship(
        "Department",
        foreign_keys="Department.manager_id",
        back_populates="manager",
        uselist=False,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
