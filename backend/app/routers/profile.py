from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileUpdate

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.get("/me")
def get_my_profile(current_user=Depends(get_current_user)):
    return ProfileService.get_or_create_profile(current_user)


@router.patch("/me")
def update_my_profile(
    profile: ProfileUpdate,
    current_user=Depends(get_current_user),
):
    return ProfileService.update_profile(
        current_user.id,
        profile.model_dump(exclude_unset=True),
    )