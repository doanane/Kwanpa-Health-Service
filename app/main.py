from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import create_tables
from app.routers import auth, users, health, notifications, caregivers
from app.config import settings


create_tables()

app = FastAPI(
    title="Kwanpa Health API",
    description="Comprehensive health tracking and caregiver coordination platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(notifications.router)
app.include_router(caregivers.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kwanpa Health API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database": "PostgreSQL",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "Kwanpa API", 
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }

@app.on_event("startup")
async def startup_event():
    print("🚀 Kwanpa API starting up...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🗄️ Database connected successfully!")