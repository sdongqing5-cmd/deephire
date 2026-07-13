# Phase 1: 数据库设计

## 1. 数据库选型

### 1.1 主数据库：PostgreSQL 16

**为什么选择 PostgreSQL？**
- ✅ JSONB 支持：灵活存储简历数据
- ✅ 全文搜索：支持中英文搜索
- ✅ pgvector 扩展：支持向量存储
- ✅ 事务支持：保证数据一致性
- ✅ 成熟稳定：生产环境验证
- ✅ 开源免费：无许可证成本

### 1.2 扩展

```sql
-- 启用 UUID 生成
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用向量搜索（可选）
CREATE EXTENSION IF NOT EXISTS vector;

-- 启用全文搜索
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

## 2. 核心表设计

### 2.1 users 表（用户）

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('hr', 'recruiter', 'interviewer')),
    avatar_url TEXT,
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- 注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.role IS '角色：hr, recruiter, interviewer';
```

**字段说明**：
- `id`: UUID 主键，分布式友好
- `email`: 登录邮箱，唯一
- `password_hash`: bcrypt 加密后的密码
- `role`: 角色枚举，控制权限
- `is_active`: 软删除标记

---

### 2.2 jobs 表（职位）

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    city VARCHAR(100),
    employment_type VARCHAR(20) DEFAULT 'full_time' CHECK (employment_type IN ('full_time', 'part_time', 'contract', 'internship')),
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'CNY',
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    jd TEXT NOT NULL,
    requirements JSONB,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'paused', 'closed')),
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_owner_id ON jobs(owner_id);
CREATE INDEX idx_jobs_department ON jobs(department);
CREATE INDEX idx_jobs_city ON jobs(city);
CREATE INDEX idx_jobs_opened_at ON jobs(opened_at DESC);

-- 全文搜索索引
CREATE INDEX idx_jobs_title_gin ON jobs USING gin(to_tsvector('english', title));
CREATE INDEX idx_jobs_jd_gin ON jobs USING gin(to_tsvector('english', jd));

-- 注释
COMMENT ON TABLE jobs IS '职位表';
COMMENT ON COLUMN jobs.status IS '状态：open-开放, paused-暂停, closed-关闭';
COMMENT ON COLUMN jobs.requirements IS 'JSON格式的职位要求';
```

**字段说明**：
- `requirements`: JSONB 存储结构化要求（技能、经验等）
- `owner_id`: 职位负责人（HR/Recruiter）
- `status`: 职位状态

**requirements JSONB 示例**：
```json
{
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "years_of_experience": 5,
  "education": "Bachelor",
  "languages": ["Chinese", "English"]
}
```

---

### 2.3 candidates 表（候选人）

```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(255),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other', 'unknown')),
    birth_year INTEGER,
    current_company VARCHAR(200),
    current_title VARCHAR(200),
    years_of_experience INTEGER,
    location VARCHAR(100),
    expected_salary_min INTEGER,
    expected_salary_max INTEGER,
    tags TEXT[],
    source VARCHAR(50),
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'interested', 'interviewing', 'offered', 'rejected', 'hired', 'archived')),
    latest_contacted_at TIMESTAMP,
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_owner_id ON candidates(owner_id);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_phone ON candidates(phone);
CREATE INDEX idx_candidates_tags ON candidates USING GIN(tags);
CREATE INDEX idx_candidates_current_company ON candidates(current_company);
CREATE INDEX idx_candidates_location ON candidates(location);
CREATE INDEX idx_candidates_years_of_experience ON candidates(years_of_experience);
CREATE INDEX idx_candidates_latest_contacted_at ON candidates(latest_contacted_at DESC);
CREATE INDEX idx_candidates_created_at ON candidates(created_at DESC);

-- 全文搜索索引
CREATE INDEX idx_candidates_name_gin ON candidates USING gin(to_tsvector('english', name));

-- 注释
COMMENT ON TABLE candidates IS '候选人表';
COMMENT ON COLUMN candidates.status IS '状态：new-新建, contacted-已联系, interested-感兴趣, interviewing-面试中, offered-已发offer, rejected-已拒绝, hired-已入职, archived-已归档';
COMMENT ON COLUMN candidates.source IS '来源：upload-上传, referral-推荐, linkedin-领英, etc';
COMMENT ON COLUMN candidates.tags IS '标签数组';
```

**字段说明**：
- `tags`: PostgreSQL 数组，支持多标签
- `owner_id`: 负责该候选人的 Recruiter
- `source`: 候选人来源渠道
- `status`: 候选人当前状态

**状态流转**：
```
new → contacted → interested → interviewing → offered → hired
                              ↓
                          rejected
```

---

### 2.4 resumes 表（简历）

```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('pdf', 'docx')),
    file_size INTEGER,
    raw_text TEXT,
    parsed_data JSONB,
    embedding VECTOR(1536),
    parse_status VARCHAR(20) DEFAULT 'pending' CHECK (parse_status IN ('pending', 'parsing', 'completed', 'failed')),
    parse_error TEXT,
    parsed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_resumes_candidate_id ON resumes(candidate_id);
CREATE INDEX idx_resumes_parse_status ON resumes(parse_status);
CREATE INDEX idx_resumes_parsed_data ON resumes USING GIN(parsed_data);
CREATE INDEX idx_resumes_created_at ON resumes(created_at DESC);

-- 向量索引（如果使用 pgvector）
-- CREATE INDEX idx_resumes_embedding ON resumes USING ivfflat (embedding vector_cosine_ops);

-- 全文搜索索引
CREATE INDEX idx_resumes_raw_text_gin ON resumes USING gin(to_tsvector('english', raw_text));

-- 注释
COMMENT ON TABLE resumes IS '简历表';
COMMENT ON COLUMN resumes.raw_text IS '简历原始文本';
COMMENT ON COLUMN resumes.parsed_data IS 'AI解析后的结构化数据';
COMMENT ON COLUMN resumes.embedding IS '简历向量（用于语义搜索）';
```

**parsed_data JSONB 示例**：
```json
{
  "personal": {
    "name": "张三",
    "phone": "+86 138 0000 0000",
    "email": "zhang@example.com",
    "location": "上海"
  },
  "experience": [
    {
      "company": "MedTech Inc",
      "title": "Senior Sales Manager",
      "start_date": "2018-01",
      "end_date": "present",
      "description": "负责东南亚市场医疗器械销售...",
      "achievements": ["年销售额$5M", "团队管理10人"]
    }
  ],
  "education": [
    {
      "school": "复旦大学",
      "degree": "Bachelor",
      "major": "市场营销",
      "start_date": "2010-09",
      "end_date": "2014-06"
    }
  ],
  "skills": ["B2B销售", "医疗器械", "东南亚市场", "团队管理"],
  "languages": ["中文", "英文"],
  "summary": "8年医疗器械销售经验，专注东南亚市场..."
}
```

---

### 2.5 candidate_jobs 表（候选人-职位关联）

```sql
CREATE TABLE candidate_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'applied' CHECK (status IN ('applied', 'screening', 'interviewing', 'offered', 'rejected', 'hired', 'withdrawn')),
    match_score DECIMAL(5,2),
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rejected_reason TEXT,
    rejected_at TIMESTAMP,
    offered_at TIMESTAMP,
    hired_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, job_id)
);

-- 索引
CREATE INDEX idx_candidate_jobs_candidate_id ON candidate_jobs(candidate_id);
CREATE INDEX idx_candidate_jobs_job_id ON candidate_jobs(job_id);
CREATE INDEX idx_candidate_jobs_status ON candidate_jobs(status);
CREATE INDEX idx_candidate_jobs_applied_at ON candidate_jobs(applied_at DESC);

-- 注释
COMMENT ON TABLE candidate_jobs IS '候选人-职位关联表';
COMMENT ON COLUMN candidate_jobs.match_score IS '匹配度分数（0-100）';
COMMENT ON COLUMN candidate_jobs.status IS '状态：applied-已申请, screening-筛选中, interviewing-面试中, offered-已发offer, rejected-已拒绝, hired-已入职, withdrawn-已撤回';
```

**字段说明**：
- `match_score`: AI 计算的匹配度（0-100）
- `status`: 该候选人在该职位的状态
- `UNIQUE(candidate_id, job_id)`: 一个候选人只能申请一个职位一次

---

### 2.6 interviews 表（面试）

```sql
CREATE TABLE interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    interviewer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    round INTEGER DEFAULT 1,
    interview_type VARCHAR(20) DEFAULT 'technical' CHECK (interview_type IN ('phone', 'technical', 'behavioral', 'final', 'other')),
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    location VARCHAR(200),
    meeting_url TEXT,
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show', 'rescheduled')),
    feedback TEXT,
    score INTEGER CHECK (score >= 1 AND score <= 5),
    result VARCHAR(20) CHECK (result IN ('pass', 'pending', 'reject')),
    completed_at TIMESTAMP,
    cancelled_reason TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX idx_interviews_job_id ON interviews(job_id);
CREATE INDEX idx_interviews_interviewer_id ON interviews(interviewer_id);
CREATE INDEX idx_interviews_scheduled_at ON interviews(scheduled_at);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_result ON interviews(result);

-- 注释
COMMENT ON TABLE interviews IS '面试表';
COMMENT ON COLUMN interviews.round IS '面试轮次';
COMMENT ON COLUMN interviews.interview_type IS '面试类型：phone-电话, technical-技术, behavioral-行为, final-终面, other-其他';
COMMENT ON COLUMN interviews.score IS '评分（1-5分）';
COMMENT ON COLUMN interviews.result IS '结果：pass-通过, pending-待定, reject-拒绝';
```

**字段说明**：
- `round`: 面试轮次（1, 2, 3...）
- `interview_type`: 面试类型
- `location`: 面试地点（"Zoom" / "Office Room 301"）
- `meeting_url`: 线上面试链接

---

### 2.7 timelines 表（时间线）

```sql
CREATE TABLE timelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    description TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_timelines_candidate_id ON timelines(candidate_id);
CREATE INDEX idx_timelines_event_type ON timelines(event_type);
CREATE INDEX idx_timelines_created_at ON timelines(created_at DESC);
CREATE INDEX idx_timelines_event_data ON timelines USING GIN(event_data);

-- 注释
COMMENT ON TABLE timelines IS '候选人时间线表';
COMMENT ON COLUMN timelines.event_type IS '事件类型：status_change, contacted, interview_scheduled, note_added, resume_uploaded, etc';
COMMENT ON COLUMN timelines.event_data IS '事件详细数据（JSON）';
```

**event_type 枚举**：
- `status_change`: 状态变更
- `contacted`: 联系候选人
- `interview_scheduled`: 安排面试
- `interview_completed`: 完成面试
- `note_added`: 添加备注
- `resume_uploaded`: 上传简历
- `job_applied`: 申请职位
- `offer_sent`: 发送 offer
- `hired`: 入职

**event_data 示例**：
```json
{
  "old_status": "contacted",
  "new_status": "interested",
  "reason": "候选人表示感兴趣"
}
```

---

### 2.8 notes 表（备注）

```sql
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_private BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_notes_candidate_id ON notes(candidate_id);
CREATE INDEX idx_notes_created_by ON notes(created_by);
CREATE INDEX idx_notes_created_at ON notes(created_at DESC);

-- 注释
COMMENT ON TABLE notes IS '备注表';
COMMENT ON COLUMN notes.is_private IS '是否私有（仅创建人可见）';
```

---

### 2.9 attachments 表（附件）

```sql
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_attachments_candidate_id ON attachments(candidate_id);
CREATE INDEX idx_attachments_uploaded_by ON attachments(uploaded_by);

-- 注释
COMMENT ON TABLE attachments IS '附件表（除简历外的其他文件）';
```

---

## 3. 数据库关系图

```
users (用户)
  ├─ 1:N → jobs (owner_id)
  ├─ 1:N → candidates (owner_id, created_by)
  ├─ 1:N → interviews (interviewer_id, created_by)
  ├─ 1:N → timelines (created_by)
  └─ 1:N → notes (created_by)

jobs (职位)
  ├─ 1:N → candidate_jobs
  └─ 1:N → interviews

candidates (候选人)
  ├─ 1:N → resumes
  ├─ 1:N → candidate_jobs
  ├─ 1:N → interviews
  ├─ 1:N → timelines
  ├─ 1:N → notes
  └─ 1:N → attachments

resumes (简历)
  └─ N:1 → candidates

candidate_jobs (候选人-职位关联)
  ├─ N:1 → candidates
  └─ N:1 → jobs

interviews (面试)
  ├─ N:1 → candidates
  ├─ N:1 → jobs
  └─ N:1 → users (interviewer)

timelines (时间线)
  └─ N:1 → candidates

notes (备注)
  └─ N:1 → candidates

attachments (附件)
  └─ N:1 → candidates
```

---

## 4. 数据库设计原则

### 4.1 主键设计

✅ **使用 UUID**：
- 分布式友好
- 不暴露数据量
- 安全性更好
- 避免主键冲突

### 4.2 外键设计

✅ **使用外键约束**：
- 保证数据一致性
- 级联删除（ON DELETE CASCADE）
- 级联置空（ON DELETE SET NULL）

### 4.3 索引设计

✅ **索引原则**：
- 外键字段必须建索引
- 查询频繁的字段建索引
- 排序字段建索引
- 数组字段用 GIN 索引
- JSONB 字段用 GIN 索引

### 4.4 时间戳设计

✅ **时间戳字段**：
- `created_at`: 创建时间
- `updated_at`: 更新时间
- 使用 TIMESTAMP 类型
- 默认值 CURRENT_TIMESTAMP

### 4.5 软删除

✅ **使用 is_active 标记**：
- 不物理删除数据
- 保留历史记录
- 支持恢复

### 4.6 JSONB 使用

✅ **适合用 JSONB 的场景**：
- 结构灵活的数据（简历数据）
- 不需要频繁查询的字段
- 嵌套数据结构

❌ **不适合用 JSONB 的场景**：
- 需要频繁查询的字段
- 需要外键约束的字段
- 需要严格类型检查的字段

---

## 5. 数据库性能优化

### 5.1 索引优化

```sql
-- 复合索引（常一起查询的字段）
CREATE INDEX idx_candidates_status_owner ON candidates(status, owner_id);
CREATE INDEX idx_interviews_interviewer_scheduled ON interviews(interviewer_id, scheduled_at);

-- 部分索引（只索引常用数据）
CREATE INDEX idx_candidates_active ON candidates(status) WHERE status NOT IN ('archived', 'rejected');
CREATE INDEX idx_jobs_open ON jobs(id) WHERE status = 'open';
```

### 5.2 查询优化

```sql
-- 使用 EXPLAIN ANALYZE 分析查询
EXPLAIN ANALYZE
SELECT * FROM candidates WHERE status = 'new' AND owner_id = 'xxx';

-- 避免 SELECT *，只查询需要的字段
SELECT id, name, email FROM candidates WHERE status = 'new';
```

### 5.3 分区表（未来）

```sql
-- 按时间分区（当数据量大时）
CREATE TABLE candidates_2026 PARTITION OF candidates
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
```

---

## 6. 数据库迁移策略

### 6.1 使用 Alembic

```bash
# 创建迁移
alembic revision --autogenerate -m "create initial tables"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 6.2 迁移原则

✅ **迁移文件必须**：
- 可重复执行
- 可回滚
- 有清晰的注释
- 测试过

---

## 7. 数据库安全

### 7.1 权限控制

```sql
-- 创建应用用户
CREATE USER deephire_app WITH PASSWORD 'strong_password';

-- 授予权限
GRANT CONNECT ON DATABASE deephire TO deephire_app;
GRANT USAGE ON SCHEMA public TO deephire_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO deephire_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO deephire_app;
```

### 7.2 敏感数据

✅ **敏感数据处理**：
- 密码：bcrypt 加密
- 个人信息：访问控制
- 简历文件：URL 签名

---

## 8. 数据库备份

### 8.1 备份策略

```bash
# 每日全量备份
pg_dump -U postgres deephire > backup_$(date +%Y%m%d).sql

# 增量备份（WAL归档）
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

### 8.2 恢复策略

```bash
# 恢复数据库
psql -U postgres deephire < backup_20260522.sql
```

---

## 9. 初始化数据

### 9.1 创建默认用户

```sql
-- HR 用户
INSERT INTO users (email, password_hash, name, role) VALUES
('hr@deephire.com', '$2b$12$...', 'HR Admin', 'hr');

-- Recruiter 用户
INSERT INTO users (email, password_hash, name, role) VALUES
('recruiter@deephire.com', '$2b$12$...', 'Recruiter', 'recruiter');

-- Interviewer 用户
INSERT INTO users (email, password_hash, name, role) VALUES
('interviewer@deephire.com', '$2b$12$...', 'Interviewer', 'interviewer');
```

---

## 10. 数据库设计总结

### 10.1 核心表

1. **users**: 用户表（3种角色）
2. **jobs**: 职位表
3. **candidates**: 候选人表（核心）
4. **resumes**: 简历表（核心）
5. **candidate_jobs**: 候选人-职位关联
6. **interviews**: 面试表
7. **timelines**: 时间线表
8. **notes**: 备注表
9. **attachments**: 附件表

### 10.2 设计亮点

✅ **UUID 主键**：分布式友好
✅ **JSONB 存储**：灵活的简历数据
✅ **Timeline 设计**：完整的活动记录
✅ **索引优化**：查询性能好
✅ **外键约束**：数据一致性
✅ **软删除**：数据可恢复

### 10.3 可扩展性

✅ **支持 10K 简历**：当前设计
✅ **支持 100万 简历**：分区表 + 主从复制
✅ **支持向量搜索**：pgvector 扩展
✅ **支持全文搜索**：PostgreSQL 内置

---

下一步：API 设计
