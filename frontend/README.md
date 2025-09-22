# SDG 1 Frontend

This directory contains the frontend assets for the SDG 1: No Poverty application.

## Structure

```
frontend/
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       ├── main.js            # Main application logic
│       ├── api.js             # API communication utilities
│       ├── auth.js            # Authentication functions
│       ├── dashboard.js       # Dashboard functionality
│       ├── transactions.js    # Transaction management
│       ├── crowdfunding.js    # Crowdfunding features
│       ├── loans.js           # Microloan management
│       ├── poverty-map.js     # Interactive poverty map
│       └── profile.js         # User profile management
├── templates/
│   └── index.html             # Main HTML template
└── package.json               # Frontend configuration
```

## Development

The frontend is built with vanilla HTML, CSS, and JavaScript using modern web standards:

- **HTML**: Semantic markup with Bootstrap 5 for responsive design
- **CSS**: Custom styling with Bootstrap 5 components
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Charts**: Chart.js for data visualization
- **Maps**: Leaflet.js for interactive mapping

## Features

- Modern, responsive banking-style interface
- Real-time data visualization with charts
- Interactive poverty map with geospatial data
- Comprehensive user authentication and profile management
- Transaction tracking and analysis
- Crowdfunding campaign management
- Microloan application and tracking system
- AI-powered financial recommendations

## Dependencies

The frontend uses CDN-hosted dependencies for optimal performance:

- Bootstrap 5.3.0 (CSS framework)
- Chart.js (data visualization)
- Leaflet.js (interactive maps)
- Font Awesome 6.4.0 (icons)

No build process is required - all assets are served directly by the FastAPI backend.
