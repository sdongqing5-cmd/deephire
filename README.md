# DeepHire - AI Recruiting System

A lightweight AI-powered recruiting system built with Next.js and FastAPI.

## Architecture

```
DeepHire/
├── frontend/          # Next.js frontend
├── backend/           # FastAPI backend
└── docker-compose.yml # Docker orchestration
```

## Tech Stack

### Frontend
- Next.js 16.2.6 with Turbopack
- TypeScript
- Tailwind CSS
- shadcn/ui components
- next-intl (i18n)

### Backend
- FastAPI
- PostgreSQL
- Redis
- OpenSearch
- SQLAlchemy ORM

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- OpenSearch: localhost:9200

### Option 2: Local Development

#### Backend

```bash
cd backend

# Create conda environment
conda create -n deephire python=3.11 -y
conda activate deephire

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

## Demo Accounts

- **HR**: hr@deephire.com / password
- **Recruiter**: recruiter@deephire.com / password
- **Interviewer**: interviewer@deephire.com / password

## Features

### Completed
- ✅ Authentication system
- ✅ Role-based dashboards (HR, Recruiter, Interviewer)
- ✅ Candidate management UI
- ✅ Job management UI
- ✅ Interview scheduling UI
- ✅ Search interface
- ✅ Headhunter system (client management, recommendations, HR communication)
- ✅ Backend API structure
- ✅ Docker configuration

### In Progress
- 🚧 Database models and migrations
- 🚧 Real JWT authentication
- 🚧 Candidate CRUD APIs

### Planned
- 📋 Resume parsing (PDF/DOCX)
- 📋 Semantic search (Hybrid: BM25 + Vector + Reranker)
- 📋 AI-powered candidate activation
- 📋 Interview scorecard system
- 📋 Email notifications

## Project Status

**Phase 2 Complete**: Backend initialization and Docker setup

**Next**: Phase 3 - Database models and authentication

## Development

### Backend Structure

```
backend/app/
├── api/v1/
│   ├── endpoints/
│   │   ├── auth.py
│   │   ├── candidates.py
│   │   ├── jobs.py
│   │   └── interviews.py
│   └── api.py
├── core/
│   ├── config.py
│   └── security.py
└── main.py
```

### Frontend Structure

```
frontend/
├── app/
│   ├── (auth)/login/
│   ├── dashboard/
│   │   ├── hr/
│   │   ├── recruiter/
│   │   └── interviewer/
│   ├── candidates/
│   └── search/
├── components/
└── lib/
```

## Contributing

This is a production-ready MVP project. Follow these principles:

1. **No placeholders** - All code must be functional
2. **Type safety** - Use TypeScript/Python type hints
3. **Clean code** - Follow project conventions
4. **Test before commit** - Ensure features work

## License

Proprietary
