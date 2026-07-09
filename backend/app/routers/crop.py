from fastapi import APIRouter, Depends
from app.services.crop_service import CropService
from app.dependencies.auth import get_current_user
from app.schemas.crop import CropUpdate

router = APIRouter(prefix="/crop", tags=["Crop"])


@router.get("")
def get_current_crop(user=Depends(get_current_user)):
    return CropService.get_crop(user.id)


@router.patch("")
def update_current_crop(
    data: CropUpdate,
    user=Depends(get_current_user),
):
    payload = data.model_dump(mode="json", exclude_none=True)
    return CropService.update_crop(user.id, payload)


@router.post("/harvest")
def harvest(user=Depends(get_current_user)):
    return CropService.harvest_crop(user.id)