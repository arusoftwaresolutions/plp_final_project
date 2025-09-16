# Poverty Alleviation Platform

A comprehensive platform for poverty alleviation, aligned with SDG 1: No Poverty. This application provides financial literacy, microloans, and crowdfunding capabilities to help combat poverty.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=)

## Features

- **Modern Web Interface**: Responsive design built with Streamlit
- **User Authentication**: Secure login with JWT
- **Financial Dashboard**: Track income, expenses, and financial health
- **Microloans**: Apply for and manage microloans
- **Crowdfunding**: Create and support poverty alleviation campaigns
- **AI-Powered Insights**: Get personalized financial recommendations
- **Admin Dashboard**: Manage users, loans, and campaigns
- **Geospatial Visualization**: Interactive maps showing poverty-affected areas

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker & Docker Compose
- **Deployment**: Railway
- **CI/CD**: GitHub Actions

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL 14+
- Node.js 16+ (for frontend development)
- Git

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (copy `.env.example` to `.env` and configure)
4. Run migrations: `alembic upgrade head`
5. Start the application: `docker-compose up --build`

## Default Admin Credentials

- Username: admin
- Password: admin123

## Project Structure

```
SDG!/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints (v1)
│   │   ├── core/          # Core configurations
│   │   ├── db/            # Database models and migrations
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI application
│   ├── tests/             # Backend tests
│   ├── alembic/           # Database migrations
│   └── requirements.txt   # Python dependencies
│
├── frontend/              # Streamlit frontend
│   ├── src/
│   │   ├── pages/        # Application pages
│   │   │   ├── auth.py   # Authentication
│   │   │   ├── dashboard.py
│   │   │   ├── loans.py
│   │   │   └── ...
│   │   ├── services/     # API services
│   │   ├── utils/        # Helper functions
│   │   └── app.py        # Main Streamlit app
│   └── requirements.txt  # Frontend dependencies
│
├── .github/              # GitHub workflows
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── railway.json
├── runtime.txt
└── README.md
```

## Local Development

### Using Docker (Recommended)

1. **Start the application**
   ```bash
   docker-compose up --build -d
   ```

2. **Access the services**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Start the Streamlit app
streamlit run src/app.py
```

## Deployment

The application is configured for deployment on Railway. You can deploy it with one click:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=)

### Manual Deployment to Railway

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Link your project**
   ```bash
   railway init
   ```

4. **Set environment variables**
   ```bash
   railway env push .env.production
   ```

5. **Deploy**
   ```bash
   railway up
   ```

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Backend
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Frontend
API_BASE_URL=http://localhost:8000/api/v1

# Production
DEBUG=False
ENVIRONMENT=production
```

## Testing

### Backend Tests
```bash
cd backend
# Install test requirements
pip install -r requirements-test.txt

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app --cov-report=term-missing
```

### Frontend Tests
```bash
cd frontend
# Install test requirements
pip install -r requirements-test.txt

# Run tests
pytest
```

### End-to-End Testing
For end-to-end testing, you can use the following command to test the entire stack:

```bash
# Start all services
docker-compose up -d

# Run tests (example using curl for API testing)
curl -X GET http://localhost:8000/api/v1/health
```

## Contributing

We welcome contributions from the community! Here's how you can help:

1. **Report Bugs**
   - Check if the issue already exists in the [Issues](https://github.com/your-repo/issues) section
   - If not, create a new issue with a clear description and steps to reproduce

2. **Suggest Enhancements**
   - Open an issue with the `enhancement` label
   - Describe the proposed changes and their benefits

3. **Code Contributions**
   1. Fork the repository
   2. Create a feature branch: `git checkout -b feature/your-feature`
   3. Commit your changes: `git commit -m 'Add some feature'`
   4. Push to the branch: `git push origin feature/your-feature`
   5. Open a Pull Request

4. **Code Style**
   - Follow PEP 8 for Python code
   - Include docstrings for all functions and classes
   - Write meaningful commit messages
   - Add tests for new features

## Support

If you need help or have questions:

- **Documentation**: Check out our [documentation](https://github.com/your-repo/docs)
- **Community**: Join our [Discord server](https://discord.gg/your-invite)
- **Email**: support@povertyalleviation.org
- **Issues**: Open an issue in our [GitHub repository](https://github.com/your-repo/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ for a poverty-free world.

[![Powered by FastAPI](https://img.shields.io/badge/Powered%20by-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=)
