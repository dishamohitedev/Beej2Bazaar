import pytest
from app.irrigation.calculators.eto_calculator import EToCalculator
from app.irrigation.calculators.etc_calculator import ETcCalculator
from app.irrigation.calculators.rainfall_calculator import RainfallCalculator
from app.irrigation.calculators.irrigation_calculator import IrrigationCalculator
from app.irrigation.calculators.electricity_optimizer import ElectricityOptimizer
from app.irrigation.irrigation_engine import IrrigationEngine
from app.irrigation.schedule_generator import ScheduleGenerator
from app.irrigation.models import DailyWeather, PyFAOOutput, DailyScheduleItem
from app.irrigation.reminder_store import ReminderStore
from app.irrigation.notification_store import NotificationStore
from app.irrigation.water_source_store import WaterSourceStore

ReminderStore.use_db = False
NotificationStore.use_db = False
WaterSourceStore.use_db = False

def test_eto_calculator_hargreaves_samani():
    # Test calculations for known inputs
    # Pune, India (Latitude: 18.5204)
    latitude = 18.5204
    date_str = "2026-07-10"
    temp_min = 22.0
    temp_max = 32.0
    
    eto = EToCalculator.calculate_hargreaves_samani(latitude, date_str, temp_min, temp_max)
    
    # ETo should be a positive value, typically between 3 and 7 mm/day in tropical bounds
    assert eto > 0.0
    assert eto < 15.0

def test_eto_calculator_resolve_eto():
    # When api_eto is provided, it should be resolved directly
    resolved = EToCalculator.resolve_eto(18.5204, "2026-07-10", 22.0, 32.0, api_eto=5.4)
    assert resolved == 5.4
    
    # When api_eto is missing, it should fallback to Hargreaves
    resolved_fallback = EToCalculator.resolve_eto(18.5204, "2026-07-10", 22.0, 32.0, api_eto=None)
    assert resolved_fallback > 0.0

def test_etc_calculator():
    # Rice is a high water requirement crop
    kc_rice_mid = ETcCalculator.get_crop_coefficient("Rice - Basmati 1121", "Mid")
    assert kc_rice_mid == 1.20
    
    # Wheat is low initial, high mid
    kc_wheat_ini = ETcCalculator.get_crop_coefficient("Wheat", "Initial")
    assert kc_wheat_ini == 0.40
    
    # Calculation etc = Kc * ETo
    etc = ETcCalculator.calculate_etc(5.0, "Tomato", "Vegetative")
    # Tomato vegetative maps to development -> Kc=0.85. ETc = 5.0 * 0.85 = 4.25
    assert etc == 4.25

def test_effective_rainfall():
    # Under 2.0mm should be 0.0 effective rainfall
    peff_dry = RainfallCalculator.calculate_effective_rainfall(1.5)
    assert peff_dry == 0.0
    
    # Between 2.0 and 75.0mm
    # Rain = 10.0mm -> Peff = 0.8 * (10 - 2) = 6.4mm
    peff_mid = RainfallCalculator.calculate_effective_rainfall(10.0)
    assert peff_mid == 6.4
    
    # Over 75.0mm
    # Rain = 100.0mm -> Peff = 0.7 * (100 - 2) = 68.6mm
    peff_heavy = RainfallCalculator.calculate_effective_rainfall(100.0)
    assert peff_heavy == 68.6

def test_irrigation_calculator():
    # Drip efficiency is 90%
    eff_drip = IrrigationCalculator.get_system_efficiency("Drip")
    assert eff_drip == 0.90
    
    # Canal efficiency is 50%
    eff_canal = IrrigationCalculator.get_system_efficiency("Canal")
    assert eff_canal == 0.50
    
    # Requirement: NIR = ETc - P_eff = 5.0 - 2.0 = 3.0mm
    # Drip GIR = 3.0 / 0.90 = 3.33mm
    gir_drip = IrrigationCalculator.calculate_requirements(5.0, 2.0, "Drip")
    assert gir_drip == 3.33
    
    # If rain exceeds ETc, GIR should be 0.0
    gir_rainy = IrrigationCalculator.calculate_requirements(3.0, 5.0, "Drip")
    assert gir_rainy == 0.0

def test_irrigation_engine_dry():
    # Dry day weather
    weather = DailyWeather(
        date="2026-07-10",
        temp_min=22.0,
        temp_max=32.0,
        precipitation=0.0,
        wind_speed=10.0,
        relative_humidity=60.0
    )
    
    # ETo=5.0, ETc=6.0 (e.g. Kc=1.20)
    pyfao_out = PyFAOOutput(eto=5.0, etc=6.0, water_requirement_mm=6.0)
    
    # Evaluate with Drip (state: Maharashtra, farm size: 2.0 acres)
    item = IrrigationEngine.evaluate_daily_need(
        weather=weather, 
        pyfao_output=pyfao_out, 
        irrigation_method="Drip",
        state="Maharashtra",
        farm_size=2.0
    )
    assert item.irrigate is True
    # GIR = 6.0 / 0.90 = 6.67
    assert item.water_mm == 6.67
    assert "exceeds effective rainfall" in item.reason
    assert item.electricity_slot is not None
    assert item.pump_run_time_str is not None

def test_irrigation_engine_rainy():
    # Rainy day weather (20mm rain)
    weather = DailyWeather(
        date="2026-07-10",
        temp_min=22.0,
        temp_max=32.0,
        precipitation=20.0,
        wind_speed=10.0,
        relative_humidity=85.0
    )
    
    # ETo=3.0, ETc=3.6
    pyfao_out = PyFAOOutput(eto=3.0, etc=3.6, water_requirement_mm=3.6)
    
    # Effective Rain = 0.8 * (20 - 2) = 14.4mm.
    # 14.4mm exceeds crop water demand (3.6mm), so no irrigation is needed.
    item = IrrigationEngine.evaluate_daily_need(
        weather=weather, 
        pyfao_output=pyfao_out, 
        irrigation_method="Drip",
        state="Maharashtra",
        farm_size=2.0
    )
    assert item.irrigate is False
    assert item.water_mm == 0.0
    assert "sufficient" in item.reason
    assert item.electricity_slot is None
    assert item.pump_run_time_str is None

def test_schedule_generator():
    schedule = [
        DailyScheduleItem(date="2026-07-10", irrigate=True, water_mm=5.4, reason="Dry", electricity_slot="08:00 AM - 04:00 PM (Day Slot)", pump_run_time_str="1 hr"),
        DailyScheduleItem(date="2026-07-11", irrigate=False, water_mm=0.0, reason="Rain"),
        DailyScheduleItem(date="2026-07-12", irrigate=True, water_mm=4.2, reason="Dry", electricity_slot="08:00 AM - 04:00 PM (Day Slot)", pump_run_time_str="45 mins")
    ]
    
    response = ScheduleGenerator.generate_response(schedule)
    assert response.today.date == "2026-07-10"
    assert response.today.irrigate is True
    assert response.next_irrigation == "2026-07-10"
    assert len(response.schedule) == 3

def test_electricity_optimizer():
    # Test Maharashtra Day Slot rotation
    slot_mh_even = ElectricityOptimizer.get_electricity_slot("Maharashtra", "2026-07-06") # July 6, 2026 is week 28 (even)
    assert "Day Slot" in slot_mh_even
    
    # Test Maharashtra Night Slot rotation
    slot_mh_odd = ElectricityOptimizer.get_electricity_slot("Maharashtra", "2026-07-13") # July 13, 2026 is week 29 (odd)
    assert "Night Slot" in slot_mh_odd
    
    # Test Punjab constant day slot
    slot_pb = ElectricityOptimizer.get_electricity_slot("Punjab", "2026-07-10")
    assert "Day Slot" in slot_pb
    
    # Test runtime calculation
    # 2.0 acres, 3.0 mm gross irrigation depth, 5 HP pump
    # Volume = 2.0 * 3.0 * 4046.86 = 24281.16 Liters
    # Flow rate = 5.0 * 3000 = 15000 Liters/hour
    # Runtime = 24281.16 / 15000 = 1.6187 hours = 1 hr 37 mins (since rounded)
    run_details = ElectricityOptimizer.calculate_pump_runtime(2.0, 3.0, 5.0)
    assert run_details["runtime_str"] == "1 hr 37 mins"
    assert run_details["runtime_hours"] == 1.62


def test_reminder_store(tmp_path):
    import os
    from unittest.mock import patch
    from app.irrigation.reminder_store import ReminderStore

    mock_store_file = os.path.join(tmp_path, "test_reminders.json")
    with patch("app.irrigation.reminder_store.STORE_FILE", mock_store_file):
        # Initial check
        assert ReminderStore.get_reminder("user1", "2026-07-10") is None

        # Update reminder
        updated = ReminderStore.update_reminder("user1", "2026-07-10", {
            "status": "pending",
            "water_mm": 4.5,
            "electricity_slot": "Day Slot",
            "pump_run_time_str": "1 hr"
        })
        assert updated["status"] == "pending"
        assert updated["water_mm"] == 4.5

        # Fetch it back
        fetched = ReminderStore.get_reminder("user1", "2026-07-10")
        assert fetched is not None
        assert fetched["water_mm"] == 4.5

        # History check
        assert len(ReminderStore.get_history("user1")) == 0

        # Mark as completed
        ReminderStore.update_reminder("user1", "2026-07-10", {"status": "completed"})
        history = ReminderStore.get_history("user1")
        assert len(history) == 1
        assert history[0]["status"] == "completed"


def test_irrigation_router_endpoints(tmp_path):
    import os
    from fastapi.testclient import TestClient
    from unittest.mock import patch
    from app.main import app
    from app.dependencies.auth import get_current_user

    class MockUser:
        id = "mock-user-123"
        email = "mockuser@beejbazaar.com"
        user_metadata = {"role": "farmer", "name": "Mock Farmer"}

    # Mock user profile database call
    mock_profile = {
        "id": "mock-user-123",
        "full_name": "Mock Farmer",
        "state": "Maharashtra",
        "district": "Pune",
        "taluka": "Haveli",
        "village": "Manjari",
        "farm_size": 2.5,
        "soil_type": "Black",
        "irrigation": "Drip",
        "language": "Marathi",
        "onboarding_completed": True
    }

    app.dependency_overrides[get_current_user] = lambda: MockUser()
    client = TestClient(app)

    mock_store_file = os.path.join(tmp_path, "test_router_reminders.json")
    with patch("app.repositories.onboarding_repository.OnboardingRepository.get_profile", return_value=mock_profile), \
         patch("app.recommendation.gemini_service.GeminiService.generate_irrigation_explanations", return_value="Mock Gemini Advice"), \
         patch("app.irrigation.reminder_store.STORE_FILE", mock_store_file):
        
        # Test status GET
        res = client.get("/api/irrigation/status")
        assert res.status_code == 200
        data = res.json()
        assert data["date"] is not None
        assert data["status"] in ["pending", "skipped"]

        # If it was pending, try starting and completing
        if data["status"] == "pending":
            res_start = client.post("/api/irrigation/start")
            assert res_start.status_code == 200
            assert res_start.json()["status"] == "watering"

            res_comp = client.post("/api/irrigation/complete")
            assert res_comp.status_code == 200
            assert res_comp.json()["status"] == "completed"

            # Check history
            res_hist = client.get("/api/irrigation/history")
            assert res_hist.status_code == 200
            assert len(res_hist.json()) > 0

