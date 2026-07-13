 ---
  DeepHire 招聘系统 - 整体架构设计文档
  
  一、系统全局状态机设计
  
  1.1 候选人全生命周期状态流转
  
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
  │  面试意向沟通中 │ (interview_intention)
  └─────────────────┘
      ↓ 候选人同意 / ↓ 候选人拒绝
      ↓              ↓
      ↓         ┌─────────────────┐
      ↓         │  候选人放弃面试 │ (candidate_declined)
      ↓         └─────────────────┘
      ↓
  ┌─────────────────┐
  │  已约定面试时间 │ (interview_scheduled)
  └─────────────────┘
      ↓
  ┌─────────────────┐
  │  面试中         │ (interviewing)
  └─────────────────┘
      ↓ 面试通过 / ↓ 面试失败
      ↓            ↓
      ↓       ┌─────────────────┐
      ↓       │  面试淘汰       │ (interview_failed)
      ↓       └─────────────────┘
      ↓
  ┌─────────────────┐
  │  面试通过       │ (interview_passed)
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

  1.2 异常流程处理

  ┌────────────────┬─────────────────────┬────────────────────────┬────────────────────────────┐
  │    异常场景    │      当前状态       │        处理方式        │          目标状态          │
  ├────────────────┼─────────────────────┼────────────────────────┼────────────────────────────┤
  │ 操作失误需撤销 │ 任意状态            │ 点击"撤销"按钮         │ 回退到上一状态             │
  ├────────────────┼─────────────────────┼────────────────────────┼────────────────────────────┤
  │ 面试临时取消   │ interview_scheduled │ 取消面试               │ 回到 interview_intention   │
  ├────────────────┼─────────────────────┼────────────────────────┼────────────────────────────┤
  │ 面试改期       │ interview_scheduled │ 修改面试时间           │ 保持 interview_scheduled   │
  ├────────────────┼─────────────────────┼────────────────────────┼────────────────────────────┤
  │ Offer薪资变动  │ offer_sent          │ 删除旧Offer，重新发起  │ 回到 verbal_offer_accepted │
  ├────────────────┼─────────────────────┼────────────────────────┼────────────────────────────┤
  │ 入职改期       │ pending_onboard     │ 修改入职日期           │ 保持 pending_onboard       │
  ├────────────────┼─────────────────────┼────────────────────────┼────────────────────────────┤
  │ 候选人中途退出 │ 任意状态            │ 标记为"候选人主动退出" │ candidate_withdrawn        │
  └────────────────┴─────────────────────┴────────────────────────┴────────────────────────────┘

  ---
  二、核心数据模型设计
  
  2.1 Application（应聘记录）- 核心关联表
  
  class ApplicationStatus(str, enum.Enum):
      """应聘状态 - 完整生命周期"""
      # 简历阶段
      NEW = "new"                                    # 新简历
      HR_SCREENING = "hr_screening"                  # HR筛选中
      HR_REJECTED = "hr_rejected"                    # HR淘汰

      # 面试官筛选阶段
      SENT_TO_INTERVIEWER = "sent_to_interviewer"   # 推送给面试官
      INTERVIEWER_REJECTED = "interviewer_rejected"  # 面试官淘汰

      # 面试意向阶段
      INTERVIEW_INTENTION = "interview_intention"    # 面试意向沟通中
      CANDIDATE_DECLINED = "candidate_declined"      # 候选人放弃面试

      # 面试阶段
      INTERVIEW_SCHEDULED = "interview_scheduled"    # 已约定面试时间
      INTERVIEWING = "interviewing"                  # 面试中
      INTERVIEW_FAILED = "interview_failed"          # 面试淘汰
      INTERVIEW_PASSED = "interview_passed"          # 面试通过

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

  class Application(Base):
      """应聘记录 - 连接候选人和职位"""
      __tablename__ = "applications"

      id = Column(String, primary_key=True, index=True)
      candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
      job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)

      # 状态
      status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.NEW, index=True)

      # 简历信息
      resume_url = Column(String)  # 简历文件URL
      resume_parsed_data = Column(Text)  # 解析后的简历数据（JSON）

      # 来源
      source = Column(String)  # 简历来源：主动投递、内推、猎头等

      # 负责人
      hr_id = Column(String, ForeignKey("users.id"), index=True)  # 负责HR
      recruiter_id = Column(String, ForeignKey("users.id"))  # 招聘专员

      # 时间戳
      applied_at = Column(DateTime(timezone=True), server_default=func.now())  # 投递时间
      hr_viewed_at = Column(DateTime(timezone=True))  # HR查看时间
      last_status_change_at = Column(DateTime(timezone=True))  # 最后状态变更时间
  
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

  2.2 Interview（面试记录）
  
  class InterviewRound(str, enum.Enum):
      """面试轮次"""
      FIRST = "first"      # 初试
      SECOND = "second"    # 复试
      FINAL = "final"      # 终试

  class InterviewStatus(str, enum.Enum):
      """面试状态"""
      SCHEDULED = "scheduled"      # 已安排
      CONFIRMED = "confirmed"      # 候选人已确认
      DECLINED = "declined"        # 候选人拒绝
      CANCELLED = "cancelled"      # 已取消
      RESCHEDULED = "rescheduled"  # 已改期
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
  
      # 面试信息
      round = Column(SQLEnum(InterviewRound), nullable=False)
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

      # 通知
      notification_sent_to_candidate = Column(Boolean, default=False)
      notification_sent_to_interviewer = Column(Boolean, default=False)
      candidate_confirmed_at = Column(DateTime(timezone=True))
  
      # 时间戳
      completed_at = Column(DateTime(timezone=True))
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  
  2.3 Offer（Offer记录）

  class OfferStatus(str, enum.Enum):
      """Offer状态"""
      APPROVAL_PENDING = "approval_pending"    # 审批中
      APPROVAL_REJECTED = "approval_rejected"  # 审批拒绝
      PENDING = "pending"                      # 待发送
      SENT = "sent"                           # 已发送
      ACCEPTED = "accepted"                   # 已接受
      REJECTED = "rejected"                   # 已拒绝
      EXPIRED = "expired"                     # 已过期
      CANCELLED = "cancelled"                 # 已取消

  class OfferApprovalStatus(str, enum.Enum):
      """Offer审批状态"""
      PENDING = "pending"              # 待审批
      APPROVED = "approved"            # 已通过
      REJECTED = "rejected"            # 已拒绝
      AUTO_APPROVED = "auto_approved"  # 自动通过

  class Offer(Base):
      """Offer记录"""
      __tablename__ = "offers"

      id = Column(String, primary_key=True, index=True)
      application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
      job_id = Column(String, ForeignKey("jobs.id"), index=True)
      candidate_id = Column(String, ForeignKey("candidates.id"), index=True)
  
      # 录用信息
      hiring_company = Column(String)  # 录用公司
      hiring_department_id = Column(String, ForeignKey("departments.id"))
      hiring_position = Column(String)  # 录用职位
      hiring_level = Column(String)  # 职级

      # 薪资信息
      base_salary = Column(Integer)  # 基本工资
      bonus = Column(Integer)  # 奖金
      stock_options = Column(Integer)  # 期权
      total_compensation = Column(Integer)  # 总薪酬
      currency = Column(String, default="CNY")

      # 入职信息
      expected_onboard_date = Column(DateTime(timezone=True))  # 期望入职日期
      work_location = Column(String)  # 工作地点

      # 审批信息
      approval_status = Column(SQLEnum(OfferApprovalStatus), default=OfferApprovalStatus.PENDING)
      approval_chain = Column(Text)  # 审批链（JSON）
      current_approver_id = Column(String, ForeignKey("users.id"))
  
      # 面试评价
      interview_feedback = Column(Text)  # 所有面试官评价汇总
      talent_category = Column(String)  # 人才类别
      culture_fit_score = Column(Integer)  # 文化匹配度
      potential_score = Column(Integer)  # 潜力度
      clarity_score = Column(Integer)  # 明白度

      # Offer文件
      offer_letter_url = Column(String)  # Offer文件URL
      offer_template = Column(String)  # 使用的模板

      # 状态
      status = Column(SQLEnum(OfferStatus), nullable=False, default=OfferStatus.APPROVAL_PENDING)

      # 有效期
      valid_until = Column(DateTime(timezone=True))

      # 备注
      notes = Column(Text)

      # 时间戳
      sent_at = Column(DateTime(timezone=True))
      accepted_at = Column(DateTime(timezone=True))
      rejected_at = Column(DateTime(timezone=True))
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  
  2.4 Onboarding（入职记录）

  class OnboardingStatus(str, enum.Enum):
      """入职状态"""
      PENDING = "pending"              # 待入职
      INFO_COLLECTING = "info_collecting"  # 信息采集中
      INFO_COLLECTED = "info_collected"    # 信息已采集
      CANCELLED = "cancelled"          # 已取消
      COMPLETED = "completed"          # 已完成

  class Onboarding(Base):
      """入职记录"""
      __tablename__ = "onboardings"

      id = Column(String, primary_key=True, index=True)
      application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
      offer_id = Column(String, ForeignKey("offers.id"), index=True)
      candidate_id = Column(String, ForeignKey("candidates.id"), index=True)
  
      # 入职信息
      onboard_date = Column(DateTime(timezone=True), nullable=False, index=True)
      department_id = Column(String, ForeignKey("departments.id"))
      position = Column(String)
      work_location = Column(String)

      # 负责人
      department_manager_id = Column(String, ForeignKey("users.id"))  # 部门负责人
      mentor_id = Column(String, ForeignKey("users.id"))  # 导师
      hr_contact_id = Column(String, ForeignKey("users.id"))  # HR对接人
  
      # 信息采集
      info_collection_sent_at = Column(DateTime(timezone=True))  # 信息采集通知发送时间
      info_collected_at = Column(DateTime(timezone=True))  # 信息采集完成时间
      collected_data = Column(Text)  # 采集的信息（JSON）
  
      # 状态
      status = Column(SQLEnum(OnboardingStatus), nullable=False, default=OnboardingStatus.PENDING)

      # 备注
      notes = Column(Text)
      cancellation_reason = Column(Text)  # 取消原因

      # 时间戳
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())
      completed_at = Column(DateTime(timezone=True))
      cancelled_at = Column(DateTime(timezone=True))

  2.5 ApplicationStatusHistory（应聘状态历史）

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

  2.6 ScorecardTemplate（评价表模板）

  class ScorecardTemplate(Base):
      """评价表模板"""
      __tablename__ = "scorecard_templates"

      id = Column(String, primary_key=True, index=True)
      name = Column(String, nullable=False)  # 如：HR初筛评价表、用人部门面试评价表
      type = Column(String)  # hr_screening, department_interview, final_interview

      # 评价维度（JSON格式）
      dimensions = Column(Text)  # [{"name": "专业能力", "weight": 0.4}, ...]

      is_active = Column(Boolean, default=True)
      created_at = Column(DateTime(timezone=True), server_default=func.now())
      updated_at = Column(DateTime(timezone=True), onupdate=func.now())

  ---
  三、关键业务流程设计

  3.1 简历投递到职位流程
  
  1. 候选人投递简历到职位
     ↓
  2. 创建 Application 记录
     - status = NEW
     - 关联 candidate_id 和 job_id
     ↓
  3. 简历解析（如果是新上传）
     - 解析PDF/DOCX
     - 提取结构化信息
     - 存储到 resume_parsed_data
     ↓
  4. 查重检查
     - 检查同一候选人是否已投递过该职位
     - 检查候选人是否在其他职位的流程中
     ↓
  5. HR收到通知
     - 右上角消息提醒
     - 待处理列表+1

  3.2 HR筛选流程

  1. HR查看简历列表
     - 筛选 status = NEW 的应聘记录
     ↓
  2. HR点击查看简历详情
     - 更新 hr_viewed_at
     ↓
  3. HR做出决策
     - 通过：status → HR_SCREENING → SENT_TO_INTERVIEWER
     - 淘汰：status → HR_REJECTED
     ↓
  4. 如果通过，推送给面试官
     - 面试官收到通知
     - 面试官待筛选列表+1

  3.3 面试官筛选流程

  1. 面试官查看简历
     - 筛选 status = SENT_TO_INTERVIEWER 的记录
     ↓
  2. 面试官做出决策
     - 通过：status → INTERVIEW_INTENTION
     - 淘汰：status → INTERVIEWER_REJECTED
     ↓
  3. HR收到通知
     - 右上角消息提醒
     - 可查看筛选结果

  3.4 面试安排流程

  1. HR发起面试意向沟通
     - status = INTERVIEW_INTENTION
     - 智能外呼 或 人工联系
     ↓
  2. 候选人反馈
     - 同意：继续
     - 拒绝：status → CANDIDATE_DECLINED
     ↓
  3. HR安排面试
     - 创建 Interview 记录
     - 选择面试官
     - 选择评价表模板
     - 设置时间地点
     ↓
  4. 发送面试通知
     - 发送邮件给候选人
     - 发送通知给面试官
     - status → INTERVIEW_SCHEDULED
     ↓
  5. 候选人确认
     - 参加：status → INTERVIEWING
     - 不参加：status → CANDIDATE_DECLINED

  3.5 面试评价流程

  1. 面试官完成面试
     - 填写评价表
     - 给出评分和反馈
     - Interview.result = PASS/FAIL
     ↓
  2. HR收到通知
     - 右上角消息提醒
     ↓
  3. HR查看评价结果
     - 通过：status → INTERVIEW_PASSED
     - 淘汰：status → INTERVIEW_FAILED
     ↓
  4. 如果有多轮面试
     - 继续安排下一轮
     - 重复面试流程

  3.6 Offer流程

  1. 谈薪成功
     - status → VERBAL_OFFER_ACCEPTED
     ↓
  2. 发起Offer审批
     - 创建 Offer 记录
     - 填写录用信息、薪资信息
     - 设置审批链
     - Offer.approval_status = PENDING
     ↓
  3. 审批流转
     - 招聘HR → 招聘组长 → 招聘部负责人 → HRD → HRD负责人
     - 如果审批人重复，自动通过
     ↓
  4. 审批通过
     - Offer.approval_status = APPROVED
     - Offer.status = PENDING
     - Application.status = OFFER_PENDING
     ↓
  5. Offer编辑
     - 完善Offer详细信息
     - 生成Offer文件
     ↓
  6. 发送Offer
     - 发送邮件给候选人
     - Offer.status = SENT
     - Application.status = OFFER_SENT
     ↓
  7. 候选人反馈
     - 接受：Offer.status = ACCEPTED, Application.status = OFFER_ACCEPTED
     - 拒绝：Offer.status = REJECTED, Application.status = OFFER_REJECTED
  
  3.7 入职流程

  1. 候选人接受Offer
     - Application.status = OFFER_ACCEPTED
     - 自动创建 Onboarding 记录
     - Onboarding.status = PENDING
     ↓
  2. 发送信息采集通知
     - 发送邮件给候选人
     - Onboarding.status = INFO_COLLECTING
     ↓
  3. 候选人填写信息
     - 采集个人信息、银行卡等
     - Onboarding.status = INFO_COLLECTED
     ↓
  4. 入职日期到达
     - HR确认入职
     - Onboarding.status = COMPLETED
     - Application.status = ONBOARDED
     - Job.application_count -= 1
     - Job.openings -= 1
  
  ---
  四、API接口设计

  4.1 职位模块 API
  
  POST   /api/v1/jobs                    # 创建职位
  GET    /api/v1/jobs                    # 获取职位列表
  GET    /api/v1/jobs/{id}               # 获取职位详情
  PUT    /api/v1/jobs/{id}               # 更新职位
  DELETE /api/v1/jobs/{id}               # 删除职位
  PATCH  /api/v1/jobs/{id}/status        # 更新职位状态
  GET    /api/v1/jobs/{id}/applications  # 获取职位的应聘记录
  GET    /api/v1/jobs/{id}/status-history # 获取职位状态历史

  4.2 简历管理模块 API

  POST   /api/v1/applications                      # 创建应聘记录（投递简历）
  GET    /api/v1/applications                      # 获取应聘记录列表
  GET    /api/v1/applications/{id}                 # 获取应聘记录详情
  PATCH  /api/v1/applications/{id}/status          # 更新应聘状态
  POST   /api/v1/applications/{id}/push-to-interviewer  # 推送给面试官
  POST   /api/v1/applications/{id}/reject          # 淘汰
  POST   /api/v1/applications/{id}/undo            # 撤销操作
  GET    /api/v1/applications/{id}/status-history  # 获取状态历史
  POST   /api/v1/applications/upload-resume        # 上传简历到职位
  POST   /api/v1/applications/check-duplicate      # 查重

  4.3 面试管理模块 API

  POST   /api/v1/interviews                        # 安排面试
  GET    /api/v1/interviews                        # 获取面试列表
  GET    /api/v1/interviews/{id}                   # 获取面试详情
  PUT    /api/v1/interviews/{id}                   # 更新面试（改期）
  DELETE /api/v1/interviews/{id}                   # 取消面试
  POST   /api/v1/interviews/{id}/reschedule        # 改期面试
  POST   /api/v1/interviews/{id}/complete          # 完成面试
  POST   /api/v1/interviews/{id}/feedback          # 提交面试评价
  POST   /api/v1/interviews/{id}/send-notification # 发送面试通知
  POST   /api/v1/interviews/{id}/candidate-confirm # 候选人确认面试
  POST   /api/v1/interviews/{id}/candidate-decline # 候选人拒绝面试
  GET    /api/v1/interviews/my-interviews          # 面试官查看自己的面试

  4.4 Offer管理模块 API

  POST   /api/v1/offers                            # 创建Offer
  GET    /api/v1/offers                            # 获取Offer列表
  GET    /api/v1/offers/{id}                       # 获取Offer详情
  PUT    /api/v1/offers/{id}                       # 编辑Offer
  DELETE /api/v1/offers/{id}                       # 删除Offer
  POST   /api/v1/offers/{id}/submit-approval       # 提交审批
  POST   /api/v1/offers/{id}/approve               # 审批通过
  ---
  POST   /api/v1/offers/{id}/reject                 # 审批拒绝
  POST   /api/v1/offers/{id}/send                   # 发送Offer
  POST   /api/v1/offers/{id}/generate-letter        # 生成Offer文件
  POST   /api/v1/offers/{id}/candidate-accept       # 候选人接受Offer
  POST   /api/v1/offers/{id}/candidate-reject       # 候选人拒绝Offer
  GET    /api/v1/offers/{id}/approval-chain         # 获取审批链
  GET    /api/v1/offers/pending                     # 获取待发Offer列表
  GET    /api/v1/offers/sent                        # 获取已发Offer列表

  4.5 入职管理模块 API

  POST   /api/v1/onboardings                        # 创建入职记录（自动）
  GET    /api/v1/onboardings                        # 获取入职记录列表
  GET    /api/v1/onboardings/{id}                   # 获取入职详情
  PUT    /api/v1/onboardings/{id}                   # 更新入职信息
  POST   /api/v1/onboardings/{id}/send-info-collection  # 发送信息采集通知
  POST   /api/v1/onboardings/{id}/reschedule        # 改期入职
  POST   /api/v1/onboardings/{id}/cancel            # 取消入职
  POST   /api/v1/onboardings/{id}/complete          # 完成入职
  GET    /api/v1/onboardings/pending                # 获取待入职列表

  4.6 部门管理 API

  POST   /api/v1/departments                        # 创建部门
  GET    /api/v1/departments                        # 获取部门列表
  GET    /api/v1/departments/tree                   # 获取部门树
  GET    /api/v1/departments/{id}                   # 获取部门详情
  PUT    /api/v1/departments/{id}                   # 更新部门
  DELETE /api/v1/departments/{id}                   # 删除部门

  4.7 评价表模板 API
  
  POST   /api/v1/scorecard-templates                # 创建评价表模板
  GET    /api/v1/scorecard-templates                # 获取模板列表
  GET    /api/v1/scorecard-templates/{id}           # 获取模板详情
  PUT    /api/v1/scorecard-templates/{id}           # 更新模板
  DELETE /api/v1/scorecard-templates/{id}           # 删除模板

  4.8 通知消息 API

  GET    /api/v1/notifications                      # 获取通知列表
  GET    /api/v1/notifications/unread-count         # 获取未读数量
  POST   /api/v1/notifications/{id}/mark-read       # 标记为已读
  POST   /api/v1/notifications/mark-all-read        # 全部标记为已读

  ---
  五、前端页面结构设计

  5.1 HR Dashboard（HR首页）
  
  ┌─────────────────────────────────────────────────┐
  │  DeepHire  [职位] [简历] [面试] [Offer] [入职]  │
  │                                    [通知🔔3] [HR]│
  ├─────────────────────────────────────────────────┤
  │  统计卡片                                        │
  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
  │  │ 招聘中   │ │ 待处理   │ │ 本月入职 │        │
  │  │ 15个职位 │ │ 23条简历 │ │ 8人      │        │
  │  └──────────┘ └──────────┘ └──────────┘        │
  ├─────────────────────────────────────────────────┤
  │  待处理事项                                      │
  │  ┌───────────────────────────────────────────┐  │
  │  │ • 5份简历待查看                           │  │
  │  │ • 3个面试评价待查看                       │  │
  │  │ • 2个Offer审批待处理                      │  │
  │  │ • 1个入职信息待确认                       │  │
  │  └───────────────────────────────────────────┘  │
  ├─────────────────────────────────────────────────┤
  │  最近活动                                        │
  │  • 张三 - 高级前端工程师 - 面试通过             │
  │  • 李四 - 产品经理 - 已接受Offer                │
  │  • 王五 - 后端工程师 - HR筛选通过               │
  └─────────────────────────────────────────────────┘

  5.2 职位列表页（/jobs）

  ┌─────────────────────────────────────────────────┐
  └─────────────────────────────────────────────────┘

  5.2 职位列表页（/jobs）

  ┌─────────────────────────────────────────────────┐
  │  职位管理                                        │
  │  [+ 创建职位]  [筛选▼]  [搜索____________]      │
  ├─────────────────────────────────────────────────┤
  │  [全部状态▼] [全部类别▼] [全部部门▼] [☐加急]  │
  ├─────────────────────────────────────────────────┤
  │  ┌───────────────────────────────────────────┐  │
  │  │ 🔴 高级前端工程师 (加急)                  │  │
  │  │ 技术部 · 北京 · 社会招聘 · 高级           │  │
  │  │ 招聘中 · 2个名额 · 15人申请 · 5人面试中  │  │
  │  │ [查看详情] [查看简历] [编辑] [暂停]       │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 产品经理                                   │  │
  │  │ 产品部 · 上海 · 社会招聘 · 高级           │  │
  │  │ 招聘中 · 1个名额 · 8人申请 · 2人面试中   │  │
  │  │ [查看详情] [查看简历] [编辑] [暂停]       │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘

  5.3 简历管理页（/applications）

  ┌─────────────────────────────────────────────────┐
  │  简历管理                                        │
  │  [上传简历]  [批量操作▼]  [搜索____________]    │
  ├─────────────────────────────────────────────────┤
  │  [全部状态▼] [全部职位▼] [全部来源▼]          │
  ├─────────────────────────────────────────────────┤
  │  ☐ 全选  [查看简历] [推送面试官] [淘汰]        │
  ├─────────────────────────────────────────────────┤
  │  ┌───────────────────────────────────────────┐  │
  │  │ ☐ 张伟 - 高级前端工程师                   │  │
  │  │    5年经验 · 字节跳动 · Python/Go         │  │
  │  │    HR待查看 · 2小时前投递                 │  │
  │  │    [查看详情] [通过] [淘汰]               │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ ☐ 李娜 - 产品经理                         │  │
  │  │    3年经验 · 腾讯 · B端产品               │  │
  │  │    面试官筛选通过 · 1天前                 │  │
  │  │    [查看详情] [安排面试]                  │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘

  5.4 简历详情页（/applications/{id}）

  ┌─────────────────────────────────────────────────┐
  │  ← 返回  张伟 - 高级前端工程师                  │
  │  [推送面试官] [安排面试] [淘汰] [更多▼]        │
  ├─────────────────────────────────────────────────┤
  │  [基本信息] [简历] [面试] [评价] [时间线]      │
  ├─────────────────────────────────────────────────┤
  │  基本信息                                        │
  │  姓名: 张伟                                      │
  │  电话: 138-1234-5678                            │
  │  邮箱: zhangwei@email.com                       │
  │  当前公司: 字节跳动                             │
  │  当前职位: 高级前端工程师                       │
  │  工作年限: 5年                                   │
  │  期望薪资: 30-50万                              │
  │                                                  │
  │  应聘信息                                        │
  │  应聘职位: 高级前端工程师                       │
  │  当前状态: HR待查看                             │
  │  投递时间: 2026-05-30 10:00                     │
  │  简历来源: 主动投递                             │
  │  负责HR: 李HR                                   │
  │                                                  │
  │  技能标签                                        │
  │  [React] [TypeScript] [Next.js] [Node.js]      │
  │                                                  │
  │  操作记录                                        │
  │  • 2026-05-30 10:00 - 简历投递                 │
  │  • 2026-05-30 10:30 - HR查看简历               │
  └─────────────────────────────────────────────────┘

  5.5 面试管理页（/interviews）

  ┌─────────────────────────────────────────────────┐
  │  面试管理                                        │
  │  [安排面试]  [批量通知]  [搜索____________]     │
  ├─────────────────────────────────────────────────┤
  │  [今天] [本周] [全部] [待评价]                  │
  ├─────────────────────────────────────────────────┤
  │  今天的面试 (3场)                               │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 10:00 - 11:00                             │  │
  │  │ 张伟 - 高级前端工程师 - 初试             │  │
  │  │ 面试官: 王经理                            │  │
  │  │ 地点: 会议室A / 线上会议                 │  │
  │  │ 状态: 候选人已确认                        │  │
  │  │ [查看详情] [改期] [取消] [催促反馈]      │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 14:00 - 15:00                             │  │
  │  │ 李娜 - 产品经理 - 复试                   │  │
  │  │ 面试官: 张总监                            │  │
  │  │ 地点: 会议室B                            │  │
  │  │ 状态: 待候选人确认                        │  │
  │  │ [查看详情] [改期] [取消] [催促答复]      │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘

  5.6 Offer管理页（/offers）

  ┌─────────────────────────────────────────────────┐
  │  Offer管理                                       │
  │  [待发Offer] [已发Offer] [已接受] [已拒绝]     │
  ├─────────────────────────────────────────────────┤
  │  待发Offer (5个)                                │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 张伟 - 高级前端工程师                     │  │
  │  │ 审批状态: 已通过                          │  │
  │  │ 薪资: 40万/年                             │  │
  │  │ 期望入职: 2026-07-01                      │  │
  │  │ [...] [发起审批] [编辑] [发送Offer]      │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 李娜 - 产品经理                           │  │
  │  │ 审批状态: 审批中 (招聘组长)              │  │
  │  │ 薪资: 35万/年                             │  │
  │  │ 期望入职: 2026-07-15                      │  │
  │  │ [...] [查看审批进度]                      │  │
  │  └───────────────────────────────────────────┘  │
  │                                                  │
  │  已发Offer (3个)                                │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 王强 - 后端工程师                         │  │
  │  │ 发送时间: 2026-05-28                      │  │
  │  │ 有效期至: 2026-06-04                      │  │
  │  │ 状态: 待候选人答复                        │  │
  │  │ [...] [催促答复] [撤回]                   │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘
  
  5.7 入职管理页（/onboardings）

  ┌─────────────────────────────────────────────────┐
  │  入职管理                                        │
  │  [全部待入职] [本周入职] [本月入职]            │
  ├─────────────────────────────────────────────────┤
  │  全部待入职 (8人)                               │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 张伟 - 高级前端工程师                     │  │
  │  │ 入职日期: 2026-07-01                      │  │
  │  │ 部门: 技术部                              │  │
  │  │ 状态: 信息已采集 ✓                       │  │
  │  │ [...] [查看详情] [改期] [取消入职]       │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 李娜 - 产品经理                           │  │
  │  │ 入职日期: 2026-07-15                      │  │
  │  │ 部门: 产品部                              │  │
  │  │ 状态: 待采集信息                          │  │
  │  │ [...] [通知采集信息] [改期] [取消入职]   │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘
  
  5.8 面试官Dashboard（/dashboard/interviewer）

  ┌─────────────────────────────────────────────────┐
  │  DeepHire                          [通知🔔2] [王]│
  ├─────────────────────────────────────────────────┤
  │  今天的面试                                      │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 10:00 - 11:00                             │  │
  │  │ 张伟 - 高级前端工程师                     │  │
  │  │ 会议室A                                   │  │
  │  │ [查看简历] [填写评价]                     │  │
  │  └───────────────────────────────────────────┘  │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 14:00 - 15:00                             │  │
  │  │ 李娜 - 产品经理                           │  │
  │  │ 会议室B                                   │  │
  │  │ [查看简历] [填写评价]                     │  │
  │  └───────────────────────────────────────────┘  │
  ├─────────────────────────────────────────────────┤
  │  待筛选简历 (3份)                               │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 王强 - 后端工程师                         │  │
  │  │ 5年经验 · 阿里巴巴 · Java/Spring         │  │
  │  │ [查看详情] [通过] [淘汰]                  │  │
  │  └───────────────────────────────────────────┘  │
  ├─────────────────────────────────────────────────┤
  │  待填写评价 (1个)                               │
  │  ┌───────────────────────────────────────────┐  │
  │  │ 赵六 - 前端工程师 - 昨天面试             │  │
  │  │ [填写评价]                                │  │
  │  └───────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────┘

  ---
  六、通知消息设计

  6.1 HR收到的通知类型
  
  ┌─────────────────┬────────────────────┬────────────────────────────────────┐
  │    通知类型     │      触发条件      │              通知内容              │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 新简历投递      │ 候选人投递简历     │ "张伟投递了「高级前端工程师」职位" │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 面试官筛选完成  │ 面试官完成简历筛选 │ "王经理完成了张伟的简历筛选：通过" │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 面试评价完成    │ 面试官完成面试评价 │ "王经理完成了张伟的面试评价：通过" │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 候选人确认面试  │ 候选人确认参加面试 │ "张伟确认参加明天10:00的面试"      │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 候选人拒绝面试  │ 候选人拒绝面试     │ "张伟拒绝了面试邀请"               │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ Offer审批完成   │ Offer审批通过/拒绝 │ "张伟的Offer审批已通过"            │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 候选人接受Offer │ 候选人接受Offer    │ "张伟接受了Offer"                  │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 候选人拒绝Offer │ 候选人拒绝Offer    │ "张伟拒绝了Offer"                  │
  ├─────────────────┼────────────────────┼────────────────────────────────────┤
  │ 入职信息已采集  │ 候选人完成信息采集 │ "张伟已完成入职信息采集"           │
  └─────────────────┴────────────────────┴────────────────────────────────────┘

  6.2 面试官收到的通知类型

  ┌──────────────┬────────────────┬──────────────────────────────────────┐
  │   通知类型   │    触发条件    │               通知内容               │
  ├──────────────┼────────────────┼──────────────────────────────────────┤
  │ 新简历待筛选 │ HR推送简历     │ "李HR推送了张伟的简历，请查看"       │
  ├──────────────┼────────────────┼──────────────────────────────────────┤
  │ 面试安排     │ HR安排面试     │ "明天10:00面试张伟 - 高级前端工程师" │
  ├──────────────┼────────────────┼──────────────────────────────────────┤
  │ 面试改期     │ HR修改面试时间 │ "张伟的面试改期至明天14:00"          │
  ├──────────────┼────────────────┼──────────────────────────────────────┤
  │ 面试取消     │ HR取消面试     │ "张伟的面试已取消"                   │
  ├──────────────┼────────────────┼──────────────────────────────────────┤
  │ 催促反馈     │ HR催促填写评价 │ "请尽快完成张伟的面试评价"           │
  └──────────────┴────────────────┴──────────────────────────────────────┘

  6.3 候选人收到的通知类型（邮件）

  ┌──────────────┬─────────────┬──────────────────────────────────┐
  │   通知类型   │  触发条件   │             邮件内容             │
  ├──────────────┼─────────────┼──────────────────────────────────┤
  │ 面试邀请     │ HR安排面试  │ 面试时间、地点、面试官、注意事项 │
  ├──────────────┼─────────────┼──────────────────────────────────┤
  │ 面试改期     │ HR修改面试  │ 新的面试时间和地点               │
  ├──────────────┼─────────────┼──────────────────────────────────┤
  │ 面试取消     │ HR取消面试  │ 取消原因和后续安排               │
  ├──────────────┼─────────────┼──────────────────────────────────┤
  │ Offer邮件    │ HR发送Offer │ Offer详情、接受/拒绝链接         │
  ├──────────────┼─────────────┼──────────────────────────────────┤
  │ 入职信息采集 │ HR发送通知  │ 信息采集表单链接                 │
  └──────────────┴─────────────┴──────────────────────────────────┘

  ---
  七、待确认清单
  
  🔶 复杂功能待确认

  1. Offer审批流程
  
  - 问题：审批链是固定的还是可配置的？
  - 当前设计：固定5级审批（招聘HR → 招聘组长 → 招聘部负责人 → HRD → HRD负责人）
  - 建议：Phase 1使用固定审批链，Phase 2支持可配置

  2. 智能外呼功能

  - 问题：是否需要集成第三方智能外呼服务？
  - 当前设计：预留接口，暂不实现
  - 建议：Phase 1仅支持人工联系，Phase 2集成智能外呼

  3. 简历查重逻辑

  - 问题：查重的精确度要求？
  - 当前设计：
    - 同一候选人（email/phone匹配）+ 同一职位 = 重复
    - 同一候选人在其他职位的有效流程中 = 提示但允许投递
  - 建议：需要确认是否允许同一候选人同时应聘多个职位

  4. 简历锁定机制

  - 问题：简历锁定的具体规则？
  - 当前设计：简历进入"HR筛选通过"及之后的状态自动锁定
  - 建议：需要确认锁定后其他HR是否完全不可见

  5. Offer薪资变动流程

  - 问题：是否真的需要删除旧Offer记录？
  - 当前设计：删除旧记录，重新创建
  - 建议：保留旧记录但标记为"已作废"，创建新版本

  6. 入职信息采集

  - 问题：采集哪些信息？是否需要表单设计器？
  - 当前设计：固定字段（身份证、银行卡、紧急联系人等）
  - 建议：Phase 1使用固定表单，Phase 2支持自定义

  7. 邮件发送

  - 问题：使用哪个邮件服务？
  - 当前设计：集成SMTP或第三方邮件服务（如SendGrid）
  - 建议：需要确认邮件服务商

  8. 权限控制粒度

  - 问题：部门负责人是否可以查看本部门的所有招聘数据？
  - 当前设计：仅HR和招聘负责人可以查看
  - 建议：需要确认部门负责人的权限范围

  9. 数据归档

  - 问题：已关闭的职位、已淘汰的候选人是否需要归档？
  - 当前设计：软删除，保留所有历史数据
  - 建议：需要确认数据保留策略

  10. 批量操作

  - 问题：哪些操作需要支持批量？
  - 当前设计：批量查看简历、批量淘汰、批量发送通知
  - 建议：需要确认批量操作的具体场景

  ---
  八、技术实现要点

  8.1 状态机实现
  
  使用状态机模式确保状态转换的合法性：
  
  class ApplicationStateMachine:
      """应聘状态机"""
  
      # 定义合法的状态转换
      TRANSITIONS = {
          ApplicationStatus.NEW: [
              ApplicationStatus.HR_SCREENING,
              ApplicationStatus.HR_REJECTED,
          ],
          ApplicationStatus.HR_SCREENING: [
              ApplicationStatus.SENT_TO_INTERVIEWER,
              ApplicationStatus.HR_REJECTED,
          ],
          ApplicationStatus.SENT_TO_INTERVIEWER: [
              ApplicationStatus.INTERVIEW_INTENTION,
              ApplicationStatus.INTERVIEWER_REJECTED,
          ],
          # ... 其他状态转换
      }
  
      @classmethod
      def can_transition(cls, from_status, to_status):
          """检查状态转换是否合法"""
          return to_status in cls.TRANSITIONS.get(from_status, [])
  
      @classmethod
      def transition(cls, application, to_status, operator, reason=None):
          """执行状态转换"""
          if not cls.can_transition(application.status, to_status):
              raise ValueError(f"不能从 {application.status} 转换到 {to_status}")

          # 记录历史
          history = ApplicationStatusHistory(
              application_id=application.id,
              from_status=application.status,
              to_status=to_status,
              operator_id=operator.id,
              operator_name=operator.name,
              reason=reason
          )

          # 更新状态
          application.status = to_status
          application.last_status_change_at = datetime.now()

          return history

  8.2 通知系统实现

  class NotificationService:
      """通知服务"""

      @staticmethod
      async def notify_hr_new_application(application):
          """通知HR有新简历"""
          notification = Notification(
              user_id=application.hr_id,
              type="new_application",
              title="新简历投递",
              content=f"{application.candidate.name}投递了「{application.job.title}」职位",
              link=f"/applications/{application.id}",
          )
          await notification.save()

          # 发送实时通知（WebSocket）
          await websocket_manager.send_to_user(
              application.hr_id,
              {"type": "notification", "data": notification.to_dict()}
          )

      @staticmethod
      async def send_interview_invitation_email(interview):
          """发送面试邀请邮件"""
          email_content = render_template(
              "interview_invitation.html",
              candidate=interview.candidate,
              interview=interview,
          )

          await email_service.send(
              to=interview.candidate.email,
              subject=f"面试邀请 - {interview.job.title}",
              html=email_content,
          )

  8.3 查重实现

  class DuplicateCheckService:
      """查重服务"""
  
      @staticmethod
      async def check_duplicate(candidate_id, job_id):
          """检查是否重复投递"""
          # 检查是否已投递该职位
          existing = await Application.query.filter_by(
              candidate_id=candidate_id,
              job_id=job_id
          ).first()

          if existing:
              return {
                  "is_duplicate": True,
                  "reason": "已投递该职位",
                  "existing_application": existing
              }

          # 检查是否在其他职位的有效流程中
          active_applications = await Application.query.filter(
              Application.candidate_id == candidate_id,
              Application.status.notin_([
                  ApplicationStatus.HR_REJECTED,
                  ApplicationStatus.INTERVIEWER_REJECTED,
                  ApplicationStatus.INTERVIEW_FAILED,
                  ApplicationStatus.SALARY_REJECTED,
                  ApplicationStatus.OFFER_REJECTED,
                  ApplicationStatus.CANDIDATE_WITHDRAWN,
              ])
          ).all()

          if active_applications:
              return {
                  "is_duplicate": False,
                  "warning": "候选人在其他职位的流程中",
                  "active_applications": active_applications
              }

          return {"is_duplicate": False}
  
  ---
  九、数据库索引优化
  
  -- Application表索引
  CREATE INDEX idx_applications_candidate_job ON applications(candidate_id, job_id);
  CREATE INDEX idx_applications_status ON applications(status);
  CREATE INDEX idx_applications_hr_id ON applications(hr_id);
  CREATE INDEX idx_applications_applied_at ON applications(applied_at);

  -- Interview表索引
  CREATE INDEX idx_interviews_application_id ON interviews(application_id);
  CREATE INDEX idx_interviews_interviewer_id ON interviews(interviewer_id);
  CREATE INDEX idx_interviews_scheduled_at ON interviews(scheduled_at);
  CREATE INDEX idx_interviews_status ON interviews(status);

  -- Offer表索引
  CREATE INDEX idx_offers_application_id ON offers(application_id);
  CREATE INDEX idx_offers_status ON offers(status);
  CREATE INDEX idx_offers_approval_status ON offers(approval_status);
  
  -- Onboarding
---
  -- Onboarding表索引
  CREATE INDEX idx_onboardings_application_id ON onboardings(application_id);
  CREATE INDEX idx_onboardings_candidate_id ON onboardings(candidate_id);
  CREATE INDEX idx_onboardings_status ON onboardings(status);
  CREATE INDEX idx_onboardings_onboard_date ON onboardings(onboard_date);

  -- Job表索引
  CREATE INDEX idx_jobs_status ON jobs(status);
  CREATE INDEX idx_jobs_category ON jobs(category);
  CREATE INDEX idx_jobs_recruitment_type ON jobs(recruitment_type);
  CREATE INDEX idx_jobs_department_id ON jobs(department_id);
  CREATE INDEX idx_jobs_is_urgent ON jobs(is_urgent);
  CREATE INDEX idx_jobs_valid_until ON jobs(valid_until);
  
  -- Department表索引
  CREATE INDEX idx_departments_parent_id ON departments(parent_id);
  CREATE INDEX idx_departments_manager_id ON departments(manager_id);
  CREATE INDEX idx_departments_is_active ON departments(is_active);

  -- 复合索引（提升查询性能）
  CREATE INDEX idx_applications_status_hr ON applications(status, hr_id);
  CREATE INDEX idx_interviews_interviewer_scheduled ON interviews(interviewer_id, scheduled_at);
  CREATE INDEX idx_jobs_status_category ON jobs(status, category);

  ---
  十、前端状态管理设计

  10.1 全局状态（使用Zustand）
  
  // stores/useApplicationStore.ts
  interface ApplicationStore {
    // 状态
    applications: Application[];
    currentApplication: Application | null;
    filters: ApplicationFilters;
  
    // 操作
    fetchApplications: (filters?: ApplicationFilters) => Promise<void>;
    fetchApplicationById: (id: string) => Promise<void>;
    updateApplicationStatus: (id: string, status: ApplicationStatus, reason?: string) => Promise<void>;
    pushToInterviewer: (id: string, interviewerId: string) => Promise<void>;
    rejectApplication: (id: string, reason: string) => Promise<void>;
    undoLastAction: (id: string) => Promise<void>;
  }

  // stores/useInterviewStore.ts
  interface InterviewStore {
    interviews: Interview[];
    myInterviews: Interview[];

    scheduleInterview: (data: ScheduleInterviewData) => Promise<void>;
    rescheduleInterview: (id: string, newTime: Date) => Promise<void>;
    cancelInterview: (id: string, reason: string) => Promise<void>;
    submitFeedback: (id: string, feedback: InterviewFeedback) => Promise<void>;
    confirmInterview: (id: string) => Promise<void>;
    declineInterview: (id: string, reason: string) => Promise<void>;
  }

  // stores/useOfferStore.ts
  interface OfferStore {
    offers: Offer[];
    pendingOffers: Offer[];
    sentOffers: Offer[];
  
    createOffer: (data: CreateOfferData) => Promise<void>;
    submitForApproval: (id: string) => Promise<void>;
    editOffer: (id: string, data: EditOfferData) => Promise<void>;
    sendOffer: (id: string) => Promise<void>;
    generateOfferLetter: (id: string, template: string) => Promise<string>;
  }

  // stores/useNotificationStore.ts
  interface NotificationStore {
    notifications: Notification[];
    unreadCount: number;
  
    fetchNotifications: () => Promise<void>;
    markAsRead: (id: string) => Promise<void>;
    markAllAsRead: () => Promise<void>;
  }

  10.2 WebSocket实时通知

  // lib/websocket.ts
  class WebSocketManager {
    private ws: WebSocket | null = null;
  
    connect(userId: string) {
      this.ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'notification':
            // 更新通知状态
            useNotificationStore.getState().addNotification(data.data);
            // 显示Toast提示
            toast.info(data.data.title);
            break;

          case 'application_status_changed':
            // 更新应聘记录状态
            useApplicationStore.getState().updateApplicationInList(data.data);
            break;
  
          case 'interview_scheduled':
            // 更新面试列表
            useInterviewStore.getState().addInterview(data.data);
            break;
        }
      };
    }

    disconnect() {
      this.ws?.close();
    }
  }
  
  ---
  十一、关键组件设计
  
  11.1 状态流转组件

  // components/StatusFlow.tsx
  interface StatusFlowProps {
    currentStatus: ApplicationStatus;
    onStatusChange: (newStatus: ApplicationStatus, reason?: string) => void;
  }

  export function StatusFlow({ currentStatus, onStatusChange }: StatusFlowProps) {
    const availableActions = getAvailableActions(currentStatus);

    return (
      <div className="flex gap-2">
        {availableActions.map(action => (
          <Button
            key={action.status}
            variant={action.variant}
            onClick={() => handleAction(action)}
          >
            {action.label}
          </Button>
        ))}
      </div>
    );
  }

  function getAvailableActions(status: ApplicationStatus) {
    const actionsMap = {
      [ApplicationStatus.NEW]: [
        { status: ApplicationStatus.HR_SCREENING, label: '开始筛选', variant: 'default' },
        { status: ApplicationStatus.HR_REJECTED, label: '淘汰', variant: 'destructive' },
      ],
      [ApplicationStatus.HR_SCREENING]: [
        { status: ApplicationStatus.SENT_TO_INTERVIEWER, label: '推送面试官', variant: 'default' },
        { status: ApplicationStatus.HR_REJECTED, label: '淘汰', variant: 'destructive' },
      ],
      // ... 其他状态的可用操作
    };
  
    return actionsMap[status] || [];
  }

  11.2 时间线组件

  // components/Timeline.tsx
  interface TimelineProps {
    applicationId: string;
  }

  export function Timeline({ applicationId }: TimelineProps) {
    const { data: history } = useQuery({
      queryKey: ['application-history', applicationId],
      queryFn: () => fetchApplicationHistory(applicationId),
    });

    return (
      <div className="space-y-4">
        {history?.map(event => (
          <div key={event.id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className={cn(
                "w-3 h-3 rounded-full",
                getStatusColor(event.to_status)
              )} />
              {!event.isLast && <div className="w-0.5 h-full bg-gray-200" />}
            </div>
  
            <div className="flex-1 pb-4">
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {getStatusLabel(event.to_status)}
                </span>
                <span className="text-sm text-gray-500">
                  {formatDate(event.created_at)}
                </span>
              </div>

              {event.reason && (
                <p className="text-sm text-gray-600 mt-1">{event.reason}</p>
              )}
  
              <p className="text-xs text-gray-400 mt-1">
                操作人: {event.operator_name}
              </p>
            </div>
          </div>
        ))}
      </div>
    );
  }

  11.3 面试安排对话框

  // components/ScheduleInterviewDialog.tsx
  interface ScheduleInterviewDialogProps {
    applicationId: string;
    open: boolean;
    onClose: () => void;
  }

  export function ScheduleInterviewDialog({
    applicationId,
    open,
    onClose
  }: ScheduleInterviewDialogProps) {
    const form = useForm<ScheduleInterviewForm>({
      defaultValues: {
        round: 'first',
        interviewerId: '',
        scorecardTemplateId: '',
        scheduledAt: new Date(),
        duration: 60,
        location: '',
      }
    });

    const onSubmit = async (data: ScheduleInterviewForm) => {
      await scheduleInterview({
        applicationId,
        ...data,
      });

      toast.success('面试安排成功');
      onClose();
    };

    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>安排面试</DialogTitle>
          </DialogHeader>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="round"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>面试轮次</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="first">初试</SelectItem>
                        <SelectItem value="second">复试</SelectItem>
                        <SelectItem value="final">终试</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="interviewerId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>面试官</FormLabel>
                    <UserSelect
                      value={field.value}
                      onChange={field.onChange}
                      role="interviewer"
                    />
                  </FormItem>
                )}
              />
  
              <FormField
                control={form.control}
                name="scorecardTemplateId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>评价表模板</FormLabel>
                    <ScorecardTemplateSelect
                      value={field.value}
                      onChange={field.onChange}
                      round={form.watch('round')}
                    />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="scheduledAt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>面试时间</FormLabel>
                    <DateTimePicker
                      value={field.value}
                      onChange={field.onChange}
                    />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="location"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>面试地点</FormLabel>
                    <Input {...field} placeholder="会议室A 或 线上会议链接" />
                  </FormItem>
                )}
              />

              <DialogFooter>
                <Button type="button" variant="outline" onClick={onClose}>
                  取消
                </Button>
                <Button type="submit">
                  确认安排
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    );
  }

  ---
  十二、邮件模板设计

  12.1 面试邀请邮件
  
  <!-- templates/interview_invitation.html -->
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <title>面试邀请</title>
  </head>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2>面试邀请</h2>

      <p>尊敬的 {{ candidate.name }}，</p>

      <p>感谢您应聘我们公司的 <strong>{{ job.title }}</strong> 职位。</p>

      <p>经过初步筛选，我们诚挚邀请您参加面试，具体安排如下：</p>

      <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>面试时间：</strong>{{ interview.scheduled_at | format_datetime }}</p>
        <p><strong>面试地点：</strong>{{ interview.location }}</p>
        <p><strong>面试官：</strong>{{ interview.interviewer_name }}</p>
        <p><strong>面试时长：</strong>约 {{ interview.duration }} 分钟</p>
      </div>

      <p>请点击以下链接确认您的参加意向：</p>

      <div style="margin: 30px 0; text-align: center;">
        <a href="{{ confirm_url }}" 
           style="display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; 
  border-radius: 5px; margin-right: 10px;">
          确认参加
        </a>
        <a href="{{ decline_url }}" 
           style="display: inline-block; padding: 12px 30px; background: #f44336; color: white; text-decoration: none; 
  border-radius: 5px;">
          无法参加
        </a>
      </div>
  
      <p>如有任何问题，请联系我们：</p>
      <p>HR联系人：{{ hr.name }}<br>
         联系电话：{{ hr.phone }}<br>
         邮箱：{{ hr.email }}</p>
  
      <p>期待与您见面！</p>

      <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

      <p style="font-size: 12px; color: #999;">
        此邮件由 DeepHire 招聘系统自动发送，请勿直接回复。
      </p>
    </div>
  </body>
  </html>

  12.2 Offer邮件
  
  <!-- templates/offer_email.html -->
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <title>Offer通知</title>
  </head>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2>🎉 Offer通知</h2>
  
      <p>尊敬的 {{ candidate.name }}，</p>

      <p>恭喜您！经过我们的综合评估，我们非常高兴地向您发出 <strong>{{ offer.hiring_position }}</strong>
  职位的录用通知。</p>
  
      <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>录用公司：</strong>{{ offer.hiring_company }}</p>
        <p><strong>录用部门：</strong>{{ offer.department.name }}</p>
        <p><strong>职位：</strong>{{ offer.hiring_position }}</p>
        <p><strong>职级：</strong>{{ offer.hiring_level }}</p>
        <p><strong>工作地点：</strong>{{ offer.work_location }}</p>
        <p><strong>期望入职日期：</strong>{{ offer.expected_onboard_date | format_date }}</p>
      </div>

      <p>详细的Offer信息请查看附件。</p>

      <p>请在 <strong>{{ offer.valid_until | format_date }}</strong> 前确认您的接受意向：</p>

      <div style="margin: 30px 0; text-align: center;">
        <a href="{{ accept_url }}" 
           style="display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; 
  border-radius: 5px; margin-right: 10px;">
          接受Offer
        </a>
        <a href="{{ reject_url }}" 
           style="display: inline-block; padding: 12px 30px; background: #f44336; color: white; text-decoration: none; 
  border-radius: 5px;">
          拒绝Offer
        </a>
      </div>
  
      <p>如有任何疑问，请随时联系我们：</p>
      <p>HR联系人：{{ hr.name }}<br>
         联系电话：{{ hr.phone }}<br>
         邮箱：{{ hr.email }}</p>
  
      <p>我们期待您的加入！</p>

      <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

      <p style="font-size: 12px; color: #999;">
        此邮件由 DeepHire 招聘系统自动发送，请勿直接回复。
      </p>
    </div>
  </body>
  </html>
  
  12.3 入职信息采集邮件
  
  <!-- templates/onboarding_info_collection.html -->
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <title>入职信息采集</title>
  </head>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2>入职信息采集</h2>
  
      <p>尊敬的 {{ candidate.name }}，</p>

      <p>欢迎加入我们！为了顺利办理入职手续，请您填写以下信息。</p>

      <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p><strong>入职日期：</strong>{{ onboarding.onboard_date | format_date }}</p>
        <p><strong>入职部门：</strong>{{ onboarding.department.name }}</p>
        <p><strong>工作地点：</strong>{{ onboarding.work_location }}</p>
      </div>

      <p>请点击以下链接填写入职信息：</p>

      <div style="margin: 30px 0; text-align: center;">
        <a href="{{ info_collection_url }}" 
           style="display: inline-block; padding: 12px 30px; background: #2196F3; color: white; text-decoration: none; 
  border-radius: 5px;">
          填写入职信息
        </a>
      </div>
  
      <p><strong>需要准备的材料：</strong></p>
      <ul>
        <li>身份证正反面照片</li>
        <li>学历学位证书</li>
        <li>银行卡信息</li>
        <li>紧急联系人信息</li>
        <li>体检报告（入职前完成）</li>
      </ul>

      <p>请在入职前3天完成信息填写。</p>

      <p>如有任何问题，请联系：</p>
      <p>HR对接人：{{ hr.name }}<br>
         联系电话：{{ hr.phone }}<br>
         邮箱：{{ hr.email }}</p>
  
      <p>期待您的到来！</p>

      <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">

      <p style="font-size: 12px; color: #999;">
        此邮件由 DeepHire 招聘系统自动发送，请勿直接回复。
      </p>
    </div>
  </body>
  </html>

  ---
  十三、实施计划

  Phase 1: 基础模块（2周）
  
  Week 1: 职位 + 简历管理
  - Day 1-2: 完善数据模型，创建数据库迁移
  - Day 3-4: 实现职位模块API和前端
  - Day 5-7: 实现简历管理模块API和前端
  
  Week 2: 面试管理
  - Day 1-3: 实现面试管理API和前端
  - Day 4-5: 实现评价表系统
  - Day 6-7: 集成邮件通知

  Phase 2: Offer + 入职（1周）
  
  Week 3: Offer + 入职管理
  - Day 1-3: 实现Offer管理（含审批流程）
  - Day 4-5: 实现入职管理
  - Day 6-7: 端到端测试
  
  Phase 3: 优化和部署（1周）
  
  Week 4: 优化
  - Day 1-2: 性能优化
  - Day 3-4: UI/UX优化
  - Day 5: 安全加固
  - Day 6-7: 生产部署

  ---
  十四、总结

  核心设计要点
  
  1. 统一的状态机：Application表作为核心，管理候选人全生命周期
  2. 清晰的数据流转：职位 → 简历 → 面试 → Offer → 入职
  3. 完善的通知系统：实时通知 + 邮件通知
  4. 灵活的权限控制：HR、Recruiter、Interviewer不同视角
  5. 可追溯的历史记录：所有状态变更都有历史记录

  技术亮点

  1. 状态机模式：确保状态转换的合法性
  2. WebSocket实时通知：提升用户体验
  3. 邮件模板系统：统一的邮件发送
  4. 查重机制：避免重复投递
  5. 审批流程：支持多级审批