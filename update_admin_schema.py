import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from sqlalchemy import text

def update_admin_schema():
    """Add missing last_login column to admins table"""
    print("Updating admin table schema...")
    
    db = SessionLocal()
    try:
        # Check if last_login column exists
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'admins' AND column_name = 'last_login'
        """
        
        result = db.execute(text(check_query)).fetchone()
        
        if not result:
            print("Adding last_login column to admins table...")
            alter_query = """
            ALTER TABLE admins 
            ADD COLUMN last_login TIMESTAMP WITH TIME ZONE
            """
            db.execute(text(alter_query))
            db.commit()
            print("✅ last_login column added successfully!")
        else:
            print("✅ last_login column already exists")
            
        # Verify the table structure
        desc_query = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'admins'"
        columns = db.execute(text(desc_query)).fetchall()
        
        print("\nAdmin table columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
            
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        db.rollback()
    finally:
        db.close()

def create_default_admin():
    """Create default superadmin"""
    db = SessionLocal()
    try:
        from app.models.admin import Admin
        from app.auth.hashing import get_password_hash
        
        # Check if admin already exists
        existing = db.query(Admin).filter(Admin.email == "superadmin@hewal3.com").first()
        if existing:
            print(f"\nAdmin already exists: {existing.email}")
            return
        
        # Create default admin
        admin = Admin(
            email="superadmin@hewal3.com",
            hashed_password=get_password_hash("Super@1234"),
            full_name="System Super Administrator",
            is_superadmin=True,
            is_active=True,
            permissions='{"all": true}'
        )
        
        db.add(admin)
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ DEFAULT SUPER ADMIN CREATED")
        print("=" * 60)
        print(f"Email: superadmin@hewal3.com")
        print(f"Password: Super@1234")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("Fixing Admin Schema and Data")
    print("=" * 60)
    
    # Update schema
    update_admin_schema()
    
    # Create default admin
    create_default_admin()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Restart server: uvicorn app.main:app --reload")
    print("2. Test login: POST /superadmin/login")
    print("3. Use credentials:")
    print("   - Email: superadmin@hewal3.com")
    print("   - Password: Super@1234")

if __name__ == "__main__":
    main()