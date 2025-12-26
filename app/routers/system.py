from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.services.openai_service import logger
import os

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/health-check")
async def system_health(db: Session = Depends(get_db)):
    status = {
        "database": "unknown",
        "openai_config": "configured" if os.getenv("AZURE_OPENAI_KEY") else "missing",
        "storage_config": "azure" if os.getenv("AZURE_STORAGE_CONNECTION_STRING") else "local",
        "environment": os.getenv("ENVIRONMENT", "dev")
    }
    
    # Check DB
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        
    return status