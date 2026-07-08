from typing import Literal

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

    current_crops: list[str]
    farming_goals: list[str]


class OnboardingStatus(BaseModel):
    completed: bool