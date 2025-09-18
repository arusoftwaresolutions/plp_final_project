# Poverty Alleviation Platform

A comprehensive platform for poverty alleviation, aligned with SDG 1: No Poverty. This application provides financial literacy, microloans, and crowdfunding capabilities to help combat poverty.

## Features

- **RESTful API**: Built with FastAPI
- **User Authentication**: Secure login with JWT
- **Financial Management**: Track transactions and financial health
- **Microloans**: Apply for and manage microloans
- **Crowdfunding**: Create and support poverty alleviation campaigns
- **Admin Dashboard**: Manage users, loans, and campaigns

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Deployment**: Render
- **API Documentation**: Auto-generated with Swagger UI and ReDoc

## Project Structure

```
SDG!
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
├── .gitignore             # Git ignore file
└── backend/               # Main application package
    ├── app/
    │   ├── __init__.py
    │   ├── main.py        # FastAPI application setup
    │   ├── core/          # Core functionality
    │   │   ├── config.py  # Application configuration
    │   │   └── security.py # Authentication utilities
    │   ├── db/           # Database models and session
    │   │   ├── models.py  # SQLAlchemy models
    │   │   └── session.py # Database session management
    │   └── api/          # API routes
    │       └── v1/        # API version 1
    │           └── endpoints/  # API endpoints
    └── tests/             # Test files
```

## Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SDG!
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables in `.env` with your local configuration

5. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

6. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Deployment

### Render Deployment

1. Push your code to a GitHub repository
2. Connect the repository to Render
3. Configure environment variables in the Render dashboard
4. Set the following build command:
   ```
   pip install -r requirements.txt
   ```
5. Set the start command:
   ```
   uvicorn backend.app.main:app --host 0.0.0.0 --port 10000
   ```

### Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: Hashing algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `ENVIRONMENT`: Set to 'production' in production

## API Documentation

Once the application is running, access the interactive API documentation at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

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

## Deployment to Render

This project includes a `render.yaml` file that makes deployment to Render simple and automated. Follow these steps:

1. **Push your code to a Git repository**
   - Make sure your code is pushed to a GitHub or GitLab repository

2. **Deploy to Render**
   - Go to your [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" and select "Blueprint"
   - Connect your repository
   - Click "Apply" to deploy all services defined in `render.yaml`

3. **Environment Variables**
   The following environment variables will be automatically configured by Render:
   - `ENVIRONMENT=production`
   - `SECRET_KEY` (auto-generated)
   - `ALGORITHM=HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
   - `FIRST_SUPERUSER=admin`
   - `FIRST_SUPERUSER_EMAIL=admin@example.com`
   - `FIRST_SUPERUSER_PASSWORD` (auto-generated)
   - `BACKEND_CORS_ORIGINS=["http://localhost:3000"]`
   - `DATABASE_URL` (auto-configured from the PostgreSQL service)

4. **Access the Application**
   - Once deployed, you can access your application at the provided Render URL
   - API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc)
   - Health check endpoint: `/health`

5. **Admin Access**
   - The first superuser will be created automatically with the credentials:
     - Email: `admin@example.com`
     - Password: Check the logs or Render environment variables for the generated password

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
