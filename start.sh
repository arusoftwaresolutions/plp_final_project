#!/bin/bash
# Start script for Poverty Alleviation Platform on Render

# Exit on error and print commands
set -eo pipefail

# Configuration
PORT=${PORT:-10000}
WORKERS=${WEB_CONCURRENCY:-$(nproc)}
TIMEOUT=${TIMEOUT:-120}

# Log environment information
echo "🚀 Starting Poverty Alleviation Platform..."
echo "🔧 Environment:"
echo "   - PORT: $PORT"
echo "   - WORKERS: $WORKERS"
echo "   - TIMEOUT: $TIMEOUT"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment not found. Please run render-build.sh first."
    exit 1
fi

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head
fi

# Start the application
echo "🚀 Starting Gunicorn with $WORKERS workers on port $PORT..."
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --timeout $TIMEOUT \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    app.main:app
