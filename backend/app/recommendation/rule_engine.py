from abc import ABC, abstractmethod
from typing import List
import logging

from app.recommendation.models import CropRecord, RecommendationContext

logger = logging.getLogger(__name__)


class CropRule(ABC):
    @abstractmethod
    def evaluate(self, crop: CropRecord, context: RecommendationContext) -> bool:
        """
        Evaluates a single crop against a specific agronomic constraint.
        Returns:
            True if the crop satisfies the rule (passes/survives).
            False if it violates the rule (is filtered out/discarded).
        """
        pass


class SeasonRule(CropRule):
    def evaluate(self, crop: CropRecord, context: RecommendationContext) -> bool:
        crop_season = crop.season.strip().lower()
        curr_season = context.season.current_season.strip().lower()
        
        # Annual or Perennial crops can be grown all year round
        if crop_season in ["annual", "perennial"]:
            return True
            
        # Match exact season
        if crop_season == curr_season:
            return True
            
        # Optional: Match growth season strings if season didn't match directly
        crop_growth = crop.growth_season.strip().lower()
        if crop_growth == "all season":
            return True
        if curr_season == "kharif" and crop_growth == "monsoon":
            return True
        if curr_season == "rabi" and crop_growth == "winter":
            return True
        if curr_season == "zaid" and crop_growth == "summer":
            return True

        return False


class SoilRule(CropRule):
    def evaluate(self, crop: CropRecord, context: RecommendationContext) -> bool:
        farmer_soil = context.profile.soil_type.strip().lower()
        compatible_soils = [s.lower() for s in crop.get_compatible_soil_types()]
        
        # If the farmer's soil is listed as compatible, let it pass
        return farmer_soil in compatible_soils


class IrrigationRule(CropRule):
    def evaluate(self, crop: CropRecord, context: RecommendationContext) -> bool:
        farmer_irrigation = context.profile.irrigation.strip().lower()
        
        # Rainfed farms cannot support crops with High water requirements
        if farmer_irrigation == "rainfed" and crop.water_requirement.strip().lower() == "high":
            return False
            
        return True


class TemperatureRule(CropRule):
    def evaluate(self, crop: CropRecord, context: RecommendationContext) -> bool:
        forecast_min = context.weather.temp_min
        forecast_max = context.weather.temp_max
        
        # Binary bounds checking:
        # If the forecasted high is below the crop's required minimum,
        # or the forecasted low is above the crop's absolute maximum, the crop fails.
        if forecast_max < crop.ideal_temp_min or forecast_min > crop.ideal_temp_max:
            return False
            
        return True


class RainfallRule(CropRule):
    def evaluate(self, crop: CropRecord, context: RecommendationContext) -> bool:
        farmer_irrigation = context.profile.irrigation.strip().lower()
        forecast_rainfall = context.weather.rainfall_mm
        
        # If the farm is purely rainfed, check if rainfall is completely insufficient
        # E.g. if forecasted rainfall is less than 30% of the crop's ideal requirement, it cannot survive
        if farmer_irrigation == "rainfed":
            if forecast_rainfall < crop.ideal_rainfall_mm * 0.3:
                return False
                
        # Excessive rainfall check (all farms):
        # If expected rainfall is extremely high (e.g. > 3.0x crop's ideal requirement),
        # it will cause flood/waterlogging for delicate crops like spices, pulses, or cumin.
        # We exclude only highly sensitive crop types (pulses, spices) under excessive rain.
        if forecast_rainfall > crop.ideal_rainfall_mm * 3.0:
            if crop.crop_type.strip().lower() in ["pulse", "spice"]:
                return False
                
        return True


class RuleEngine:
    def __init__(self):
        self.rules: List[CropRule] = [
            SeasonRule(),
            SoilRule(),
            IrrigationRule(),
            TemperatureRule(),
            RainfallRule()
        ]

    def filter_candidates(self, crops: List[CropRecord], context: RecommendationContext) -> List[CropRecord]:
        """Filters out incompatible crops from the pool based on hard agronomic rules."""
        surviving_crops = []
        for crop in crops:
            is_compatible = True
            for rule in self.rules:
                if not rule.evaluate(crop, context):
                    is_compatible = False
                    logger.debug(f"Crop {crop.crop_name} filtered out by {rule.__class__.__name__}")
                    break
            if is_compatible:
                surviving_crops.append(crop)
        return surviving_crops
