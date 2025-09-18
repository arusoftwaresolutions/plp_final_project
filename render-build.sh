#!/usr/bin/env bash
# Render build script for Poverty Alleviation Platform

# Exit on error
set -o errexit
set -o pipefail
set -o nounset

# Print commands as they are executed
set -x

echo "🚀 Starting build process for Poverty Alleviation Platform..."

# Create and activate virtual environment
echo "🔧 Setting up Python environment..."
python -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Install any additional build dependencies
# pip install --no-cache-dir gunicorn uvicorn[standard]

# Run database migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head
fi

# Collect static files (if using any)
# if [ -f "manage.py" ]; then
#     echo "📁 Collecting static files..."
#     python manage.py collectstatic --noinput
# fi

echo "✅ Build completed successfully!"
echo "🚀 Application is ready to deploy!"
