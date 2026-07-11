import os
import pytest
from datetime import time, datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies.auth import get_current_user
from app.irrigation.notification_service import NotificationService
from app.irrigation.notification_store import NotificationStore
from app.irrigation.reminder_store import ReminderStore
from app.irrigation.notification_model import Notification

def test_parse_slot_times():
    # Test standard day slot
    start, end = NotificationService.parse_slot_times("08:00 AM - 04:00 PM (Day Slot)")
    assert start == time(8, 0)
    assert end == time(16, 0)

    # Test night slot
    start, end = NotificationService.parse_slot_times("10:00 PM - 06:00 AM (Night Slot)")
    assert start == time(22, 0)
    assert end == time(6, 0)

    # Test custom day slot
    start, end = NotificationService.parse_slot_times("09:00 AM - 05:00 PM (Day Slot)")
    assert start == time(9, 0)
    assert end == time(17, 0)

    # Test malformed/fallback slot
    start, end = NotificationService.parse_slot_times("Invalid Slot String")
    assert start == time(8, 0)
    assert end == time(16, 0)


def test_is_time_in_slot():
    # Day slot: 8:00 AM to 4:00 PM
    start = time(8, 0)
    end = time(16, 0)
    assert NotificationService.is_time_in_slot(time(10, 0), start, end) is True
    assert NotificationService.is_time_in_slot(time(8, 0), start, end) is True
    assert NotificationService.is_time_in_slot(time(16, 0), start, end) is True
    assert NotificationService.is_time_in_slot(time(7, 59), start, end) is False
    assert NotificationService.is_time_in_slot(time(16, 0, 1), start, end) is False

    # Night slot: 10:00 PM to 6:00 AM (spans midnight)
    start_night = time(22, 0)
    end_night = time(6, 0)
    assert NotificationService.is_time_in_slot(time(23, 0), start_night, end_night) is True
    assert NotificationService.is_time_in_slot(time(1, 0), start_night, end_night) is True
    assert NotificationService.is_time_in_slot(time(22, 0), start_night, end_night) is True
    assert NotificationService.is_time_in_slot(time(6, 0), start_night, end_night) is True
    assert NotificationService.is_time_in_slot(time(21, 59), start_night, end_night) is False
    assert NotificationService.is_time_in_slot(time(6, 1), start_night, end_night) is False
    assert NotificationService.is_time_in_slot(time(12, 0), start_night, end_night) is False


def test_notification_store(tmp_path):
    mock_notif_file = os.path.join(tmp_path, "test_notifications.json")
    with patch("app.irrigation.notification_store.STORE_FILE", mock_notif_file):
        # Fresh store checks
        assert len(NotificationStore.get_notifications("user123")) == 0
        assert NotificationStore.has_notification_been_sent("user123", "2026-07-11", "electricity_available") is False

        # Add notification
        notif = NotificationStore.add_notification(
            user_id="user123",
            title="💧 Test Title",
            message="Test message body",
            date_str="2026-07-11",
            type_str="electricity_available"
        )
        assert notif["user_id"] == "user123"
        assert notif["status"] == "unread"
        assert notif["date"] == "2026-07-11"

        # Check has been sent
        assert NotificationStore.has_notification_been_sent("user123", "2026-07-11", "electricity_available") is True
        assert NotificationStore.has_notification_been_sent("user123", "2026-07-12", "electricity_available") is False

        # Retrieve user notifications
        notifs = NotificationStore.get_notifications("user123")
        assert len(notifs) == 1
        assert notifs[0]["id"] == notif["id"]

        # Mark as read
        updated = NotificationStore.mark_as_read("user123", notif["id"])
        assert updated is not None
        assert updated["status"] == "read"

        # Fetch again to verify persistence
        notifs_updated = NotificationStore.get_notifications("user123")
        assert notifs_updated[0]["status"] == "read"


def test_notification_service_trigger(tmp_path):
    mock_notif_file = os.path.join(tmp_path, "test_notifications.json")
    mock_reminders_file = os.path.join(tmp_path, "test_reminders.json")

    # Setup mock reminder today in pending status
    mock_user_id = "user-abc"
    mock_date = "2026-07-11"

    with patch("app.irrigation.notification_store.STORE_FILE", mock_notif_file), \
         patch("app.irrigation.reminder_store.STORE_FILE", mock_reminders_file):

        ReminderStore.update_reminder(mock_user_id, mock_date, {
            "status": "pending",
            "water_mm": 6.2,
            "electricity_slot": "08:00 AM - 04:00 PM (Day Slot)",
            "pump_run_time_str": "1 hr 30 mins"
        })

        # Test Scenario A: Simulated time before slot (07:00 AM)
        sim_time_before = datetime(2026, 7, 11, 7, 0)
        notif_before = NotificationService.check_and_trigger_notifications(mock_user_id, simulated_time=sim_time_before)
        assert notif_before is None
        assert NotificationStore.has_notification_been_sent(mock_user_id, mock_date, "electricity_available") is False

        # Test Scenario B: Simulated time during slot (09:00 AM) - Mocking Profile with Marathi language
        sim_time_during = datetime(2026, 7, 11, 9, 0)
        mock_profile = {"id": mock_user_id, "language": "Marathi"}

        with patch("app.repositories.onboarding_repository.OnboardingRepository.get_profile", return_value=mock_profile):
            notif_during = NotificationService.check_and_trigger_notifications(mock_user_id, simulated_time=sim_time_during)
            assert notif_during is not None
            assert notif_during["title"] == "💧 सिंचन संदेश"
            assert "वीज उपलब्ध आहे" in notif_during["message"]
            assert "6.2" in notif_during["message"]

        # Test Scenario C: Simulated time subsequent check inside slot (10:00 AM)
        sim_time_later = datetime(2026, 7, 11, 10, 0)
        notif_later = NotificationService.check_and_trigger_notifications(mock_user_id, simulated_time=sim_time_later)
        assert notif_later is None  # Should not trigger again (duplicate prevention)


def test_notification_router_endpoints(tmp_path):
    class MockUser:
        id = "mock-user-123"
        email = "mockuser@beejbazaar.com"
        user_metadata = {"role": "farmer", "name": "Mock Farmer"}

    app.dependency_overrides[get_current_user] = lambda: MockUser()
    client = TestClient(app)

    mock_notif_file = os.path.join(tmp_path, "test_router_notifications.json")
    mock_reminders_file = os.path.join(tmp_path, "test_router_reminders.json")

    mock_profile = {
        "id": "mock-user-123",
        "language": "English",
        "state": "Maharashtra"
    }

    with patch("app.irrigation.notification_store.STORE_FILE", mock_notif_file), \
         patch("app.irrigation.reminder_store.STORE_FILE", mock_reminders_file), \
         patch("app.repositories.onboarding_repository.OnboardingRepository.get_profile", return_value=mock_profile):
        
        # 1. Initialize today's reminder as pending
        today_str = datetime.now().strftime("%Y-%m-%d")
        ReminderStore.update_reminder("mock-user-123", today_str, {
            "status": "pending",
            "water_mm": 4.5,
            "electricity_slot": "08:00 AM - 04:00 PM (Day Slot)",
            "pump_run_time_str": "1 hr 15 mins"
        })

        # 2. Test Router GET notifications (should be empty initially)
        res_get = client.get("/api/notifications")
        assert res_get.status_code == 200
        assert len(res_get.json()) == 0

        # 3. Test Router POST check notification with simulated time BEFORE slot starts
        res_check_before = client.post(f"/api/notifications/check?simulated_time={today_str}T07:00:00")
        assert res_check_before.status_code == 200
        assert res_check_before.json()["triggered"] is False

        # 4. Test Router POST check notification with simulated time DURING slot starts
        res_check_during = client.post(f"/api/notifications/check?simulated_time={today_str}T08:30:00")
        assert res_check_during.status_code == 200
        assert res_check_during.json()["triggered"] is True
        notif_data = res_check_during.json()["notification"]
        assert notif_data["title"] == "💧 Irrigation Alert"
        assert notif_data["status"] == "unread"

        # 5. Test Router GET notifications (should have 1 notification now)
        res_get_after = client.get("/api/notifications")
        assert res_get_after.status_code == 200
        assert len(res_get_after.json()) == 1

        # 6. Test Router POST mark as read
        notif_id = notif_data["id"]
        res_read = client.post(f"/api/notifications/{notif_id}/read")
        assert res_read.status_code == 200
        assert res_read.json()["status"] == "read"

        # 7. Try marking invalid notification as read
        res_read_invalid = client.post("/api/notifications/invalid-id/read")
        assert res_read_invalid.status_code == 404
