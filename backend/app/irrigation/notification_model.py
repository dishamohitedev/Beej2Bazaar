from pydantic import BaseModel
from typing import Optional

class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str  # e.g., "electricity_available"
    status: str = "unread"  # "unread", "read"
    created_at: str
    date: str  # YYYY-MM-DD
