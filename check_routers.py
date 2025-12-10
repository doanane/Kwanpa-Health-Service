import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Checking router imports...")

# Test each router import
routers_to_check = [
    "auth",
    "users", 
    "health",
    "notifications",
    "superadmin",  # This is the important one!
    "caregivers",
    "doctors",
    "leaderboard",
    "admin"
]

for router_name in routers_to_check:
    try:
        # Try to import the router module
        module_path = f"app.routers.{router_name}"
        module = __import__(module_path, fromlist=["router"])
        
        if hasattr(module, 'router'):
            print(f"✅ {router_name}.py - router found")
            # Check if router has endpoints
            endpoints = [route for route in module.router.routes]
            print(f"   Endpoints: {len(endpoints)}")
        else:
            print(f"❌ {router_name}.py - No router attribute found")
            
    except ImportError as e:
        print(f"❌ {router_name}.py - Import error: {e}")
    except Exception as e:
        print(f"❌ {router_name}.py - Error: {e}")

print("\n" + "=" * 60)
print("Checking if /superadmin/login endpoint will be available...")
print("=" * 60)

# Specifically check superadmin
try:
    from app.routers.superadmin import router
    print("✅ superadmin router imported successfully")
    
    # List all endpoints in superadmin router
    print("\nSuperadmin endpoints:")
    for route in router.routes:
        if hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            path = route.path
            print(f"  {methods} {path}")
            
except ImportError as e:
    print(f"❌ Failed to import superadmin router: {e}")
    print("\nPossible reasons:")
    print("1. app/routers/superadmin.py doesn't exist")
    print("2. Syntax error in superadmin.py")
    print("3. Missing imports in superadmin.py")
    