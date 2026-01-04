import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserProfile
from app.auth.hashing import get_password_hash

logger = logging.getLogger(__name__)

def seed_db():
    """Seed the database with default users (patient and caregiver)"""
    db = SessionLocal()
    try:
        # Seed patient user
        patient_email = "nii@gmail.com"
        existing_patient = db.query(User).filter(User.email == patient_email).first()
        
        if not existing_patient:
            logger.info(f"Seeding default patient user: {patient_email}")
            
            new_patient = User(
                email=patient_email,
                username="nii",
                hashed_password=get_password_hash("StrongPass1"),
                is_active=True,
                is_email_verified=True,
                is_caregiver=False
            )
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            
            patient_profile = UserProfile(
                user_id=new_patient.id,
                full_name="Patient Nii",
                age=30,
                gender="Male",
                chronic_conditions=["Hypertension"],
                profile_completed=True
            )
            db.add(patient_profile)
            db.commit()
            
            logger.info("✅ Default patient user seeded successfully")
        else:
            logger.info("ℹ️ Default patient user already exists, skipping")
        
        # Seed caregiver user
        caregiver_email = "caregiver@gmail.com"
        existing_caregiver = db.query(User).filter(User.email == caregiver_email).first()
        
        if not existing_caregiver:
            logger.info(f"Seeding default caregiver user: {caregiver_email}")
            
            new_caregiver = User(
                email=caregiver_email,
                username="caregiver",
                hashed_password=get_password_hash("StrongPass1"),
                is_active=True,
                is_email_verified=True,
                is_caregiver=True
            )
            db.add(new_caregiver)
            db.commit()
            db.refresh(new_caregiver)
            
            caregiver_profile = UserProfile(
                user_id=new_caregiver.id,
                full_name="Caregiver Nii",
                age=35,
                gender="Female",
                chronic_conditions=[],
                profile_completed=True
            )
            db.add(caregiver_profile)
            db.commit()
            
            logger.info("✅ Default caregiver user seeded successfully")
        else:
            logger.info("ℹ️ Default caregiver user already exists, skipping")
        
        # Seed second patient user
        patient2_email = "patient@gmail.com"
        existing_patient2 = db.query(User).filter(User.email == patient2_email).first()
        
        if not existing_patient2:
            logger.info(f"Seeding second patient user: {patient2_email}")
            
            new_patient2 = User(
                email=patient2_email,
                username="patient",
                hashed_password=get_password_hash("StrongPass1"),
                is_active=True,
                is_email_verified=True,
                is_caregiver=False
            )
            db.add(new_patient2)
            db.commit()
            db.refresh(new_patient2)
            
            patient2_profile = UserProfile(
                user_id=new_patient2.id,
                full_name="Patient Demo",
                age=28,
                gender="Female",
                chronic_conditions=["Diabetes"],
                profile_completed=True
            )
            db.add(patient2_profile)
            db.commit()
            
            logger.info("✅ Second patient user seeded successfully")
        else:
            logger.info("ℹ️ Second patient user already exists, skipping")
            
    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

