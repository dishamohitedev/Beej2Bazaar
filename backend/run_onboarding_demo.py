import os
import sys
from datetime import date

# Ensure backend root is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.supabase import admin_supabase
from app.services.onboarding_service import OnboardingService

def main():
    print("=" * 60)
    # Reconfigure stdout to support UTF-8 (for Devanagari/local script outputs in Windows terminals)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("ONBOARDING PROCESS AND PROFILE STORAGE DEMO")
    print("=" * 60)

    # 1. Retrieve a test farmer from the database
    try:
        response = admin_supabase.table("profiles").select("id").limit(1).execute()
        if not response.data:
            print("No profiles found in the database. Please sign up a user first!")
            return
        
        farmer_id = response.data[0]["id"]
        print(f"Using test Profile ID from DB: {farmer_id}")
        print("-" * 60)
        
        # 2. Define test onboarding data with every requested field
        test_onboarding_data = {
            "full_name": "Rajesh Shinde (Demo Farmer)",
            "language": "Marathi",
            "state": "Maharashtra",
            "district": "Satara",
            "taluka": "Karad",
            "village": "Umbraj",
            "farm_size": 4.5,
            "farm_unit": "acre",
            "soil_type": "Black Clayey",
            "irrigation": "Canal",
            "farming_goals": ["Increase Yield", "Reduce Water Usage", "Soil Health Improvement"],
            "current_crop_id": None,
            "growth_stage": "Vegetative",
            "sowing_date": "2026-06-15",
            "expected_harvest": "2026-10-15"
        }

        print("Submitting Onboarding Data...")
        for key, val in test_onboarding_data.items():
            print(f"  - {key}: {val}")
        
        print("\nProcessing onboarding submission (this includes geocoding the address)...")
        
        # 3. Call the onboarding submission service
        updated_profile = OnboardingService.submit(farmer_id, test_onboarding_data.copy())
        
        print("\nOnboarding Submission Completed successfully!")
        print("-" * 60)

        # 4. Fetch the profile directly from Supabase to verify all fields are saved
        print("VERIFYING SAVED PROFILE DIRECTLY FROM DATABASE:")
        print("-" * 60)
        
        db_response = admin_supabase.table("profiles").select("*").eq("id", farmer_id).single().execute()
        saved_profile = db_response.data
        
        # Check all fields
        fields_to_check = [
            "full_name", "language", "state", "district", "taluka", "village",
            "farm_size", "farm_unit", "soil_type", "irrigation", "farming_goals",
            "onboarding_completed", "current_crop_id", "growth_stage",
            "sowing_date", "expected_harvest", "latitude", "longitude"
        ]
        
        all_match = True
        for field in fields_to_check:
            saved_val = saved_profile.get(field)
            original_val = test_onboarding_data.get(field)
            
            # Special case for onboarding_completed which is auto-set to True by service
            if field == "onboarding_completed":
                original_val = True
            
            # Special case for geocoded coordinates
            if field in ["latitude", "longitude"]:
                status = f"✅ Saved (Auto-Geocoded: {saved_val})"
            elif saved_val == original_val:
                status = f"✅ Match ({saved_val})"
            else:
                # Handle list formatting, string conversions or dates
                if str(saved_val) == str(original_val):
                    status = f"✅ Match ({saved_val})"
                else:
                    status = f"❌ Mismatch! (Expected: {original_val}, Got: {saved_val})"
                    all_match = False
                    
            print(f"Field '{field}':".ljust(28) + status)
            
        print("-" * 60)
        if all_match:
            print("SUCCESS: Every onboarding detail matches and is fully verified in the database!")
        else:
            print("WARNING: Some fields did not match. Please check database column constraints.")
        print("=" * 60)
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
