import os
import json
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from app.database.supabase import admin_supabase

STORE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "notifications.json"))

class NotificationStore:
    use_db = True

    @staticmethod
    def _read_store() -> List[dict]:
        if not os.path.exists(STORE_FILE):
            return []
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _write_store(data: List[dict]):
        try:
            with open(STORE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[NotificationStore] Failed to write to {STORE_FILE}: {e}")

    @classmethod
    def add_notification(
        cls, user_id: str, title: str, message: str, date_str: str, type_str: str
    ) -> dict:
        if cls.use_db:
            try:
                notif = {
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "type": type_str,
                    "status": "unread",
                    "date": date_str,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                res = admin_supabase.table("irrigation_notifications").insert(notif).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[NotificationStore] DB Error in add_notification: {e}")

        # JSON fallback
        store = cls._read_store()
        
        notif = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": type_str,
            "status": "unread",
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "date": date_str
        }
        
        store.append(notif)
        cls._write_store(store)
        return notif

    @classmethod
    def get_notifications(cls, user_id: str) -> List[dict]:
        if cls.use_db:
            try:
                res = admin_supabase.table("irrigation_notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                return res.data or []
            except Exception as e:
                print(f"[NotificationStore] DB Error in get_notifications: {e}")

        # JSON fallback
        store = cls._read_store()
        user_notifs = [n for n in store if n.get("user_id") == user_id]
        return sorted(user_notifs, key=lambda x: x.get("created_at", ""), reverse=True)

    @classmethod
    def mark_as_read(cls, user_id: str, notification_id: str) -> Optional[dict]:
        if cls.use_db:
            try:
                res = admin_supabase.table("irrigation_notifications").update({"status": "read"}).eq("user_id", user_id).eq("id", notification_id).execute()
                if res.data:
                    return res.data[0]
                return None
            except Exception as e:
                print(f"[NotificationStore] DB Error in mark_as_read: {e}")

        # JSON fallback
        store = cls._read_store()
        updated_notif = None
        for n in store:
            if n.get("id") == notification_id and n.get("user_id") == user_id:
                n["status"] = "read"
                updated_notif = n
                break
        
        if updated_notif:
            cls._write_store(store)
        return updated_notif

    @classmethod
    def has_notification_been_sent(cls, user_id: str, date_str: str, type_str: str) -> bool:
        if cls.use_db:
            try:
                res = admin_supabase.table("irrigation_notifications").select("id").eq("user_id", user_id).eq("date", date_str).eq("type", type_str).execute()
                return len(res.data or []) > 0
            except Exception as e:
                print(f"[NotificationStore] DB Error in has_notification_been_sent: {e}")

        # JSON fallback
        store = cls._read_store()
        for n in store:
            if (
                n.get("user_id") == user_id
                and n.get("date") == date_str
                and n.get("type") == type_str
            ):
                return True
        return False
