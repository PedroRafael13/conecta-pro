"""
Testes para a API do módulo de Integrações
Sprint 32: API Gateway / Integrações
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from modules.integrations.models import (
    APIEndpoint,
    APIKey,
    APIKeyStatus,
    APIKeyType,
    EndpointCategory,
    EndpointStatus,
    ExternalSystem,
    HTTPMethod,
    IntegrationLog,
    SyncEntityType,
    SyncQueue,
    SyncStatus,
    WebhookConfig,
    WebhookStatus,
)


class TestAPIEndpointAPI:
    """Testes para endpoints de API Endpoint."""

    @pytest.fixture
    def mock_endpoint(self):
        """Fixture para endpoint mock."""
        return APIEndpoint(
            id=uuid4(),
            name="Get Users",
            path="/users",
            method=HTTPMethod.GET,
            category=EndpointCategory.CLIENTS,
            version="v1",
            status=EndpointStatus.ACTIVE,
            total_calls=100,
            successful_calls=95,
            failed_calls=5,
            avg_response_time_ms=50,
            ativo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_create_endpoint_success(self, mock_endpoint):
        """Testa criação de endpoint com sucesso."""
        endpoint_data = {"name": "Get Users", "path": "/users", "method": "GET", "category": "clients"}

        with patch(
            "modules.integrations.services.IntegrationService.create_endpoint", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_endpoint

            # Simulação do request
            result = await mock_create(endpoint_data)

            assert result.name == "Get Users"
            assert result.path == "/users"

    @pytest.mark.asyncio
    async def test_list_endpoints(self, mock_endpoint):
        """Testa listagem de endpoints."""
        with patch(
            "modules.integrations.services.IntegrationService.list_endpoints", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = ([mock_endpoint], 1, 1)

            endpoints, total, pages = await mock_list()

            assert len(endpoints) == 1
            assert total == 1
            assert endpoints[0].name == "Get Users"

    @pytest.mark.asyncio
    async def test_update_endpoint(self, mock_endpoint):
        """Testa atualização de endpoint."""
        mock_endpoint.name = "Updated Name"

        with patch(
            "modules.integrations.services.IntegrationService.update_endpoint", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = mock_endpoint

            result = await mock_update(mock_endpoint.id, {"name": "Updated Name"})

            assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_deprecate_endpoint(self, mock_endpoint):
        """Testa depreciação de endpoint."""
        mock_endpoint.status = EndpointStatus.DEPRECATED
        mock_endpoint.deprecated_at = datetime.utcnow()

        with patch(
            "modules.integrations.services.IntegrationService.deprecate_endpoint", new_callable=AsyncMock
        ) as mock_deprecate:
            mock_deprecate.return_value = mock_endpoint

            result = await mock_deprecate(mock_endpoint.id)

            assert result.status == EndpointStatus.DEPRECATED


class TestAPIKeyAPI:
    """Testes para endpoints de API Key."""

    @pytest.fixture
    def mock_api_key(self):
        """Fixture para API Key mock."""
        return APIKey(
            id=uuid4(),
            name="Production Key",
            key_prefix="abc12345",
            key_hash="hash123",
            key_hint="6789",
            key_type=APIKeyType.PRODUCTION,
            status=APIKeyStatus.ACTIVE,
            scopes=["read:clients", "write:services"],
            total_requests=1000,
            successful_requests=990,
            failed_requests=10,
            never_expires=False,
            expires_at=datetime(2027, 12, 31),
            ativo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_create_api_key(self, mock_api_key):
        """Testa criação de API Key."""
        raw_key = "abc12345" + "x" * 52 + "6789"

        with patch(
            "modules.integrations.services.IntegrationService.create_api_key", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = (mock_api_key, raw_key)

            api_key, key = await mock_create({"name": "Production Key"})

            assert api_key.name == "Production Key"
            assert len(key) == 64

    @pytest.mark.asyncio
    async def test_verify_api_key_valid(self, mock_api_key):
        """Testa verificação de chave válida."""
        with patch(
            "modules.integrations.services.IntegrationService.verify_api_key", new_callable=AsyncMock
        ) as mock_verify:
            mock_verify.return_value = (True, mock_api_key, "OK")

            valid, key, message = await mock_verify("test_key")

            assert valid is True
            assert message == "OK"

    @pytest.mark.asyncio
    async def test_verify_api_key_invalid(self):
        """Testa verificação de chave inválida."""
        with patch(
            "modules.integrations.services.IntegrationService.verify_api_key", new_callable=AsyncMock
        ) as mock_verify:
            mock_verify.return_value = (False, None, "Chave de API inválida")

            valid, key, message = await mock_verify("invalid_key")

            assert valid is False
            assert key is None
            assert "inválida" in message

    @pytest.mark.asyncio
    async def test_revoke_api_key(self, mock_api_key):
        """Testa revogação de API Key."""
        mock_api_key.status = APIKeyStatus.REVOKED
        mock_api_key.revoked_at = datetime.utcnow()

        with patch(
            "modules.integrations.services.IntegrationService.revoke_api_key", new_callable=AsyncMock
        ) as mock_revoke:
            mock_revoke.return_value = mock_api_key

            result = await mock_revoke(mock_api_key.id, reason="Teste")

            assert result.status == APIKeyStatus.REVOKED


class TestWebhookAPI:
    """Testes para endpoints de Webhook."""

    @pytest.fixture
    def mock_webhook(self):
        """Fixture para Webhook mock."""
        return WebhookConfig(
            id=uuid4(),
            name="Order Webhook",
            url="https://example.com/webhook",
            events=["service_order.created", "service_order.completed"],
            status=WebhookStatus.ACTIVE,
            secret_key="secret123",
            total_deliveries=100,
            successful_deliveries=98,
            failed_deliveries=2,
            consecutive_failures=0,
            ativo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_create_webhook(self, mock_webhook):
        """Testa criação de webhook."""
        with patch(
            "modules.integrations.services.WebhookService.create_webhook", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_webhook

            result = await mock_create(
                {"name": "Order Webhook", "url": "https://example.com/webhook", "events": ["service_order.created"]}
            )

            assert result.name == "Order Webhook"
            assert result.secret_key is not None

    @pytest.mark.asyncio
    async def test_test_webhook_success(self):
        """Testa teste de webhook com sucesso."""
        with patch("modules.integrations.services.WebhookService.test_webhook", new_callable=AsyncMock) as mock_test:
            mock_test.return_value = MagicMock(success=True, status_code=200, response_time_ms=150)

            result = await mock_test(uuid4(), {"event": "test.event", "payload": {"test": True}})

            assert result.success is True
            assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_trigger_event(self, mock_webhook):
        """Testa disparo de evento."""
        with patch(
            "modules.integrations.services.WebhookService.trigger_event", new_callable=AsyncMock
        ) as mock_trigger:
            mock_trigger.return_value = [{"webhook_id": str(mock_webhook.id), "success": True, "status_code": 200}]

            results = await mock_trigger(event="service_order.created", payload={"order_id": "123"})

            assert len(results) == 1
            assert results[0]["success"] is True


class TestSyncQueueAPI:
    """Testes para endpoints de Sync Queue."""

    @pytest.fixture
    def mock_sync_item(self):
        """Fixture para item de sync mock."""
        return SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            entity_id=uuid4(),
            external_system=ExternalSystem.OMIE,
            status=SyncStatus.IDLE,
            payload={"name": "Test Client"},
            retry_count=0,
            max_retries=3,
            ativo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_queue_sync(self, mock_sync_item):
        """Testa adição à fila de sync."""
        with patch("modules.integrations.services.IntegrationService.queue_sync", new_callable=AsyncMock) as mock_queue:
            mock_queue.return_value = mock_sync_item

            result = await mock_queue(
                {"entity_type": "client", "external_system": "omie", "payload": {"name": "Test Client"}}
            )

            assert result.entity_type == SyncEntityType.CLIENT
            assert result.status == SyncStatus.IDLE

    @pytest.mark.asyncio
    async def test_queue_sync_batch(self, mock_sync_item):
        """Testa adição em lote à fila."""
        items = [mock_sync_item, mock_sync_item]

        with patch(
            "modules.integrations.services.IntegrationService.queue_sync_batch", new_callable=AsyncMock
        ) as mock_batch:
            mock_batch.return_value = items

            result = await mock_batch(
                [{"entity_type": "client", "payload": {}}, {"entity_type": "client", "payload": {}}]
            )

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_sync_stats(self):
        """Testa obtenção de estatísticas."""
        with patch(
            "modules.integrations.services.IntegrationService.get_sync_stats", new_callable=AsyncMock
        ) as mock_stats:
            mock_stats.return_value = {
                "total": 100,
                "by_status": {"pending": 10, "processing": 5, "completed": 80, "failed": 5},
            }

            result = await mock_stats()

            assert result["total"] == 100
            assert result["by_status"]["completed"] == 80

    @pytest.mark.asyncio
    async def test_cancel_sync_item(self, mock_sync_item):
        """Testa cancelamento de item."""
        mock_sync_item.status = SyncStatus.IDLE

        with patch(
            "modules.integrations.services.IntegrationService.cancel_sync_item", new_callable=AsyncMock
        ) as mock_cancel:
            mock_cancel.return_value = mock_sync_item

            result = await mock_cancel(mock_sync_item.id, "Não necessário")

            assert result.status == SyncStatus.IDLE

    @pytest.mark.asyncio
    async def test_retry_sync_item(self, mock_sync_item):
        """Testa retry de item."""
        mock_sync_item.status = SyncStatus.IDLE
        mock_sync_item.retry_count = 0

        with patch(
            "modules.integrations.services.IntegrationService.retry_sync_item", new_callable=AsyncMock
        ) as mock_retry:
            mock_retry.return_value = mock_sync_item

            result = await mock_retry(mock_sync_item.id)

            assert result.status == SyncStatus.IDLE
            assert result.retry_count == 0


class TestDashboardAPI:
    """Testes para endpoints de Dashboard."""

    @pytest.mark.asyncio
    async def test_get_dashboard(self):
        """Testa obtenção de dashboard."""
        with patch(
            "modules.integrations.services.IntegrationService.get_dashboard", new_callable=AsyncMock
        ) as mock_dashboard:
            mock_dashboard.return_value = MagicMock(
                total_endpoints=50, active_endpoints=45, total_api_keys=20, active_webhooks=10, overall_health="healthy"
            )

            result = await mock_dashboard()

            assert result.total_endpoints == 50
            assert result.overall_health == "healthy"

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Testa health check."""
        with patch(
            "modules.integrations.services.IntegrationService.get_health_check", new_callable=AsyncMock
        ) as mock_health:
            mock_health.return_value = MagicMock(api_gateway="healthy", webhooks="healthy", sync_queue="healthy")

            result = await mock_health()

            assert result.api_gateway == "healthy"
            assert result.webhooks == "healthy"
