"""Delete audit rows older than the configured retention period."""

from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.db.database import SessionLocal
from app.models import AuditLog
from app.core.logging import configure_logging, logger


configure_logging()
db = SessionLocal()
try:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
    deleted = db.query(AuditLog).filter(AuditLog.created_at < cutoff).delete(synchronize_session=False)
    db.commit()
    logger.info("audit log retention cleanup completed", deleted=deleted, cutoff=cutoff.isoformat())
finally:
    db.close()
