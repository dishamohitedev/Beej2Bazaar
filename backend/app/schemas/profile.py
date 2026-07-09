from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    village: Optional[str] = None
    avatar_url: Optional[str] = None

    farm_size: Optional[float] = None
    farm_unit: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation: Optional[str] = None

    current_crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest: Optional[date] = None

    farming_goals: Optional[list[str]] = None
    onboarding_completed: Optional[bool] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    village: Optional[str] = None
    avatar_url: Optional[str] = None

    farm_size: Optional[float] = None
    farm_unit: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation: Optional[str] = None

    current_crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest: Optional[date] = None

    farming_goals: Optional[list[str]] = None