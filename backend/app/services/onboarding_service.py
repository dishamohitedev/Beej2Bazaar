import logging
from app.repositories.onboarding_repository import OnboardingRepository

logger = logging.getLogger(__name__)


class OnboardingService:

    @staticmethod
    def submit(user_id: str, data: dict):

        data["onboarding_completed"] = True

        # Try geocoding the address fields
        from app.recommendation.data_collector import DataCollector
        coords = DataCollector.geocode_location(
            data.get("state", ""),
            data.get("district", ""),
            data.get("taluka", ""),
            data.get("village", "")
        )
        if coords:
            data["latitude"], data["longitude"] = coords

        try:
            return OnboardingRepository.update_profile(
                user_id,
                data,
            )
        except Exception as e:
            # If the database fails because the latitude/longitude columns don't exist yet,
            # fall back and save without them to make sure onboarding doesn't break.
            err_str = str(e).lower()
            if "latitude" in err_str or "longitude" in err_str or "column" in err_str:
                logger.warning(
                    f"Failed to save latitude/longitude coordinates to database (profiles table might be missing columns). "
                    f"Retrying save without coordinates. Error: {e}"
                )
                data.pop("latitude", None)
                data.pop("longitude", None)
                return OnboardingRepository.update_profile(
                    user_id,
                    data,
                )
            raise e

    @staticmethod
    def status(user_id: str):

        profile = OnboardingRepository.get_profile(user_id)

        return {
            "completed": profile["onboarding_completed"]
        }

