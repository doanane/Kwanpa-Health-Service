from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

# Use the database URL directly from settings
DATABASE_URL = settings.DATABASE_URL

print(f"🔗 Database URL: {DATABASE_URL}")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables - DROPS EXISTING TABLES FIRST"""
    try:
        # Drop all tables first (use with caution in production!)
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Dropped existing tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise e