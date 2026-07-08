from app.recommendation.models import CropRecord, RecommendationContext

# Baseline market prices (INR per quintal) for comparison
COMMODITY_BASELINES = {
    "Rice": 2200.0,
    "Wheat": 2150.0,
    "Cotton": 6800.0,
    "Sugarcane": 330.0,
    "Maize": 2000.0,
    "Chickpea": 5400.0,
    "Soybean": 4500.0,
    "Groundnut": 6500.0,
    "Tomato": 1500.0,
    "Onion": 2000.0,
    "Chilli": 19000.0,
    "Potato": 1200.0
}


class MarketScorer:
    @staticmethod
    def score(crop: CropRecord, context: RecommendationContext) -> float:
        """
        Scores market price profitability between 0.0 and 100.0.
        Finds matching mandi records from context and evaluates price performance against baselines.
        """
        crop_root = crop.crop_name.split("-")[0].strip()
        
        # Find matching mandi record from the collected market context
        mandi_record = None
        for record in context.market:
            # Match if crop root name is inside the commodity name (e.g. "Rice" in "Rice - Basmati")
            if crop_root.lower() in record.commodity.lower() or record.commodity.lower() in crop_root.lower():
                mandi_record = record
                break
                
        # If no real-time price is found, assign a standard average score
        if not mandi_record or mandi_record.modal_price <= 0:
            return 75.0

        modal_price = mandi_record.modal_price
        baseline = COMMODITY_BASELINES.get(crop_root, 2000.0)

        # Performance ratio: how much higher/lower is the current price compared to baseline
        price_ratio = modal_price / baseline

        # Baseline gets a score of 75.0
        # If price is 20% higher than baseline, score is 75 + 20 = 95.0
        # Capped between 30.0 and 100.0
        calculated_score = 75.0 + (price_ratio - 1.0) * 100.0
        
        return round(max(30.0, min(100.0, calculated_score)), 1)
