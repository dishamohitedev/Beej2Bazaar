from app.recommendation.models import CropRecord, RecommendationContext

class RiskScorer:
    @staticmethod
    def score(crop: CropRecord, context: RecommendationContext) -> float:
        """
        Scores crop safety and low-risk profile between 0.0 and 100.0.
        A score of 100.0 means extremely low risk. Low scores mean high vulnerability.
        Checks:
        1. Temperature boundary proximity (frost/heat stress risk)
        2. Rainfed water stress risk
        3. Pest susceptibility based on crop category
        """
        base_score = 90.0
        
        # 1. Pest and disease susceptibility defaults by crop type
        crop_type = crop.crop_type.strip().lower()
        if crop_type in ["vegetable", "fruit"]:
            base_score = 80.0  # high pest/perishable risk
        elif crop_type == "fiber":  # e.g., cotton
            base_score = 75.0  # highly susceptible to bollworm
        elif crop_type in ["cereal", "millet"]:
            base_score = 95.0  # sturdy crops
            
        # 2. Temperature extreme proximity risk
        forecast_min = context.weather.temp_min
        forecast_max = context.weather.temp_max
        
        # Heat stress risk: forecast high is within 3°C of crop's ideal max
        if (crop.ideal_temp_max - forecast_max) <= 3.0:
            base_score -= 15.0
            
        # Cold stress/frost risk: forecast low is within 3°C of crop's ideal min
        if (forecast_min - crop.ideal_temp_min) <= 3.0:
            base_score -= 15.0
            
        # 3. Rainfed moisture stress risk
        irrigation = context.profile.irrigation.strip().lower()
        water_req = crop.water_requirement.strip().lower()
        if irrigation == "rainfed" and water_req == "medium":
            base_score -= 20.0  # high risk of crop failure if monsoon fails
            
        return round(max(10.0, min(100.0, base_score)), 1)
