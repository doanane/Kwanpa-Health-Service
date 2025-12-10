import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models.caregiver import Doctor
from app.models.admin import Admin
from app.auth.hashing import get_password_hash
import secrets

def create_tables_if_not_exists():
    """Create database tables if they don't exist"""
    try:
        create_tables()
        print("✓ Database tables created/verified")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

def create_superadmin():
    """Create initial superadmin user with email login"""
    db = SessionLocal()
    try:
        # Check if superadmin already exists
        existing_admin = db.query(Admin).filter(Admin.email == "superadmin@hewal3.com").first()
        if existing_admin:
            print(f"Superadmin already exists:")
            print(f"  Email: {existing_admin.email}")
            print(f"  Full Name: {existing_admin.full_name}")
            print(f"  Is Superadmin: {existing_admin.is_superadmin}")
            return existing_admin
        
        # Create superadmin credentials
        superadmin_email = "superadmin@hewal3.com"
        superadmin_password = "Super@1234"  # Strong default password
        
        superadmin = Admin(
            email=superadmin_email,
            hashed_password=get_password_hash(superadmin_password),
            full_name="System Super Administrator",
            is_superadmin=True,
            is_active=True,
            permissions='{"all": true, "create_doctor": true, "delete_user": true, "view_all": true, "manage_admins": true}'
        )
        
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        
        print("=" * 60)
        print("SUPER ADMIN CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Email: {superadmin_email}")
        print(f"Password: {superadmin_password}")
        print(f"Full Name: {superadmin.full_name}")
        print("=" * 60)
        print("IMPORTANT: Login and change this password immediately!")
        print("=" * 60)
        
        return superadmin
        
    except Exception as e:
        print(f"Error creating superadmin: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

def create_sample_doctors():
    """Create sample doctors for testing"""
    db = SessionLocal()
    try:
        # Sample doctors
        sample_doctors = [
            {
                "doctor_id": "DOC001001",
                "full_name": "Dr. Kwame Mensah",
                "specialization": "Cardiology",
                "hospital": "Korle Bu Teaching Hospital",
                "email": "dr.mensah@korbu.com",
                "password": "Doctor@123"
            },
            {
                "doctor_id": "DOC001002", 
                "full_name": "Dr. Ama Serwaa",
                "specialization": "Endocrinology",
                "hospital": "37 Military Hospital",
                "email": "dr.serwaa@37military.com",
                "password": "Doctor@123"
            },
            {
                "doctor_id": "DOC001003",
                "full_name": "Dr. Kofi Ansah",
                "specialization": "General Physician",
                "hospital": "Ridge Hospital",
                "email": "dr.ansah@ridge.com",
                "password": "Doctor@123"
            }
        ]
        
        created_count = 0
        for doc_data in sample_doctors:
            # Check if doctor exists
            existing = db.query(Doctor).filter(Doctor.doctor_id == doc_data["doctor_id"]).first()
            if not existing:
                doctor = Doctor(
                    doctor_id=doc_data["doctor_id"],
                    hashed_password=get_password_hash(doc_data["password"]),
                    full_name=doc_data["full_name"],
                    specialization=doc_data["specialization"],
                    hospital=doc_data["hospital"],
                    email=doc_data["email"],
                    created_by="system"
                )
                db.add(doctor)
                created_count += 1
                print(f"✓ Created doctor: {doc_data['doctor_id']} - {doc_data['full_name']}")
            else:
                print(f"⚠ Doctor already exists: {doc_data['doctor_id']}")
        
        db.commit()
        
        if created_count > 0:
            print(f"\nCreated {created_count} sample doctors")
            print("\nSample Doctor Credentials:")
            print("-" * 60)
            for doc in sample_doctors:
                print(f"Doctor ID: {doc['doctor_id']}")
                print(f"Password: {doc['password']}")
                print(f"Name: {doc['full_name']}")
                print(f"Email: {doc['email']}")
                print(f"Specialization: {doc['specialization']}")
                print("-" * 60)
        
        return created_count
        
    except Exception as e:
        print(f"Error creating doctors: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 0
    finally:
        db.close()

def check_database():
    """Check database connection and existing data"""
    db = SessionLocal()
    try:
        # Count existing data
        admin_count = db.query(Admin).count()
        doctor_count = db.query(Doctor).count()
        
        print("\n" + "=" * 60)
        print("DATABASE STATUS")
        print("=" * 60)
        print(f"Admins in database: {admin_count}")
        print(f"Doctors in database: {doctor_count}")
        print("=" * 60)
        
        # List all admins
        if admin_count > 0:
            print("\nExisting Admins:")
            admins = db.query(Admin).all()
            for admin in admins:
                print(f"  - Email: {admin.email}")
                print(f"    Name: {admin.full_name}")
                print(f"    Type: {'Superadmin' if admin.is_superadmin else 'Admin'}")
                print(f"    Active: {admin.is_active}")
                print()
        
        # List all doctors
        if doctor_count > 0:
            print("\nExisting Doctors:")
            doctors = db.query(Doctor).all()
            for doctor in doctors:
                print(f"  - ID: {doctor.doctor_id}")
                print(f"    Name: {doctor.full_name}")
                print(f"    Email: {doctor.email}")
                print(f"    Specialization: {doctor.specialization}")
                print(f"    Active: {doctor.is_active}")
                print()
        
        return True
        
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def create_admin_cli():
    """CLI to create new admin from terminal"""
    print("\n" + "=" * 60)
    print("CREATE NEW ADMIN")
    print("=" * 60)
    
    email = input("Enter admin email: ").strip()
    if not email:
        print("Email is required!")
        return
    
    full_name = input("Enter full name: ").strip()
    if not full_name:
        print("Full name is required!")
        return
    
    is_superadmin = input("Is superadmin? (y/n): ").strip().lower() == 'y'
    
    password = input("Enter password (min 8 chars): ").strip()
    if len(password) < 8:
        print("Password must be at least 8 characters!")
        return
    
    confirm = input(f"Create admin '{email}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"❌ Admin with email '{email}' already exists!")
            return
        
        # Create new admin
        admin = Admin(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_superadmin=is_superadmin,
            is_active=True,
            permissions='{"all": true}' if is_superadmin else '{"view_dashboard": true}'
        )
        
        db.add(admin)
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ ADMIN CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Full Name: {full_name}")
        print(f"Type: {'Superadmin' if is_superadmin else 'Regular Admin'}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("HEWAL3 System Initialization")
    print("=" * 60)
    
    # Step 1: Ensure tables exist
    print("\n1. Checking/Creating database tables...")
    if not create_tables_if_not_exists():
        print("Failed to create tables. Exiting.")
        return
    
    # Step 2: Create superadmin
    print("\n2. Creating Super Administrator...")
    superadmin = create_superadmin()
    
    # Step 3: Create sample doctors
    print("\n3. Creating Sample Doctors...")
    create_sample_doctors()
    
    # Step 4: Check database
    print("\n4. Checking Database...")
    check_database()
    
    # Step 5: Ask if user wants to create another admin
    print("\n5. Additional Options")
    print("-" * 60)
    choice = input("Create another admin? (y/n): ").strip().lower()
    if choice == 'y':
        create_admin_cli()
    
    print("\n" + "=" * 60)
    print("✅ INITIALIZATION COMPLETE")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Login as Super Admin:")
    print("   - Email: superadmin@hewal3.com")
    print("   - Password: Super@1234")
    print("3. Access API Documentation: http://localhost:8000/docs")
    print("4. Use the access token from login for other endpoints")
    print("\n🔧 ADMIN MANAGEMENT:")
    print("- Create new admins through CLI (run this script again)")
    print("- Or use the superadmin interface after login")
    print("=" * 60)

if __name__ == "__main__":
    main()