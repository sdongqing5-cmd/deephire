# Phase 1: 项目目录结构

## 1. Monorepo 结构

```
DeepHire/
├── frontend/                 # Next.js 前端
├── backend/                  # FastAPI 后端
├── shared/                   # 共享代码
├── docs/                     # 文档
├── docker/                   # Docker 配置
├── scripts/                  # 脚本工具
├── .github/                  # GitHub Actions
├── docker-compose.yml        # 开发环境
├── docker-compose.prod.yml   # 生产环境
├── .gitignore
├── README.md
└── PROJECT_BRIEF.md          # 项目需求文档
```

**为什么 Monorepo？**
- 前后端代码在一个仓库
- 共享类型定义
- 统一版本管理
- 简化部署流程

---

## 2. Frontend 目录结构

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/                   # 认证路由组
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── (dashboard)/              # Dashboard 路由组
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── jobs/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── new/
│   │   │   │       └── page.tsx
│   │   │   ├── search/
│   │   │   │   └── page.tsx          # 核心搜索页面
│   │   │   ├── candidates/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── interviews/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── feedback/
│   │   │   │           └── page.tsx
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx            # Dashboard 布局
│   │   │
│   │   ├── api/                      # API Routes (可选)
│   │   │   └── health/
│   │   │       └── route.ts
│   │   │
│   │   ├── layout.tsx                # Root Layout
│   │   ├── page.tsx                  # Home (redirect)
│   │   └── globals.css
│   │
│   ├── components/                   # React 组件
│   │   ├── ui/                       # shadcn/ui 组件
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── select.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                   # 布局组件
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── DashboardLayout.tsx
│   │   │   └── AuthLayout.tsx
│   │   │
│   │   ├── candidates/               # 候选人相关组件
│   │   │   ├── CandidateCard.tsx
│   │   │   ├── CandidateList.tsx
│   │   │   ├── CandidateDetail.tsx
│   │   │   ├── CandidateTimeline.tsx
│   │   │   ├── CandidateNotes.tsx
│   │   │   └── CandidateStatusBadge.tsx
│   │   │
│   │   ├── search/                   # 搜索相关组件
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchFilters.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   ├── FilterChip.tsx
│   │   │   └── MatchScoreBadge.tsx
│   │   │
│   │   ├── jobs/                     # 职位相关组件
│   │   │   ├── JobCard.tsx
│   │   │   ├── JobList.tsx
│   │   │   ├── JobForm.tsx
│   │   │   └── JobStatusBadge.tsx
│   │   │
│   │   ├── interviews/               # 面试相关组件
│   │   │   ├── InterviewCard.tsx
│   │   │   ├── InterviewList.tsx
│   │   │   ├── InterviewCalendar.tsx
│   │   │   ├── FeedbackForm.tsx
│   │   │   └── ScoreRating.tsx
│   │   │
│   │   ├── dashboard/                # Dashboard 组件
│   │   │   ├── StatsCard.tsx
│   │   │   ├── QuickActions.tsx
│   │   │   ├── RecentActivities.tsx
│   │   │   └── UpcomingInterviews.tsx
│   │   │
│   │   ├── resume/                   # 简历相关组件
│   │   │   ├── ResumeUpload.tsx
│   │   │   ├── ResumeViewer.tsx
│   │   │   └── ParsedResumeDisplay.tsx
│   │   │
│   │   └── common/                   # 通用组件
│   │       ├── LoadingSkeleton.tsx
│   │       ├── EmptyState.tsx
│   │       ├── ErrorBoundary.tsx
│   │       ├── Pagination.tsx
│   │       └── ConfirmDialog.tsx
│   │
│   ├── lib/                          # 工具库
│   │   ├── api/                      # API 客户端
│   │   │   ├── client.ts             # Axios 实例
│   │   │   ├── auth.ts               # 认证 API
│   │   │   ├── candidates.ts         # 候选人 API
│   │   │   ├── jobs.ts               # 职位 API
│   │   │   ├── search.ts             # 搜索 API
│   │   │   ├── interviews.ts         # 面试 API
│   │   │   └── dashboard.ts          # Dashboard API
│   │   │
│   │   ├── hooks/                    # Custom Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useCandidates.ts
│   │   │   ├── useSearch.ts
│   │   │   ├── useJobs.ts
│   │   │   └── useInterviews.ts
│   │   │
│   │   ├── store/                    # Zustand Store
│   │   │   ├── authStore.ts
│   │   │   ├── uiStore.ts
│   │   │   └── searchStore.ts
│   │   │
│   │   ├── utils/                    # 工具函数
│   │   │   ├── cn.ts                 # classnames 合并
│   │   │   ├── date.ts               # 日期格式化
│   │   │   ├── format.ts             # 格式化工具
│   │   │   └── validation.ts         # 验证工具
│   │   │
│   │   └── constants/                # 常量
│   │       ├── routes.ts
│   │       ├── status.ts
│   │       └── roles.ts
│   │
│   ├── types/                        # TypeScript 类型
│   │   ├── api.ts                    # API 类型
│   │   ├── candidate.ts
│   │   ├── job.ts
│   │   ├── interview.ts
│   │   ├── user.ts
│   │   └── search.ts
│   │
│   └── styles/                       # 样式文件
│       └── globals.css
│
├── public/                           # 静态资源
│   ├── images/
│   ├── icons/
│   └── favicon.ico
│
├── .env.local                        # 环境变量
├── .env.example
├── .eslintrc.json
├── .prettierrc
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md
```

**为什么这样设计？**

1. **App Router**：
   - 使用 Next.js 15 的 App Router
   - 路由组 `(auth)` 和 `(dashboard)` 分离
   - 清晰的路由结构

2. **组件分类**：
   - `ui/`: shadcn/ui 基础组件
   - `layout/`: 布局组件
   - 按功能模块分组（candidates, jobs, interviews）
   - `common/`: 通用组件

3. **API 客户端**：
   - 按模块分离 API 调用
   - 统一的 Axios 实例
   - 类型安全

4. **Hooks**：
   - 封装业务逻辑
   - 复用性高
   - 与 TanStack Query 集成

5. **Store**：
   - Zustand 管理客户端状态
   - 轻量级
   - 不需要 Provider

---

## 3. Backend 目录结构

```
backend/
├── app/
│   ├── main.py                       # FastAPI 应用入口
│   │
│   ├── api/                          # API 路由
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # 认证路由
│   │   │   ├── candidates.py         # 候选人路由
│   │   │   ├── jobs.py               # 职位路由
│   │   │   ├── resumes.py            # 简历路由
│   │   │   ├── search.py             # 搜索路由（核心）
│   │   │   ├── interviews.py         # 面试路由
│   │   │   ├── dashboard.py          # Dashboard 路由
│   │   │   └── health.py             # 健康检查
│   │   └── deps.py                   # 依赖注入
│   │
│   ├── core/                         # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py                 # 配置管理
│   │   ├── security.py               # 安全相关（JWT, bcrypt）
│   │   ├── database.py               # 数据库连接
│   │   ├── redis.py                  # Redis 连接
│   │   ├── opensearch.py             # OpenSearch 连接
│   │   └── logging.py                # 日志配置
│   │
│   ├── models/                       # SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── candidate.py
│   │   ├── job.py
│   │   ├── resume.py
│   │   ├── candidate_job.py
│   │   ├── interview.py
│   │   ├── timeline.py
│   │   ├── note.py
│   │   └── attachment.py
│   │
│   ├── schemas/                      # Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── candidate.py
│   │   ├── job.py
│   │   ├── resume.py
│   │   ├── interview.py
│   │   ├── search.py
│   │   └── common.py                 # 通用 Schema
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── candidate_service.py
│   │   ├── job_service.py
│   │   ├── resume_service.py
│   │   ├── search_service.py         # 搜索服务（核心）
│   │   ├── interview_service.py
│   │   ├── ai_service.py             # AI 服务
│   │   └── activation_service.py     # 候选人激活服务
│   │
│   ├── repositories/                 # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py                   # 基础 Repository
│   │   ├── user_repository.py
│   │   ├── candidate_repository.py
│   │   ├── job_repository.py
│   │   ├── resume_repository.py
│   │   ├── interview_repository.py
│   │   └── timeline_repository.py
│   │
│   ├── ai/                           # AI 相关
│   │   ├── __init__.py
│   │   ├── resume_parser.py          # 简历解析
│   │   ├── embeddings.py             # 向量生成
│   │   ├── reranker.py               # 重排序
│   │   ├── script_generator.py       # 脚本生成
│   │   └── prompts/                  # Prompt 模板
│   │       ├── resume_parsing.txt
│   │       ├── contact_script.txt
│   │       └── match_reasoning.txt
│   │
│   ├── search/                       # 搜索引擎
│   │   ├── __init__.py
│   │   ├── opensearch_client.py      # OpenSearch 客户端
│   │   ├── indexer.py                # 索引管理
│   │   ├── query_builder.py          # 查询构建
│   │   ├── hybrid_search.py          # Hybrid Search
│   │   └── filters.py                # 过滤器
│   │
│   ├── workers/                      # 后台任务
│   │   ├── __init__.py
│   │   ├── resume_parser_worker.py   # 简历解析 Worker
│   │   └── indexer_worker.py         # 索引 Worker
│   │
│   ├── utils/                        # 工具函数
│   │   ├── __init__.py
│   │   ├── file.py                   # 文件处理
│   │   ├── pdf.py                    # PDF 解析
│   │   ├── docx.py                   # DOCX 解析
│   │   ├── text.py                   # 文本处理
│   │   └── validators.py             # 验证器
│   │
│   ├── middleware/                   # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py                   # 认证中间件
│   │   ├── rate_limit.py             # 限流中间件
│   │   └── logging.py                # 日志中间件
│   │
│   └── tests/                        # 测试
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_candidates.py
│       ├── test_search.py
│       └── test_ai.py
│
├── alembic/                          # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── uploads/                          # 上传文件（开发环境）
│   └── resumes/
│
├── .env                              # 环境变量
├── .env.example
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml                    # Poetry 配置（可选）
├── pytest.ini
└── README.md
```

**为什么这样设计？**

1. **三层架构**：
   - API Layer: 路由和请求处理
   - Service Layer: 业务逻辑
   - Repository Layer: 数据访问

2. **模块化**：
   - 按功能分模块
   - 清晰的职责划分
   - 易于测试

3. **AI 模块独立**：
   - `ai/`: AI 相关功能
   - `search/`: 搜索引擎
   - 便于后续优化

4. **Workers**：
   - 异步任务处理
   - 简历解析
   - 索引更新

---

## 4. Shared 目录结构

```
shared/
├── types/                            # 共享类型定义
│   ├── candidate.ts
│   ├── job.ts
│   ├── interview.ts
│   └── api.ts
│
├── constants/                        # 共享常量
│   ├── status.ts
│   ├── roles.ts
│   └── errors.ts
│
└── utils/                            # 共享工具函数
    └── validation.ts
```

**为什么需要 Shared？**
- 前后端共享类型定义
- 避免重复代码
- 保持一致性

---

## 5. Docker 目录结构

```
docker/
├── frontend/
│   └── Dockerfile
│
├── backend/
│   └── Dockerfile
│
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
│
└── postgres/
    └── init.sql
```

---

## 6. Scripts 目录结构

```
scripts/
├── setup.sh                          # 初始化脚本
├── dev.sh                            # 启动开发环境
├── build.sh                          # 构建脚本
├── deploy.sh                         # 部署脚本
├── seed.sh                           # 数据填充
└── backup.sh                         # 备份脚本
```

---

## 7. 环境变量

### 7.1 Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Auth
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### 7.2 Backend (.env)

```bash
# App
APP_NAME=DeepHire
APP_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/deephire
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenSearch
OPENSEARCH_URL=http://localhost:9200
OPENSEARCH_INDEX=candidates

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

---

## 8. 依赖管理

### 8.1 Frontend (package.json)

```json
{
  "name": "deephire-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.0.0",
    "axios": "^1.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.0.0",
    "@hookform/resolvers": "^3.0.0",
    "date-fns": "^3.0.0",
    "framer-motion": "^11.0.0",
    "lucide-react": "latest",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "tailwindcss": "^3.0.0",
    "postcss": "^8.0.0",
    "autoprefixer": "^10.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.0.0"
  }
}
```

### 8.2 Backend (requirements.txt)

```txt
# FastAPI
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9

# Database
sqlalchemy==2.0.0
alembic==1.13.0
asyncpg==0.29.0
psycopg2-binary==2.9.0

# Redis
redis==5.0.0

# OpenSearch
opensearch-py==2.0.0

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Validation
pydantic==2.0.0
pydantic-settings==2.0.0

# AI
openai==1.0.0
tiktoken==0.7.0

# Resume Parsing
python-docx==1.1.0
PyPDF2==3.0.0
pdfplumber==0.11.0

# Utils
python-dotenv==1.0.0
loguru==0.7.0
httpx==0.27.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.0
pytest-cov==4.1.0
```

---

## 9. Git 结构

### 9.1 .gitignore

```
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Environment
.env
.env.local
.env.*.local

# Build
.next/
dist/
build/

# Uploads
uploads/
*.pdf
*.docx

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
```

---

## 10. 总结

这个项目结构：

✅ **清晰分层**：前端、后端、共享代码分离
✅ **模块化**：按功能模块组织
✅ **可扩展**：易于添加新功能
✅ **可维护**：职责清晰，易于理解
✅ **类型安全**：TypeScript + Pydantic
✅ **测试友好**：结构支持单元测试

下一步：开发 Roadmap
