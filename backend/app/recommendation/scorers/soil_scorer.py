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

        # 1. Direct Match Check
        if farmer_soil == compatible_soils[0]:
            return 100.0
            
        if farmer_soil in compatible_soils:
            idx = compatible_soils.index(farmer_soil)
            return max(50.0, 100.0 - (idx * 15.0))

        # 2. Token Matching
        farmer_tokens = []
        if "black" in farmer_soil:
            farmer_tokens.append("black")
        if "clay" in farmer_soil:
            farmer_tokens.append("clayey")
        if "red" in farmer_soil:
            farmer_tokens.append("red")
        if "sandy" in farmer_soil:
            farmer_tokens.append("sandy")
        if "laterite" in farmer_soil:
            farmer_tokens.append("laterite")
        if "alluvial" in farmer_soil:
            farmer_tokens.append("alluvial")
        if "loam" in farmer_soil:
            farmer_tokens.append("loamy")

        # Check if any mapped token matches compatible soils
        best_idx = None
        for token in farmer_tokens:
            if token in compatible_soils:
                idx = compatible_soils.index(token)
                if best_idx is None or idx < best_idx:
                    best_idx = idx

        if best_idx is not None:
            if best_idx == 0:
                return 100.0
            return max(50.0, 100.0 - (best_idx * 15.0))

        # 3. Substring match fallback
        for idx, comp in enumerate(compatible_soils):
            if comp in farmer_soil or farmer_soil in comp:
                if idx == 0:
                    return 90.0
                return max(50.0, 90.0 - (idx * 15.0))
            
        return 0.0  # Fallback if not compatible
