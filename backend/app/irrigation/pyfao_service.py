from app.irrigation.models import DailyWeather, PyFAOOutput
from app.irrigation.calculators.eto_calculator import EToCalculator
from app.irrigation.calculators.etc_calculator import ETcCalculator

class PyFAOService:
    @staticmethod
    def calculate_crop_water_demand(
        latitude: float,
        weather: DailyWeather,
        crop_name: str,
        growth_stage: str
    ) -> PyFAOOutput:
        """
        Runs the FAO-56 Penman-Monteith crop water calculations for a given day:
          1. Computes or resolves reference evapotranspiration (ETo)
          2. Applies the crop coefficient (Kc) matching the growth stage to compute crop ET (ETc)
          3. Returns ETo, ETc, and the base crop water requirement (mm)
        """
        # 1. Resolve ETo (prefers Open-Meteo, falls back to Hargreaves-Samani)
        eto = EToCalculator.resolve_eto(
            latitude=latitude,
            date_str=weather.date,
            temp_min=weather.temp_min,
            temp_max=weather.temp_max,
            api_eto=weather.eto
        )
        
        # 2. Resolve ETc (ETc = Kc * ETo)
        etc = ETcCalculator.calculate_etc(
            eto=eto,
            crop_name=crop_name,
            growth_stage=growth_stage
        )
        
        # The daily crop water requirement is equal to ETc (expressed in mm/day)
        return PyFAOOutput(
            eto=eto,
            etc=etc,
            water_requirement_mm=etc
        )
