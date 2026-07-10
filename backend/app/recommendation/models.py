from pydantic import BaseModel, Field
from typing import Optional, List

# scientific Python-based mapping of crop roots to compatible soil types
CROP_SOIL_COMPATIBILITY = {
    # Cereals & Millets
    "Rice": ["Alluvial", "Clayey", "Loamy", "Red"],
    "Wheat": ["Alluvial", "Loamy", "Clayey", "Black"],
    "Maize": ["Alluvial", "Loamy", "Red", "Sandy"],
    "Sorghum": ["Black", "Alluvial", "Loamy", "Red"],
    "Pearl Millet": ["Sandy", "Black", "Red", "Loamy"],
    "Finger Millet": ["Red", "Loamy", "Sandy", "Laterite"],
    
    # Pulses
    "Chickpea": ["Alluvial", "Clayey", "Loamy", "Black"],
    "Pigeon Pea": ["Alluvial", "Loamy", "Black", "Red"],
    "Green Gram": ["Alluvial", "Loamy", "Black", "Red"],
    "Black Gram": ["Alluvial", "Loamy", "Black", "Red"],
    "Lentil": ["Alluvial", "Clayey", "Loamy", "Black"],
    
    # Oilseeds
    "Soybean": ["Black", "Loamy", "Alluvial"],
    "Groundnut": ["Sandy", "Red", "Loamy"],
    "Mustard": ["Alluvial", "Loamy", "Sandy"],
    "Sesame": ["Alluvial", "Loamy", "Red", "Sandy"],
    "Sunflower": ["Black", "Alluvial", "Loamy", "Red"],
    
    # Cash / Commercial
    "Sugarcane": ["Alluvial", "Black", "Loamy", "Clayey"],
    "Cotton": ["Black", "Alluvial", "Loamy"],
    "Jute": ["Alluvial", "Loamy"],
    "Tobacco": ["Alluvial", "Loamy", "Sandy", "Red"],
    "Rubber": ["Laterite", "Red", "Sandy"],
    
    # Fruits
    "Mango": ["Alluvial", "Loamy", "Red", "Laterite"],
    "Banana": ["Alluvial", "Loamy", "Black", "Clayey"],
    "Coconut": ["Sandy", "Alluvial", "Laterite"],
    "Apple": ["Loamy", "Red"],
    "Cashew": ["Laterite", "Red", "Sandy"],
    "Citrus": ["Alluvial", "Loamy", "Black", "Red"],
    "Guava": ["Alluvial", "Loamy", "Black", "Red"],
    "Pomegranate": ["Alluvial", "Loamy", "Black", "Red"],
    "Grapes": ["Alluvial", "Loamy", "Black", "Red"],
    
    # Spices
    "Turmeric": ["Laterite", "Red", "Loamy", "Alluvial"],
    "Ginger": ["Laterite", "Red", "Loamy", "Alluvial"],
    "Cardamom": ["Laterite", "Red", "Loamy", "Alluvial"],
    "Black Pepper": ["Laterite", "Red", "Loamy", "Alluvial"],
    "Coriander": ["Alluvial", "Loamy", "Black"],
    "Cumin": ["Alluvial", "Loamy", "Black"],
    
    # Vegetables
    "Tomato": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Onion": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Chilli": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Brinjal": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Okra": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Potato": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Cabbage": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    "Cauliflower": ["Alluvial", "Loamy", "Black", "Red", "Sandy"],
    
    # Flowers
    "Rose": ["Alluvial", "Loamy", "Red"],
    "Marigold": ["Alluvial", "Loamy", "Red"],
    "Tuberose": ["Alluvial", "Loamy", "Red"],
    "Jasmine": ["Alluvial", "Loamy", "Red"],
    
    # Medicinal
    "Ashwagandha": ["Sandy", "Loamy", "Red"],
    "Tulsi": ["Sandy", "Loamy", "Red"],
    "Aloe Vera": ["Sandy", "Loamy", "Red"],
    
    # Fodder
    "Berseem": ["Alluvial", "Loamy", "Black", "Clayey"],
    "Lucerne": ["Alluvial", "Loamy", "Black", "Clayey"],
    "Napier Grass": ["Alluvial", "Loamy", "Black", "Clayey"]
}


class CropRecord(BaseModel):
    id: str
    crop_name: str
    scientific_name: str
    season: str
    duration_days: int
    water_requirement: str  # 'Low', 'Medium', 'High'
    soil_types: Optional[List[str]] = None
    ideal_temp_min: int
    ideal_temp_max: int
    ideal_rainfall_mm: int
    description: Optional[str] = None
    crop_type: str
    growth_season: str

    def get_compatible_soil_types(self) -> List[str]:
        """Returns compatible soils from database, falling back to a python-based mapping if null."""
        if self.soil_types:
            return self.soil_types
        # Extract root crop name (e.g. "Rice - Basmati 1121" -> "Rice")
        root_name = self.crop_name.split("-")[0].strip()
        return CROP_SOIL_COMPATIBILITY.get(root_name, ["Alluvial", "Loamy"])  # Fallback to default safe soils


class FarmerProfile(BaseModel):
    id: str
    full_name: str
    state: str
    district: str
    taluka: str
    village: str
    soil_type: str  # e.g., 'Black', 'Clayey', 'Loamy', etc.
    irrigation: str  # e.g., 'Drip', 'Sprinkler', 'Canal', 'Borewell', 'Rainfed'
    language: str  # e.g., 'English', 'Hindi', etc.
    farm_size: float
    farm_unit: str = "acre"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class WeatherForecast(BaseModel):
    temp_min: float
    temp_max: float
    rainfall_mm: float
    description: Optional[str] = "Clear sky"


class MarketPrice(BaseModel):
    crop_name: str
    commodity: str
    state: str
    district: str
    market: str
    min_price: float  # Price per quintal (INR)
    max_price: float
    modal_price: float


class SeasonInfo(BaseModel):
    current_month: int  # 1 to 12
    current_season: str  # 'Kharif', 'Rabi', 'Zaid', 'Annual', 'Perennial'


class RecommendationContext(BaseModel):
    profile: FarmerProfile
    weather: WeatherForecast
    market: List[MarketPrice] = Field(default_factory=list)
    season: SeasonInfo


class ScoreBreakdown(BaseModel):
    soil_score: float = 0.0
    weather_score: float = 0.0
    market_score: float = 0.0
    water_score: float = 0.0
    season_score: float = 0.0
    risk_score: float = 0.0


class ScoredCrop(BaseModel):
    crop: CropRecord
    scores: ScoreBreakdown
    final_score: float = 0.0


class RecommendationResponse(BaseModel):
    farmer_id: str
    recommendations: List[ScoredCrop]
    explanation: Optional[str] = None
