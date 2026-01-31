"""
Monitoring and Observability Module for Evolution Todo API.

Phase 4: Kubernetes Deployment
Task: Production-ready observability infrastructure

This module provides:
- Structured JSON logging
- Request/Response logging middleware
- Health check endpoints
- Metrics collection
"""
from .logging_config import setup_logging, get_logger
from .middleware import LoggingMiddleware

__all__ = [
    "setup_logging",
    "get_logger",
    "LoggingMiddleware",
]
