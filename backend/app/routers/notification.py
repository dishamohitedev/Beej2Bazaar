from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.dependencies.auth import get_current_user
from app.irrigation.notification_store import NotificationStore
from app.irrigation.notification_service import NotificationService
from app.irrigation.notification_model import Notification

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

@router.get("", response_model=List[Notification])
def get_user_notifications(current_user = Depends(get_current_user)):
    """
    Retrieves all notifications for the authenticated user, sorted by date descending.
    """
    return NotificationStore.get_notifications(current_user.id)

@router.post("/{notification_id}/read", response_model=Notification)
def mark_notification_as_read(notification_id: str, current_user = Depends(get_current_user)):
    """
    Marks a specific notification as read.
    """
    updated = NotificationStore.mark_as_read(current_user.id, notification_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found."
        )
    return updated

@router.post("/check")
def trigger_notification_check(
    simulated_time: Optional[str] = Query(
        None, 
        description="Optional simulated time in ISO format (e.g. YYYY-MM-DDTHH:MM:SS)"
    ),
    current_user = Depends(get_current_user)
):
    """
    Manually triggers notification evaluation. Can simulate time for testing.
    """
    parsed_time = None
    if simulated_time:
        try:
            # support both YYYY-MM-DDTHH:MM:SS and YYYY-MM-DDTHH:MM:SSZ
            clean_time = simulated_time.replace("Z", "")
            parsed_time = datetime.fromisoformat(clean_time)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid simulated_time format. Use ISO format (e.g., YYYY-MM-DDTHH:MM:SS)."
            )
            
    triggered = NotificationService.check_and_trigger_notifications(
        current_user.id, 
        simulated_time=parsed_time
    )
    
    if triggered:
        return {
            "triggered": True,
            "message": "Notification triggered and saved successfully.",
            "notification": triggered
        }
    else:
        return {
            "triggered": False,
            "message": "No new notifications triggered. Current state does not warrant an alert or alert was already sent."
        }
