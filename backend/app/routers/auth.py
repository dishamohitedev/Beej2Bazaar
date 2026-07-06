from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import LoginRequest
from app.services.auth_service import sign_in

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
async def login(data: LoginRequest):
    response = sign_in(data.email, data.password)

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "expires_at": response.session.expires_at,
    }


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }