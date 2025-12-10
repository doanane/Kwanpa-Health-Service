# This file makes the routers directory a Python package

# You can import all routers here for easier access
from .auth import router as auth_router
from .users import router as users_router
from .health import router as health_router
from .notifications import router as notifications_router
from .caregivers import router as caregivers_router
from .doctors import router as doctors_router
from .leaderboard import router as leaderboard_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "health_router",
    "notifications_router",
    "caregivers_router",
    "doctors_router",
    "leaderboard_router",
    "admin_router"
]