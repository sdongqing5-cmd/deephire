# DeepHire 招聘系统 - V2核心设计文档

## 📋 文档说明

本文档是V2版本的核心设计，包含：
- 完整的状态机设计
- 核心数据模型
- 状态流转逻辑

**基于V0的修正**：
1. ✅ 新增HR初筛面试环节
2. ✅ 新增面试意向沟通环节
3. ✅ 新增面试时间确认环节
4. ✅ 新增面试官简历筛选记录
5. ✅ 新增测评环节
6. ✅ 新增HR复试环节
7. ✅ 所有面试环节区分"已安排"、"进行中"、"已完成"状态

---

## 一、完整状态机设计

### 1.1 ApplicationStatus（应聘状态枚举）

```python
class ApplicationStatus(str, enum.Enum):
    """应聘状态 - 完整生命周期"""
    
    # ==================== 简历阶段 ====================
    NEW = "new"                                    # 新简历
    HR_SCREENING = "hr_screening"                  # HR筛选中（含电话沟通确认意向）
    HR_REJECTED = "hr_rejected"                    # HR淘汰
    
    # ==================== HR初筛面试阶段 ====================
    HR_INTERVIEW_SCHEDULED = "hr_interview_scheduled"      # HR初筛面试已安排
    HR_INTERVIEWING = "hr_interviewing"                    # HR初筛面试进行中
    HR_INTERVIEW_COMPLETED = "hr_interview_completed"      # HR初筛面试已完成
    HR_INTERVIEW_REJECTED = "hr_interview_rejected"        # HR初筛面试淘汰
    
    # ==================== 面试官筛选阶段 ====================
    SENT_TO_INTERVIEWER = "sent_to_interviewer"           # 推送给面试官（面试官筛选简历）
    INTERVIEWER_REJECTED = "interviewer_rejected"          # 面试官淘汰
    
    # ==================== 面试意向沟通阶段 ====================
    INTERVIEW_INTENTION_COMMUNICATION = "interview_intention_communication"  # 面试意向沟通中
    CANDIDATE_DECLINED_INTERVIEW = "candidate_declined_interview"            # 候选人放弃面试
    
    # ==================== 面试时间确认阶段 ====================
    INTERVIEW_TIME_CONFIRMING = "interview_time_confirming"  # 等待候选人确认面试时间
    
    # ==================== 部门面试阶段 ====================
    DEPARTMENT_INTERVIEW_SCHEDULED = "department_interview_scheduled"  # 部门面试已安排
    DEPARTMENT_INTERVIEWING = "department_interviewing"                # 部门面试进行中
    DEPARTMENT_INTERVIEW_COMPLETED = "department_interview_completed"  # 部门面试已完成
    DEPARTMENT_INTERVIEW_REJECTED = "department_interview_rejected"    # 部门面试淘汰
    
    # ==================== 测评阶段（可选）====================
    ASSESSMENT_INVITED = "assessment_invited"              # 测评邀请已发送
    ASSESSMENT_IN_PROGRESS = "assessment_in_progress"      # 测评进行中
    ASSESSMENT_COMPLETED = "assessment_completed"          # 测评已完成
    ASSESSMENT_FAILED = "assessment_failed"                # 测评未通过
    
    # ==================== HR复试阶段（可选）====================
    HR_REINTERVIEW_SCHEDULED = "hr_reinterview_scheduled"  # HR复试已安排
    HR_REINTERVIEWING = "hr_reinterviewing"                # HR复试进行中
    HR_REINTERVIEW_COMPLETED = "hr_reinterview_completed"  # HR复试已完成
    HR_REINTERVIEW_REJECTED = "hr_reinterview_rejected"    # HR复试淘汰
    
    # ==================== 终面阶段 ====================
    FINAL_INTERVIEW_SCHEDULED = "final_interview_scheduled"  # 终面已安排
    FINAL_INTERVIEWING = "final_interviewing"                # 终面进行中
    FINAL_INTERVIEW_COMPLETED = "final_interview_completed"  # 终面已完成
    FINAL_INTERVIEW_REJECTED = "final_interview_rejected"    # 终面淘汰
    
    # ==================== Offer阶段 ====================
    SALARY_NEGOTIATION = "salary_negotiation"              # 谈薪中
    SALARY_REJECTED = "salary_rejected"                    # 谈薪失败
    VERBAL_OFFER_ACCEPTED = "verbal_offer_accepted"        # 接受口头Offer
    OFFER_APPROVAL = "offer_approval"                      # Offer审批中
    OFFER_APPROVAL_REJECTED = "offer_approval_rejected"    # Offer审批拒绝
    OFFER_PENDING = "offer_pending"                        # 待发Offer
    OFFER_SENT = "offer_sent"                              # 已发Offer
    OFFER_REJECTED = "offer_rejected"                      # 已拒绝Offer
    OFFER_ACCEPTED = "offer_accepted"                      # 已接受Offer
    
    # ==================== 入职阶段 ====================
    PENDING_ONBOARD = "pending_onboard"                    # 待入职
    ONBOARD_CANCELLED = "onboard_cancelled"                # 取消入职
    ONBOARDED = "onboarded"                                # 已入职
    
    # ==================== 其他 ====================
    CANDIDATE_WITHDRAWN = "candidate_withdrawn"            # 候选人主动退出
```

### 1.2 正确的完整流程（基于功能列表第109行）

```
1. 简历投递 → NEW
2. HR筛选（含电话沟通确认意向）→ HR_SCREENING
3. HR初筛面试 → HR_INTERVIEW_SCHEDULED → HR_INTERVIEWING → HR_INTERVIEW_COMPLETED
4. 推送面试官筛选简历 → SENT_TO_INTERVIEWER
5. 面试意向沟通（智能外呼/人工）→ INTERVIEW_INTENTION_COMMUNICATION
6. 等待确认面试时间（邮件确认）→ INTERVIEW_TIME_CONFIRMING
7. 部门面试 → DEPARTMENT_INTERVIEW_SCHEDULED → DEPARTMENT_INTERVIEWING → DEPARTMENT_INTERVIEW_COMPLETED
8. 测评（可选）→ ASSESSMENT_INVITED → ASSESSMENT_IN_PROGRESS → ASSESSMENT_COMPLETED
9. HR复试（可选）→ HR_REINTERVIEW_SCHEDULED → HR_REINTERVIEWING → HR_REINTERVIEW_COMPLETED
10. 终面 → FINAL_INTERVIEW_SCHEDULED → FINAL_INTERVIEWING → FINAL_INTERVIEW_COMPLETED
11. 谈薪 → SALARY_NEGOTIATION → VERBAL_OFFER_ACCEPTED
12. Offer审批 → OFFER_APPROVAL → OFFER_PENDING
13. Offer编辑和发送 → OFFER_SENT
14. 候选人接受 → OFFER_ACCEPTED
15. 入职 → PENDING_ONBOARD → ONBOARDED
```

### 1.3 状态流转规则

```python
class ApplicationStateMachine:
    """应聘状态机 - 定义合法的状态转换"""
    
    TRANSITIONS = {
        # 简历阶段
        ApplicationStatus.NEW: [
            ApplicationStatus.HR_SCREENING,
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
```

---

## 二、核心数据模型

### 2.1 Application（应聘记录）- 完整版

```python
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime

class Application(Base):
    """应聘记录 - 核心表"""
    __tablename__ = "applications"
    
    # ==================== 基本信息 ====================
    id = Column(String, primary_key=True, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # ==================== 状态 ====================
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW, index=True)
    
    # ==================== 简历信息 ====================
    resume_url = Column(String)  # 简历文件URL
    resume_parsed_data = Column(Text)  # 解析后的简历数据（JSON）
    
    # ==================== 来源 ====================
    source = Column(String)  # 简历来源：主动投递、内推、猎头等
    
    # ==================== 负责人 ====================
    hr_id = Column(String, ForeignKey("users.id"), index=True)  # 负责HR
    recruiter_id = Column(String, ForeignKey("users.id"))  # 招聘专员
    
    # ==================== 锁定信息 ====================
    is_locked = Column(Boolean, default=False, index=True)  # 是否锁定
    locked_by = Column(String, ForeignKey("users.id"))  # 锁定人
    locked_at = Column(DateTime(timezone=True))  # 锁定时间
    
    # ==================== 应聘次数统计 ====================
    application_count = Column(Integer, default=1)  # 该候选人应聘该职位的次数
    
    # ==================== 🆕 面试意向沟通 ====================
    intention_contact_method = Column(String)  # 联系方式：ai_call（智能外呼）, manual（人工联系）
    intention_contact_result = Column(String)  # 沟通结果：agreed（同意）, declined（拒绝）, no_answer（未接听）
    intention_contact_notes = Column(Text)  # 沟通备注
    intention_contacted_at = Column(DateTime(timezone=True))  # 沟通时间
    intention_contacted_by = Column(String, ForeignKey("users.id"))  # 沟通人
    
    # ==================== 🆕 面试时间确认 ====================
    interview_notification_sent_at = Column(DateTime(timezone=True))  # 面试通知发送时间
    interview_confirmed_at = Column(DateTime(timezone=True))  # 候选人确认时间
    interview_confirmation_token = Column(String)  # 确认token（用于邮件链接）
    
    # ==================== 面试流程配置 ====================
    interview_flow_config = Column(Text)  # 面试流程配置（JSON格式）
    # 示例：{"has_assessment": true, "has_hr_reinterview": false}
    
    # ==================== 时间戳 ====================
    applied_at = Column(DateTime(timezone=True), server_default=func.now())  # 投递时间
    hr_viewed_at = Column(DateTime(timezone=True))  # HR查看时间
    last_status_change_at = Column(DateTime(timezone=True))  # 最后状态变更时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 2.2 InterviewerScreening（面试官简历筛选）- 🆕 新增表

```python
class InterviewerScreening(Base):
    """面试官简历筛选记录"""
    __tablename__ = "interviewer_screenings"
    
    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    interviewer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    interviewer_name = Column(String)
    
    # 筛选结果
    result = Column(String, nullable=False)  # pass（通过）, reject（淘汰）
    comments = Column(Text)  # 筛选意见（简单填写）
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 2.3 Interview（面试记录）- 完整版

```python
class InterviewType(str, enum.Enum):
    """面试类型"""
    HR_INITIAL = "hr_initial"          # HR初筛面试
    DEPARTMENT = "department"          # 部门面试
    HR_REINTERVIEW = "hr_reinterview"  # HR复试
    FINAL = "final"                    # 终面

class InterviewStatus(str, enum.Enum):
    """面试状态"""
    SCHEDULED = "scheduled"      # 已安排
    CONFIRMED = "confirmed"      # 候选人已确认
    DECLINED = "declined"        # 候选人拒绝
    CANCELLED = "cancelled"      # 已取消
    RESCHEDULED = "rescheduled"  # 已改期
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    NO_SHOW = "no_show"         # 候选人未到

class InterviewResult(str, enum.Enum):
    """面试结果"""
    PENDING = "pending"          # 待评价
    PASS = "pass"               # 通过
    FAIL = "fail"               # 未通过
    HOLD = "hold"               # 待定

class Interview(Base):
    """面试记录"""
    __tablename__ = "interviews"
    
    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), index=True)
    
    # 🆕 面试类型
    interview_type = Column(SQLEnum(InterviewType), nullable=False, index=True)
    
    # 面试信息
    title = Column(String)  # 面试主题
    
    # 面试官
    interviewer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    interviewer_name = Column(String)
    
    # 评价表
    scorecard_template_id = Column(String, ForeignKey("scorecard_templates.id"))
    
    # 时间地点
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    duration = Column(Integer, default=60)  # 面试时长（分钟）
    location = Column(String)  # 面试地点
    meeting_link = Column(String)  # 线上面试链接
    
    # 状态和结果
    status = Column(SQLEnum(InterviewStatus), nullable=False, default=InterviewStatus.SCHEDULED)
    result = Column(SQLEnum(InterviewResult), default=InterviewResult.PENDING)
    
    # 评价
    feedback = Column(Text)  # 面试反馈
    score = Column(Integer)  # 评分
    evaluation_data = Column(Text)  # 评价表数据（JSON）
    
    # 通知
    notification_sent_to_candidate = Column(Boolean, default=False)
    notification_sent_to_interviewer = Column(Boolean, default=False)
    candidate_confirmed_at = Column(DateTime(timezone=True))
    
    # 时间戳
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 2.4 Assessment（测评记录）- 🆕 新增表

```python
class AssessmentStatus(str, enum.Enum):
    """测评状态"""
    INVITED = "invited"          # 已邀请
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 未通过
    EXPIRED = "expired"          # 已过期

class Assessment(Base):
    """测评记录"""
    __tablename__ = "assessments"
    
    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), index=True)
    
    # 测评信息
    assessment_type = Column(String)  # 测评类型：商推、SHL等
    assessment_url = Column(String)  # 测评链接
    
    # 状态
    status = Column(SQLEnum(AssessmentStatus), nullable=False, default=AssessmentStatus.INVITED)
    
    # 结果
    score = Column(Float)  # 得分
    result_data = Column(Text)  # 测评结果数据（JSON）
    report_url = Column(String)  # 测评报告URL
    
    # 有效期
    valid_until = Column(DateTime(timezone=True))
    
    # 时间戳
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 2.5 ApplicationStatusHistory（应聘状态历史）

```python
class ApplicationStatusHistory(Base):
    """应聘状态历史"""
    __tablename__ = "application_status_history"
    
    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    
    from_status = Column(SQLEnum(ApplicationStatus))
    to_status = Column(SQLEnum(ApplicationStatus), nullable=False)
    
    reason = Column(Text)  # 状态变更原因
    operator_id = Column(String, ForeignKey("users.id"))
    operator_name = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## 三、关键业务逻辑

### 3.1 状态流转Service

```python
class ApplicationService:
    """应聘记录服务"""
    
    @staticmethod
    async def transition_status(
        application_id: str,
        to_status: ApplicationStatus,
        operator_id: str,
        reason: str = None
    ) -> Application:
        """状态流转"""
        application = await Application.get(application_id)
        
        # 检查状态转换是否合法
        if not ApplicationStateMachine.can_transition(application.status, to_status):
            raise ValueError(
                f"不能从 {application.status} 转换到 {to_status}"
            )
        
        # 记录历史
        history = ApplicationStatusHistory(
            application_id=application.id,
            from_status=application.status,
            to_status=to_status,
            operator_id=operator_id,
            reason=reason
        )
        await history.save()
        
        # 更新状态
        old_status = application.status
        application.status = to_status
        application.last_status_change_at = datetime.now()
        await application.save()
        
        # 触发后续操作
        await ApplicationService._handle_status_change(application, old_status, to_status)
        
        return application
    
    @staticmethod
    async def _handle_status_change(
        application: Application,
        old_status: ApplicationStatus,
        new_status: ApplicationStatus
    ):
        """处理状态变更后的操作"""
        
        # HR初筛面试完成 → 推送给面试官
        if new_status == ApplicationStatus.SENT_TO_INTERVIEWER:
            await NotificationService.notify_interviewer_new_resume(application)
        
        # 面试意向沟通完成 → 发送面试确认邮件
        elif new_status == ApplicationStatus.INTERVIEW_TIME_CONFIRMING:
            await EmailService.send_interview_confirmation(application)
        
        # 候选人确认面试时间 → 创建面试记录
        elif new_status == ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED:
            await InterviewService.create_department_interview(application)
        
        # ... 其他状态变更处理
```

---

## 四、V0到V2的关键修正总结

### 修正1: HR初筛面试环节
**V0问题**: HR_SCREENING后直接推送给面试官
**V2修正**: 增加HR初筛面试环节
```
HR_SCREENING → HR_INTERVIEW_SCHEDULED → HR_INTERVIEWING → HR_INTERVIEW_COMPLETED → SENT_TO_INTERVIEWER
```

### 修正2: 面试官筛选简历
**V0问题**: 没有记录面试官筛选结果
**V2修正**: 新增InterviewerScreening表，记录筛选意见

### 修正3: 面试意向沟通
**V0问题**: 只有一个INTERVIEW_INTENTION状态
**V2修正**: 增加详细字段记录沟通方式和结果
- intention_contact_method: ai_call / manual
- intention_contact_result: agreed / declined / no_answer

### 修正4: 面试时间确认
**V0问题**: 缺少等待确认环节
**V2修正**: 增加INTERVIEW_TIME_CONFIRMING状态

### 修正5: 面试环节细化
**V0问题**: 只有INTERVIEWING一个状态
**V2修正**: 每个面试环节都有"已安排"、"进行中"、"已完成"三个状态

### 修正6: 测评环节
**V0问题**: 没有测评相关状态
**V2修正**: 增加测评状态和Assessment表

### 修正7: HR复试环节
**V0问题**: 没有HR复试状态
**V2修正**: 增加HR复试相关状态

### 修正8: 流程顺序
**V0问题**: HR初筛面试位置错误
**V2修正**: HR初筛面试在推送面试官之前

---

**文档版本**: v2.0
**创建时间**: 2026-05-30
**状态**: 核心设计完成
