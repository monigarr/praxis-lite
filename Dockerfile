# PRAXIS Lite Dockerfile
# Builds the FastAPI backend for Render web service
FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps from pyproject.toml
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application source
COPY . .

# Run FastAPI with uvicorn, Render sets $PORT
CMD ["sh", "-c", "uvicorn knowledge.serve.app:app --host 0.0.0.0 --port ${PORT:-8000}"]