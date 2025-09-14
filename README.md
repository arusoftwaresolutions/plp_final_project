# 💰 Financial Platform

A comprehensive Python-based financial platform that connects families, donors, and businesses to provide financial assistance, AI-powered budgeting advice, and loan management services.

## 🚀 Features

### 👨‍👩‍👧‍👦 Family Features
- **Expense & Income Tracking**: Add and categorize financial transactions
- **AI Budgeting Assistant**: Get personalized financial recommendations
- **Interactive Dashboard**: Visualize spending patterns with charts and graphs
- **Campaign Creation**: Create fundraising campaigns for financial needs
- **Geospatial Integration**: View poverty hotspots and community resources

### 💝 Donor Features
- **Browse Campaigns**: Discover families in need of financial assistance
- **Secure Donations**: Make donations with integrated payment processing
- **Donation Tracking**: Monitor your giving history and impact
- **Anonymous Giving**: Option to donate anonymously

### 🏢 Business Features
- **Loan Applications**: Apply for business loans with detailed purpose statements
- **Application Tracking**: Monitor loan application status
- **Business Profile**: Manage business information and financial details

### 👨‍💼 Admin Features
- **Loan Management**: Review, approve, or reject loan applications
- **Campaign Oversight**: Monitor all fundraising campaigns
- **User Management**: View and manage platform users
- **Analytics Dashboard**: Comprehensive platform statistics

### 🤖 AI Features
- **Smart Recommendations**: AI-powered budgeting and financial advice
- **Spending Analysis**: Identify patterns and optimization opportunities
- **Budget Forecasting**: Predict future financial trends
- **Priority-based Alerts**: High, medium, and low priority recommendations

### 🗺️ Geospatial Features
- **Poverty Hotspot Mapping**: Visualize areas with high poverty rates
- **Family Location Tracking**: Map family locations for targeted assistance
- **Interactive Maps**: Folium-powered interactive maps
- **Distance Calculations**: Find families near poverty hotspots

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database with PostGIS extension
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **JWT**: Secure authentication with JSON Web Tokens

### Frontend
- **Streamlit**: Rapid web app development framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **Folium**: Interactive maps and geospatial visualization

### AI/ML
- **Scikit-learn**: Machine learning library for budgeting recommendations
- **Joblib**: Model persistence and loading

### Infrastructure
- **Docker**: Containerization for easy deployment
- **Docker Compose**: Multi-container orchestration
- **PostGIS**: Geospatial database extensions

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd financial-platform
```

### 2. Start the Platform
```bash
docker-compose up --build
```

### 3. Access the Applications
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### 4. Seed Demo Data
```bash
# Access the backend container
docker-compose exec backend bash

# Run the seed script
python seed_data.py
```

## 🔧 Development Setup

### Backend Development
```bash
cd backend
pip install -r requirements.txt

# Set up environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/financial_platform"
export SECRET_KEY="your-secret-key"

# Run the backend
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
pip install -r requirements.txt

# Set backend URL
export BACKEND_URL="http://localhost:8000"

# Run the frontend
streamlit run app.py
```

### Database Setup
```bash
# Create database
createdb financial_platform

# Run migrations
cd backend
alembic upgrade head

# Seed data
python seed_data.py
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
# Streamlit tests can be run manually through the UI
# Automated testing can be added with pytest and selenium
```

## 📊 API Documentation

The API is fully documented with Swagger UI available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

#### Family Management
- `POST /api/families/profile` - Create family profile
- `GET /api/families/dashboard` - Get dashboard data
- `POST /api/families/transactions` - Add transaction
- `GET /api/families/transactions` - Get transactions

#### Donor Management
- `GET /api/donors/campaigns` - Browse campaigns
- `POST /api/donors/donate` - Make donation
- `GET /api/donors/my-donations` - Get donation history

#### AI Assistant
- `GET /api/ai/recommendations` - Get AI recommendations
- `POST /api/ai/generate-recommendations` - Generate new recommendations
- `GET /api/ai/budget-forecast` - Get budget forecast

#### Geospatial
- `GET /api/geospatial/map` - Get map data
- `GET /api/geospatial/poverty-hotspots` - Get poverty hotspots
- `GET /api/geospatial/families-near-hotspot/{id}` - Find nearby families

## 🔐 Security

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control (Family, Donor, Business, Admin)

### Data Protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- CORS configuration for frontend-backend communication

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here

# Optional
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

## 🗄️ Database Schema

### Core Tables
- **users**: User accounts and authentication
- **family_profiles**: Family-specific information
- **donor_profiles**: Donor information and statistics
- **business_profiles**: Business information for loan applications
- **transactions**: Financial transactions (income/expenses)
- **campaigns**: Fundraising campaigns
- **donations**: Donation records
- **loan_applications**: Business loan applications
- **ai_recommendations**: AI-generated financial advice
- **poverty_hotspots**: Geospatial poverty data

## 🚀 Deployment

### Production Deployment
1. **Environment Setup**:
   ```bash
   # Set production environment variables
   export DATABASE_URL="postgresql://user:password@prod-db:5432/financial_platform"
   export SECRET_KEY="production-secret-key"
   export STRIPE_SECRET_KEY="production-stripe-key"
   ```

2. **Database Migration**:
   ```bash
   alembic upgrade head
   ```

3. **Docker Deployment**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Scaling Considerations
- Use a production PostgreSQL database
- Implement Redis for session management
- Add load balancing for multiple backend instances
- Use CDN for static assets
- Implement proper logging and monitoring

## 🔧 Configuration

### Backend Configuration
Edit `backend/config.py` to modify:
- Database connection settings
- JWT token expiration
- AI model paths
- Payment processor settings

### Frontend Configuration
Edit `frontend/app.py` to modify:
- Backend API URL
- UI themes and layouts
- Chart configurations

## 📈 Monitoring and Analytics

### Built-in Analytics
- User registration and activity tracking
- Transaction volume and patterns
- Donation statistics
- Loan application metrics
- AI recommendation effectiveness

### Logging
- Application logs in Docker containers
- Database query logging
- API request/response logging
- Error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the test cases for usage examples

## 🔮 Future Enhancements

- **Mobile App**: React Native or Flutter mobile application
- **Advanced AI**: More sophisticated ML models for financial predictions
- **Real Payments**: Full Stripe integration for actual payments
- **Notifications**: Email and SMS notifications for important events
- **Reporting**: Advanced reporting and analytics dashboard
- **Multi-language**: Internationalization support
- **Blockchain**: Cryptocurrency donation support
- **Social Features**: Community features and social sharing

## 📊 Demo Data

The platform comes with comprehensive demo data including:
- Sample families with transaction history
- Mock poverty hotspots with geospatial data
- Campaign examples with donation records
- AI recommendations for different scenarios
- Business loan applications in various states

## 🎯 Use Cases

### For Families
- Track monthly income and expenses
- Get AI-powered budgeting advice
- Create fundraising campaigns for emergencies
- Access community resources and support

### For Donors
- Discover families in need
- Make secure donations
- Track donation impact
- Support specific causes or communities

### For Businesses
- Apply for business loans
- Track application status
- Access financial resources
- Connect with the community

### For Administrators
- Manage loan applications
- Oversee platform operations
- Monitor user activity
- Generate reports and analytics

---

**Built with ❤️ using Python, FastAPI, Streamlit, and modern web technologies.**
