from fastapi import HTTPException, UploadFile

from app.repositories.crop_repository import CropRepository
from app.repositories.disease_repository import DiseaseRepository
from app.repositories.profile_repository import ProfileRepository

from app.services.gemini_disease_service import GeminiDiseaseService
from app.services.storage_service import StorageService


class DiseaseService:

    @staticmethod
    async def detect(user_id: str, image: UploadFile):

        # Get user profile
        profile = ProfileRepository.get_by_id(user_id)

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        # Ensure current crop is selected
        if not profile.get("current_crop_id"):
            raise HTTPException(
                status_code=400,
                detail="No current crop selected"
            )

        # Get crop name
        crop_name = CropRepository.get_crop_name(
            profile["current_crop_id"]
        )

        # Read uploaded image
        image_bytes = await image.read()

        # Upload image to Supabase Storage
        image_url = StorageService.upload_disease_image(
            user_id=user_id,
            image_bytes=image_bytes,
            content_type=image.content_type,
        )

        # Analyze image using Gemini
        ai_response = GeminiDiseaseService.detect_disease(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            crop_name=crop_name,
            growth_stage=profile.get("growth_stage"),
            soil_type=profile.get("soil_type"),
            irrigation=profile.get("irrigation"),
            language=profile.get("language"),
        )

        # Save report in database
        report = DiseaseRepository.save_report(
            {
                "reported_by": user_id,
                "crop_id": profile["current_crop_id"],
                "image_url": image_url,
                "disease_name": ai_response["disease_name"],
                "confidence": ai_response["confidence"],
                "ai_response": ai_response,
                "status": "completed",
            }
        )

        # Return API response
        return {
            "report_id": report["id"],
            **ai_response,
        }

    @staticmethod
    def get_history(user_id: str):
        return DiseaseRepository.get_history(user_id)

    @staticmethod
    def get_report(user_id: str, report_id: str):

        report = DiseaseRepository.get_report(
            user_id,
            report_id
        )

        if not report:
            raise HTTPException(
            status_code=404,
            detail="Disease report not found"
        )

        return report