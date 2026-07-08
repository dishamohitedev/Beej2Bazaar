import os
import sys

# Reconfigure stdout to support UTF-8 (for Devanagari/local script outputs in Windows terminals)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# Ensure backend root is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database.supabase import admin_supabase
from app.recommendation.recommendation_service import RecommendationService

def main():
    print("=" * 60)
    print("AGRONOMIC DECISION ENGINE (ADE) - LIVE DEMO RUNNER")
    print("=" * 60)
    
    # 1. Retrieve a test farmer from the database
    try:
        response = admin_supabase.table("profiles").select("id, full_name, soil_type, irrigation, language").limit(1).execute()
        if not response.data:
            print("No profiles found in the database. Please onboard a farmer first!")
            return
        
        farmer = response.data[0]
        farmer_id = farmer["id"]
        
        print(f"Found Profile in DB: {farmer.get('full_name')} (ID: {farmer_id})")
        print("--> Overriding profile context to Maharashtra for this demo run.")
        print("-" * 60)
        
        # 2. Instantiate and run Recommendation Service with Maharashtra context
        print("Running Agronomic Pipeline (fetching crops, weather, mandi rates for Pune, Maharashtra)...")
        
        mock_maharashtra_profile = {
            "id": farmer_id,
            "full_name": "Amit Patel (Maharashtra Farmer)",
            "state": "Maharashtra",
            "district": "Pune",
            "taluka": "Haveli",
            "village": "Manjari",
            "soil_type": "Black",
            "irrigation": "Drip",
            "language": "Marathi",
            "farm_size": 5.0,
            "farm_unit": "acre",
            "onboarding_completed": True
        }
        
        from unittest.mock import patch
        service = RecommendationService()
        with patch("app.recommendation.data_collector.OnboardingRepository.get_profile", return_value=mock_maharashtra_profile):
            result = service.generate_recommendations(farmer_id)
        
        # 3. Print recommendations
        print("\nDetermined TOP RECOMMENDED CROPS:")
        for idx, rec in enumerate(result.recommendations):
            print(f"\n[{idx+1}] {rec.crop.crop_name} (Final Score: {rec.final_score}/100)")
            print(f"    - Type: {rec.crop.crop_type} | Scientific: {rec.crop.scientific_name}")
            print(f"    - Sub-scores: Soil={rec.scores.soil_score}, Weather={rec.scores.weather_score}, Market={rec.scores.market_score}, Water={rec.scores.water_score}, Season={rec.scores.season_score}")
            print(f"    - Water Req: {rec.crop.water_requirement} | Temp bounds: {rec.crop.ideal_temp_min}-{rec.crop.ideal_temp_max}°C")
            
        # 4. Print Gemini Explanations
        print("\n" + "=" * 60)
        print(f"GEMINI EXPLANATION (Target Language: {farmer.get('language')}):")
        print("=" * 60)
        print(result.explanation)
        print("=" * 60)
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
