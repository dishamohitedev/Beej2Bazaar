from datetime import datetime
from typing import Dict, Any

class ElectricityOptimizer:
    @staticmethod
    def get_electricity_slot(state: str, date_str: str) -> str:
        """
        Determines the available agricultural electricity slot for the state on a given date.
        Uses a standard rotating day/night slot logic (rotating weekly) for states like Maharashtra and Gujarat,
        and continuous day slots for states like Punjab.
        """
        state_lower = (state or "").lower().strip()
        
        try:
            # Parse the date
            if isinstance(date_str, str):
                dt = datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
            else:
                dt = date_str
            week_num = dt.isocalendar().week
        except Exception:
            week_num = 1
            
        # 1. Maharashtra: Weekly rotating day/night blocks
        if "maharashtra" in state_lower or state_lower == "mh":
            if week_num % 2 == 0:
                return "08:00 AM - 04:00 PM (Day Slot)"
            else:
                return "10:00 PM - 06:00 AM (Night Slot)"
                
        # 2. Punjab: Standard 8-hour day slots (paddy/agricultural guarantee)
        elif "punjab" in state_lower or state_lower == "pb":
            return "09:00 AM - 05:00 PM (Day Slot)"
            
        # 3. Gujarat: Weekly rotating 3-phase agricultural slots
        elif "gujarat" in state_lower or state_lower == "gj":
            if week_num % 2 == 0:
                return "08:00 AM - 04:00 PM (Day Slot)"
            else:
                return "10:00 PM - 06:00 AM (Night Slot)"
                
        # Default fallback slot
        return "08:00 AM - 04:00 PM (Day Slot)"

    @staticmethod
    def calculate_pump_runtime(farm_size: float, water_mm: float, pump_hp: float = 5.0) -> Dict[str, Any]:
        """
        Calculates the required agricultural water pump run time to deliver the gross water depth.
        Formula:
          - 1 acre-mm of water = 4,046.86 Liters
          - Total Water Volume (Liters) = Farm Size (acres) * Water Depth (mm) * 4046.86
          - Pump Flow Rate (Liters/hour) = Pump HP * 3,000 (typical 5 HP pump ~ 15,000 Liters/hour discharge)
          - Run Time (hours) = Total Water Volume / Pump Flow Rate
        """
        if water_mm <= 0.0 or farm_size <= 0.0:
            return {
                "volume_liters": 0.0,
                "flow_rate_lph": 0.0,
                "runtime_hours": 0.0,
                "runtime_str": "0 mins"
            }

        # 1. Calculate total water volume required in Liters
        total_liters = farm_size * water_mm * 4046.86
        
        # 2. Estimate pump flow rate based on HP (assumes 3000 Liters/hour per HP at standard head)
        flow_rate_lph = pump_hp * 3000.0
        
        # 3. Calculate run time in hours
        runtime_hours = total_liters / flow_rate_lph
        
        # 4. Format run time string (e.g. "1 hr 15 mins")
        hours_int = int(runtime_hours)
        minutes_int = int(round((runtime_hours - hours_int) * 60))
        
        # Carry over minutes to hours if rounded to 60
        if minutes_int >= 60:
            hours_int += 1
            minutes_int -= 60
            
        if hours_int > 0:
            runtime_str = f"{hours_int} hr {minutes_int} mins" if minutes_int > 0 else f"{hours_int} hr"
        else:
            runtime_str = f"{minutes_int} mins"
            
        return {
            "volume_liters": round(total_liters, 1),
            "flow_rate_lph": round(flow_rate_lph, 1),
            "runtime_hours": round(runtime_hours, 2),
            "runtime_str": runtime_str
        }
