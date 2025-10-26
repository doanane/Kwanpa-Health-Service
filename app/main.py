from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth
import os

# Create tables only if DATABASE_URL is set (i.e., in production)
if os.getenv("DATABASE_URL"):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

app = FastAPI(
    title="Kwanpa Health API",
    description="Comprehensive health tracking and caregiver coordination platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kwanpa Health API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Kwanpa API"}

@app.get("/debug")
async def debug_info():
    return {
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "secret_key_set": bool(os.getenv("SECRET_KEY")),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)