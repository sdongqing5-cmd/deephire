#` DeepHire 招聘系统 - 设计方案 v2（完整修正版）

## 📋 修正说明

**v2版本修正内容**：
1. ✅ 新增"面试意向沟通"环节（智能外呼/人工联系）
2. ✅ 新增"等待确认面试时间"环节（邮件确认）
3. ✅ 所有面试环节区分"进行中"和"已完成"状态
4. ✅ 新增面试官简历筛选记录表
5. ✅ 修正HR初筛面试的位置（固定在推送面试官之前）
6. ✅ 完善面试意向沟通的数据模型

**用户确认的关键决策**：
- HR复试位置：部门面试后，再安排一轮HR面试
- 面试官筛选简历：需要填写简单的筛选意见
- 面试意向沟通：支持智能外呼和人工联系两种，HR自己选择
- 候选人同意面试后：发送邮件/短信，候选人在线确认面试时间

---

## 一、完整状态机设计

### 1.1 ApplicationStatus（应聘状态）- 最终版

```python
class ApplicationStatus(str, enum.Enum):
    """应聘状态 - 完整生命周期"""
    
    # 简历阶段
    NEW = "new"                                    # 新简历
    HR_SCREENING = "hr_screening"                  # HR筛选中（含电话沟通确认意向）
    HR_REJECTED = "hr_rejected"                    # HR淘汰
    
    # HR初筛面试阶段
    HR_INTERVIEW_SCHEDULED = "hr_interview_scheduled"      # HR面试已安排
    HR_INTERVIEW_COMPLETED = "hr_interview_completed"      # HR面试已完成（已填写评价表）
    HR_INTERVIEW_REJECTED = "hr_interview_rejected"        # HR面试淘汰
    
    # 面试官筛选阶段
    SENT_TO_INTERVIEWER = "sent_to_interviewer"           # 推送给面试官（面试官筛选简历）
    INTERVIEWER_REJECTED = "interviewer_rejected"          # 面试官淘汰
    
    # 面试意向沟通阶段
    INTERVIEW_INTENTION_COMMUNICATION = "interview_intention_communication"  # 面试意向沟通中
    CANDIDATE_DECLINED_INTERVIEW = "candidate_declined_interview"            # 候选人放弃面试
    
    # 面试时间确认阶段
    INTERVIEW_TIME_CONFIRMING = "interview_time_confirming"  # 等待候选人确认面试时间
    
    # 部门面试阶段
    DEPARTMENT_INTERVIEW_SCHEDULED = "department_interview_scheduled"  # 部门面试已安排
    DEPARTMENT_INTERVIEWING = "department_interviewing"                # 部门面试中
    DEPARTMENT_INTERVIEW_COMPLETED = "department_interview_completed"  # 部门面试已完成
    DEPARTMENT_INTERVIEW_REJECTED = "department_interview_rejected"    # 部门面试淘汰
    
    # 测评阶段（可选）
    ASSESSMENT_INVITED = "assessment_invited"              # 测评邀请已发送
    ASSESSMENT_IN_PROGRESS = "assessment_in_progress"      # 测评进行中
    ASSESSMENT_COMPLETED = "assessment_completed"          # 测评已完成
    ASSESSMENT_FAILED = "assessment_failed"                # 测评未通过
    
    # HR复试阶段（可选）
    HR_REINTERVIEW_SCHEDULED = "hr_reinterview_scheduled"  # HR复试已安排
    HR_REINTERVIEW_COMPLETED = "hr_reinterview_completed"  # HR复试已完成
    HR_REINTERVIEW_REJECTED = "hr_reinterview_rejected"    # HR复试淘汰
    
    # 终面阶段
    FINAL_INTERVIEW_SCHEDULED = "final_interview_scheduled"  # 终面已安排
    FINAL_INTERVIEWING = "final_interviewing"                # 终面中
    FINAL_INTERVIEW_COMPLETED = "final_interview_completed"  # 终面已完成
    FINAL_INTERVIEW_REJECTED = "final_interview_rejected"    # 终面淘汰
    
    # Offer阶段
    SALARY_NEGOTIATION = "salary_negotiation"              # 谈薪中
    SALARY_REJECTED = "salary_rejected"                    # 谈薪失败
    VERBAL_OFFER_ACCEPTED = "verbal_offer_accepted"        # 接受口头Offer
    OFFER_APPROVAL = "offer_approval"                      # Offer审批中
    OFFER_APPROVAL_REJECTED = "offer_approval_rejected"    # Offer审批拒绝
    OFFER_PENDING = "offer_pending"                        # 待发Offer
    OFFER_SENT = "offer_sent"                              # 已发Offer
    OFFER_REJECTED = "offer_rejected"                      # 已拒绝Offer
    OFFER_ACCEPTED = "offer_accepted"                      # 已接受Offer
    
    # 入职阶段
    PENDING_ONBOARD = "pending_onboard"                    # 待入职
    ONBOARD_CANCELLED = "onboard_cancelled"                # 取消入职
    ONBOARDED = "onboarded"                                # 已入职
    
    # 其他
    CANDIDATE_WITHDRAWN = "candidate_withdrawn"            # 候选人主动退出
```

---

## 二、完整状态流转图

详见附录A（由于流转图过长，放在文档末尾）

---

## 三、数据模型设计

### 3.1 Application（应聘记录）- 新增字段

```python
class Application(Base):
    """应聘记录"""
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
    
    # 锁定信息
    is_locked = Column(Boolean, default=False, index=True)
    locked_by = Column(String, ForeignKey("users.id"))
    locked_at = Column(DateTime(timezone=True))
    
    # 应聘次数统计
    application_count = Column(Integer, default=1)
    
    # 🆕 面试意向沟通
    intention_contact_method = Column(String)  # ai_call, manual
    intention_contact_result = Column(String)  # agreed, declined, no_answer
    intention_contact_notes = Column(Text)
    intention_contacted_at = Column(DateTime(timezone=True))
    
    # 🆕 面试时间确认
    interview_notification_sent_at = Column(DateTime(timezone=True))
    interview_confirmed_at = Column(DateTime(timezone=True))
    
    # 面试流程配置
    interview_flow_config = Column(Text)  # JSON格式
    
    # 时间戳
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    hr_viewed_at = Column(DateTime(timezone=True))
    last_status_change_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 3.2 InterviewerScreening（面试官简历筛选）- 新增表

```python
class InterviewerScreening(Base):
    """面试官简历筛选记录"""
    __tablename__ = "interviewer_screenings"
    
    id = Column(String, primary_key=True, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    interviewer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    interviewer_name = Column(String)
    
    # 筛选结果
    result = Column(String, nullable=False)  # pass, reject
    comments = Column(Text)  # 筛选意见
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 四、关键业务流程

### 4.1 完整招聘流程（按功能列表第109行）

```
1. 新建职位
2. 导入简历并进行查重/查相似
3. 若无重复，则HR与人选进行电话沟通确认意向
4. HR给自己安排面试，选择并填写《HR初筛评价表》
5. 安排用人部门进行简历筛选
6. 安排部门面试，部门在完成面试后填写《用人部门面试评价表》
7. 邀请测评（可选）
8. 测评通过后，安排终面官面
9. 谈薪成功的，转移到"接受口头offer"
10. 进入"offer"管理模块，进行线上offer审批
11. offer编辑
12. 发送offer
13. 到已接受offer后，进入"入职管理"模块，发送"通知信息采集"
```

### 4.2 面试意向沟通流程

```python
# 详细实现代码见后续章节
```

---

## 五、API接口设计

### 5.1 面试意向沟通相关

```
POST   /api/v1/applications/{id}/initiate-intention-contact    # 发起面试意向沟通
POST   /api/v1/applications/{id}/record-intention-result       # 记录沟通结果
POST   /api/v1/applications/{id}/intention-callback            # 智能外呼回调
```

### 5.2 面试时间确认相关

```
POST   /api/v1/applications/{id}/send-interview-confirmation   # 发送面试确认邮件
POST   /api/v1/interviews/confirm/{token}                      # 候选人确认面试
POST   /api/v1/interviews/decline/{token}                      # 候选人拒绝面试
```

### 5.3 面试官筛选相关

```
POST   /api/v1/interviewer-screenings                          # 提交筛选结果
GET    /api/v1/interviewer-screenings/my-pending               # 获取我的待筛选简历
GET    /api/v1/interviewer-screenings/{id}                     # 获取筛选详情
```

---

## 附录A：完整状态流转图

（流转图内容过长，建议使用Mermaid或其他工具可视化）

---

## 待补充章节

- 详细业务流程代码实现
- 前端页面设计
- 数据库迁移脚本
- 测试用例

**文档创建时间**：2026-05-30
**版本**：v2.0
**状态**：框架已完成，详细内容待补充
