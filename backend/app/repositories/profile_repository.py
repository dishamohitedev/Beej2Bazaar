from urllib import response

from app.database.supabase import admin_supabase


class ProfileRepository:
    @staticmethod
    def get_by_user_id(user_id: str):
        response = (
            admin_supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            return response.data[0]

        return None

    @staticmethod
    def create(profile: dict):
        response = (
            admin_supabase.table("profiles")
            .insert(profile)
            .execute()
        )

        return response.data[0]

    @staticmethod
    def update(user_id: str, profile: dict):
        response = (
            admin_supabase.table("profiles")
            .update(profile)
            .eq("id", user_id)
            .execute()
        )

        return response.data[0]
    @staticmethod
    def get_by_id(user_id: str):
        """
        Fetches a profile by user UUID.
        Returns the profile dict or None if not found.
        Uses a safe query (no .single()) to avoid APIError on missing rows.
        """
        try:
            response = (
                admin_supabase.table("profiles")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None