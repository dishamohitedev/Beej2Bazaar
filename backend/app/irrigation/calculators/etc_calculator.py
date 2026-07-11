from typing import Dict, Any

# FAO-56 standard crop coefficients (Kc) for main stages: Initial, Development, Mid, and Late.
# Sources: FAO Irrigation and Drainage Paper No. 56.
CROP_FAO_COEFFICIENTS: Dict[str, Dict[str, float]] = {
    "rice": {
        "initial": 1.05,
        "development": 1.15,
        "mid": 1.20,
        "late": 0.90,
        "max_root_depth_m": 0.6
    },
    "wheat": {
        "initial": 0.40,
        "development": 0.75,
        "mid": 1.15,
        "late": 0.40,
        "max_root_depth_m": 1.2
    },
    "cotton": {
        "initial": 0.35,
        "development": 0.75,
        "mid": 1.20,
        "late": 0.60,
        "max_root_depth_m": 1.5
    },
    "sorghum": {
        "initial": 0.30,
        "development": 0.75,
        "mid": 1.05,
        "late": 0.55,
        "max_root_depth_m": 1.0
    },
    "sugarcane": {
        "initial": 0.40,
        "development": 0.90,
        "mid": 1.25,
        "late": 0.75,
        "max_root_depth_m": 1.2
    },
    "maize": {
        "initial": 0.30,
        "development": 0.75,
        "mid": 1.20,
        "late": 0.50,
        "max_root_depth_m": 1.0
    },
    "tomato": {
        "initial": 0.60,
        "development": 0.85,
        "mid": 1.15,
        "late": 0.80,
        "max_root_depth_m": 0.8
    },
    "onion": {
        "initial": 0.70,
        "development": 0.90,
        "mid": 1.05,
        "late": 0.75,
        "max_root_depth_m": 0.4
    },
    "potato": {
        "initial": 0.50,
        "development": 0.80,
        "mid": 1.15,
        "late": 0.75,
        "max_root_depth_m": 0.6
    },
    "soybean": {
        "initial": 0.40,
        "development": 0.80,
        "mid": 1.15,
        "late": 0.50,
        "max_root_depth_m": 0.9
    },
    "groundnut": {
        "initial": 0.40,
        "development": 0.80,
        "mid": 1.15,
        "late": 0.60,
        "max_root_depth_m": 0.8
    }
}

DEFAULT_COEFFICIENTS = {
    "initial": 0.40,
    "development": 0.80,
    "mid": 1.10,
    "late": 0.60,
    "max_root_depth_m": 0.8
}

class ETcCalculator:
    @staticmethod
    def get_crop_params(crop_name: str) -> Dict[str, float]:
        """
        Looks up crop-specific FAO-56 parameters using substring matching.
        """
        crop_lower = crop_name.lower()
        for key, params in CROP_FAO_COEFFICIENTS.items():
            if key in crop_lower:
                return params
        return DEFAULT_COEFFICIENTS

    @classmethod
    def get_crop_coefficient(cls, crop_name: str, growth_stage: str) -> float:
        """
        Determines the crop coefficient (Kc) based on the crop name and growth stage.
        Maps common growth stage terms to FAO-56 standard stages.
        """
        params = cls.get_crop_params(crop_name)
        stage_lower = (growth_stage or "mid").lower()

        # Map growth stage terms to standard FAO-56 stages
        if any(term in stage_lower for term in ["initial", "sowing", "germination", "seedling"]):
            stage_key = "initial"
        elif any(term in stage_lower for term in ["development", "vegetative", "growth"]):
            stage_key = "development"
        elif any(term in stage_lower for term in ["mid", "flowering", "reproductive", "heading"]):
            stage_key = "mid"
        elif any(term in stage_lower for term in ["late", "harvest", "maturity", "senescence"]):
            stage_key = "late"
        else:
            # Default to mid-season as a safe peak crop demand baseline
            stage_key = "mid"

        return params.get(stage_key, DEFAULT_COEFFICIENTS[stage_key])

    @classmethod
    def calculate_etc(cls, eto: float, crop_name: str, growth_stage: str) -> float:
        """
        Calculates crop evapotranspiration (ETc) in mm/day:
        ETc = Kc * ETo
        """
        kc = cls.get_crop_coefficient(crop_name, growth_stage)
        etc = kc * eto
        return round(max(0.0, etc), 2)
