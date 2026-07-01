"""
User model + Role enum. Every other module's permission checks reference
UserRole, so this file is the single source of truth for roles.
"""
from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    FARMER = "farmer"
    ADMIN = "admin"
    AGRONOMIST = "agronomist"
    EQUIPMENT_VENDOR = "equipment_vendor"
    LABOUR_CONTRACTOR = "labour_contractor"
    BUYER = "buyer"
    GOVERNMENT_OFFICER = "government_officer"


class UserBase(BaseModel):
    phone: str = Field(..., description="E.164 format, e.g. +919876543210")
    name: Optional[str] = None
    role: UserRole


class UserInDB(UserBase):
    id: str
    is_active: bool = True
    is_profile_complete: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPublic(BaseModel):
    id: str
    phone: str
    name: Optional[str] = None
    role: UserRole
    is_profile_complete: bool


class OTPRequestIn(BaseModel):
    phone: str = Field(..., min_length=8, max_length=20)


class OTPVerifyIn(BaseModel):
    phone: str = Field(..., min_length=8, max_length=20)
    otp: str = Field(..., min_length=4, max_length=6)
    # role + name are only required/used on first-time registration
    role: Optional[UserRole] = None
    name: Optional[str] = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


class RefreshIn(BaseModel):
    refresh_token: str
