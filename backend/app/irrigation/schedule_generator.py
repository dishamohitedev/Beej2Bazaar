from typing import List, Optional
from app.irrigation.models import DailyScheduleItem, IrrigationScheduleResponse

class ScheduleGenerator:
    @staticmethod
    def generate_response(schedule: List[DailyScheduleItem]) -> IrrigationScheduleResponse:
        """
        Compiles the 7-day daily irrigation schedule into the final response format:
          1. Sets the "today" status using the first item in the schedule (day 0)
          2. Finds the first day starting from today (or subsequent days) where irrigation is needed
          3. Assembles the final IrrigationScheduleResponse model.
        """
        if not schedule:
            raise ValueError("Schedule items list cannot be empty.")
            
        # 1. Set today's action item (first day in forecast)
        today_item = schedule[0]
        
        # 2. Find the next scheduled irrigation date
        next_irrigation_date = None
        for item in schedule:
            if item.irrigate:
                next_irrigation_date = item.date
                break
                
        return IrrigationScheduleResponse(
            today=today_item,
            next_irrigation=next_irrigation_date,
            schedule=schedule
        )
