from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import auth, users, health, notifications, caregivers
import traceback

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kwanpa Health API",
    description="Comprehensive health tracking and caregiver coordination platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )

# Include routers
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
        "endpoints": {
            "auth": "/auth",
            "users": "/users", 
            "health": "/health",
            "notifications": "/notifications",
            "caregivers": "/caregivers"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Kwanpa API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")