"""Database initialization and seeding"""

import uuid
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models import User, UserRole, Candidate, Job, Interview, Department
from app.models.job import JobStatus, JobCategory, RecruitmentType
from app.core.security import get_password_hash
from datetime import datetime, timedelta


def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def seed_users(db: Session):
    """Seed demo users"""
    print("Seeding users...")

    users = [
        User(
            id="1",
            email="hr@deephire.com",
            name="HR Manager",
            hashed_password=get_password_hash("password"),
            role=UserRole.HR,
        ),
        User(
            id="2",
            email="recruiter@deephire.com",
            name="Recruiter",
            hashed_password=get_password_hash("password"),
            role=UserRole.RECRUITER,
        ),
        User(
            id="3",
            email="interviewer@deephire.com",
            name="Interviewer",
            hashed_password=get_password_hash("password"),
            role=UserRole.INTERVIEWER,
        ),
        User(
            id="platform-admin-1",
            email="admin@deephire.com",
            name="DeepHire 平台管理员",
            hashed_password=get_password_hash("password"),
            role=UserRole.PLATFORM_ADMIN,
        ),
    ]

    for user in users:
        existing = db.query(User).filter(User.email == user.email).first()
        if not existing:
            db.add(user)

    db.commit()
    print(f"✓ Seeded {len(users)} users")


def seed_candidates(db: Session):
    """Seed demo candidates"""
    print("Seeding candidates...")

    candidates = [
        Candidate(
            id="1",
            name="Alex Zhang",
            email="alex.zhang@email.com",
            phone="+86 138 0000 0001",
            current_company="ByteDance",
            current_title="Senior Frontend Engineer",
            years_of_experience=5,
            location="Beijing",
            status="interviewing",
            tags=["React", "TypeScript", "Next.js", "Node.js"],
            source="referral",
        ),
        Candidate(
            id="2",
            name="Lisa Chen",
            email="lisa.chen@email.com",
            phone="+86 138 0000 0002",
            current_company="Alibaba",
            current_title="Backend Engineer",
            years_of_experience=3,
            location="Hangzhou",
            status="screening",
            tags=["Python", "FastAPI", "PostgreSQL", "Redis"],
            source="linkedin",
        ),
        Candidate(
            id="3",
            name="David Liu",
            email="david.liu@email.com",
            phone="+86 138 0000 0003",
            current_company="Tencent",
            current_title="Full Stack Engineer",
            years_of_experience=4,
            location="Shenzhen",
            status="new",
            tags=["Vue", "Java", "Spring Boot", "MySQL"],
            source="job_board",
        ),
        Candidate(
            id="4",
            name="Sarah Wang",
            email="sarah.wang@email.com",
            phone="+86 138 0000 0004",
            current_company="Huawei",
            current_title="Product Manager",
            years_of_experience=6,
            location="Shenzhen",
            status="contacted",
            tags=["Product Management", "Agile", "B2B SaaS"],
            source="referral",
        ),
        Candidate(
            id="5",
            name="Michael Wu",
            email="michael.wu@email.com",
            phone="+86 138 0000 0005",
            current_company="Meituan",
            current_title="Data Scientist",
            years_of_experience=4,
            location="Beijing",
            status="interested",
            tags=["Python", "Machine Learning", "SQL", "Tableau"],
            source="linkedin",
        ),
    ]

    for candidate in candidates:
        existing = db.query(Candidate).filter(Candidate.email == candidate.email).first()
        if not existing:
            db.add(candidate)

    db.commit()
    print(f"✓ Seeded {len(candidates)} candidates")


def seed_departments(db: Session):
    """Seed demo departments"""
    print("Seeding departments...")

    departments = [
        Department(
            id="dept_tech",
            name="Technology",
            code="TECH",
            level=1,
            path="/dept_tech",
            is_active=True,
        ),
        Department(
            id="dept_product",
            name="Product",
            code="PROD",
            level=1,
            path="/dept_product",
            is_active=True,
        ),
        Department(
            id="dept_sales",
            name="Sales",
            code="SALES",
            level=1,
            path="/dept_sales",
            is_active=True,
        ),
    ]

    for dept in departments:
        existing = db.query(Department).filter(Department.id == dept.id).first()
        if not existing:
            db.add(dept)

    db.commit()
    print(f"✓ Seeded {len(departments)} departments")

    # Link demo users to the organization after departments exist.
    org_fields = {
        "hr@deephire.com": {"department_id": "dept_tech", "title": "HR Manager", "employee_no": "EMP-001"},
        "recruiter@deephire.com": {"department_id": "dept_tech", "title": "Recruiter", "employee_no": "EMP-002"},
        "interviewer@deephire.com": {"department_id": "dept_tech", "title": "Interviewer", "employee_no": "EMP-003"},
    }
    for email, fields in org_fields.items():
        db.query(User).filter(User.email == email).update(fields, synchronize_session=False)
    db.commit()


def seed_jobs(db: Session):
    """Seed demo jobs"""
    print("Seeding jobs...")

    jobs = [
        Job(
            id="1",
            title="Senior Frontend Engineer",
            department_id="dept_tech",
            location="Beijing",
            category=JobCategory.TECHNOLOGY,
            recruitment_type=RecruitmentType.SOCIAL,
            description="We are looking for a senior frontend engineer...",
            requirements="5+ years of experience with React, TypeScript...",
            status=JobStatus.RECRUITING,
            hiring_manager_id="1",
            openings=2,
        ),
        Job(
            id="2",
            title="Backend Engineer",
            department_id="dept_tech",
            location="Shanghai",
            category=JobCategory.TECHNOLOGY,
            recruitment_type=RecruitmentType.SOCIAL,
            description="Join our backend team to build scalable systems...",
            requirements="3+ years of Python/Go experience...",
            status=JobStatus.RECRUITING,
            hiring_manager_id="1",
            openings=3,
        ),
        Job(
            id="3",
            title="Product Manager",
            department_id="dept_product",
            location="Beijing",
            category=JobCategory.PRODUCT,
            recruitment_type=RecruitmentType.SOCIAL,
            description="Lead product strategy and execution...",
            requirements="5+ years of product management experience...",
            status=JobStatus.RECRUITING,
            hiring_manager_id="1",
            openings=1,
        ),
    ]

    for job in jobs:
        existing = db.query(Job).filter(Job.id == job.id).first()
        if not existing:
            db.add(job)

    db.commit()
    print(f"✓ Seeded {len(jobs)} jobs")


def seed_applications(db: Session):
    """Seed demo applications"""
    print("Seeding applications...")
    from app.models.application import Application, ApplicationStatus

    applications = [
        Application(
            id="app_1",
            job_id="1",
            candidate_id="1",
            status=ApplicationStatus.DEPARTMENT_INTERVIEWING,
            recruiter_id="2",
        ),
        Application(
            id="app_2",
            job_id="2",
            candidate_id="2",
            status=ApplicationStatus.HR_INTERVIEW_SCHEDULED,
            recruiter_id="2",
        ),
    ]

    for app in applications:
        existing = db.query(Application).filter(Application.id == app.id).first()
        if not existing:
            db.add(app)

    db.commit()
    print(f"✓ Seeded {len(applications)} applications")


def seed_interviews(db: Session):
    """Seed demo interviews"""
    print("Seeding interviews...")
    from app.models.interview import InterviewType, InterviewStatus, InterviewResult

    now = datetime.now()
    interviews = [
        Interview(
            id="int_1",
            application_id="app_1",
            job_id="1",
            candidate_id="1",
            interviewer_id="3",
            interviewer_name="Interviewer",
            interview_type=InterviewType.DEPARTMENT,
            scheduled_at=now + timedelta(hours=2),
            duration=60,
            status=InterviewStatus.SCHEDULED,
        ),
        Interview(
            id="int_2",
            application_id="app_2",
            job_id="2",
            candidate_id="2",
            interviewer_id="3",
            interviewer_name="Interviewer",
            interview_type=InterviewType.HR_INITIAL,
            scheduled_at=now + timedelta(days=1),
            duration=45,
            status=InterviewStatus.SCHEDULED,
        ),
        Interview(
            id="int_3",
            application_id="app_1",
            job_id="1",
            candidate_id="1",
            interviewer_id="3",
            interviewer_name="Interviewer",
            interview_type=InterviewType.HR_INITIAL,
            scheduled_at=now - timedelta(days=2),
            duration=60,
            status=InterviewStatus.COMPLETED,
            result=InterviewResult.PASS,
            feedback="Strong communication skills, good cultural fit",
        ),
    ]

    for interview in interviews:
        existing = db.query(Interview).filter(Interview.id == interview.id).first()
        if not existing:
            db.add(interview)

    db.commit()
    print(f"✓ Seeded {len(interviews)} interviews")


def main():
    """Main seeding function"""
    print("\n=== Database Initialization ===\n")

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Seed data
        seed_users(db)
        seed_departments(db)
        seed_candidates(db)
        seed_jobs(db)
        seed_applications(db)
        seed_interviews(db)

        print("\n✓ Database initialization complete!\n")

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}\n")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
