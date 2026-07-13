from urllib import response

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
    @staticmethod
    def get_crop_name(crop_id: str):
        response = (
            admin_supabase.table("crops")
            .select("crop_name")
            .eq("id", crop_id)
            .single()
            .execute()
        )

        return response.data["crop_name"]

    @staticmethod
    def get_all_crops():
        response = (
            admin_supabase.table("crops")
            .select("id, crop_name, scientific_name, season")
            .execute()
        )
        return response.data