"""Database models package"""

from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.job import Job, JobStatus, JobCategory, RecruitmentType, JobLevel
from app.models.department import Department
from app.models.job_status_history import JobStatusHistory
from app.models.interview import Interview, InterviewType, InterviewStatus, InterviewResult
from app.models.application import Application, ApplicationStatus, ApplicationStatusHistory
from app.models.interviewer_screening import InterviewerScreening
from app.models.assessment import Assessment, AssessmentStatus
from app.models.notification import NotificationTemplate, MailboxConfig, NotificationLog
from app.models.headhunter import HeadhunterRecommendation
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "UserRole",
    "Candidate",
    "Job",
    "JobStatus",
    "JobCategory",
    "RecruitmentType",
    "JobLevel",
    "Department",
    "JobStatusHistory",
    "Interview",
    "InterviewType",
    "InterviewStatus",
    "InterviewResult",
    "Application",
    "ApplicationStatus",
    "ApplicationStatusHistory",
    "InterviewerScreening",
    "Assessment",
    "AssessmentStatus",
    "NotificationTemplate",
    "MailboxConfig",
    "NotificationLog",
    "HeadhunterRecommendation",
    "AuditLog",
]
