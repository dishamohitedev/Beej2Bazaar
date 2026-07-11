import httpx
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from app.irrigation.models import DailyWeather, WeatherForecastData

logger = logging.getLogger(__name__)

class WeatherService:
    @staticmethod
    def fetch_forecast(latitude: float, longitude: float) -> WeatherForecastData:
        """
        Fetches 7-day weather forecast from Open-Meteo for the given coordinates.
        Averages hourly relative humidity into daily means.
        Falls back to realistic seasonal weather data if the API request fails or times out.
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "wind_speed_10m_max",
                "et0_fao_evapotranspiration"
            ],
            "hourly": "relative_humidity_2m",
            "timezone": "auto"
        }

        try:
            # Query the API with a 4.0 second timeout
            response = httpx.get(url, params=params, timeout=4.0)
            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})
                hourly = data.get("hourly", {})
                
                dates = daily.get("time", [])
                temp_maxs = daily.get("temperature_2m_max", [])
                temp_mins = daily.get("temperature_2m_min", [])
                precips = daily.get("precipitation_sum", [])
                winds = daily.get("wind_speed_10m_max", [])
                etos = daily.get("et0_fao_evapotranspiration", [])
                
                hourly_rh = hourly.get("relative_humidity_2m", [])

                daily_forecasts = []
                for i in range(len(dates)):
                    # Calculate mean relative humidity for the day (average of 24 hours)
                    start_idx = i * 24
                    end_idx = (i + 1) * 24
                    day_rh_slice = hourly_rh[start_idx:end_idx] if len(hourly_rh) >= end_idx else []
                    mean_rh = sum(day_rh_slice) / len(day_rh_slice) if day_rh_slice else 65.0 # default fallback 65%
                    
                    # Open-Meteo wind speed is in km/h. Keep it as km/h.
                    daily_forecasts.append(DailyWeather(
                        date=dates[i],
                        temp_min=float(temp_mins[i]) if temp_mins[i] is not None else 20.0,
                        temp_max=float(temp_maxs[i]) if temp_maxs[i] is not None else 30.0,
                        precipitation=float(precips[i]) if precips[i] is not None else 0.0,
                        wind_speed=float(winds[i]) if winds[i] is not None else 10.0,
                        relative_humidity=round(mean_rh, 1),
                        eto=float(etos[i]) if (etos and etos[i] is not None) else None
                    ))
                    
                if daily_forecasts:
                    return WeatherForecastData(daily_forecasts=daily_forecasts)
            else:
                logger.warning(f"Open-Meteo API returned error {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Failed to query Open-Meteo API for irrigation: {e}. Generating fallback forecast.")

        # Fallback to realistic dry-season mock forecast if API is unreachable
        return WeatherService.generate_fallback_forecast()

    @staticmethod
    def generate_fallback_forecast() -> WeatherForecastData:
        """Generates a realistic 7-day weather forecast fallback."""
        daily_forecasts = []
        today = datetime.now()
        
        # Simple weather pattern (mix of dry days and one minor rain shower day)
        for i in range(7):
            forecast_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            # Day 3 has some light rain forecast, others are dry
            rain = 4.2 if i == 2 else 0.0
            daily_forecasts.append(DailyWeather(
                date=forecast_date,
                temp_min=22.0,
                temp_max=32.0,
                precipitation=rain,
                wind_speed=12.5,
                relative_humidity=65.0,
                eto=None # Triggers Hargreaves-Samani calculation
            ))
            
        return WeatherForecastData(daily_forecasts=daily_forecasts)
