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

# CORS Configuration - FIXED
allowed_origins = [
    "http://localhost:8081",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://kwanpa-health-hub-six.vercel.app",
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

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
        logger.info("Database setup completed")
    except Exception as e:
        logger.warning(f"Database setup warning: {e}")

# Include all routers
try:
    from app.routers.auth import router as auth_router
    app.include_router(auth_router)
except ImportError as e:
    logger.error(f"Failed to import auth router: {e}")

try:
    from app.routers.users import router as users_router
    app.include_router(users_router)
except ImportError as e:
    logger.error(f"Failed to import users router: {e}")

try:
    from app.routers.health import router as health_router
    app.include_router(health_router)
except ImportError as e:
    logger.error(f"Failed to import health router: {e}")

try:
    from app.routers.notifications import router as notifications_router
    app.include_router(notifications_router)
except ImportError as e:
    logger.error(f"Failed to import notifications router: {e}")

try:
    from app.routers.caregivers import router as caregivers_router
    app.include_router(caregivers_router)
    logger.info("✅ Caregivers router loaded")
except ImportError as e:
    logger.error(f"❌ Failed to import caregivers router: {e}")

try:
    from app.routers.doctors import router as doctors_router
    app.include_router(doctors_router)
except ImportError as e:
    logger.error(f"Failed to import doctors router: {e}")

try:
    from app.routers.admin import router as admin_router
    app.include_router(admin_router)
    logger.info("Admin router loaded")
except ImportError as e:
    logger.error(f"Failed to import admin router: {e}")

try:
    from app.routers.food_analysis import router as food_analysis_router
    app.include_router(food_analysis_router)
    logger.info("Food Analysis router loaded")
except ImportError as e:
    logger.error(f"Failed to import food analysis router: {e}")

try:
    from app.routers.superadmin import router as superadmin_router
    app.include_router(superadmin_router)
    logger.info("Superadmin router loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import superadmin router: {e}")

try:
    from app.routers.google_auth import router as google_auth_router
    app.include_router(google_auth_router)
    logger.info("✅ Google OAuth router loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import Google Auth router: {e}")

try:
    from app.routers.leaderboard import router as leaderboard_router
    app.include_router(leaderboard_router)
except ImportError as e:
    logger.warning(f"Leaderboard router not loaded: {e}")

@app.get("/")
def read_root():
    return {"message": "Hello from HEWAL3 API!"}

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

@app.options("/{full_path:path}", include_in_schema=False)
async def options_handler(full_path: str):
    """Handle preflight requests"""
    return {"status": "ok"}

@app.get("/oauth/callback", response_class=HTMLResponse, include_in_schema=False)
async def oauth_callback_page():
    """HTML page for OAuth callback handling"""
    with open("app/templates/oauth_callback.html", "r") as f:
        return HTMLResponse(content=f.read())

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
                .logo { margin-bottom: 20px; }
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
                <div class="logo">HEWAL3</div>
                <h1>Health Management System</h1>
                <p>AI-powered health tracking and caregiver coordination</p>
                
                <div class="section">
                    <h2>Get Started</h2>
                    <a href="/docs" class="button api-button">API Documentation</a>
                    <a href="/docs#/authentication/signup" class="button">Sign Up</a>
                    <a href="/docs#/authentication/login" class="button">Login</a>
                </div>
                
                <div class="section">
                    <h2>Features</h2>
                    <p>• Health Data Tracking • AI Food Analysis • Emergency Alerts</p>
                    <p>• Caregiver Portal • Doctor Dashboard • Progress Monitoring</p>
                </div>
                
                <div class="section">
                    <h2>Email Verification & Password Reset</h2>
                    <p>If you received an email verification or password reset link:</p>
                    <p>• Click the link in your email</p>
                    <p>• Or visit: <code>/auth/verify-email-page/{token}</code> or <code>/auth/reset-password-page?token={token}</code></p>
                </div>
            </div>
        </body>
    </html>
    """