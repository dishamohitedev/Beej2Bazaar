from pydantic import BaseModel, Field
from typing import Optional, List

class IrrigationProfile(BaseModel):
    id: str
    full_name: str
    state: str
    district: str
    taluka: str
    village: str
    soil_type: str
    irrigation: str  # Drip, Sprinkler, Canal, Flood, Rainfed, etc.
    language: str
    farm_size: float
    farm_unit: str = "acre"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DailyWeather(BaseModel):
    date: str  # YYYY-MM-DD
    temp_min: float
    temp_max: float
    precipitation: float  # mm
    wind_speed: float  # km/h
    relative_humidity: float  # % (relative humidity mean)
    eto: Optional[float] = None  # Reference Evapotranspiration (mm/day)

class WeatherForecastData(BaseModel):
    daily_forecasts: List[DailyWeather]

class PyFAOOutput(BaseModel):
    eto: float  # Reference ET (mm/day)
    etc: float  # Crop ET (mm/day)
    water_requirement_mm: float  # Crop Water Requirement (mm/day)

class DailyScheduleItem(BaseModel):
    date: str  # YYYY-MM-DD
    irrigate: bool
    water_mm: float  # gross irrigation water depth (mm)
    reason: str
    electricity_slot: Optional[str] = None  # e.g., '08:00 AM - 04:00 PM (Day Slot)'
    pump_run_time_str: Optional[str] = None  # e.g., '1 hr 15 mins'

class IrrigationScheduleResponse(BaseModel):
    today: DailyScheduleItem
    next_irrigation: Optional[str] = None  # YYYY-MM-DD
    schedule: List[DailyScheduleItem]
    explanation: Optional[str] = None  # Gemini natural language explanation

class WaterSource(BaseModel):
    id: Optional[str] = None
    user_id: str
    source_name: str
    source_type: str
    current_level_pct: int
    max_capacity_liters: Optional[float] = None
    updated_at: Optional[str] = None
