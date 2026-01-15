"""
ConnectorService - Serviço para gerenciamento de conectores externos
Sprint 33: Integration Framework
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from modules.integrations.models.integration_account import IntegrationAccount
from modules.integrations.models.sync_run import SyncRun
from modules.integrations.models.sync_state import SyncState
from modules.integrations.models.id_map import IDMap
from modules.integrations.sync.engine import ConnectorRegistry, SyncEngine
from modules.integrations.schemas.connector_schemas import (
    IntegrationAccountCreate,
    IntegrationAccountUpdate,
    SyncRunCreate,
    ConnectorStats,
    IntegrationStats,
)

logger = logging.getLogger(__name__)


class ConnectorService:
    """Serviço para gerenciamento de conectores externos."""

    def __init__(self, db: AsyncSession):
        """Inicializa o serviço."""
        self.db = db

    # ==================== Connectors ====================

    def list_available_connectors(self) -> List[Dict[str, Any]]:
        """Lista conectores disponíveis no sistema."""
        connectors = []
        for name, connector_class in ConnectorRegistry.list_connectors().items():
            try:
                temp_instance = connector_class.__new__(connector_class)
                temp_instance._credentials = {}
                temp_instance._config = {}
                caps = temp_instance.capabilities

                connectors.append({
                    "name": connector_class.NAME,
                    "version": connector_class.VERSION,
                    "supported_entities": caps.supported_entities,
                    "supports_incremental_sync": caps.supports_incremental_sync,
                    "supports_webhooks": caps.supports_webhooks,
                    "supports_write": caps.supports_write,
                    "rate_limit_per_second": caps.rate_limit_per_second,
                    "rate_limit_per_minute": caps.rate_limit_per_minute,
                })
            except Exception as e:
                logger.warning(f"Erro ao obter info do conector {name}: {e}")
                continue

        return connectors

    def get_connector_info(self, connector_name: str) -> Optional[Dict[str, Any]]:
        """Retorna informações de um conector específico."""
        connector_class = ConnectorRegistry.get(connector_name)
        if not connector_class:
            return None

        try:
            temp_instance = connector_class.__new__(connector_class)
            temp_instance._credentials = {}
            temp_instance._config = {}
            caps = temp_instance.capabilities

            return {
                "name": connector_class.NAME,
                "version": connector_class.VERSION,
                "supported_entities": caps.supported_entities,
                "supports_incremental_sync": caps.supports_incremental_sync,
                "supports_full_sync": caps.supports_full_sync,
                "supports_webhooks": caps.supports_webhooks,
                "supports_write": caps.supports_write,
                "supports_delete": caps.supports_delete,
                "rate_limit_per_second": caps.rate_limit_per_second,
                "rate_limit_per_minute": caps.rate_limit_per_minute,
            }
        except Exception as e:
            logger.error(f"Erro ao obter info do conector {connector_name}: {e}")
            return None

    # ==================== Integration Accounts ====================

    async def create_account(
        self,
        data: IntegrationAccountCreate,
        tenant_id: UUID,
        user_id: Optional[UUID] = None
    ) -> IntegrationAccount:
        """Cria uma nova conta de integração."""
        # Verificar se conector existe
        if not ConnectorRegistry.get(data.connector_type):
            raise ValueError(f"Conector '{data.connector_type}' não disponível")

        auth_type = self._get_auth_type(data.connector_type)

        account = IntegrationAccount(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            connector_type=data.connector_type,
            auth_type=auth_type,
            environment=data.environment,
            extra_config=data.config or {},
            sync_enabled=data.sync_enabled,
            sync_interval_minutes=data.sync_interval_minutes,
            sync_entities=data.sync_entities,
            status="pending_auth",
            created_by=user_id,
        )

        # Criptografar e armazenar credenciais
        account.set_credentials(data.credentials)

        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        logger.info(f"Conta de integração criada: {account.id} ({data.connector_type})")
        return account

    async def get_account(
        self,
        account_id: UUID,
        tenant_id: UUID
    ) -> Optional[IntegrationAccount]:
        """Busca conta por ID."""
        query = select(IntegrationAccount).where(
            IntegrationAccount.id == account_id,
            IntegrationAccount.tenant_id == tenant_id,
            IntegrationAccount.ativo == True
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_accounts(
        self,
        tenant_id: UUID,
        connector_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[IntegrationAccount], int, int]:
        """Lista contas com paginação."""
        query = select(IntegrationAccount).where(
            IntegrationAccount.tenant_id == tenant_id,
            IntegrationAccount.ativo == True
        )

        if connector_type:
            query = query.where(IntegrationAccount.connector_type == connector_type)
        if status:
            query = query.where(IntegrationAccount.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(
            IntegrationAccount.created_at.desc()
        )

        result = await self.db.execute(query)
        accounts = list(result.scalars().all())

        pages = (total + page_size - 1) // page_size

        return accounts, total, pages

    async def update_account(
        self,
        account_id: UUID,
        tenant_id: UUID,
        data: IntegrationAccountUpdate,
        user_id: Optional[UUID] = None
    ) -> Optional[IntegrationAccount]:
        """Atualiza uma conta de integração."""
        account = await self.get_account(account_id, tenant_id)
        if not account:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "credentials" in update_data and update_data["credentials"]:
            account.set_credentials(update_data.pop("credentials"))

        if "config" in update_data:
            account.extra_config = update_data.pop("config")

        for key, value in update_data.items():
            setattr(account, key, value)

        account.updated_by = user_id

        await self.db.commit()
        await self.db.refresh(account)

        return account

    async def delete_account(
        self,
        account_id: UUID,
        tenant_id: UUID,
        user_id: Optional[UUID] = None
    ) -> bool:
        """Remove (soft delete) uma conta de integração."""
        account = await self.get_account(account_id, tenant_id)
        if not account:
            return False

        account.ativo = False
        account.updated_by = user_id

        await self.db.commit()
        return True

    # ==================== Health Check ====================

    async def health_check(
        self,
        account_id: UUID,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Verifica saúde da conexão com o sistema externo."""
        account = await self.get_account(account_id, tenant_id)
        if not account:
            raise ValueError("Conta não encontrada")

        connector_class = ConnectorRegistry.get(account.connector_type)
        if not connector_class:
            raise ValueError(f"Conector '{account.connector_type}' não disponível")

        try:
            credentials = account.get_credentials()
            config = account.extra_config or {}
            config["base_url"] = account.base_url

            connector = connector_class(
                credentials=credentials,
                config=config
            )

            health_result = await connector.health_check()

            # Atualizar account com resultado
            account.last_health_check_at = datetime.utcnow()
            account.last_health_check_status = health_result.healthy
            account.last_health_check_latency_ms = health_result.latency_ms

            if health_result.healthy:
                account.status = "active"
                account.health_check_failures = 0
            else:
                account.health_check_failures = (account.health_check_failures or 0) + 1
                if account.health_check_failures >= 3:
                    account.status = "error"

            await self.db.commit()

            return {
                "connector": account.connector_type,
                "healthy": health_result.healthy,
                "latency_ms": health_result.latency_ms,
                "message": health_result.message,
                "details": health_result.details
            }

        except Exception as e:
            logger.error(f"Erro no health check da conta {account_id}: {e}")

            account.last_health_check_at = datetime.utcnow()
            account.last_health_check_status = False
            account.health_check_failures = (account.health_check_failures or 0) + 1
            account.last_error = str(e)
            account.last_error_at = datetime.utcnow()

            await self.db.commit()

            return {
                "connector": account.connector_type,
                "healthy": False,
                "latency_ms": 0,
                "message": str(e),
                "details": {"error_type": type(e).__name__}
            }

    # ==================== Sync Runs ====================

    async def create_sync_run(
        self,
        data: SyncRunCreate,
        tenant_id: UUID,
        user_id: Optional[UUID] = None
    ) -> SyncRun:
        """Cria um registro de sync run."""
        account = await self.get_account(UUID(data.account_id), tenant_id)
        if not account:
            raise ValueError("Conta não encontrada")

        if account.status not in ["active", "pending_auth"]:
            raise ValueError(f"Conta em status '{account.status}' não pode executar sync")

        sync_run = SyncRun(
            tenant_id=tenant_id,
            account_id=account.id,
            connector_type=account.connector_type,
            mode=data.mode,
            trigger="manual",
            triggered_by=user_id,
            entities=data.entities or account.sync_entities,
            status="pending",
        )

        self.db.add(sync_run)
        await self.db.commit()
        await self.db.refresh(sync_run)

        return sync_run

    async def get_sync_run(
        self,
        run_id: UUID,
        tenant_id: UUID
    ) -> Optional[SyncRun]:
        """Busca sync run por ID."""
        query = select(SyncRun).where(
            SyncRun.id == run_id,
            SyncRun.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_sync_runs(
        self,
        tenant_id: UUID,
        account_id: Optional[UUID] = None,
        connector_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[SyncRun], int, int]:
        """Lista sync runs com paginação."""
        query = select(SyncRun).where(
            SyncRun.tenant_id == tenant_id,
            SyncRun.ativo == True
        )

        if account_id:
            query = query.where(SyncRun.account_id == account_id)
        if connector_type:
            query = query.where(SyncRun.connector_type == connector_type)
        if status:
            query = query.where(SyncRun.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(
            SyncRun.created_at.desc()
        )

        result = await self.db.execute(query)
        runs = list(result.scalars().all())

        pages = (total + page_size - 1) // page_size

        return runs, total, pages

    async def cancel_sync_run(
        self,
        run_id: UUID,
        tenant_id: UUID,
        user_email: Optional[str] = None
    ) -> Optional[SyncRun]:
        """Cancela um sync run em andamento."""
        sync_run = await self.get_sync_run(run_id, tenant_id)
        if not sync_run:
            return None

        if sync_run.status not in ["pending", "running"]:
            raise ValueError(
                f"Execução em status '{sync_run.status}' não pode ser cancelada"
            )

        sync_run.status = "cancelled"
        sync_run.status_message = f"Cancelado por {user_email}" if user_email else "Cancelado"

        await self.db.commit()
        await self.db.refresh(sync_run)

        return sync_run

    # ==================== Sync State ====================

    async def get_sync_states(
        self,
        account_id: UUID,
        tenant_id: UUID
    ) -> List[SyncState]:
        """Retorna estados de sync de uma conta."""
        query = select(SyncState).where(
            SyncState.account_id == account_id,
            SyncState.tenant_id == tenant_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== ID Mapping ====================

    async def list_id_mappings(
        self,
        account_id: UUID,
        tenant_id: UUID,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[IDMap], int, int]:
        """Lista mapeamentos de ID."""
        # Verificar se account pertence ao tenant
        account = await self.get_account(account_id, tenant_id)
        if not account:
            raise ValueError("Conta não encontrada")

        query = select(IDMap).where(
            IDMap.account_id == account_id
        )

        if entity_type:
            query = query.where(IDMap.entity_type == entity_type)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(
            IDMap.last_synced_at.desc()
        )

        result = await self.db.execute(query)
        mappings = list(result.scalars().all())

        pages = (total + page_size - 1) // page_size

        return mappings, total, pages

    # ==================== Statistics ====================

    async def get_stats(self, tenant_id: UUID) -> IntegrationStats:
        """Retorna estatísticas de integração."""
        # Contas por status
        accounts_query = select(
            IntegrationAccount.status,
            func.count(IntegrationAccount.id)
        ).where(
            IntegrationAccount.tenant_id == tenant_id,
            IntegrationAccount.ativo == True
        ).group_by(IntegrationAccount.status)

        accounts_result = await self.db.execute(accounts_query)
        accounts_by_status = dict(accounts_result.all())

        total_accounts = sum(accounts_by_status.values())
        active_accounts = accounts_by_status.get("active", 0)
        error_accounts = accounts_by_status.get("error", 0)

        # Syncs hoje
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        syncs_query = select(
            SyncRun.status,
            func.count(SyncRun.id)
        ).where(
            SyncRun.tenant_id == tenant_id,
            SyncRun.created_at >= today_start
        ).group_by(SyncRun.status)

        syncs_result = await self.db.execute(syncs_query)
        syncs_by_status = dict(syncs_result.all())

        syncs_today = sum(syncs_by_status.values())
        syncs_success = syncs_by_status.get("completed", 0)
        syncs_failed = syncs_by_status.get("failed", 0)

        # Items sincronizados hoje
        items_query = select(
            func.coalesce(func.sum(SyncRun.items_processed), 0)
        ).where(
            SyncRun.tenant_id == tenant_id,
            SyncRun.created_at >= today_start,
            SyncRun.status == "completed"
        )
        items_result = await self.db.execute(items_query)
        items_synced = items_result.scalar() or 0

        # Stats por conector
        connector_stats = await self._get_connector_stats(tenant_id, today_start)

        return IntegrationStats(
            total_accounts=total_accounts,
            active_accounts=active_accounts,
            error_accounts=error_accounts,
            syncs_today=syncs_today,
            syncs_success_today=syncs_success,
            syncs_failed_today=syncs_failed,
            items_synced_today=items_synced,
            connectors=connector_stats
        )

    async def _get_connector_stats(
        self,
        tenant_id: UUID,
        today_start: datetime
    ) -> List[ConnectorStats]:
        """Retorna estatísticas por conector."""
        # Contas por conector
        accounts_query = select(
            IntegrationAccount.connector_type,
            IntegrationAccount.status,
            func.count(IntegrationAccount.id)
        ).where(
            IntegrationAccount.tenant_id == tenant_id,
            IntegrationAccount.ativo == True
        ).group_by(
            IntegrationAccount.connector_type,
            IntegrationAccount.status
        )

        accounts_result = await self.db.execute(accounts_query)
        accounts_data = accounts_result.all()

        # Organizar por conector
        connector_data: Dict[str, Dict[str, int]] = {}
        for connector_type, status, count in accounts_data:
            if connector_type not in connector_data:
                connector_data[connector_type] = {"total": 0, "active": 0, "error": 0}
            connector_data[connector_type]["total"] += count
            if status == "active":
                connector_data[connector_type]["active"] += count
            elif status == "error":
                connector_data[connector_type]["error"] += count

        # Items sincronizados por conector
        items_query = select(
            SyncRun.connector_type,
            func.sum(SyncRun.items_processed).label("synced"),
            func.sum(SyncRun.items_failed).label("failed")
        ).where(
            SyncRun.tenant_id == tenant_id,
            SyncRun.created_at >= today_start
        ).group_by(SyncRun.connector_type)

        items_result = await self.db.execute(items_query)
        items_data = {row[0]: (row[1] or 0, row[2] or 0) for row in items_result.all()}

        stats = []
        for connector_type, data in connector_data.items():
            synced, failed = items_data.get(connector_type, (0, 0))
            stats.append(ConnectorStats(
                connector_type=connector_type,
                accounts_total=data["total"],
                accounts_active=data["active"],
                accounts_error=data["error"],
                last_sync_success=None,
                last_sync_failure=None,
                items_synced_24h=synced,
                items_failed_24h=failed,
                avg_sync_duration_seconds=None
            ))

        return stats

    # ==================== Helpers ====================

    def _get_auth_type(self, connector_name: str) -> str:
        """Retorna tipo de autenticação do conector."""
        auth_types = {
            "bling": "api_key",
            "solides": "oauth2_client_credentials",
            "dominio": "api_key",
            "omie": "api_key",
            "nibo": "oauth2",
            "totvs": "oauth2",
            "sap": "oauth2",
        }
        return auth_types.get(connector_name, "api_key")
