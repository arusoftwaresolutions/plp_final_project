FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Railway will inject PORT dynamically
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt uvicorn[standard]

# Copy backend code
COPY backend/ .

# Install the package in development mode
RUN pip install -e .

# Expose the port (Railway overrides with $PORT)
EXPOSE 8000

# Simple health check (inside container, for Docker)
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=10 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1
