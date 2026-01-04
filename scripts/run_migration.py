import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations_001_initial_schema import create_tables

if __name__ == "__main__":
    print("🚀 Running database migration...")
    create_tables()
<<<<<<< HEAD:back/run_migration.py
    print("Migration completed successfully!")
=======
    print("✅ Migration completed successfully!")
>>>>>>> main:back/scripts/run_migration.py
