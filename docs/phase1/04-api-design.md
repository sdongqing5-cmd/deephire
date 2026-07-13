# Phase 1: API 设计

## 1. API 设计原则

### 1.1 RESTful API

✅ **遵循 REST 规范**：
- 使用标准 HTTP 方法（GET, POST, PUT, DELETE）
- 使用名词而非动词
- 使用复数形式
- 使用 HTTP 状态码

### 1.2 URL 设计规范

```
/api/v1/{resource}
/api/v1/{resource}/{id}
/api/v1/{resource}/{id}/{sub-resource}
```

### 1.3 响应格式

**成功响应**：
```json
{
  "data": { ... },
  "message": "Success"
}
```

**错误响应**：
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": { ... }
  }
}
```

### 1.4 分页规范

```
GET /api/v1/candidates?page=1&page_size=20
```

响应：
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1000,
    "total_pages": 50
  }
}
```

---

## 2. 认证 API

### 2.1 登录

```http
POST /api/v1/auth/login
```

**Request**：
```json
{
  "email": "hr@deephire.com",
  "password": "password123"
}
```

**Response**：
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "uuid",
      "email": "hr@deephire.com",
      "name": "HR Admin",
      "role": "hr",
      "avatar_url": null
    }
  }
}
```

### 2.2 刷新 Token

```http
POST /api/v1/auth/refresh
```

**Request**：
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2.3 登出

```http
POST /api/v1/auth/logout
```

### 2.4 获取当前用户

```http
GET /api/v1/auth/me
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "email": "hr@deephire.com",
    "name": "HR Admin",
    "role": "hr",
    "avatar_url": null,
    "last_login_at": "2026-05-23T10:00:00Z"
  }
}
```

---

## 3. 职位 API

### 3.1 创建职位

```http
POST /api/v1/jobs
```

**Request**：
```json
{
  "title": "Senior Backend Engineer",
  "department": "Engineering",
  "city": "Shanghai",
  "employment_type": "full_time",
  "salary_min": 300000,
  "salary_max": 500000,
  "salary_currency": "CNY",
  "jd": "We are looking for...",
  "requirements": {
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "years_of_experience": 5,
    "education": "Bachelor",
    "languages": ["Chinese", "English"]
  }
}
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "title": "Senior Backend Engineer",
    "department": "Engineering",
    "city": "Shanghai",
    "employment_type": "full_time",
    "salary_min": 300000,
    "salary_max": 500000,
    "salary_currency": "CNY",
    "owner_id": "uuid",
    "jd": "We are looking for...",
    "requirements": { ... },
    "status": "open",
    "opened_at": "2026-05-23T10:00:00Z",
    "created_at": "2026-05-23T10:00:00Z",
    "updated_at": "2026-05-23T10:00:00Z"
  }
}
```

### 3.2 获取职位列表

```http
GET /api/v1/jobs?status=open&page=1&page_size=20
```

**Query Parameters**：
- `status`: open | paused | closed
- `department`: string
- `city`: string
- `owner_id`: uuid
- `page`: integer
- `page_size`: integer

### 3.3 获取职位详情

```http
GET /api/v1/jobs/{job_id}
```

### 3.4 更新职位

```http
PUT /api/v1/jobs/{job_id}
```

### 3.5 更新职位状态

```http
PATCH /api/v1/jobs/{job_id}/status
```

**Request**：
```json
{
  "status": "paused"
}
```

### 3.6 删除职位

```http
DELETE /api/v1/jobs/{job_id}
```

---

## 4. 候选人 API

### 4.1 创建候选人

```http
POST /api/v1/candidates
```

**Request**：
```json
{
  "name": "张三",
  "phone": "+86 138 0000 0000",
  "email": "zhang@example.com",
  "gender": "male",
  "birth_year": 1990,
  "current_company": "MedTech Inc",
  "current_title": "Senior Sales Manager",
  "years_of_experience": 8,
  "location": "Shanghai",
  "expected_salary_min": 400000,
  "expected_salary_max": 600000,
  "tags": ["医疗器械", "东南亚市场", "B2B销售"],
  "source": "upload"
}
```

### 4.2 获取候选人列表

```http
GET /api/v1/candidates?status=new&page=1&page_size=20
```

**Query Parameters**：
- `status`: new | contacted | interested | interviewing | offered | rejected | hired | archived
- `owner_id`: uuid
- `location`: string
- `years_of_experience_min`: integer
- `years_of_experience_max`: integer
- `tags`: string[] (comma-separated)
- `current_company`: string
- `page`: integer
- `page_size`: integer
- `sort_by`: created_at | updated_at | latest_contacted_at
- `sort_order`: asc | desc

**Response**：
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "张三",
      "phone": "+86 138 0000 0000",
      "email": "zhang@example.com",
      "current_company": "MedTech Inc",
      "current_title": "Senior Sales Manager",
      "years_of_experience": 8,
      "location": "Shanghai",
      "tags": ["医疗器械", "东南亚市场"],
      "status": "new",
      "latest_contacted_at": null,
      "created_at": "2026-05-23T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 1000,
    "total_pages": 50
  }
}
```

### 4.3 获取候选人详情

```http
GET /api/v1/candidates/{candidate_id}
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "name": "张三",
    "phone": "+86 138 0000 0000",
    "email": "zhang@example.com",
    "gender": "male",
    "birth_year": 1990,
    "current_company": "MedTech Inc",
    "current_title": "Senior Sales Manager",
    "years_of_experience": 8,
    "location": "Shanghai",
    "expected_salary_min": 400000,
    "expected_salary_max": 600000,
    "tags": ["医疗器械", "东南亚市场", "B2B销售"],
    "source": "upload",
    "status": "new",
    "latest_contacted_at": null,
    "owner_id": "uuid",
    "created_by": "uuid",
    "created_at": "2026-05-23T10:00:00Z",
    "updated_at": "2026-05-23T10:00:00Z",
    "resumes": [
      {
        "id": "uuid",
        "file_name": "张三_简历.pdf",
        "file_url": "/uploads/resumes/xxx.pdf",
        "parsed_data": { ... },
        "created_at": "2026-05-23T10:00:00Z"
      }
    ],
    "timeline": [
      {
        "id": "uuid",
        "event_type": "resume_uploaded",
        "description": "上传了简历",
        "created_by": "uuid",
        "created_at": "2026-05-23T10:00:00Z"
      }
    ]
  }
}
```

### 4.4 更新候选人

```http
PUT /api/v1/candidates/{candidate_id}
```

### 4.5 更新候选人状态

```http
PATCH /api/v1/candidates/{candidate_id}/status
```

**Request**：
```json
{
  "status": "contacted",
  "notes": "已电话联系，候选人表示感兴趣"
}
```

### 4.6 添加候选人标签

```http
POST /api/v1/candidates/{candidate_id}/tags
```

**Request**：
```json
{
  "tags": ["重点关注", "高优先级"]
}
```

### 4.7 删除候选人标签

```http
DELETE /api/v1/candidates/{candidate_id}/tags
```

**Request**：
```json
{
  "tags": ["重点关注"]
}
```

---

## 5. 简历 API

### 5.1 上传简历

```http
POST /api/v1/resumes/upload
```

**Request**：
- Content-Type: multipart/form-data
- file: File (PDF or DOCX)
- candidate_id: uuid (optional, 如果是新候选人则不传)

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "candidate_id": "uuid",
    "file_name": "张三_简历.pdf",
    "file_url": "/uploads/resumes/xxx.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "parse_status": "parsing",
    "created_at": "2026-05-23T10:00:00Z"
  }
}
```

### 5.2 获取简历解析状态

```http
GET /api/v1/resumes/{resume_id}/status
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "parse_status": "completed",
    "parsed_at": "2026-05-23T10:00:30Z",
    "parsed_data": {
      "personal": {
        "name": "张三",
        "phone": "+86 138 0000 0000",
        "email": "zhang@example.com",
        "location": "上海"
      },
      "experience": [ ... ],
      "education": [ ... ],
      "skills": [ ... ],
      "summary": "..."
    }
  }
}
```

### 5.3 重新解析简历

```http
POST /api/v1/resumes/{resume_id}/reparse
```

---

## 6. 搜索 API（核心）

### 6.1 搜索候选人

```http
POST /api/v1/candidates/search
```

**Request**：
```json
{
  "query": "找做过医疗器械销售，负责东南亚市场的人",
  "filters": {
    "years_of_experience_min": 5,
    "years_of_experience_max": 10,
    "location": ["Shanghai", "Beijing"],
    "current_company": ["MedTech Inc", "HealthCare Corp"],
    "tags": ["医疗器械", "B2B销售"],
    "status": ["new", "contacted", "interested"]
  },
  "search_mode": "hybrid",
  "page": 1,
  "page_size": 20
}
```

**Query Parameters**：
- `query`: 自然语言搜索（可选）
- `filters`: 结构化过滤（可选）
- `search_mode`: keyword | semantic | hybrid（默认 hybrid）
- `page`: integer
- `page_size`: integer

**Response**：
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "张三",
      "current_company": "MedTech Inc",
      "current_title": "Senior Sales Manager",
      "years_of_experience": 8,
      "location": "Shanghai",
      "tags": ["医疗器械", "东南亚市场"],
      "match_score": 0.95,
      "match_reasons": [
        "医疗器械销售经验 8 年",
        "负责东南亚市场",
        "B2B 销售背景"
      ],
      "status": "new",
      "created_at": "2026-05-23T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 50,
    "total_pages": 3
  },
  "search_metadata": {
    "query": "找做过医疗器械销售，负责东南亚市场的人",
    "search_mode": "hybrid",
    "took_ms": 150
  }
}
```

**为什么这样设计？**

1. **Hybrid Search**：
   - 支持自然语言搜索（semantic）
   - 支持关键词搜索（keyword）
   - 支持组合搜索（hybrid）

2. **match_score**：
   - 0-1 之间的匹配度分数
   - 帮助 Recruiter 快速判断候选人质量

3. **match_reasons**：
   - 解释为什么匹配
   - 提升用户信任度

---

## 7. 候选人激活 API

### 7.1 生成联系脚本

```http
POST /api/v1/candidates/activate/generate-script
```

**Request**：
```json
{
  "candidate_ids": ["uuid1", "uuid2"],
  "job_id": "uuid",
  "context": "我们正在招聘医疗器械销售经理"
}
```

**Response**：
```json
{
  "data": {
    "scripts": [
      {
        "candidate_id": "uuid1",
        "candidate_name": "张三",
        "script": "您好，张先生。我是 XX 公司的招聘专员。我看到您在 MedTech Inc 有 8 年医疗器械销售经验，并且负责过东南亚市场。我们目前有一个医疗器械销售经理的职位，年薪 40-60 万，想确认一下您近期是否还在考虑新的机会？",
        "talking_points": [
          "强调候选人的医疗器械背景",
          "提及东南亚市场经验",
          "说明薪资范围",
          "询问是否考虑机会"
        ]
      }
    ]
  }
}
```

### 7.2 记录联系结果

```http
POST /api/v1/candidates/{candidate_id}/contact
```

**Request**：
```json
{
  "result": "interested",
  "notes": "候选人表示感兴趣，约定下周一详细沟通",
  "next_follow_up_at": "2026-05-30T10:00:00Z"
}
```

**result 枚举**：
- `interested`: 感兴趣
- `not_interested`: 不感兴趣
- `follow_up_later`: 稍后跟进
- `unreachable`: 无法联系

---

## 8. 候选人-职位关联 API

### 8.1 申请职位

```http
POST /api/v1/candidate-jobs
```

**Request**：
```json
{
  "candidate_id": "uuid",
  "job_id": "uuid"
}
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "candidate_id": "uuid",
    "job_id": "uuid",
    "status": "applied",
    "match_score": 0.85,
    "applied_at": "2026-05-23T10:00:00Z"
  }
}
```

### 8.2 获取候选人的职位申请

```http
GET /api/v1/candidates/{candidate_id}/jobs
```

### 8.3 获取职位的候选人

```http
GET /api/v1/jobs/{job_id}/candidates?status=applied&page=1&page_size=20
```

### 8.4 更新申请状态

```http
PATCH /api/v1/candidate-jobs/{id}/status
```

**Request**：
```json
{
  "status": "interviewing",
  "notes": "进入面试流程"
}
```

---

## 9. 面试 API

### 9.1 创建面试

```http
POST /api/v1/interviews
```

**Request**：
```json
{
  "candidate_id": "uuid",
  "job_id": "uuid",
  "interviewer_id": "uuid",
  "round": 1,
  "interview_type": "technical",
  "scheduled_at": "2026-05-25T14:00:00Z",
  "duration_minutes": 60,
  "location": "Office Room 301",
  "meeting_url": null
}
```

### 9.2 获取面试列表

```http
GET /api/v1/interviews?status=scheduled&interviewer_id=uuid&date=2026-05-25
```

**Query Parameters**：
- `status`: scheduled | completed | cancelled | no_show | rescheduled
- `interviewer_id`: uuid
- `candidate_id`: uuid
- `job_id`: uuid
- `date`: YYYY-MM-DD
- `page`: integer
- `page_size`: integer

### 9.3 获取面试详情

```http
GET /api/v1/interviews/{interview_id}
```

### 9.4 更新面试

```http
PUT /api/v1/interviews/{interview_id}
```

### 9.5 提交面试反馈

```http
POST /api/v1/interviews/{interview_id}/feedback
```

**Request**：
```json
{
  "feedback": "候选人技术能力强，沟通清晰，团队协作意识好。",
  "score": 4,
  "result": "pass",
  "dimensions": {
    "technical_skills": 4,
    "communication": 5,
    "team_fit": 4
  }
}
```

**score**: 1-5 分
**result**: pass | pending | reject

### 9.6 取消面试

```http
POST /api/v1/interviews/{interview_id}/cancel
```

**Request**：
```json
{
  "cancelled_reason": "候选人时间冲突，需要重新安排"
}
```

---

## 10. 时间线 API

### 10.1 获取候选人时间线

```http
GET /api/v1/candidates/{candidate_id}/timeline?page=1&page_size=50
```

**Response**：
```json
{
  "data": [
    {
      "id": "uuid",
      "event_type": "status_change",
      "description": "状态从 new 变更为 contacted",
      "event_data": {
        "old_status": "new",
        "new_status": "contacted"
      },
      "created_by": {
        "id": "uuid",
        "name": "Recruiter"
      },
      "created_at": "2026-05-23T10:00:00Z"
    },
    {
      "id": "uuid",
      "event_type": "contacted",
      "description": "电话联系候选人",
      "event_data": {
        "result": "interested",
        "notes": "候选人表示感兴趣"
      },
      "created_by": {
        "id": "uuid",
        "name": "Recruiter"
      },
      "created_at": "2026-05-23T10:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 10,
    "total_pages": 1
  }
}
```

---

## 11. 备注 API

### 11.1 添加备注

```http
POST /api/v1/candidates/{candidate_id}/notes
```

**Request**：
```json
{
  "content": "候选人对薪资要求较高，需要进一步沟通",
  "is_private": false
}
```

### 11.2 获取备注列表

```http
GET /api/v1/candidates/{candidate_id}/notes
```

### 11.3 更新备注

```http
PUT /api/v1/notes/{note_id}
```

### 11.4 删除备注

```http
DELETE /api/v1/notes/{note_id}
```

---

## 12. Dashboard API

### 12.1 HR Dashboard

```http
GET /api/v1/dashboard/hr
```

**Response**：
```json
{
  "data": {
    "stats": {
      "open_jobs": 15,
      "total_candidates": 10000,
      "active_candidates": 500,
      "interviews_today": 8,
      "pending_actions": 12
    },
    "recent_activities": [
      {
        "type": "candidate_activated",
        "description": "张三 被激活并联系",
        "timestamp": "2026-05-23T10:00:00Z"
      }
    ],
    "upcoming_interviews": [
      {
        "id": "uuid",
        "candidate_name": "张三",
        "job_title": "Senior Backend Engineer",
        "interviewer_name": "李四",
        "scheduled_at": "2026-05-23T14:00:00Z"
      }
    ]
  }
}
```

### 12.2 Recruiter Dashboard

```http
GET /api/v1/dashboard/recruiter
```

**Response**：
```json
{
  "data": {
    "stats": {
      "my_jobs": 5,
      "my_candidates": 50,
      "to_contact_today": 10,
      "contacted_this_week": 25
    },
    "my_jobs": [ ... ],
    "my_candidates": [ ... ],
    "recent_contacts": [ ... ]
  }
}
```

### 12.3 Interviewer Dashboard

```http
GET /api/v1/dashboard/interviewer
```

**Response**：
```json
{
  "data": {
    "today_interviews": [
      {
        "id": "uuid",
        "candidate_name": "张三",
        "job_title": "Senior Backend Engineer",
        "scheduled_at": "2026-05-23T14:00:00Z",
        "duration_minutes": 60,
        "location": "Office Room 301"
      }
    ],
    "pending_feedback": [
      {
        "id": "uuid",
        "candidate_name": "李四",
        "job_title": "Frontend Engineer",
        "completed_at": "2026-05-22T15:00:00Z"
      }
    ]
  }
}
```

---

## 13. 统计 API

### 13.1 招聘漏斗

```http
GET /api/v1/stats/funnel?job_id=uuid&start_date=2026-01-01&end_date=2026-05-23
```

**Response**：
```json
{
  "data": {
    "applied": 100,
    "screening": 50,
    "interviewing": 20,
    "offered": 5,
    "hired": 3
  }
}
```

### 13.2 候选人来源统计

```http
GET /api/v1/stats/candidate-sources
```

---

## 14. API 安全

### 14.1 认证

所有 API（除了 `/api/v1/auth/login`）都需要：

```http
Authorization: Bearer {access_token}
```

### 14.2 权限控制

基于角色的访问控制（RBAC）：

| API | HR | Recruiter | Interviewer |
|-----|----|-----------| ------------|
| 查看所有候选人 | ✅ | ❌ | ❌ |
| 查看自己的候选人 | ✅ | ✅ | ❌ |
| 创建职位 | ✅ | ❌ | ❌ |
| 上传简历 | ✅ | ✅ | ❌ |
| 搜索候选人 | ✅ | ✅ | ❌ |
| 安排面试 | ✅ | ✅ | ❌ |
| 提交面试反馈 | ✅ | ✅ | ✅ |

### 14.3 Rate Limiting

```
100 requests / minute / user
```

超过限制返回：
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

---

## 15. API 文档

使用 **FastAPI** 自动生成：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 16. API 版本管理

当前版本：`v1`

未来版本：
- 使用 URL 版本控制：`/api/v2/...`
- 保持向后兼容
- 提前通知废弃 API

---

## 总结

这套 API 设计：

✅ **RESTful 规范**：清晰易懂
✅ **完整覆盖**：支持所有核心功能
✅ **搜索优化**：Hybrid Search 架构
✅ **权限控制**：基于角色的访问控制
✅ **可扩展**：支持未来功能扩展
✅ **文档完善**：自动生成 API 文档

下一步：UI Sitemap 设计
