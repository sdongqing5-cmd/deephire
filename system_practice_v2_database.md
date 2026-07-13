# DeepHire 招聘系统 - V2数据库设计文档

## 📋 文档说明

本文档包含：
- 完整的数据库表设计
- 数据库迁移脚本
- 索引优化方案

---

## 一、数据库迁移脚本

### 1.1 Application表新增字段

```sql
-- 迁移脚本: 001_add_application_fields.sql

-- 新增面试意向沟通字段
ALTER TABLE applications ADD COLUMN intention_contact_method VARCHAR(50);
ALTER TABLE applications ADD COLUMN intention_contact_result VARCHAR(50);
ALTER TABLE applications ADD COLUMN intention_contact_notes TEXT;
ALTER TABLE applications ADD COLUMN intention_contacted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE applications ADD COLUMN intention_contacted_by VARCHAR(255);

-- 新增面试时间确认字段
ALTER TABLE applications ADD COLUMN interview_notification_sent_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE applications ADD COLUMN interview_confirmed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE applications ADD COLUMN interview_confirmation_token VARCHAR(255);

-- 新增面试流程配置字段
ALTER TABLE applications ADD COLUMN interview_flow_config TEXT;

-- 新增锁定信息字段
ALTER TABLE applications ADD COLUMN is_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE applications ADD COLUMN locked_by VARCHAR(255);
ALTER TABLE applications ADD COLUMN locked_at TIMESTAMP WITH TIME ZONE;

-- 新增应聘次数统计
ALTER TABLE applications ADD COLUMN application_count INTEGER DEFAULT 1;

-- 添加索引
CREATE INDEX idx_applications_is_locked ON applications(is_locked);
CREATE INDEX idx_applications_intention_contacted_by ON applications(intention_contacted_by);
CREATE INDEX idx_applications_locked_by ON applications(locked_by);

-- 添加注释
COMMENT ON COLUMN applications.intention_contact_method IS '面试意向沟通方式: ai_call, manual';
COMMENT ON COLUMN applications.intention_contact_result IS '沟通结果: agreed, declined, no_answer';
COMMENT ON COLUMN applications.interview_confirmation_token IS '面试确认token（用于邮件链接）';
COMMENT ON COLUMN applications.interview_flow_config IS '面试流程配置（JSON格式）';
```

### 1.2 创建InterviewerScreening表

```sql
-- 迁移脚本: 002_create_interviewer_screening.sql

CREATE TABLE interviewer_screenings (
    id VARCHAR(255) PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL,
    interviewer_id VARCHAR(255) NOT NULL,
    interviewer_name VARCHAR(255),
    
    -- 筛选结果
    result VARCHAR(50) NOT NULL,  -- pass, reject
    comments TEXT,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- 外键
    CONSTRAINT fk_interviewer_screening_application 
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CONSTRAINT fk_interviewer_screening_interviewer 
        FOREIGN KEY (interviewer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 添加索引
CREATE INDEX idx_interviewer_screenings_application_id ON interviewer_screenings(application_id);
CREATE INDEX idx_interviewer_screenings_interviewer_id ON interviewer_screenings(interviewer_id);
CREATE INDEX idx_interviewer_screenings_result ON interviewer_screenings(result);

-- 添加注释
COMMENT ON TABLE interviewer_screenings IS '面试官简历筛选记录';
COMMENT ON COLUMN interviewer_screenings.result IS '筛选结果: pass（通过）, reject（淘汰）';
COMMENT ON COLUMN interviewer_screenings.comments IS '筛选意见（简单填写）';
```

### 1.3 Interview表新增字段

```sql
-- 迁移脚本: 003_add_interview_type.sql

-- 新增面试类型字段
ALTER TABLE interviews ADD COLUMN interview_type VARCHAR(50) NOT NULL DEFAULT 'department';

-- 添加索引
CREATE INDEX idx_interviews_interview_type ON interviews(interview_type);

-- 添加注释
COMMENT ON COLUMN interviews.interview_type IS '面试类型: hr_initial, department, hr_reinterview, final';

-- 更新现有数据（根据实际情况调整）
UPDATE interviews SET interview_type = 'department' WHERE interview_type IS NULL;
```

### 1.4 创建Assessment表

```sql
-- 迁移脚本: 004_create_assessment.sql

CREATE TABLE assessments (
    id VARCHAR(255) PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL,
    candidate_id VARCHAR(255),
    
    -- 测评信息
    assessment_type VARCHAR(100),  -- 商推、SHL等
    assessment_url TEXT,
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'invited',  -- invited, in_progress, completed, failed, expired
    
    -- 结果
    score DECIMAL(5, 2),
    result_data TEXT,  -- JSON格式
    report_url TEXT,
    
    -- 有效期
    valid_until TIMESTAMP WITH TIME ZONE,
    
    -- 时间戳
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- 外键
    CONSTRAINT fk_assessment_application 
        FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CONSTRAINT fk_assessment_candidate 
        FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- 添加索引
CREATE INDEX idx_assessments_application_id ON assessments(application_id);
CREATE INDEX idx_assessments_candidate_id ON assessments(candidate_id);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessments_assessment_type ON assessments(assessment_type);

-- 添加注释
COMMENT ON TABLE assessments IS '测评记录';
COMMENT ON COLUMN assessments.assessment_type IS '测评类型：商推、SHL等';
COMMENT ON COLUMN assessments.status IS '测评状态: invited, in_progress, completed, failed, expired';
COMMENT ON COLUMN assessments.result_data IS '测评结果数据（JSON格式）';
```

### 1.5 更新ApplicationStatus枚举

```sql
-- 迁移脚本: 005_update_application_status_enum.sql

-- 添加新的状态值
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_interview_scheduled';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_interviewing';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_interview_completed';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_interview_rejected';

ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'interview_intention_communication';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'candidate_declined_interview';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'interview_time_confirming';

ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'department_interview_scheduled';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'department_interviewing';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'department_interview_completed';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'department_interview_rejected';

ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'assessment_invited';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'assessment_in_progress';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'assessment_completed';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'assessment_failed';

ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_reinterview_scheduled';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_reinterviewing';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_reinterview_completed';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'hr_reinterview_rejected';

ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'final_interview_scheduled';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'final_interviewing';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'final_interview_completed';
ALTER TYPE application_status ADD VALUE IF NOT EXISTS 'final_interview_rejected';

-- 注意: PostgreSQL的枚举类型不支持删除值，只能添加
-- 如果需要删除旧的状态值，需要重建枚举类型
```

---

## 二、完整表结构

### 2.1 applications表（完整版）

```sql
CREATE TABLE applications (
    -- 基本信息
    id VARCHAR(255) PRIMARY KEY,
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    
    -- 状态
    status application_status NOT NULL DEFAULT 'new',
    
    -- 简历信息
    resume_url TEXT,
    resume_parsed_data TEXT,
    
    -- 来源
    source VARCHAR(100),
    
    -- 负责人
    hr_id VARCHAR(255),
    recruiter_id VARCHAR(255),
    
    -- 锁定信息
    is_locked BOOLEAN DEFAULT FALSE,
    locked_by VARCHAR(255),
    locked_at TIMESTAMP WITH TIME ZONE,
    
    -- 应聘次数统计
    application_count INTEGER DEFAULT 1,
    
    -- 面试意向沟通
    intention_contact_method VARCHAR(50),
    intention_contact_result VARCHAR(50),
    intention_contact_notes TEXT,
    intention_contacted_at TIMESTAMP WITH TIME ZONE,
    intention_contacted_by VARCHAR(255),
    
    -- 面试时间确认
    interview_notification_sent_at TIMESTAMP WITH TIME ZONE,
    interview_confirmed_at TIMESTAMP WITH TIME ZONE,
    interview_confirmation_token VARCHAR(255),
    
    -- 面试流程配置
    interview_flow_config TEXT,
    
    -- 时间戳
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hr_viewed_at TIMESTAMP WITH TIME ZONE,
    last_status_change_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- 外键
    CONSTRAINT fk_application_candidate FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    CONSTRAINT fk_application_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT fk_application_hr FOREIGN KEY (hr_id) REFERENCES users(id),
    CONSTRAINT fk_application_recruiter FOREIGN KEY (recruiter_id) REFERENCES users(id),
    CONSTRAINT fk_application_locked_by FOREIGN KEY (locked_by) REFERENCES users(id),
    CONSTRAINT fk_application_intention_contacted_by FOREIGN KEY (intention_contacted_by) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_hr_id ON applications(hr_id);
CREATE INDEX idx_applications_is_locked ON applications(is_locked);
CREATE INDEX idx_applications_applied_at ON applications(applied_at);
CREATE INDEX idx_applications_candidate_job ON applications(candidate_id, job_id);
CREATE INDEX idx_applications_status_hr ON applications(status, hr_id);
```

### 2.2 interviews表（完整版）

```sql
CREATE TABLE interviews (
    id VARCHAR(255) PRIMARY KEY,
    application_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255),
    candidate_id VARCHAR(255),
    
    -- 面试类型
    interview_type interview_type NOT NULL,
    
    -- 面试信息
    title VARCHAR(255),
    
    -- 面试官
    interviewer_id VARCHAR(255) NOT NULL,
    interviewer_name VARCHAR(255),
    
    -- 评价表
    scorecard_template_id VARCHAR(255),
    
    -- 时间地点
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER DEFAULT 60,
    location TEXT,
    meeting_link TEXT,
    
    -- 状态和结果
    status interview_status NOT NULL DEFAULT 'scheduled',
    result interview_result DEFAULT 'pending',
    
    -- 评价
    feedback TEXT,
    score INTEGER,
    evaluation_data TEXT,
    
    -- 通知
    notification_sent_to_candidate BOOLEAN DEFAULT FALSE,
    notification_sent_to_interviewer BOOLEAN DEFAULT FALSE,
    candidate_confirmed_at TIMESTAMP WITH TIME ZONE,
    
    -- 时间戳
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- 外键
    CONSTRAINT fk_interview_application FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    CONSTRAINT fk_interview_job FOREIGN KEY (job_id) REFERENCES jobs(id),
    CONSTRAINT fk_interview_candidate FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    CONSTRAINT fk_interview_interviewer FOREIGN KEY (interviewer_id) REFERENCES users(id),
    CONSTRAINT fk_interview_scorecard_template FOREIGN KEY (scorecard_template_id) REFERENCES scorecard_templates(id)
);

-- 索引
CREATE INDEX idx_interviews_application_id ON interviews(application_id);
CREATE INDEX idx_interviews_interviewer_id ON interviews(interviewer_id);
CREATE INDEX idx_interviews_scheduled_at ON interviews(scheduled_at);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_interview_type ON interviews(interview_type);
CREATE INDEX idx_interviews_interviewer_scheduled ON interviews(interviewer_id, scheduled_at);
```

---

## 三、索引优化方案

### 3.1 查询性能优化索引

```sql
-- 优化HR工作台查询
CREATE INDEX idx_applications_hr_status_applied ON applications(hr_id, status, applied_at DESC);

-- 优化面试官待筛选简历查询
CREATE INDEX idx_interviewer_screenings_interviewer_pending ON interviewer_screenings(interviewer_id, created_at DESC) 
WHERE result IS NULL;

-- 优化面试列表查询
CREATE INDEX idx_interviews_date_range ON interviews(scheduled_at) 
WHERE status IN ('scheduled', 'confirmed', 'in_progress');

-- 优化候选人应聘历史查询
CREATE INDEX idx_applications_candidate_applied ON applications(candidate_id, applied_at DESC);

-- 优化状态历史查询
CREATE INDEX idx_application_status_history_app_created ON application_status_history(application_id, created_at DESC);
```

### 3.2 部分索引（提升特定查询性能）

```sql
-- 只索引活跃状态的应聘记录
CREATE INDEX idx_applications_active_status ON applications(status, last_status_change_at DESC)
WHERE status NOT IN ('hr_rejected', 'interviewer_rejected', 'department_interview_rejected', 
                     'hr_interview_rejected', 'hr_reinterview_rejected', 'final_interview_rejected',
                     'assessment_failed', 'salary_rejected', 'offer_rejected', 'candidate_withdrawn',
                     'onboard_cancelled', 'onboarded');

-- 只索引未完成的面试
CREATE INDEX idx_interviews_pending ON interviews(interviewer_id, scheduled_at)
WHERE status IN ('scheduled', 'confirmed') AND result = 'pending';

-- 只索引待审批的Offer
CREATE INDEX idx_offers_pending_approval ON offers(current_approver_id, created_at DESC)
WHERE approval_status = 'pending';
```

---

## 四、数据迁移注意事项

### 4.1 迁移前检查

```sql
-- 检查现有数据
SELECT status, COUNT(*) 
FROM applications 
GROUP BY status 
ORDER BY COUNT(*) DESC;

-- 检查是否有孤立数据
SELECT COUNT(*) 
FROM applications a 
LEFT JOIN candidates c ON a.candidate_id = c.id 
WHERE c.id IS NULL;

-- 检查面试记录
SELECT COUNT(*) 
FROM interviews 
WHERE interview_type IS NULL;
```

### 4.2 数据备份

```sql
-- 备份关键表
CREATE TABLE applications_backup AS SELECT * FROM applications;
CREATE TABLE interviews_backup AS SELECT * FROM interviews;
CREATE TABLE application_status_history_backup AS SELECT * FROM application_status_history;
```

### 4.3 迁移后验证

```sql
-- 验证新字段
SELECT 
    COUNT(*) as total,
    COUNT(intention_contact_method) as has_intention_method,
    COUNT(interview_confirmation_token) as has_confirmation_token
FROM applications;

-- 验证新表
SELECT COUNT(*) FROM interviewer_screenings;
SELECT COUNT(*) FROM assessments;

-- 验证索引
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename IN ('applications', 'interviews', 'interviewer_screenings', 'assessments')
ORDER BY tablename, indexname;
```

---

## 五、性能监控查询

### 5.1 慢查询监控

```sql
-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- 查看未使用的索引
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0 
AND schemaname = 'public';
```

---

**文档版本**: v2.0
**创建时间**: 2026-05-30
**状态**: 数据库设计完成
