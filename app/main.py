from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import create_tables
from app.routers import (
    auth, users, health, notifications, 
    caregivers, doctors, leaderboard, admin, superuser
)
from app.config import settings

# Create database tables on startup
create_tables()

app = FastAPI(
    title="Kwanpa Health API",
    description="Comprehensive health tracking and caregiver coordination platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend-domain.vercel.app",  # Update with your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(caregivers.router)
app.include_router(doctors.router)
app.include_router(leaderboard.router)
app.include_router(admin.router)
app.include_router(superuser.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kwanpa Health API",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Kwanpa API", 
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }