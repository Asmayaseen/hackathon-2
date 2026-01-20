# syntax=docker/dockerfile:1
# Phase 4: Backend Dockerfile - Multi-stage build for FastAPI
# Following containerizing-applications skill patterns

FROM python:3.12-slim AS builder
WORKDIR /app

# Install uv for faster dependency installation
RUN pip install uv

# Copy dependency files from phase-3/backend
COPY pyproject.toml .

# Install dependencies with timeout handling
RUN UV_HTTP_TIMEOUT=120 uv pip install --system --no-cache -r pyproject.toml

FROM python:3.12-slim
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -u 1000 appuser && chown -R appuser /app
USER appuser

# Environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Health check using curl (more reliable than python)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
