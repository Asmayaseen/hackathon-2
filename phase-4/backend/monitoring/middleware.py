"""
Logging Middleware for FastAPI.

Phase 4: Kubernetes Deployment
Provides request/response logging for observability.

Features:
- Request correlation IDs
- Request/Response timing
- Error logging
- Path filtering (skip health checks)
"""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_config import get_logger

logger = get_logger(__name__)

# Paths to skip logging (health checks, etc.)
SKIP_PATHS = {"/health", "/ready", "/metrics", "/favicon.ico"}


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.

    Adds:
    - X-Request-ID header for correlation
    - Request timing
    - Structured log output
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""

        # Skip logging for certain paths
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

        # Start timing
        start_time = time.perf_counter()

        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params) if request.query_params else None,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log response
            log_method = logger.info if response.status_code < 400 else logger.warning
            log_method(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )

            # Add correlation header to response
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": round(duration_ms, 2),
                },
                exc_info=True
            )
            raise
