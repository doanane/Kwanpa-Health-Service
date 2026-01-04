import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.caregiver import Doctor
from app.auth.hashing import get_password_hash

def create_initial_doctors():
    db = SessionLocal()
    try:
        initial_doctors = [
            {
                "doctor_id": "DOC001234",
                "full_name": "Dr. Kwame Mensah",
                "specialization": "Cardiology",
                "hospital": "Korle Bu Teaching Hospital",
                "password": "doctor123"
            },
            {
                "doctor_id": "DOC005678",
                "full_name": "Dr. Ama Serwaa",
                "specialization": "Endocrinology",
                "hospital": "37 Military Hospital",
                "password": "doctor123"
            },
            {
                "doctor_id": "DOC009012",
                "full_name": "Dr. Kofi Ansah",
                "specialization": "General Physician",
                "hospital": "Ridge Hospital",
                "password": "doctor123"
            }
        ]
        
        created_count = 0
        for doc_data in initial_doctors:
            # Check if already exists
            existing = db.query(Doctor).filter(Doctor.doctor_id == doc_data["doctor_id"]).first()
            if not existing:
                doctor = Doctor(
                    doctor_id=doc_data["doctor_id"],
                    hashed_password=get_password_hash(doc_data["password"]),
                    full_name=doc_data["full_name"],
                    specialization=doc_data["specialization"],
                    hospital=doc_data["hospital"],
                    created_by="system"
                )
                db.add(doctor)
                created_count += 1
                print(f"Created doctor: {doc_data['doctor_id']} - {doc_data['full_name']}")
        
        db.commit()
        print(f"\nSuccessfully created {created_count} doctors!")
        print("\nDoctor IDs and passwords:")
        print("-------------------------")
        for doc in initial_doctors:
            print(f"ID: {doc['doctor_id']} | Password: {doc['password']} | Name: {doc['full_name']}")
        
    except Exception as e:
        print(f"Error creating doctors: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_doctors()