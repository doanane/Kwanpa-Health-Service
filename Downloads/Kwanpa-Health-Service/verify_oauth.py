
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("VERIFYING GOOGLE OAUTH CONFIGURATION")
print("="*70)


env_vars = {
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
    "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI"),
    "BASE_URL": os.getenv("BASE_URL")
}

for key, value in env_vars.items():
    if value:
        print(f"{key}: {value}")
        
        
        if key == "GOOGLE_REDIRECT_URI":
            if "//auth" in value:
                print(f"   🔴 ERROR: Double slash in redirect URI!")
            if "southafricanorth" not in value:
                print(f"    WARNING: Check domain spelling")
            if not value.endswith("/auth/google/callback"):
                print(f"    WARNING: Should end with /auth/google/callback")
    else:
        print(f"{key}: Not set in environment")


try:
    from app.config import settings
    print(f"\nConfig import successful")
    
    if hasattr(settings, 'GOOGLE_REDIRECT_URI'):
        print(f"Settings.GOOGLE_REDIRECT_URI: {settings.GOOGLE_REDIRECT_URI}")
        
        
        env_uri = env_vars["GOOGLE_REDIRECT_URI"]
        settings_uri = settings.GOOGLE_REDIRECT_URI
        
        if env_uri != settings_uri:
            print(f"    WARNING: Environment and settings don't match!")
            print(f"   Env: {env_uri}")
            print(f"   Settings: {settings_uri}")
        
except Exception as e:
    print(f"\nError importing config: {e}")

print("\n" + "="*70)
print("GOOGLE CLOUD CONSOLE CHECKLIST:")
print("="*70)
print("1. Go to: https://console.cloud.google.com/")
print("2. Navigation Menu → APIs & Services → Credentials")
print("3. Click your OAuth 2.0 Client ID (Web application)")
print("4. Scroll to 'Authorised redirect URIs'")
print("5. ADD this EXACT URI:")
print("   https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net/auth/google/callback")
print("6. Click SAVE")
print("7. Wait 5-10 minutes")
print("8. Test OAuth login again")
print("="*70)


print("\nMake sure these URIs are NOT in Google Console (remove if present):")
bad_uris = [
    "https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net//auth/google/callback",
    "https://hewal3-backend-api-aya3dzgefte4b3c3.southafriAnorth-01.azurewebsites.net/auth/google/callback",  
    "https://hewal3-backend-api-aya3dzgefte4b3c3.southafricaNorth-01.azurewebsites.net/auth/google/callback",  
]

for uri in bad_uris:
    print(f"   {uri}")