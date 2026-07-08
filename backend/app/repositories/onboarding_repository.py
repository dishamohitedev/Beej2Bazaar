from app.database.supabase import admin_supabase


class OnboardingRepository:

    @staticmethod
    def update_profile(user_id: str, data: dict):

        response = (
            admin_supabase.table("profiles")
            .update(data)
            .eq("id", user_id)
            .execute()
        )

        return response.data[0]

    @staticmethod
    def get_profile(user_id: str):

        response = (
            admin_supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )

        return response.data