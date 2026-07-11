from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List
from app.dependencies.auth import get_current_user
from app.irrigation.irrigation_service import IrrigationService
from app.irrigation.reminder_store import ReminderStore
from app.irrigation.water_source_store import WaterSourceStore
from app.irrigation.models import WaterSource, WaterSavingsResponse, WaterSavingsRecord
from app.repositories.onboarding_repository import OnboardingRepository

router = APIRouter(
    prefix="/irrigation",
    tags=["Irrigation"],
)

@router.get("/status")
def get_irrigation_status(current_user = Depends(get_current_user)):
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Check if a log exists for today
    reminder = ReminderStore.get_reminder(current_user.id, today_str)
    
    if not reminder:
        try:
            # Query the scheduling pipeline for today's forecast
            result = IrrigationService.get_irrigation_schedule(current_user.id)
            
            # If the calculation says to irrigate, initialize as pending, else skipped
            initial_status = "pending" if result.today.irrigate else "skipped"
            
            reminder = ReminderStore.update_reminder(current_user.id, today_str, {
                "status": initial_status,
                "water_mm": result.today.water_mm,
                "electricity_slot": result.today.electricity_slot,
                "pump_run_time_str": result.today.pump_run_time_str,
                "reason": result.today.reason
            })
        except Exception as e:
            # Fallback if profile onboarding is incomplete or weather API fails
            reminder = {
                "date": today_str,
                "status": "skipped",
                "water_mm": 0.0,
                "started_at": None,
                "completed_at": None,
                "electricity_slot": None,
                "pump_run_time_str": None,
                "reason": f"Could not determine status: {str(e)}",
                "error": True
            }
            
    return reminder

@router.post("/start")
def start_irrigation(current_user = Depends(get_current_user)):
    today_str = datetime.now().strftime("%Y-%m-%d")
    reminder = ReminderStore.get_reminder(current_user.id, today_str)
    
    if not reminder:
        # Initialize first
        get_irrigation_status(current_user)
        reminder = ReminderStore.get_reminder(current_user.id, today_str)
        
    if reminder.get("status") == "skipped":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No irrigation is scheduled for today."
        )
        
    updated = ReminderStore.update_reminder(current_user.id, today_str, {
        "status": "watering",
        "started_at": datetime.now().isoformat()
    })
    return updated

@router.post("/complete")
def complete_irrigation(current_user = Depends(get_current_user)):
    today_str = datetime.now().strftime("%Y-%m-%d")
    reminder = ReminderStore.get_reminder(current_user.id, today_str)
    
    if not reminder or reminder.get("status") != "watering":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Irrigation pump must be started before completing."
        )
        
    updated = ReminderStore.update_reminder(current_user.id, today_str, {
        "status": "completed",
        "completed_at": datetime.now().isoformat()
    })
    return updated

@router.get("/history")
def get_irrigation_history(current_user = Depends(get_current_user)):
    return ReminderStore.get_history(current_user.id)

@router.get("/schedule")
def get_irrigation_schedule(current_user = Depends(get_current_user)):
    try:
        return IrrigationService.get_irrigation_schedule(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch schedule: {str(e)}"
        )

@router.get("/water-sources", response_model=List[WaterSource])
def get_water_sources(current_user = Depends(get_current_user)):
    return WaterSourceStore.get_sources(current_user.id)

@router.post("/water-sources", response_model=WaterSource)
def upsert_water_source(source: WaterSource, current_user = Depends(get_current_user)):
    source_data = source.dict()
    source_data["user_id"] = current_user.id
    return WaterSourceStore.upsert_source(current_user.id, source_data)

@router.put("/water-sources/{source_id}/level", response_model=WaterSource)
def update_water_source_level(
    source_id: str,
    level_pct: int = Query(..., ge=0, le=100, description="Current capacity percentage (0 to 100)"),
    current_user = Depends(get_current_user)
):
    updated = WaterSourceStore.update_level(current_user.id, source_id, level_pct)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Water source not found."
        )
    return updated

@router.get("/water-savings", response_model=WaterSavingsResponse)
def get_water_savings(current_user = Depends(get_current_user)):
    """
    Exposes daily water savings compared to traditional farming baselines.
    Used to construct the frontend visualization graph.
    """
    try:
        profile = OnboardingRepository.get_profile(current_user.id) or {}
    except Exception:
        profile = {}
        
    farm_size = float(profile.get("farm_size") if profile.get("farm_size") is not None else 1.0)
    reminders = ReminderStore.get_all_reminders(current_user.id)
    
    daily_records = []
    total_savings_mm = 0.0
    total_savings_liters = 0.0
    total_runs_optimized = 0
    
    BASELINE_MM = 6.0
    LITERS_PER_ACRE_MM = 4046.86
    
    # Take the last 7 logged days
    recent_logs = sorted(reminders, key=lambda x: x.get("date", ""), reverse=True)[:7]
    # Sort chronologically (oldest to newest) for left-to-right plotting
    recent_logs.reverse()
    
    for run in recent_logs:
        status_str = run.get("status", "pending")
        actual_mm = float(run.get("water_mm") if run.get("water_mm") is not None else 0.0)
        
        if status_str == "completed":
            savings_mm = max(0.0, BASELINE_MM - actual_mm)
            total_runs_optimized += 1
        elif status_str == "skipped":
            savings_mm = BASELINE_MM
            actual_mm = 0.0
            total_runs_optimized += 1
        else:
            # Pending or active watering run - no finalized savings logged yet
            savings_mm = 0.0
            
        savings_liters = savings_mm * farm_size * LITERS_PER_ACRE_MM
        
        daily_records.append(WaterSavingsRecord(
            date=run.get("date", ""),
            baseline_mm=BASELINE_MM,
            actual_mm=actual_mm,
            savings_mm=round(savings_mm, 2),
            savings_liters=round(savings_liters, 1),
            status=status_str
        ))
        
        total_savings_mm += savings_mm
        total_savings_liters += savings_liters
        
    return WaterSavingsResponse(
        daily_records=daily_records,
        total_savings_mm=round(total_savings_mm, 2),
        total_savings_liters=round(total_savings_liters, 1),
        total_runs_optimized=total_runs_optimized
    )

