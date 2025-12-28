# create_superadmin.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.database import SessionLocal
from app.models.admin import Admin
from app.auth.hashing import get_password_hash
import getpass

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

def create_superadmin():
    print("=" * 50)
    print("HEWAL3 Super Admin Creator")
    print("=" * 50)
    
    # Get admin details
    email = input("Enter admin email: ").strip()
    
    # Get password securely
    while True:
        password = getpass.getpass("Enter password (min 8 chars): ").strip()
        confirm_password = getpass.getpass("Confirm password: ").strip()
        
        if password != confirm_password:
            print("Passwords do not match. Try again.\n")
            continue
        
        if len(password) < 8:
            print("Password must be at least 8 characters.\n")
            continue
        
        break
    
    full_name = input("Enter full name: ").strip()
    
    print("\n" + "=" * 50)
    print("Creating super admin...")
    print(f"Email: {email}")
    print(f"Full Name: {full_name}")
    print("=" * 50)
    
    # Create database session
    engine = create_engine(DATABASE_URL)

    
    with Session(engine) as db:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.email == email).first()
        
        if existing_admin:
            print(f"Admin with email {email} already exists.")
            choice = input("Do you want to reset password? (y/n): ").lower()
            
            if choice == 'y':
                existing_admin.hashed_password = get_password_hash(password)
                existing_admin.is_active = True
                existing_admin.is_superadmin = True
                db.commit()
                print("Password reset successfully!")
                print(f"Updated admin: {email}")
                return
            else:
                print("Operation cancelled.")
                return
        
        # Create new admin
        new_admin = Admin(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_superadmin=True
        )
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        print("Super admin created successfully!")
        print(f"Email: {email}")
        print(f"Password: [hidden]")
        print(f"Full Name: {full_name}")
        print(f"Is Superadmin: Yes")
        print(f"Is Active: Yes")
        print("\n Keep these credentials secure!")

if __name__ == "__main__":
    create_superadmin()