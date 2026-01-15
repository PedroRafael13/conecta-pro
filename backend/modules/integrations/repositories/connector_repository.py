"""
Repository para Conectores Externos
Sprint 33: Integration Framework
"""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.models.integration_account import IntegrationAccount
from modules.integrations.models.sync_run import SyncRun
from modules.integrations.models.sync_state import SyncState
from modules.integrations.models.id_map import IDMap

logger = logging.getLogger(__name__)


class ConnectorRepository:
    """Repository para operações de dados de conectores."""

    def __init__(self, db: AsyncSession):
        """Inicializa o repository."""
        self.db = db

    # ==================== Integration Account ====================

    async def create_account(self, account: IntegrationAccount) -> IntegrationAccount:
        """Cria uma nova conta de integração."""
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        logger.info(f"Conta de integração criada: {account.id}")
        return account

    async def get_account_by_id(
        self,
        account_id: UUID,
        tenant_id: Optional[UUID] = None,
        include_inactive: bool = False
    ) -> Optional[IntegrationAccount]:
        """Busca conta por ID."""
        conditions = [IntegrationAccount.id == account_id]

        if tenant_id:
            conditions.append(IntegrationAccount.tenant_id == tenant_id)

        if not include_inactive:
            conditions.append(IntegrationAccount.ativo == True)

        query = select(IntegrationAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_accounts(
        self,
        tenant_id: UUID,
        connector_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[IntegrationAccount], int]:
        """Lista contas com paginação."""
        conditions = [
            IntegrationAccount.tenant_id == tenant_id,
            IntegrationAccount.ativo == True
        ]

        if connector_type:
            conditions.append(IntegrationAccount.connector_type == connector_type)
        if status:
            conditions.append(IntegrationAccount.status == status)

        # Query com filtros
        query = select(IntegrationAccount).where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(
            IntegrationAccount.created_at.desc()
        )

        result = await self.db.execute(query)
        accounts = list(result.scalars().all())

        return accounts, total

    async def update_account(self, account: IntegrationAccount) -> IntegrationAccount:
        """Atualiza conta de integração."""
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def delete_account(
        self,
        account_id: UUID,
        tenant_id: UUID,
        user_id: Optional[UUID] = None
    ) -> bool:
        """Soft delete de conta."""
        account = await self.get_account_by_id(account_id, tenant_id)
        if not account:
            return False

        account.ativo = False
        account.updated_by = user_id
        await self.db.commit()
        return True

    async def get_accounts_for_sync(
        self,
        connector_type: Optional[str] = None
    ) -> List[IntegrationAccount]:
        """Busca contas que precisam de sync."""
        now = datetime.utcnow()

        conditions = [
            IntegrationAccount.ativo == True,
            IntegrationAccount.sync_enabled == True,
            IntegrationAccount.status.in_(["active", "pending_auth"]),
        ]

        if connector_type:
            conditions.append(IntegrationAccount.connector_type == connector_type)

        query = select(IntegrationAccount).where(and_(*conditions))
        result = await self.db.execute(query)
        accounts = list(result.scalars().all())

        # Filtrar as que estão no horário de sync
        due_accounts = []
        for account in accounts:
            if account.next_sync_at is None or account.next_sync_at <= now:
                due_accounts.append(account)

        return due_accounts

    # ==================== Sync Run ====================

    async def create_sync_run(self, sync_run: SyncRun) -> SyncRun:
        """Cria um novo registro de sync run."""
        self.db.add(sync_run)
        await self.db.commit()
        await self.db.refresh(sync_run)
        logger.info(f"Sync run criado: {sync_run.id}")
        return sync_run

    async def get_sync_run_by_id(
        self,
        run_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> Optional[SyncRun]:
        """Busca sync run por ID."""
        conditions = [SyncRun.id == run_id]

        if tenant_id:
            conditions.append(SyncRun.tenant_id == tenant_id)

        query = select(SyncRun).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_sync_runs(
        self,
        tenant_id: UUID,
        account_id: Optional[UUID] = None,
        connector_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SyncRun], int]:
        """Lista sync runs com paginação."""
        conditions = [
            SyncRun.tenant_id == tenant_id,
            SyncRun.ativo == True
        ]

        if account_id:
            conditions.append(SyncRun.account_id == account_id)
        if connector_type:
            conditions.append(SyncRun.connector_type == connector_type)
        if status:
            conditions.append(SyncRun.status == status)

        query = select(SyncRun).where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(
            SyncRun.created_at.desc()
        )

        result = await self.db.execute(query)
        runs = list(result.scalars().all())

        return runs, total

    async def update_sync_run(self, sync_run: SyncRun) -> SyncRun:
        """Atualiza sync run."""
        await self.db.commit()
        await self.db.refresh(sync_run)
        return sync_run

    async def get_running_sync_for_account(
        self,
        account_id: UUID
    ) -> Optional[SyncRun]:
        """Verifica se há sync em execução para a conta."""
        query = select(SyncRun).where(
            SyncRun.account_id == account_id,
            SyncRun.status.in_(["pending", "running"])
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # ==================== Sync State ====================

    async def get_sync_state(
        self,
        account_id: UUID,
        entity_type: str
    ) -> Optional[SyncState]:
        """Busca estado de sync de uma entidade."""
        query = select(SyncState).where(
            SyncState.account_id == account_id,
            SyncState.entity_type == entity_type
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def upsert_sync_state(
        self,
        account_id: UUID,
        tenant_id: UUID,
        entity_type: str,
        **kwargs
    ) -> SyncState:
        """Cria ou atualiza estado de sync."""
        state = await self.get_sync_state(account_id, entity_type)

        if state:
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
        else:
            state = SyncState(
                account_id=account_id,
                tenant_id=tenant_id,
                entity_type=entity_type,
                **kwargs
            )
            self.db.add(state)

        await self.db.commit()
        await self.db.refresh(state)
        return state

    async def list_sync_states(
        self,
        account_id: UUID
    ) -> List[SyncState]:
        """Lista estados de sync de uma conta."""
        query = select(SyncState).where(
            SyncState.account_id == account_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== ID Map ====================

    async def get_id_mapping(
        self,
        account_id: UUID,
        entity_type: str,
        external_id: Optional[str] = None,
        internal_id: Optional[UUID] = None
    ) -> Optional[IDMap]:
        """Busca mapeamento de ID."""
        conditions = [
            IDMap.account_id == account_id,
            IDMap.entity_type == entity_type
        ]

        if external_id:
            conditions.append(IDMap.external_id == external_id)
        if internal_id:
            conditions.append(IDMap.internal_id == internal_id)

        query = select(IDMap).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_id_mapping(self, id_map: IDMap) -> IDMap:
        """Cria mapeamento de ID."""
        self.db.add(id_map)
        await self.db.commit()
        await self.db.refresh(id_map)
        return id_map

    async def update_id_mapping(self, id_map: IDMap) -> IDMap:
        """Atualiza mapeamento de ID."""
        await self.db.commit()
        await self.db.refresh(id_map)
        return id_map

    async def list_id_mappings(
        self,
        account_id: UUID,
        entity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[IDMap], int]:
        """Lista mapeamentos de ID."""
        conditions = [IDMap.account_id == account_id]

        if entity_type:
            conditions.append(IDMap.entity_type == entity_type)

        query = select(IDMap).where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginação
        query = query.offset(skip).limit(limit).order_by(
            IDMap.last_synced_at.desc()
        )

        result = await self.db.execute(query)
        mappings = list(result.scalars().all())

        return mappings, total

    async def delete_id_mappings_for_account(
        self,
        account_id: UUID
    ) -> int:
        """Remove todos os mapeamentos de uma conta."""
        query = select(IDMap).where(IDMap.account_id == account_id)
        result = await self.db.execute(query)
        mappings = list(result.scalars().all())

        count = len(mappings)
        for mapping in mappings:
            await self.db.delete(mapping)

        await self.db.commit()
        return count
