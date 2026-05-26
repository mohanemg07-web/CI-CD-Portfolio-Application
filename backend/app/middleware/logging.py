import logging
import uuid
from datetime import datetime, timezone
import requests
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import BETTERSTACK_INGEST_URL, BETTERSTACK_SOURCE_TOKEN

LOGGER_NAME = "portfolio.access"


class BetterStackHTTPHandler(logging.Handler):
    """POSTs JSON log records to Better Stack Logs ingest endpoint."""

    def __init__(self, token: str, url: str) -> None:
        super().__init__()
        self.token = token
        self.url = url

    def emit(self, record: logging.LogRecord) -> None:
        try:
            payload = self.format(record)
            requests.post(
                self.url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                timeout=3,
            )
        except Exception:
            # Never let log shipping crash the request path.
            pass


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        rename_fields={"levelname": "level"},
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if BETTERSTACK_SOURCE_TOKEN:
        bs_handler = BetterStackHTTPHandler(
            BETTERSTACK_SOURCE_TOKEN, BETTERSTACK_INGEST_URL
        )
        bs_handler.setFormatter(formatter)
        logger.addHandler(bs_handler)

    logger.propagate = False
    return logger


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.logger = configure_logging()

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        latency_ms = getattr(request.state, "latency_ms", None)
        self.logger.info(
            "request",
            extra={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "route": request.url.path,
                "method": request.method,
                "latency_ms": latency_ms,
                "status_code": response.status_code,
                "request_id": request_id,
            },
        )
        return response
