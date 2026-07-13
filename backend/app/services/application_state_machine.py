"""Application State Machine - 应聘状态机"""

from app.models.application import ApplicationStatus


class ApplicationStateMachine:
    """应聘状态机 - 定义合法的状态转换"""

    TRANSITIONS = {
        # 简历阶段
        ApplicationStatus.NEW: [
            ApplicationStatus.SENT_TO_INTERVIEWER,
            ApplicationStatus.HR_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.HR_SCREENING: [
            ApplicationStatus.HR_INTERVIEW_SCHEDULED,  # HR筛选通过，安排HR初筛面试
            ApplicationStatus.HR_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        # HR初筛面试阶段
        ApplicationStatus.HR_INTERVIEW_SCHEDULED: [
            ApplicationStatus.HR_INTERVIEWING,
            ApplicationStatus.HR_INTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.HR_INTERVIEWING: [
            ApplicationStatus.HR_INTERVIEW_COMPLETED,
            ApplicationStatus.HR_INTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.HR_INTERVIEW_COMPLETED: [
            ApplicationStatus.SENT_TO_INTERVIEWER,  # HR面试通过，推送给面试官
            ApplicationStatus.HR_INTERVIEW_REJECTED,
        ],

        # 面试官筛选阶段
        ApplicationStatus.SENT_TO_INTERVIEWER: [
            ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION,  # 面试官筛选通过
            ApplicationStatus.INTERVIEWER_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        # 面试意向沟通阶段
        ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION: [
            ApplicationStatus.INTERVIEW_TIME_CONFIRMING,  # 候选人同意面试
            ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
        ],

        # 面试时间确认阶段
        ApplicationStatus.INTERVIEW_TIME_CONFIRMING: [
            ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED,  # 候选人确认时间
            ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
        ],

        # 部门面试阶段
        ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED: [
            ApplicationStatus.DEPARTMENT_INTERVIEWING,
            ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.DEPARTMENT_INTERVIEWING: [
            ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED,
            ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED: [
            ApplicationStatus.ASSESSMENT_INVITED,  # 可选：进入测评
            ApplicationStatus.HR_REINTERVIEW_SCHEDULED,  # 可选：进入HR复试
            ApplicationStatus.FINAL_INTERVIEW_SCHEDULED,  # 直接进入终面
            ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
        ],

        # 测评阶段（可选）
        ApplicationStatus.ASSESSMENT_INVITED: [
            ApplicationStatus.ASSESSMENT_IN_PROGRESS,
            ApplicationStatus.ASSESSMENT_FAILED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.ASSESSMENT_IN_PROGRESS: [
            ApplicationStatus.ASSESSMENT_COMPLETED,
            ApplicationStatus.ASSESSMENT_FAILED,
        ],

        ApplicationStatus.ASSESSMENT_COMPLETED: [
            ApplicationStatus.HR_REINTERVIEW_SCHEDULED,  # 可选：进入HR复试
            ApplicationStatus.FINAL_INTERVIEW_SCHEDULED,  # 直接进入终面
        ],

        # HR复试阶段（可选）
        ApplicationStatus.HR_REINTERVIEW_SCHEDULED: [
            ApplicationStatus.HR_REINTERVIEWING,
            ApplicationStatus.HR_REINTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.HR_REINTERVIEWING: [
            ApplicationStatus.HR_REINTERVIEW_COMPLETED,
            ApplicationStatus.HR_REINTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.HR_REINTERVIEW_COMPLETED: [
            ApplicationStatus.FINAL_INTERVIEW_SCHEDULED,
            ApplicationStatus.HR_REINTERVIEW_REJECTED,
        ],

        # 终面阶段
        ApplicationStatus.FINAL_INTERVIEW_SCHEDULED: [
            ApplicationStatus.FINAL_INTERVIEWING,
            ApplicationStatus.FINAL_INTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.FINAL_INTERVIEWING: [
            ApplicationStatus.FINAL_INTERVIEW_COMPLETED,
            ApplicationStatus.FINAL_INTERVIEW_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.FINAL_INTERVIEW_COMPLETED: [
            ApplicationStatus.SALARY_NEGOTIATION,
            ApplicationStatus.FINAL_INTERVIEW_REJECTED,
        ],

        # Offer阶段
        ApplicationStatus.SALARY_NEGOTIATION: [
            ApplicationStatus.VERBAL_OFFER_ACCEPTED,
            ApplicationStatus.SALARY_REJECTED,
            ApplicationStatus.CANDIDATE_WITHDRAWN,
        ],

        ApplicationStatus.VERBAL_OFFER_ACCEPTED: [
            ApplicationStatus.OFFER_APPROVAL,
        ],

        ApplicationStatus.OFFER_APPROVAL: [
            ApplicationStatus.OFFER_PENDING,
            ApplicationStatus.OFFER_APPROVAL_REJECTED,
        ],

        ApplicationStatus.OFFER_PENDING: [
            ApplicationStatus.OFFER_SENT,
        ],

        ApplicationStatus.OFFER_SENT: [
            ApplicationStatus.OFFER_ACCEPTED,
            ApplicationStatus.OFFER_REJECTED,
        ],

        ApplicationStatus.OFFER_ACCEPTED: [
            ApplicationStatus.PENDING_ONBOARD,
        ],

        # 入职阶段
        ApplicationStatus.PENDING_ONBOARD: [
            ApplicationStatus.ONBOARDED,
            ApplicationStatus.ONBOARD_CANCELLED,
        ],
    }

    @classmethod
    def can_transition(cls, from_status: ApplicationStatus, to_status: ApplicationStatus) -> bool:
        """检查状态转换是否合法"""
        allowed_transitions = cls.TRANSITIONS.get(from_status, [])
        return to_status in allowed_transitions

    @classmethod
    def get_available_transitions(cls, current_status: ApplicationStatus) -> list[ApplicationStatus]:
        """获取当前状态可以转换到的所有状态"""
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def get_status_label(cls, status: ApplicationStatus) -> str:
        """获取状态的中文标签"""
        labels = {
            ApplicationStatus.NEW: "HR待查看",
            ApplicationStatus.HR_SCREENING: "HR筛选中",
            ApplicationStatus.HR_REJECTED: "HR筛选未通过",
            ApplicationStatus.HR_INTERVIEW_SCHEDULED: "HR初筛面试已安排",
            ApplicationStatus.HR_INTERVIEWING: "HR初筛面试进行中",
            ApplicationStatus.HR_INTERVIEW_COMPLETED: "HR初筛面试已完成",
            ApplicationStatus.HR_INTERVIEW_REJECTED: "HR初筛面试淘汰",
            ApplicationStatus.SENT_TO_INTERVIEWER: "HR筛选通过，已推送用人部门",
            ApplicationStatus.INTERVIEWER_REJECTED: "面试官筛选未通过",
            ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION: "面试意向沟通中",
            ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW: "候选人放弃面试",
            ApplicationStatus.INTERVIEW_TIME_CONFIRMING: "候选人同意面试，约定时间中",
            ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED: "已约定面试时间",
            ApplicationStatus.DEPARTMENT_INTERVIEWING: "面试中",
            ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED: "面试通过",
            ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED: "面试失败",
            ApplicationStatus.ASSESSMENT_INVITED: "测评邀请已发送",
            ApplicationStatus.ASSESSMENT_IN_PROGRESS: "测评进行中",
            ApplicationStatus.ASSESSMENT_COMPLETED: "测评已完成",
            ApplicationStatus.ASSESSMENT_FAILED: "测评未通过",
            ApplicationStatus.HR_REINTERVIEW_SCHEDULED: "HR复试已安排",
            ApplicationStatus.HR_REINTERVIEWING: "HR复试进行中",
            ApplicationStatus.HR_REINTERVIEW_COMPLETED: "HR复试已完成",
            ApplicationStatus.HR_REINTERVIEW_REJECTED: "HR复试淘汰",
            ApplicationStatus.FINAL_INTERVIEW_SCHEDULED: "终面已安排",
            ApplicationStatus.FINAL_INTERVIEWING: "终面进行中",
            ApplicationStatus.FINAL_INTERVIEW_COMPLETED: "终面已完成",
            ApplicationStatus.FINAL_INTERVIEW_REJECTED: "终面淘汰",
            ApplicationStatus.SALARY_NEGOTIATION: "谈薪中",
            ApplicationStatus.SALARY_REJECTED: "谈薪失败",
            ApplicationStatus.VERBAL_OFFER_ACCEPTED: "接受口头Offer",
            ApplicationStatus.OFFER_APPROVAL: "Offer审批中",
            ApplicationStatus.OFFER_APPROVAL_REJECTED: "Offer审批拒绝",
            ApplicationStatus.OFFER_PENDING: "待发Offer",
            ApplicationStatus.OFFER_SENT: "已发Offer",
            ApplicationStatus.OFFER_REJECTED: "已拒绝Offer",
            ApplicationStatus.OFFER_ACCEPTED: "已接受Offer",
            ApplicationStatus.PENDING_ONBOARD: "待入职",
            ApplicationStatus.ONBOARD_CANCELLED: "取消入职",
            ApplicationStatus.ONBOARDED: "已入职",
            ApplicationStatus.CANDIDATE_WITHDRAWN: "候选人主动退出",
        }
        return labels.get(status, status.value)
