
  ---
  DeepHire 招聘系统 - 修正版设计文档

  📋 修正说明
  
  根据用户确认：
  1. ✅ HR面试可以在第一轮或用人部门面试后
  2. ✅ 测评环节可选
  3. ✅ 简历锁定后其他HR可见可查看，但不能修改状态
  4. ✅ 需要管理员角色
  5. ❓ "历史审批人"逻辑待确认
  6. ✅ 终面需要在系统中记录

  ---
  一、修正后的状态机设计

  1.1 完整状态流转图

  [简历投递]
      ↓
  ┌─────────────────┐
  │  新简历         │ (new)
  │  HR待查看       │
  └─────────────────┘
      ↓ HR查看
  ┌─────────────────┐
  │  HR筛选中       │ (hr_screening)
  └─────────────────┘
      ↓ HR筛选通过 / ↓ HR筛选未通过
      ↓              ↓
      ↓         ┌─────────────────┐
      ↓         │  HR淘汰         │ (hr_rejected)
      ↓         └─────────────────┘
      ↓
      ↓ ┌─────────────────────────────────┐
      ↓ │  分支选择：                     │
      ↓ │  A. 先HR面试                    │
      ↓ │  B. 先推送用人部门              │
      ↓ └─────────────────────────────────┘
      ↓
      ├─→ [路径A: 先HR面试]
      │   ┌─────────────────┐
      │   │ HR面试已安排    │ (hr_interview_scheduled)
      │   └─────────────────┘
      │       ↓
      │   ┌─────────────────┐
      │   │ HR面试中        │ (hr_interviewing)
      │   └─────────────────┘
      │       ↓ 通过 / ↓ 未通过
      │       ↓        ↓
      │       ↓   ┌─────────────────┐
      │       ↓   │ HR面试淘汰      │ (hr_interview_rejected)
      │       ↓   └─────────────────┘
      │       ↓
      │       └─→ 推送用人部门
      │
      └─→ [路径B: 直接推送用人部门]
          ↓
  ┌─────────────────┐
  │  推送面试官     │ (sent_to_interviewer)
  │  面试官待筛选   │
  └─────────────────┘
      ↓ 面试官筛选通过 / ↓ 面试官筛选未通过
      ↓                  ↓
      ↓             ┌─────────────────┐
      ↓             │  面试官淘汰     │ (interviewer_rejected)
      ↓             └─────────────────┘
      ↓
  ┌─────────────────┐
  │  部门面试已安排 │ (department_interview_scheduled)
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  部门面试中     │ (department_interviewing)
  └─────────────────┘
      ↓ 通过 / ↓ 未通过
      ↓        ↓
      ↓   ┌─────────────────┐
      ↓   │ 部门面试淘汰    │ (department_interview_rejected)
      ↓   └─────────────────┘
      ↓
      ↓ ┌─────────────────────────────────┐
      ↓ │  可选：是否需要HR复试？         │
      ↓ └─────────────────────────────────┘
      ↓
      ├─→ [如果需要HR复试]
      │   ┌─────────────────┐
      │   │ HR复试已安排    │ (hr_reinterview_scheduled)
      │   └─────────────────┘
      │       ↓
      │   ┌─────────────────┐
      │   │ HR复试中        │ (hr_reinterviewing)
      │   └─────────────────┘
      │       ↓ 通过 / ↓ 未通过
      │       ↓        ↓
      │       ↓   ┌─────────────────┐
      │       ↓   │ HR复试淘汰      │ (hr_reinterview_rejected)
      │       ↓   └─────────────────┘
      │       ↓
      │       └─→ 继续
      │
      └─→ [跳过HR复试]
          ↓
      ↓ ┌─────────────────────────────────┐
      ↓ │  可选：是否需要测评？           │
      ↓ └─────────────────────────────────┘
      ↓
      ├─→ [如果需要测评]
      │   ┌─────────────────┐
      │   │ 测评邀请已发送  │ (assessment_invited)
      │   └─────────────────┘
      │       ↓
      │   ┌─────────────────┐
      │   │ 测评进行中      │ (assessment_in_progress)
      │   └─────────────────┘
      │       ↓ 通过 / ↓ 未通过
      │       ↓        ↓
      │       ↓   ┌─────────────────┐
      │       ↓   │ 测评未通过      │ (assessment_failed)
      │       ↓   └─────────────────┘
      │       ↓
      │   ┌─────────────────┐
      │   │ 测评已完成      │ (assessment_completed)
      │   └─────────────────┘
      │       ↓
      │       └─→ 继续
      │
      └─→ [跳过测评]
          ↓
  ┌─────────────────┐
  │  终面已安排     │ (final_interview_scheduled)
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  终面中         │ (final_interviewing)
  └─────────────────┘
      ↓ 通过 / ↓ 未通过
      ↓        ↓
      ↓   ┌─────────────────┐
      ↓   │ 终面淘汰        │ (final_interview_rejected)
      ↓   └─────────────────┘
      ↓
  ┌─────────────────┐
  │  终面通过       │ (final_interview_passed)
  │  待谈薪         │
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  谈薪中         │ (salary_negotiation)
  └─────────────────┘
      ↓ 谈薪成功 / ↓ 谈薪失败
      ↓            ↓
      ↓       ┌─────────────────┐
      ↓       │  谈薪失败       │ (salary_rejected)
      ↓       └─────────────────┘
      ↓
  ┌─────────────────┐
  │  接受口头Offer  │ (verbal_offer_accepted)
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  Offer审批中    │ (offer_approval)
  └─────────────────┘
      ↓ 审批通过 / ↓ 审批拒绝
      ↓            ↓
      ↓       ┌─────────────────┐
      ↓       │  Offer审批拒绝  │ (offer_approval_rejected)
      ↓       └─────────────────┘
      ↓
  ┌─────────────────┐
  │  待发Offer      │ (offer_pending)
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  已发Offer      │ (offer_sent)
  └─────────────────┘
      ↓ 候选人接受 / ↓ 候选人拒绝
      ↓              ↓
      ↓         ┌─────────────────┐
      ↓         │  已拒绝Offer    │ (offer_rejected)
      ↓         └─────────────────┘
      ↓
  ┌─────────────────┐
  │  已接受Offer    │ (offer_accepted)
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  待入职         │ (pending_onboard)
  └─────────────────┘
      ↓ 入职 / ↓ 取消入职
      ↓        ↓
      ↓   ┌─────────────────┐
      ↓   │  取消入职       │ (onboard_cancelled)
      ↓   └─────────────────┘
      ↓
  ┌─────────────────┐
  │  已入职         │ (onboarded)
  └─────────────────┘

  ---
  二、修正后的数据模型

  2.1 ApplicationStatus（应聘状态）- 完整版

  class ApplicationStatus(str, enum.Enum):
      """应聘状态 - 完整生命周期"""
      # 简历阶段
      NEW = "new"                                    # 新简历
      HR_SCREENING = "hr_screening"                  # HR筛选中
      HR_REJECTED = "hr_rejected"                    # HR淘汰
  
      # HR面试阶段（可选，可在第一轮或最后）
      HR_INTERVIEW_SCHEDULED = "hr_interview_scheduled"      # HR面试已安排
      HR_INTERVIEWING = "hr_interviewing"                    # HR面试中
      HR_INTERVIEW_REJECTED = "hr_interview_rejected"        # HR面试淘汰

      # 面试官筛选阶段
      SENT_TO_INTERVIEWER = "sent_to_interviewer"   # 推送给面试官
      INTERVIEWER_REJECTED = "interviewer_rejected"  # 面试官淘汰

      # 部门面试阶段
      DEPARTMENT_INTERVIEW_SCHEDULED = "department_interview_scheduled"  # 部门面试已安排
      DEPARTMENT_INTERVIEWING = "department_interviewing"                # 部门面试中
      DEPARTMENT_INTERVIEW_REJECTED = "department_interview_rejected"    # 部门面试淘汰

      # HR复试阶段（可选）
      HR_REINTERVIEW_SCHEDULED = "hr_reinterview_scheduled"  # HR复试已安排
      HR_REINTERVIEWING = "hr_reinterviewing"                # HR复试中
      HR_REINTERVIEW_REJECTED = "hr_reinterview_rejected"    # HR复试淘汰

      # 测评阶段（可选）
      ASSESSMENT_INVITED = "assessment_invited"              # 测评邀请已发送
      ASSESSMENT_IN_PROGRESS = "assessment_in_progress"      # 测评进行中
      ASSESSMENT_COMPLETED = "assessment_completed"          # 测评已完成
      ASSESSMENT_FAILED = "assessment_failed"                # 测评未通过
  
      # 终面阶段
      FINAL_INTERVIEW_SCHEDULED = "final_interview_scheduled"  # 终面已安排
      FINAL_INTERVIEWING = "final_interviewing"                # 终面中
      FINAL_INTERVIEW_PASSED = "final_interview_passed"        # 终面通过
      FINAL_INTERVIEW_REJECTED = "final_interview_rejected"    # 终面淘汰
  
      # Offer阶段
      SALARY_NEGOTIATION = "salary_negotiation"      # 谈薪中
      SALARY_REJECTED = "salary_rejected"            # 谈薪失败
      VERBAL_OFFER_ACCEPTED = "verbal_offer_accepted" # 接受口头Offer
      OFFER_APPROVAL = "offer_approval"              # Offer审批中
      OFFER_APPROVAL_REJECTED = "offer_approval_rejected" # Offer审批拒绝
      OFFER_PENDING = "offer_pending"                # 待发Offer
      OFFER_SENT = "offer_sent"                      # 已发Offer
      OFFER_REJECTED = "offer_rejected"              # 已拒绝Offer
      OFFER_ACCEPTED = "offer_accepted"              # 已接受Offer

      # 入职阶段
      PENDING_ONBOARD = "pending_onboard"            # 待入职
      ONBOARD_CANCELLED = "onboard_cancelled"        # 取消入职
      ONBOARDED = "onboarded"                        # 已入职

      # 其他
      CANDIDATE_WITHDRAWN = "candidate_withdrawn"    # 候选人主动退出

  2.2 Application（应聘记录）- 新增字段

  class Application(Base):
      """应聘记录 - 连接候选人和职位"""
      __tablename__ = "applications"

      id = Column(String, primary_key=True, index=True)
      candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
      job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)

      # 状态
      status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW, index=True)
  
      # 简历信息
      resume_url = Column(String)
      resume_parsed_data = Column(Text)
  
      # 来源
      source = Column(String)
  
      # 负责人
      hr_id = Column(String, ForeignKey("users.id"), index=True)
      recruiter_id = Column(String, ForeignKey("users.id"))
  
      # 🆕 锁定信息
      is_locked = Column(Boolean, default=False, index=True)  # 是否锁定
      locked_by = Column(String, ForeignKey("users.id"))      # 锁定人
      locked_at = Column(DateTime(timezone=True))             # 锁定时间

      # 🆕 应聘次数统计
      application_count = Column(Integer, default=1)  # 该候选人应聘该职位的次数
  
      # 🆕 面试流程配置
      interview_flow_config = Column(Text)  # JSON格式，配置面试流程
      # 例如：{"hr_first": true, "need_assessment": true, "need_hr_reinterview": false}
  
      # 时间戳
      applied_at = Column(DateTime(timezone=True), server_default=func.now())
      hr_viewed_at = Column(DateTime(timezone=True))
      last_status_change_at = Column(DateTime(timezone=True))
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  
  2.3 User（用户）- 新增管理员角色

  class UserRole(str, enum.Enum):
      """用户角色"""
      ADMIN = "admin"              # 🆕 管理员
      HR = "hr"                    # HR
      RECRUITER = "recruiter"      # 招聘专员
      INTERVIEWER = "interviewer"  # 面试官

  2.4 Assessment（测评记录）- 新增

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

      # 测评类型
      assessment_type = Column(String)  # 如：商推测评、SHL测评
  
      # 测评链接
      assessment_url = Column(String)

      # 测评结果
      score = Column(Float)  # 得分
      level = Column(String)  # 水平：低、中低、中高、高
      report_url = Column(String)  # 测评报告URL

      # 状态
      status = Column(SQLEnum(AssessmentStatus), nullable=False, default=AssessmentStatus.INVITED)

      # 时间戳
      invited_at = Column(DateTime(timezone=True), server_default=func.now())
      started_at = Column(DateTime(timezone=True))
      completed_at = Column(DateTime(timezone=True))
      expires_at = Column(DateTime(timezone=True))  # 过期时间

      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

  2.5 OfferApprovalHistory（Offer审批历史）- 新增

  class OfferApprovalHistory(Base):
      """Offer审批历史"""
      __tablename__ = "offer_approval_history"

      id = Column(String, primary_key=True, index=True)
      offer_id = Column(String, ForeignKey("offers.id"), nullable=False, index=True)

      # 审批人
      approver_id = Column(String, ForeignKey("users.id"), nullable=False)
      approver_name = Column(String)
      approver_role = Column(String)  # 如：招聘组长、招聘部负责人

      # 审批结果
      action = Column(String)  # approved, rejected, auto_approved
      comments = Column(Text)  # 审批意见

      # 🆕 自动审批标识
      is_auto_approved = Column(Boolean, default=False)
      auto_approve_reason = Column(String)  # 如："与上一级审批人相同"

      # 时间戳
      created_at = Column(DateTime(timezone=True), server_default=func.now())
  
  ---
  三、关键业务逻辑调整

  3.1 简历锁定逻辑

  class ApplicationLockService:
      """简历锁定服务"""

      # 定义哪些状态会触发锁定
      LOCK_STATUSES = [
          ApplicationStatus.HR_INTERVIEW_SCHEDULED,
          ApplicationStatus.SENT_TO_INTERVIEWER,
          # ... 所有"简历初筛-已处理"之后的状态
      ]
  
      @staticmethod
      async def auto_lock(application: Application, operator: User):
          """自动锁定简历"""
          if application.status in ApplicationLockService.LOCK_STATUSES:
              if not application.is_locked:
                  application.is_locked = True
                  application.locked_by = operator.id
                  application.locked_at = datetime.now()
                  await application.save()

      @staticmethod
      async def check_permission(application: Application, operator: User) -> dict:
          """检查操作权限"""
          if not application.is_locked:
              return {"can_modify": True}

          # 如果是锁定人或管理员，可以修改
          if operator.id == application.locked_by or operator.role == UserRole.ADMIN:
              return {"can_modify": True}

          # 其他HR可以查看但不能修改
          return {
              "can_modify": False,
              "can_view": True,
              "locked_by": application.locked_by,
              "message": "该简历已被其他HR锁定，您可以查看但不能修改状态"
          }
  
  3.2 面试流程配置

  class InterviewFlowService:
      """面试流程配置服务"""

      @staticmethod
      async def configure_flow(application: Application, config: dict):
          """配置面试流程"""
          # config示例：
          # {
          #     "hr_first": true,           # HR面试是否在第一轮
          #     "need_assessment": true,    # 是否需要测评
          #     "need_hr_reinterview": false # 是否需要HR复试
          # }
          application.interview_flow_config = json.dumps(config)
          await application.save()

      @staticmethod
      def get_next_status(application: Application, current_status: ApplicationStatus) -> ApplicationStatus:
          """根据配置获取下一个状态"""
          config = json.loads(application.interview_flow_config or "{}")

          # 示例逻辑
          if current_status == ApplicationStatus.HR_SCREENING:
              if config.get("hr_first"):
                  return ApplicationStatus.HR_INTERVIEW_SCHEDULED
              else:
                  return ApplicationStatus.SENT_TO_INTERVIEWER
  
          if current_status == ApplicationStatus.DEPARTMENT_INTERVIEWING:
              if config.get("need_hr_reinterview"):
                  return ApplicationStatus.HR_REINTERVIEW_SCHEDULED
              elif config.get("need_assessment"):
                  return ApplicationStatus.ASSESSMENT_INVITED
              else:
                  return ApplicationStatus.FINAL_INTERVIEW_SCHEDULED

          # ... 其他逻辑

  3.3 Offer审批自动通过逻辑

  class OfferApprovalService:
      """Offer审批服务"""
  
      @staticmethod
      async def process_approval(offer: Offer, approver: User, action: str, comments: str = None):
          """处理审批"""
          # 记录审批历史
          history = OfferApprovalHistory(
              offer_id=offer.id,
              approver_id=approver.id,
              approver_name=approver.name,
              approver_role=approver.role,
              action=action,
              comments=comments,
          )

          # 检查是否需要自动通过
          if action == "approved":
              # 获取上一级审批人
              previous_approver = await OfferApprovalService.get_previous_approver(offer.id)

              # 如果当前审批人与上一级审批人相同，自动通过
              if previous_approver and previous_approver.approver_id == approver.id:
                  history.is_auto_approved = True
                  history.auto_approve_reason = "与上一级审批人相同，自动通过"

          await history.save()
  
          # 更新Offer状态
          await OfferApprovalService.move_to_next_approver(offer)

      @staticmethod
      async def get_previous_approver(offer_id: str):
          """获取上一级审批人"""
          histories = await OfferApprovalHistory.query.filter_by(
              offer_id=offer_id
          ).order_by(OfferApprovalHistory.created_at.desc()).all()
  
          return histories[0] if histories else None

  3.4 "X次应聘"功能

  class ApplicationHistoryService:
      """应聘历史服务"""
  
      @staticmethod
      async def get_application_count(candidate_id: str, job_id: str) -> int:
          """获取候选人应聘该职位的次数"""
          count = await Application.query.filter_by(
              candidate_id=candidate_id,
              job_id=job_id
          ).count()
          return count

      @staticmethod
      async def get_all_applications(candidate_id: str) -> list:
          """获取候选人的所有应聘记录"""
          applications = await Application.query.filter_by(
              candidate_id=candidate_id
          ).order_by(Application.applied_at.desc()).all()
  
          return [
              {
                  "job_title": app.job.title,
                  "status": app.status,
                  "applied_at": app.applied_at,
                  "is_active": app.status not in [
                      ApplicationStatus.HR_REJECTED,
                      ApplicationStatus.INTERVIEWER_REJECTED,
                      # ... 其他淘汰状态
                  ]
              }
              for app in applications
          ]

  ---
  四、新增API接口
  
  4.1 简历锁定相关

  POST   /api/v1/applications/{id}/lock          # 手动锁定简历
  POST   /api/v1/applications/{id}/unlock        # 解锁简历（仅管理员）
  GET    /api/v1/applications/{id}/lock-status   # 获取锁定状态
  
  4.2 面试流程配置

  POST   /api/v1/applications/{id}/configure-flow  # 配置面试流程
  GET    /api/v1/applications/{id}/flow-config     # 获取流程配置

  4.3 测评管理
  
  POST   /api/v1/assessments                      # 创建测评邀请
  GET    /api/v1/assessments/{id}                 # 获取测评详情
  POST   /api/v1/assessments/{id}/submit-result   # 提交测评结果
  POST   /api/v1/assessments/{id}/upload-report   # 上传测评报告
  
  4.4 应聘历史

  GET    /api/v1/candidates/{id}/application-history  # 获取候选人应聘历史
  GET    /api/v1/candidates/{id}/application-count    # 获取应聘次数

  4.5 管理员功能
  
  DELETE /api/v1/offers/{id}/admin-delete         # 管理员删除Offer
  POST   /api/v1/applications/{id}/admin-unlock   # 管理员解锁简历
  GET    /api/v1/admin/system-config              # 获取系统配置
  PUT    /api/v1/admin/system-config              # 更新系统配置
  
  ---
  五、前端UI调整

  5.1 简历列表页 - 新增锁定标识

  ┌─────────────────────────────────────────────────┐
  │  简历管理                                        │
  │  [上传简历]  [批量操作▼]  [搜索____________]    │
  ├─────────────────────────────────────────────────┤
  │  ┌───────────────────────────────────────────┐  │
  │  │ ☐ 张伟 - 高级前端工程师 🔒 (李HR锁定)    │  │
  │  │    5年经验 · 字节跳动 · Python/Go         │  │
  │  │    HR待查看 · 2小时前投递 · 2次应聘      │  │  ← 显示应聘次数
  │  │    [查看详情] [查看历史]                  │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘

  5.2 简历详情页 - 新增流程配置

  ┌─────────────────────────────────────────────────┐
  │  ← 返回  张伟 - 高级前端工程师                  │
  │  🔒 已锁定 (李HR) [解锁]                        │
  │  [配置面试流程] [查看应聘历史]                  │
  ├─────────────────────────────────────────────────┤
  │  [基本信息] [简历] [面试] [测评] [评价] [时间线]│
  ├─────────────────────────────────────────────────┤
  │  应聘历史 (2次)                                 │
  │  • 2026-05-30 - 高级前端工程师 - HR筛选中      │
  │  • 2026-03-15 - 前端工程师 - 已淘汰            │
  └─────────────────────────────────────────────────┘

  5.3 面试流程配置对话框
  
  ┌─────────────────────────────────────────────────┐
  │  配置面试流程                                    │
  ├─────────────────────────────────────────────────┤
  │  ☑ HR面试在第一轮                               │
  │  ☐ HR面试在用人部门面试后                       │
  │                                                  │
  │  ☑ 需要测评环节                                 │
  │  ☐ 需要HR复试                                   │
  │                                                  │
  │  [取消] [保存配置]                              │
  └─────────────────────────────────────────────────┘

  5.4 测评管理页面

  ┌─────────────────────────────────────────────────┐
  │  测评管理                                        │
  │  [邀请测评]  [批量邀请]  [搜索____________]     │
  ├─────────────────────────────────────────────────┤
  │  ┌───────────────────────────────────────────┐  │
  │  │ 张伟 - 高级前端工程师                     │  │
  │  │ 商推测评 ·
  ---
  │  │ 商推测评 · 得分: 5.5 (中高) · 已完成     │  │
  │  │ 邀请时间: 2026-05-25                      │  │
  │  │ 完成时间: 2026-05-27                      │  │
  │  │ [查看报告] [下载报告]                     │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 李娜 - 产品经理                           │  │
  │  │ SHL测评 · 进行中                          │  │
  │  │ 邀请时间: 2026-05-28                      │  │
  │  │ 有效期至: 2026-06-04                      │  │
  │  │ [催促完成] [重新发送]                     │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘

  ---
  六、状态转换规则表（完整版）

  6.1 正常流程转换

  ┌───────────────────────────────┬───────────────────────────────┬────────────────────────┬───────────────┐
  │           当前状态            │           可转换到            │        触发条件        │     说明      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ new                           │ hr_screening                  │ HR开始筛选             │ HR查看简历    │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_screening                  │ hr_interview_scheduled        │ HR筛选通过（路径A）    │ 先安排HR面试  │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_screening                  │ sent_to_interviewer           │ HR筛选通过（路径B）    │ 直接推送面试  │
  │                               │                               │                        │ 官            │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_screening                  │ hr_rejected                   │ HR筛选未通过           │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_interview_scheduled        │ hr_interviewing               │ 面试开始               │ HR面试进行中  │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_interviewing               │ sent_to_interviewer           │ HR面试通过             │ 推送给面试官  │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_interviewing               │ hr_interview_rejected         │ HR面试未通过           │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ sent_to_interviewer           │ department_interview_schedule │ 面试官筛选通过         │ 安排部门面试  │
  │                               │ d                             │                        │               │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ sent_to_interviewer           │ interviewer_rejected          │ 面试官筛选未通过       │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ department_interview_schedule │ department_interviewing       │ 面试开始               │ 部门面试进行  │
  │ d                             │                               │                        │ 中            │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ department_interviewing       │ hr_reinterview_scheduled      │ 部门面试通过+需要HR复  │ 安排HR复试    │
  │                               │                               │ 试                     │               │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ department_interviewing       │ assessment_invited            │ 部门面试通过+需要测评  │ 邀请测评      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ department_interviewing       │ final_interview_scheduled     │ 部门面试通过+直接终面  │ 安排终面      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ department_interviewing       │ department_interview_rejected │ 部门面试未通过         │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_reinterview_scheduled      │ hr_reinterviewing             │ 面试开始               │ HR复试进行中  │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_reinterviewing             │ assessment_invited            │ HR复试通过+需要测评    │ 邀请测评      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_reinterviewing             │ final_interview_scheduled     │ HR复试通过+直接终面    │ 安排终面      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ hr_reinterviewing             │ hr_reinterview_rejected       │ HR复试未通过           │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ assessment_invited            │ assessment_in_progress        │ 候选人开始测评         │ 测评进行中    │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ assessment_in_progress        │ assessment_completed          │ 测评完成+通过          │ 测评通过      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ assessment_in_progress        │ assessment_failed             │ 测评完成+未通过        │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ assessment_completed          │ final_interview_scheduled     │ 安排终面               │ 进入终面      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ final_interview_scheduled     │ final_interviewing            │ 面试开始               │ 终面进行中    │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ final_interviewing            │ final_interview_passed        │ 终面通过               │ 进入谈薪      │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ final_interviewing            │ final_interview_rejected      │ 终面未通过             │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ final_interview_passed        │ salary_negotiation            │ 开始谈薪               │ 谈薪中        │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ salary_negotiation            │ verbal_offer_accepted         │ 谈薪成功               │ 接受口头Offer │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ salary_negotiation            │ salary_rejected               │ 谈薪失败               │ 淘汰          │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ verbal_offer_accepted         │ offer_approval                │ 发起Offer审批          │ 审批中        │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ offer_approval                │ offer_pending                 │ 审批通过               │ 待发Offer     │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ offer_approval                │ offer_approval_rejected       │ 审批拒绝               │ 审批未通过    │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ offer_pending                 │ offer_sent                    │ 发送Offer              │ 已发Offer     │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ offer_sent                    │ offer_accepted                │ 候选人接受             │ 已接受Offer   │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ offer_sent                    │ offer_rejected                │ 候选人拒绝             │ 已拒绝Offer   │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ offer_accepted                │ pending_onboard               │ 自动创建入职记录       │ 待入职        │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ pending_onboard               │ onboarded                     │ 入职日期到达           │ 已入职        │
  ├───────────────────────────────┼───────────────────────────────┼────────────────────────┼───────────────┤
  │ pending_onboard               │ onboard_cancelled             │ 取消入职               │ 取消入职      │
  └───────────────────────────────┴───────────────────────────────┴────────────────────────┴───────────────┘

  6.2 异常流程转换

  ┌────────────────┬────────────────────────────────┬─────────────┬────────────────────────────┐
  │    异常场景    │            当前状态            │  处理方式   │          目标状态          │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 操作失误需撤销 │ 任意状态                       │ 点击"撤销"  │ 回退到上一状态             │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 面试临时取消   │ *_interview_scheduled          │ 取消面试    │ 回到上一状态               │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 面试改期       │ *_interview_scheduled          │ 修改时间    │ 保持当前状态               │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 候选人未到     │ *_interviewing                 │ 标记未到    │ 保持当前状态               │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ Offer薪资变动  │ offer_sent                     │ 删除旧Offer │ 回到 verbal_offer_accepted │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 入职改期       │ pending_onboard                │ 修改日期    │ 保持 pending_onboard       │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 候选人中途退出 │ 任意状态                       │ 标记退出    │ candidate_withdrawn        │
  ├────────────────┼────────────────────────────────┼─────────────┼────────────────────────────┤
  │ 测评过期       │ assessment_invited/in_progress │ 自动过期    │ assessment_failed          │
  └────────────────┴────────────────────────────────┴─────────────┴────────────────────────────┘

  ---
  七、权限控制矩阵
  
  7.1 角色权限对照表
  
  ┌──────────────┬────────┬───────────────┬───────────────┬─────────────┐
  │     功能     │ 管理员 │      HR       │   Recruiter   │ Interviewer │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 职位管理       │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 创建职位       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 编辑职位       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 删除职位       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看所有职位   │ ✅     │ ✅            │ ✅            │ ✅          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 简历管理       │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 上传简历       │ ✅     │ ✅            │ ✅            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看所有简历   │ ✅     │ ✅            │ ⚠️  仅自己负责 │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看锁定简历   │ ✅     │ ⚠️  可见不可改 │ ⚠️  可见不可改 │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 解锁简历       │ ✅     │ ⚠️  仅自己锁定 │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 修改简历状态   │ ✅     │ ✅            │ ⚠️  仅自己负责 │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 推送给面试官   │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 面试管理       │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 安排面试       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看所有面试   │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看自己的面试 │ ✅     │ ✅            │ ❌            │ ✅          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 填写面试评价   │ ✅     │ ✅            │ ❌            │ ✅          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 筛选简历       │ ✅     │ ❌            │ ❌            │ ✅          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 测评管理       │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 邀请测评       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看测评结果   │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 上传测评报告   │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ Offer管理      │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 发起Offer审批  │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 审批Offer      │ ✅     │ ⚠️  根据审批链 │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 编辑Offer      │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 发送Offer      │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 删除Offer      │ ✅     │ ❌            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 入职管理       │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 查看待入职     │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 发送信息采集   │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 改期入职       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 取消入职       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 系统管理       │        │               │               │             │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 系统配置       │ ✅     │ ❌            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 用户管理       │ ✅     │ ❌            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 部门管理       │ ✅     │ ✅            │ ❌            │ ❌          │
  ├────────────────┼────────┼───────────────┼───────────────┼─────────────┤
  │ 评价表模板     │ ✅     │ ✅            │ ❌            │ ❌          │
  └────────────────┴────────┴───────────────┴───────────────┴─────────────┘

  ---
  八、评价表模板自动匹配规则
  
  8.1 评价表类型定义
  
  class ScorecardType(str, enum.Enum):
      """评价表类型"""
      HR_SCREENING = "hr_screening"              # HR初筛评价表
      DEPARTMENT_INTERVIEW = "department_interview"  # 用人部门面试评价表
      FINAL_INTERVIEW = "final_interview"        # 终面官面试评价表
      HR_REINTERVIEW = "hr_reinterview"          # HR复试评价表

  8.2 自动匹配逻辑

  class ScorecardMatchService:
      """评价表匹配服务"""

      @staticmethod
      def get_scorecard_template(
          interview_round: InterviewRound,
          recruitment_type: RecruitmentType,
          interviewer_role: UserRole
      ) -> str:
          """根据面试轮次、招聘类别、面试官角色自动匹配评价表"""

          # 规则1：社招 + HR面 → HR初筛评价表
          if recruitment_type == RecruitmentType.SOCIAL and interviewer_role == UserRole.HR:
              if interview_round == InterviewRound.FIRST:
                  return ScorecardType.HR_SCREENING
              else:
                  return ScorecardType.HR_REINTERVIEW
  
          # 规则2：社招 + 用人部门面试 → 用人部门面试评价表
          if recruitment_type == RecruitmentType.SOCIAL and interviewer_role == UserRole.INTERVIEWER:
              if interview_round == InterviewRound.FINAL:
                  return ScorecardType.FINAL_INTERVIEW
              else:
                  return ScorecardType.DEPARTMENT_INTERVIEW
  
          # 规则3：校招 + 任何面试 → 校招评价表
          if recruitment_type == RecruitmentType.CAMPUS:
              return "campus_interview"

          # 默认
          return ScorecardType.DEPARTMENT_INTERVIEW
  
  ---
  九、Offer模板自动推荐规则

  9.1 Offer模板类型

  class OfferTemplateType(str, enum.Enum):
      """Offer模板类型"""
      SOCIAL_NO_EQUITY = "social_no_equity"      # 社招无期权
      SOCIAL_WITH_EQUITY = "social_with_equity"  # 社招有期权
      CAMPUS = "campus"                          # 校招/应届生
      INTERNSHIP = "internship"                  # 实习生

  9.2 自动推荐逻辑

  class OfferTemplateService:
      """Offer模板服务"""

      @staticmethod
      def recommend_template(
          recruitment_type: RecruitmentType,
          has_stock_options: bool
      ) -> OfferTemplateType:
          """根据招聘类别和是否有期权推荐模板"""
  
          if recruitment_type == RecruitmentType.SOCIAL:
              if has_stock_options:
                  return OfferTemplateType.SOCIAL_WITH_EQUITY
              else:
                  return OfferTemplateType.SOCIAL_NO_EQUITY
  
          elif recruitment_type == RecruitmentType.CAMPUS:
              return OfferTemplateType.CAMPUS

          elif recruitment_type == RecruitmentType.INTERNSHIP:
              return OfferTemplateType.INTERNSHIP

          return OfferTemplateType.SOCIAL_NO_EQUITY

  ---
  十、前端组件设计（新增）

  10.1 应聘历史弹窗
  
  // components/ApplicationHistoryDialog.tsx
  interface ApplicationHistoryDialogProps {
    candidateId: string;
    open: boolean;
    onClose: () => void;
  }

  export function ApplicationHistoryDialog({
    candidateId,
    open,
    onClose
  }: ApplicationHistoryDialogProps) {
    const { data: history } = useQuery({
      queryKey: ['application-history', candidateId],
      queryFn: () => fetchApplicationHistory(candidateId),
    });
  
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>应聘历史 ({history?.length || 0}次)</DialogTitle>
          </DialogHeader>
  
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {history?.map(app => (
              <div key={app.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">{app.job_title}</h4>
                    <p className="text-sm text-gray-500">
                      {formatDate(app.applied_at)}
                    </p>
                  </div>
                  <Badge variant={app.is_active ? 'default' : 'secondary'}>
                    {getStatusLabel(app.status)}
                  </Badge>
                </div>

                {app.is_active && (
                  <div className="mt-2 text-sm text-orange-600">
                    ⚠️  该候选人在此职位的流程中
                  </div>
                )}
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  10.2 面试流程配置组件

  // components/InterviewFlowConfig.tsx
  interface InterviewFlowConfigProps {
    applicationId: string;
    currentConfig: InterviewFlowConfig;
    onSave: (config: InterviewFlowConfig) => void;
  }

  export function InterviewFlowConfig({
    applicationId,
    currentConfig,
    onSave
  }: InterviewFlowConfigProps) {
    const [config, setConfig] = useState(currentConfig);
  
    return (
      <Card>
        <CardHeader>
          <CardTitle>面试流程配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>HR面试时机</Label>
            <RadioGroup
              value={config.hr_first ? 'first' : 'after'}
              onValueChange={(value) =>
                setConfig({ ...config, hr_first: value === 'first' })
              }
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="first" id="hr-first" />
                <Label htmlFor="hr-first">第一轮（HR初筛面试）</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="after" id="hr-after" />
                <Label htmlFor="hr-after">用人部门面试后（HR复试）</Label>
              </div>
            </RadioGroup>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="need-assessment"
              checked={config.need_assessment}
              onCheckedChange={(checked) =>
                setConfig({ ...config, need_assessment: checked as boolean })
              }
            />
            <Label htmlFor="need-assessment">需要测评环节</Label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="need-hr-reinterview"
              checked={config.need_hr_reinterview}
              onCheckedChange={(checked) =>
                setConfig({ ...config, need_hr_reinterview: checked as boolean })
              }
            />
            <Label htmlFor="need-hr-reinterview">需要HR复试</Label>
          </div>

          <Button onClick={() => onSave(config)}>
            保存配置
          </Button>
        </CardContent>
      </Card>
    );
  }

  10.3 简历锁定提示组件

  // components/ApplicationLockBanner.tsx
  interface ApplicationLockBannerProps {
    application: Application;
    currentUser: User;
  }
  
  export function ApplicationLockBanner({
    application,
    currentUser
  }: ApplicationLockBannerProps) {
    if (!application.is_locked) return null;

    const isLockedByMe = application.locked_by === currentUser.id;
    const canUnlock = isLockedByMe || currentUser.role === UserRole.ADMIN;
  
    return (
      <Alert variant={isLockedByMe ? 'default' : 'warning'}>
        <Lock className="h-4 w-4" />
        <AlertTitle>
          {isLockedByMe ? '您已锁定此简历' : '此简历已被锁定'}
        </AlertTitle>
        <AlertDescription className="flex items-center justify-between">
          <span>
            {isLockedByMe
              ? '其他HR可以查看但不能修改状态'
              : `由 ${application.locked_by_name} 锁定，您可以查看但不能修改状态`
            }
          </span>
          {canUnlock && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => unlockApplication(application.id)}
            >
              解锁
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  }
  
  ---
  十一、数据库迁移脚本

  11.1 新增字段迁移
  
  -- Application表新增字段
  ALTER TABLE applications ADD COLUMN is_locked BOOLEAN DEFAULT FALSE;
  ALTER TABLE applications ADD COLUMN locked_by VARCHAR;
  ALTER TABLE applications ADD COLUMN locked_at TIMESTAMP WITH TIME ZONE;
  ALTER TABLE applications ADD COLUMN application_count INTEGER DEFAULT 1;
  ALTER TABLE applications ADD COLUMN interview_flow_config TEXT;

  CREATE INDEX idx_applications_is_locked ON applications(is_locked);
  CREATE INDEX idx_applications_locked_by ON applications(locked_by);

  -- User表新增管理员角色
  -- 需要更新枚举类型
  ALTER TYPE userrole ADD VALUE 'admin';
  
  -- 创建Assessment表
  CREATE TABLE assessments (
      id VARCHAR PRIMARY KEY,
      application_id VARCHAR NOT NULL REFERENCES applications(id),
      candidate_id VARCHAR REFERENCES candidates(id),
      assessment_type VARCHAR,
      assessment_url VARCHAR,
      score FLOAT,
      level VARCHAR,
      report_url VARCHAR,
      status VARCHAR NOT NULL DEFAULT 'invited',
      invited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      started_at TIMESTAMP WITH TIME ZONE,
      completed_at TIMESTAMP WITH TIME ZONE,
      expires_at TIMESTAMP WITH TIME ZONE,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE
  );

  CREATE INDEX idx_assessments_application_id ON assessments(application_id);
  CREATE INDEX idx_assessments_candidate_id ON assessments(candidate_id);
  CREATE INDEX idx_assessments_status ON assessments(status);

  -- 创建OfferApprovalHistory表
  CREATE TABLE offer_approval_history (
      id VARCHAR PRIMARY KEY,
      offer_id VARCHAR NOT NULL REFERENCES offers(id),
      approver_id VARCHAR NOT NULL REFERENCES users(id),
      approver_name VARCHAR,
      approver_role VARCHAR,
      action VARCHAR,
      comments TEXT,
      is_auto_approved BOOLEAN DEFAULT FALSE,
      auto_approve_reason VARCHAR,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  
  CREATE INDEX idx_offer_approval_history_offer_id ON offer_approval_history(offer_id);
  CREATE INDEX idx_offer_approval_history_approver_id ON offer_approval_history(approver_id);

  ---
  十二、待确认清单（更新）

  🔶 仍需确认的问题

  1. "历史审批人"的具体定义
    - 问题：Offer审批自动通过时，"历史审批人"指的是什么？
    - 选项：
        - A. 同一个Offer的上一级审批人
      - B. 同一个候选人之前Offer的审批人
      - C. 其他定义
    - 请明确说明
  2. 测评报告的具体字段
    - 商推报告需要哪些字段？
    - SHL报告需要哪些字段？
    - 是否需要支持其他测评类型？
  3. 面试流程配置的默认值
    - 新创建的应聘记录，默认流程配置是什么？
    - 是否需要在职位级别设置默认流程？
  4. 简历锁定的自动解锁机制
    - 是否需要自动解锁？（如：7天后自动解锁）
    - 还是永久锁定，只能手动解锁？
  5. 管理员的具体权限范围
    - 除了删除Offer、解锁简历，还需要哪些权限？
    - 是否需要查看所有操作日志？
    - 是否需要数据导出功能？

  ---
  十三、总结

  修正内容汇总
  
  1. ✅ 新增HR面试环节（可在第一轮或最后）
  2. ✅ 新增测评环节（可选）
  3. ✅ 新增简历锁定机制（可见可查看，不可修改）
  4. ✅ 新增管理员角色
  5. ✅ 新增应聘历史功能（"X次应聘"）
  6. ✅ 新增面试流程配置
  7. ✅ 新增评价表自动匹配规则
  8. ✅ 新增Offer模板自动推荐
  9. ✅ 完善权限控制矩阵
  10. ❓ Offer审批自动通过逻辑待确认

  下一步行动

  请先确认"历史审批人"的定义，然后我可以：
  1. 完善Offer审批自动通过的代码实现
  2. 开始编写完整的数据模型代码
  3. 开始编写API接口代码
  4. 开始编写前端页面代码

  ---
  修正版设计文档完成！请确认"历史审批人"的定义后，我们开始编码实现。 🎯
  
✻ Baked for 1m 32s
  