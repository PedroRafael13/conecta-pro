"""Tests for Mobile Services."""

import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.mobile.models.push_notification import (
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from modules.mobile.models.sync_queue import (
    ConflictResolution,
    SyncOperationType,
    SyncStatus,
)
from modules.mobile.schemas.notification_schemas import (
    BroadcastNotificationRequest,
    PushNotificationCreate,
)
from modules.mobile.schemas.sync_schemas import (
    MobileSyncOperation,
    MobileSyncRequest,
)
from modules.mobile.services.mobile_metrics import MobileMetrics, get_metrics
from modules.mobile.services.mobile_security import MobileSecurity, RateLimitExceededError
from modules.mobile.services.offline_sync_manager import OfflineSyncManager
from modules.mobile.services.push_notification_service import PushNotificationService


class TestPushNotificationService:
    """Tests for PushNotificationService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = PushNotificationService(
            fcm_credentials=None,
            apns_credentials=None,
            default_ttl=86400,
        )

    @pytest.mark.asyncio
    async def test_send_notification_no_tokens(self):
        """Test sending notification with no device tokens."""
        db = AsyncMock()
        db.execute = AsyncMock(
            return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
        )
        db.commit = AsyncMock()

        notification_data = PushNotificationCreate(
            user_id=1,
            title="Test",
            body="Test notification",
        )

        result = await self.service.send_notification(db, notification_data)

        assert result.status == NotificationStatus.FAILED
        assert "No active device tokens" in result.error_message

    @pytest.mark.asyncio
    async def test_send_fcm_simulation(self):
        """Test FCM send simulation (no credentials)."""
        mock_token = MagicMock()
        mock_token.platform = "android"
        mock_token.token = "test_token"

        mock_notification = MagicMock()
        mock_notification.title = "Test"
        mock_notification.body = "Body"
        mock_notification.data_payload = {}
        mock_notification.priority = NotificationPriority.NORMAL
        mock_notification.image_url = None
        mock_notification.collapse_key = None
        mock_notification.ttl_seconds = 86400

        result = await self.service._send_fcm(mock_token, mock_notification)

        assert result is True
        assert mock_notification.external_id.startswith("fcm_sim_")

    @pytest.mark.asyncio
    async def test_send_apns_simulation(self):
        """Test APNs send simulation (no credentials)."""
        mock_token = MagicMock()
        mock_token.platform = "ios"
        mock_token.token = "test_token"

        mock_notification = MagicMock()
        mock_notification.title = "Test"
        mock_notification.body = "Body"
        mock_notification.data_payload = {}
        mock_notification.category = None
        mock_notification.thread_id = None
        mock_notification.image_url = None

        result = await self.service._send_apns(mock_token, mock_notification)

        assert result is True
        assert mock_notification.external_id.startswith("apns_sim_")

    @pytest.mark.asyncio
    async def test_mark_as_delivered(self):
        """Test marking notification as delivered."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(rowcount=1))
        db.commit = AsyncMock()

        notification_id = uuid.uuid4()

        result = await self.service.mark_as_delivered(db, notification_id)

        assert result is True
        db.execute.assert_called_once()
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_as_read(self):
        """Test marking notification as read."""
        db = AsyncMock()
        db.execute = AsyncMock(return_value=MagicMock(rowcount=1))
        db.commit = AsyncMock()

        notification_id = uuid.uuid4()

        result = await self.service.mark_as_read(db, notification_id)

        assert result is True


class TestOfflineSyncManager:
    """Tests for OfflineSyncManager."""

    def setup_method(self):
        """Setup test fixtures."""
        self.manager = OfflineSyncManager(
            max_operations_per_sync=100,
            max_server_changes=500,
            conflict_window_seconds=300,
        )

    def test_syncable_tables_config(self):
        """Test syncable tables configuration."""
        assert "leads" in self.manager.SYNCABLE_TABLES
        assert "tasks" in self.manager.SYNCABLE_TABLES

        leads_config = self.manager.SYNCABLE_TABLES["leads"]
        assert leads_config["conflict_resolution"] == ConflictResolution.LAST_WRITE_WINS

        tasks_config = self.manager.SYNCABLE_TABLES["tasks"]
        assert tasks_config["conflict_resolution"] == ConflictResolution.MERGE

    def test_generate_sync_token(self):
        """Test sync token generation."""
        token1 = self.manager._generate_sync_token(1, datetime.utcnow())
        token2 = self.manager._generate_sync_token(1, datetime.utcnow())

        assert len(token1) == 32
        assert len(token2) == 32
        assert token1 != token2  # Should be unique

    def test_auto_merge_success(self):
        """Test automatic merge of non-conflicting changes."""

        # Fields changed in both with same value - no conflict
        merged = self.manager._auto_merge(
            {"status": "active"},
            {"status": "active", "phone": "123"},
        )

        assert merged is not None
        assert merged["status"] == "active"

    def test_auto_merge_conflict(self):
        """Test automatic merge failure on conflicting changes."""
        client_data = {"name": "Client Name"}
        server_data = {"name": "Server Name"}

        merged = self.manager._auto_merge(client_data, server_data)

        assert merged is None  # Conflict detected

    @pytest.mark.asyncio
    async def test_process_sync(self):
        """Test sync processing."""
        db = AsyncMock()

        # Mock session query
        mock_session = MagicMock()
        mock_session.sync_token = "old_token"
        mock_session.last_sync_at = datetime.utcnow() - timedelta(hours=1)

        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_session)))
        db.flush = AsyncMock()
        db.commit = AsyncMock()

        sync_request = MobileSyncRequest(
            device_id="device123",
            sync_token="old_token",
            operations=[
                MobileSyncOperation(
                    id="op1",
                    table="leads",
                    operation="update",
                    record_id="lead123",
                    data={"name": "Updated"},
                    changed_fields=["name"],
                    timestamp=datetime.utcnow(),
                )
            ],
        )

        response = await self.manager.process_sync(db, 1, sync_request)

        assert response.user_id == 1
        assert len(response.operations) == 1
        assert response.new_sync_token is not None
        assert len(response.new_sync_token) == 32


class TestMobileSecurity:
    """Tests for MobileSecurity."""

    def setup_method(self):
        """Setup test fixtures."""
        self.security = MobileSecurity(
            api_key_secret="test_secret_key",
            enable_strict_mode=False,
            allow_rooted_devices=True,
        )

    def test_generate_api_key(self):
        """Test API key generation."""
        key = self.security.generate_mobile_api_key("app_v1")

        assert "." in key
        parts = key.split(".")
        assert parts[0] == "app_v1"
        assert len(parts[1]) == 16

    def test_validate_api_key_valid(self):
        """Test validation of valid API key."""
        key = self.security.generate_mobile_api_key("test_key_id")

        # Call sync version for testing
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(self.security._validate_api_key(key))

        assert result is True

    def test_validate_api_key_invalid(self):
        """Test validation of invalid API key."""
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(self.security._validate_api_key("invalid.key"))

        assert result is False

    def test_validate_api_key_empty(self):
        """Test validation of empty API key."""
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(self.security._validate_api_key(None))

        assert result is False

    def test_rate_limit_check_success(self):
        """Test rate limit check passes."""
        import asyncio

        # First request should pass
        result = asyncio.get_event_loop().run_until_complete(self.security._check_rate_limit("device:test", "default"))

        assert result is True

    def test_rate_limit_check_exceeded(self):
        """Test rate limit exceeded."""
        import asyncio

        # Exhaust rate limit
        for _ in range(100):  # default is 100 req/min
            asyncio.get_event_loop().run_until_complete(self.security._check_rate_limit("device:exceeded", "default"))

        # 101st request should fail
        result = asyncio.get_event_loop().run_until_complete(
            self.security._check_rate_limit("device:exceeded", "default")
        )

        assert result is False

    def test_suspicious_ua_detection(self):
        """Test suspicious user agent detection."""
        suspicious_request = MagicMock()
        suspicious_request.headers = {"user-agent": "python-requests/2.28"}

        assert self.security._is_suspicious_ua(suspicious_request) is True

        normal_request = MagicMock()
        normal_request.headers = {"user-agent": "ConectaPRO-Android/2.0"}

        assert self.security._is_suspicious_ua(normal_request) is False

    def test_calculate_security_level_high(self):
        """Test high security level calculation."""
        headers = {
            "is_rooted": False,
            "is_emulator": False,
            "app_signature": "valid",
            "device_fingerprint": "fingerprint123",
            "install_source": "play_store",
        }

        level = self.security._calculate_security_level(headers)

        assert level == "high"

    def test_calculate_security_level_low(self):
        """Test low security level calculation."""
        headers = {
            "is_rooted": True,
            "is_emulator": True,
            "app_signature": None,
            "device_fingerprint": None,
            "install_source": "sideload",
        }

        level = self.security._calculate_security_level(headers)

        assert level in ["low", "critical"]

    def test_generate_request_signature(self):
        """Test request signature generation."""
        signature = self.security.generate_request_signature(
            method="POST",
            path="/api/mobile/sync",
            timestamp="1234567890",
            nonce="abc123",
        )

        assert len(signature) == 64  # SHA256 hex length

    def test_security_recommendations(self):
        """Test security recommendations generation."""
        recommendations = self.security.get_security_recommendations(
            security_level="low",
            security_headers={
                "is_rooted": True,
                "is_emulator": False,
                "app_signature": None,
                "install_source": "sideload",
            },
        )

        assert len(recommendations) > 0
        assert any("rooted" in r.lower() for r in recommendations)


class TestMobileMetrics:
    """Tests for MobileMetrics."""

    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = MobileMetrics(
            flush_interval_seconds=60,
            max_buffer_size=1000,
        )

    def teardown_method(self):
        """Reset metrics after each test."""
        self.metrics.reset()

    def test_record_request(self):
        """Test recording request metrics."""
        self.metrics.record_request(
            endpoint="/api/mobile/sync",
            method="POST",
            status_code=200,
            response_time_ms=150.5,
            response_size_bytes=1024,
            compressed=True,
            device_type="mobile",
            platform="android",
            connection_type="4g",
        )

        stats = self.metrics.get_endpoint_stats()
        assert "POST:/api/mobile/sync" in stats
        assert stats["POST:/api/mobile/sync"]["count"] == 1

    def test_record_multiple_requests(self):
        """Test recording multiple requests."""
        for i in range(10):
            self.metrics.record_request(
                endpoint="/api/test",
                method="GET",
                status_code=200 if i < 8 else 500,
                response_time_ms=100 + i,
                response_size_bytes=500,
            )

        stats = self.metrics.get_endpoint_stats()
        assert stats["GET:/api/test"]["count"] == 10
        assert stats["GET:/api/test"]["error_rate"] == 20.0  # 2/10 errors

    def test_record_sync(self):
        """Test recording sync metrics."""
        self.metrics.record_sync(
            user_id=1,
            device_id="device123",
            operations_sent=10,
            operations_received=5,
            conflicts=2,
            duration_ms=500,
            data_size_bytes=2048,
        )

        device_stats = self.metrics.get_device_stats()
        assert "device12..." in device_stats
        assert device_stats["device12..."]["syncs"] == 1

    def test_record_push_metrics(self):
        """Test recording push notification metrics."""
        notification_id = "notif_123"

        self.metrics.record_push_sent(
            notification_id=notification_id,
            user_id=1,
            platform="android",
        )

        self.metrics.record_push_delivered(
            notification_id=notification_id,
            delivery_time_ms=250.0,
        )

        self.metrics.record_push_read(notification_id=notification_id)

        push_stats = self.metrics.get_push_stats()
        assert push_stats["total_sent"] == 1
        assert push_stats["total_delivered"] == 1
        assert push_stats["total_read"] == 1
        assert push_stats["delivery_rate"] == 100.0

    def test_connection_stats(self):
        """Test connection-based statistics."""
        # Record requests for different connection types
        for conn in ["wifi", "4g", "3g"]:
            for _ in range(5):
                self.metrics.record_request(
                    endpoint="/api/test",
                    method="GET",
                    status_code=200,
                    response_time_ms=100 if conn == "wifi" else 300,
                    response_size_bytes=500,
                    connection_type=conn,
                )

        conn_stats = self.metrics.get_connection_stats()

        assert "wifi" in conn_stats
        assert "4g" in conn_stats
        assert conn_stats["wifi"]["requests"] == 5

    def test_get_summary(self):
        """Test getting metrics summary."""
        for i in range(20):
            self.metrics.record_request(
                endpoint=f"/api/endpoint{i % 3}",
                method="GET",
                status_code=200,
                response_time_ms=100,
                response_size_bytes=500,
                device_type="mobile",
                connection_type="4g",
            )

        summary = self.metrics.get_summary()

        assert summary["total_requests"] == 20
        assert summary["endpoints_count"] == 3
        assert "mobile" in summary["device_types"]

    def test_reset(self):
        """Test metrics reset."""
        self.metrics.record_request(
            endpoint="/api/test",
            method="GET",
            status_code=200,
            response_time_ms=100,
            response_size_bytes=500,
        )

        self.metrics.reset()

        stats = self.metrics.get_endpoint_stats()
        assert len(stats) == 0

    def test_get_metrics_singleton(self):
        """Test get_metrics returns singleton."""
        metrics1 = get_metrics()
        metrics2 = get_metrics()

        assert metrics1 is metrics2
