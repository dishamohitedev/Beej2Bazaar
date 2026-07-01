"""
Phone OTP verification. Two implementations behind one interface:

- MockOTPService: for local dev without Firebase credentials. OTP is always
  "123456" for any phone number. Clearly logged so it's never mistaken for
  a real security control.
- FirebaseOTPService: production path. Firebase handles OTP delivery on the
  CLIENT side (React app calls Firebase JS SDK directly to send/verify OTP
  and gets an `idToken` back). This backend then verifies that idToken via
  firebase-admin. This is the standard, secure Firebase phone-auth pattern —
  raw OTPs should never be sent to your own backend.

Set FIREBASE_PROJECT_ID + FIREBASE_CREDENTIALS_JSON in .env to switch.
"""
from abc import ABC, abstractmethod
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger("otp_service")

MOCK_OTP = "123456"


class OTPService(ABC):
    @abstractmethod
    async def send_otp(self, phone: str) -> None:
        ...

    @abstractmethod
    async def verify(self, phone: str, otp_or_token: str) -> bool:
        ...


class MockOTPService(OTPService):
    async def send_otp(self, phone: str) -> None:
        logger.warning(
            "[MOCK OTP] No Firebase configured. OTP for %s is always '%s'. "
            "Set FIREBASE_PROJECT_ID + FIREBASE_CREDENTIALS_JSON in .env for production.",
            phone, MOCK_OTP,
        )

    async def verify(self, phone: str, otp_or_token: str) -> bool:
        return otp_or_token == MOCK_OTP


class FirebaseOTPService(OTPService):
    """
    Production adapter. Expects `otp_or_token` to be the Firebase idToken
    returned to the React app after client-side phone auth (NOT a raw 6-digit
    code). Verifies signature + phone_number claim via firebase-admin.
    """

    def __init__(self):
        import firebase_admin
        from firebase_admin import credentials
        import json

        if not firebase_admin._apps:
            cred = credentials.Certificate(json.loads(settings.FIREBASE_CREDENTIALS_JSON))
            firebase_admin.initialize_app(cred)

    async def send_otp(self, phone: str) -> None:
        # No-op: Firebase Phone Auth sends the OTP directly from the client
        # SDK (React), not from this backend. This method exists only to
        # satisfy the shared interface used by the auth router.
        return None

    async def verify(self, phone: str, otp_or_token: str) -> bool:
        from firebase_admin import auth as firebase_auth

        try:
            decoded = firebase_auth.verify_id_token(otp_or_token)
        except Exception:
            return False
        return decoded.get("phone_number") == phone


def get_otp_service() -> OTPService:
    if settings.USE_MOCK_FIREBASE:
        return MockOTPService()
    return FirebaseOTPService()


otp_service: OTPService = get_otp_service()
