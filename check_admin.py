# test_email_flow.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_email_verification_flow():
    print("Testing Email Verification Flow...")
    
    # 1. Sign up a new user
    print("\n1. Signing up new user...")
    signup_data = {
        "email": "verify_test@example.com",
        "password": "TestPass123!",
        "username": "verifytest"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"   Signup Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.json()}")
        return
    
    user_data = response.json()
    user_id = user_data["user_id"]
    print(f"   User created with ID: {user_id}")
    print(f"   Email verified: {user_data['is_email_verified']}")
    
    # Note: In real scenario, you would extract token from email
    # For testing, we'll simulate by getting a new verification token
    print("\n2. Requesting new verification email...")
    verify_response = requests.post(
        f"{BASE_URL}/auth/resend-verification",
        json={"email": "verify_test@example.com"}
    )
    print(f"   Resend Status: {verify_response.status_code}")
    
    # 3. Test password reset
    print("\n3. Testing password reset request...")
    reset_response = requests.post(
        f"{BASE_URL}/auth/forgot-password",
        json={"email": "verify_test@example.com"}
    )
    print(f"   Reset Request Status: {reset_response.status_code}")
    
    # 4. Check the HTML pages exist
    print("\n4. Checking HTML pages...")
    
    # Check verify email page (without token)
    verify_page = requests.get(f"{BASE_URL}/auth/verify-email/invalid_token")
    print(f"   Verify Email Page: {verify_page.status_code}")
    
    # Check reset password page
    reset_page = requests.get(f"{BASE_URL}/auth/reset-password")
    print(f"   Reset Password Page: {reset_page.status_code}")
    
    # 5. Check welcome page
    welcome_page = requests.get(f"{BASE_URL}/welcome")
    print(f"   Welcome Page: {welcome_page.status_code}")
    
    print("\n" + "="*50)
    print("✅ Email Flow Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Check your email for verification link")
    print("2. Click the link to verify email")
    print("3. Test password reset flow")
    print("4. All links should now work with backend URLs")

if __name__ == "__main__":
    test_email_verification_flow()