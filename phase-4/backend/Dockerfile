# Use python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
# Also copy requirements.txt as fallback/reference if needed, but rely on pyproject/uv
COPY requirements.txt .

# Install dependencies using uv
# --system installs into system python, avoiding virtualenv overhead in container
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Expose port (FastAPI default)
EXPOSE 8000

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
