"""
Testes para os Models do módulo de Integrações
Sprint 32: API Gateway / Integrações
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from modules.integrations.models import (
    APIEndpoint,
    APIKey,
    WebhookConfig,
    IntegrationLog,
    SyncQueue,
    HTTPMethod,
    EndpointCategory,
    EndpointStatus,
    APIKeyType,
    APIKeyStatus,
    WebhookEvent,
    WebhookStatus,
    WebhookAuthType,
    LogType,
    LogLevel,
    LogStatus,
    SyncStatus,
    SyncPriority,
    SyncEntityType,
    SyncOperationType,
    ExternalSystem,
)


class TestAPIEndpoint:
    """Testes para o model APIEndpoint."""

    def test_create_api_endpoint(self):
        """Testa criação de APIEndpoint."""
        endpoint = APIEndpoint(
            id=uuid4(),
            name="Get Users",
            path="/users",
            method=HTTPMethod.GET,
            category=EndpointCategory.CLIENTS,
            version="v1"
        )

        assert endpoint.name == "Get Users"
        assert endpoint.path == "/users"
        assert endpoint.method == HTTPMethod.GET
        assert endpoint.category == EndpointCategory.CLIENTS
        assert endpoint.status == EndpointStatus.ACTIVE
        assert endpoint.requires_auth is True

    def test_increment_calls(self):
        """Testa incremento de chamadas."""
        endpoint = APIEndpoint(
            id=uuid4(),
            name="Test",
            path="/test",
            method=HTTPMethod.GET
        )

        endpoint.increment_calls(success=True, response_time_ms=100)
        assert endpoint.total_calls == 1
        assert endpoint.successful_calls == 1
        assert endpoint.failed_calls == 0
        assert endpoint.avg_response_time_ms == 100

        endpoint.increment_calls(success=False, response_time_ms=200)
        assert endpoint.total_calls == 2
        assert endpoint.successful_calls == 1
        assert endpoint.failed_calls == 1
        assert endpoint.avg_response_time_ms == 150

    def test_deprecate_endpoint(self):
        """Testa depreciação de endpoint."""
        endpoint = APIEndpoint(
            id=uuid4(),
            name="Old Endpoint",
            path="/old",
            method=HTTPMethod.GET
        )

        replacement_id = str(uuid4())
        endpoint.deprecate(replacement_id)

        assert endpoint.status == EndpointStatus.DEPRECATED
        assert endpoint.deprecated_at is not None
        assert endpoint.replacement_endpoint_id == replacement_id

    def test_success_rate(self):
        """Testa cálculo de taxa de sucesso."""
        endpoint = APIEndpoint(
            id=uuid4(),
            name="Test",
            path="/test",
            method=HTTPMethod.GET,
            total_calls=100,
            successful_calls=90,
            failed_calls=10
        )

        assert endpoint.success_rate == 90.0

    def test_full_path(self):
        """Testa geração do path completo."""
        endpoint = APIEndpoint(
            id=uuid4(),
            name="Test",
            path="/users",
            method=HTTPMethod.GET,
            version="v2"
        )

        assert endpoint.full_path == "/api/v2/users"

    def test_is_available(self):
        """Testa verificação de disponibilidade."""
        endpoint = APIEndpoint(
            id=uuid4(),
            name="Test",
            path="/test",
            method=HTTPMethod.GET,
            status=EndpointStatus.ACTIVE
        )
        assert endpoint.is_available is True

        endpoint.status = EndpointStatus.DEPRECATED
        assert endpoint.is_available is False

        endpoint.status = EndpointStatus.BETA
        assert endpoint.is_available is True


class TestAPIKey:
    """Testes para o model APIKey."""

    def test_create_api_key(self):
        """Testa criação de APIKey."""
        api_key = APIKey(
            id=uuid4(),
            name="Production Key",
            key_prefix="abc123",
            key_hash="hash123",
            key_type=APIKeyType.PRODUCTION
        )

        assert api_key.name == "Production Key"
        assert api_key.key_type == APIKeyType.PRODUCTION
        assert api_key.status == APIKeyStatus.ACTIVE
        assert api_key.never_expires is False

    def test_generate_key(self):
        """Testa geração de chave."""
        raw_key, prefix, key_hash, hint = APIKey.generate_key()

        assert len(raw_key) == 64
        assert len(prefix) == 8
        assert len(key_hash) == 64
        assert len(hint) == 4
        assert raw_key.startswith(prefix)
        assert raw_key.endswith(hint)

    def test_verify_key(self):
        """Testa verificação de chave."""
        raw_key, prefix, key_hash, hint = APIKey.generate_key()

        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix=prefix,
            key_hash=key_hash,
            key_hint=hint
        )

        assert api_key.verify_key(raw_key) is True
        assert api_key.verify_key("wrong_key") is False

    def test_check_rate_limit(self):
        """Testa verificação de rate limit."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash="hash",
            rate_limit_per_minute=10,
            current_minute_calls=5
        )

        allowed, reason = api_key.check_rate_limit()
        assert allowed is True

        api_key.current_minute_calls = 10
        allowed, reason = api_key.check_rate_limit()
        assert allowed is False
        assert "minuto" in reason

    def test_check_ip_allowed(self):
        """Testa verificação de IP."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash="hash",
            ip_whitelist=["192.168.1.1", "192.168.1.2"]
        )

        assert api_key.check_ip_allowed("192.168.1.1") is True
        assert api_key.check_ip_allowed("192.168.1.3") is False

        api_key.ip_whitelist = None
        api_key.ip_blacklist = ["10.0.0.1"]
        assert api_key.check_ip_allowed("192.168.1.1") is True
        assert api_key.check_ip_allowed("10.0.0.1") is False

    def test_has_scope(self):
        """Testa verificação de escopo."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash="hash",
            scopes=["read:clients", "write:services"]
        )

        assert api_key.has_scope("read:clients") is True
        assert api_key.has_scope("write:services") is True
        assert api_key.has_scope("admin") is False

        api_key.scopes = ["admin"]
        assert api_key.has_scope("read:anything") is True

        api_key.scopes = ["read:all"]
        assert api_key.has_scope("read:clients") is True
        assert api_key.has_scope("write:clients") is False

    def test_revoke(self):
        """Testa revogação de chave."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash="hash"
        )

        user_id = str(uuid4())
        api_key.revoke(revoked_by=user_id, reason="Teste")

        assert api_key.status == APIKeyStatus.REVOKED
        assert api_key.revoked_at is not None
        assert api_key.revoked_by == user_id
        assert api_key.revocation_reason == "Teste"
        assert api_key.ativo is False

    def test_is_valid(self):
        """Testa verificação de validade."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash="hash",
            status=APIKeyStatus.ACTIVE,
            ativo=True,
            never_expires=True
        )

        assert api_key.is_valid is True

        api_key.status = APIKeyStatus.SUSPENDED
        assert api_key.is_valid is False

        api_key.status = APIKeyStatus.ACTIVE
        api_key.never_expires = False
        api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        assert api_key.is_valid is False

    def test_is_expired(self):
        """Testa verificação de expiração."""
        api_key = APIKey(
            id=uuid4(),
            name="Test",
            key_prefix="test",
            key_hash="hash",
            never_expires=True
        )

        assert api_key.is_expired is False

        api_key.never_expires = False
        api_key.expires_at = datetime.utcnow() + timedelta(days=1)
        assert api_key.is_expired is False

        api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        assert api_key.is_expired is True


class TestWebhookConfig:
    """Testes para o model WebhookConfig."""

    def test_create_webhook(self):
        """Testa criação de webhook."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Order Webhook",
            url="https://example.com/webhook",
            events=[WebhookEvent.SERVICE_ORDER_CREATED.value]
        )

        assert webhook.name == "Order Webhook"
        assert webhook.url == "https://example.com/webhook"
        assert webhook.status == WebhookStatus.ACTIVE
        assert webhook.auth_type == WebhookAuthType.HMAC

    def test_generate_secret(self):
        """Testa geração de secret."""
        secret = WebhookConfig.generate_secret()
        assert len(secret) == 64

    def test_sign_payload(self):
        """Testa assinatura de payload."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=["test.event"],
            secret_key="test_secret_key"
        )

        signature = webhook.sign_payload('{"test": true}')
        assert signature.startswith("sha256=")

    def test_verify_signature(self):
        """Testa verificação de assinatura."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=["test.event"],
            secret_key="test_secret_key"
        )

        payload = '{"test": true}'
        signature = webhook.sign_payload(payload)

        assert webhook.verify_signature(payload, signature) is True
        assert webhook.verify_signature(payload, "wrong_signature") is False

    def test_is_subscribed_to(self):
        """Testa verificação de inscrição em evento."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=[
                WebhookEvent.CLIENT_CREATED.value,
                WebhookEvent.CLIENT_UPDATED.value
            ]
        )

        assert webhook.is_subscribed_to(WebhookEvent.CLIENT_CREATED.value) is True
        assert webhook.is_subscribed_to(WebhookEvent.CLIENT_DELETED.value) is False

    def test_record_delivery(self):
        """Testa registro de entrega."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=["test"]
        )

        webhook.record_delivery(success=True, response_time_ms=100)
        assert webhook.total_deliveries == 1
        assert webhook.successful_deliveries == 1
        assert webhook.consecutive_failures == 0

        webhook.record_delivery(success=False, response_time_ms=50, error="Timeout")
        assert webhook.total_deliveries == 2
        assert webhook.failed_deliveries == 1
        assert webhook.consecutive_failures == 1
        assert webhook.last_failure_reason == "Timeout"

    def test_delivery_rate(self):
        """Testa cálculo de taxa de entrega."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=["test"],
            total_deliveries=100,
            successful_deliveries=95,
            failed_deliveries=5
        )

        assert webhook.delivery_rate == 95.0

    def test_health_status(self):
        """Testa status de saúde."""
        webhook = WebhookConfig(
            id=uuid4(),
            name="Test",
            url="https://example.com",
            events=["test"],
            status=WebhookStatus.ACTIVE,
            ativo=True,
            consecutive_failures=0
        )

        assert webhook.health_status == "healthy"

        webhook.consecutive_failures = 3
        assert webhook.health_status == "warning"

        webhook.consecutive_failures = 6
        assert webhook.health_status == "critical"

        webhook.status = WebhookStatus.DISABLED
        assert webhook.health_status == "offline"


class TestIntegrationLog:
    """Testes para o model IntegrationLog."""

    def test_create_api_log(self):
        """Testa criação de log de API."""
        log = IntegrationLog.create_api_log(
            endpoint_id=str(uuid4()),
            api_key_id=str(uuid4()),
            method="GET",
            path="/users",
            status_code=200,
            duration_ms=50,
            client_ip="192.168.1.1"
        )

        assert log.log_type == LogType.API_CALL
        assert log.level == LogLevel.INFO
        assert log.status == LogStatus.SUCCESS
        assert log.method == "GET"
        assert log.path == "/users"
        assert log.response_status_code == 200

    def test_create_webhook_log(self):
        """Testa criação de log de webhook."""
        log = IntegrationLog.create_webhook_log(
            webhook_id=str(uuid4()),
            success=True,
            duration_ms=100,
            status_code=200
        )

        assert log.log_type == LogType.WEBHOOK_DELIVERY
        assert log.status == LogStatus.SUCCESS

    def test_create_error_log(self):
        """Testa criação de log de erro."""
        log = IntegrationLog.create_error_log(
            error_code="ERR001",
            error_message="Erro de teste"
        )

        assert log.log_type == LogType.ERROR
        assert log.level == LogLevel.ERROR
        assert log.status == LogStatus.FAILURE
        assert log.error_code == "ERR001"

    def test_create_auth_log(self):
        """Testa criação de log de autenticação."""
        log = IntegrationLog.create_auth_log(
            api_key_id=str(uuid4()),
            success=False,
            client_ip="192.168.1.1",
            reason="Chave inválida"
        )

        assert log.log_type == LogType.AUTHENTICATION
        assert log.status == LogStatus.UNAUTHORIZED
        assert log.error_message == "Chave inválida"

    def test_is_error(self):
        """Testa verificação de erro."""
        log = IntegrationLog(
            id=uuid4(),
            log_type=LogType.API_CALL,
            status=LogStatus.FAILURE
        )
        assert log.is_error is True

        log.status = LogStatus.SUCCESS
        assert log.is_error is False


class TestSyncQueue:
    """Testes para o model SyncQueue."""

    def test_create_sync_item(self):
        """Testa criação de item de sync."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE,
            external_system=ExternalSystem.OMIE,
            payload={"name": "Test Client"}
        )

        assert item.entity_type == SyncEntityType.CLIENT
        assert item.operation == SyncOperationType.CREATE
        assert item.status == SyncStatus.PENDING
        assert item.priority == SyncPriority.NORMAL

    def test_start_processing(self):
        """Testa início de processamento."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE
        )

        item.start_processing("worker-1")

        assert item.status == SyncStatus.PROCESSING
        assert item.started_at is not None
        assert item.processed_by == "worker-1"

    def test_complete_success(self):
        """Testa conclusão com sucesso."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE
        )
        item.start_processing("worker-1")
        item.complete_success(external_id="ext-123", response={"id": "ext-123"})

        assert item.status == SyncStatus.COMPLETED
        assert item.external_id == "ext-123"
        assert item.completed_at is not None
        assert item.error_code is None

    def test_complete_failure_with_retry(self):
        """Testa falha com retry."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE,
            max_retries=3,
            retry_delay_seconds=60
        )
        item.start_processing("worker-1")
        item.complete_failure(
            error_code="ERR001",
            error_message="Erro de conexão"
        )

        assert item.status == SyncStatus.RETRYING
        assert item.retry_count == 1
        assert item.next_retry_at is not None
        assert item.error_code == "ERR001"

    def test_complete_failure_max_retries(self):
        """Testa falha sem retry (max atingido)."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE,
            max_retries=2,
            retry_count=2
        )
        item.start_processing("worker-1")
        item.complete_failure(
            error_code="ERR001",
            error_message="Erro de conexão"
        )

        assert item.status == SyncStatus.FAILED

    def test_cancel(self):
        """Testa cancelamento."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE
        )

        item.cancel("Não mais necessário")

        assert item.status == SyncStatus.CANCELLED
        assert "Cancelado" in item.notes

    def test_reset(self):
        """Testa reset para reprocessamento."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE,
            status=SyncStatus.FAILED,
            retry_count=3,
            error_code="ERR001"
        )

        item.reset()

        assert item.status == SyncStatus.PENDING
        assert item.retry_count == 0
        assert item.error_code is None
        assert item.started_at is None

    def test_is_ready_to_process(self):
        """Testa verificação de pronto para processar."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE,
            status=SyncStatus.PENDING
        )

        assert item.is_ready_to_process is True

        item.status = SyncStatus.PROCESSING
        assert item.is_ready_to_process is False

        item.status = SyncStatus.RETRYING
        item.next_retry_at = datetime.utcnow() + timedelta(minutes=5)
        assert item.is_ready_to_process is False

        item.next_retry_at = datetime.utcnow() - timedelta(minutes=1)
        assert item.is_ready_to_process is True

    def test_can_retry(self):
        """Testa verificação de possibilidade de retry."""
        item = SyncQueue(
            id=uuid4(),
            entity_type=SyncEntityType.CLIENT,
            operation=SyncOperationType.CREATE,
            max_retries=3,
            retry_count=2
        )

        assert item.can_retry is True

        item.retry_count = 3
        assert item.can_retry is False
