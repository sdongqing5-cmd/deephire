"""API v1 router aggregation"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    candidates,
    jobs,
    interviews,
    interview_management,
    resumes,
    search,
    scorecards,
    outbound_calls,
    applications,
    application_actions,
    hr_interviews,
    interviewer_screenings,
    interview_intentions,
    interview_confirmations,
    department_interviews,
    assessments,
    final_interviews,
    offers,
    notifications,
    headhunters,
    audit_logs,
)

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(interview_management.router, prefix="/interview-management", tags=["interview-management"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(scorecards.router, prefix="/scorecards", tags=["scorecards"])
api_router.include_router(outbound_calls.router, prefix="/outbound-calls", tags=["outbound-calls"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(application_actions.router, prefix="/application-actions", tags=["application-actions"])
api_router.include_router(hr_interviews.router, prefix="/hr-interviews", tags=["hr-interviews"])
api_router.include_router(interviewer_screenings.router, prefix="/interviewer-screenings", tags=["interviewer-screenings"])
api_router.include_router(interview_intentions.router, prefix="/interview-intentions", tags=["interview-intentions"])
api_router.include_router(interview_confirmations.router, prefix="/interview-confirmations", tags=["interview-confirmations"])
api_router.include_router(department_interviews.router, prefix="/department-interviews", tags=["department-interviews"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(final_interviews.router, prefix="/final-interviews", tags=["final-interviews"])
api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(headhunters.router, prefix="/headhunters", tags=["headhunters"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
