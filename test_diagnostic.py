# test_diagnostic.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== CAREGIVERS ROUTER DIAGNOSTIC ===")

# Test 1: Check if file exists
caregivers_path = os.path.join("app", "routers", "caregivers.py")
print(f"1. File exists: {os.path.exists(caregivers_path)}")

# Test 2: Try to import
try:
    from app.routers.caregivers import router
    print("2. ✅ Router imported successfully")
    print(f"   Prefix: {router.prefix}")
    print(f"   Tags: {router.tags}")
    print(f"   Routes: {len(router.routes)}")
    
    for route in router.routes:
        print(f"   - {getattr(route, 'path', 'N/A')}")
        
except Exception as e:
    print(f"2. ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check models exist
try:
    from app.models.user import User
    from app.models.caregiver import CaregiverRelationship
    print("3. ✅ Models imported successfully")
except Exception as e:
    print(f"3. ❌ Models import failed: {e}")

print("=== END DIAGNOSTIC ===")