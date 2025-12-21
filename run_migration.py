import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from migrations_001_initial_schema import create_tables

if __name__ == "__main__":
    print("🚀 Running database migration...")
    create_tables()
    print("✅ Migration completed successfully!")