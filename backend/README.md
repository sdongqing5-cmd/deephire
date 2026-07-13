# DeepHire Backend

FastAPI-based backend for DeepHire AI recruiting system.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Search**: OpenSearch
- **AI**: OpenAI Compatible API
- **ORM**: SQLAlchemy

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py          # Authentication
│   │       │   ├── candidates.py    # Candidate management
│   │       │   ├── jobs.py          # Job management
│   │       │   └── interviews.py    # Interview management
│   │       └── api.py               # API router aggregation
│   ├── core/
│   │   ├── config.py                # Configuration
│   │   └── security.py              # Security utilities
│   ├── models/                      # SQLAlchemy models (TODO)
│   ├── schemas/                     # Pydantic schemas (TODO)
│   ├── services/                    # Business logic (TODO)
│   └── main.py                      # Application entry point
├── requirements.txt
└── .env.example
```

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Available Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Candidates
- `GET /api/v1/candidates` - List candidates
- `GET /api/v1/candidates/{id}` - Get candidate details
- `POST /api/v1/candidates` - Create candidate
- `PUT /api/v1/candidates/{id}` - Update candidate

### Jobs
- `GET /api/v1/jobs` - List jobs
- `GET /api/v1/jobs/{id}` - Get job details
- `POST /api/v1/jobs` - Create job

### Interviews
- `GET /api/v1/interviews` - List interviews
- `GET /api/v1/interviews/{id}` - Get interview details

## Demo Accounts

For testing, use these credentials:

- **HR**: hr@deephire.com / password
- **Recruiter**: recruiter@deephire.com / password
- **Interviewer**: interviewer@deephire.com / password

## Development

### Code Style

Follow PEP 8 guidelines. Use type hints for all functions.

### Adding New Endpoints

1. Create endpoint file in `app/api/v1/endpoints/`
2. Define router and endpoints
3. Add router to `app/api/v1/api.py`

## Next Steps

- [ ] Implement database models
- [ ] Add database migrations with Alembic
- [ ] Implement real JWT authentication
- [ ] Add resume parsing service
- [ ] Implement semantic search
- [ ] Add OpenSearch integration
- [ ] Implement candidate activation
