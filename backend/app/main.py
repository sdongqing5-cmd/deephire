"""FastAPI application entry point"""

import time
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import bind_request_context, configure_logging, logger, notify_alert
from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.services.audit_service import record_audit_event


configure_logging()

app = FastAPI(
    title="DeepHire API",
    description="AI-powered recruiting system API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request, call_next):
    """Add request context, structured access logs and mutation audit records."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    user_id = "-"
    user_email = "-"
    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        token_payload = decode_access_token(authorization[7:])
        if token_payload:
            user_id = str(token_payload.get("user_id") or "-")
            user_email = str(token_payload.get("sub") or "-")

    bind_request_context(request_id, user_id, user_email)
    started = time.perf_counter()
    status_code = 500
    response = None
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        logger.exception("Unhandled request exception")
        raise
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000)
        logger.bind(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else "-",
        ).log("ERROR" if status_code >= 500 else "INFO", "request completed")

        if status_code >= 500:
            await notify_alert(
                "DeepHire backend request failure",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )

        if request.method not in {"GET", "HEAD", "OPTIONS"} and not request.url.path.startswith(("/docs", "/redoc", "/openapi.json", "/health")):
            db = None
            try:
                db = SessionLocal()
                path_parts = [part for part in request.url.path.strip("/").split("/") if part]
                resource_type = path_parts[2] if len(path_parts) >= 3 and path_parts[0] == "api" else (path_parts[0] if path_parts else "root")
                resource_id = path_parts[3] if len(path_parts) >= 4 and path_parts[0] == "api" else None
                record_audit_event(
                    db,
                    request_id=request_id,
                    user_id=None if user_id == "-" else user_id,
                    user_email=None if user_email == "-" else user_email,
                    action=f"{request.method.lower()} {request.url.path}",
                    resource_type=resource_type,
                    resource_id=resource_id,
                    method=request.method,
                    path=request.url.path,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    details={"query": str(request.query_params)} if request.query_params else None,
                )
                db.close()
            except Exception:
                logger.exception("Failed to persist audit event")
                try:
                    if db:
                        db.close()
                except Exception:
                    pass

        if response is not None:
            response.headers["X-Request-ID"] = request_id


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DeepHire API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API router
app.include_router(api_router, prefix="/api/v1")

# Serve uploaded resume files for local review.
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
