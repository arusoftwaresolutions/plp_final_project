# Use official Python image as base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY . /app

# Set the working directory to the backend
WORKDIR /app/backend

# Install the application in development mode
RUN pip install -e .

# Set the working directory back to /app
WORKDIR /app

# Expose port
EXPOSE 8000

# Command to run the application with environment variable support
CMD ["sh", "-c", "python -c \"import os; from uvicorn import run; run('backend.app.main:app', host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))\n"]
