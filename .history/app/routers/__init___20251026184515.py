from .auth import router as auth_router
from .users import router as users_router
from .health import router as health_router
from .notifications import router as notifications_router
from .caregivers import router as caregivers_router

__all__ = [
    "auth_router",
    "users_router", 
    "health_router",
    "notifications_router",
    "caregivers_router"
]