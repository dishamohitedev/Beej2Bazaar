from pydantic import BaseModel
from typing import Optional


class ProfileResponse(BaseModel):
    id: str
    full_name: str
    phone: str
    language: str
    district: str
    taluka: str
    village: str
    avatar_url: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    village: Optional[str] = None
    avatar_url: Optional[str] = None