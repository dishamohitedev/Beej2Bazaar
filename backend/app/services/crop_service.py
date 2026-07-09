from app.repositories.crop_repository import CropRepository


class CropService:

    @staticmethod
    def get_crop(user_id: str):
        return CropRepository.get_crop(user_id)

    @staticmethod
    def update_crop(user_id: str, data: dict):
        return CropRepository.update_crop(user_id, data)

    @staticmethod
    def harvest_crop(user_id: str):
        return CropRepository.update_crop(
            user_id,
            {
                "current_crop_id": None,
                "growth_stage": None,
                "sowing_date": None,
                "expected_harvest": None,
            },
        )