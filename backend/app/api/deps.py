"""
Shared dependency helpers for API endpoints.

Usage in endpoint modules:
    from app.api import deps
    @router.get("/...")
    async def handler(db: AsyncSession = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
        ...
"""

from backend.app.db.session import get_db  # AsyncSession provider
from backend.app.core.security import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
)
from backend.app.db.models import User

def is_superuser(user: User) -> bool:
    """Return True if the user has an 'admin' role or is_superuser attribute."""
    if getattr(user, "is_superuser", False):
        return True
    try:
        roles = getattr(user, "roles", []) or []
        return any(getattr(r, "name", None) == "admin" for r in roles)
    except Exception:
        return False

__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_active_superuser",
    "is_superuser",
]
