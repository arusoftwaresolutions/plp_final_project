# Financial Inclusion App - Frontend

This is the frontend for the Financial Inclusion App, built with Streamlit. It provides a user-friendly interface for managing financial services for underserved communities.

## Features

- User authentication (login/register)
- Dashboard with financial overview
- Transaction management
- AI-powered financial recommendations
- Crowdfunding platform
- Microloans management
- Poverty mapping visualization
- User profile management
- Admin panel for user management

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Node.js and npm (for frontend assets if needed)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

## Running the Application

1. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

## Development

### Code Style

We use the following tools to maintain code quality:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

You can run these tools with the following commands:

```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8

# Run type checking
mypy .
```

### Testing

Run tests with pytest:

```bash
pytest
```

## Project Structure

```
frontend/
├── .env.example           # Example environment variables
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── app.py                # Main application entry point
├── pages/                # Streamlit page modules
│   ├── __init__.py
│   ├── dashboard.py      # Dashboard page
│   ├── auth.py           # Authentication pages
│   ├── transactions.py   # Transactions management
│   ├── crowdfunding.py   # Crowdfunding features
│   ├── microloans.py     # Microloans management
│   ├── poverty_map.py    # Poverty mapping visualization
│   ├── profile.py        # User profile
│   └── admin_panel.py    # Admin interface
└── utils/                # Utility modules
    ├── __init__.py
    ├── api.py           # API client
    ├── auth.py          # Authentication utilities
    └── helpers.py       # Helper functions
```

## Environment Variables

See `.env.example` for a list of required environment variables.

## Deployment

### Production

For production deployment, consider using:
- Streamlit Cloud
- Heroku
- AWS Elastic Beanstalk
- Google Cloud Run

Make sure to:
1. Set `DEBUG=False` in production
2. Use a proper WSGI server like Gunicorn
3. Set up proper CORS policies
4. Use HTTPS
5. Set secure cookie flags

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing framework
- [Plotly](https://plotly.com/) for interactive visualizations
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API
- [Financial Inclusion Initiative](https://www.example.org) for the inspiration
