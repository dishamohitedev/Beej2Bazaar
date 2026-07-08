from app.recommendation.models import CropRecord, RecommendationContext

class WeatherScorer:
    @staticmethod
    def score(crop: CropRecord, context: RecommendationContext) -> float:
        """
        Scores temperature and rainfall suitability between 0.0 and 100.0.
        Adjusts rainfall penalties if the farmer has active irrigation capabilities.
        """
        # --- 1. Temperature Suitability Score ---
        forecast_min = context.weather.temp_min
        forecast_max = context.weather.temp_max
        
        ideal_min = crop.ideal_temp_min
        ideal_max = crop.ideal_temp_max
        
        temp_penalty = 0.0
        # Penalty for exceeding ideal max
        if forecast_max > ideal_max:
            temp_penalty += (forecast_max - ideal_max) * 5.0
        # Penalty for falling below ideal min
        if forecast_min < ideal_min:
            temp_penalty += (ideal_min - forecast_min) * 5.0
            
        temp_score = max(0.0, 100.0 - temp_penalty)

        # --- 2. Rainfall Suitability Score ---
        forecast_rain = context.weather.rainfall_mm
        ideal_rain = crop.ideal_rainfall_mm
        
        if ideal_rain <= 0:
            rain_score = 100.0
        else:
            ratio = forecast_rain / ideal_rain
            
            if 0.8 <= ratio <= 1.2:
                rain_score = 100.0
            elif ratio < 0.8:
                # Under-watering penalty
                raw_penalty = (1.0 - ratio) * 100.0
                
                # If farmer has irrigation, they can supplement water, so reduce the penalty
                irrigation_type = context.profile.irrigation.strip().lower()
                if irrigation_type != "rainfed":
                    # Reduce penalty by 60% for drip/sprinkler, and 40% for canal/borewell
                    reduction = 0.6 if irrigation_type in ["drip", "sprinkler"] else 0.4
                    raw_penalty *= (1.0 - reduction)
                    
                rain_score = max(0.0, 100.0 - raw_penalty)
            else:
                # Over-watering/flooding penalty (ratio > 1.2)
                raw_penalty = (ratio - 1.0) * 50.0
                rain_score = max(0.0, 100.0 - raw_penalty)

        # Weather score is the average of temperature and rainfall scores
        return round((temp_score + rain_score) / 2.0, 1)
