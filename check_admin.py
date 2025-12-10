import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.caregiver import Doctor
from app.auth.hashing import get_password_hash

def test_doctor_creation():
    """Test creating a doctor directly"""
    db = SessionLocal()
    try:
        # Test 1: Create without email
        print("Test 1: Creating doctor without email...")
        doctor1 = Doctor(
            doctor_id="DOCTEST1",
            hashed_password=get_password_hash("test123"),
            full_name="Dr. Test One",
            specialization="Testology",
            hospital="Test Hospital",
            created_by="test_admin",
            is_active=True
        )
        
        db.add(doctor1)
        db.commit()
        print("✅ Doctor 1 created without email")
        
        # Test 2: Create with email
        print("\nTest 2: Creating doctor with email...")
        doctor2 = Doctor(
            doctor_id="DOCTEST2",
            hashed_password=get_password_hash("test123"),
            full_name="Dr. Test Two",
            specialization="Testology",
            hospital="Test Hospital",
            email="dr.test@hospital.com",
            created_by="test_admin",
            is_active=True
        )
        
        db.add(doctor2)
        db.commit()
        print("✅ Doctor 2 created with email")
        
        # List doctors
        print("\nAll doctors in database:")
        doctors = db.query(Doctor).all()
        for doc in doctors:
            print(f"  - {doc.doctor_id}: {doc.full_name} (Email: {doc.email})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_doctor_creation()