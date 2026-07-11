from app.irrigation.models import DailyWeather, PyFAOOutput, DailyScheduleItem
from app.irrigation.calculators.rainfall_calculator import RainfallCalculator
from app.irrigation.calculators.irrigation_calculator import IrrigationCalculator
from app.irrigation.calculators.electricity_optimizer import ElectricityOptimizer

class IrrigationEngine:
    @staticmethod
    def evaluate_daily_need(
        weather: DailyWeather,
        pyfao_output: PyFAOOutput,
        irrigation_method: str,
        state: str,
        farm_size: float
    ) -> DailyScheduleItem:
        """
        Determines the irrigation schedule for a single day:
          1. Computes effective rainfall from total forecast precipitation
          2. Compares crop water demand (ETc) with effective rainfall
          3. If rainfall is insufficient, calculates required gross irrigation depth in mm
          4. Resolves the active agricultural electricity slot and estimated pump run time
          5. Returns a DailyScheduleItem with the decision, gross amount, reason, slot, and runtime.
        """
        # 1. Calculate effective rainfall
        peff = RainfallCalculator.calculate_effective_rainfall(weather.precipitation)
        
        # 2. Get crop water requirement (ETc)
        etc = pyfao_output.etc
        
        # 3. Calculate gross irrigation requirement using system efficiency
        eta = IrrigationCalculator.get_system_efficiency(irrigation_method)
        gir = IrrigationCalculator.calculate_requirements(etc, peff, irrigation_method)
        
        # 4. Resolve electricity slot (state-based rotating schedule lookup)
        electricity_slot = ElectricityOptimizer.get_electricity_slot(state, weather.date)
        
        # 5. Calculate pump run time (assuming typical 5 HP motor)
        pump_details = ElectricityOptimizer.calculate_pump_runtime(
            farm_size=farm_size,
            water_mm=gir,
            pump_hp=5.0
        )
        pump_run_time_str = pump_details["runtime_str"]
        
        # 6. Generate decision and reason
        if etc <= 0.0:
            irrigate = False
            water_mm = 0.0
            reason = "Crop water demand is zero for this day."
        elif gir > 0.0:
            irrigate = True
            water_mm = gir
            # Explanatory scientific reasoning including electricity details
            reason = (
                f"Crop water demand (ETc: {etc:.1f} mm) exceeds effective rainfall (P_eff: {peff:.1f} mm). "
                f"Gross irrigation of {gir:.1f} mm required using {irrigation_method} (eta: {int(eta * 100)}%). "
                f"Recommend running 5 HP pump for {pump_run_time_str} during power slot {electricity_slot}."
            )
        else:
            irrigate = False
            water_mm = 0.0
            if weather.precipitation > 0.0:
                reason = (
                    f"Forecast rainfall ({weather.precipitation:.1f} mm) provides effective moisture ({peff:.1f} mm) "
                    f"sufficient to satisfy crop water demand (ETc: {etc:.1f} mm)."
                )
            else:
                reason = "Soil moisture remains sufficient or crop demand is fully covered without rainfall."

        return DailyScheduleItem(
            date=weather.date,
            irrigate=irrigate,
            water_mm=water_mm,
            reason=reason,
            electricity_slot=electricity_slot if irrigate else None,
            pump_run_time_str=pump_run_time_str if irrigate else None
        )
