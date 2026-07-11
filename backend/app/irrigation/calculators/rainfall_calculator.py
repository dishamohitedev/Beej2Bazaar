class RainfallCalculator:
    @staticmethod
    def calculate_effective_rainfall(total_rainfall_mm: float) -> float:
        """
        Calculates effective daily rainfall (P_eff) in mm.
        Not all rainfall reaches the crop root zone due to:
          - Canopy interception (very light rains evaporate off leaves)
          - Surface runoff (heavy rains saturate the soil surface and run off)
          - Deep percolation (water that drains past the root zone)

        Standard agricultural engineering formula:
          - If total rain <= 2.0 mm: P_eff = 0.0 mm (interception loss)
          - If 2.0 mm < total rain <= 75.0 mm: P_eff = 0.8 * (total_rain - 2.0)
          - If total rain > 75.0 mm: P_eff = 0.7 * (total_rain - 2.0) (increased runoff)
        """
        if total_rainfall_mm <= 2.0:
            peff = 0.0
        elif total_rainfall_mm <= 75.0:
            peff = 0.8 * (total_rainfall_mm - 2.0)
        else:
            peff = 0.7 * (total_rainfall_mm - 2.0)
            
        return round(max(0.0, peff), 2)
