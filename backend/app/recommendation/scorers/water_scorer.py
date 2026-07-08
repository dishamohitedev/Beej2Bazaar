from app.recommendation.models import CropRecord, RecommendationContext

class WaterScorer:
    @staticmethod
    def score(crop: CropRecord, context: RecommendationContext) -> float:
        """
        Scores water requirement and irrigation method alignment between 0.0 and 100.0.
        Evaluates how well the crop's water need matches the farmer's water delivery method.
        """
        irrigation = context.profile.irrigation.strip().lower()
        req = crop.water_requirement.strip().lower()
        
        # Scoring grid matching irrigation method with water requirement level
        if irrigation == "drip":
            if req == "low":
                return 100.0
            elif req == "medium":
                return 95.0
            else:  # high
                return 65.0  # sub-optimal for drip micro-irrigation
                
        elif irrigation == "sprinkler":
            if req == "low":
                return 95.0
            elif req == "medium":
                return 100.0
            else:  # high
                return 75.0
                
        elif irrigation in ["canal", "borewell", "tubewell"]:
            if req == "low":
                return 70.0  # inefficient use of heavy flood irrigation
            elif req == "medium":
                return 90.0
            else:  # high
                return 100.0  # flood methods match water-heavy crops
                
        elif irrigation == "rainfed":
            if req == "low":
                return 90.0  # very good fit for dryland
            elif req == "medium":
                return 50.0  # risky
            else:  # high
                return 0.0  # completely unsuitable (usually filtered by rules)
                
        return 75.0  # Default safe score for other/unknown types
