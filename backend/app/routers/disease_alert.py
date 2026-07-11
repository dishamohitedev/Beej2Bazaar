from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth import get_current_user
from app.repositories.disease_alert_repository import DiseaseAlertRepository
from app.schemas.disease_alert import (
    DiseaseAlert,
    DiseaseAlertNotification,
)

router = APIRouter(
    prefix="/alerts",
    tags=["Disease Alerts"],
)


@router.get(
    "",
    response_model=List[DiseaseAlert],
)
def get_alerts():

    return DiseaseAlertRepository.get_active_alerts()

@router.get(
    "/my-notifications",
    response_model=List[DiseaseAlertNotification],
)
def my_notifications(
    current_user=Depends(get_current_user),
):

    return DiseaseAlertRepository.get_user_notifications(
        current_user.id
    )

@router.get("/unread-count")
def unread_count(
    current_user=Depends(get_current_user),
):

    return {
        "count": DiseaseAlertRepository.get_unread_count(
            current_user.id
        )
    }

@router.get(
    "/{alert_id}",
    response_model=DiseaseAlert,
)
def get_alert(alert_id: str):

    alert = DiseaseAlertRepository.get_alert(alert_id)

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    return alert




@router.patch("/{notification_id}/read")
def mark_read(notification_id: str):

    DiseaseAlertRepository.mark_as_read(
        notification_id
    )

    return {
        "message": "Notification marked as read"
    }