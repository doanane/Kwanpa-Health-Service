# app/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.config import settings
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_engine_with_fallback():
    """Create database engine with Azure first, fallback to local, then SQLite"""
    db_url = settings.DATABASE_URL
    
    # Try Azure connection first
    if "azure" in db_url.lower():
        logger.info("🔗 Attempting Azure PostgreSQL connection...")
        try:
            engine = create_engine(
                db_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={
                    'connect_timeout': 10,
                    'sslmode': 'require'
                }
            )
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                logger.info(f"✅ Connected to Azure PostgreSQL: {version[:50]}...")
            
            return engine
            
        except Exception as e:
            logger.warning(f"❌ Azure connection failed: {e}")
            logger.info("🔄 Falling back to local PostgreSQL...")
    
    # Try local PostgreSQL
    try:
        # If not already local, create local connection string
        if "localhost" not in db_url and "azure" not in db_url.lower():
            local_url = "postgresql+psycopg2://postgres:S%400570263170s@localhost:5432/hewal3_db"
        else:
            local_url = db_url
            
        engine = create_engine(
            local_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connected to local PostgreSQL")
        return engine
        
    except Exception as e:
        logger.warning(f"❌ Local PostgreSQL failed: {e}")
        logger.info("🔄 Falling back to SQLite...")
        
        # Use SQLite as last resort
        engine = create_engine("sqlite:///./hewal3.db", connect_args={"check_same_thread": False})
        logger.info("✅ Using SQLite database")
        return engine

# Create engine
engine = create_engine_with_fallback()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/database.py
def create_tables():
    """Create database tables - DROPS EXISTING TABLES FIRST"""
    try:
        # Import all models to ensure they're registered with Base
        from app.models import (
            user, health, notification, 
            caregiver, emergency
        )
        
        # Drop all tables first (use with caution in production!)
        if settings.ENVIRONMENT == "development":
            Base.metadata.drop_all(bind=engine)
            print("Dropped existing tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise e

def create_tables():
    """Create database tables safely"""
    try:
        # Only drop tables in development with local database
        if settings.ENVIRONMENT == "development" and "localhost" in str(engine.url):
            try:
                Base.metadata.drop_all(bind=engine)
                logger.info("🗑️  Dropped existing tables (development mode)...")
            except Exception as e:
                logger.info(f"ℹ️  Could not drop tables: {e}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        if settings.ENVIRONMENT != "development":
            raise