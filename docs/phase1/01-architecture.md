# Phase 1: 系统架构设计

## 1. 总体系统架构

### 1.1 架构模式

采用 **前后端分离 + 微服务化** 架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│                  Next.js 15 + TypeScript                     │
│              (SSR + Client-side Rendering)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓ REST API
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│                      FastAPI + Python                        │
│              (Authentication + Rate Limiting)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬──────────────────────┐
│  Business Logic  │   AI Services    │   Search Engine      │
│   FastAPI Core   │  Resume Parser   │   OpenSearch         │
│                  │  Semantic Search │   (BM25 + Vector)    │
└──────────────────┴──────────────────┴──────────────────────┘
                              ↓
┌──────────────────┬──────────────────┬──────────────────────┐
│   PostgreSQL     │      Redis       │    Object Storage    │
│  (Primary DB)    │   (Cache+Queue)  │   (Resume Files)     │
└──────────────────┴──────────────────┴──────────────────────┘
```

### 1.2 为什么这样设计？

**前后端分离**：
- 前端专注产品体验，后端专注业务逻辑
- 支持未来移动端扩展
- 开发效率高，职责清晰

**PostgreSQL 作为主数据库**：
- 支持复杂查询和事务
- JSONB 字段支持灵活的简历数据存储
- 成熟稳定，运维成本低
- pgvector 扩展支持向量存储

**OpenSearch 作为搜索引擎**：
- 支持 BM25 全文搜索
- 支持向量搜索（语义搜索）
- 支持 Hybrid Search（组合搜索）
- 可扩展到百万级简历

**Redis 作为缓存层**：
- 缓存热点数据（候选人列表、搜索结果）
- 支持异步任务队列（简历解析）
- Session 存储

**Object Storage**：
- 存储原始简历文件（PDF/DOCX）
- 第一版可以用本地文件系统
- 未来可以迁移到 S3/OSS

---

## 2. 数据流设计

### 2.1 简历上传与解析流程

```
User Upload Resume (PDF/DOCX)
         ↓
Frontend → API: POST /api/resumes/upload
         ↓
Backend: Save file to Object Storage
         ↓
Backend: Create Resume record (status: parsing)
         ↓
Backend: Push to Redis Queue
         ↓
Worker: Parse resume with AI
         ↓
Worker: Extract structured data
         ↓
Worker: Save to PostgreSQL
         ↓
Worker: Generate embedding
         ↓
Worker: Index to OpenSearch
         ↓
Worker: Update status (status: completed)
         ↓
Frontend: Poll or WebSocket notification
```

**为什么异步处理？**
- 简历解析需要调用 AI，耗时较长（5-30秒）
- 避免阻塞用户操作
- 支持批量上传

### 2.2 简历搜索流程（核心）

```
User Input Search Query
         ↓
Frontend → API: POST /api/candidates/search
         ↓
Backend: Parse query (filters + semantic)
         ↓
Step 1: PostgreSQL Filter
  - years_of_experience
  - location
  - status
  - tags
         ↓
Step 2: OpenSearch Hybrid Search
  - BM25 (keyword matching)
  - Vector Search (semantic matching)
  - Combine scores
         ↓
Step 3: Rerank (optional)
  - Use AI to rerank top 50 results
         ↓
Backend: Return top N candidates
         ↓
Frontend: Display results with match scores
```

**为什么 Hybrid Search？**
- BM25：精确匹配关键词（公司名、技能）
- Vector：语义理解（"医疗器械销售" ≈ "healthcare sales"）
- 组合：召回率高 + 准确率高

### 2.3 候选人激活流程

```
Recruiter selects candidates
         ↓
Frontend → API: POST /api/candidates/activate
  Body: { candidate_ids: [...], job_id: "..." }
         ↓
Backend: Load candidate profiles
         ↓
Backend: Load job description
         ↓
Backend: Generate contact script with AI
  Prompt: "Generate a phone script for contacting 
           [candidate] about [job]"
         ↓
Backend: Return script to Recruiter
         ↓
Recruiter contacts candidate (manual)
         ↓
Recruiter updates status
         ↓
Frontend → API: POST /api/candidates/:id/contact
  Body: { result: "interested", notes: "..." }
         ↓
Backend: Update candidate status
         ↓
Backend: Save to Timeline
         ↓
Backend: Update latest_contacted_at
```

**为什么不做自动拨打？**
- 第一版 MVP，降低复杂度
- 自动拨打需要语音 AI + 电话集成
- Semi-AI 已经能提升效率 80%

---

## 3. 技术架构分层

### 3.1 前端架构

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (Pages + Components + UI)        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         State Management            │
│  (Zustand + TanStack Query)         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         API Client Layer            │
│      (Axios + Type-safe)            │
└─────────────────────────────────────┘
```

**关键决策**：
- **TanStack Query**：管理服务端状态（缓存、重试、乐观更新）
- **Zustand**：管理客户端状态（用户信息、UI 状态）
- **不用 Redux**：太重，Zustand 足够

### 3.2 后端架构

```
┌─────────────────────────────────────┐
│          API Layer                  │
│    (FastAPI Routes + Validation)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        Service Layer                │
│     (Business Logic)                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Repository Layer               │
│   (Database Access + ORM)           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Infrastructure Layer           │
│  (PostgreSQL + Redis + OpenSearch)  │
└─────────────────────────────────────┘
```

**关键决策**：
- **三层架构**：API → Service → Repository
- **依赖注入**：使用 FastAPI 的 Depends
- **不用微服务**：第一版 Monolith 足够，后续可拆分

---

## 4. 扩展性设计

### 4.1 数据库扩展

**当前（10K 简历）**：
- 单机 PostgreSQL
- 单机 OpenSearch

**未来（100万+ 简历）**：
- PostgreSQL 主从复制
- OpenSearch 集群（3+ 节点）
- 分库分表（按时间或地区）

### 4.2 搜索扩展

**当前**：
- OpenSearch 单节点
- 所有数据在一个索引

**未来**：
- OpenSearch 集群
- 按行业/地区分索引
- 冷热数据分离

### 4.3 AI 服务扩展

**当前**：
- 同步调用 OpenAI API
- 简单重试机制

**未来**：
- 异步队列处理
- 批量处理
- 自建模型服务

---

## 5. 安全设计

### 5.1 认证与授权

**认证**：
- JWT Token
- Access Token (15分钟) + Refresh Token (7天)
- HttpOnly Cookie 存储

**授权**：
- 基于角色的访问控制（RBAC）
- 三种角色：HR、Recruiter、Interviewer
- API 级别权限检查

### 5.2 数据安全

**敏感数据**：
- 密码：bcrypt 加密
- 简历文件：访问控制
- 个人信息：脱敏展示

**API 安全**：
- Rate Limiting（每分钟 100 请求）
- CORS 配置
- SQL 注入防护（ORM）
- XSS 防护（前端转义）

---

## 6. 性能优化

### 6.1 前端性能

- **代码分割**：Next.js 自动分割
- **图片优化**：Next.js Image 组件
- **缓存策略**：TanStack Query 缓存
- **懒加载**：React.lazy + Suspense

### 6.2 后端性能

- **数据库索引**：关键字段建索引
- **Redis 缓存**：热点数据缓存
- **连接池**：数据库连接池
- **异步处理**：耗时任务异步

### 6.3 搜索性能

- **索引优化**：合理设置分片
- **查询优化**：限制返回字段
- **缓存**：搜索结果缓存 5 分钟
- **分页**：限制每页 20 条

---

## 7. 监控与日志

### 7.1 日志

- **应用日志**：结构化日志（JSON）
- **访问日志**：Nginx 日志
- **错误日志**：Sentry 集成

### 7.2 监控

- **性能监控**：API 响应时间
- **错误监控**：错误率
- **业务监控**：搜索量、上传量

---

## 8. 部署架构

### 8.1 开发环境

```
Docker Compose:
  - frontend (Next.js dev server)
  - backend (FastAPI with hot reload)
  - postgres
  - redis
  - opensearch
```

### 8.2 生产环境

```
┌─────────────┐
│   Nginx     │  (反向代理 + 静态文件)
└─────────────┘
       ↓
┌─────────────┬─────────────┐
│  Frontend   │   Backend   │
│  (Next.js)  │  (FastAPI)  │
└─────────────┴─────────────┘
       ↓
┌─────────────┬─────────────┬─────────────┐
│ PostgreSQL  │    Redis    │ OpenSearch  │
└─────────────┴─────────────┴─────────────┘
```

**部署方式**：
- Docker + Docker Compose
- 单机部署（第一版）
- 未来可迁移到 Kubernetes

---

## 总结

这个架构设计：

✅ **满足当前需求**：支持 10K+ 简历
✅ **可扩展**：可升级到 100万+ 简历
✅ **技术成熟**：使用主流技术栈
✅ **开发效率高**：Monorepo + 清晰分层
✅ **产品体验好**：前端现代化设计
✅ **运维简单**：Docker 部署

下一步：技术选型详细说明
