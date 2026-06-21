# PRAXIS Lite Dockerfile
# Placeholder for future services (e.g. knowledge/serve FastAPI or React build)
FROM python:3.12-slim

WORKDIR /app

# Install system deps if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python deps (add requirements when present)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy source (adjust as structure grows)
COPY . .

# Default command - override per service
CMD ["python", "-m", "http.server", "8000"]