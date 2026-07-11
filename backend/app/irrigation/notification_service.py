import re
import logging
from datetime import datetime, time
from typing import Optional, Tuple

from app.repositories.onboarding_repository import OnboardingRepository
from app.irrigation.reminder_store import ReminderStore
from app.irrigation.irrigation_service import IrrigationService
from app.irrigation.notification_store import NotificationStore
from app.irrigation.water_source_store import WaterSourceStore

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def parse_slot_times(slot_str: str) -> Tuple[time, time]:
        """
        Parses a slot string like '08:00 AM - 04:00 PM (Day Slot)' 
        and returns a Tuple of (start_time, end_time).
        """
        if not slot_str:
            return time(8, 0), time(16, 0)
        
        # Pattern: HH:MM AM/PM - HH:MM AM/PM
        match = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))", slot_str)
        if not match:
            return time(8, 0), time(16, 0)
        
        start_str, end_str = match.groups()
        try:
            start_str = re.sub(r"\s+", " ", start_str.upper().strip())
            end_str = re.sub(r"\s+", " ", end_str.upper().strip())
            
            start_time = datetime.strptime(start_str, "%I:%M %p").time()
            end_time = datetime.strptime(end_str, "%I:%M %p").time()
            return start_time, end_time
        except Exception:
            return time(8, 0), time(16, 0)

    @staticmethod
    def is_time_in_slot(current_time: time, start_time: time, end_time: time) -> bool:
        """
        Checks if current_time falls within the slot defined by start_time and end_time.
        Handles slots crossing midnight (e.g. 10:00 PM to 06:00 AM).
        """
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Spans midnight
            return current_time >= start_time or current_time <= end_time

    @classmethod
    def check_and_trigger_notifications(cls, user_id: str, simulated_time: Optional[datetime] = None) -> Optional[dict]:
        """
        Main runner: checks if the current/simulated time warrants sending a scheduled notification.
        First processes low water alerts, then processes electricity slots.
        """
        eval_time = simulated_time or datetime.now()
        date_str = eval_time.strftime("%Y-%m-%d")

        # Fetch profile for localization
        profile = {}
        try:
            profile = OnboardingRepository.get_profile(user_id) or {}
        except Exception:
            pass

        lang = (profile.get("language") or "English").strip().lower()

        # A. WATER LEVEL WARNING CHECK
        sources = WaterSourceStore.get_sources(user_id)
        for s in sources:
            level = s.get("current_level_pct", 100)
            source_id = s.get("id", "default")
            source_name = s.get("source_name", "Water Source")
            
            if level <= 20:
                type_str = f"low_water_{source_id}"
                if not NotificationStore.has_notification_been_sent(user_id, date_str, type_str):
                    # Generate localized warning
                    if "marathi" in lang:
                        title = "⚠️ सिंचन चेतावणी"
                        message = f"⚠️ चेतावणी: तुमच्या '{source_name}' मधील पाण्याची पातळी अत्यंत कमी आहे ({level}%). कृपया सिंचन काळजीपूर्वक करा!"
                    elif "hindi" in lang:
                        title = "⚠️ सिंचाई चेतावनी"
                        message = f"⚠️ चेतावनी: आपके '{source_name}' में पानी का स्तर बहुत कम है ({level}%). कृपया सिंचाई का नियोजन सावधानी से करें!"
                    else:
                        title = "⚠️ Water Level Warning"
                        message = f"⚠️ Warning: Your '{source_name}' water level is critically low ({level}%). Please plan your irrigation runs conservatively."
                    
                    return NotificationStore.add_notification(
                        user_id=user_id,
                        title=title,
                        message=message,
                        date_str=date_str,
                        type_str=type_str
                    )

        # B. REGULAR ELECTRICITY SLOT CHECK
        # 1. Fetch today's reminder log
        reminder = ReminderStore.get_reminder(user_id, date_str)
        if not reminder:
            try:
                # Query scheduling pipeline and initialize reminder
                result = IrrigationService.get_irrigation_schedule(user_id)
                initial_status = "pending" if result.today.irrigate else "skipped"
                reminder = ReminderStore.update_reminder(user_id, date_str, {
                    "status": initial_status,
                    "water_mm": result.today.water_mm,
                    "electricity_slot": result.today.electricity_slot,
                    "pump_run_time_str": result.today.pump_run_time_str,
                    "reason": result.today.reason
                })
            except Exception as e:
                logger.warning(f"Could not determine irrigation schedule for user {user_id}: {e}")
                return None

        # 2. If status is not pending, do not alert
        if reminder.get("status") != "pending" or reminder.get("error"):
            return None

        electricity_slot = reminder.get("electricity_slot")
        if not electricity_slot:
            return None

        # 3. Check if notification has already been sent for today
        if NotificationStore.has_notification_been_sent(user_id, date_str, "electricity_available"):
            return None

        # 4. Check if current time is inside the electricity slot
        start_time, end_time = cls.parse_slot_times(electricity_slot)
        if not cls.is_time_in_slot(eval_time.time(), start_time, end_time):
            return None

        water_mm = reminder.get("water_mm", 0.0)
        pump_run_time_str = reminder.get("pump_run_time_str") or "0 mins"

        # 5. Generate localized message
        if "marathi" in lang:
            title = "💧 सिंचन संदेश"
            message = (
                f"⚡ वीज उपलब्ध आहे! आज सिंचन करण्याचे नियोजित आहे.\n"
                f"पाण्याची मात्रा: {water_mm:.1f} मि.मी.\n"
                f"पंप सुरू ठेवण्याची वेळ: {pump_run_time_str}\n"
                f"वीज उपलब्धता वेळ: {electricity_slot}"
            )
        elif "hindi" in lang:
            title = "💧 सिंचाई संदेश"
            message = (
                f"⚡ बिजली उपलब्ध है! आज सिंचाई निर्धारित है।\n"
                f"पानी की मात्रा: {water_mm:.1f} मिमी\n"
                f"पंप चलाने का समय: {pump_run_time_str}\n"
                f"बिजली उपलब्धता स्लॉट: {electricity_slot}"
            )
        else:
            title = "💧 Irrigation Alert"
            message = (
                f"⚡ Electricity is now available for your scheduled irrigation!\n"
                f"Water required: {water_mm:.1f} mm\n"
                f"Estimated Pump Runtime: {pump_run_time_str}\n"
                f"Electricity Slot: {electricity_slot}"
            )

        # 6. Add notification to store
        notif = NotificationStore.add_notification(
            user_id=user_id,
            title=title,
            message=message,
            date_str=date_str,
            type_str="electricity_available"
        )
        return notif
