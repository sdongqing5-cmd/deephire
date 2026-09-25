"""Application logging configuration and request context helpers."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from contextvars import ContextVar
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings

try:
    from loguru import logger
except ModuleNotFoundError:
    class _FallbackLogger:
        """Small stdlib-backed compatibility layer for minimal environments."""

        def __init__(self) -> None:
            self._logger = logging.getLogger("deephire.fallback")
            self._logger.propagate = False
            if not self._logger.handlers:
                self._logger.addHandler(logging.StreamHandler(sys.stdout))

        def remove(self, *args: Any, **kwargs: Any) -> None:
            return None

        def configure(self, *args: Any, **kwargs: Any) -> None:
            return None

        def add(self, *args: Any, **kwargs: Any) -> None:
            return None

        def bind(self, **kwargs: Any) -> "_FallbackLogger":
            return self

        def level(self, name: str) -> Any:
            return type("LogLevel", (), {"name": name})()

        def opt(self, **kwargs: Any) -> "_FallbackLogger":
            return self

        def log(self, level: Any, message: str, *args: Any, **kwargs: Any) -> None:
            level_number = logging.getLevelName(level) if isinstance(level, str) else level
            if not isinstance(level_number, int):
                level_number = logging.INFO
            self._logger.log(level_number, message, *args)

        def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
            self._logger.exception(message, *args)

        def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
            self._logger.warning(message, *args)

        def info(self, message: str, *args: Any, **kwargs: Any) -> None:
            self._logger.info(message, *args)

    logger = _FallbackLogger()


request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="-")
user_email_ctx: ContextVar[str] = ContextVar("user_email", default="-")


class InterceptHandler(logging.Handler):
    """Forward standard-library and Uvicorn logs through Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: Any = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(exception=record.exc_info).log(level, record.getMessage())


def _patch_record(record: dict[str, Any]) -> None:
    record["extra"].update(
        {
            "request_id": request_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "user_email": user_email_ctx.get(),
            "service": "deephire-backend",
            "environment": settings.ENVIRONMENT,
        }
    )


def configure_logging() -> None:
    """Configure JSON stdout plus separate application and error files."""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.configure(patcher=_patch_record)
    logger.add(
        sys.stdout,
        serialize=True,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        log_dir / "app.log",
        serialize=True,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="gz",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        log_dir / "error.log",
        serialize=True,
        level="ERROR",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "sqlalchemy.engine"):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False


def bind_request_context(request_id: str, user_id: str = "-", user_email: str = "-") -> None:
    request_id_ctx.set(request_id)
    user_id_ctx.set(user_id)
    user_email_ctx.set(user_email)


def bind_user_context(user_id: str, user_email: str = "-") -> None:
    user_id_ctx.set(user_id)
    user_email_ctx.set(user_email)


async def notify_alert(message: str, **details: Any) -> None:
    """Send critical request failures to an optional webhook."""
    if not settings.ALERT_WEBHOOK_URL:
        return
    payload = {
        "text": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.post(settings.ALERT_WEBHOOK_URL, json=payload)
            response.raise_for_status()
    except Exception:
        logger.exception("failed to send alert webhook")


__all__ = ["logger", "configure_logging", "bind_request_context", "bind_user_context", "notify_alert"]
