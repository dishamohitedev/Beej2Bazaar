from app.database.supabase import admin_supabase


class CropRepository:

    @staticmethod
    def get_crop(user_id: str):
        response = (
            admin_supabase.table("profiles")
            .select(
                "current_crop_id, growth_stage, sowing_date, expected_harvest"
            )
            .eq("id", user_id)
            .single()
            .execute()
        )

        return response.data

    @staticmethod
    def update_crop(user_id: str, data: dict):
        response = (
            admin_supabase.table("profiles")
            .update(data)
            .eq("id", user_id)
            .execute()
        )

        return response.data[0]
    