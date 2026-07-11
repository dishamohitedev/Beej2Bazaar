import math
from datetime import datetime
from typing import Optional

class EToCalculator:
    @staticmethod
    def calculate_hargreaves_samani(latitude: float, date_str: str, temp_min: float, temp_max: float) -> float:
        """
        Calculates reference evapotranspiration (ETo) in mm/day using the Hargreaves-Samani method.
        This is the standard FAO-56 fallback when solar radiation, wind speed, and humidity are missing.
        """
        try:
            # Handle date formatting (e.g. if datetime object is passed or string)
            if isinstance(date_str, str):
                dt = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
            else:
                dt = date_str
        except ValueError:
            dt = datetime.now()
            
        julian_day = dt.timetuple().tm_yday
        
        # Latitude in radians
        lat_rad = math.radians(latitude)
        
        # Solar declination delta (radians)
        delta = 0.409 * math.sin((2 * math.pi * julian_day / 365) - 1.39)
        
        # Earth-Sun distance factor dr
        dr = 1 + 0.033 * math.cos(2 * math.pi * julian_day / 365)
        
        # Sunset hour angle omega_s (radians)
        x = -math.tan(lat_rad) * math.tan(delta)
        if x >= 1.0:
            omega_s = math.pi
        elif x <= -1.0:
            omega_s = 0.0
        else:
            omega_s = math.acos(x)
            
        # Extraterrestrial radiation Ra (MJ / m^2 / day)
        # Solar constant Gsc = 0.0820 MJ/m^2/min
        Ra = (24 * 60 / math.pi) * 0.0820 * dr * (
            omega_s * math.sin(lat_rad) * math.sin(delta) +
            math.cos(lat_rad) * math.cos(delta) * math.sin(omega_s)
        )
        
        # Mean temperature
        temp_mean = (temp_max + temp_min) / 2.0
        temp_range = max(0.0, temp_max - temp_min)
        
        # Hargreaves-Samani formula (ETo in mm/day)
        # 0.408 converts MJ/m^2/day to mm/day
        eto = 0.0023 * 0.408 * Ra * (temp_mean + 17.8) * math.sqrt(temp_range)
        
        return round(max(0.0, eto), 2)

    @classmethod
    def resolve_eto(cls, latitude: float, date_str: str, temp_min: float, temp_max: float, api_eto: Optional[float] = None) -> float:
        """
        Resolves ETo. Prefers Open-Meteo pre-computed ETo, otherwise falls back to Hargreaves-Samani.
        """
        if api_eto is not None and api_eto >= 0:
            return round(api_eto, 2)
            
        return cls.calculate_hargreaves_samani(latitude, date_str, temp_min, temp_max)
