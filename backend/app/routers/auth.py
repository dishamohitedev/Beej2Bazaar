from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.dependencies.auth import get_current_user
from app.schemas.auth import LoginRequest
from app.services.auth_service import sign_in, sign_up
from app.schemas.auth import SignupRequest
from app.services.profile_service import ProfileService
from app.database.supabase import admin_supabase

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

class OTPRequest(BaseModel):
    phone: str

class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str
    role: Optional[str] = None
    name: Optional[str] = None


@router.post("/otp/request")
async def otp_request(data: OTPRequest):
    # Mock OTP request - always succeeds
    return {"message": "OTP sent successfully"}


@router.post("/otp/verify")
async def otp_verify(data: OTPVerifyRequest):
    if data.otp != "123456":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP. Try again."
        )

    # Map phone to a mock email/password for Supabase authentication
    clean_phone = data.phone.replace("+", "").replace(" ", "").strip()
    email = f"phone_{clean_phone}@beejbazaar.com"
    password = f"password_{clean_phone}"

    # Try signing in first
    try:
        session = sign_in(email, password)
    except Exception:
        # If user does not exist, create a new one using admin client
        try:
            admin_supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "role": data.role or "farmer",
                    "name": data.name or "Farmer"
                }
            })
            # Sign in after successful creation
            session = sign_in(email, password)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to verify and authenticate: {str(e)}"
            )

    # Resolve corresponding DB profile row
    profile = ProfileService.get_or_create_profile(session.user)

    # Sync name/phone updates if present
    update_data = {}
    if not profile.get("phone") and data.phone:
        update_data["phone"] = data.phone
    if not profile.get("full_name") and data.name:
        update_data["full_name"] = data.name
    
    # Store/update user metadata role if necessary
    user_metadata = session.user.user_metadata or {}
    metadata_updated = False
    if data.role and user_metadata.get("role") != data.role:
        user_metadata["role"] = data.role
        metadata_updated = True
    if data.name and user_metadata.get("name") != data.name:
        user_metadata["name"] = data.name
        metadata_updated = True

    if metadata_updated:
        try:
            admin_supabase.auth.admin.update_user_by_id(
                session.user.id,
                {"user_metadata": user_metadata}
            )
            # Re-fetch user to update session user attributes
            user_res = admin_supabase.auth.admin.get_user_by_id(session.user.id)
            session.user = user_res.user
        except Exception:
            pass

    if update_data:
        try:
            ProfileService.update_profile(session.user.id, update_data)
            # Fetch updated profile
            profile = ProfileService.get_or_create_profile(session.user)
        except Exception:
            pass

    return {
        "access_token": session.session.access_token,
        "refresh_token": session.session.refresh_token,
        "user": {
            "id": session.user.id,
            "email": session.user.email,
            "phone": profile.get("phone") or data.phone,
            "name": profile.get("full_name") or session.user.user_metadata.get("name") or "",
            "role": session.user.user_metadata.get("role") or data.role or "farmer",
            "is_profile_complete": profile.get("onboarding_completed") or False
        }
    }


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
    profile = ProfileService.get_or_create_profile(current_user)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "phone": profile.get("phone") or "",
        "name": profile.get("full_name") or current_user.user_metadata.get("name") or "",
        "role": current_user.user_metadata.get("role") or "farmer",
        "is_profile_complete": profile.get("onboarding_completed") or False
    }


@router.post("/signup")
def signup(data: SignupRequest):

    response = sign_up(data.email, data.password)

    # Create profile row if it doesn't exist
    ProfileService.get_or_create_profile(response.user)

    return {
        "message": "Signup successful",
        "user_id": response.user.id
    }