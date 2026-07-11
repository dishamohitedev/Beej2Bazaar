import os
import sys

# Ensure backend root is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.supabase import admin_supabase
from app.irrigation.irrigation_service import IrrigationService

def main():
    print("=" * 60)
    # Reconfigure stdout to support UTF-8 (for Devanagari/local script outputs in Windows terminals)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("INTELLIGENT IRRIGATION SCHEDULER - LIVE DEMO RUNNER")
    print("=" * 60)

    try:
        # 1. Retrieve a test farmer from the database
        response = admin_supabase.table("profiles").select("id, full_name, language").limit(1).execute()
        if not response.data:
            print("No profiles found in the database. Please onboard a farmer first!")
            return
            
        farmer = response.data[0]
        farmer_id = farmer["id"]
        
        print(f"Found Profile in DB: {farmer.get('full_name')} (ID: {farmer_id})")
        print("Running Irrigation Scheduling Pipeline (fetching weather, calculating crop water demands)...")
        print("-" * 60)

        # 2. Execute the Irrigation Service
        result = IrrigationService.get_irrigation_schedule(farmer_id)
        
        # 3. Print Results
        print("\nTODAY'S IRRIGATION ACTION:")
        print(f"  - Irrigate: {'YES' if result.today.irrigate else 'NO'}")
        print(f"  - Water Amount: {result.today.water_mm:.1f} mm")
        if result.today.irrigate:
            print(f"  - Electricity Power Slot: {result.today.electricity_slot}")
            print(f"  - Est. Pump Run Time: {result.today.pump_run_time_str}")
        print(f"  - Reason: {result.today.reason}")
        
        if result.next_irrigation:
            print(f"\nNEXT SCHEDULED WATERING DATE: {result.next_irrigation}")
        else:
            print("\nNEXT SCHEDULED WATERING DATE: None in the next 7 days.")

        print("\n7-DAY IRRIGATION SCHEDULE:")
        for idx, item in enumerate(result.schedule):
            status = "IRRIGATE" if item.irrigate else "SKIP"
            water = f"{item.water_mm:.1f} mm" if item.irrigate else "0.0 mm"
            slot_info = f" | Power: {item.electricity_slot} | Pump: {item.pump_run_time_str}" if item.irrigate else ""
            print(f"  [{idx+1}] Date: {item.date} | Action: {status.ljust(8)} | Water: {water.ljust(8)}{slot_info}")
            print(f"      Reason: {item.reason}")

        print("\n" + "=" * 60)
        print(f"GEMINI EXPLANATION (Target Language: {farmer.get('language')}):")
        print("=" * 60)
        # Avoid printing non-ASCII text to the console on Windows to prevent terminal corruption/wrapping bugs
        is_ascii = all(ord(c) < 128 for c in result.explanation)
        if is_ascii:
            print(result.explanation)
        else:
            print("Explanation contains non-ASCII characters (Marathi/Hindi).")
            print("To prevent terminal rendering glitches, it has been written directly to 'irrigation_demo_output.md'.")
        print("=" * 60)

        # 4. Save to a markdown file for clean viewing (prevents terminal encoding/wrapping issues)
        output_filepath = "irrigation_demo_output.md"
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("# Intelligent Irrigation Scheduler (ADE Feature 2) - Demo Output\n\n")
            f.write(f"**Farmer Profile**: {farmer.get('full_name')} (ID: {farmer_id})\n")
            f.write(f"**Language**: {farmer.get('language')}\n\n")
            
            f.write("## Today's Recommendation\n")
            f.write(f"- **Irrigate**: {'YES' if result.today.irrigate else 'NO'}\n")
            f.write(f"- **Water Amount**: {result.today.water_mm:.1f} mm\n")
            if result.today.irrigate:
                f.write(f"- **Active Power Slot**: {result.today.electricity_slot}\n")
                f.write(f"- **Est. Pump Run Time**: {result.today.pump_run_time_str}\n")
            f.write(f"- **Reason**: {result.today.reason}\n\n")
            
            f.write(f"**Next Scheduled Irrigation**: {result.next_irrigation or 'None in next 7 days'}\n\n")
            
            f.write("## 7-Day Irrigation Schedule\n\n")
            f.write("| Day | Date | Action | Water Amount (mm) | Active Power Slot | Est. Pump Run Time | Reason |\n")
            f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
            for idx, item in enumerate(result.schedule):
                status = "**IRRIGATE**" if item.irrigate else "SKIP"
                water = f"{item.water_mm:.1f} mm" if item.irrigate else "0.0 mm"
                slot = item.electricity_slot or "-"
                runtime = item.pump_run_time_str or "-"
                f.write(f"| {idx+1} | {item.date} | {status} | {water} | {slot} | {runtime} | {item.reason} |\n")
            
            f.write("\n## Gemini Explanation\n\n")
            f.write(result.explanation)
            f.write("\n")
            
        print(f"\n[INFO] Saved formatted output to {output_filepath} for clean reading in VS Code.")

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
