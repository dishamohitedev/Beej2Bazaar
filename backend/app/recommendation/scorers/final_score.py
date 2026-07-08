from app.recommendation.models import ScoreBreakdown

class FinalScoreScorer:
    @staticmethod
    def calculate(breakdown: ScoreBreakdown) -> float:
        """
        Combines individual scorer outputs using default weights:
        - Soil: 30%
        - Weather: 25%
        - Market: 20%
        - Water: 15%
        - Season: 10%
        
        Formula:
        Final Score = 0.30 * Soil + 0.25 * Weather + 0.20 * Market + 0.15 * Water + 0.10 * Season
        """
        raw_score = (
            0.30 * breakdown.soil_score +
            0.25 * breakdown.weather_score +
            0.20 * breakdown.market_score +
            0.15 * breakdown.water_score +
            0.10 * breakdown.season_score
        )
        
        # Risk factor penalty:
        # If the risk_score is extremely low (meaning high risk), we can apply a small penalty.
        # E.g., if risk is below 70, deduct up to 10 points proportional to risk severity.
        if breakdown.risk_score < 70.0:
            penalty = (70.0 - breakdown.risk_score) * 0.2
            raw_score -= penalty
            
        return round(max(0.0, min(100.0, raw_score)), 1)
