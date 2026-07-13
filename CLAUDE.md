# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DeepHire is a production-ready AI recruiting system with a lightweight, modern architecture. This is **not a demo or toy project** - all code must be functional, production-ready, and follow the established patterns.

**Core Philosophy:**
- Lightweight over enterprise complexity
- Modern SaaS UX (think Linear, Ashby) over traditional HR systems
- Three roles only: HR, Recruiter, Interviewer
- Core focus: recruiting collaboration, resume search, candidate activation

## Architecture

**Monorepo Structure:**
```
DeepHire/
├── frontend/          # Next.js 16.2.6 + TypeScript + Tailwind + shadcn/ui
├── backend/           # FastAPI + PostgreSQL + Redis + OpenSearch
└── docker-compose.yml # Orchestration for all services
```

**Backend Stack:**
- FastAPI with async/await patterns
- SQLAlchemy ORM with Alembic migrations
- PostgreSQL for relational data
- Redis for caching and session management
- OpenSearch for hybrid search (BM25 + vector embeddings)
- OpenAI-compatible API for resume parsing and AI features

**Frontend Stack:**
- Next.js 16.2.6 with App Router and Turbopack
- TypeScript with strict type checking
- Tailwind CSS for styling
- shadcn/ui for component library
- next-intl for i18n support
- framer-motion for micro-interactions (use sparingly)

## Development Commands

### Initial Setup

**Option 1: Docker (Recommended for first-time setup)**
```bash
# Start all services
docker-compose up -d

# Initialize database with seed data
docker exec -it deephire-backend python init_db.py

# Sync OpenSearch indexes
docker exec -it deephire-backend python sync_opensearch.py

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/api/docs
# - OpenSearch: http://localhost:9200
```

**Option 2: Local Development**
```bash
# Start infrastructure only
docker-compose up -d postgres redis opensearch

# Backend setup (in backend/)
conda create -n deephire python=3.11 -y
conda activate deephire
pip install -r requirements.txt
cp .env.example .env  # Edit with your OPENAI_API_KEY
python init_db.py
python sync_opensearch.py
uvicorn app.main:app --reload --port 8000

# Frontend setup (in frontend/)
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### Daily Development

```bash
# Backend (terminal 1)
cd backend
conda activate deephire
uvicorn app.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend
npm run dev
```

### Testing & Validation

```bash
# Backend
cd backend
python -m pytest  # When tests are added

# Frontend
cd frontend
npm run lint
npm run build  # Verify production build

# Check API health
curl http://localhost:8000/health
```

### Database Management

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Reset database (development only)
python init_db.py
```

### Search Index Management

```bash
cd backend

# Rebuild OpenSearch indexes
python sync_opensearch.py

# Check index health
curl http://localhost:9200/_cat/indices
```

## Backend Architecture

### Directory Structure
```
backend/app/
├── api/v1/endpoints/    # API route handlers
│   ├── auth.py
│   ├── candidates.py
│   ├── resumes.py
│   ├── applications.py  # Candidate application workflow
│   ├── interviewer_screenings.py
│   ├── hr_interviews.py
│   ├── department_interviews.py
│   ├── final_interviews.py
│   ├── assessments.py
│   ├── offers.py
│   └── outbound_calls.py
├── models/              # SQLAlchemy models
│   ├── user.py
│   ├── candidate.py
│   ├── job.py
│   ├── application.py   # Core recruitment workflow model
│   └── interview.py
├── services/            # Business logic layer
│   ├── resume_parser.py           # PDF/DOCX parsing with AI
│   ├── search_service.py          # Hybrid search implementation
│   ├── llm_client.py              # OpenAI client wrapper
│   ├── application_state_machine.py  # Workflow state transitions
│   └── *_service.py               # Feature-specific services
├── core/
│   ├── config.py        # Settings with pydantic-settings
│   └── security.py      # JWT, password hashing
└── db/
    └── session.py       # Database session management
```

### Key Patterns

**State Machine Workflow:**
The recruitment process uses a state machine pattern (`application_state_machine.py`) to manage transitions through:
1. Resume submission → Screening
2. HR Interview → Department Interview → Final Interview
3. Assessment → Offer → Onboarding

**Hybrid Search Architecture:**
- PostgreSQL filters for structured queries (location, years of experience, etc.)
- OpenSearch BM25 for keyword matching
- Vector embeddings (sentence-transformers) for semantic search
- Reranking for final result ordering

**LLM Integration:**
- Resume parsing extracts structured data from PDFs/DOCX
- Candidate activation generates communication scripts
- All LLM calls use OpenAI-compatible API (configurable base URL)

### API Conventions

- All endpoints under `/api/v1/`
- JWT authentication with role-based access control
- Pydantic schemas for request/response validation
- Async/await for all database and external API calls
- Type hints required on all functions

## Frontend Architecture

### Directory Structure
```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/login/      # Auth pages
│   ├── dashboard/         # Role-based dashboards
│   │   ├── hr/
│   │   ├── recruiter/
│   │   └── interviewer/
│   ├── candidates/        # Candidate management
│   ├── jobs/              # Job postings
│   ├── search/            # Hybrid search UI
│   └── activation/        # Candidate activation
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── candidates/        # Feature components
│   ├── auth/
│   ├── layout/
│   └── recruiter/
└── lib/
    ├── api.ts             # API client with axios
    └── utils.ts           # Shared utilities
```

### UI/UX Principles

**Critical:** This system must have a modern SaaS feel, not a traditional HR admin panel.

- **High information density** without clutter
- **Minimal clicks** to complete actions
- **Card-based layouts** over tables where appropriate
- **Smooth micro-interactions** (hover states, transitions)
- **Premium typography** with proper hierarchy
- **Generous whitespace** and clear visual grouping

**Reference Products:**
- Linear (for workflow efficiency)
- Ashby ATS (for recruiting UX)
- Notion (for information density)

**Avoid:**
- Bootstrap-style admin panels
- Complex gradients or flashy animations
- Table-heavy interfaces
- Traditional enterprise software aesthetics

### Component Standards

- Use shadcn/ui components as the foundation
- All components must be TypeScript with proper types
- Use Tailwind CSS utility classes (avoid custom CSS)
- Loading states with skeleton loaders
- Empty states with helpful messaging
- Error boundaries for graceful degradation

## Role-Based Access

**HR:**
- Full access to all candidates, jobs, and interviews
- Can assign candidates to recruiters
- Dashboard shows: open jobs, all candidates, today's interviews, recruitment pipeline

**Recruiter:**
- Access only to assigned candidates
- Can upload resumes, search candidates, update statuses
- Dashboard shows: my candidates, my jobs, today's contacts, communication history

**Interviewer:**
- Minimal interface - only today's scheduled interviews
- Can view candidate details and submit interview feedback
- Dashboard shows: today's interview schedule only

## Key Features Implementation Notes

### Resume Parsing
- Supports PDF and DOCX formats
- Uses LLM (OpenAI-compatible) for structured extraction
- Extracts: name, contact, experience, skills, education, industry
- Results stored in PostgreSQL, indexed in OpenSearch

### Semantic Search
- Natural language queries like "找做过医疗器械销售的人"
- Hybrid approach: structured filters + BM25 + vector search
- Must return results in <1 second for good UX
- Implements reranking for result quality

### Candidate Activation
- Semi-automated approach (no real-time voice agents in MVP)
- AI generates communication scripts for recruiters
- Tracks contact history and status updates
- Updates reflected in candidate timeline

## Demo Accounts

Always use these accounts for testing:
- **HR**: hr@deephire.com / password
- **Recruiter**: recruiter@deephire.com / password
- **Interviewer**: interviewer@deephire.com / password

## Development Workflow

### Adding New Features

1. **Backend-first approach:**
   - Define SQLAlchemy models in `backend/app/models/`
   - Create Alembic migration: `alembic revision --autogenerate -m "description"`
   - Implement service layer in `backend/app/services/`
   - Add API endpoints in `backend/app/api/v1/endpoints/`
   - Test with FastAPI docs at `/api/docs`

2. **Frontend integration:**
   - Add API client methods in `frontend/lib/api.ts`
   - Create UI components following shadcn/ui patterns
   - Implement pages under appropriate `app/` directory
   - Test user flow across different roles

### Code Quality Standards

- **No placeholders or TODOs** - all code must be production-ready
- **Type safety** - TypeScript/Python type hints everywhere
- **Follow existing patterns** - match the project's conventions
- **Test before committing** - verify features work end-to-end

### Common Pitfalls

- Don't create generic CRUD interfaces - each feature has specific UX requirements
- Don't add enterprise features (approval workflows, complex RBAC, org hierarchies)
- Don't use traditional table layouts when cards would be more modern
- Don't skip loading/empty states - they're critical for perceived performance
- Don't introduce new dependencies without verifying alignment with tech stack

## Environment Variables

### Backend (.env)
Required:
- `OPENAI_API_KEY` - For resume parsing and AI features
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (change in production)

Optional:
- `OPENAI_BASE_URL` - For using API proxies or alternative providers
- `REDIS_URL` - Defaults to localhost:6379
- `OPENSEARCH_HOST` - Defaults to localhost
- `CORS_ORIGINS` - Frontend URLs for CORS

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API endpoint (http://localhost:8000)

## Troubleshooting

**Database connection issues:**
```bash
docker-compose ps postgres  # Check if running
docker-compose restart postgres
```

**OpenSearch memory issues:**
```bash
# macOS
sudo sysctl -w vm.max_map_count=262144
```

**Frontend can't reach backend:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS_ORIGINS in backend/.env includes frontend URL
- Verify NEXT_PUBLIC_API_URL in frontend/.env.local

**Resume parsing failures:**
- Verify OPENAI_API_KEY is set correctly
- Check backend logs: `docker-compose logs backend`
- Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

## Important Context

This system is designed for **2-6 week MVP development** with a focus on shipping production-ready code. The architecture supports scaling to 100K+ resumes while maintaining sub-second search performance through the hybrid search approach.

When working on this codebase:
- Prioritize user efficiency over technical complexity
- Keep the UX modern and premium
- Follow the existing patterns strictly
- All code must be functional and tested
- No enterprise bloat - stay lightweight and focused
