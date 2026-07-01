"""
Authentication API — Phone OTP based, role-aware.

Flow:
  1. POST /api/auth/otp/request   {phone}
     -> sends OTP (mock: always "123456"; prod: handled by Firebase client SDK)

  2. POST /api/auth/otp/verify    {phone, otp, role?, name?}
     -> verifies OTP. If user doesn't exist yet, `role` is required (first-time
        registration). Returns access + refresh JWT plus the user object.

  3. POST /api/auth/refresh       {refresh_token}
     -> exchanges a valid refresh token for a new access token.

  4. GET  /api/auth/me            (Bearer token required)
     -> returns the current authenticated user.
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request

from app.models.user import (
    OTPRequestIn, OTPVerifyIn, RefreshIn, TokenPair, UserPublic, UserInDB,
)
from app.services.otp_service import otp_service
from app.db.user_repository import user_repository
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.middleware.rbac import get_current_user
from app.middleware.rate_limit import check_rate_limit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _to_public(user: UserInDB) -> UserPublic:
    return UserPublic(
        id=user.id, phone=user.phone, name=user.name,
        role=user.role, is_profile_complete=user.is_profile_complete,
    )


@router.post("/otp/request", status_code=status.HTTP_200_OK)
async def request_otp(payload: OTPRequestIn, request: Request):
    # Rate limit: max 5 OTP requests per phone number per 10 minutes
    check_rate_limit(f"otp_req:{payload.phone}", max_requests=5, window_seconds=600)
    await otp_service.send_otp(payload.phone)
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify", response_model=TokenPair)
async def verify_otp(payload: OTPVerifyIn):
    # Rate limit: max 10 verify attempts per phone number per 10 minutes (anti-brute-force)
    check_rate_limit(f"otp_verify:{payload.phone}", max_requests=10, window_seconds=600)

    is_valid = await otp_service.verify(payload.phone, payload.otp)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")

    user = await user_repository.get_by_phone(payload.phone)

    if not user:
        # First-time login = registration. Role is mandatory here.
        if not payload.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New account: 'role' is required on first verification",
            )
        user = await user_repository.create(phone=payload.phone, role=payload.role, name=payload.name)

    access_token = create_access_token(user.id, user.phone, user.role.value)
    refresh_token = create_refresh_token(user.id)

    return TokenPair(access_token=access_token, refresh_token=refresh_token, user=_to_public(user))


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(payload: RefreshIn):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = await user_repository.get_by_id(decoded["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access_token = create_access_token(user.id, user.phone, user.role.value)
    new_refresh_token = create_refresh_token(user.id)

    return TokenPair(access_token=access_token, refresh_token=new_refresh_token, user=_to_public(user))


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    return _to_public(current_user)
