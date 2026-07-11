from app.database.supabase import admin_supabase
from app.repositories.disease_alert_repository import DiseaseAlertRepository


class DiseaseAlertService:

    # Minimum reports required before creating an alert
    ALERT_THRESHOLD = 1

    @staticmethod
    def check_and_create_alert(
        crop_id: str,
        disease_name: str,
        district: str,
        severity: str,
    ):

        # Count reports with the same disease in the same district
        reports = (
            admin_supabase.table("disease_reports")
            .select("id")
            .eq("crop_id", crop_id)
            .eq("disease_name", disease_name)
            .execute()
            .data
        )

        report_count = len(reports)

        # Not enough reports -> no outbreak
        if report_count < DiseaseAlertService.ALERT_THRESHOLD:
            return None

        # Avoid duplicate active alerts
        existing = (
            admin_supabase.table("disease_alerts")
            .select("id")
            .eq("crop_id", crop_id)
            .eq("district", district)
            .eq("disease_name", disease_name)
            .eq("status", "active")
            .execute()
            .data
        )

        if existing:
            return existing[0]

        # Create alert
        alert = DiseaseAlertRepository.create_alert(
            {
                "crop_id": crop_id,
                "district": district,
                "disease_name": disease_name,
                "severity": severity,
                "report_count": report_count,
                "message": (
                    f"{disease_name} outbreak detected in "
                    f"{district}. Please inspect your crop."
                ),
            }
        )

        DiseaseAlertService.notify_farmers(
            alert["id"],
            crop_id,
            district,
        )

        return alert

    @staticmethod
    def notify_farmers(
        alert_id: str,
        crop_id: str,
        district: str,
    ):

        farmers = (
            admin_supabase.table("profiles")
            .select("id")
            .eq("district", district)
            .eq("current_crop_id", crop_id)
            .execute()
            .data
        )

        if not farmers:
            return

        notifications = []

        for farmer in farmers:
            notifications.append(
                {
                    "user_id": farmer["id"],
                    "alert_id": alert_id,
                }
            )

        DiseaseAlertRepository.create_notifications(
            notifications
        )