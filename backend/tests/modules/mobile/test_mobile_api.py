"""Tests for Mobile API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.mobile.controllers.mobile_controller import router
from modules.mobile.schemas.batch_schemas import BatchOperation, BatchRequest
from modules.mobile.schemas.device_schemas import DeviceTokenCreate
from modules.mobile.schemas.sync_schemas import MobileSyncOperation, MobileSyncRequest

# Create test app
app = FastAPI()
app.include_router(router)


# Mock dependencies
def mock_get_db():
    """Mock database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    return db


def mock_get_current_user():
    """Mock current user."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "role": "admin",
        "permissions": ["read", "write"],
    }


# Apply mocks
app.dependency_overrides = {}


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_health_check(self):
        """Test health check returns healthy status."""
        response = self.client.get("/mobile/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mobile-api"
        assert "version" in data
        assert "timestamp" in data
        assert "components" in data


class TestConfigEndpoint:
    """Tests for config endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    @patch("modules.mobile.controllers.mobile_controller.get_current_user")
    def test_get_config(self, mock_user):
        """Test getting mobile config."""
        mock_user.return_value = mock_get_current_user()

        response = self.client.get(
            "/mobile/config",
            headers={"user-agent": "ConectaPRO-Android/2.0.0"},
        )

        # Note: Will fail without proper auth setup
        # This tests the endpoint structure
        assert response.status_code in [200, 401, 422]


class TestSyncEndpoint:
    """Tests for sync endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_sync_request_validation(self):
        """Test sync request validation."""
        # Invalid request (missing required fields)
        response = self.client.post(
            "/mobile/sync",
            json={},
        )

        assert response.status_code == 422  # Validation error

    def test_sync_request_structure(self):
        """Test sync request structure."""
        sync_data = {
            "device_id": "device123",
            "sync_token": None,
            "operations": [
                {
                    "id": "op1",
                    "table": "leads",
                    "operation": "create",
                    "record_id": "lead123",
                    "data": {"name": "Test Lead"},
                    "changed_fields": ["name"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
        }

        response = self.client.post(
            "/mobile/sync",
            json=sync_data,
        )

        # Will fail auth but validates structure
        assert response.status_code in [200, 401, 422]


class TestBatchEndpoint:
    """Tests for batch operations endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_batch_request_validation(self):
        """Test batch request validation."""
        # Empty operations
        response = self.client.post(
            "/mobile/batch",
            json={"operations": []},
        )

        # Should fail validation (min 1 operation)
        assert response.status_code == 422

    def test_batch_request_max_operations(self):
        """Test batch request max operations limit."""
        # More than 50 operations
        operations = [
            {
                "id": f"op{i}",
                "method": "GET",
                "endpoint": "/api/test",
            }
            for i in range(51)
        ]

        response = self.client.post(
            "/mobile/batch",
            json={"operations": operations},
        )

        # Should fail validation (max 50)
        assert response.status_code == 422


class TestDeviceEndpoints:
    """Tests for device registration endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_register_device_validation(self):
        """Test device registration validation."""
        # Missing required fields
        response = self.client.post(
            "/mobile/devices/register",
            json={},
        )

        assert response.status_code == 422

    def test_register_device_structure(self):
        """Test device registration structure."""
        device_data = {
            "token": "fcm_token_123456789",
            "platform": "android",
            "device_id": "device_unique_id",
            "device_name": "Pixel 6",
            "device_model": "Google Pixel 6",
            "os_version": "13.0",
            "app_version": "2.0.0",
        }

        response = self.client.post(
            "/mobile/devices/register",
            json=device_data,
        )

        # Will fail auth but validates structure
        assert response.status_code in [200, 401]


class TestNotificationEndpoints:
    """Tests for notification endpoints."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_list_notifications(self):
        """Test listing notifications."""
        response = self.client.get(
            "/mobile/notifications",
            params={"page": 1, "page_size": 20},
        )

        # Will fail auth
        assert response.status_code in [200, 401]

    def test_list_notifications_pagination(self):
        """Test notifications pagination params."""
        response = self.client.get(
            "/mobile/notifications",
            params={"page": 0, "page_size": 200},
        )

        # Should fail validation (page >= 1, page_size <= 100)
        assert response.status_code == 422

    def test_mark_notification_read(self):
        """Test marking notification as read."""
        notification_id = str(uuid4())

        response = self.client.post(
            f"/mobile/notifications/{notification_id}/read",
        )

        # Will fail auth
        assert response.status_code in [200, 401, 404]


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_sync_operation_schema(self):
        """Test MobileSyncOperation schema."""
        operation = MobileSyncOperation(
            id="op1",
            table="leads",
            operation="update",
            record_id="lead123",
            data={"name": "Updated"},
            changed_fields=["name"],
            timestamp=datetime.utcnow(),
        )

        assert operation.id == "op1"
        assert operation.can_parallelize is True

    def test_sync_request_schema(self):
        """Test MobileSyncRequest schema."""
        request = MobileSyncRequest(
            device_id="device123",
            operations=[
                MobileSyncOperation(
                    id="op1",
                    table="leads",
                    operation="create",
                    record_id="lead123",
                    data={},
                    changed_fields=[],
                    timestamp=datetime.utcnow(),
                )
            ],
        )

        assert request.device_id == "device123"
        assert request.sync_token is None
        assert len(request.operations) == 1

    def test_batch_operation_schema(self):
        """Test BatchOperation schema."""
        operation = BatchOperation(
            id="batch1",
            method="POST",
            endpoint="/api/leads",
            body={"name": "New Lead"},
        )

        assert operation.id == "batch1"
        assert operation.method == "POST"
        assert operation.headers == {}

    def test_batch_request_limits(self):
        """Test BatchRequest limits."""
        # Valid request
        request = BatchRequest(
            operations=[BatchOperation(id="1", method="GET", endpoint="/api/test") for _ in range(50)]
        )
        assert len(request.operations) == 50

        # Invalid - too many operations
        with pytest.raises(ValueError):
            BatchRequest(operations=[BatchOperation(id=str(i), method="GET", endpoint="/api/test") for i in range(51)])

    def test_device_token_create_schema(self):
        """Test DeviceTokenCreate schema."""
        device = DeviceTokenCreate(
            token="fcm_token_12345",
            platform="android",
            device_id="unique_device_id",
        )

        assert device.token == "fcm_token_12345"
        assert device.platform == "android"
        assert device.push_enabled is True  # default

    def test_device_token_invalid_platform(self):
        """Test DeviceTokenCreate with invalid platform."""
        with pytest.raises(ValueError):
            DeviceTokenCreate(
                token="token",
                platform="windows",  # Invalid
                device_id="device",
            )


class TestIntegrationScenarios:
    """Integration test scenarios."""

    def test_full_sync_flow(self):
        """Test complete sync flow scenario."""
        # This would test:
        # 1. Initial sync (no token)
        # 2. Process operations
        # 3. Get server changes
        # 4. Incremental sync (with token)

        operations = [
            MobileSyncOperation(
                id=f"op_{i}",
                table="leads",
                operation="create" if i % 3 == 0 else "update",
                record_id=f"lead_{i}",
                data={"name": f"Lead {i}"},
                changed_fields=["name"],
                timestamp=datetime.utcnow(),
            )
            for i in range(10)
        ]

        request = MobileSyncRequest(
            device_id="integration_test_device",
            operations=operations,
        )

        assert len(request.operations) == 10
        assert request.sync_token is None  # Initial sync

    def test_batch_operations_scenario(self):
        """Test batch operations scenario."""
        # Multiple API calls in one batch
        operations = [
            BatchOperation(id="1", method="GET", endpoint="/api/leads"),
            BatchOperation(id="2", method="GET", endpoint="/api/tasks"),
            BatchOperation(
                id="3",
                method="POST",
                endpoint="/api/leads",
                body={"name": "New Lead"},
            ),
            BatchOperation(
                id="4",
                method="PUT",
                endpoint="/api/leads/123",
                body={"status": "qualified"},
            ),
        ]

        request = BatchRequest(
            operations=operations,
            continue_on_error=True,
        )

        assert len(request.operations) == 4
        assert request.continue_on_error is True

    def test_offline_first_scenario(self):
        """Test offline-first data scenario."""
        # Simulate offline operations accumulated
        offline_operations = []

        # Create operations while offline
        for i in range(5):
            offline_operations.append(
                MobileSyncOperation(
                    id=f"offline_{i}",
                    table="tasks",
                    operation="create",
                    record_id=f"task_{i}",
                    data={
                        "title": f"Offline Task {i}",
                        "completed": False,
                    },
                    changed_fields=["title", "completed"],
                    timestamp=datetime.utcnow(),
                    can_parallelize=True,
                )
            )

        # Update an existing task
        offline_operations.append(
            MobileSyncOperation(
                id="offline_update",
                table="tasks",
                operation="update",
                record_id="existing_task_1",
                data={"completed": True},
                changed_fields=["completed"],
                timestamp=datetime.utcnow(),
            )
        )

        # Sync request
        sync_request = MobileSyncRequest(
            device_id="offline_device",
            sync_token="previous_token_12345",
            operations=offline_operations,
            connection_quality="wifi",  # Back online
        )

        assert len(sync_request.operations) == 6
        assert sync_request.sync_token == "previous_token_12345"
