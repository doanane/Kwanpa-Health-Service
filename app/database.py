import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL with fallbacks"""
    db_url = settings.DATABASE_URL
    
    # If Azure URL provided, use it
    if db_url and "azure" in db_url.lower():
        logger.info("Using Azure PostgreSQL connection")
        return db_url
    
    # Otherwise use local PostgreSQL
    logger.info("Using local PostgreSQL database")
    return settings.LOCAL_DB_URL

# Get database URL
db_url = get_database_url()

# Create engine
try:
    if "sqlite" in db_url:
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(
            db_url,
            echo=False, 
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={'connect_timeout': 10}
        )
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✅ Database connection successful")
    
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    
    # Fallback to SQLite
    logger.info("Falling back to SQLite...")
    engine = create_engine("sqlite:///./hewal3.db", 
                          connect_args={"check_same_thread": False},
                          echo=True)
    logger.info("✅ Using SQLite database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables(preserve_data: bool = True):
    """Create database tables with option to preserve data"""
    try:
        # SQLite fallback often has schema drift; recreate tables to match models
        if engine.dialect.name == "sqlite":
            logger.warning("⚠️ SQLite detected – recreating tables to keep schema in sync")
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
        else:
            if not preserve_data and settings.ENVIRONMENT == "development":
                logger.warning("⚠️ Dropping tables (data will be lost!)")
                Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
        
        # if preserve_data:
        #     logger.info("✅ Database tables verified - existing data preserved")
        # else:
        #     logger.info("✅ Database tables recreated - all data cleared")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


