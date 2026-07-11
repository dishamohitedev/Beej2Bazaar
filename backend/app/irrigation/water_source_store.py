import os
import json
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from app.database.supabase import admin_supabase

STORE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "farm_water_sources.json"))

class WaterSourceStore:
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
            print(f"[WaterSourceStore] Failed to write to {STORE_FILE}: {e}")

    @classmethod
    def get_sources(cls, user_id: str) -> List[dict]:
        if cls.use_db:
            try:
                res = admin_supabase.table("farm_water_sources").select("*").eq("user_id", user_id).execute()
                return res.data or []
            except Exception as e:
                print(f"[WaterSourceStore] DB Error in get_sources: {e}")
                # Fallback if DB fails
        
        # JSON fallback
        store = cls._read_store()
        return [s for s in store if s.get("user_id") == user_id]

    @classmethod
    def upsert_source(cls, user_id: str, source_data: dict) -> dict:
        if cls.use_db:
            try:
                # Prepare data
                db_data = {
                    "user_id": user_id,
                    "source_name": source_data.get("source_name", "Water Source"),
                    "source_type": source_data.get("source_type", "Borewell"),
                    "current_level_pct": int(source_data.get("current_level_pct", 100)),
                    "max_capacity_liters": source_data.get("max_capacity_liters"),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                source_id = source_data.get("id")
                if source_id:
                    res = admin_supabase.table("farm_water_sources").update(db_data).eq("user_id", user_id).eq("id", source_id).execute()
                else:
                    res = admin_supabase.table("farm_water_sources").insert(db_data).execute()
                
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[WaterSourceStore] DB Error in upsert_source: {e}")

        # JSON fallback
        store = cls._read_store()
        source_id = source_data.get("id")
        
        if source_id:
            # Find and update
            updated = None
            for s in store:
                if s.get("id") == source_id and s.get("user_id") == user_id:
                    s.update({
                        "source_name": source_data.get("source_name", s["source_name"]),
                        "source_type": source_data.get("source_type", s["source_type"]),
                        "current_level_pct": int(source_data.get("current_level_pct", s["current_level_pct"])),
                        "max_capacity_liters": source_data.get("max_capacity_liters", s.get("max_capacity_liters")),
                        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                    })
                    updated = s
                    break
            if updated:
                cls._write_store(store)
                return updated
        
        # Create new
        new_source = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "source_name": source_data.get("source_name", "Water Source"),
            "source_type": source_data.get("source_type", "Borewell"),
            "current_level_pct": int(source_data.get("current_level_pct", 100)),
            "max_capacity_liters": source_data.get("max_capacity_liters"),
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        store.append(new_source)
        cls._write_store(store)
        return new_source

    @classmethod
    def update_level(cls, user_id: str, source_id: str, level_pct: int) -> Optional[dict]:
        if level_pct < 0 or level_pct > 100:
            raise ValueError("Level percentage must be between 0 and 100.")
            
        if cls.use_db:
            try:
                res = admin_supabase.table("farm_water_sources").update({
                    "current_level_pct": level_pct,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("user_id", user_id).eq("id", source_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[WaterSourceStore] DB Error in update_level: {e}")

        # JSON fallback
        store = cls._read_store()
        for s in store:
            if s.get("id") == source_id and s.get("user_id") == user_id:
                s["current_level_pct"] = level_pct
                s["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                cls._write_store(store)
                return s
        return None
