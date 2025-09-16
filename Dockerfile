# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Create and use virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
WORKDIR /app/backend
RUN pip install -e .

# Production stage
FROM python:3.9-slim

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/backend /app/backend
# Create backend.egg-info if it doesn't exist
RUN cd /app/backend && \
    if [ ! -d "backend.egg-info" ]; then \
        python setup.py egg_info; \
    fi

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app"

# Set the working directory to the backend
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Command to run the application with proper PORT handling
CMD ["sh", "-c", "cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --log-level ${LOG_LEVEL:-info}"]
