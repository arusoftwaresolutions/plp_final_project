# SDG 1: No Poverty – Full-Stack MVP

This repository contains a deployment-ready MVP with:
- Frontend PWA (React + TypeScript + Vite + TailwindCSS)
- Backend API (Node + Express + PostgreSQL + PostGIS + Redis)
- AI advice service (OpenAI) with safe fallback and text-only outputs
- Render deployment config, seed data, and tests

## Environment
Copy `.env.example` to `.env` and fill values:

- DATABASE_URL
- OPENAI_API_KEY
- MODEL_NAME=gpt-4o-mini
- JWT_SECRET
- FRONTEND_URL (comma-separated origins)
- NODE_ENV=production
- REDIS_URL
- VITE_API_BASE_URL

## Run locally

Backend:
- cd apps/backend
- npm install
- npm run dev

Frontend:
- cd apps/frontend
- npm install
- npm run dev

## Database
Run migrations in your PostgreSQL (ensure `CREATE EXTENSION postgis;`).
- db/migrations/001_init.sql
- db/migrations/002_seed.sql

## API
- Health: GET /api/health -> {"status":"ok"}
- AI advice: GET /api/ai/budget/1 -> { advice: "human text" }
- Docs: /api/docs

## Testing (backend)
- npm run test

Sample assertions (Jest):
- advice is string and not JSON
- /api/health returns ok

## Render deployment
- Push to a Git repo and connect on Render
- Backend (Web Service):
  - build: npm install && npm run build
  - start: npm run start
  - health: /api/health
- Frontend (Static Site):
  - build: npm run build
  - publish: dist

Set environment variables in Render dashboard as in `.env.example`.

## AI Prompt
`ai/system_prompt.txt` – loaded by the backend AI service.

## Notes
- No hard-coded secrets; everything via env
- Frontend shows plain, human-readable text (no JSON)
