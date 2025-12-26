# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.database import create_tables, engine
from app.config import settings
from fastapi.responses import RedirectResponse, HTMLResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HEWAL3 Health API",
    description="AI-powered health management system with emergency response",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
allowed_origins = [
    "http://localhost:8081",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://kwanpa-health-hub-six.vercel.app",
    "https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net"
]

if settings.ENVIRONMENT == "development":
    allowed_origins.extend([
        "http://localhost:*",
        "http://127.0.0.1:*",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Ensure upload directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/profile_images", exist_ok=True)
os.makedirs("uploads/profile_photos", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/verify-email/{token}", include_in_schema=False)
async def redirect_verify_email(token: str):
    """Redirect old verification links"""
    return RedirectResponse(url=f"/auth/verify-email-page/{token}")

@app.get("/reset-password", include_in_schema=False)
async def redirect_reset_password(token: str = None):
    """Redirect old reset password links"""
    if token:
        return RedirectResponse(url=f"/auth/reset-password-page?token={token}")
    return RedirectResponse(url="/auth/reset-password-page")

@app.on_event("startup")
def startup_event():
    try:
        create_tables()
        logger.info("✅ Database setup completed")
    except Exception as e:
        logger.warning(f"⚠️ Database setup warning: {e}")

# --- IMPORT ROUTERS (No try/except to ensure visibility of errors) ---

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.health import router as health_router
from app.routers.notifications import router as notifications_router
from app.routers.caregivers import router as caregivers_router
from app.routers.doctors import router as doctors_router
from app.routers.admin import router as admin_router
from app.routers.food_analysis import router as food_analysis_router
from app.routers.superadmin import router as superadmin_router
from app.routers.google_auth import router as google_auth_router
from app.routers.leaderboard import router as leaderboard_router

# Attempt to load system router (optional)
try:
    from app.routers.system import router as system_router
    app.include_router(system_router)
except ImportError:
    pass

# --- INCLUDE ROUTERS ---
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(health_router)
app.include_router(notifications_router)
app.include_router(caregivers_router)
app.include_router(doctors_router)
app.include_router(admin_router)
app.include_router(food_analysis_router)
app.include_router(superadmin_router)
app.include_router(google_auth_router)
app.include_router(leaderboard_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to HEWAL3 Health API",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    try:
        with engine.connect():
            db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "HEWAL3 API", 
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }

@app.options("/{full_path:path}", include_in_schema=False)
async def options_handler(full_path: str):
    """Handle preflight requests"""
    return {"status": "ok"}

@app.get("/oauth/callback", response_class=HTMLResponse, include_in_schema=False)
async def oauth_callback_page():
    """HTML page for OAuth callback handling"""
    path = "app/templates/oauth_callback.html"
    if os.path.exists(path):
        with open(path, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>OAuth Callback</h1><p>Processing authentication...</p>")

@app.get("/welcome", response_class=HTMLResponse)
async def welcome_page():
    """Welcome page for new users"""
    return """
    <html>
        <head>
            <title>HEWAL3 Health System</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .container { max-width: 800px; margin: 0 auto; }
                .button { 
                    display: inline-block; 
                    padding: 12px 24px; 
                    margin: 10px; 
                    background-color: #4CAF50; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                }
                .api-button { background-color: #2196F3; }
                .section { margin: 40px 0; padding: 20px; background: #f5f5f5; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>HEWAL3 Health System</h1>
                <p>AI-powered health tracking and caregiver coordination</p>
                <div class="section">
                    <h2>Get Started</h2>
                    <a href="/docs" class="button api-button">API Documentation</a>
                </div>
            </div>
        </body>
    </html>
    """