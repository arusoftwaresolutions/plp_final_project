FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/backend" \
    PORT=8000 \
    WEB_CONCURRENCY=1 \
    LOG_LEVEL=info \
    APP_MODULE="app.main:app"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app/backend

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt uvicorn[standard]

# Copy backend code
COPY backend/ .

# Install the package in development mode
RUN pip install -e .

# Expose the port the app runs on
EXPOSE 8000

# Create a simple startup script
RUN echo '#!/bin/sh\n\
# Wait for database to be available (if needed)\n# while ! nc -z $POSTGRES_SERVER 5432; do\n#   echo "Waiting for PostgreSQL..."\n#   sleep 1\ndone\n\n# Run migrations (if needed)\n# alembic upgrade head\n\n# Start the application\nexec uvicorn $APP_MODULE \\
    --host 0.0.0.0 \\
    --port ${PORT} \\
    --workers ${WEB_CONCURRENCY} \\
    --log-level ${LOG_LEVEL}\n' > /app/start.sh && chmod +x /app/start.sh

# Health check configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the application
CMD ["/app/start.sh"]
