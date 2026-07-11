import os
import sys
from datetime import datetime, timedelta, time

# Ensure backend root is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.supabase import admin_supabase
from app.irrigation.reminder_store import ReminderStore
from app.irrigation.notification_store import NotificationStore, STORE_FILE
from app.irrigation.notification_service import NotificationService
from app.irrigation.water_source_store import WaterSourceStore, STORE_FILE as WATER_STORE_FILE

def clean_test_stores(user_id: str, date_str: str):
    # Remove notification store file if it exists to start fresh
    if os.path.exists(STORE_FILE):
        try:
            os.remove(STORE_FILE)
            print(f"[Prep] Cleared notification history ({STORE_FILE})")
        except Exception as e:
            print(f"[Prep] Failed to clear notification store: {e}")
            
    # Remove water source store file if it exists to start fresh
    if os.path.exists(WATER_STORE_FILE):
        try:
            os.remove(WATER_STORE_FILE)
            print(f"[Prep] Cleared water sources storage ({WATER_STORE_FILE})")
        except Exception:
            pass
            
    # Pre-configure today's reminder to be 'pending' so we can trigger a slot start alert
    ReminderStore.update_reminder(user_id, date_str, {
        "status": "pending",
        "water_mm": 5.4,
        "electricity_slot": "08:00 AM - 04:00 PM (Day Slot)",
        "pump_run_time_str": "1 hr 15 mins",
        "reason": "Simulated pending irrigation run."
    })
    print(f"[Prep] Pre-configured today's reminder for user {user_id} on {date_str} as PENDING.")

    # Pre-configure a default water source at 100%
    WaterSourceStore.upsert_source(user_id, {
        "source_name": "Main Borewell",
        "source_type": "Borewell",
        "current_level_pct": 100
    })
    print(f"[Prep] Pre-configured a default water source 'Main Borewell' at 100% capacity.")

def main():
    # Force mock files for demo running to ensure it executes without Supabase table setup
    ReminderStore.use_db = False
    NotificationStore.use_db = False
    WaterSourceStore.use_db = False

    print("=" * 60)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    print("SCHEDULED IRRIGATION NOTIFICATIONS - TIME SIMULATOR")
    print("=" * 60)
    
    try:
        # 1. Retrieve a test farmer from the database
        response = admin_supabase.table("profiles").select("id, full_name, language").limit(1).execute()
        if not response.data:
            print("No profiles found in the database. Utilizing a fallback mock profile.")
            farmer_id = "mock-farmer-id"
            farmer_name = "Mock Farmer Patill"
            farmer_lang = "Marathi"
            # Upsert mock profile in database or dictionary if needed, but OnboardingRepository has a db call.
            # To avoid database dependency issues in case the Supabase table is empty or missing,
            # we will create a mock profile object or mock the onboarding repo for the test run.
        else:
            farmer = response.data[0]
            farmer_id = farmer["id"]
            farmer_name = farmer.get("full_name", "Farmer")
            farmer_lang = farmer.get("language", "Marathi")
            
        print(f"Testing with Farmer: {farmer_name} (ID: {farmer_id}), preferred language: {farmer_lang}")
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # 2. Reset stores for clean testing
        clean_test_stores(farmer_id, today_date)
        print("-" * 60)

        # 3. Scenario A: Simulate time BEFORE the slot starts (e.g. 07:15 AM today)
        sim_time_a = datetime.combine(datetime.now().date(), time(7, 15))
        print(f"\n[Scenario A] Current time simulated at: {sim_time_a.strftime('%I:%M %p')}")
        print("Checking if notification should be sent...")
        notif_a = NotificationService.check_and_trigger_notifications(farmer_id, simulated_time=sim_time_a)
        if notif_a is None:
            print(">> Output: [SKIP] No notification sent. Reason: Electricity slot hasn't started yet (Slot is 08:00 AM - 04:00 PM).")
        else:
            print(f">> Output: [ERROR] Triggered unexpected notification: {notif_a.get('message')}")

        # 4. Scenario B: Simulate time DURING the slot (e.g. 08:30 AM today)
        sim_time_b = datetime.combine(datetime.now().date(), time(8, 30))
        print(f"\n[Scenario B] Current time simulated at: {sim_time_b.strftime('%I:%M %p')}")
        print("Checking if notification should be sent...")
        notif_b = NotificationService.check_and_trigger_notifications(farmer_id, simulated_time=sim_time_b)
        if notif_b is not None:
            print(">> Output: [ALERT] Localized notification triggered and sent!")
            print(f"   - Title: {notif_b.get('title')}")
            print(f"   - Message:\n{notif_b.get('message')}")
        else:
            print(">> Output: [ERROR] Notification was not triggered inside the slot.")

        # 5. Scenario C: Simulate subsequent check inside slot (e.g. 09:45 AM today)
        sim_time_c = datetime.combine(datetime.now().date(), time(9, 45))
        print(f"\n[Scenario C] Current time simulated at: {sim_time_c.strftime('%I:%M %p')}")
        print("Checking if notification should be sent...")
        notif_c = NotificationService.check_and_trigger_notifications(farmer_id, simulated_time=sim_time_c)
        if notif_c is None:
            print(">> Output: [SKIP] No notification sent. Reason: Duplicate prevention (already sent today's alert).")
        else:
            print(f">> Output: [ERROR] Duplicate notification sent: {notif_c.get('message')}")

        # 6. Retrieve notification list from API
        user_notifs = NotificationStore.get_notifications(farmer_id)
        print("\n" + "=" * 60)
        print("NOTIFICATION LIST IN DATABASE FOR FARMER:")
        print("=" * 60)
        for idx, n in enumerate(user_notifs):
            print(f"[{idx+1}] ID: {n.get('id')[:8]}... | Status: {n.get('status').upper()} | Type: {n.get('type')}")
            print(f"    Created: {n.get('created_at')}")
            print(f"    Message:\n{n.get('message')}")
            print("-" * 40)

        # 7. Try marking as read
        if user_notifs:
            notif_id = user_notifs[0]["id"]
            print(f"\nMarking notification {notif_id[:8]}... as READ...")
            updated = NotificationStore.mark_as_read(farmer_id, notif_id)
            print(f"Updated status: {updated.get('status').upper()}")
            
        # 8. Marathi Localization Simulation Pass
        print("\n" + "=" * 60)
        print("RUNNING MARATHI LOCALIZATION DEMO PASS")
        print("=" * 60)
        from unittest.mock import patch
        
        marathi_profile = {
            "id": farmer_id,
            "full_name": farmer_name,
            "language": "Marathi"
        }
        
        # Reset store files to clear previous alerts
        clean_test_stores(farmer_id, today_date)
        
        sim_time_mr = datetime.combine(datetime.now().date(), time(10, 15))
        print(f"\n[Marathi Scenario] Current time simulated at: {sim_time_mr.strftime('%I:%M %p')}")
        print("Checking if notification should be sent (patched with language = Marathi)...")
        
        with patch("app.repositories.onboarding_repository.OnboardingRepository.get_profile", return_value=marathi_profile):
            notif_mr = NotificationService.check_and_trigger_notifications(farmer_id, simulated_time=sim_time_mr)
            if notif_mr is not None:
                print(">> Output: [ALERT] Localized Marathi notification triggered!")
                print(f"   - Title: {notif_mr.get('title')}")
                print(f"   - Message:\n{notif_mr.get('message')}")
            else:
                print(">> Output: [ERROR] Marathi notification was not triggered.")
            if notif_mr is not None:
                notif_id_mr = notif_mr["id"]
                print(f"\nMarking Marathi notification {notif_id_mr[:8]}... as READ...")
                updated_mr = NotificationStore.mark_as_read(farmer_id, notif_id_mr)
                print(f"Updated status: {updated_mr.get('status').upper()}")

        # 9. Scenario D: Simulate critically low water level alert (e.g. Borewell drops to 15%)
        print("\n" + "=" * 60)
        print("RUNNING SCENARIO D: LOW WATER CAPACITY WARNING")
        print("=" * 60)
        # Fetch current water source for farmer
        sources = WaterSourceStore.get_sources(farmer_id)
        if sources:
            source = sources[0]
            print(f"[Scenario D] Simulating drop in water levels for: {source.get('source_name')}")
            # Update main borewell level to 15% (which triggers alert, <= 20%)
            WaterSourceStore.update_level(farmer_id, source["id"], 15)
            
            sim_time_d = datetime.combine(datetime.now().date(), time(11, 0))
            print(f"Current time simulated at: {sim_time_d.strftime('%I:%M %p')}")
            print("Checking if notification should be sent (patched with language = Marathi)...")
            
            # We'll patch with language = Marathi to see Devanagari warning
            with patch("app.repositories.onboarding_repository.OnboardingRepository.get_profile", return_value=marathi_profile):
                notif_d = NotificationService.check_and_trigger_notifications(farmer_id, simulated_time=sim_time_d)
                if notif_d is not None:
                    print(">> Output: [ALERT] Low-water safety warning alert triggered!")
                    print(f"   - Title: {notif_d.get('title')}")
                    print(f"   - Message:\n{notif_d.get('message')}")
                else:
                    print(">> Output: [ERROR] Low-water notification was not triggered.")
            
            # Reset levels back to 100%
            WaterSourceStore.update_level(farmer_id, source["id"], 100)
            
        print("\n" + "=" * 60)
        print("SIMULATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
