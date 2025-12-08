# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.database import create_tables, engine
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to create tables, but don't crash if it fails
try:
    create_tables()
    logger.info("✅ Database setup completed")
except Exception as e:
    logger.warning(f"⚠️  Database setup warning: {e}")
    if settings.ENVIRONMENT == "development":
        logger.info("🔄 Continuing in development mode...")
    else:
        # In production, we might want to be stricter
        logger.error("🚨 Database setup failed in production!")

app = FastAPI(
    title="HEWAL3 Health API",
    description="AI-powered health management system with emergency response",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import and include routers
try:
    from app.routers import (
        auth, users, health, notifications, 
        caregivers, doctors, leaderboard, admin
    )
    
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(health.router)
    app.include_router(notifications.router)
    app.include_router(caregivers.router)
    app.include_router(doctors.router)
    app.include_router(leaderboard.router)
    app.include_router(admin.router)
    
    logger.info("✅ All routers loaded successfully")
    
except Exception as e:
    logger.error(f"🚨 Error loading routers: {e}")

@app.get("/")
async def root():
    # Check if database is connected
    db_status = "unknown"
    try:
        with engine.connect():
            db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "message": "Welcome to HEWAL3 Health API",
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    try:
        with engine.connect():
            db_status = "connected"
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "HEWAL3 API", 
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }