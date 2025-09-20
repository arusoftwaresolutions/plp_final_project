# Setup script for the frontend environment

# Check if .env file exists
if (Test-Path .env) {
    Write-Host ".env file already exists. Skipping creation." -ForegroundColor Yellow
} else {
    # Create .env file with default values
    @"
# Backend API Configuration
API_BASE_URL=https://plp-final-project-bgex.onrender.com/api/v1

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend Configuration
STREAMLIT_SERVER_HEADLESS=true
"@ | Out-File -FilePath .env -Encoding utf8
    
    Write-Host "Created .env file with default values." -ForegroundColor Green
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "Setup complete!" -ForegroundColor Green
