# Poverty Alleviation Platform - Frontend

This is the frontend for the Poverty Alleviation Platform, built with Streamlit. It provides a user-friendly interface for managing financial transactions, microloans, crowdfunding campaigns, and accessing poverty insights.

## Features

- **Dashboard**: Overview of financial status, recent transactions, and key metrics
- **Transactions**: Track income and expenses with categorization and filtering
- **Loans**: Apply for and manage microloans with repayment tracking
- **Crowdfunding**: Discover and contribute to poverty alleviation campaigns
- **Insights**: View poverty statistics and AI-powered recommendations
- **Admin Panel**: Manage users, campaigns, and platform settings (admin only)
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   # Backend API URL
   API_BASE_URL=http://localhost:8000/api/v1
   
   # JWT Secret Key (should match backend)
   SECRET_KEY=your-secret-key-here
   
   # Other configuration
   DEBUG=True
   ```

5. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

   The application will be available at `http://localhost:8501`

## Project Structure

```
frontend/
├── src/
│   ├── pages/               # Application pages
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication pages
│   │   ├── dashboard.py     # Main dashboard
│   │   ├── transactions.py  # Transaction management
│   │   ├── loans.py         # Microloan management
│   │   ├── crowdfunding.py  # Crowdfunding campaigns
│   │   ├── insights.py      # Poverty insights
│   │   ├── admin.py         # Admin panel
│   │   └── settings.py      # User settings
│   ├── services/
│   │   ├── __init__.py
│   │   └── api.py           # API service layer
│   └── app.py               # Main application entry point
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
streamlit run src/app.py --server.runOnSave true
```

### Code Style

This project follows the PEP 8 style guide. Before committing, run:

```bash
# Run linter
flake8 src

# Run formatter
black src

# Sort imports
isort src
```

### Testing

Run the test suite with:

```bash
pytest tests/
```

## Deployment

### Production Deployment

For production deployment, consider using:

1. **Streamlit Cloud**
2. **Docker** with Nginx
3. **AWS ECS/EKS**
4. **Google Cloud Run**

Example Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the repository or contact the development team.

---

Built with ❤️ for a poverty-free world.
