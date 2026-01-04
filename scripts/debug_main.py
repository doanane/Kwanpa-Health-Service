import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("="*60)
print("MAIN.PY ROUTER LOADING DIAGNOSTIC")
print("="*60)

# Test 1: Try to import the actual caregivers router
print("\n1. Testing caregivers router import...")
try:
    from app.routers.caregivers import router
    print("   SUCCESS: Router imported")
    print(f"   Prefix: {router.prefix}")
    print(f"   Tags: {router.tags}")
    print(f"   Routes count: {len(router.routes)}")
    
    for i, route in enumerate(router.routes[:5]):  # Show first 5
        path = getattr(route, 'path', 'No path')
        methods = getattr(route, 'methods', 'No methods')
        print(f"   {i+1}. {path} - {methods}")
        
except Exception as e:
    print(f"   FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check if there are syntax errors
print("\n2. Checking for syntax errors...")
import subprocess
result = subprocess.run(
    [sys.executable, "-m", "py_compile", "app/routers/caregivers.py"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    print("   No syntax errors")
else:
    print(f"   Syntax error found!")
    print(result.stderr)

# Test 3: Check what routers are actually loaded
print("\n3. Simulating main.py loading...")
from fastapi import FastAPI
test_app = FastAPI()

# Try to load like main.py does
routers_loaded = []

# Try auth router (should work since it shows in docs)
try:
    from app.routers.auth import router as auth_router
    test_app.include_router(auth_router)
    routers_loaded.append(("auth", True))
except Exception as e:
    routers_loaded.append(("auth", False))

# Try caregivers router
try:
    from app.routers.caregivers import router as caregivers_router
    test_app.include_router(caregivers_router)
    routers_loaded.append(("caregivers", True))
except Exception as e:
    routers_loaded.append(("caregivers", False, str(e)))

print("   Router loading results:")
for router_name, *status in routers_loaded:
    if status[0]:
        print(f"   {router_name}: Loaded successfully")
    else:
        print(f"   {router_name}: Failed - {status[1] if len(status) > 1 else 'Unknown'}")

# Test 4: Count routes in test app
print(f"\n4. Routes in test app: {len(test_app.routes)}")
caregiver_routes = [r for r in test_app.routes if hasattr(r, 'path') and '/caregivers' in str(r.path)]
print(f"   Caregiver routes found: {len(caregiver_routes)}")

print("\n" + "="*60)
print("QUICK FIX COMMANDS:")
print("="*60)
print("1. Create simple test router:")
print("   python -c \"from fastapi import APIRouter; r = APIRouter(prefix='/care', tags=['care']); ")
print("   @r.get('/test')\ndef t(): return {'ok': True}; print('Router created')\"")
print("\n2. Check current routes in your running app:")
print("   curl http://localhost:8000/docs 2>/dev/null | grep -i caregiver")
print("\n3. Direct test endpoint:")
print("   curl http://localhost:8000/caregivers/test")
print("="*60)
