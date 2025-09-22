"""
SDG 1: No Poverty Application
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from app.database import Base, engine
from app.auth import router as auth_router
from app.dashboard import router as dashboard_router
from app.transactions import router as transactions_router
from app.crowdfunding import router as crowdfunding_router
from app.loans import router as loans_router
from app.profile import router as profile_router
from app.poverty_map import router as poverty_map_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SDG 1: No Poverty Application",
    description="A full-stack application to address SDG 1: No Poverty through financial empowerment",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(transactions_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(crowdfunding_router, prefix="/api/crowdfunding", tags=["Crowdfunding"])
app.include_router(loans_router, prefix="/api/loans", tags=["Loans"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])
app.include_router(poverty_map_router, prefix="/api/poverty-map", tags=["Poverty Map"])

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Templates for server-side rendering if needed
templates = Jinja2Templates(directory="../frontend/templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Serve the main frontend page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "SDG 1 Application is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
