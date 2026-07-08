from app.recommendation.models import CropRecord, RecommendationContext

class SoilScorer:
    @staticmethod
    def score(crop: CropRecord, context: RecommendationContext) -> float:
        """
        Scores soil suitability between 0.0 and 100.0.
        All candidates passing the rule engine are compatible, but some soils are optimal.
        """
        farmer_soil = context.profile.soil_type.strip().lower()
        compatible_soils = [s.strip().lower() for s in crop.get_compatible_soil_types()]
        
        if not compatible_soils:
            return 80.0  # Safe default if no soil compatibility is defined

        # If it is the first (primary) compatible soil, it's highly optimal
        if farmer_soil == compatible_soils[0]:
            return 100.0
            
        # If it is in the list, assign score based on position
        if farmer_soil in compatible_soils:
            idx = compatible_soils.index(farmer_soil)
            # Declines slightly: index 1 gets 85, index 2 gets 70, etc.
            return max(50.0, 100.0 - (idx * 15.0))
            
        return 0.0  # Fallback if not compatible
