from .admin import r as admin_router
from .user import r as user_router
from .start import r as start_router

routers = [admin_router, start_router, user_router]
