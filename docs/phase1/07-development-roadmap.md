# Phase 1: 开发 Roadmap

## 1. 开发阶段总览

```
Phase 1: 架构设计 (已完成)          ✅ 1 周
Phase 2: 项目初始化                 ⏱️ 3-5 天
Phase 3: 认证与角色系统             ⏱️ 5-7 天
Phase 4: 候选人模块                 ⏱️ 7-10 天
Phase 5: 简历解析                   ⏱️ 5-7 天
Phase 6: 搜索能力（核心）           ⏱️ 10-14 天
Phase 7: AI 短信激活系统（核心）    ⏱️ 10-15 天 ⭐ 新增
Phase 8: 面试模块                   ⏱️ 5-7 天
Phase 9: 优化与部署                 ⏱️ 3-5 天
───────────────────────────────────────────
总计：                              10-13 周
```

**为什么这样安排？**
- 先做基础，再做核心功能
- 搜索 + AI 激活是核心竞争力，分配时间最多
- AI 短信激活是差异化功能 ⭐
- 每个阶段可独立测试
- 支持迭代开发

---

## 2. Phase 2: 项目初始化（3-5 天）

### 2.1 目标

搭建完整的开发环境，确保前后端可以运行。

### 2.2 任务清单

#### Day 1: 项目结构

- [ ] 创建 Monorepo 目录结构
- [ ] 初始化 Git 仓库
- [ ] 配置 .gitignore
- [ ] 创建 README.md

#### Day 2: Frontend 初始化

- [ ] 创建 Next.js 15 项目
- [ ] 配置 TypeScript
- [ ] 配置 Tailwind CSS
- [ ] 安装 shadcn/ui
- [ ] 配置 ESLint + Prettier
- [ ] 创建基础布局组件
- [ ] 测试运行：`npm run dev`

#### Day 3: Backend 初始化

- [ ] 创建 FastAPI 项目
- [ ] 配置 Python 虚拟环境
- [ ] 安装依赖（requirements.txt）
- [ ] 配置数据库连接（PostgreSQL）
- [ ] 配置 Alembic 迁移
- [ ] 创建健康检查 API
- [ ] 测试运行：`uvicorn app.main:app --reload`

#### Day 4: Docker 配置

- [ ] 编写 Dockerfile（frontend）
- [ ] 编写 Dockerfile（backend）
- [ ] 编写 docker-compose.yml
- [ ] 配置 PostgreSQL 容器
- [ ] 配置 Redis 容器
- [ ] 配置 OpenSearch 容器
- [ ] 测试运行：`docker-compose up`

#### Day 5: 基础设施

- [ ] 配置环境变量
- [ ] 配置日志系统
- [ ] 配置 CORS
- [ ] 前后端联调测试
- [ ] 编写初始化脚本

### 2.3 验收标准

✅ 前端可以访问：http://localhost:3000
✅ 后端可以访问：http://localhost:8000/docs
✅ 数据库连接成功
✅ Docker 环境运行正常
✅ 前后端可以通信

---

## 3. Phase 3: 认证与角色系统（5-7 天）

### 3.1 目标

实现用户登录、JWT 认证、角色权限控制。

### 3.2 任务清单

#### Day 1-2: 数据库与模型

- [ ] 创建 users 表迁移
- [ ] 创建 User Model（SQLAlchemy）
- [ ] 创建 User Schema（Pydantic）
- [ ] 实现密码加密（bcrypt）
- [ ] 创建初始用户（seed data）

#### Day 3-4: 后端认证 API

- [ ] 实现 POST /api/v1/auth/login
- [ ] 实现 POST /api/v1/auth/refresh
- [ ] 实现 GET /api/v1/auth/me
- [ ] 实现 JWT Token 生成
- [ ] 实现认证中间件
- [ ] 实现权限检查装饰器
- [ ] 编写单元测试

#### Day 5-6: 前端登录页面

- [ ] 创建登录页面 UI
- [ ] 实现登录表单（React Hook Form + Zod）
- [ ] 实现 API 调用
- [ ] 实现 Token 存储（Cookie）
- [ ] 实现自动刷新 Token
- [ ] 实现路由守卫
- [ ] 实现登出功能

#### Day 7: 角色系统

- [ ] 实现角色路由守卫
- [ ] HR Dashboard 页面
- [ ] Recruiter Dashboard 页面
- [ ] Interviewer Dashboard 页面
- [ ] 测试不同角色权限

### 3.3 验收标准

✅ 用户可以登录
✅ JWT Token 正常工作
✅ 不同角色看到不同页面
✅ 未登录用户被重定向到登录页
✅ Token 过期自动刷新

---

## 4. Phase 4: 候选人模块（7-10 天）

### 4.1 目标

实现候选人的 CRUD、列表、详情、状态管理。

### 4.2 任务清单

#### Day 1-2: 数据库与模型

- [ ] 创建 candidates 表迁移
- [ ] 创建 timelines 表迁移
- [ ] 创建 notes 表迁移
- [ ] 创建 attachments 表迁移
- [ ] 创建对应的 Models 和 Schemas

#### Day 3-4: 后端 API

- [ ] POST /api/v1/candidates（创建候选人）
- [ ] GET /api/v1/candidates（列表）
- [ ] GET /api/v1/candidates/:id（详情）
- [ ] PUT /api/v1/candidates/:id（更新）
- [ ] PATCH /api/v1/candidates/:id/status（状态更新）
- [ ] POST /api/v1/candidates/:id/tags（标签）
- [ ] GET /api/v1/candidates/:id/timeline（时间线）
- [ ] POST /api/v1/candidates/:id/notes（备注）
- [ ] 实现 Repository 层
- [ ] 实现 Service 层
- [ ] 编写单元测试

#### Day 5-7: 前端候选人列表

- [ ] 创建候选人列表页面
- [ ] 实现 CandidateCard 组件
- [ ] 实现过滤器（状态、标签、地区）
- [ ] 实现排序
- [ ] 实现分页
- [ ] 实现 Loading Skeleton
- [ ] 实现 Empty State
- [ ] 集成 TanStack Query

#### Day 8-10: 前端候选人详情

- [ ] 创建候选人详情页面
- [ ] 实现三栏布局
- [ ] 实现基础信息展示
- [ ] 实现 Timeline 组件
- [ ] 实现 Notes 组件
- [ ] 实现状态更新
- [ ] 实现标签管理
- [ ] 实现编辑功能

### 4.3 验收标准

✅ 可以创建候选人
✅ 可以查看候选人列表
✅ 可以查看候选人详情
✅ 可以更新候选人状态
✅ 可以添加标签和备注
✅ Timeline 正常工作

---

## 5. Phase 5: 简历解析（5-7 天）

### 5.1 目标

实现简历上传、解析、结构化存储。

### 5.2 任务清单

#### Day 1-2: 数据库与文件存储

- [ ] 创建 resumes 表迁移
- [ ] 配置文件上传目录
- [ ] 实现文件上传工具
- [ ] 实现 PDF 解析（PyPDF2）
- [ ] 实现 DOCX 解析（python-docx）

#### Day 3-4: AI 简历解析

- [ ] 编写简历解析 Prompt
- [ ] 实现 OpenAI API 调用
- [ ] 实现结构化数据提取
- [ ] 实现解析结果验证
- [ ] 实现错误处理和重试
- [ ] 实现异步解析（BackgroundTasks）
- [ ] 编写单元测试

#### Day 5: 后端 API

- [ ] POST /api/v1/resumes/upload
- [ ] GET /api/v1/resumes/:id/status
- [ ] POST /api/v1/resumes/:id/reparse
- [ ] 实现解析状态管理
- [ ] 实现解析结果存储

#### Day 6-7: 前端上传组件

- [ ] 创建 ResumeUpload 组件
- [ ] 实现拖拽上传
- [ ] 实现文件验证（类型、大小）
- [ ] 实现上传进度
- [ ] 实现解析状态轮询
- [ ] 实现解析结果展示
- [ ] 集成到候选人创建流程

### 5.3 验收标准

✅ 可以上传 PDF 和 DOCX
✅ 简历自动解析
✅ 解析结果结构化存储
✅ 解析失败有错误提示
✅ 可以重新解析

---

## 6. Phase 6: 搜索能力（10-14 天）- 核心

### 6.1 目标

实现 Hybrid Search（BM25 + Vector Search）。

### 6.2 任务清单

#### Day 1-2: OpenSearch 配置

- [ ] 配置 OpenSearch 容器
- [ ] 创建 candidates 索引
- [ ] 配置 Mapping（字段类型）
- [ ] 配置中文分词器
- [ ] 测试索引创建

#### Day 3-4: 索引管理

- [ ] 实现 OpenSearch 客户端
- [ ] 实现索引器（Indexer）
- [ ] 实现候选人数据索引
- [ ] 实现增量索引更新
- [ ] 实现批量索引
- [ ] 编写单元测试

#### Day 5-6: 向量搜索

- [ ] 实现 Embedding 生成（OpenAI）
- [ ] 实现向量存储（PostgreSQL pgvector）
- [ ] 实现向量相似度搜索
- [ ] 优化向量生成成本
- [ ] 编写单元测试

#### Day 7-8: Hybrid Search

- [ ] 实现 BM25 搜索
- [ ] 实现 Vector Search
- [ ] 实现 Hybrid Search（组合）
- [ ] 实现 Reranker（可选）
- [ ] 实现 Match Reasons 生成
- [ ] 优化搜索性能
- [ ] 编写单元测试

#### Day 9-10: 后端搜索 API

- [ ] POST /api/v1/candidates/search
- [ ] 实现查询解析
- [ ] 实现过滤器（PostgreSQL）
- [ ] 实现搜索模式切换
- [ ] 实现结果排序
- [ ] 实现分页
- [ ] 实现缓存（Redis）
- [ ] 编写单元测试

#### Day 11-14: 前端搜索页面

- [ ] 创建搜索页面
- [ ] 实现超大搜索框
- [ ] 实现 Filter Chips
- [ ] 实现搜索模式切换
- [ ] 实现搜索结果展示
- [ ] 实现 Match Score 展示
- [ ] 实现 Match Reasons 展示
- [ ] 实现搜索历史
- [ ] 实现保存搜索
- [ ] 优化搜索体验

### 6.3 验收标准

✅ 自然语言搜索正常工作
✅ 关键词搜索正常工作
✅ Hybrid Search 正常工作
✅ 搜索结果准确
✅ 搜索速度 < 500ms
✅ Match Score 和 Reasons 正确

---

## 7. Phase 7: 面试模块（5-7 天）

### 7.1 目标

实现面试安排、面试反馈、面试列表。

### 7.2 任务清单

#### Day 1-2: 数据库与模型

- [ ] 创建 interviews 表迁移
- [ ] 创建 Interview Model 和 Schema
- [ ] 创建 candidate_jobs 表迁移

#### Day 3-4: 后端 API

- [ ] POST /api/v1/interviews（创建面试）
- [ ] GET /api/v1/interviews（列表）
- [ ] GET /api/v1/interviews/:id（详情）
- [ ] PUT /api/v1/interviews/:id（更新）
- [ ] POST /api/v1/interviews/:id/feedback（反馈）
- [ ] POST /api/v1/interviews/:id/cancel（取消）
- [ ] 实现面试提醒（可选）
- [ ] 编写单元测试

#### Day 5-6: 前端面试列表

- [ ] 创建面试列表页面
- [ ] 实现 InterviewCard 组件
- [ ] 实现日历视图（可选）
- [ ] 实现过滤器
- [ ] 实现 Interviewer Dashboard

#### Day 7: 前端面试反馈

- [ ] 创建面试反馈页面
- [ ] 实现评分组件
- [ ] 实现反馈表单
- [ ] 实现结果选择
- [ ] 集成到面试流程

### 7.3 验收标准

✅ 可以创建面试
✅ 可以查看面试列表
✅ Interviewer 可以看到今日面试
✅ 可以提交面试反馈
✅ 可以取消面试

---

## 8. Phase 8: 优化与部署（3-5 天）

### 8.1 目标

优化性能、修复 Bug、部署上线。

### 8.2 任务清单

#### Day 1: 性能优化

- [ ] 前端代码分割
- [ ] 图片优化
- [ ] API 响应时间优化
- [ ] 数据库查询优化
- [ ] 缓存优化
- [ ] 搜索性能优化

#### Day 2: 测试

- [ ] 前端 E2E 测试（可选）
- [ ] 后端集成测试
- [ ] 手动测试所有功能
- [ ] 修复发现的 Bug

#### Day 3: 部署准备

- [ ] 编写生产环境 Dockerfile
- [ ] 编写 docker-compose.prod.yml
- [ ] 配置 Nginx
- [ ] 配置 SSL（可选）
- [ ] 配置环境变量
- [ ] 编写部署脚本

#### Day 4: 部署

- [ ] 部署到服务器
- [ ] 配置域名
- [ ] 配置数据库备份
- [ ] 配置日志收集
- [ ] 配置监控（可选）

#### Day 5: 验收

- [ ] 生产环境测试
- [ ] 性能测试
- [ ] 安全检查
- [ ] 文档完善

### 8.3 验收标准

✅ 所有功能正常工作
✅ 性能达标
✅ 部署成功
✅ 文档完善

---

## 9. 职位模块（可选，Phase 4.5）

如果时间允许，可以在 Phase 4 和 Phase 5 之间插入职位模块。

### 9.1 任务清单（3-5 天）

#### Day 1-2: 数据库与 API

- [ ] 创建 jobs 表迁移
- [ ] 创建 Job Model 和 Schema
- [ ] POST /api/v1/jobs
- [ ] GET /api/v1/jobs
- [ ] GET /api/v1/jobs/:id
- [ ] PUT /api/v1/jobs/:id
- [ ] PATCH /api/v1/jobs/:id/status

#### Day 3-5: 前端

- [ ] 创建职位列表页面
- [ ] 创建职位详情页面
- [ ] 创建职位表单
- [ ] 实现职位状态管理

---

## 10. 候选人激活（可选，Phase 6.5）

如果时间允许，可以在 Phase 6 之后添加。

### 10.1 任务清单（3-5 天）

#### Day 1-2: AI 脚本生成

- [ ] 编写联系脚本 Prompt
- [ ] 实现脚本生成 API
- [ ] POST /api/v1/candidates/activate/generate-script
- [ ] 编写单元测试

#### Day 3-4: 前端

- [ ] 创建批量选择功能
- [ ] 创建脚本生成对话框
- [ ] 实现联系结果记录
- [ ] 集成到搜索页面

#### Day 5: 测试

- [ ] 测试脚本生成质量
- [ ] 测试联系流程
- [ ] 优化 Prompt

---

## 11. 里程碑

### Milestone 1: 基础设施（Week 1）
- ✅ 项目初始化
- ✅ 认证系统

### Milestone 2: 核心功能（Week 2-4）
- ✅ 候选人模块
- ✅ 简历解析
- ✅ 搜索能力

### Milestone 3: 完整功能（Week 5-6）
- ✅ 面试模块
- ✅ 职位模块（可选）
- ✅ 候选人激活（可选）

### Milestone 4: 上线（Week 7-8）
- ✅ 优化
- ✅ 测试
- ✅ 部署

---

## 12. 风险与应对

### 12.1 技术风险

**风险 1：OpenSearch 配置复杂**
- 应对：先用 PostgreSQL 全文搜索，后续再迁移

**风险 2：AI 解析不准确**
- 应对：优化 Prompt，增加验证逻辑

**风险 3：搜索性能不达标**
- 应对：优化索引，增加缓存

### 12.2 时间风险

**风险：开发时间超出预期**
- 应对：优先完成核心功能，可选功能后续迭代

---

## 13. 每日工作流程

### 13.1 开发流程

1. **早上**：
   - 查看任务清单
   - 确定今日目标

2. **开发**：
   - 先写测试（TDD，可选）
   - 实现功能
   - 自测

3. **下午**：
   - Code Review（如果有团队）
   - 集成测试
   - 文档更新

4. **晚上**：
   - 提交代码
   - 更新进度
   - 规划明日任务

### 13.2 Git 工作流

```bash
# 创建功能分支
git checkout -b feature/candidate-list

# 开发...

# 提交
git add .
git commit -m "feat: implement candidate list"

# 合并到 main
git checkout main
git merge feature/candidate-list
```

---

## 14. 总结

这个 Roadmap：

✅ **分阶段开发**：每个阶段独立可测试
✅ **优先级清晰**：核心功能优先
✅ **时间合理**：6-8 周完成 MVP
✅ **可调整**：支持功能裁剪
✅ **风险可控**：有应对方案

**关键成功因素**：
1. 严格按照阶段推进
2. 每个阶段完成后验收
3. 不要过度设计
4. 保持代码质量
5. 及时测试和修复

下一步：风险分析
