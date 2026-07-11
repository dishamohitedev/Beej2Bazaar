from typing import Dict

# Standard irrigation system efficiencies (eta) representing the percentage of water that actually reaches the roots.
IRRIGATION_EFFICIENCIES: Dict[str, float] = {
    "drip": 0.90,       # Drip irrigation is highly efficient, minimal evaporation/runoff
    "sprinkler": 0.75,  # Sprinkler loses some water to wind drift/evaporation
    "canal": 0.50,      # Canal/Flood loses water to percolation and runoff
    "flood": 0.50,      # Flood irrigation is similarly low efficiency
    "borewell": 0.65,   # Pump/Borewell furrow irrigation averages ~65%
    "rainfed": 0.60,    # Default fallback efficiency if supplemental water is applied
}

DEFAULT_EFFICIENCY = 0.65

class IrrigationCalculator:
    @staticmethod
    def get_system_efficiency(method_name: str) -> float:
        """
        Retrieves the water application efficiency (eta) for the given irrigation method.
        """
        method_lower = (method_name or "").lower()
        for key, eff in IRRIGATION_EFFICIENCIES.items():
            if key in method_lower:
                return eff
        return DEFAULT_EFFICIENCY

    @classmethod
    def calculate_requirements(cls, etc: float, effective_rainfall: float, method_name: str) -> float:
        """
        Calculates the Gross Irrigation Requirement (GIR) in mm.
        GIR = Net Irrigation Requirement / System Efficiency
        GIR = max(0.0, ETc - P_eff) / eta
        """
        # 1. Calculate Net Irrigation Requirement (NIR)
        nir = etc - effective_rainfall
        if nir <= 0:
            return 0.0
            
        # 2. Apply Irrigation System Efficiency (eta)
        eta = cls.get_system_efficiency(method_name)
        gir = nir / eta
        
        return round(gir, 2)
