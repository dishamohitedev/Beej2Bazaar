import uuid

from app.database.supabase import admin_supabase


class StorageService:

    BUCKET_NAME = "disease-images"

    @staticmethod
    def upload_disease_image(
        user_id: str,
        image_bytes: bytes,
        content_type: str,
    ) -> str:

        extension = content_type.split("/")[-1]

        filename = f"{uuid.uuid4()}.{extension}"

        file_path = f"{user_id}/{filename}"

        admin_supabase.storage.from_(StorageService.BUCKET_NAME).upload(
            path=file_path,
            file=image_bytes,
            file_options={
                "content-type": content_type,
                "upsert": False,
            },
        )

        public_url = (
            admin_supabase.storage
            .from_(StorageService.BUCKET_NAME)
            .get_public_url(file_path)
        )

        return public_url