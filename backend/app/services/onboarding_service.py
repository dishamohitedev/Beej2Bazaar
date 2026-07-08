from app.repositories.onboarding_repository import OnboardingRepository


class OnboardingService:

    @staticmethod
    def submit(user_id: str, data: dict):

        data["onboarding_completed"] = True

        return OnboardingRepository.update_profile(
            user_id,
            data,
        )

    @staticmethod
    def status(user_id: str):

        profile = OnboardingRepository.get_profile(user_id)

        return {
            "completed": profile["onboarding_completed"]
        }