"""
Repository para o módulo de Integrações
Sprint 32: API Gateway / Integrações
"""
# pylint: disable=too-many-locals,too-many-branches

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
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
    WebhookConfig,
    WebhookStatus,
)

logger = logging.getLogger(__name__)


class IntegrationRepository:
    """Repository para operações de dados de integrações."""

    def __init__(self, db: AsyncSession):
        """Inicializa o repository."""
        self.db = db

    # ==================== API Endpoint ====================

    async def create_endpoint(self, endpoint: APIEndpoint) -> APIEndpoint:
        """Cria um novo endpoint."""
        self.db.add(endpoint)
        await self.db.commit()
        await self.db.refresh(endpoint)
        logger.info(f"Endpoint criado: {endpoint.id}")
        return endpoint

    async def get_endpoint_by_id(self, endpoint_id: UUID) -> APIEndpoint | None:
        """Busca endpoint por ID."""
        result = await self.db.execute(
            select(APIEndpoint).where(APIEndpoint.id == endpoint_id, APIEndpoint.ativo.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_endpoint_by_path_method(self, path: str, method: str) -> APIEndpoint | None:
        """Busca endpoint por path e método."""
        result = await self.db.execute(
            select(APIEndpoint).where(
                APIEndpoint.path == path, APIEndpoint.method == method, APIEndpoint.ativo.is_(True)
            )
        )
        return result.scalar_one_or_none()

    async def list_endpoints(
        self,
        status: EndpointStatus | None = None,
        category: str | None = None,
        version: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[APIEndpoint], int]:
        """Lista endpoints com filtros."""
        query = select(APIEndpoint).where(APIEndpoint.ativo.is_(True))

        if status:
            query = query.where(APIEndpoint.status == status)
        if category:
            query = query.where(APIEndpoint.category == category)
        if version:
            query = query.where(APIEndpoint.version == version)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar() or 0

        # Paginate
        query = query.order_by(APIEndpoint.path).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_endpoint(self, endpoint: APIEndpoint) -> APIEndpoint:
        """Atualiza endpoint."""
        endpoint.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(endpoint)
        logger.info(f"Endpoint atualizado: {endpoint.id}")
        return endpoint

    async def delete_endpoint(self, endpoint_id: UUID) -> bool:
        """Deleta endpoint (soft delete)."""
        endpoint = await self.get_endpoint_by_id(endpoint_id)
        if endpoint:
            endpoint.ativo = False
            endpoint.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"Endpoint deletado: {endpoint_id}")
            return True
        return False

    # ==================== API Key ====================

    async def create_api_key(self, api_key: APIKey) -> APIKey:
        """Cria uma nova chave de API."""
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        logger.info(f"API Key criada: {api_key.id}")
        return api_key

    async def get_api_key_by_id(self, key_id: UUID) -> APIKey | None:
        """Busca API Key por ID."""
        result = await self.db.execute(select(APIKey).where(APIKey.id == key_id, APIKey.ativo.is_(True)))
        return result.scalar_one_or_none()

    async def get_api_key_by_hash(self, key_hash: str) -> APIKey | None:
        """Busca API Key pelo hash."""
        result = await self.db.execute(select(APIKey).where(APIKey.key_hash == key_hash, APIKey.ativo.is_(True)))
        return result.scalar_one_or_none()

    async def get_api_key_by_prefix(self, prefix: str) -> APIKey | None:
        """Busca API Key pelo prefixo."""
        result = await self.db.execute(select(APIKey).where(APIKey.key_prefix == prefix, APIKey.ativo.is_(True)))
        return result.scalar_one_or_none()

    async def list_api_keys(
        self,
        client_id: UUID | None = None,
        user_id: UUID | None = None,
        status: APIKeyStatus | None = None,
        key_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[APIKey], int]:
        """Lista API Keys com filtros."""
        query = select(APIKey).where(APIKey.ativo.is_(True))

        if client_id:
            query = query.where(APIKey.client_id == client_id)
        if user_id:
            query = query.where(APIKey.user_id == user_id)
        if status:
            query = query.where(APIKey.status == status)
        if key_type:
            query = query.where(APIKey.key_type == key_type)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar() or 0

        # Paginate
        query = query.order_by(desc(APIKey.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_api_key(self, api_key: APIKey) -> APIKey:
        """Atualiza API Key."""
        api_key.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(api_key)
        logger.info(f"API Key atualizada: {api_key.id}")
        return api_key

    async def delete_api_key(self, key_id: UUID) -> bool:
        """Deleta API Key (soft delete)."""
        api_key = await self.get_api_key_by_id(key_id)
        if api_key:
            api_key.ativo = False
            api_key.status = APIKeyStatus.REVOKED
            api_key.revoked_at = datetime.utcnow()
            api_key.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"API Key deletada: {key_id}")
            return True
        return False

    async def get_expired_api_keys(self) -> list[APIKey]:
        """Busca API Keys expiradas."""
        now = datetime.utcnow()
        result = await self.db.execute(
            select(APIKey).where(
                APIKey.ativo.is_(True),
                APIKey.status == APIKeyStatus.ACTIVE,
                APIKey.never_expires.is_(False),
                APIKey.expires_at < now,
            )
        )
        return list(result.scalars().all())

    # ==================== Webhook Config ====================

    async def create_webhook(self, webhook: WebhookConfig) -> WebhookConfig:
        """Cria um novo webhook."""
        self.db.add(webhook)
        await self.db.commit()
        await self.db.refresh(webhook)
        logger.info(f"Webhook criado: {webhook.id}")
        return webhook

    async def get_webhook_by_id(self, webhook_id: UUID) -> WebhookConfig | None:
        """Busca webhook por ID."""
        result = await self.db.execute(
            select(WebhookConfig).where(WebhookConfig.id == webhook_id, WebhookConfig.ativo.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_webhooks_for_event(self, event: str, client_id: UUID | None = None) -> list[WebhookConfig]:
        """Busca webhooks ativos para um evento."""
        query = select(WebhookConfig).where(WebhookConfig.ativo.is_(True), WebhookConfig.status == WebhookStatus.ACTIVE)

        if client_id:
            query = query.where(or_(WebhookConfig.client_id == client_id, WebhookConfig.client_id.is_(None)))

        result = await self.db.execute(query)
        webhooks = result.scalars().all()

        # Filtra por evento
        return [w for w in webhooks if w.is_subscribed_to(event)]

    async def list_webhooks(
        self, client_id: UUID | None = None, status: WebhookStatus | None = None, skip: int = 0, limit: int = 100
    ) -> tuple[list[WebhookConfig], int]:
        """Lista webhooks com filtros."""
        query = select(WebhookConfig).where(WebhookConfig.ativo.is_(True))

        if client_id:
            query = query.where(WebhookConfig.client_id == client_id)
        if status:
            query = query.where(WebhookConfig.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar() or 0

        # Paginate
        query = query.order_by(desc(WebhookConfig.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_webhook(self, webhook: WebhookConfig) -> WebhookConfig:
        """Atualiza webhook."""
        webhook.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(webhook)
        logger.info(f"Webhook atualizado: {webhook.id}")
        return webhook

    async def delete_webhook(self, webhook_id: UUID) -> bool:
        """Deleta webhook (soft delete)."""
        webhook = await self.get_webhook_by_id(webhook_id)
        if webhook:
            webhook.ativo = False
            webhook.status = WebhookStatus.DISABLED
            webhook.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"Webhook deletado: {webhook_id}")
            return True
        return False

    async def get_failing_webhooks(self, min_failures: int = 5) -> list[WebhookConfig]:
        """Busca webhooks com muitas falhas."""
        result = await self.db.execute(
            select(WebhookConfig).where(
                WebhookConfig.ativo.is_(True), WebhookConfig.consecutive_failures >= min_failures
            )
        )
        return list(result.scalars().all())

    # ==================== Integration Log ====================

    async def create_log(self, log: IntegrationLog) -> IntegrationLog:
        """Cria um novo log."""
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_log_by_id(self, log_id: UUID) -> IntegrationLog | None:
        """Busca log por ID."""
        result = await self.db.execute(select(IntegrationLog).where(IntegrationLog.id == log_id))
        return result.scalar_one_or_none()

    async def list_logs(
        self,
        log_type: LogType | None = None,
        level: LogLevel | None = None,
        status: LogStatus | None = None,
        endpoint_id: UUID | None = None,
        api_key_id: UUID | None = None,
        webhook_id: UUID | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        client_id: UUID | None = None,
        user_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        error_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[IntegrationLog], int]:
        """Lista logs com filtros."""
        query = select(IntegrationLog)

        if log_type:
            query = query.where(IntegrationLog.log_type == log_type)
        if level:
            query = query.where(IntegrationLog.level == level)
        if status:
            query = query.where(IntegrationLog.status == status)
        if endpoint_id:
            query = query.where(IntegrationLog.endpoint_id == endpoint_id)
        if api_key_id:
            query = query.where(IntegrationLog.api_key_id == api_key_id)
        if webhook_id:
            query = query.where(IntegrationLog.webhook_id == webhook_id)
        if correlation_id:
            query = query.where(IntegrationLog.correlation_id == correlation_id)
        if trace_id:
            query = query.where(IntegrationLog.trace_id == trace_id)
        if client_id:
            query = query.where(IntegrationLog.client_id == client_id)
        if user_id:
            query = query.where(IntegrationLog.user_id == user_id)
        if start_date:
            query = query.where(IntegrationLog.timestamp >= start_date)
        if end_date:
            query = query.where(IntegrationLog.timestamp <= end_date)
        if error_only:
            query = query.where(
                IntegrationLog.status.in_([LogStatus.FAILURE, LogStatus.TIMEOUT, LogStatus.VALIDATION_ERROR])
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar() or 0

        # Paginate
        query = query.order_by(desc(IntegrationLog.timestamp)).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def get_logs_by_correlation_id(self, correlation_id: str) -> list[IntegrationLog]:
        """Busca logs por correlation ID."""
        result = await self.db.execute(
            select(IntegrationLog)
            .where(IntegrationLog.correlation_id == correlation_id)
            .order_by(IntegrationLog.timestamp)
        )
        return list(result.scalars().all())

    async def get_recent_errors(self, hours: int = 24, limit: int = 10) -> list[IntegrationLog]:
        """Busca erros recentes."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.db.execute(
            select(IntegrationLog)
            .where(IntegrationLog.timestamp >= since, IntegrationLog.status.in_([LogStatus.FAILURE, LogStatus.TIMEOUT]))
            .order_by(desc(IntegrationLog.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_log_stats(
        self, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Obtém estatísticas de logs."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=1)
        if not end_date:
            end_date = datetime.utcnow()

        # Total por status
        status_query = (
            select(IntegrationLog.status, func.count(IntegrationLog.id))
            .where(IntegrationLog.timestamp >= start_date, IntegrationLog.timestamp <= end_date)
            .group_by(IntegrationLog.status)
        )

        result = await self.db.execute(status_query)
        status_counts = {str(row[0].value): row[1] for row in result.all()}

        # Tempo médio de resposta
        avg_time_query = select(func.avg(IntegrationLog.duration_ms)).where(
            IntegrationLog.timestamp >= start_date,
            IntegrationLog.timestamp <= end_date,
            IntegrationLog.duration_ms.isnot(None),
        )
        avg_result = await self.db.execute(avg_time_query)
        avg_time = avg_result.scalar()

        return {
            "by_status": status_counts,
            "avg_response_time_ms": int(avg_time) if avg_time else None,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        }

    # ==================== Sync Queue ====================

    async def create_sync_item(self, item: SyncQueue) -> SyncQueue:
        """Cria item na fila de sync."""
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        logger.info(f"Sync item criado: {item.id}")
        return item

    async def create_sync_batch(self, items: list[SyncQueue]) -> list[SyncQueue]:
        """Cria múltiplos itens na fila."""
        self.db.add_all(items)
        await self.db.commit()
        for item in items:
            await self.db.refresh(item)
        logger.info(f"Batch de sync criado com {len(items)} itens")
        return items

    async def get_sync_item_by_id(self, item_id: UUID) -> SyncQueue | None:
        """Busca item da fila por ID."""
        result = await self.db.execute(select(SyncQueue).where(SyncQueue.id == item_id))
        return result.scalar_one_or_none()

    async def get_next_sync_items(
        self, limit: int = 10, external_system: ExternalSystem | None = None
    ) -> list[SyncQueue]:
        """Busca próximos itens para processar."""
        now = datetime.utcnow()

        query = select(SyncQueue).where(
            SyncQueue.ativo.is_(True),
            SyncQueue.requires_review.is_(False),
            or_(
                SyncQueue.status == SyncStatus.PENDING,
                and_(SyncQueue.status == SyncStatus.RETRYING, SyncQueue.next_retry_at <= now),
            ),
            or_(SyncQueue.not_before.is_(None), SyncQueue.not_before <= now),
            or_(SyncQueue.not_after.is_(None), SyncQueue.not_after > now),
        )

        if external_system:
            query = query.where(SyncQueue.external_system == external_system)

        # Ordena por prioridade (CRITICAL > HIGH > NORMAL > LOW > BATCH) e data agendada
        query = query.order_by(
            SyncQueue.priority.desc(), SyncQueue.scheduled_at.asc().nullsfirst(), SyncQueue.created_at.asc()
        ).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_sync_items(
        self,
        status: SyncStatus | None = None,
        priority: SyncPriority | None = None,
        entity_type: SyncEntityType | None = None,
        external_system: ExternalSystem | None = None,
        direction: SyncDirection | None = None,
        batch_id: UUID | None = None,
        correlation_id: str | None = None,
        requires_review: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SyncQueue], int]:
        """Lista itens da fila com filtros."""
        query = select(SyncQueue).where(SyncQueue.ativo.is_(True))

        if status:
            query = query.where(SyncQueue.status == status)
        if priority:
            query = query.where(SyncQueue.priority == priority)
        if entity_type:
            query = query.where(SyncQueue.entity_type == entity_type)
        if external_system:
            query = query.where(SyncQueue.external_system == external_system)
        if direction:
            query = query.where(SyncQueue.direction == direction)
        if batch_id:
            query = query.where(SyncQueue.batch_id == batch_id)
        if correlation_id:
            query = query.where(SyncQueue.correlation_id == correlation_id)
        if requires_review is not None:
            query = query.where(SyncQueue.requires_review == requires_review)
        if start_date:
            query = query.where(SyncQueue.created_at >= start_date)
        if end_date:
            query = query.where(SyncQueue.created_at <= end_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.execute(count_query)
        total_count = total.scalar() or 0

        # Paginate
        query = query.order_by(desc(SyncQueue.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total_count

    async def update_sync_item(self, item: SyncQueue) -> SyncQueue:
        """Atualiza item da fila."""
        item.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_sync_item(self, item_id: UUID) -> bool:
        """Deleta item da fila."""
        item = await self.get_sync_item_by_id(item_id)
        if item:
            item.ativo = False
            item.updated_at = datetime.utcnow()
            await self.db.commit()
            logger.info(f"Sync item deletado: {item_id}")
            return True
        return False

    async def get_sync_stats(self) -> dict[str, Any]:
        """Obtém estatísticas da fila."""
        # Total por status
        status_query = (
            select(SyncQueue.status, func.count(SyncQueue.id))
            .where(SyncQueue.ativo.is_(True))
            .group_by(SyncQueue.status)
        )

        result = await self.db.execute(status_query)
        status_counts = {str(row[0].value): row[1] for row in result.all()}

        # Por tipo de entidade
        entity_query = (
            select(SyncQueue.entity_type, func.count(SyncQueue.id))
            .where(SyncQueue.ativo.is_(True), SyncQueue.status.in_([SyncStatus.PENDING, SyncStatus.RETRYING]))
            .group_by(SyncQueue.entity_type)
        )

        entity_result = await self.db.execute(entity_query)
        entity_counts = {str(row[0].value): row[1] for row in entity_result.all()}

        # Por sistema externo
        system_query = (
            select(SyncQueue.external_system, func.count(SyncQueue.id))
            .where(SyncQueue.ativo.is_(True), SyncQueue.status.in_([SyncStatus.PENDING, SyncStatus.RETRYING]))
            .group_by(SyncQueue.external_system)
        )

        system_result = await self.db.execute(system_query)
        system_counts = {str(row[0].value): row[1] for row in system_result.all()}

        # Tempo médio de processamento
        avg_time_query = select(func.avg(SyncQueue.processing_time_ms)).where(
            SyncQueue.status == SyncStatus.COMPLETED, SyncQueue.processing_time_ms.isnot(None)
        )
        avg_result = await self.db.execute(avg_time_query)
        avg_time = avg_result.scalar()

        # Mais antigo pendente
        oldest_query = select(func.min(SyncQueue.created_at)).where(
            SyncQueue.ativo.is_(True), SyncQueue.status == SyncStatus.PENDING
        )
        oldest_result = await self.db.execute(oldest_query)
        oldest = oldest_result.scalar()

        # Requer revisão
        review_query = select(func.count()).where(SyncQueue.ativo.is_(True), SyncQueue.requires_review.is_(True))
        review_result = await self.db.execute(review_query)
        requires_review = review_result.scalar() or 0

        return {
            "total": sum(status_counts.values()),
            "by_status": status_counts,
            "by_entity_type": entity_counts,
            "by_external_system": system_counts,
            "avg_processing_time_ms": int(avg_time) if avg_time else None,
            "oldest_pending_at": oldest.isoformat() if oldest else None,
            "requires_review": requires_review,
        }

    async def cleanup_old_sync_items(self, days: int = 30, statuses: list[SyncStatus] | None = None) -> int:
        """Remove itens antigos da fila."""
        if not statuses:
            statuses = [SyncStatus.COMPLETED, SyncStatus.CANCELLED, SyncStatus.SKIPPED]

        cutoff = datetime.utcnow() - timedelta(days=days)

        query = select(SyncQueue).where(
            SyncQueue.ativo.is_(True), SyncQueue.status.in_(statuses), SyncQueue.completed_at < cutoff
        )

        result = await self.db.execute(query)
        items = result.scalars().all()

        count = 0
        for item in items:
            item.ativo = False
            count += 1

        await self.db.commit()
        logger.info(f"Removidos {count} itens antigos da fila de sync")
        return count
