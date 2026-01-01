"""
Testes para os Services do módulo de Integrações
Sprint 32: API Gateway / Integrações
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from modules.integrations.models import (
    APIEndpoint,
    APIKey,
    WebhookConfig,
    IntegrationLog,
    SyncQueue,
    HTTPMethod,
    EndpointStatus,
    APIKeyStatus,
    WebhookStatus,
    SyncStatus,
    SyncEntityType,
    ExternalSystem,
)
from modules.integrations.services import IntegrationService, WebhookService
from modules.integrations.schemas import (
    APIEndpointCreate,
    APIKeyCreate,
    WebhookConfigCreate,
    SyncQueueCreate,
)


class TestIntegrationService:
    """Testes para IntegrationService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para o serviço."""
        return IntegrationService(mock_db)

    @pytest.mark.asyncio
    async def test_create_endpoint(self, service):
        """Testa criação de endpoint."""
        with patch.object(
            service.repository,
            'get_endpoint_by_path_method',
            new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            with patch.object(
                service.repository,
                'create_endpoint',
                new_callable=AsyncMock
            ) as mock_create:
                endpoint = APIEndpoint(
                    id=uuid4(),
                    name="Test",
                    path="/test",
                    method=HTTPMethod.GET
                )
                mock_create.return_value = endpoint

                data = APIEndpointCreate(
                    name="Test",
                    path="/test",
                    method=HTTPMethod.GET
                )

                result = await service.create_endpoint(data)

                assert result.name == "Test"
                mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_endpoint_duplicate(self, service):
        """Testa criação de endpoint duplicado."""
        with patch.object(
            service.repository,
            'get_endpoint_by_path_method',
            new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = APIEndpoint(
                id=uuid4(),
                name="Existing",
                path="/test",
                method=HTTPMethod.GET
            )

            data = APIEndpointCreate(
                name="Test",
                path="/test",
                method=HTTPMethod.GET
            )

            with pytest.raises(ValueError, match="já existe"):
                await service.create_endpoint(data)

    @pytest.mark.asyncio
    async def test_create_api_key(self, service):
        """Testa criação de API Key."""
        with patch.object(
            service.repository,
            'create_api_key',
            new_callable=AsyncMock
        ) as mock_create:
            api_key = APIKey(
                id=uuid4(),
                name="Test Key",
                key_prefix="abc12345",
                key_hash="hash",
                key_hint="6789"
            )
            mock_create.return_value = api_key

            with patch.object(
                service.repository,
                'create_log',
                new_callable=AsyncMock
            ):
                data = APIKeyCreate(name="Test Key")
                result, raw_key = await service.create_api_key(data)

                assert result.name == "Test Key"
                assert len(raw_key) == 64

    @pytest.mark.asyncio
    async def test_verify_api_key_success(self, service):
        """Testa verificação de chave com sucesso."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash=APIKey.hash_key("test_key"),
            status=APIKeyStatus.ACTIVE,
            ativo=True,
            never_expires=True,
            scopes=["read:all"]
        )

        with patch.object(
            service.repository,
            'get_api_key_by_hash',
            new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = api_key

            with patch.object(
                service.repository,
                'update_api_key',
                new_callable=AsyncMock
            ):
                valid, key, msg = await service.verify_api_key(
                    "test_key",
                    client_ip="127.0.0.1"
                )

                assert valid is True
                assert msg == "OK"

    @pytest.mark.asyncio
    async def test_verify_api_key_expired(self, service):
        """Testa verificação de chave expirada."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash=APIKey.hash_key("test_key"),
            status=APIKeyStatus.ACTIVE,
            ativo=True,
            never_expires=False,
            expires_at=datetime.utcnow() - timedelta(days=1)
        )

        with patch.object(
            service.repository,
            'get_api_key_by_hash',
            new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = api_key

            valid, key, msg = await service.verify_api_key("test_key")

            assert valid is False
            assert "expirada" in msg

    @pytest.mark.asyncio
    async def test_queue_sync(self, service):
        """Testa adição à fila de sync."""
        with patch.object(
            service.repository,
            'create_sync_item',
            new_callable=AsyncMock
        ) as mock_create:
            item = SyncQueue(
                id=uuid4(),
                entity_type=SyncEntityType.CLIENT,
                external_system=ExternalSystem.OMIE
            )
            mock_create.return_value = item

            data = SyncQueueCreate(
                entity_type=SyncEntityType.CLIENT,
                external_system=ExternalSystem.OMIE,
                payload={"test": True}
            )

            result = await service.queue_sync(data)

            assert result.entity_type == SyncEntityType.CLIENT
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_sync_success(self, service):
        """Testa conclusão de sync com sucesso."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            external_system=ExternalSystem.OMIE,
            status=SyncStatus.PROCESSING
        )

        with patch.object(
            service,
            'get_sync_item',
            new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = item

            with patch.object(
                service.repository,
                'update_sync_item',
                new_callable=AsyncMock
            ) as mock_update:
                mock_update.return_value = item

                with patch.object(
                    service.repository,
                    'create_log',
                    new_callable=AsyncMock
                ):
                    result = await service.complete_sync_success(
                        item.id,
                        external_id="ext-123"
                    )

                    assert result.status == SyncStatus.COMPLETED


class TestWebhookService:
    """Testes para WebhookService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para o serviço."""
        return WebhookService(mock_db)

    @pytest.mark.asyncio
    async def test_create_webhook(self, service):
        """Testa criação de webhook."""
        with patch.object(
            service.repository,
            'create_webhook',
            new_callable=AsyncMock
        ) as mock_create:
            webhook = WebhookConfig(
                id=uuid4(),
                name="Test Webhook",
                url="https://example.com/webhook",
                events=["test.event"],
                secret_key="secret123"
            )
            mock_create.return_value = webhook

            with patch.object(
                service.repository,
                'create_log',
                new_callable=AsyncMock
            ):
                data = WebhookConfigCreate(
                    name="Test Webhook",
                    url="https://example.com/webhook",
                    events=["client.created"]
                )

                result = await service.create_webhook(data)

                assert result.name == "Test Webhook"
                assert result.secret_key is not None

    @pytest.mark.asyncio
    async def test_regenerate_secret(self, service):
        """Testa regeneração de secret."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=["test"],
            secret_key="old_secret"
        )

        with patch.object(
            service,
            'get_webhook',
            new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = webhook

            with patch.object(
                service.repository,
                'update_webhook',
                new_callable=AsyncMock
            ):
                with patch.object(
                    service.repository,
                    'create_log',
                    new_callable=AsyncMock
                ):
                    new_secret = await service.regenerate_secret(webhook.id)

                    assert len(new_secret) == 64
                    assert new_secret != "old_secret"

    @pytest.mark.asyncio
    async def test_trigger_event(self, service):
        """Testa disparo de evento."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com/webhook",
            events=["client.created"],
            status=WebhookStatus.ACTIVE,
            ativo=True,
            secret_key="secret"
        )

        with patch.object(
            service.repository,
            'get_webhooks_for_event',
            new_callable=AsyncMock
        ) as mock_webhooks:
            mock_webhooks.return_value = [webhook]

            with patch.object(
                service,
                '_deliver_webhook',
                new_callable=AsyncMock
            ) as mock_deliver:
                mock_deliver.return_value = {
                    "webhook_id": str(webhook.id),
                    "success": True,
                    "status_code": 200
                }

                results = await service.trigger_event(
                    event="client.created",
                    payload={"id": "123"}
                )

                assert len(results) == 1
                assert results[0]["success"] is True

    @pytest.mark.asyncio
    async def test_trigger_event_no_webhooks(self, service):
        """Testa disparo sem webhooks inscritos."""
        with patch.object(
            service.repository,
            'get_webhooks_for_event',
            new_callable=AsyncMock
        ) as mock_webhooks:
            mock_webhooks.return_value = []

            results = await service.trigger_event(
                event="unknown.event",
                payload={}
            )

            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_check_failing_webhooks(self, service):
        """Testa verificação de webhooks com falha."""
        failing = [
            WebhookConfig(
                id=uuid4(),
                name=f"Failing {i}",
                url="https://example.com",
                events=["test"],
                consecutive_failures=10
            )
            for i in range(3)
        ]

        with patch.object(
            service.repository,
            'get_failing_webhooks',
            new_callable=AsyncMock
        ) as mock_failing:
            mock_failing.return_value = failing

            result = await service.check_failing_webhooks()

            assert len(result) == 3

    @pytest.mark.asyncio
    async def test_auto_disable_failing_webhooks(self, service):
        """Testa desativação automática de webhooks."""
        failing = [
            WebhookConfig(
                id=uuid4(),
                name=f"Failing {i}",
                url="https://example.com",
                events=["test"],
                status=WebhookStatus.ACTIVE,
                consecutive_failures=15
            )
            for i in range(2)
        ]

        with patch.object(
            service.repository,
            'get_failing_webhooks',
            new_callable=AsyncMock
        ) as mock_failing:
            mock_failing.return_value = failing

            with patch.object(
                service.repository,
                'update_webhook',
                new_callable=AsyncMock
            ):
                with patch.object(
                    service.repository,
                    'create_log',
                    new_callable=AsyncMock
                ):
                    count = await service.auto_disable_failing_webhooks()

                    assert count == 2


class TestIntegrationServiceDashboard:
    """Testes para Dashboard no IntegrationService."""

    @pytest.fixture
    def mock_db(self):
        """Fixture para mock do banco."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db):
        """Fixture para o serviço."""
        return IntegrationService(mock_db)

    @pytest.mark.asyncio
    async def test_get_dashboard(self, service):
        """Testa geração de dashboard."""
        endpoints = [
            APIEndpoint(
                id=uuid4(),
                name="Test",
                path="/test",
                method=HTTPMethod.GET,
                status=EndpointStatus.ACTIVE,
                total_calls=100,
                successful_calls=95
            )
        ]

        keys = [
            APIKey(
                id=uuid4(),
                name="Key",
                key_prefix="test",
                key_hash="hash",
                status=APIKeyStatus.ACTIVE
            )
        ]

        webhooks = [
            WebhookConfig(
                id=uuid4(),
                name="Webhook",
                url="https://test.com",
                events=["test"],
                status=WebhookStatus.ACTIVE,
                total_deliveries=50,
                successful_deliveries=48
            )
        ]

        with patch.object(
            service.repository,
            'list_endpoints',
            new_callable=AsyncMock
        ) as mock_endpoints:
            mock_endpoints.return_value = (endpoints, 1)

            with patch.object(
                service.repository,
                'list_api_keys',
                new_callable=AsyncMock
            ) as mock_keys:
                mock_keys.return_value = (keys, 1)

                with patch.object(
                    service.repository,
                    'list_webhooks',
                    new_callable=AsyncMock
                ) as mock_webhooks:
                    mock_webhooks.return_value = (webhooks, 1)

                    with patch.object(
                        service,
                        'get_sync_stats',
                        new_callable=AsyncMock
                    ) as mock_stats:
                        mock_stats.return_value = {
                            "total": 10,
                            "by_status": {},
                            "by_entity_type": {},
                            "by_external_system": {}
                        }

                        with patch.object(
                            service.repository,
                            'get_recent_errors',
                            new_callable=AsyncMock
                        ) as mock_errors:
                            mock_errors.return_value = []

                            dashboard = await service.get_dashboard()

                            assert dashboard.total_endpoints == 1
                            assert dashboard.active_endpoints == 1
                            assert dashboard.total_api_keys == 1
                            assert dashboard.total_webhooks == 1

    @pytest.mark.asyncio
    async def test_get_health_check(self, service):
        """Testa health check."""
        with patch.object(
            service.repository,
            'list_endpoints',
            new_callable=AsyncMock
        ) as mock_endpoints:
            mock_endpoints.return_value = ([MagicMock()], 1)

            with patch.object(
                service.repository,
                'get_failing_webhooks',
                new_callable=AsyncMock
            ) as mock_failing:
                mock_failing.return_value = []

                with patch.object(
                    service,
                    'get_sync_stats',
                    new_callable=AsyncMock
                ) as mock_stats:
                    mock_stats.return_value = {"by_status": {"failed": 0}}

                    health = await service.get_health_check()

                    assert health.api_gateway == "healthy"
                    assert health.webhooks == "healthy"
                    assert health.sync_queue == "healthy"
