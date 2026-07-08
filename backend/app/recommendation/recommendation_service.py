import logging
from typing import List

from app.recommendation.models import (
    RecommendationContext,
    ScoreBreakdown,
    ScoredCrop,
    RecommendationResponse
)
from app.recommendation.data_collector import DataCollector
from app.recommendation.rule_engine import RuleEngine
from app.recommendation.scorers.soil_scorer import SoilScorer
from app.recommendation.scorers.weather_scorer import WeatherScorer
from app.recommendation.scorers.water_scorer import WaterScorer
from app.recommendation.scorers.season_scorer import SeasonScorer
from app.recommendation.scorers.market_scorer import MarketScorer
from app.recommendation.scorers.risk_scorer import RiskScorer
from app.recommendation.scorers.final_score import FinalScoreScorer
from app.recommendation.ranking_engine import RankingEngine
from app.recommendation.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.ranking_engine = RankingEngine()
        self.gemini_service = GeminiService()

    def generate_recommendations(self, user_id: str) -> RecommendationResponse:
        """
        Runs the full deterministic Agronomic Decision Engine (ADE) pipeline.
        1. Collects context from user profile, weather, and mandi APIs.
        2. Retrieves the crop dataset from Supabase.
        3. Evaluates candidates against hard agronomic constraints.
        4. Calculates suitability scores across soil, weather, water, season, market, and risk.
        5. Ranks crops by weighted scores and selects the Top 5 candidates.
        """
        logger.info(f"Initiating crop recommendation pipeline for farmer ID: {user_id}")

        # 1. Collect Context Data
        context: RecommendationContext = DataCollector.collect_context(user_id)
        logger.info(
            f"Collected Context for {user_id}: "
            f"Soil={context.profile.soil_type}, "
            f"Irrigation={context.profile.irrigation}, "
            f"Forecasted Temp={context.weather.temp_min}-{context.weather.temp_max}°C, "
            f"Forecasted Rain={context.weather.rainfall_mm}mm, "
            f"Active Season={context.season.current_season}"
        )

        # 2. Retrieve Crops Pool
        all_crops = DataCollector.fetch_all_crops()
        logger.info(f"Loaded {len(all_crops)} candidate crop records from Supabase.")

        # 3. Rule Engine Filtering
        surviving_crops = self.rule_engine.filter_candidates(all_crops, context)
        logger.info(f"Rule Engine: {len(surviving_crops)} / {len(all_crops)} crops survived hard constraints.")

        # 4. Scoring Engine
        scored_candidates: List[ScoredCrop] = []
        for crop in surviving_crops:
            # Calculate individual sub-scores
            soil_s = SoilScorer.score(crop, context)
            weather_s = WeatherScorer.score(crop, context)
            water_s = WaterScorer.score(crop, context)
            season_s = SeasonScorer.score(crop, context)
            market_s = MarketScorer.score(crop, context)
            risk_s = RiskScorer.score(crop, context)

            breakdown = ScoreBreakdown(
                soil_score=soil_s,
                weather_score=weather_s,
                water_score=water_s,
                season_score=season_s,
                market_score=market_s,
                risk_score=risk_s
            )

            # Aggregate into the final weighted score
            final_s = FinalScoreScorer.calculate(breakdown)

            scored_candidates.append(ScoredCrop(
                crop=crop,
                scores=breakdown,
                final_score=final_s
            ))

        # 5. Ranking & Selection
        top_recommendations = self.ranking_engine.rank_crops(scored_candidates)
        logger.info(f"Ranking Engine: Selected {len(top_recommendations)} top crops.")

        # Log recommendations summary
        for idx, rec in enumerate(top_recommendations):
            logger.info(f"  [{idx+1}] {rec.crop.crop_name} (Final Score: {rec.final_score})")

        # 6. Generate Natural Language Explanation
        explanation = None
        if top_recommendations:
            explanation = self.gemini_service.generate_explanations(top_recommendations, context)

        return RecommendationResponse(
            farmer_id=user_id,
            recommendations=top_recommendations,
            explanation=explanation
        )
