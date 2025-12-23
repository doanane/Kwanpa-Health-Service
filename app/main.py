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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

from fastapi.responses import RedirectResponse, HTMLResponse


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


# In app/main.py, ensure you have all these routers:
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.health import router as health_router
from app.routers.notifications import router as notifications_router
from app.routers.caregivers import router as caregivers_router  # Make sure this is here
from app.routers.doctors import router as doctors_router
from app.routers.admin import router as admin_router
from app.routers.food_analysis import router as food_analysis_router

app.include_router(auth_router)
app.include_router(users_router)  
app.include_router(health_router)
app.include_router(notifications_router)
app.include_router(caregivers_router)  
app.include_router(doctors_router)
app.include_router(admin_router)
app.include_router(food_analysis_router)


logger.info("Loading superadmin router...")
try:
    from app.routers.superadmin import router as superadmin_router
    app.include_router(superadmin_router)
    logger.info("Superadmin router loaded successfully")
    
    
    # logger.info("Superadmin endpoints registered:")
    # for route in superadmin_router.routes:
    #     if hasattr(route, 'methods'):
    #         methods = ', '.join(route.methods)
    #         logger.info(f"  {methods} {route.path}")
            
except ImportError as e:
    logger.error(f"Failed to import superadmin router: {e}")
    
    import traceback
    traceback.print_exc()
except Exception as e:
    logger.error(f"Error loading superadmin router: {e}")
    import traceback
    traceback.print_exc()

# In app/main.py, ensure this section exists:
try:
    from app.routers.caregivers import router as caregivers_router
    app.include_router(caregivers_router)
    # logger.info("✅ Caregivers router loaded successfully")
    
    # # Log routes for debugging
    # for route in caregivers_router.routes:
    #     if hasattr(route, 'path'):
    #         logger.info(f"   - {route.path}")
            
except Exception as e:
    logger.error(f"❌ Failed to load caregivers router: {e}")
    import traceback
    traceback.print_exc()

# try:
#     from app.routers.doctors import router as doctors_router
#     app.include_router(doctors_router)
#     logger.info("Doctors router loaded")
# except ImportError as e:
#     logger.warning(f"Doctors router not loaded: {e}")

try:
    from app.routers.leaderboard import router as leaderboard_router
    app.include_router(leaderboard_router)
    # logger.info("Leaderboard router loaded")
except ImportError as e:
    logger.warning(f"Leaderboard router not loaded: {e}")

try:
    from app.routers.admin import router as admin_router
    app.include_router(admin_router)
    logger.info("Admin router loaded")
except ImportError as e:
    logger.warning(f"Admin router not loaded: {e}")


# try:
#     from app.routers.google_auth import router as google_auth_router
#     app.include_router(google_auth_router)
#     logger.info("✅ Google OAuth router loaded successfully")
# except ImportError as e:
#     logger.error(f"❌ Failed to import Google Auth router: {e}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kwanpa-health-hub-six.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8001",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from app.routers.food_analysis import router as food_analysis_router
    app.include_router(food_analysis_router)
    logger.info("Food Analysis router loaded")
except ImportError as e:
    logger.warning(f"Food Analysis router not loaded: {e}")

@app.get("/")
def read_root():
    return {"message": "Hello from Azure!"}
    
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    
    return {
        "message": "Welcome to HEWAL3 Health API",
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "status": "running",
        "docs": "/docs",
        "routes_count": len(routes)
    }


@app.get("/oauth/callback", response_class=HTMLResponse, include_in_schema=False)
async def oauth_callback_page():
    """HTML page for OAuth callback handling"""
    with open("app/templates/oauth_callback.html", "r") as f:
        return HTMLResponse(content=f.read())

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
                .logo { color: margin-bottom: 20px; }
                .button { 
                    display: inline-block; 
                    padding: 12px 24px; 
                    margin: 10px;
                    background-color: 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                }
                .api-button { background-color: 
                .section { margin: 40px 0; padding: 20px; background: 
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
                    <a href="/docsclass="button">Sign Up</a>
                    <a href="/docsclass="button">Login</a>
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