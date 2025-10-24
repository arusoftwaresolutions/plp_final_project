# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SDG 1: No Poverty Full-Stack MVP - A monorepo containing a React frontend PWA and Node.js backend API for poverty alleviation tools including budgeting assistance, crowdfunding, microloans, and poverty mapping with geospatial data.

## Repository Structure

- **apps/backend/**: Node.js + Express API with PostgreSQL/PostGIS + Redis
- **apps/frontend/**: React + TypeScript + Vite PWA with TailwindCSS
- **db/migrations/**: PostgreSQL schema with PostGIS extension
- **ai/**: System prompt configuration for OpenAI integration

## Development Commands

### Root Level (Workspace Management)
```bash
# Install all dependencies (uses workspaces)
npm install
```

### Backend Development (apps/backend)
```bash
cd apps/backend
npm install
npm run dev          # Start development server with tsx watch
npm run build        # TypeScript compilation
npm run start        # Start production build
npm run test         # Run Jest tests
npm run test:watch   # Run tests in watch mode
```

### Frontend Development (apps/frontend)
```bash
cd apps/frontend
npm install
npm run dev          # Start Vite development server
npm run build        # Build for production
npm run preview      # Preview production build
```

### Testing
- Backend tests are in `apps/backend/tests/`
- Uses Jest with ts-jest preset
- Test files: `*.test.ts`
- Configuration: `jest.config.cjs`

## Architecture Overview

### Backend Architecture
- **Express.js** REST API with modular route structure
- **Security**: Helmet, CORS with configurable origins, JWT authentication
- **Database**: PostgreSQL with PostGIS extension for geospatial features
- **Caching**: Redis integration
- **AI Integration**: OpenAI API with configurable model (default: gpt-4o-mini)
- **API Documentation**: Swagger/OpenAPI at `/api/docs`

**Key Patterns:**
- Route handlers in `src/routes/` (health, auth, users, transactions, ai)
- Business logic in `src/services/` (db, redis, ai)
- Centralized security configuration in `src/security.ts`
- OpenAPI spec generation in `src/openapi.ts`

### Frontend Architecture  
- **React 18** with TypeScript and React Router DOM
- **Styling**: TailwindCSS with PostCSS
- **Build Tool**: Vite
- **Pages**: Modular page components (Onboarding, BudgetCoach, Crowdfunding, Microloan, PovertyMap)
- **Mapping**: Leaflet integration for poverty visualization

### Database Schema
- **Users & Households**: User management with household financial data
- **Transactions**: Financial tracking by category and type
- **Geospatial**: Regions with MultiPolygon geometry, poverty aggregation indices
- **PostGIS**: Required extension for geospatial operations

### AI Service
- Budget coaching with safety constraints (text-only responses, no JSON)
- System prompt in `ai/system_prompt.txt` emphasizes family-friendly financial advice
- Configurable via `MODEL_NAME` environment variable

## Environment Configuration

Copy `.env.example` to `.env` with these required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API access
- `MODEL_NAME` - AI model (default: gpt-4o-mini)
- `JWT_SECRET` - Authentication secret
- `FRONTEND_URL` - CORS origins (comma-separated)
- `REDIS_URL` - Redis connection
- `VITE_API_BASE_URL` - Frontend API endpoint

## Database Setup

1. Ensure PostgreSQL has PostGIS: `CREATE EXTENSION postgis;`
2. Run migrations in order:
   - `db/migrations/001_init.sql`
   - `db/migrations/002_seed.sql`

## Deployment (Render)

- Configuration in `render.yaml`
- Backend: Web service with health check at `/api/health`
- Frontend: Static site from `dist/` folder
- Database: Managed PostgreSQL with PostGIS extension
- Environment variables configured in Render dashboard

## Key API Endpoints

- `GET /api/health` - Health check
- `GET /api/ai/budget/:householdId` - AI budget advice (returns plain text)
- `GET /api/docs` - Swagger documentation
- Authentication, users, and transactions endpoints available

## Development Notes

- Backend uses ES modules (`"type": "module"`)
- TypeScript strict mode enabled
- AI responses are constrained to human-readable text (no JSON output)
- All secrets managed via environment variables
- CORS configured for development and production origins