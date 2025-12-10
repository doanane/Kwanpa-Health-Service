import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    print("Testing HEWAL3 API Endpoints")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/docs", "Swagger documentation"),
    ]
    
    print("\n📋 AVAILABLE ENDPOINTS:")
    print("-" * 60)
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            status = "✅" if response.status_code < 400 else "❌"
            print(f"{status} {method} {endpoint} - {description}")
            print(f"   Status: {response.status_code}")
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - {description}")
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("🔐 AUTHENTICATION ENDPOINTS:")
    print("-" * 60)
    print("For Patients/Users:")
    print("  POST /auth/login - User login (email & password)")
    print("  POST /auth/signup - User registration")
    print("\nFor Doctors:")
    print("  POST /doctors/login - Doctor login (doctor_id & password)")
    print("\nFor Super Admin:")
    print("  POST /superadmin/login - Admin login (email & password)")
    print("=" * 60)

def test_superadmin_login():
    print("\n🧪 TESTING SUPER ADMIN LOGIN")
    print("-" * 60)
    
    # Try the correct endpoint
    login_data = {
        "email": "superadmin@hewal3.com",
        "password": "Super@1234"
    }
    
    print(f"Testing login with: {login_data['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/superadmin/login",
            json=login_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"Access Token: {data['access_token'][:50]}...")
            print(f"Admin Email: {data['admin']['email']}")
            print(f"Is Superadmin: {data['admin']['is_superadmin']}")
            
            # Test using the token
            headers = {"Authorization": f"Bearer {data['access_token']}"}
            
            # Test dashboard
            print("\n🧪 Testing dashboard access...")
            dash_response = requests.get(
                f"{BASE_URL}/superadmin/dashboard",
                headers=headers,
                timeout=10
            )
            
            if dash_response.status_code == 200:
                dash_data = dash_response.json()
                print(f"✅ Dashboard accessible!")
                print(f"Dashboard Type: {dash_data['dashboard_type']}")
                print(f"Admin Name: {dash_data['admin_info']['full_name']}")
            else:
                print(f"❌ Dashboard failed: {dash_response.status_code}")
                print(dash_response.text)
                
        else:
            print(f"❌ Login failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")

def create_your_own_superadmin():
    print("\n👨‍💼 CREATE YOUR OWN SUPER ADMIN")
    print("-" * 60)
    
    # First login with default superadmin
    default_login = {
        "email": "superadmin@hewal3.com",
        "password": "Super@1234"
    }
    
    print("1. Logging in with default superadmin...")
    
    try:
        # Get default admin token
        login_response = requests.post(
            f"{BASE_URL}/superadmin/login",
            json=default_login,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Cannot login with default superadmin")
            print("Creating your admin directly in database...")
            create_admin_directly()
            return
        
        default_token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {default_token}"}
        
        print("✅ Logged in with default superadmin")
        
        # Create your admin
        your_admin_data = {
            "email": "superadmin@gmail.com",
            "password": "super1234",
            "full_name": "Your Name",
            "is_superadmin": True
        }
        
        print(f"\n2. Creating your admin: {your_admin_data['email']}")
        
        create_response = requests.post(
            f"{BASE_URL}/superadmin/create-admin",
            json=your_admin_data,
            headers=headers,
            timeout=10
        )
        
        if create_response.status_code == 201:
            print("✅ Your admin created successfully!")
            admin_data = create_response.json()
            print(f"Email: {admin_data['admin']['email']}")
            print(f"Password: {your_admin_data['password']}")
            print(f"Full Name: {admin_data['admin']['full_name']}")
            print(f"Is Superadmin: {admin_data['admin']['is_superadmin']}")
            
            # Test login with your admin
            print(f"\n3. Testing login with your admin...")
            your_login = {
                "email": your_admin_data['email'],
                "password": your_admin_data['password']
            }
            
            your_login_response = requests.post(
                f"{BASE_URL}/superadmin/login",
                json=your_login,
                timeout=10
            )
            
            if your_login_response.status_code == 200:
                print("✅ Your admin login successful!")
                your_token = your_login_response.json()['access_token']
                print(f"Your Access Token: {your_token[:50]}...")
            else:
                print(f"❌ Your admin login failed")
                print(your_login_response.text)
                
        else:
            print(f"❌ Failed to create your admin")
            print(create_response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def create_admin_directly():
    """Fallback: Create admin directly in database"""
    print("\nCreating admin directly in database...")
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app.database import SessionLocal
    from app.models.admin import Admin
    from app.auth.hashing import get_password_hash
    
    db = SessionLocal()
    try:
        # Create your admin
        your_admin = Admin(
            email="superadmin@gmail.com",
            hashed_password=get_password_hash("super1234"),
            full_name="Your Name",
            is_superadmin=True,
            is_active=True,
            permissions='{"all": true}'
        )
        
        db.add(your_admin)
        db.commit()
        
        print("✅ Your admin created directly in database!")
        print(f"Email: superadmin@gmail.com")
        print(f"Password: super1234")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("HEWAL3 API Testing Script")
    print("=" * 60)
    
    # Test if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server is not responding properly")
            return
    except:
        print("❌ Server is not running. Start it with: uvicorn app.main:app --reload")
        return
    
    # Show available endpoints
    test_all_endpoints()
    
    # Test superadmin login
    test_superadmin_login()
    
    # Create your own superadmin
    create_your_own_superadmin()
    
    print("\n" + "=" * 60)
    print("📚 SUMMARY")
    print("=" * 60)
    print("\nFor Super Admin access:")
    print("1. Use endpoint: POST /superadmin/login")
    print("2. NOT: POST /auth/login (that's for patients/users)")
    print("\nDefault credentials:")
    print("  Email: superadmin@hewal3.com")
    print("  Password: Super@1234")
    print("\nYour credentials (after creation):")
    print("  Email: superadmin@gmail.com")
    print("  Password: super1234")
    print("=" * 60)

if __name__ == "__main__":
    main()
    