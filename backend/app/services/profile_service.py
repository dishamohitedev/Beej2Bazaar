from app.repositories.profile_repository import ProfileRepository


class ProfileService:

    @staticmethod
    def get_or_create_profile(user):
        profile = ProfileRepository.get_by_user_id(user.id)

        if profile:
            return profile

        profile_data = {
            "id": user.id,
            "full_name": "",
            "phone": "",
            "language": "",
            "district": "",
            "taluka": "",
            "village": "",
            "avatar_url": "",
        }

        return ProfileRepository.create(profile_data)

    @staticmethod
    def update_profile(user_id: str, profile_data: dict):
        return ProfileRepository.update(user_id, profile_data)