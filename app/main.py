from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.database import create_tables, engine
from app.config import settings

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
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def startup_event():
    try:
        create_tables()
        logger.info("Database setup completed")
    except Exception as e:
        logger.warning(f"Database setup warning: {e}")

# Import core routers
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.health import router as health_router
from app.routers.notifications import router as notifications_router

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(health_router)
app.include_router(notifications_router)

# DEBUG: Check superadmin router specifically
logger.info("Loading superadmin router...")
try:
    from app.routers.superadmin import router as superadmin_router
    app.include_router(superadmin_router)
    logger.info("✅ Superadmin router loaded successfully")
    
    # Test if endpoints are registered
    logger.info("Superadmin endpoints registered:")
    for route in superadmin_router.routes:
        if hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            logger.info(f"  {methods} {route.path}")
            
except ImportError as e:
    logger.error(f"❌ Failed to import superadmin router: {e}")
    # Try to show what's wrong
    import traceback
    traceback.print_exc()
except Exception as e:
    logger.error(f"❌ Error loading superadmin router: {e}")
    import traceback
    traceback.print_exc()

# Load other routers with error handling
try:
    from app.routers.caregivers import router as caregivers_router
    app.include_router(caregivers_router)
    logger.info("Caregivers router loaded")
except ImportError as e:
    logger.warning(f"Caregivers router not loaded: {e}")

try:
    from app.routers.doctors import router as doctors_router
    app.include_router(doctors_router)
    logger.info("Doctors router loaded")
except ImportError as e:
    logger.warning(f"Doctors router not loaded: {e}")

try:
    from app.routers.leaderboard import router as leaderboard_router
    app.include_router(leaderboard_router)
    logger.info("Leaderboard router loaded")
except ImportError as e:
    logger.warning(f"Leaderboard router not loaded: {e}")

try:
    from app.routers.admin import router as admin_router
    app.include_router(admin_router)
    logger.info("Admin router loaded")
except ImportError as e:
    logger.warning(f"Admin router not loaded: {e}")

@app.get("/")
async def root():
    try:
        with engine.connect():
            db_status = "connected"
    except:
        db_status = "disconnected"
    
    # List all routes for debugging
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

# Debug endpoint to list all routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name if hasattr(route, 'name') else None
            })
    return {"routes": routes}