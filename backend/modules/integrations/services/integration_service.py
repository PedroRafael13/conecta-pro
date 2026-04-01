"""
IntegrationService - Serviço principal de integrações
Sprint 32: API Gateway / Integrações
"""
# pylint: disable=too-many-locals,too-many-return-statements

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.models import (
    APIEndpoint,
    APIKey,
    APIKeyStatus,
    EndpointStatus,
    ExternalSystem,
    IntegrationLog,
    LogLevel,
    LogStatus,
    LogType,
    SyncDirection,
    SyncEntityType,
    SyncPriority,
    SyncQueue,
    SyncStatus,
    WebhookStatus,
)
from modules.integrations.repositories import IntegrationRepository
from modules.integrations.schemas import (
    APIEndpointCreate,
    APIEndpointUpdate,
    APIKeyCreate,
    APIKeyUpdate,
    IntegrationDashboard,
    IntegrationHealthCheck,
    IntegrationLogResponse,
    SyncQueueCreate,
    SyncQueueStats,
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """Serviço para gerenciamento de integrações."""

    def __init__(self, db: AsyncSession):
        """Inicializa o serviço."""
        self.db = db
        self.repository = IntegrationRepository(db)

    # ==================== API Endpoint ====================

    async def create_endpoint(self, data: APIEndpointCreate, user_id: UUID | None = None) -> APIEndpoint:
        """Cria um novo endpoint de API."""
        # Verifica se já existe
        existing = await self.repository.get_endpoint_by_path_method(data.path, data.method.value)
        if existing:
            raise ValueError(f"Endpoint {data.method.value} {data.path} já existe")

        endpoint = APIEndpoint(**data.model_dump(), created_by=user_id, updated_by=user_id)

        return await self.repository.create_endpoint(endpoint)

    async def get_endpoint(self, endpoint_id: UUID) -> APIEndpoint | None:
        """Busca endpoint por ID."""
        return await self.repository.get_endpoint_by_id(endpoint_id)

    async def list_endpoints(
        self,
        status: EndpointStatus | None = None,
        category: str | None = None,
        version: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[APIEndpoint], int, int]:
        """Lista endpoints com paginação."""
        skip = (page - 1) * page_size
        endpoints, total = await self.repository.list_endpoints(
            status=status, category=category, version=version, skip=skip, limit=page_size
        )
        pages = (total + page_size - 1) // page_size
        return endpoints, total, pages

    async def update_endpoint(
        self, endpoint_id: UUID, data: APIEndpointUpdate, user_id: UUID | None = None
    ) -> APIEndpoint:
        """Atualiza endpoint."""
        endpoint = await self.get_endpoint(endpoint_id)
        if not endpoint:
            raise ValueError("Endpoint não encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(endpoint, key, value)

        endpoint.updated_by = user_id

        return await self.repository.update_endpoint(endpoint)

    async def delete_endpoint(self, endpoint_id: UUID) -> bool:
        """Deleta endpoint."""
        return await self.repository.delete_endpoint(endpoint_id)

    async def deprecate_endpoint(
        self, endpoint_id: UUID, replacement_id: UUID | None = None, sunset_date: datetime | None = None
    ) -> APIEndpoint:
        """Deprecia um endpoint."""
        endpoint = await self.get_endpoint(endpoint_id)
        if not endpoint:
            raise ValueError("Endpoint não encontrado")

        endpoint.deprecate(str(replacement_id) if replacement_id else None)
        if sunset_date:
            endpoint.sunset_date = sunset_date

        return await self.repository.update_endpoint(endpoint)

    async def record_endpoint_call(
        self,
        endpoint_id: UUID,
        success: bool,
        response_time_ms: int,
        api_key_id: UUID | None = None,
        client_ip: str | None = None,
        status_code: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Registra chamada a um endpoint."""
        endpoint = await self.get_endpoint(endpoint_id)
        if endpoint:
            endpoint.increment_calls(success, response_time_ms)
            await self.repository.update_endpoint(endpoint)

        # Cria log
        log = IntegrationLog.create_api_log(
            endpoint_id=str(endpoint_id),
            api_key_id=str(api_key_id) if api_key_id else None,
            method=endpoint.method.value if endpoint else "UNKNOWN",
            path=endpoint.path if endpoint else "unknown",
            status_code=status_code or (200 if success else 500),
            duration_ms=response_time_ms,
            client_ip=client_ip or "unknown",
            error_message=error_message,
        )
        await self.repository.create_log(log)

    # ==================== API Key ====================

    async def create_api_key(self, data: APIKeyCreate, user_id: UUID | None = None) -> tuple[APIKey, str]:
        """
        Cria uma nova chave de API.
        Retorna: (APIKey, chave_completa)
        """
        # Gera a chave
        raw_key, prefix, key_hash, hint = APIKey.generate_key()

        api_key = APIKey(
            **data.model_dump(),
            key_prefix=prefix,
            key_hash=key_hash,
            key_hint=hint,
            created_by=user_id,
            updated_by=user_id,
        )

        created = await self.repository.create_api_key(api_key)

        # Log de criação
        log = IntegrationLog(
            api_key_id=created.id,
            log_type=LogType.SYSTEM,
            level=LogLevel.INFO,
            status=LogStatus.SUCCESS,
            action="api_key_created",
            metadata={"key_name": data.name},
        )
        await self.repository.create_log(log)

        return created, raw_key

    async def get_api_key(self, key_id: UUID) -> APIKey | None:
        """Busca API Key por ID."""
        return await self.repository.get_api_key_by_id(key_id)

    async def verify_api_key(
        self, key: str, required_scope: str | None = None, client_ip: str | None = None
    ) -> tuple[bool, APIKey | None, str]:
        """
        Verifica uma chave de API.
        Retorna: (válida, APIKey, mensagem)
        """
        key_hash = APIKey.hash_key(key)
        api_key = await self.repository.get_api_key_by_hash(key_hash)

        if not api_key:
            return False, None, "Chave de API inválida"

        if not api_key.is_valid:
            if api_key.is_expired:
                return False, api_key, "Chave de API expirada"
            return False, api_key, "Chave de API inativa"

        # Verifica IP
        if client_ip and not api_key.check_ip_allowed(client_ip):
            log = IntegrationLog.create_auth_log(
                api_key_id=str(api_key.id), success=False, client_ip=client_ip, reason="IP não permitido"
            )
            await self.repository.create_log(log)
            return False, api_key, "IP não autorizado"

        # Verifica rate limit
        allowed, reason = api_key.check_rate_limit()
        if not allowed:
            log = IntegrationLog.create_rate_limit_log(
                api_key_id=str(api_key.id),
                client_ip=client_ip or "unknown",
                limit_remaining=0,
                reset_at=datetime.utcnow() + timedelta(minutes=1),
            )
            await self.repository.create_log(log)
            return False, api_key, reason

        # Verifica escopo
        if required_scope and not api_key.has_scope(required_scope):
            return False, api_key, f"Escopo necessário: {required_scope}"

        # Registra uso
        api_key.record_usage(client_ip or "unknown")
        await self.repository.update_api_key(api_key)

        return True, api_key, "OK"

    async def list_api_keys(
        self,
        client_id: UUID | None = None,
        user_id: UUID | None = None,
        status: APIKeyStatus | None = None,
        key_type: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[APIKey], int, int]:
        """Lista API Keys com paginação."""
        skip = (page - 1) * page_size
        keys, total = await self.repository.list_api_keys(
            client_id=client_id, user_id=user_id, status=status, key_type=key_type, skip=skip, limit=page_size
        )
        pages = (total + page_size - 1) // page_size
        return keys, total, pages

    async def update_api_key(self, key_id: UUID, data: APIKeyUpdate, user_id: UUID | None = None) -> APIKey:
        """Atualiza API Key."""
        api_key = await self.get_api_key(key_id)
        if not api_key:
            raise ValueError("API Key não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(api_key, key, value)

        api_key.updated_by = user_id

        return await self.repository.update_api_key(api_key)

    async def revoke_api_key(self, key_id: UUID, reason: str | None = None, user_id: UUID | None = None) -> APIKey:
        """Revoga uma API Key."""
        api_key = await self.get_api_key(key_id)
        if not api_key:
            raise ValueError("API Key não encontrada")

        api_key.revoke(revoked_by=str(user_id) if user_id else None, reason=reason)

        result = await self.repository.update_api_key(api_key)

        # Log
        log = IntegrationLog(
            api_key_id=api_key.id,
            log_type=LogType.SYSTEM,
            level=LogLevel.WARNING,
            status=LogStatus.SUCCESS,
            action="api_key_revoked",
            metadata={"reason": reason},
        )
        await self.repository.create_log(log)

        return result

    async def check_and_expire_keys(self) -> int:
        """Verifica e expira chaves vencidas."""
        expired_keys = await self.repository.get_expired_api_keys()
        count = 0

        for api_key in expired_keys:
            api_key.status = APIKeyStatus.EXPIRED
            await self.repository.update_api_key(api_key)
            count += 1

            log = IntegrationLog(
                api_key_id=api_key.id,
                log_type=LogType.SYSTEM,
                level=LogLevel.INFO,
                status=LogStatus.SUCCESS,
                action="api_key_expired",
            )
            await self.repository.create_log(log)

        logger.info(f"Expiradas {count} chaves de API")
        return count

    # ==================== Sync Queue ====================

    async def queue_sync(self, data: SyncQueueCreate, user_id: UUID | None = None) -> SyncQueue:
        """Adiciona item à fila de sincronização."""
        # Calcula hash do payload
        payload_hash = None
        if data.payload:
            payload_str = json.dumps(data.payload, sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        item = SyncQueue(**data.model_dump(), payload_hash=payload_hash, created_by=user_id, updated_by=user_id)

        return await self.repository.create_sync_item(item)

    async def queue_sync_batch(
        self, items_data: list[SyncQueueCreate], batch_id: UUID | None = None, user_id: UUID | None = None
    ) -> list[SyncQueue]:
        """Adiciona múltiplos itens à fila."""
        if not batch_id:
            batch_id = uuid4()

        items = []
        for data in items_data:
            payload_hash = None
            if data.payload:
                payload_str = json.dumps(data.payload, sort_keys=True)
                payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

            item = SyncQueue(
                **data.model_dump(),
                batch_id=batch_id,
                payload_hash=payload_hash,
                created_by=user_id,
                updated_by=user_id,
            )
            items.append(item)

        return await self.repository.create_sync_batch(items)

    async def get_sync_item(self, item_id: UUID) -> SyncQueue | None:
        """Busca item da fila."""
        return await self.repository.get_sync_item_by_id(item_id)

    async def get_next_sync_items(
        self, limit: int = 10, external_system: ExternalSystem | None = None
    ) -> list[SyncQueue]:
        """Busca próximos itens para processar."""
        return await self.repository.get_next_sync_items(limit=limit, external_system=external_system)

    async def process_sync_item(self, item_id: UUID, worker_id: str) -> SyncQueue:
        """Marca item como em processamento."""
        item = await self.get_sync_item(item_id)
        if not item:
            raise ValueError("Item não encontrado")

        if not item.is_ready_to_process:
            raise ValueError("Item não está pronto para processamento")

        item.start_processing(worker_id)
        return await self.repository.update_sync_item(item)

    async def complete_sync_success(
        self, item_id: UUID, external_id: str | None = None, response: dict | None = None
    ) -> SyncQueue:
        """Marca item como completado com sucesso."""
        item = await self.get_sync_item(item_id)
        if not item:
            raise ValueError("Item não encontrado")

        item.complete_success(external_id, response)
        result = await self.repository.update_sync_item(item)

        # Log
        log = IntegrationLog(
            sync_queue_id=item.id,
            log_type=LogType.SYNC_OPERATION,
            level=LogLevel.INFO,
            status=LogStatus.SUCCESS,
            action="sync_completed",
            duration_ms=item.processing_time_ms,
            metadata={"entity_type": item.entity_type.value, "external_system": item.external_system.value},
        )
        await self.repository.create_log(log)

        return result

    async def complete_sync_failure(
        self,
        item_id: UUID,
        error_code: str,
        error_message: str,
        error_details: dict | None = None,
        status_code: int | None = None,
    ) -> SyncQueue:
        """Marca item como falha."""
        item = await self.get_sync_item(item_id)
        if not item:
            raise ValueError("Item não encontrado")

        item.complete_failure(error_code, error_message, error_details, status_code)
        result = await self.repository.update_sync_item(item)

        # Log
        log = IntegrationLog(
            sync_queue_id=item.id,
            log_type=LogType.SYNC_OPERATION,
            level=LogLevel.ERROR,
            status=LogStatus.FAILURE,
            action="sync_failed",
            error_code=error_code,
            error_message=error_message,
            duration_ms=item.processing_time_ms,
            metadata={
                "entity_type": item.entity_type.value,
                "external_system": item.external_system.value,
                "retry_count": item.retry_count,
            },
        )
        await self.repository.create_log(log)

        return result

    async def list_sync_items(
        self,
        status: SyncStatus | None = None,
        priority: SyncPriority | None = None,
        entity_type: SyncEntityType | None = None,
        external_system: ExternalSystem | None = None,
        direction: SyncDirection | None = None,
        batch_id: UUID | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[SyncQueue], int, int]:
        """Lista itens da fila com paginação."""
        skip = (page - 1) * page_size
        items, total = await self.repository.list_sync_items(
            status=status,
            priority=priority,
            entity_type=entity_type,
            external_system=external_system,
            direction=direction,
            batch_id=batch_id,
            skip=skip,
            limit=page_size,
        )
        pages = (total + page_size - 1) // page_size
        return items, total, pages

    async def get_sync_stats(self) -> dict[str, Any]:
        """Obtém estatísticas da fila."""
        return await self.repository.get_sync_stats()

    async def cancel_sync_item(self, item_id: UUID, reason: str | None = None) -> SyncQueue:
        """Cancela item da fila."""
        item = await self.get_sync_item(item_id)
        if not item:
            raise ValueError("Item não encontrado")

        item.cancel(reason)
        return await self.repository.update_sync_item(item)

    async def retry_sync_item(self, item_id: UUID) -> SyncQueue:
        """Reseta item para reprocessamento."""
        item = await self.get_sync_item(item_id)
        if not item:
            raise ValueError("Item não encontrado")

        item.reset()
        return await self.repository.update_sync_item(item)

    # ==================== Dashboard ====================

    async def get_dashboard(self) -> IntegrationDashboard:
        """Obtém dashboard de integrações."""
        # API Endpoints
        endpoints, total_endpoints = await self.repository.list_endpoints(limit=1000)
        active_endpoints = len([e for e in endpoints if e.status == EndpointStatus.ACTIVE])
        deprecated_endpoints = len([e for e in endpoints if e.status == EndpointStatus.DEPRECATED])

        # Calcula chamadas do dia
        total_calls = sum(e.total_calls for e in endpoints)
        successful_calls = sum(e.successful_calls for e in endpoints)
        api_success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 100.0
        avg_response = sum(e.avg_response_time_ms or 0 for e in endpoints if e.avg_response_time_ms)
        avg_response_time = (
            avg_response // len([e for e in endpoints if e.avg_response_time_ms])
            if any(e.avg_response_time_ms for e in endpoints)
            else None
        )

        # API Keys
        keys, total_keys = await self.repository.list_api_keys(limit=1000)
        active_keys = len([k for k in keys if k.status == APIKeyStatus.ACTIVE])
        expired_keys = len([k for k in keys if k.status == APIKeyStatus.EXPIRED])
        revoked_keys = len([k for k in keys if k.status == APIKeyStatus.REVOKED])

        # Webhooks
        webhooks, total_webhooks = await self.repository.list_webhooks(limit=1000)
        active_webhooks = len([w for w in webhooks if w.status == WebhookStatus.ACTIVE])
        failing_webhooks = len([w for w in webhooks if w.status == WebhookStatus.FAILING])

        total_deliveries = sum(w.total_deliveries for w in webhooks)
        successful_deliveries = sum(w.successful_deliveries for w in webhooks)
        webhook_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 100.0

        # Sync Stats
        sync_stats_data = await self.get_sync_stats()
        sync_stats = SyncQueueStats(
            total=sync_stats_data.get("total", 0),
            pending=sync_stats_data.get("by_status", {}).get("pending", 0),
            processing=sync_stats_data.get("by_status", {}).get("processing", 0),
            completed=sync_stats_data.get("by_status", {}).get("completed", 0),
            failed=sync_stats_data.get("by_status", {}).get("failed", 0),
            retrying=sync_stats_data.get("by_status", {}).get("retrying", 0),
            requires_review=sync_stats_data.get("requires_review", 0),
            by_entity_type=sync_stats_data.get("by_entity_type", {}),
            by_external_system=sync_stats_data.get("by_external_system", {}),
            avg_processing_time_ms=sync_stats_data.get("avg_processing_time_ms"),
        )

        # Recent errors
        recent_errors_data = await self.repository.get_recent_errors(hours=24, limit=5)
        recent_errors = [IntegrationLogResponse.model_validate(log) for log in recent_errors_data]

        # Health
        health = "healthy"
        if failing_webhooks > 0 or sync_stats.failed > 10:
            health = "degraded"
        if api_success_rate < 90 or sync_stats.failed > 50:
            health = "critical"

        return IntegrationDashboard(
            total_endpoints=total_endpoints,
            active_endpoints=active_endpoints,
            deprecated_endpoints=deprecated_endpoints,
            total_api_calls_today=total_calls,
            api_success_rate=round(api_success_rate, 2),
            avg_response_time_ms=avg_response_time,
            total_api_keys=total_keys,
            active_api_keys=active_keys,
            expired_api_keys=expired_keys,
            revoked_api_keys=revoked_keys,
            total_webhooks=total_webhooks,
            active_webhooks=active_webhooks,
            failing_webhooks=failing_webhooks,
            webhook_delivery_rate=round(webhook_rate, 2),
            sync_stats=sync_stats,
            recent_errors=recent_errors,
            overall_health=health,
        )

    async def get_health_check(self) -> IntegrationHealthCheck:
        """Verifica saúde das integrações."""
        # API Gateway
        api_health = "healthy"
        try:
            endpoints, _ = await self.repository.list_endpoints(limit=1)
            if not endpoints:
                api_health = "unknown"
        except (ValueError, RuntimeError):
            api_health = "unhealthy"

        # Webhooks
        webhook_health = "healthy"
        failing = await self.repository.get_failing_webhooks(min_failures=5)
        if len(failing) > 0:
            webhook_health = "degraded"
        if len(failing) > 5:
            webhook_health = "unhealthy"

        # Sync Queue
        sync_health = "healthy"
        stats = await self.get_sync_stats()
        if stats.get("by_status", {}).get("failed", 0) > 10:
            sync_health = "degraded"
        if stats.get("by_status", {}).get("failed", 0) > 50:
            sync_health = "unhealthy"

        return IntegrationHealthCheck(
            api_gateway=api_health,
            webhooks=webhook_health,
            sync_queue=sync_health,
            external_systems={},
            last_check_at=datetime.utcnow(),
        )
