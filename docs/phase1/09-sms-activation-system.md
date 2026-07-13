# Phase 1: AI 短信激活系统设计

## 1. 系统概述

### 1.1 核心功能

**AI 短信激活系统** 是 DeepHire 的核心差异化功能，用于批量激活简历库中的候选人。

**核心价值**：
- 从 10,000+ 简历库中快速找到合适候选人
- AI 生成个性化短信话术
- 批量发送短信
- 自动收集候选人意向
- 自动更新候选人状态

**为什么是短信而不是语音？**
- ✅ 合规（无需电信资质）
- ✅ 成本低（¥0.045/条）
- ✅ 快速上线（3周）
- ✅ 候选人接受度高
- ✅ 可追踪、可统计

---

## 2. 业务流程

### 2.1 完整流程

```
Step 1: 搜索候选人
Recruiter 输入：
"找做过医疗器械销售，负责东南亚市场的人"

系统返回：
50 个匹配候选人

↓

Step 2: 勾选候选人
Recruiter 勾选：
10 个候选人

↓

Step 3: 配置激活任务
- 选择职位
- 选择短信模板（或自定义）
- 预览短信内容
- 设置发送时间

↓

Step 4: AI 生成个性化短信
系统为每个候选人生成个性化短信：

候选人 A（张三）：
"张先生您好，我是 XX 公司的招聘专员。
看到您在 MedTech Inc 有 8 年医疗器械销售经验，
并且负责过东南亚市场。我们目前有一个医疗器械
销售经理的职位，年薪 40-60 万，想确认一下您
近期是否还在考虑新的机会？
点击链接表达意向：https://deephire.com/i/abc123"

候选人 B（李四）：
"李先生您好，我是 XX 公司的招聘专员。
看到您在 HealthCare Corp 有 6 年医疗设备销售
经验。我们目前有一个医疗器械销售经理的职位，
年薪 40-60 万，想确认一下您近期是否还在考虑
新的机会？
点击链接表达意向：https://deephire.com/i/def456"

↓

Step 5: 批量发送短信
系统通过阿里云短信批量发送

↓

Step 6: 候选人响应
候选人点击链接，进入 H5 页面：

┌─────────────────────────────┐
│  DeepHire 候选人意向确认    │
├─────────────────────────────┤
│                             │
│  职位：医疗器械销售经理      │
│  公司：XX 公司              │
│  薪资：40-60 万             │
│                             │
│  您是否考虑这个机会？        │
│                             │
│  ● 感兴趣，请联系我          │
│  ○ 暂时不考虑               │
│  ○ 稍后再说                 │
│                             │
│  [提交]                     │
│                             │
└─────────────────────────────┘

↓

Step 7: 自动更新状态
系统自动：
- 更新候选人状态
- 记录到 Timeline
- 通知 Recruiter

↓

Step 8: Recruiter 跟进
Recruiter 看到：
- 张三：感兴趣 ✅
- 李四：暂时不考虑 ❌
- 王五：未读

Recruiter 重点跟进感兴趣的候选人
```

---

## 3. 技术架构

### 3.1 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 搜索页面     │  │ 激活配置页面 │  │ 激活报告页面 │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓ REST API
┌─────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Activation Service                               │   │
│  │  - 创建激活任务                                   │   │
│  │  - 生成个性化短信                                 │   │
│  │  - 批量发送                                       │   │
│  │  - 结果统计                                       │   │
│  └──────────────────────────────────────────────────┘   │
│                            ↓                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ AI Service   │  │ SMS Service  │  │ Task Queue   │  │
│  │ (OpenAI)     │  │ (阿里云短信) │  │ (Redis)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ candidates   │  │ activation_  │  │ activation_  │  │
│  │              │  │ tasks        │  │ logs         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 3.2 核心模块

#### 3.2.1 Activation Service（激活服务）

```python
class ActivationService:
    """候选人激活服务"""
    
    async def create_activation_task(
        self,
        candidate_ids: List[str],
        job_id: str,
        template_id: str,
        scheduled_at: datetime
    ) -> ActivationTask:
        """创建激活任务"""
        
    async def generate_personalized_sms(
        self,
        candidate: Candidate,
        job: Job,
        template: SMSTemplate
    ) -> str:
        """生成个性化短信"""
        
    async def send_batch_sms(
        self,
        task_id: str
    ) -> BatchSendResult:
        """批量发送短信"""
        
    async def get_task_report(
        self,
        task_id: str
    ) -> ActivationReport:
        """获取激活报告"""
```

#### 3.2.2 AI Service（AI 服务）

```python
class AIService:
    """AI 服务"""
    
    async def generate_sms_content(
        self,
        candidate: Candidate,
        job: Job,
        template: str
    ) -> str:
        """生成短信内容"""
        # 使用 OpenAI API
        # Prompt: 根据候选人简历和职位生成个性化短信
```

#### 3.2.3 SMS Service（短信服务）

```python
class SMSService:
    """短信服务（阿里云）"""
    
    async def send_sms(
        self,
        phone: str,
        content: str,
        template_code: str
    ) -> SendResult:
        """发送单条短信"""
        
    async def send_batch_sms(
        self,
        messages: List[SMSMessage]
    ) -> BatchSendResult:
        """批量发送短信"""
```

---

## 4. 数据库设计

### 4.1 activation_tasks 表（激活任务）

```sql
CREATE TABLE activation_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    template_id UUID REFERENCES sms_templates(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    total_count INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    response_count INTEGER DEFAULT 0,
    interested_count INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activation_tasks_status ON activation_tasks(status);
CREATE INDEX idx_activation_tasks_created_by ON activation_tasks(created_by);
CREATE INDEX idx_activation_tasks_scheduled_at ON activation_tasks(scheduled_at);
```

### 4.2 activation_logs 表（激活日志）

```sql
CREATE TABLE activation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES activation_tasks(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    phone VARCHAR(50) NOT NULL,
    sms_content TEXT NOT NULL,
    intent_url TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed', 'responded')),
    send_result JSONB,
    response_result VARCHAR(20) CHECK (response_result IN ('interested', 'not_interested', 'later')),
    response_at TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activation_logs_task_id ON activation_logs(task_id);
CREATE INDEX idx_activation_logs_candidate_id ON activation_logs(candidate_id);
CREATE INDEX idx_activation_logs_status ON activation_logs(status);
CREATE INDEX idx_activation_logs_response_result ON activation_logs(response_result);
```

### 4.3 sms_templates 表（短信模板）

```sql
CREATE TABLE sms_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    variables JSONB,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sms_templates_is_active ON sms_templates(is_active);
```

**模板示例**：
```json
{
  "name": "医疗器械销售激活模板",
  "content": "{{candidate_name}}您好，我是{{company_name}}的招聘专员。看到您在{{current_company}}有{{years_of_experience}}年{{industry}}经验，并且{{highlight}}。我们目前有一个{{job_title}}的职位，年薪{{salary_range}}，想确认一下您近期是否还在考虑新的机会？点击链接表达意向：{{intent_url}}",
  "variables": [
    "candidate_name",
    "company_name",
    "current_company",
    "years_of_experience",
    "industry",
    "highlight",
    "job_title",
    "salary_range",
    "intent_url"
  ]
}
```

---

## 5. API 设计

### 5.1 创建激活任务

```http
POST /api/v1/activation/tasks
```

**Request**：
```json
{
  "name": "医疗器械销售激活 - 2026-05",
  "candidate_ids": ["uuid1", "uuid2", "uuid3"],
  "job_id": "uuid",
  "template_id": "uuid",
  "scheduled_at": "2026-05-24T09:00:00Z"
}
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "name": "医疗器械销售激活 - 2026-05",
    "status": "pending",
    "total_count": 10,
    "scheduled_at": "2026-05-24T09:00:00Z",
    "preview": [
      {
        "candidate_id": "uuid1",
        "candidate_name": "张三",
        "phone": "+86 138 0000 0000",
        "sms_content": "张先生您好，我是 XX 公司的招聘专员..."
      }
    ]
  }
}
```

### 5.2 获取激活任务列表

```http
GET /api/v1/activation/tasks?status=completed&page=1&page_size=20
```

### 5.3 获取激活任务详情

```http
GET /api/v1/activation/tasks/{task_id}
```

**Response**：
```json
{
  "data": {
    "id": "uuid",
    "name": "医疗器械销售激活 - 2026-05",
    "status": "completed",
    "total_count": 10,
    "sent_count": 10,
    "success_count": 10,
    "failed_count": 0,
    "response_count": 7,
    "interested_count": 3,
    "scheduled_at": "2026-05-24T09:00:00Z",
    "started_at": "2026-05-24T09:00:05Z",
    "completed_at": "2026-05-24T09:02:30Z",
    "logs": [
      {
        "candidate_id": "uuid1",
        "candidate_name": "张三",
        "phone": "+86 138 0000 0000",
        "status": "responded",
        "response_result": "interested",
        "sent_at": "2026-05-24T09:00:10Z",
        "response_at": "2026-05-24T09:15:00Z"
      }
    ]
  }
}
```

### 5.4 候选人意向响应（H5 页面调用）

```http
POST /api/v1/activation/intent/{token}
```

**Request**：
```json
{
  "result": "interested"
}
```

**result 枚举**：
- `interested`: 感兴趣
- `not_interested`: 不感兴趣
- `later`: 稍后再说

---

## 6. 前端设计

### 6.1 激活配置页面

**路由**：`/activation/new`

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  创建激活任务                                            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Step 1: 选择候选人 (已选择 10 人)                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │ [Card] 张三 - MedTech Inc - 8 years              │  │
│  │ [Card] 李四 - HealthCare Corp - 6 years          │  │
│  │ ...                                               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Step 2: 选择职位                                        │
│  [Dropdown] 医疗器械销售经理                             │
│                                                           │
│  Step 3: 选择短信模板                                    │
│  [Dropdown] 医疗器械销售激活模板                         │
│                                                           │
│  Step 4: 预览短信内容                                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 张先生您好，我是 XX 公司的招聘专员。              │  │
│  │ 看到您在 MedTech Inc 有 8 年医疗器械销售经验，   │  │
│  │ 并且负责过东南亚市场。我们目前有一个医疗器械     │  │
│  │ 销售经理的职位，年薪 40-60 万，想确认一下您      │  │
│  │ 近期是否还在考虑新的机会？                       │  │
│  │ 点击链接表达意向：https://deephire.com/i/abc123 │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  Step 5: 设置发送时间                                    │
│  ● 立即发送                                              │
│  ○ 定时发送  [日期选择器] [时间选择器]                   │
│                                                           │
│  [取消] [创建任务]                                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 6.2 激活任务列表页面

**路由**：`/activation/tasks`

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  激活任务                                [+ 创建任务]     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 医疗器械销售激活 - 2026-05                        │  │
│  │ 状态：已完成  ✅                                  │  │
│  │                                                   │  │
│  │ 发送：10/10  成功：10  响应：7  感兴趣：3        │  │
│  │                                                   │  │
│  │ 创建时间：2026-05-24 09:00                       │  │
│  │ 完成时间：2026-05-24 09:02                       │  │
│  │                                                   │  │
│  │ [查看详情] [查看报告]                            │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  [更多任务...]                                           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 6.3 激活报告页面

**路由**：`/activation/tasks/{id}/report`

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│  激活报告 - 医疗器械销售激活 - 2026-05                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Stats Cards                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 10       │ │ 10       │ │ 7        │ │ 3        │  │
│  │ 总发送   │ │ 成功     │ │ 已响应   │ │ 感兴趣   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                           │
│  响应详情                                                │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 张三  ✅ 感兴趣  2026-05-24 09:15                 │  │
│  │ 李四  ❌ 不感兴趣  2026-05-24 09:20               │  │
│  │ 王五  ⏰ 稍后再说  2026-05-24 09:25               │  │
│  │ 赵六  ⏳ 未响应                                   │  │
│  │ ...                                               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                           │
│  [导出报告] [批量跟进感兴趣的候选人]                     │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 6.4 候选人意向确认页面（H5）

**路由**：`/intent/{token}`

**布局**：
```
┌─────────────────────────────┐
│  DeepHire 候选人意向确认    │
├─────────────────────────────┤
│                             │
│  职位：医疗器械销售经理      │
│  公司：XX 公司              │
│  地点：上海                 │
│  薪资：40-60 万             │
│                             │
│  职位描述：                 │
│  我们正在寻找一位有经验的   │
│  医疗器械销售经理...        │
│                             │
│  您是否考虑这个机会？        │
│                             │
│  ● 感兴趣，请联系我          │
│  ○ 暂时不考虑               │
│  ○ 稍后再说                 │
│                             │
│  [提交]                     │
│                             │
└─────────────────────────────┘
```

---

## 7. 阿里云短信配置

### 7.1 申请流程

```
1. 注册阿里云账号
2. 实名认证
3. 开通短信服务
4. 申请签名（公司名称）
5. 申请模板（需要审核）
6. 获取 AccessKey
```

### 7.2 短信模板审核

**模板示例**：
```
${name}您好，我是${company}的招聘专员。
看到您在${current_company}有${years}年${industry}经验。
我们目前有一个${job}的职位，年薪${salary}，
想确认一下您近期是否还在考虑新的机会？
点击链接表达意向：${url}
```

**审核要点**：
- 不能有营销性质
- 必须有退订方式
- 内容合规

### 7.3 成本估算

```
阿里云短信价格：¥0.045/条

假设：
- 每月激活 1000 个候选人
- 每个候选人发 1 条短信

成本：
1000 * ¥0.045 = ¥45/月

结论：成本极低
```

---

## 8. 开发计划

### Week 8: 数据库与后端基础（5天）

**Day 1-2: 数据库设计**
- [ ] 创建 activation_tasks 表
- [ ] 创建 activation_logs 表
- [ ] 创建 sms_templates 表
- [ ] 创建初始模板数据

**Day 3-4: 后端 API**
- [ ] 实现 ActivationService
- [ ] 实现 AIService（短信生成）
- [ ] 实现 SMSService（阿里云集成）
- [ ] POST /api/v1/activation/tasks
- [ ] GET /api/v1/activation/tasks
- [ ] GET /api/v1/activation/tasks/{id}
- [ ] POST /api/v1/activation/intent/{token}

**Day 5: 测试**
- [ ] 单元测试
- [ ] 集成测试
- [ ] 阿里云短信测试

### Week 9: 前端开发（5天）

**Day 1-2: 激活配置页面**
- [ ] 创建激活配置页面
- [ ] 候选人选择组件
- [ ] 职位选择组件
- [ ] 模板选择组件
- [ ] 短信预览组件

**Day 3: 激活任务列表**
- [ ] 创建任务列表页面
- [ ] 任务卡片组件
- [ ] 状态展示

**Day 4: 激活报告页面**
- [ ] 创建报告页面
- [ ] 统计卡片
- [ ] 响应详情列表
- [ ] 导出功能

**Day 5: H5 意向确认页面**
- [ ] 创建 H5 页面
- [ ] 响应式设计
- [ ] 提交功能
- [ ] 测试

### Week 10: 集成与优化（5天）

**Day 1-2: 前后端联调**
- [ ] API 集成
- [ ] 测试完整流程
- [ ] 修复 Bug

**Day 3: 批量发送优化**
- [ ] 异步任务队列
- [ ] 并发控制
- [ ] 失败重试

**Day 4: 用户体验优化**
- [ ] Loading 状态
- [ ] 错误处理
- [ ] Toast 提示
- [ ] 进度展示

**Day 5: 测试与文档**
- [ ] 完整测试
- [ ] 用户文档
- [ ] API 文档

---

## 9. Phase 2: 语音外呼（6个月后）

### 9.1 申请资质

```
时间：3-6 个月
成本：几万到几十万

需要：
1. 公司营业执照
2. ICP 备案
3. 呼叫中心许可证申请
4. 码号资源申请
```

### 9.2 技术升级

```
语音外呼系统：
- 集成阿里云智能外呼
- ASR（语音识别）
- LLM（对话理解）
- TTS（语音合成）
- 多轮对话
- 意图识别
- 情绪识别
```

---

## 10. 总结

### 10.1 Phase 1 短信激活系统

✅ **合规**：无需电信资质
✅ **成本低**：¥0.045/条
✅ **快速上线**：3 周
✅ **效果好**：解决 80% 激活需求
✅ **可扩展**：未来升级到语音

### 10.2 核心价值

1. **批量激活**：从 10K+ 简历库快速激活
2. **AI 个性化**：每个候选人不同的短信
3. **自动化**：自动发送、自动收集、自动更新
4. **数据驱动**：完整的激活报告

### 10.3 差异化竞争力

**传统招聘系统**：
- 手动搜索简历
- 手动拨打电话
- 手动记录结果
- 效率低

**DeepHire**：
- AI 搜索（Hybrid Search）
- AI 生成个性化短信
- 批量自动发送
- 自动收集意向
- 自动更新状态
- 效率提升 10 倍 ⭐

---

下一步：更新开发 Roadmap
