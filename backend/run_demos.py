import subprocess
import sys
import os

def main():
    # Force stdout to UTF-8 to support local scripts (Marathi/Hindi) in terminal
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 70)
    print("BEEJ2BAZAR DEMO PLATFORM - IRRIGATION & NOTIFICATIONS")
    print("=" * 70)
    
    # 1. Run Irrigation Scheduling Demo
    print("\n🎬 STEP 1: Running Irrigation Recommendation Engine Demo...")
    print("-" * 70)
    subprocess.run([sys.executable, "run_irrigation_demo.py"], cwd=backend_dir)
    
    print("\n" + "=" * 70)
    # 2. Run Notifications Demo
    print("🎬 STEP 2: Running Scheduled Electricity Notifications Time-Travel Demo...")
    print("-" * 70)
    subprocess.run([sys.executable, "run_notification_demo.py"], cwd=backend_dir)
    
    print("\n" + "=" * 70)
    print("ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
