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


------------------------------
    ## Dockerfile
    
    # Use an official, lightweight Python runtime as a parent imageFROM python:3.11-slim as builder
    # Set environment variables to prevent Python from writing pyc files and buffering stdoutENV PYTHONDONTWRITEBYTECODE=1ENV PYTHONUNBUFFERED=1
    # Establish a secure working directoryWORKDIR /app
    # Install system dependencies needed for compilation and security scanningRUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*
    # Copy dependency structures first to leverage Docker cache layersCOPY requirements.txt .
    # Install dependencies into a localized user space to prevent root-access vector risksRUN pip install --no-cache-dir --user -r requirements.txt
    # Final minimal execution stageFROM python:3.11-slim as runner
    WORKDIR /app
    ENV PYTHONDONTWRITEBYTECODE=1ENV PYTHONUNBUFFERED=1ENV PATH=/root/.local/bin:$PATH
    # Copy installed dependencies and codebase from the builder stageCOPY --from=builder /root/.local /root/.localCOPY . .
    # Expose default port for Render.com and local routing matrixEXPOSE 10000
    # Healthcheck definition for automated infrastructure monitoringHEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
      CMD curl -f http://localhost:10000/health || exit 1
    # Execute the application via Uvicorn as a non-privileged process spaceCMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]