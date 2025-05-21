import logging
import uuid
from contextvars import ContextVar
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from datetime import datetime, timezone

request_id: ContextVar[str] = ContextVar("request_id", default="")

class StructuredLogger:
    def __init__(self):
        self.logger = structlog.get_logger()
        
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                self._add_common_fields,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.BoundLogger,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )

    def _add_common_fields(self, _, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
        event_dict["request_id"] = request_id.get("")
        return event_dict

    async def log_request(self, request: Request):
        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        self.logger.info("request.received")

    async def log_response(self, response: Response, duration_ms: float):
        structlog.contextvars.bind_contextvars(
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        self.logger.info("request.completed")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        request_id.set(req_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response

def configure_logging():
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(
            file=logging.StreamHandler()
        ),
        wrapper_class=structlog.BoundLogger,
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").disabled = True

def get_logger() -> structlog.BoundLogger:
    return structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.struct_logger = StructuredLogger()

    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now(timezone.utc)
        
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id.set(req_id)
        
        await self.struct_logger.log_request(request)
        
        try:
            response = await call_next(request)
        except Exception as e:
            structlog.get_logger().error(
                "request.error",
                error=str(e),
                exc_info=True
            )
            raise

        duration = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        response.headers["X-Request-ID"] = req_id
        
        await self.struct_logger.log_response(response, duration)
        
        return response