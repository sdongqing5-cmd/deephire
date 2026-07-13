# DeepHire 招聘系统 - V2业务流程设计文档

## 📋 文档说明

本文档包含：
- 完整的业务流程设计
- 关键环节的详细逻辑
- Service层代码实现

---

## 一、完整招聘流程（基于功能列表第109行）

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

---

## 二、详细业务流程

### 2.1 简历投递和查重流程

```python
class ResumeService:
    """简历服务"""
    
    @staticmethod
    async def upload_resume(
        job_id: str,
        candidate_data: dict,
        resume_file: UploadFile,
        hr_id: str
    ) -> Application:
        """上传简历到职位"""
        
        # 1. 解析简历
        parsed_data = await ResumeParser.parse(resume_file)
        
        # 2. 创建或更新候选人
        candidate = await CandidateService.create_or_update(
            name=candidate_data.get('name') or parsed_data.get('name'),
            phone=candidate_data.get('phone') or parsed_data.get('phone'),
            email=candidate_data.get('email') or parsed_data.get('email'),
            parsed_data=parsed_data
        )
        
        # 3. 查重检查
        duplicate_check = await DuplicateCheckService.check(candidate.id, job_id)
        
        if duplicate_check['is_duplicate']:
            raise DuplicateApplicationError(
                f"候选人已投递该职位，上次投递时间：{duplicate_check['existing_application'].applied_at}"
            )
        
        if duplicate_check.get('warning'):
            # 有警告但允许投递，记录警告信息
            logger.warning(f"候选人在其他职位流程中：{duplicate_check['active_applications']}")
        
        # 4. 创建应聘记录
        application = Application(
            id=generate_id(),
            candidate_id=candidate.id,
            job_id=job_id,
            status=ApplicationStatus.NEW,
            resume_url=await FileService.upload(resume_file),
            resume_parsed_data=json.dumps(parsed_data),
            source=candidate_data.get('source', '主动投递'),
            hr_id=hr_id,
            applied_at=datetime.now()
        )
        await application.save()
        
        # 5. 通知HR
        await NotificationService.notify_hr_new_application(application)
        
        return application


class DuplicateCheckService:
    """查重服务"""
    
    @staticmethod
    async def check(candidate_id: str, job_id: str) -> dict:
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
        active_statuses = [
            ApplicationStatus.HR_SCREENING,
            ApplicationStatus.HR_INTERVIEW_SCHEDULED,
            ApplicationStatus.HR_INTERVIEWING,
            ApplicationStatus.HR_INTERVIEW_COMPLETED,
            ApplicationStatus.SENT_TO_INTERVIEWER,
            ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION,
            ApplicationStatus.INTERVIEW_TIME_CONFIRMING,
            ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED,
            ApplicationStatus.DEPARTMENT_INTERVIEWING,
            ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED,
            ApplicationStatus.ASSESSMENT_INVITED,
            ApplicationStatus.ASSESSMENT_IN_PROGRESS,
            ApplicationStatus.ASSESSMENT_COMPLETED,
            ApplicationStatus.HR_REINTERVIEW_SCHEDULED,
            ApplicationStatus.HR_REINTERVIEWING,
            ApplicationStatus.HR_REINTERVIEW_COMPLETED,
            ApplicationStatus.FINAL_INTERVIEW_SCHEDULED,
            ApplicationStatus.FINAL_INTERVIEWING,
            ApplicationStatus.FINAL_INTERVIEW_COMPLETED,
            ApplicationStatus.SALARY_NEGOTIATION,
            ApplicationStatus.VERBAL_OFFER_ACCEPTED,
            ApplicationStatus.OFFER_APPROVAL,
            ApplicationStatus.OFFER_PENDING,
            ApplicationStatus.OFFER_SENT,
            ApplicationStatus.OFFER_ACCEPTED,
            ApplicationStatus.PENDING_ONBOARD,
        ]
        
        active_applications = await Application.query.filter(
            Application.candidate_id == candidate_id,
            Application.status.in_(active_statuses)
        ).all()
        
        if active_applications:
            return {
                "is_duplicate": False,
                "warning": "候选人在其他职位的流程中",
                "active_applications": active_applications
            }
        
        return {"is_duplicate": False}
```

### 2.2 HR筛选流程（含电话沟通）

```python
class HRScreeningService:
    """HR筛选服务"""
    
    @staticmethod
    async def start_screening(application_id: str, hr_id: str) -> Application:
        """开始HR筛选"""
        application = await Application.get(application_id)
        
        # 更新查看时间
        application.hr_viewed_at = datetime.now()
        
        # 转换状态
        await ApplicationService.transition_status(
            application_id=application_id,
            to_status=ApplicationStatus.HR_SCREENING,
            operator_id=hr_id,
            reason="HR开始筛选"
        )
        
        return application
    
    @staticmethod
    async def phone_communication(
        application_id: str,
        hr_id: str,
        communication_result: str,
        notes: str = None
    ) -> Application:
        """电话沟通确认意向"""
        application = await Application.get(application_id)
        
        # 记录沟通信息
        application.intention_contact_method = "manual"
        application.intention_contact_result = communication_result
        application.intention_contact_notes = notes
        application.intention_contacted_at = datetime.now()
        application.intention_contacted_by = hr_id
        await application.save()
        
        if communication_result == "agreed":
            # 候选人同意，可以进入下一步
            return application
        elif communication_result == "declined":
            # 候选人拒绝
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.HR_REJECTED,
                operator_id=hr_id,
                reason="候选人电话沟通时表示不感兴趣"
            )
        
        return application
    
    @staticmethod
    async def reject(application_id: str, hr_id: str, reason: str) -> Application:
        """HR淘汰"""
        await ApplicationService.transition_status(
            application_id=application_id,
            to_status=ApplicationStatus.HR_REJECTED,
            operator_id=hr_id,
            reason=reason
        )
        
        application = await Application.get(application_id)
        return application
```

### 2.3 HR初筛面试流程

```python
class HRInterviewService:
    """HR初筛面试服务"""
    
    @staticmethod
    async def schedule_hr_interview(
        application_id: str,
        hr_id: str,
        scheduled_at: datetime,
        duration: int = 30,
        location: str = None,
        scorecard_template_id: str = None
    ) -> Interview:
        """HR给自己安排初筛面试"""
        
        # 1. 创建面试记录
        interview = Interview(
            id=generate_id(),
            application_id=application_id,
            job_id=(await Application.get(application_id)).job_id,
            candidate_id=(await Application.get(application_id)).candidate_id,
            interview_type=InterviewType.HR_INITIAL,
            title="HR初筛面试",
            interviewer_id=hr_id,
            interviewer_name=(await User.get(hr_id)).name,
            scorecard_template_id=scorecard_template_id,
            scheduled_at=scheduled_at,
            duration=duration,
            location=location,
            status=InterviewStatus.SCHEDULED
        )
        await interview.save()
        
        # 2. 转换应聘状态
        await ApplicationService.transition_status(
            application_id=application_id,
            to_status=ApplicationStatus.HR_INTERVIEW_SCHEDULED,
            operator_id=hr_id,
            reason="HR安排初筛面试"
        )
        
        # 3. 发送通知给候选人
        await EmailService.send_interview_invitation(interview)
        
        return interview
    
    @staticmethod
    async def start_interview(interview_id: str, hr_id: str) -> Interview:
        """开始HR初筛面试"""
        interview = await Interview.get(interview_id)
        interview.status = InterviewStatus.IN_PROGRESS
        await interview.save()
        
        # 更新应聘状态
        await ApplicationService.transition_status(
            application_id=interview.application_id,
            to_status=ApplicationStatus.HR_INTERVIEWING,
            operator_id=hr_id,
            reason="HR初筛面试开始"
        )
        
        return interview
    
    @staticmethod
    async def complete_interview(
        interview_id: str,
        hr_id: str,
        result: InterviewResult,
        feedback: str,
        score: int,
        evaluation_data: dict
    ) -> Interview:
        """完成HR初筛面试并填写评价表"""
        
        interview = await Interview.get(interview_id)
        
        # 1. 更新面试记录
        interview.status = InterviewStatus.COMPLETED
        interview.result = result
        interview.feedback = feedback
        interview.score = score
        interview.evaluation_data = json.dumps(evaluation_data)
        interview.completed_at = datetime.now()
        await interview.save()
        
        # 2. 更新应聘状态
        if result == InterviewResult.PASS:
            await ApplicationService.transition_status(
                application_id=interview.application_id,
                to_status=ApplicationStatus.HR_INTERVIEW_COMPLETED,
                operator_id=hr_id,
                reason="HR初筛面试通过"
            )
        else:
            await ApplicationService.transition_status(
                application_id=interview.application_id,
                to_status=ApplicationStatus.HR_INTERVIEW_REJECTED,
                operator_id=hr_id,
                reason="HR初筛面试未通过"
            )
        
        return interview
```

### 2.4 面试官筛选简历流程

```python
class InterviewerScreeningService:
    """面试官筛选简历服务"""
    
    @staticmethod
    async def push_to_interviewer(
        application_id: str,
        interviewer_id: str,
        hr_id: str
    ) -> Application:
        """推送简历给面试官筛选"""
        
        # 1. 转换应聘状态
        await ApplicationService.transition_status(
            application_id=application_id,
            to_status=ApplicationStatus.SENT_TO_INTERVIEWER,
            operator_id=hr_id,
            reason=f"推送给面试官筛选"
        )
        
        # 2. 通知面试官
        await NotificationService.notify_interviewer_new_resume(
            application_id=application_id,
            interviewer_id=interviewer_id
        )
        
        application = await Application.get(application_id)
        return application
    
    @staticmethod
    async def submit_screening_result(
        application_id: str,
        interviewer_id: str,
        result: str,  # "pass" or "reject"
        comments: str
    ) -> InterviewerScreening:
        """面试官提交筛选结果"""
        
        # 1. 创建筛选记录
        screening = InterviewerScreening(
            id=generate_id(),
            application_id=application_id,
            interviewer_id=interviewer_id,
            interviewer_name=(await User.get(interviewer_id)).name,
            result=result,
            comments=comments
        )
        await screening.save()
        
        # 2. 更新应聘状态
        if result == "pass":
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.INTERVIEW_INTENTION_COMMUNICATION,
                operator_id=interviewer_id,
                reason="面试官筛选通过"
            )
        else:
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.INTERVIEWER_REJECTED,
                operator_id=interviewer_id,
                reason=f"面试官筛选未通过：{comments}"
            )
        
        # 3. 通知HR
        await NotificationService.notify_hr_interviewer_screening_completed(
            application_id=application_id,
            result=result
        )
        
        return screening
```

### 2.5 面试意向沟通流程

```python
class InterviewIntentionService:
    """面试意向沟通服务"""
    
    @staticmethod
    async def initiate_contact(
        application_id: str,
        hr_id: str,
        contact_method: str  # "ai_call" or "manual"
    ) -> Application:
        """发起面试意向沟通"""
        
        application = await Application.get(application_id)
        
        if contact_method == "ai_call":
            # 调用智能外呼服务
            await AICallService.initiate_call(
                phone=application.candidate.phone,
                callback_url=f"/api/v1/applications/{application_id}/intention-callback"
            )
        
        # 记录沟通方式
        application.intention_contact_method = contact_method
        application.intention_contacted_at = datetime.now()
        application.intention_contacted_by = hr_id
        await application.save()
        
        return application
    
    @staticmethod
    async def record_contact_result(
        application_id: str,
        hr_id: str,
        result: str,  # "agreed", "declined", "no_answer"
        notes: str = None
    ) -> Application:
        """记录沟通结果"""
        
        application = await Application.get(application_id)
        application.intention_contact_result = result
        application.intention_contact_notes = notes
        await application.save()
        
        if result == "agreed":
            # 候选人同意面试，进入时间确认环节
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.INTERVIEW_TIME_CONFIRMING,
                operator_id=hr_id,
                reason="候选人同意面试"
            )
        elif result == "declined":
            # 候选人拒绝面试
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
                operator_id=hr_id,
                reason="候选人拒绝面试"
            )
        
        return application
    
    @staticmethod
    async def handle_ai_call_callback(
        application_id: str,
        call_result: dict
    ) -> Application:
        """处理智能外呼回调"""
        
        # 解析外呼结果
        result = call_result.get('result')  # "agreed", "declined", "no_answer"
        transcript = call_result.get('transcript')  # 通话记录
        
        application = await Application.get(application_id)
        application.intention_contact_result = result
        application.intention_contact_notes = f"智能外呼结果：{transcript}"
        await application.save()
        
        if result == "agreed":
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.INTERVIEW_TIME_CONFIRMING,
                operator_id="system",
                reason="候选人同意面试（智能外呼）"
            )
        elif result == "declined":
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
                operator_id="system",
                reason="候选人拒绝面试（智能外呼）"
            )
        
        return application
```

### 2.6 面试时间确认流程

```python
class InterviewConfirmationService:
    """面试时间确认服务"""
    
    @staticmethod
    async def send_confirmation_email(
        application_id: str,
        hr_id: str,
        interview_time_options: list[datetime]
    ) -> Application:
        """发送面试时间确认邮件"""
        
        application = await Application.get(application_id)
        
        # 生成确认token
        token = generate_token()
        application.interview_confirmation_token = token
        application.interview_notification_sent_at = datetime.now()
        await application.save()
        
        # 发送邮件
        await EmailService.send_interview_time_confirmation(
            application=application,
            time_options=interview_time_options,
            confirm_url=f"{settings.FRONTEND_URL}/interviews/confirm/{token}",
            decline_url=f"{settings.FRONTEND_URL}/interviews/decline/{token}"
        )
        
        return application
    
    @staticmethod
    async def candidate_confirm(
        token: str,
        selected_time: datetime
    ) -> Application:
        """候选人确认面试时间"""
        
        application = await Application.query.filter_by(
            interview_confirmation_token=token
        ).first()
        
        if not application:
            raise ValueError("无效的确认链接")
        
        # 记录确认时间
        application.interview_confirmed_at = datetime.now()
        await application.save()
        
        # 转换状态并创建面试记录
        await ApplicationService.transition_status(
            application_id=application.id,
            to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_SCHEDULED,
            operator_id="candidate",
            reason=f"候选人确认面试时间：{selected_time}"
        )
        
        # 创建部门面试记录
        await DepartmentInterviewService.create_interview(
            application_id=application.id,
            scheduled_at=selected_time
        )
        
        return application
    
    @staticmethod
    async def candidate_decline(token: str, reason: str = None) -> Application:
        """候选人拒绝面试"""
        
        application = await Application.query.filter_by(
            interview_confirmation_token=token
        ).first()
        
        if not application:
            raise ValueError("无效的确认链接")
        
        await ApplicationService.transition_status(
            application_id=application.id,
            to_status=ApplicationStatus.CANDIDATE_DECLINED_INTERVIEW,
            operator_id="candidate",
            reason=f"候选人拒绝面试：{reason}"
        )
        
        return application
```

### 2.7 部门面试流程

```python
class DepartmentInterviewService:
    """部门面试服务"""
    
    @staticmethod
    async def create_interview(
        application_id: str,
        scheduled_at: datetime,
        interviewer_id: str = None,
        duration: int = 60,
        location: str = None,
        scorecard_template_id: str = None
    ) -> Interview:
        """创建部门面试"""
        
        application = await Application.get(application_id)
        
        interview = Interview(
            id=generate_id(),
            application_id=application_id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            interview_type=InterviewType.DEPARTMENT,
            title="部门面试",
            interviewer_id=interviewer_id,
            interviewer_name=(await User.get(interviewer_id)).name if interviewer_id else None,
            scorecard_template_id=scorecard_template_id,
            scheduled_at=scheduled_at,
            duration=duration,
            location=location,
            status=InterviewStatus.SCHEDULED
        )
        await interview.save()
        
        # 发送通知
        await EmailService.send_interview_invitation(interview)
        if interviewer_id:
            await NotificationService.notify_interviewer_scheduled(interview)
        
        return interview
    
    @staticmethod
    async def complete_interview(
        interview_id: str,
        interviewer_id: str,
        result: InterviewResult,
        feedback: str,
        score: int,
        evaluation_data: dict
    ) -> Interview:
        """完成部门面试并填写评价表"""
        
        interview = await Interview.get(interview_id)
        
        # 更新面试记录
        interview.status = InterviewStatus.COMPLETED
        interview.result = result
        interview.feedback = feedback
        interview.score = score
        interview.evaluation_data = json.dumps(evaluation_data)
        interview.completed_at = datetime.now()
        await interview.save()
        
        # 更新应聘状态
        if result == InterviewResult.PASS:
            await ApplicationService.transition_status(
                application_id=interview.application_id,
                to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_COMPLETED,
                operator_id=interviewer_id,
                reason="部门面试通过"
            )
        else:
            await ApplicationService.transition_status(
                application_id=interview.application_id,
                to_status=ApplicationStatus.DEPARTMENT_INTERVIEW_REJECTED,
                operator_id=interviewer_id,
                reason="部门面试未通过"
            )
        
        # 通知HR
        await NotificationService.notify_hr_interview_completed(interview)
        
        return interview
```

### 2.8 测评流程（可选）

```python
class AssessmentService:
    """测评服务"""
    
    @staticmethod
    async def invite_assessment(
        application_id: str,
        hr_id: str,
        assessment_type: str,
        valid_days: int = 7
    ) -> Assessment:
        """邀请候选人参加测评"""
        
        application = await Application.get(application_id)
        
        # 创建测评记录
        assessment = Assessment(
            id=generate_id(),
            application_id=application_id,
            candidate_id=application.candidate_id,
            assessment_type=assessment_type,
            status=AssessmentStatus.INVITED,
            valid_until=datetime.now() + timedelta(days=valid_days)
        )
        
        # 生成测评链接（调用第三方测评平台API）
        assessment.assessment_url = await ThirdPartyAssessmentService.generate_link(
            candidate_email=application.candidate.email,
            assessment_type=assessment_type
        )
        
        await assessment.save()
        
        # 转换应聘状态
        await ApplicationService.transition_status(
            application_id=application_id,
            to_status=ApplicationStatus.ASSESSMENT_INVITED,
            operator_id=hr_id,
            reason=f"邀请{assessment_type}测评"
        )
        
        # 发送邮件
        await EmailService.send_assessment_invitation(assessment)
        
        return assessment
    
    @staticmethod
    async def handle_assessment_result(
        assessment_id: str,
        score: float,
        result_data: dict,
        report_url: str
    ) -> Assessment:
        """处理测评结果（第三方回调）"""
        
        assessment = await Assessment.get(assessment_id)
        
        # 更新测评记录
        assessment.status = AssessmentStatus.COMPLETED
        assessment.score = score
        assessment.result_data = json.dumps(result_data)
        assessment.report_url = report_url
        assessment.completed_at = datetime.now()
        await assessment.save()
        
        # 判断是否通过（根据业务规则）
        passed = score >= 5.5  # 示例：5.5分及以上通过
        
        if passed:
            await ApplicationService.transition_status(
                application_id=assessment.application_id,
                to_status=ApplicationStatus.ASSESSMENT_COMPLETED,
                operator_id="system",
                reason=f"测评完成，得分：{score}"
            )
        else:
            await ApplicationService.transition_status(
                application_id=assessment.application_id,
                to_status=ApplicationStatus.ASSESSMENT_FAILED,
                operator_id="system",
                reason=f"测评未通过，得分：{score}"
            )
        
        # 通知HR
        await NotificationService.notify_hr_assessment_completed(assessment)
        
        return assessment
```

---

## 三、状态流转决策逻辑

### 3.1 部门面试完成后的流转决策

```python
class InterviewFlowDecisionService:
    """面试流程决策服务"""
    
    @staticmethod
    async def decide_next_step_after_department_interview(
        application_id: str,
        hr_id: str
    ) -> str:
        """决定部门面试后的下一步"""
        
        application = await Application.get(application_id)
        flow_config = json.loads(application.interview_flow_config or '{}')
        
        # 检查是否需要测评
        if flow_config.get('has_assessment'):
            return "assessment"
        
        # 检查是否需要HR复试
        if flow_config.get('has_hr_reinterview'):
            return "hr_reinterview"
        
        # 直接进入终面
        return "final_interview"
    
    @staticmethod
    async def proceed_to_next_step(
        application_id: str,
        hr_id: str,
        next_step: str
    ) -> Application:
        """执行下一步"""
        
        if next_step == "assessment":
            await AssessmentService.invite_assessment(
                application_id=application_id,
                hr_id=hr_id,
                assessment_type="商推"
            )
        elif next_step == "hr_reinterview":
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.HR_REINTERVIEW_SCHEDULED,
                operator_id=hr_id,
                reason="安排HR复试"
            )
        elif next_step == "final_interview":
            await ApplicationService.transition_status(
                application_id=application_id,
                to_status=ApplicationStatus.FINAL_INTERVIEW_SCHEDULED,
                operator_id=hr_id,
                reason="安排终面"
            )
        
        application = await Application.get(application_id)
        return application
```

---

**文档版本**: v2.0
**创建时间**: 2026-05-30
**状态**: 业务流程设计完成
