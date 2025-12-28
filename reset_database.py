import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.admin import Admin
from app.models.caregiver import Doctor
from app.models.user import User, UserProfile
from app.models.health import HealthData, FoodLog, WeeklyProgress
from app.models.notification import Notification
from app.auth.hashing import get_password_hash

def reset_database():
    """Completely reset database and create fresh data"""
    print("RESETTING DATABASE...")
    print("=" * 60)
    
    confirm = input(" This will DELETE ALL DATA. Type 'YES' to confirm: ")
    if confirm != "YES":
        print("Cancelled.")
        return
    
    try:
        
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        
        print("Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        
        print("Database reset complete")
        
        
        create_default_data()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def create_default_data():
    """Create default superadmin and doctors"""
    db = SessionLocal()
    try:
        
        superadmin = Admin(
            email="superadmin@hewal3.com",
            hashed_password=get_password_hash("Super@1234"),
            full_name="System Super Administrator",
            is_superadmin=True,
            is_active=True,
            permissions='{"all": true}'
        )
        db.add(superadmin)
        
        
        your_admin = Admin(
            email="superadmin@gmail.com",
            hashed_password=get_password_hash("super1234"),
            full_name="Your Name",
            is_superadmin=True,
            is_active=True,
            permissions='{"all": true}'
        )
        db.add(your_admin)
        
        
        doctors = [
            {
                "doctor_id": "DOC001001",
                "full_name": "Dr. Kwame Mensah",
                "specialization": "Cardiology",
                "hospital": "Korle Bu Teaching Hospital",
                "password": "Doctor@123"
            },
            {
                "doctor_id": "DOC001002", 
                "full_name": "Dr. Ama Serwaa",
                "specialization": "Endocrinology",
                "hospital": "37 Military Hospital",
                "password": "Doctor@123"
            }
        ]
        
        for doc_data in doctors:
            doctor = Doctor(
                doctor_id=doc_data["doctor_id"],
                hashed_password=get_password_hash(doc_data["password"]),
                full_name=doc_data["full_name"],
                specialization=doc_data["specialization"],
                hospital=doc_data["hospital"],
                created_by="system"
            )
            db.add(doctor)
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("DEFAULT DATA CREATED")
        print("=" * 60)
        print("\n🔐 SUPER ADMIN CREDENTIALS:")
        print("-" * 40)
        print("1. Default Superadmin:")
        print("   Email: superadmin@hewal3.com")
        print("   Password: Super@1234")
        print("\n2. Your Superadmin:")
        print("   Email: superadmin@gmail.com")
        print("   Password: super1234")
        print("\n👨‍⚕️ DOCTOR CREDENTIALS:")
        print("-" * 40)
        for doc in doctors:
            print(f"Doctor ID: {doc['doctor_id']}")
            print(f"Password: {doc['password']}")
            print(f"Name: {doc['full_name']}")
            print()
        print("=" * 60)
        
    except Exception as e:
        print(f"Error creating default data: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
    