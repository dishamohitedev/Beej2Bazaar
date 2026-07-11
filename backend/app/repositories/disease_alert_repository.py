from app.database.supabase import admin_supabase



class DiseaseAlertRepository:

    TABLE = "disease_alerts"
    NOTIFICATION_TABLE = "disease_alert_notifications"

    @staticmethod
    def create_alert(data: dict):

        return (
            admin_supabase.table(DiseaseAlertRepository.TABLE)
            .insert(data)
            .execute()
            .data[0]
        )

    @staticmethod
    def create_notifications(data: list):

        return (
            admin_supabase.table(DiseaseAlertRepository.NOTIFICATION_TABLE)
            .insert(data)
            .execute()
            .data
        )

    @staticmethod
    def get_active_alerts():

        return (
            admin_supabase.table(DiseaseAlertRepository.TABLE)
            .select("*")
            .eq("status", "active")
            .order("created_at", desc=True)
            .execute()
            .data
        )

    @staticmethod
    def get_alert(alert_id: str):

        result = (
            admin_supabase.table(DiseaseAlertRepository.TABLE)
            .select("*")
            .eq("id", alert_id)
            .execute()
            .data
        )

        return result[0] if result else None

    @staticmethod
    def get_user_notifications(user_id: str):

        return (
            admin_supabase.table(DiseaseAlertRepository.NOTIFICATION_TABLE)
            .select(
                """
                id,
                is_read,
                created_at,
                disease_alerts(*)
                """
            )
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
            .data
        )

    @staticmethod
    def mark_as_read(notification_id: str):

        return (
            admin_supabase.table(DiseaseAlertRepository.NOTIFICATION_TABLE)
            .update({"is_read": True})
            .eq("id", notification_id)
            .execute()
            .data
        )
    
    @staticmethod
    def get_unread_count(user_id: str):

        response = (
            admin_supabase.table(DiseaseAlertRepository.NOTIFICATION_TABLE)
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("is_read", False)
            .execute()
    )

        return response.count or 0