import logging
from app.repositories.onboarding_repository import OnboardingRepository
from app.database.supabase import admin_supabase
from app.irrigation.models import IrrigationProfile, IrrigationScheduleResponse
from app.irrigation.weather_service import WeatherService
from app.irrigation.pyfao_service import PyFAOService
from app.irrigation.irrigation_engine import IrrigationEngine
from app.irrigation.schedule_generator import ScheduleGenerator
from app.recommendation.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class IrrigationService:
    @staticmethod
    def get_irrigation_schedule(user_id: str) -> IrrigationScheduleResponse:
        """
        Orchestrates the entire Intelligent Irrigation Scheduling pipeline:
          1. Fetches farmer profile and resolves coordinates
          2. Resolves current crop and growth stage details
          3. Obtains 7-day daily weather forecasts
          4. Computes daily crop water demand (ETc) using PyFAO
          5. Determines daily water additions and schedules deterministically (no AI)
          6. Generates final schedule structured payload
          7. Passes results to Gemini to append a supportive, natural-language explanation.
        """
        # 1. Fetch farmer profile details from Supabase
        profile_data = OnboardingRepository.get_profile(user_id)
        if not profile_data:
            raise ValueError(f"Farmer profile not found for user ID: {user_id}")

        # Resolve coordinates (with dynamic geocoding fallback)
        lat = profile_data.get("latitude")
        lon = profile_data.get("longitude")
        if lat is None or lon is None:
            from app.recommendation.data_collector import DataCollector
            coords = DataCollector.geocode_location(
                profile_data.get("state", ""),
                profile_data.get("district", ""),
                profile_data.get("taluka", ""),
                profile_data.get("village", "")
            )
            if coords:
                lat, lon = coords
            else:
                # Default to Pune, Maharashtra coordinates if geocoding fails
                lat, lon = 18.5204, 73.8567

        # Parse profile model
        profile = IrrigationProfile(
            id=user_id,
            full_name=profile_data.get("full_name") or "Farmer",
            state=profile_data.get("state") or "Maharashtra",
            district=profile_data.get("district") or "Pune",
            taluka=profile_data.get("taluka") or "Haveli",
            village=profile_data.get("village") or "Manjari",
            soil_type=profile_data.get("soil_type") or "Black",
            irrigation=profile_data.get("irrigation") or "Drip",
            language=profile_data.get("language") or "Marathi",
            farm_size=float(profile_data.get("farm_size") if profile_data.get("farm_size") is not None else 1.0),
            farm_unit=profile_data.get("farm_unit") or "acre",
            latitude=lat,
            longitude=lon
        )

        # 2. Retrieve current crop name
        crop_name = "Sorghum"
        crop_id = profile_data.get("current_crop_id")
        if crop_id:
            try:
                crop_res = admin_supabase.table("crops").select("crop_name").eq("id", crop_id).single().execute()
                if crop_res.data:
                    crop_name = crop_res.data.get("crop_name", "Sorghum")
            except Exception:
                logger.warning(f"Could not retrieve crop name for crop ID {crop_id}. Defaulting to Sorghum.")

        growth_stage = profile_data.get("growth_stage") or "Vegetative"

        # 3. Fetch weather forecast from Open-Meteo
        weather_forecast = WeatherService.fetch_forecast(profile.latitude, profile.longitude)

        # 4. Generate daily irrigation schedule items using PyFAO and IrrigationEngine
        daily_schedule_items = []
        for weather_day in weather_forecast.daily_forecasts:
            # Calculate evapotranspiration metrics using PyFAO service
            pyfao_out = PyFAOService.calculate_crop_water_demand(
                latitude=profile.latitude,
                weather=weather_day,
                crop_name=crop_name,
                growth_stage=growth_stage
            )
            
            # Make the daily rules-based decision
            schedule_item = IrrigationEngine.evaluate_daily_need(
                weather=weather_day,
                pyfao_output=pyfao_out,
                irrigation_method=profile.irrigation,
                state=profile.state,
                farm_size=profile.farm_size
            )
            daily_schedule_items.append(schedule_item)

        # 5. Compile the final structured response (today status, next date, and schedule list)
        schedule_response = ScheduleGenerator.generate_response(daily_schedule_items)

        # 6. Request natural-language explanation from Gemini in target language
        try:
            gemini = GeminiService()
            explanation = gemini.generate_irrigation_explanations(
                schedule=schedule_response,
                profile=profile,
                crop_name=crop_name,
                growth_stage=growth_stage
            )
            schedule_response.explanation = explanation
        except Exception as e:
            logger.warning(f"Failed to generate Gemini explanation for irrigation: {e}")
            schedule_response.explanation = "Gemini explanation is currently unavailable."

        return schedule_response
