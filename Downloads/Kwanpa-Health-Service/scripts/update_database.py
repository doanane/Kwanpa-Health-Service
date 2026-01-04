# Create: C:\Users\hp\Downloads\Kwanpa-Health-Service\update_database.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_caregiver_columns():
    """Add missing caregiver columns to database"""
    sql_commands = [
        # Add new columns
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS caregiver_id VARCHAR(20);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS caregiver_type VARCHAR(50);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_years INTEGER;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS max_patients INTEGER DEFAULT 5;",
        
        # Update existing rows: set is_caregiver = false if null
        "UPDATE users SET is_caregiver = false WHERE is_caregiver IS NULL;",
        "UPDATE users SET is_available = true WHERE is_available IS NULL;",
        "UPDATE users SET max_patients = 5 WHERE max_patients IS NULL;",
        
        # Create indexes
        "CREATE INDEX IF NOT EXISTS idx_users_caregiver_id ON users(caregiver_id);",
        "CREATE INDEX IF NOT EXISTS idx_users_is_caregiver ON users(is_caregiver);",
    ]
    
    try:
        with engine.connect() as conn:
            for sql in sql_commands:
                logger.info(f"Executing: {sql[:50]}...")
                conn.execute(text(sql))
                conn.commit()
            
            logger.info("Database updated successfully!")
            logger.info("Caregiver columns added to users table")
            
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("DATABASE UPDATE FOR CAREGIVER FUNCTIONALITY")
    print("="*60)
    
    success = add_caregiver_columns()
    
    if success:
        print("\nDatabase update completed!")
        print("\nNext steps:")
        print("1. Restart your FastAPI server")
        print("2. Test caregiver signup: POST /auth/signup/caregiver")
        print("3. Check docs: http://localhost:8000/docs")
    else:
        print("\nDatabase update failed!")
    
    print("="*60)
