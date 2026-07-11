from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List
from app.dependencies.auth import get_current_user
from app.irrigation.irrigation_service import IrrigationService
from app.irrigation.reminder_store import ReminderStore
from app.irrigation.water_source_store import WaterSourceStore
from app.irrigation.models import WaterSource

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

