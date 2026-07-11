from urllib import response

from app.database.supabase import admin_supabase


class DiseaseRepository:

    @staticmethod
    def save_report(data: dict):
        response = (
            admin_supabase
            .table("disease_reports")
            .insert(data)
            .execute()
        )

        return response.data[0]

    @staticmethod
    def get_history(user_id: str):
        response = (
            admin_supabase
            .table("disease_reports")
            .select(
                "id,disease_name,confidence,status,created_at,image_url"
            )
            .eq("reported_by", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    @staticmethod
    def get_report(user_id: str, report_id: str):
        response = (
        admin_supabase.table("disease_reports")
        .select("*")
        .eq("id", report_id)
        .eq("reported_by", user_id)
        .execute()
    )

        if not response.data:
            return None

        return response.data[0]