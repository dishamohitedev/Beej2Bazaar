import httpx
import logging
from typing import List, Tuple, Optional
from datetime import datetime

from app.core.config import settings
from app.database.supabase import admin_supabase
from app.repositories.onboarding_repository import OnboardingRepository
from app.recommendation.models import (
    CropRecord,
    FarmerProfile,
    WeatherForecast,
    MarketPrice,
    SeasonInfo,
    RecommendationContext
)

logger = logging.getLogger(__name__)

# Coordinates lookup for major agricultural districts/states in India
DISTRICT_COORDINATES = {
    # Punjab
    ("punjab", "amritsar"): (31.63, 74.87),
    ("punjab", "ludhiana"): (30.90, 75.85),
    ("punjab", "patiala"): (30.34, 76.38),
    ("punjab", "jalandhar"): (31.32, 75.57),
    # Maharashtra
    ("maharashtra", "pune"): (18.52, 73.85),
    ("maharashtra", "nashik"): (19.99, 73.78),
    ("maharashtra", "nagpur"): (21.14, 79.08),
    ("maharashtra", "aurangabad"): (19.87, 75.34),
    # Andhra Pradesh / Telangana
    ("andhra pradesh", "anantapur"): (14.68, 77.60),
    ("andhra pradesh", "guntur"): (16.30, 80.45),
    ("telangana", "hyderabad"): (17.38, 78.48),
    # Karnataka
    ("karnataka", "bengaluru"): (12.97, 77.59),
    ("karnataka", "belagavi"): (15.84, 74.49),
    # Uttar Pradesh
    ("uttar pradesh", "lucknow"): (26.85, 80.94),
    ("uttar pradesh", "kanpur"): (26.44, 80.33),
    ("uttar pradesh", "varanasi"): (25.31, 82.97),
    # Madhya Pradesh
    ("madhya pradesh", "indore"): (22.71, 75.85),
    ("madhya pradesh", "bhopal"): (23.25, 77.41),
    # Gujarat
    ("gujarat", "ahmedabad"): (23.02, 72.57),
    ("gujarat", "surat"): (21.17, 72.83),
    # Rajasthan
    ("rajasthan", "jaipur"): (26.91, 75.78),
    ("rajasthan", "jodhpur"): (26.23, 73.02),
    # Tamil Nadu
    ("tamil nadu", "coimbatore"): (11.01, 76.95),
    ("tamil nadu", "chennai"): (13.08, 80.27),
    # West Bengal
    ("west bengal", "hooghly"): (22.90, 88.39),
    ("west bengal", "bardhaman"): (23.23, 87.86),
    # Bihar
    ("bihar", "patna"): (25.59, 85.13),
    # Haryana
    ("haryana", "karnal"): (29.68, 76.99)
}


class DataCollector:

    @staticmethod
    def get_coordinates(state: str, district: str) -> Tuple[float, float]:
        """Looks up coordinates for the given state and district, falling back to default Central India."""
        state_key = state.strip().lower()
        dist_key = district.strip().lower()
        
        # Check direct match
        coords = DISTRICT_COORDINATES.get((state_key, dist_key))
        if coords:
            return coords
            
        # Check if we can match by state centroid
        state_centroids = {
            "punjab": (31.14, 75.34),
            "maharashtra": (19.75, 75.71),
            "andhra pradesh": (15.91, 79.74),
            "telangana": (18.11, 79.01),
            "karnataka": (15.31, 75.71),
            "uttar pradesh": (26.84, 80.88),
            "madhya pradesh": (22.97, 78.65),
            "gujarat": (22.25, 71.19),
            "rajasthan": (27.02, 74.21),
            "tamil nadu": (11.12, 78.65),
            "west bengal": (22.98, 87.85),
            "bihar": (25.09, 85.31),
            "haryana": (29.05, 76.08),
        }
        coords = state_centroids.get(state_key)
        if coords:
            return coords
            
        # Default to Central India coordinates (Nagpur)
        return 21.14, 79.08

    @staticmethod
    def determine_season(month: int) -> str:
        """Determines the current cropping season in India based on the calendar month."""
        if 6 <= month <= 10:
            return "Kharif"
        elif 11 <= month <= 12 or 1 <= month <= 2:
            return "Rabi"
        else:
            return "Zaid"

    @classmethod
    def fetch_weather(cls, latitude: float, longitude: float, season: str) -> WeatherForecast:
        """
        Fetches the 7-day weather forecast from Open-Meteo API.
        Falls back to scientific seasonal defaults if the API call fails or times out.
        """
        # Seasonal climate defaults in India
        seasonal_defaults = {
            "Kharif": WeatherForecast(temp_min=22.0, temp_max=34.0, rainfall_mm=1100.0, description="Monsoon Climate (Heavier Rain)"),
            "Rabi": WeatherForecast(temp_min=10.0, temp_max=27.0, rainfall_mm=120.0, description="Winter Climate (Dry/Mild)"),
            "Zaid": WeatherForecast(temp_min=24.0, temp_max=40.0, rainfall_mm=60.0, description="Summer Climate (Hot/Dry)")
        }
        default_forecast = seasonal_defaults.get(season, seasonal_defaults["Kharif"])

        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        try:
            # Short timeout to ensure responsiveness
            response = httpx.get(url, timeout=4.0)
            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})
                
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                precips = daily.get("precipitation_sum", [])
                
                if max_temps and min_temps:
                    avg_max_temp = sum(max_temps) / len(max_temps)
                    avg_min_temp = sum(min_temps) / len(min_temps)
                    weekly_rain_sum = sum(precips) if precips else 0.0
                    
                    # Extrapolate weekly precipitation to seasonal scaling factors
                    # Scale weekly rain to typical crop cycle length (~100-150 days, approx 16 weeks)
                    estimated_seasonal_rainfall = weekly_rain_sum * 16.0
                    
                    # Ensure estimated rainfall is within realistic bounds (not 0 if it's monsoon)
                    if estimated_seasonal_rainfall == 0.0 and season == "Kharif":
                        estimated_seasonal_rainfall = default_forecast.rainfall_mm
                    elif estimated_seasonal_rainfall == 0.0:
                        estimated_seasonal_rainfall = 50.0  # basic dryland average

                    return WeatherForecast(
                        temp_min=round(avg_min_temp, 1),
                        temp_max=round(avg_max_temp, 1),
                        rainfall_mm=round(estimated_seasonal_rainfall, 1),
                        description="Real-time Open-Meteo Forecast"
                    )
        except Exception as e:
            logger.warning(f"Failed to fetch weather from Open-Meteo: {e}. Using seasonal defaults.")
            
        return default_forecast

    @classmethod
    def fetch_market_prices(cls, state: str, district: str) -> List[MarketPrice]:
        """
        Fetches commodity prices from data.gov.in Mandi API (Agmarknet).
        Falls back to generating realistic mock mandi prices if API key is missing or call fails.
        Uses a local JSON file to cache results for up to 12 hours to prevent slow queries and rate limits.
        """
        import json
        import os
        import time

        api_key = settings.DATA_GOV_IN_API_KEY
        if not api_key:
            logger.info("DATA_GOV_IN_API_KEY not found in configuration. Generating mock mandi data.")
            return cls.generate_mock_market_prices(state, district)

        cache_file = os.path.join(os.path.dirname(__file__), "mandi_cache.json")
        cache_key = f"{state.strip().lower()}_{district.strip().lower()}"

        # 1. Try loading from cache first if it's less than 12 hours old
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                if cache_key in cache_data:
                    entry = cache_data[cache_key]
                    # 12 hours = 43200 seconds
                    if time.time() - entry.get("timestamp", 0) < 43200:
                        logger.info(f"Loaded cached mandi prices for {state}, {district}")
                        prices = []
                        for rec in entry.get("records", []):
                            prices.append(MarketPrice(
                                crop_name=rec.get("crop_name", "Unknown"),
                                commodity=rec.get("commodity", "Unknown"),
                                state=rec.get("state", state),
                                district=rec.get("district", district),
                                market=rec.get("market", "Local Mandi"),
                                min_price=float(rec.get("min_price", 0)),
                                max_price=float(rec.get("max_price", 0)),
                                modal_price=float(rec.get("modal_price", 0))
                            ))
                        if prices:
                            return prices
            except Exception as cache_err:
                logger.warning(f"Failed to read mandi cache: {cache_err}")

        # Standard Agmarknet commodity prices resource ID on data.gov.in
        resource_id = "9ef8428a-d404-411a-bbaf-ac2c67da124d"
        url = f"https://api.data.gov.in/resource/{resource_id}"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": 50,
            "filters[state]": state.strip(),
            "filters[district]": district.strip()
        }

        # 2. Query the remote API with a fast 3-second timeout
        try:
            response = httpx.get(url, params=params, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                market_prices = []
                for rec in records:
                    try:
                        # Extract and parse prices
                        min_p = float(rec.get("min_price", 0))
                        max_p = float(rec.get("max_price", 0))
                        modal_p = float(rec.get("modal_price", 0))
                        
                        market_prices.append(MarketPrice(
                            crop_name=rec.get("commodity", "Unknown"),
                            commodity=rec.get("commodity", "Unknown"),
                            state=rec.get("state", state),
                            district=rec.get("district", district),
                            market=rec.get("market", "Local Mandi"),
                            min_price=min_p,
                            max_price=max_p,
                            modal_price=modal_p
                        ))
                    except (ValueError, TypeError):
                        continue
                
                # If we successfully retrieved prices, save them to the cache
                if market_prices:
                    try:
                        cache_data = {}
                        if os.path.exists(cache_file):
                            with open(cache_file, "r", encoding="utf-8") as f:
                                cache_data = json.load(f)
                        
                        serialized_records = [
                            {
                                "crop_name": p.crop_name,
                                "commodity": p.commodity,
                                "state": p.state,
                                "district": p.district,
                                "market": p.market,
                                "min_price": p.min_price,
                                "max_price": p.max_price,
                                "modal_price": p.modal_price
                            }
                            for p in market_prices
                        ]
                        cache_data[cache_key] = {
                            "timestamp": time.time(),
                            "records": serialized_records
                        }
                        with open(cache_file, "w", encoding="utf-8") as f:
                            json.dump(cache_data, f, indent=4)
                        logger.info(f"Cached fetched mandi prices for {state}, {district}")
                    except Exception as cache_write_err:
                        logger.warning(f"Failed to write mandi cache: {cache_write_err}")
                        
                    return market_prices
        except Exception as e:
            logger.warning(f"Failed to query data.gov.in Agmarknet API: {e}.")

        # 3. Fallback to stale cache if available (even if older than 12 hours)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                if cache_key in cache_data:
                    logger.info(f"Using stale cached mandi prices for {state}, {district} after API failure")
                    entry = cache_data[cache_key]
                    prices = []
                    for rec in entry.get("records", []):
                        prices.append(MarketPrice(
                            crop_name=rec.get("crop_name", "Unknown"),
                            commodity=rec.get("commodity", "Unknown"),
                            state=rec.get("state", state),
                            district=rec.get("district", district),
                            market=rec.get("market", "Local Mandi"),
                            min_price=float(rec.get("min_price", 0)),
                            max_price=float(rec.get("max_price", 0)),
                            modal_price=float(rec.get("modal_price", 0))
                        ))
                    if prices:
                        return prices
            except Exception:
                pass

        # 4. Final fallback to generated mock prices
        logger.info(f"Generating mock mandi data for {state}, {district}.")
        return cls.generate_mock_market_prices(state, district)

    @staticmethod
    def generate_mock_market_prices(state: str, district: str) -> List[MarketPrice]:
        """Generates mock mandi prices (per quintal in INR) for main commodity categories."""
        commodities = [
            ("Rice", 2183.0, 2350.0, 2250.0),
            ("Wheat", 2125.0, 2275.0, 2200.0),
            ("Cotton", 6500.0, 7500.0, 7000.0),
            ("Sugarcane", 315.0, 350.0, 330.0),  # FRP is per quintal
            ("Maize", 1962.0, 2150.0, 2050.0),
            ("Chickpea", 5335.0, 5800.0, 5500.0),
            ("Soybean", 4300.0, 4800.0, 4600.0),
            ("Groundnut", 6375.0, 7200.0, 6800.0),
            ("Tomato", 1200.0, 2000.0, 1500.0),
            ("Onion", 1500.0, 2800.0, 2200.0),
            ("Chilli", 18000.0, 24000.0, 21000.0),
            ("Potato", 800.0, 1500.0, 1200.0)
        ]
        
        return [
            MarketPrice(
                crop_name=comm,
                commodity=comm,
                state=state,
                district=district,
                market="Main Mandi",
                min_price=min_p,
                max_price=max_p,
                modal_price=modal_p
            )
            for comm, min_p, max_p, modal_p in commodities
        ]

    @classmethod
    def geocode_location(cls, state: str, district: str, taluka: str, village: str) -> Optional[Tuple[float, float]]:
        """
        Geocodes a village/taluka location using OpenStreetMap Nominatim API.
        Falls back to None if not found or API times out.
        """
        query = f"{village}, {taluka}, {district}, {state}, India"
        url = "https://nominatim.openstreetmap.org/search"
        headers = {
            "User-Agent": "Beej2Bazaar-ADE-Engine/1.0 (contact: support@beej2bazaar.com)"
        }
        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }
        try:
            response = httpx.get(url, headers=headers, params=params, timeout=4.0)
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    logger.info(f"Geocoded successfully: '{query}' -> ({lat}, {lon})")
                    return lat, lon
                else:
                    logger.warning(f"Nominatim returned no results for query: '{query}'")
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed for '{query}': {e}")
        return None

    @classmethod
    def collect_context(cls, user_id: str) -> RecommendationContext:
        """Retrieves and compiles all input variables into a unified context."""
        # 1. Fetch profile/onboarding details from Supabase
        profile_data = OnboardingRepository.get_profile(user_id)
        if not profile_data:
            raise ValueError(f"Farmer profile not found for user ID: {user_id}")

        profile = FarmerProfile(
            id=user_id,
            full_name=profile_data.get("full_name") or "Farmer",
            state=profile_data.get("state") or "Punjab",
            district=profile_data.get("district") or "Amritsar",
            taluka=profile_data.get("taluka") or "Ajnala",
            village=profile_data.get("village") or "Kaler",
            soil_type=profile_data.get("soil_type") or "Loamy",
            irrigation=profile_data.get("irrigation") or "Rainfed",
            language=profile_data.get("language") or "English",
            farm_size=float(profile_data.get("farm_size") if profile_data.get("farm_size") is not None else 1.0),
            farm_unit=profile_data.get("farm_unit") or "acre",
            latitude=profile_data.get("latitude") if profile_data.get("latitude") is not None else None,
            longitude=profile_data.get("longitude") if profile_data.get("longitude") is not None else None
        )

        # 2. Get coords (priority: stored coords -> dynamic geocode -> local fallback)
        lat = profile.latitude
        lon = profile.longitude

        if lat is None or lon is None:
            # Try dynamic geocoding
            coords = cls.geocode_location(profile.state, profile.district, profile.taluka, profile.village)
            if coords:
                lat, lon = coords
                # Attempt to save to database if possible so future requests are fast
                try:
                    OnboardingRepository.update_profile(user_id, {"latitude": lat, "longitude": lon})
                    logger.info(f"Saved geocoded coordinates to profile for user {user_id}")
                except Exception as db_err:
                    logger.warning(f"Could not save coordinates to database (schema might need update): {db_err}")
            else:
                lat, lon = cls.get_coordinates(profile.state, profile.district)

        # Update profile instance with whatever coords we ended up using/resolving
        profile.latitude = lat
        profile.longitude = lon

        # 3. Determine current season
        current_month = datetime.now().month
        current_season_str = cls.determine_season(current_month)
        season = SeasonInfo(current_month=current_month, current_season=current_season_str)

        # 4. Fetch weather
        weather = cls.fetch_weather(lat, lon, current_season_str)

        # 5. Fetch market mandi prices
        market = cls.fetch_market_prices(profile.state, profile.district)

        return RecommendationContext(
            profile=profile,
            weather=weather,
            market=market,
            season=season
        )

    @staticmethod
    def fetch_all_crops() -> List[CropRecord]:
        """Queries the `crops` table from Supabase database and returns parsed CropRecords."""
        response = admin_supabase.table("crops").select("*").execute()
        crops_list = []
        for item in response.data:
            crops_list.append(CropRecord(
                id=item.get("id"),
                crop_name=item.get("crop_name"),
                scientific_name=item.get("scientific_name"),
                season=item.get("season"),
                growth_season=item.get("growth_season", ""),
                duration_days=item.get("duration_days", 120),
                water_requirement=item.get("water_requirement", "Medium"),
                soil_types=item.get("soil_types"),  # Will be None
                ideal_temp_min=item.get("ideal_temp_min", 15),
                ideal_temp_max=item.get("ideal_temp_max", 35),
                ideal_rainfall_mm=item.get("ideal_rainfall_mm", 600),
                description=item.get("description"),
                crop_type=item.get("crop_type", "Cereal")
            ))
        return crops_list
