from datetime import datetime
from pydantic import BaseModel


class DiseaseAlert(BaseModel):
    id: str
    crop_id: str
    district: str
    disease_name: str
    severity: str
    report_count: int
    message: str
    status: str
    created_at: datetime


class DiseaseAlertNotification(BaseModel):
    id: str
    is_read: bool
    created_at: datetime
    disease_alerts: DiseaseAlert