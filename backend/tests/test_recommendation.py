import pytest
from unittest.mock import patch, MagicMock

from app.recommendation.models import (
    CropRecord,
    FarmerProfile,
    WeatherForecast,
    MarketPrice,
    SeasonInfo,
    RecommendationContext,
    ScoreBreakdown,
    ScoredCrop
)
from app.recommendation.rule_engine import (
    SeasonRule,
    SoilRule,
    IrrigationRule,
    TemperatureRule,
    RainfallRule,
    RuleEngine
)
from app.recommendation.scorers.soil_scorer import SoilScorer
from app.recommendation.scorers.weather_scorer import WeatherScorer
from app.recommendation.scorers.water_scorer import WaterScorer
from app.recommendation.scorers.season_scorer import SeasonScorer
from app.recommendation.scorers.market_scorer import MarketScorer
from app.recommendation.scorers.risk_scorer import RiskScorer
from app.recommendation.scorers.final_score import FinalScoreScorer
from app.recommendation.ranking_engine import RankingEngine
from app.recommendation.recommendation_service import RecommendationService
from app.recommendation.gemini_service import GeminiService


# --- Dummy Data Helpers ---
def create_dummy_crop(
    crop_name="Rice - Naveen",
    season="Kharif",
    water_req="High",
    temp_min=21,
    temp_max=35,
    rainfall=1200,
    crop_type="Cereal",
    growth_season="Monsoon"
) -> CropRecord:
    return CropRecord(
        id="dummy-uuid",
        crop_name=crop_name,
        scientific_name="Oryza sativa",
        season=season,
        growth_season=growth_season,
        duration_days=140,
        water_requirement=water_req,
        soil_types=None,  # null in DB, triggers Python mapping
        ideal_temp_min=temp_min,
        ideal_temp_max=temp_max,
        ideal_rainfall_mm=rainfall,
        description="A water intensive crop",
        crop_type=crop_type
    )


def create_dummy_context(
    soil_type="Black",
    irrigation="Drip",
    temp_min=25.0,
    temp_max=32.0,
    rainfall=1000.0,
    season_name="Kharif",
    month=7,
    language="English"
) -> RecommendationContext:
    profile = FarmerProfile(
        id="farmer-123",
        full_name="Rajesh Kumar",
        state="Punjab",
        district="Amritsar",
        taluka="Ajnala",
        village="Kaler",
        soil_type=soil_type,
        irrigation=irrigation,
        language=language,
        farm_size=2.5,
        farm_unit="acre"
    )
    weather = WeatherForecast(
        temp_min=temp_min,
        temp_max=temp_max,
        rainfall_mm=rainfall,
        description="Scattered Clouds"
    )
    market = [
        MarketPrice(
            crop_name="Rice",
            commodity="Rice",
            state="Punjab",
            district="Amritsar",
            market="Amritsar Mandi",
            min_price=2100.0,
            max_price=2400.0,
            modal_price=2250.0
        )
    ]
    season = SeasonInfo(
        current_month=month,
        current_season=season_name
    )
    return RecommendationContext(
        profile=profile,
        weather=weather,
        market=market,
        season=season
    )


# --- Rule Engine Tests ---
def test_season_rule():
    rule = SeasonRule()
    
    # Correct season: Kharif crop in Kharif season -> True
    crop = create_dummy_crop(season="Kharif", growth_season="Monsoon")
    context = create_dummy_context(season_name="Kharif")
    assert rule.evaluate(crop, context) is True
    
    # Mismatch season: Rabi crop in Kharif season -> False
    crop_rabi = create_dummy_crop(season="Rabi", growth_season="Winter")
    assert rule.evaluate(crop_rabi, context) is False
    
    # Annual crop in Kharif season -> True
    crop_annual = create_dummy_crop(season="Annual", growth_season="All Season")
    assert rule.evaluate(crop_annual, context) is True


def test_soil_rule():
    rule = SoilRule()
    
    # Rice maps to ['Alluvial', 'Clayey', 'Loamy', 'Red']. Black soil is not in it -> False
    crop = create_dummy_crop(crop_name="Rice - Naveen")
    context_black = create_dummy_context(soil_type="Black")
    assert rule.evaluate(crop, context_black) is False

    # Rice grown on Alluvial soil -> True
    context_alluvial = create_dummy_context(soil_type="Alluvial")
    assert rule.evaluate(crop, context_alluvial) is True


def test_irrigation_rule():
    rule = IrrigationRule()
    
    # Rainfed farm + High water requirement crop -> False
    crop_high = create_dummy_crop(water_req="High")
    context_rainfed = create_dummy_context(irrigation="Rainfed")
    assert rule.evaluate(crop_high, context_rainfed) is False

    # Drip irrigation + High water requirement crop -> True
    context_drip = create_dummy_context(irrigation="Drip")
    assert rule.evaluate(crop_high, context_drip) is True


def test_temperature_rule():
    rule = TemperatureRule()
    
    # Crop ideal temp is 21 - 35. Forecast max is 40 -> True (it doesn't exceed completely)
    # Forecast min is 22, max is 32. Fully inside -> True
    crop = create_dummy_crop(temp_min=20, temp_max=35)
    context = create_dummy_context(temp_min=22, temp_max=30)
    assert rule.evaluate(crop, context) is True

    # Forecast max is 18 (below crop's min limit 20) -> False
    context_cold = create_dummy_context(temp_min=10, temp_max=18)
    assert rule.evaluate(crop, context_cold) is False


def test_rainfall_rule():
    rule = RainfallRule()
    
    # Rainfed farm + low rain (100mm) for a high-rain crop (1200mm) -> False (under-watered)
    crop = create_dummy_crop(rainfall=1200)
    context_dry = create_dummy_context(irrigation="Rainfed", rainfall=100.0)
    assert rule.evaluate(crop, context_dry) is False

    # Pulse crop + excessive rainfall (4000mm vs 600mm ideal) -> False (over-watered/flooded)
    crop_pulse = create_dummy_crop(rainfall=600, crop_type="Pulse")
    context_flood = create_dummy_context(rainfall=3000.0)
    assert rule.evaluate(crop_pulse, context_flood) is False


# --- Scorers Tests ---
def test_soil_scorer():
    crop = create_dummy_crop(crop_name="Rice - Naveen")
    # Rice soil mapping: ["Alluvial", "Clayey", "Loamy", "Red"]
    
    # Primary soil match (index 0) gets 100
    context_1 = create_dummy_context(soil_type="Alluvial")
    assert SoilScorer.score(crop, context_1) == 100.0

    # Index 1 match gets 85
    context_2 = create_dummy_context(soil_type="Clayey")
    assert SoilScorer.score(crop, context_2) == 85.0


def test_weather_scorer():
    crop = create_dummy_crop(temp_min=20, temp_max=30, rainfall=1000)
    
    # Perfect weather: min=22, max=28, rain=1000 (ratio=1.0) -> 100
    context = create_dummy_context(temp_min=22.0, temp_max=28.0, rainfall=1000.0, irrigation="Drip")
    assert WeatherScorer.score(crop, context) == 100.0

    # Temp deviation: forecast max 32 (exceeds ideal by 2 degrees). Penalty = 2 * 5 = 10. Temp score = 90.
    # Rain ratio = 0.5 (underwatered, 500/1000). Penalty = 50. But with drip, penalty reduced by 60% (becomes 20). Rain score = 80.
    # Average weather score = (90 + 80) / 2 = 85.0
    context_dev = create_dummy_context(temp_min=22.0, temp_max=32.0, rainfall=500.0, irrigation="Drip")
    assert WeatherScorer.score(crop, context_dev) == 85.0


def test_water_scorer():
    crop_medium = create_dummy_crop(water_req="Medium")
    
    # Drip + Medium water crop -> 95
    context_drip = create_dummy_context(irrigation="Drip")
    assert WaterScorer.score(crop_medium, context_drip) == 95.0

    # Canal + Medium water crop -> 90
    context_canal = create_dummy_context(irrigation="Canal")
    assert WaterScorer.score(crop_medium, context_canal) == 90.0


def test_season_scorer():
    crop_kharif = create_dummy_crop(season="Kharif")
    
    # Kharif crop, month 7 (July) -> 100.0
    context_july = create_dummy_context(month=7)
    assert SeasonScorer.score(crop_kharif, context_july) == 100.0

    # Kharif crop, month 9 (September) -> 60.0 (late sowing)
    context_sept = create_dummy_context(month=9)
    assert SeasonScorer.score(crop_kharif, context_sept) == 60.0


def test_market_scorer():
    crop = create_dummy_crop(crop_name="Rice - Naveen")
    
    # Matching mandi price modal = 2250, baseline Rice = 2200. Ratio = 2250/2200 = 1.0227
    # Score = 75 + (1.0227 - 1) * 100 = 77.3
    context = create_dummy_context()
    assert MarketScorer.score(crop, context) == 77.3


def test_risk_scorer():
    crop_cereal = create_dummy_crop(crop_type="Cereal")
    # Set forecast max temp to 28 so it is not within 3 degrees of crop's ideal_temp_max (35)
    context = create_dummy_context(temp_max=28.0)
    
    # Cereal sturdy crop -> base 95 (no temperature proximity stress)
    assert RiskScorer.score(crop_cereal, context) == 95.0

    # High pest crop (vegetable) -> base 80
    crop_veg = create_dummy_crop(crop_type="Vegetable")
    assert RiskScorer.score(crop_veg, context) == 80.0


def test_final_score_scorer():
    # Test formula: 0.3 * Soil + 0.25 * Weather + 0.2 * Market + 0.15 * Water + 0.1 * Season
    breakdown = ScoreBreakdown(
        soil_score=100.0,
        weather_score=80.0,
        market_score=90.0,
        water_score=90.0,
        season_score=100.0,
        risk_score=90.0
    )
    expected = (0.3 * 100) + (0.25 * 80) + (0.2 * 90) + (0.15 * 90) + (0.10 * 100)
    # 30 + 20 + 18 + 13.5 + 10 = 91.5 (No risk penalty as risk_score >= 70)
    assert FinalScoreScorer.calculate(breakdown) == 91.5


# --- Ranking Engine Tests ---
def test_ranking_engine():
    crop1 = create_dummy_crop(crop_name="Crop A")
    crop2 = create_dummy_crop(crop_name="Crop B")
    crop3 = create_dummy_crop(crop_name="Crop C")
    crop4 = create_dummy_crop(crop_name="Crop D")
    crop5 = create_dummy_crop(crop_name="Crop E")
    crop6 = create_dummy_crop(crop_name="Crop F")

    scored = [
        ScoredCrop(crop=crop1, scores=ScoreBreakdown(), final_score=90.0),
        ScoredCrop(crop=crop2, scores=ScoreBreakdown(), final_score=35.0),  # below min threshold 40
        ScoredCrop(crop=crop3, scores=ScoreBreakdown(), final_score=85.0),
        ScoredCrop(crop=crop4, scores=ScoreBreakdown(), final_score=95.0),
        ScoredCrop(crop=crop5, scores=ScoreBreakdown(), final_score=85.0),  # tie-breaker with crop3
        ScoredCrop(crop=crop6, scores=ScoreBreakdown(), final_score=60.0)
    ]

    top_5 = RankingEngine.rank_crops(scored)
    
    # Should only return 5 crops, sorting descending by score, tie-break by name
    assert len(top_5) == 5
    assert top_5[0].crop.crop_name == "Crop D"  # Score 95
    assert top_5[1].crop.crop_name == "Crop A"  # Score 90
    assert top_5[2].crop.crop_name == "Crop C"  # Score 85 (Crop B is excluded!)
    assert top_5[3].crop.crop_name == "Crop E"  # Score 85 (tie-broken by name alphabet C < E)
    assert top_5[4].crop.crop_name == "Crop F"  # Score 60


# --- Pipeline Orchestration Tests ---
@patch("app.recommendation.recommendation_service.DataCollector")
def test_pipeline_integration(mock_collector):
    # Set up mocks for collector
    crop_list = [
        create_dummy_crop(crop_name="Rice - Naveen", season="Kharif", crop_type="Cereal", growth_season="Monsoon"),
        create_dummy_crop(crop_name="Wheat - HD2967", season="Rabi", crop_type="Cereal", growth_season="Winter")
    ]
    context = create_dummy_context(soil_type="Alluvial", season_name="Kharif")
    
    mock_collector.collect_context.return_value = context
    mock_collector.fetch_all_crops.return_value = crop_list

    service = RecommendationService()
    response = service.generate_recommendations("farmer-123")
    
    assert response.farmer_id == "farmer-123"
    # Rice is Kharif, Wheat is Rabi. Kharif context -> only Rice survives.
    assert len(response.recommendations) == 1
    assert response.recommendations[0].crop.crop_name == "Rice - Naveen"
    assert response.recommendations[0].final_score > 0
    # Explanation should be generated (fallback in this mock case)
    assert response.explanation is not None
    assert "Rice - Naveen" in response.explanation


# --- Gemini Service Unit Tests ---
def test_gemini_service_local_fallback():
    service = GeminiService()
    crop = create_dummy_crop(crop_name="Rice - Naveen")
    scored = [ScoredCrop(crop=crop, scores=ScoreBreakdown(), final_score=85.0)]
    
    # 1. English Fallback
    context_en = create_dummy_context(language="English")
    explanation_en = service._generate_local_fallback(scored, context_en)
    assert "Hello Rajesh Kumar" in explanation_en
    assert "Rice - Naveen" in explanation_en
    assert "weeding" in explanation_en.lower()
    
    # 2. Hindi Fallback
    context_hi = create_dummy_context(language="Hindi")
    explanation_hi = service._generate_local_fallback(scored, context_hi)
    assert "नमस्ते Rajesh Kumar" in explanation_hi
    assert "Rice - Naveen" in explanation_hi

    # 3. Marathi Fallback
    context_mr = create_dummy_context(language="Marathi")
    explanation_mr = service._generate_local_fallback(scored, context_mr)
    assert "नमस्कार Rajesh Kumar" in explanation_mr
    assert "Rice - Naveen" in explanation_mr


@patch("httpx.post")
def test_gemini_service_api_call_success(mock_post):
    # Mock a successful HTTP response from the Gemini API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Gemini: Rice is a great match for your Alluvial soil!"
                        }
                    ]
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    # Force a mock API key in settings
    with patch("app.recommendation.gemini_service.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "fake-key"
        
        service = GeminiService()
        crop = create_dummy_crop(crop_name="Rice - Naveen")
        scored = [ScoredCrop(crop=crop, scores=ScoreBreakdown(), final_score=85.0)]
        context = create_dummy_context(soil_type="Alluvial")
        
        explanation = service.generate_explanations(scored, context)
        
        # Verify that mock API was called and response returned
        assert mock_post.called
        assert explanation == "Gemini: Rice is a great match for your Alluvial soil!"


@patch("httpx.post")
def test_gemini_service_api_call_failure_fallback(mock_post):
    # Mock a failed HTTP response (e.g. 500 error)
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    # Force a mock API key in settings
    with patch("app.recommendation.gemini_service.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "fake-key"
        
        service = GeminiService()
        crop = create_dummy_crop(crop_name="Rice - Naveen")
        scored = [ScoredCrop(crop=crop, scores=ScoreBreakdown(), final_score=85.0)]
        context = create_dummy_context(soil_type="Alluvial", language="English")
        
        explanation = service.generate_explanations(scored, context)
        
        # Verify that mock API was called, failed, and fell back to local generation
        assert mock_post.called
        assert "Hello Rajesh Kumar" in explanation
        assert "Rice - Naveen" in explanation

