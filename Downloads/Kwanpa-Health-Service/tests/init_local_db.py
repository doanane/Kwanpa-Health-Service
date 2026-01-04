# back/init_local_db.py
import sys
import os

# Add the current directory to sys.path to ensure we can import 'app' modules
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from app.database import Base

# --- IMPORT ALL MODELS ---
# We must import all model files here so they register with Base.metadata
# before we try to create the tables.
from app.models import (
    user,
    auth,
    caregiver,
    health,
    notification,
    emergency,
    food_analysis,
    iot_device,
    admin,
    audit
)

# Your Local Connection String
# Note: %40 is the URL encoded version of @
LOCAL_DB_URL = "postgresql+psycopg2://postgres:S%400570263170s@localhost:5432/kwanpa_db1"

def init_db():
    print("🚀 Initializing Local Database...")
    print(f"📡 Connecting to: {LOCAL_DB_URL}")
    
    try:
        engine = create_engine(LOCAL_DB_URL)
        
        # Optional: Uncomment the next line if you want to wipe the DB clean every time
        # Base.metadata.drop_all(bind=engine)
        
        print("🔨 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables created successfully in 'kwanpa_db1'!")
        print("   - Users")
        print("   - Caregiver Relationships")
        print("   - Health Data")
        print("   - ...and all others.")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    init_db()