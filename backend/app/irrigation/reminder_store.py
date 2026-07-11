import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.database.supabase import admin_supabase

STORE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "irrigation_reminders.json"))

class ReminderStore:
    use_db = True

    @staticmethod
    def _read_store() -> Dict[str, Dict[str, dict]]:
        if not os.path.exists(STORE_FILE):
            return {}
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _write_store(data: Dict[str, Dict[str, dict]]):
        try:
            with open(STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ReminderStore] Failed to write to {STORE_FILE}: {e}")

    @classmethod
    def get_reminder(cls, user_id: str, date_str: str) -> Optional[dict]:
        if cls.use_db:
            try:
                res = admin_supabase.table("irrigation_reminders").select("*").eq("user_id", user_id).eq("date", date_str).execute()
                if res.data:
                    return res.data[0]
                return None
            except Exception as e:
                print(f"[ReminderStore] DB Error in get_reminder: {e}")
                # Fallback if DB is not configured or query fails during local run
                
        store = cls._read_store()
        user_data = store.get(user_id, {})
        return user_data.get(date_str)

    @classmethod
    def update_reminder(cls, user_id: str, date_str: str, updates: dict) -> dict:
        if cls.use_db:
            try:
                existing = cls.get_reminder(user_id, date_str)
                if existing:
                    # Construct update dictionary
                    db_updates = {
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    db_updates.update(updates)
                    # Exclude fields not in reminders schema if they exist
                    db_updates.pop("id", None)
                    db_updates.pop("user_id", None)
                    db_updates.pop("date", None)
                    
                    res = admin_supabase.table("irrigation_reminders").update(db_updates).eq("user_id", user_id).eq("date", date_str).execute()
                    if res.data:
                        return res.data[0]
                else:
                    # Insert new reminder log
                    record = {
                        "user_id": user_id,
                        "date": date_str,
                        "status": "pending",
                        "water_mm": 0.0,
                        "started_at": None,
                        "completed_at": None,
                        "electricity_slot": None,
                        "pump_run_time_str": None,
                        "reason": None,
                        "error": False,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    record.update(updates)
                    res = admin_supabase.table("irrigation_reminders").insert(record).execute()
                    if res.data:
                        return res.data[0]
            except Exception as e:
                print(f"[ReminderStore] DB Error in update_reminder: {e}")

        # JSON fallback
        store = cls._read_store()
        if user_id not in store:
            store[user_id] = {}
        
        current = store[user_id].get(date_str, {
            "date": date_str,
            "status": "pending",  # pending, watering, completed, skipped
            "water_mm": 0.0,
            "started_at": None,
            "completed_at": None,
            "electricity_slot": None,
            "pump_run_time_str": None,
            "reason": None,
            "error": False,
            "updated_at": None
        })
        
        current.update(updates)
        current["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        store[user_id][date_str] = current
        cls._write_store(store)
        return current

    @classmethod
    def get_history(cls, user_id: str) -> List[dict]:
        if cls.use_db:
            try:
                res = admin_supabase.table("irrigation_reminders").select("*").eq("user_id", user_id).eq("status", "completed").order("date", desc=True).execute()
                return res.data or []
            except Exception as e:
                print(f"[ReminderStore] DB Error in get_history: {e}")

        # JSON fallback
        store = cls._read_store()
        user_data = store.get(user_id, {})
        # Return all items sorted by date descending, filtering for completed status
        completed_runs = [run for run in user_data.values() if run.get("status") == "completed"]
        return sorted(completed_runs, key=lambda x: x.get("date", ""), reverse=True)

    @classmethod
    def get_all_reminders(cls, user_id: str) -> List[dict]:
        if cls.use_db:
            try:
                res = admin_supabase.table("irrigation_reminders").select("*").eq("user_id", user_id).order("date", desc=True).execute()
                return res.data or []
            except Exception as e:
                print(f"[ReminderStore] DB Error in get_all_reminders: {e}")

        # JSON fallback
        store = cls._read_store()
        user_data = store.get(user_id, {})
        return sorted(user_data.values(), key=lambda x: x.get("date", ""), reverse=True)
