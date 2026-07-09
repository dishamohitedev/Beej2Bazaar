from datetime import date
from typing import Optional

from pydantic import BaseModel


class CropUpdate(BaseModel):
    current_crop_id: Optional[str] = None
    growth_stage: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest: Optional[date] = None