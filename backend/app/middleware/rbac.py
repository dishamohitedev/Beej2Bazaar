"""
Role-based access control.

Usage in any router:

    from app.middleware.rbac import get_current_user, require_roles
    from app.models.user import UserRole

    @router.get("/farms/{farm_id}")
    async def get_farm(farm_id: str, user=Depends(require_roles(UserRole.FARMER, UserRole.ADMIN))):
        ...

`get_current_user` alone just requires "any authenticated user".
`require_roles(...)` additionally restricts to specific roles.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_token
from app.db.user_repository import user_repository
from app.models.user import UserInDB, UserRole

# tokenUrl is just for OpenAPI docs' "Authorize" button; actual login is /api/auth/otp/verify
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/otp/verify", auto_error=False)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    user = await user_repository.get_by_id(user_id)
    if not user or not user.is_active:
        raise credentials_exception

    return user


def require_roles(*allowed_roles: UserRole):
    async def dependency(user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role.value}' is not permitted to access this resource",
            )
        return user

    return dependency
