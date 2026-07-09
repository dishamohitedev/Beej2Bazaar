from typing import Literal
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    full_name: str
    language: str

    state: str
    district: str
    taluka: str
    village: str

    farm_size: float = Field(gt=0)
    farm_unit: Literal["acre"] = "acre"

    soil_type: str
    irrigation: str

    farming_goals: list[str]

    current_crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest: Optional[date] = None

class OnboardingStatus(BaseModel):
    completed: bool