# DeepHire 招聘系统 - V2 API接口设计文档

## 📋 文档说明

本文档包含：
- 完整的API接口定义
- 请求/响应格式
- 错误码定义

---

## 一、API接口列表

### 1.1 简历管理模块

#### 上传简历
```
POST /api/v1/applications/upload-resume
```

**Request Body:**
```json
{
  "job_id": "string",
  "candidate": {
    "name": "string (optional)",
    "phone": "string (optional)",
    "email": "string (optional)"
  },
  "source": "string (optional)",
  "resume_file": "file"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "candidate_id": "string",
    "status": "new",
    "duplicate_check": {
      "is_duplicate": false,
      "warning": "string (optional)"
    }
  }
}
```

#### 查重检查
```
POST /api/v1/applications/check-duplicate
```

**Request Body:**
```json
{
  "candidate_id": "string",
  "job_id": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "is_duplicate": false,
    "reason": "string (optional)",
    "existing_application": {
      "id": "string",
      "applied_at": "datetime",
      "status": "string"
    },
    "active_applications": [
      {
        "id": "string",
        "job_title": "string",
        "status": "string"
      }
    ]
  }
}
```

#### 获取应聘记录列表
```
GET /api/v1/applications
```

**Query Parameters:**
```
status: string (optional)
job_id: string (optional)
hr_id: string (optional)
page: int (default: 1)
page_size: int (default: 20)
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "string",
        "candidate": {
          "id": "string",
          "name": "string",
          "phone": "string",
          "email": "string"
        },
        "job": {
          "id": "string",
          "title": "string"
        },
        "status": "string",
        "applied_at": "datetime",
        "last_status_change_at": "datetime"
      }
    ]
  }
}
```

#### 获取应聘记录详情
```
GET /api/v1/applications/{id}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "string",
    "candidate": {
      "id": "string",
      "name": "string",
      "phone": "string",
      "email": "string",
      "current_company": "string",
      "current_position": "string",
      "work_years": 5
    },
    "job": {
      "id": "string",
      "title": "string",
      "department": "string"
    },
    "status": "string",
    "resume_url": "string",
    "source": "string",
    "hr": {
      "id": "string",
      "name": "string"
    },
    "intention_contact": {
      "method": "string",
      "result": "string",
      "notes": "string",
      "contacted_at": "datetime"
    },
    "applied_at": "datetime",
    "last_status_change_at": "datetime"
  }
}
```

---

### 1.2 HR筛选模块

#### 开始HR筛选
```
POST /api/v1/applications/{id}/start-screening
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "status": "hr_screening"
  }
}
```

#### 记录电话沟通结果
```
POST /api/v1/applications/{id}/phone-communication
```

**Request Body:**
```json
{
  "result": "agreed | declined | no_answer",
  "notes": "string (optional)"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "status": "string"
  }
}
```

#### HR淘汰
```
POST /api/v1/applications/{id}/reject
```

**Request Body:**
```json
{
  "reason": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "status": "hr_rejected"
  }
}
```

---

### 1.3 HR初筛面试模块

#### 安排HR初筛面试
```
POST /api/v1/hr-interviews/schedule
```

**Request Body:**
```json
{
  "application_id": "string",
  "scheduled_at": "datetime",
  "duration": 30,
  "location": "string (optional)",
  "scorecard_template_id": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "application_id": "string",
    "scheduled_at": "datetime",
    "status": "scheduled"
  }
}
```

#### 完成HR初筛面试
```
POST /api/v1/hr-interviews/{id}/complete
```

**Request Body:**
```json
{
  "result": "pass | fail",
  "feedback": "string",
  "score": 85,
  "evaluation_data": {
    "专业能力": 4,
    "沟通能力": 5,
    "学习能力": 4
  }
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "result": "pass",
    "application_status": "hr_interview_completed"
  }
}
```

---

### 1.4 面试官筛选模块

#### 推送简历给面试官
```
POST /api/v1/applications/{id}/push-to-interviewer
```

**Request Body:**
```json
{
  "interviewer_id": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "status": "sent_to_interviewer"
  }
}
```

#### 提交筛选结果
```
POST /api/v1/interviewer-screenings
```

**Request Body:**
```json
{
  "application_id": "string",
  "result": "pass | reject",
  "comments": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "screening_id": "string",
    "application_id": "string",
    "result": "pass",
    "application_status": "interview_intention_communication"
  }
}
```

#### 获取我的待筛选简历
```
GET /api/v1/interviewer-screenings/my-pending
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 5,
    "items": [
      {
        "application_id": "string",
        "candidate": {
          "name": "string",
          "current_company": "string",
          "work_years": 5
        },
        "job": {
          "title": "string"
        },
        "resume_url": "string",
        "pushed_at": "datetime"
      }
    ]
  }
}
```

---

### 1.5 面试意向沟通模块

#### 发起面试意向沟通
```
POST /api/v1/applications/{id}/initiate-intention-contact
```

**Request Body:**
```json
{
  "contact_method": "ai_call | manual"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "contact_method": "ai_call",
    "status": "interview_intention_communication"
  }
}
```

#### 记录沟通结果
```
POST /api/v1/applications/{id}/record-intention-result
```

**Request Body:**
```json
{
  "result": "agreed | declined | no_answer",
  "notes": "string (optional)"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "status": "interview_time_confirming | candidate_declined_interview"
  }
}
```

#### 智能外呼回调
```
POST /api/v1/applications/{id}/intention-callback
```

**Request Body:**
```json
{
  "result": "agreed | declined | no_answer",
  "transcript": "string",
  "call_duration": 120
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success"
}
```

---

### 1.6 面试时间确认模块

#### 发送面试确认邮件
```
POST /api/v1/applications/{id}/send-interview-confirmation
```

**Request Body:**
```json
{
  "time_options": [
    "2026-06-01T10:00:00Z",
    "2026-06-01T14:00:00Z",
    "2026-06-02T10:00:00Z"
  ]
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "notification_sent_at": "datetime",
    "confirmation_token": "string"
  }
}
```

#### 候选人确认面试（公开接口）
```
POST /api/v1/interviews/confirm/{token}
```

**Request Body:**
```json
{
  "selected_time": "2026-06-01T10:00:00Z"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "application_id": "string",
    "interview_id": "string",
    "scheduled_at": "datetime"
  }
}
```

#### 候选人拒绝面试（公开接口）
```
POST /api/v1/interviews/decline/{token}
```

**Request Body:**
```json
{
  "reason": "string (optional)"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success"
}
```

---

### 1.7 部门面试模块

#### 安排部门面试
```
POST /api/v1/department-interviews/schedule
```

**Request Body:**
```json
{
  "application_id": "string",
  "interviewer_id": "string",
  "scheduled_at": "datetime",
  "duration": 60,
  "location": "string (optional)",
  "meeting_link": "string (optional)",
  "scorecard_template_id": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "application_id": "string",
    "scheduled_at": "datetime"
  }
}
```

#### 完成部门面试
```
POST /api/v1/department-interviews/{id}/complete
```

**Request Body:**
```json
{
  "result": "pass | fail",
  "feedback": "string",
  "score": 90,
  "evaluation_data": {
    "技术能力": 5,
    "项目经验": 4,
    "团队协作": 5
  }
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "result": "pass",
    "application_status": "department_interview_completed"
  }
}
```

---

### 1.8 测评模块

#### 邀请测评
```
POST /api/v1/assessments/invite
```

**Request Body:**
```json
{
  "application_id": "string",
  "assessment_type": "商推 | SHL",
  "valid_days": 7
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "assessment_id": "string",
    "assessment_url": "string",
    "valid_until": "datetime"
  }
}
```

#### 测评结果回调（第三方）
```
POST /api/v1/assessments/{id}/result-callback
```

**Request Body:**
```json
{
  "score": 6.5,
  "result_data": {
    "商业综合推理能力": 6.5,
    "逻辑推理": 7.0,
    "数据分析": 6.0
  },
  "report_url": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success"
}
```

#### 获取测评详情
```
GET /api/v1/assessments/{id}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "string",
    "application_id": "string",
    "assessment_type": "商推",
    "status": "completed",
    "score": 6.5,
    "report_url": "string",
    "completed_at": "datetime"
  }
}
```

---

### 1.9 HR复试模块

#### 安排HR复试
```
POST /api/v1/hr-reinterviews/schedule
```

**Request Body:**
```json
{
  "application_id": "string",
  "interviewer_id": "string",
  "scheduled_at": "datetime",
  "duration": 45,
  "location": "string (optional)",
  "scorecard_template_id": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "scheduled_at": "datetime"
  }
}
```

#### 完成HR复试
```
POST /api/v1/hr-reinterviews/{id}/complete
```

**Request Body:**
```json
{
  "result": "pass | fail",
  "feedback": "string",
  "score": 88,
  "evaluation_data": {}
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "result": "pass",
    "application_status": "hr_reinterview_completed"
  }
}
```

---

### 1.10 终面模块

#### 安排终面
```
POST /api/v1/final-interviews/schedule
```

**Request Body:**
```json
{
  "application_id": "string",
  "interviewer_id": "string",
  "scheduled_at": "datetime",
  "duration": 60,
  "location": "string (optional)",
  "scorecard_template_id": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "scheduled_at": "datetime"
  }
}
```

#### 完成终面
```
POST /api/v1/final-interviews/{id}/complete
```

**Request Body:**
```json
{
  "result": "pass | fail",
  "feedback": "string",
  "score": 92,
  "evaluation_data": {
    "战略思维": 5,
    "领导力": 4,
    "文化匹配": 5
  }
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "result": "pass",
    "application_status": "final_interview_completed"
  }
}
```

---

### 1.11 面试管理通用接口

#### 获取面试列表
```
GET /api/v1/interviews
```

**Query Parameters:**
```
application_id: string (optional)
interviewer_id: string (optional)
interview_type: string (optional)
status: string (optional)
date_from: date (optional)
date_to: date (optional)
page: int (default: 1)
page_size: int (default: 20)
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 50,
    "items": [
      {
        "id": "string",
        "interview_type": "department",
        "candidate": {
          "name": "string"
        },
        "job": {
          "title": "string"
        },
        "interviewer": {
          "name": "string"
        },
        "scheduled_at": "datetime",
        "status": "scheduled",
        "result": "pending"
      }
    ]
  }
}
```

#### 改期面试
```
POST /api/v1/interviews/{id}/reschedule
```

**Request Body:**
```json
{
  "new_scheduled_at": "datetime",
  "reason": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "interview_id": "string",
    "scheduled_at": "datetime"
  }
}
```

#### 取消面试
```
POST /api/v1/interviews/{id}/cancel
```

**Request Body:**
```json
{
  "reason": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success"
}
```

---

### 1.12 Offer管理模块

#### 创建Offer
```
POST /api/v1/offers
```

**Request Body:**
```json
{
  "application_id": "string",
  "hiring_company": "string",
  "hiring_department_id": "string",
  "hiring_position": "string",
  "hiring_level": "string",
  "base_salary": 400000,
  "bonus": 100000,
  "stock_options": 50000,
  "expected_onboard_date": "date",
  "work_location": "string",
  "interview_feedback": "string",
  "talent_category": "string",
  "culture_fit_score": 5,
  "potential_score": 4,
  "clarity_score": 5
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "offer_id": "string",
    "status": "approval_pending"
  }
}
```

#### 提交Offer审批
```
POST /api/v1/offers/{id}/submit-approval
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "offer_id": "string",
    "approval_status": "pending",
    "current_approver": {
      "id": "string",
      "name": "string"
    }
  }
}
```

#### 审批Offer
```
POST /api/v1/offers/{id}/approve
```

**Request Body:**
```json
{
  "approved": true,
  "comments": "string (optional)"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "offer_id": "string",
    "approval_status": "approved | rejected",
    "next_approver": {
      "id": "string",
      "name": "string"
    }
  }
}
```

#### 编辑Offer
```
PUT /api/v1/offers/{id}
```

**Request Body:**
```json
{
  "base_salary": 420000,
  "bonus": 120000,
  "expected_onboard_date": "date"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "offer_id": "string"
  }
}
```

#### 发送Offer
```
POST /api/v1/offers/{id}/send
```

**Request Body:**
```json
{
  "offer_template": "string",
  "cc_emails": ["string"]
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "offer_id": "string",
    "sent_at": "datetime",
    "valid_until": "datetime"
  }
}
```

---

### 1.13 入职管理模块

#### 发送信息采集通知
```
POST /api/v1/onboardings/{id}/send-info-collection
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "onboarding_id": "string",
    "info_collection_sent_at": "datetime"
  }
}
```

#### 改期入职
```
POST /api/v1/onboardings/{id}/reschedule
```

**Request Body:**
```json
{
  "new_onboard_date": "date",
  "reason": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "onboarding_id": "string",
    "onboard_date": "date"
  }
}
```

#### 取消入职
```
POST /api/v1/onboardings/{id}/cancel
```

**Request Body:**
```json
{
  "reason": "string"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "success"
}
```

#### 完成入职
```
POST /api/v1/onboardings/{id}/complete
```

**Response:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "onboarding_id": "string",
    "completed_at": "datetime"
  }
}
```

---

## 二、错误码定义

```python
class ErrorCode:
    """错误码定义"""
    
    # 通用错误 (1000-1999)
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    INVALID_PARAMETER = 1001
    UNAUTHORIZED = 1002
    FORBIDDEN = 1003
    NOT_FOUND = 1004
    
    # 应聘记录错误 (2000-2999)
    APPLICATION_NOT_FOUND = 2000
    DUPLICATE_APPLICATION = 2001
    INVALID_STATUS_TRANSITION = 2002
    APPLICATION_LOCKED = 2003
    
    # 面试错误 (3000-3999)
    INTERVIEW_NOT_FOUND = 3000
    INTERVIEW_TIME_CONFLICT = 3001
    INTERVIEW_ALREADY_COMPLETED = 3002
    INVALID_INTERVIEW_RESULT = 3003
    
    # Offer错误 (4000-4999)
    OFFER_NOT_FOUND = 4000
    OFFER_APPROVAL_REJECTED = 4001
    OFFER_EXPIRED = 4002
    
    # 入职错误 (5000-5999)
    ONBOARDING_NOT_FOUND = 5000
    ONBOARDING_ALREADY_COMPLETED = 5001
```

---

**文档版本**: v2.0
**创建时间**: 2026-05-30
**状态**: API接口设计完成
