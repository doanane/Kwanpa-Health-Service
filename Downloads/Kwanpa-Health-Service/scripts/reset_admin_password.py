import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def add_email_column():
    """Add email column to doctors table if it doesn't exist"""
    print("Checking doctors table for email column...")
    
    with engine.connect() as conn:
        
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='doctors' AND column_name='email'
        """))
        
        if not result.fetchone():
            print("Adding email column to doctors table...")
            try:
                conn.execute(text("ALTER TABLE doctors ADD COLUMN email VARCHAR"))
                conn.commit()
<<<<<<< HEAD:back/reset_admin_password.py
                print("Email column added successfully")
            except Exception as e:
                print(f"Error adding column: {e}")
                conn.rollback()
        else:
            print("Email column already exists")
=======
                print("✅ Email column added successfully")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
                conn.rollback()
        else:
            print("✅ Email column already exists")
>>>>>>> main:back/scripts/reset_admin_password.py
        
        
        print("\nDoctors table structure:")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name='doctors'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            print(f"  {row.column_name}: {row.data_type} ({'nullable' if row.is_nullable == 'YES' else 'not null'})")

if __name__ == "__main__":
    add_email_column()
