"""Gerenciador de sincronização offline."""

import hashlib
import logging
import uuid
from datetime import datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.mobile.models.mobile_session import MobileSession
from modules.mobile.models.sync_queue import (
    ConflictResolution,
    SyncOperationType,
    SyncQueueItem,
    SyncStatus,
)
from modules.mobile.schemas.sync_schemas import (
    MobileSyncOperation,
    MobileSyncRequest,
    MobileSyncResponse,
    ServerChange,
    SyncConflict,
    SyncOperationResult,
)

logger = logging.getLogger(__name__)


class OfflineSyncManager:
    """
    Gerenciador de sincronização offline.

    Responsabilidades:
    - Processar operações offline do cliente
    - Detectar e resolver conflitos
    - Gerar delta de mudanças do servidor
    - Manter tokens de sincronização
    """

    # Tabelas sincronizáveis e seus campos essenciais
    SYNCABLE_TABLES = {
        "leads": {
            "id_field": "id",
            "timestamp_field": "updated_at",
            "essential_fields": ["id", "name", "email", "phone", "status", "updated_at"],
            "conflict_resolution": ConflictResolution.LAST_WRITE_WINS,
        },
        "opportunities": {
            "id_field": "id",
            "timestamp_field": "updated_at",
            "essential_fields": ["id", "lead_id", "title", "value", "stage", "updated_at"],
            "conflict_resolution": ConflictResolution.LAST_WRITE_WINS,
        },
        "proposals": {
            "id_field": "id",
            "timestamp_field": "updated_at",
            "essential_fields": ["id", "opportunity_id", "status", "total_value", "updated_at"],
            "conflict_resolution": ConflictResolution.USER_DECIDES,
        },
        "tasks": {
            "id_field": "id",
            "timestamp_field": "updated_at",
            "essential_fields": ["id", "title", "status", "due_date", "completed_at", "updated_at"],
            "conflict_resolution": ConflictResolution.MERGE,
        },
        "contacts": {
            "id_field": "id",
            "timestamp_field": "updated_at",
            "essential_fields": ["id", "name", "email", "phone", "company", "updated_at"],
            "conflict_resolution": ConflictResolution.LAST_WRITE_WINS,
        },
    }

    def __init__(
        self,
        max_operations_per_sync: int = 100,
        max_server_changes: int = 500,
        conflict_window_seconds: int = 300,  # 5 minutos
    ) -> None:
        """
        Inicializa o manager.

        Args:
            max_operations_per_sync: Máximo de operações por sincronização
            max_server_changes: Máximo de mudanças do servidor por sync
            conflict_window_seconds: Janela de tempo para detectar conflitos
        """
        self.max_operations = max_operations_per_sync
        self.max_server_changes = max_server_changes
        self.conflict_window = conflict_window_seconds

    async def process_sync(
        self,
        db: AsyncSession,
        user_id: int,
        sync_request: MobileSyncRequest,
    ) -> MobileSyncResponse:
        """
        Processa requisição de sincronização.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            sync_request: Requisição de sync

        Returns:
            Response com resultados e mudanças do servidor
        """
        start_time = datetime.utcnow()

        # Obter ou criar sessão mobile
        device_id = sync_request.device_info.device_id if sync_request.device_info else None
        session = await self._get_or_create_session(db, user_id, device_id)

        # Validar sync token
        last_sync = await self._validate_sync_token(session, sync_request.last_sync_token)

        # Processar operações do cliente
        operation_results = []
        conflicts = []

        for operation in sync_request.operations[: self.max_operations]:
            result, conflict = await self._process_operation(db, user_id, operation, last_sync)
            operation_results.append(result)
            if conflict:
                conflicts.append(conflict)

        # Buscar mudanças do servidor
        server_changes = await self._get_server_changes(
            db, user_id, last_sync, sync_request.tables or list(self.SYNCABLE_TABLES.keys())
        )

        # Gerar novo sync token
        new_sync_token = self._generate_sync_token(user_id, start_time)

        # Atualizar sessão
        session.sync_token = new_sync_token
        session.last_sync_at = start_time
        session.pending_operations = len([r for r in operation_results if r.status in ["pending", "conflict"]])
        session.connection_quality = sync_request.connection_quality

        await db.commit()

        return MobileSyncResponse(
            timestamp=start_time,
            user_id=user_id,
            operations=operation_results,
            server_changes=server_changes,
            conflicts=conflicts,
            new_sync_token=new_sync_token,
        )

    async def _get_or_create_session(
        self,
        db: AsyncSession,
        user_id: int,
        device_id: str,
    ) -> MobileSession:
        """Obtém ou cria sessão mobile."""
        query = select(MobileSession).where(
            MobileSession.user_id == user_id,
            MobileSession.device_id == device_id,
        )
        result = await db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            session = MobileSession(
                user_id=user_id,
                device_id=device_id,
                sync_token=self._generate_sync_token(user_id, datetime.utcnow()),
            )
            db.add(session)
            await db.flush()

        return session

    async def _validate_sync_token(
        self,
        session: MobileSession,
        sync_token: str | None,
    ) -> datetime | None:
        """
        Valida sync token e retorna timestamp do último sync.

        Returns:
            DateTime do último sync ou None para sync completo
        """
        if not sync_token:
            # Primeiro sync
            return None

        if sync_token != session.sync_token:
            # Token inválido, forçar sync completo
            logger.warning(f"Invalid sync token for session {session.id}")
            return None

        return session.last_sync_at

    def _generate_sync_token(self, user_id: int, timestamp: datetime) -> str:
        """Gera novo sync token."""
        data = f"{user_id}:{timestamp.isoformat()}:{uuid.uuid4().hex}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    async def _process_operation(
        self,
        db: AsyncSession,
        user_id: int,
        operation: MobileSyncOperation,
        last_sync: datetime | None,
    ) -> tuple[SyncOperationResult, SyncConflict | None]:
        """
        Processa uma operação de sync.

        Returns:
            Tupla (resultado, conflito_se_houver)
        """
        table_config = self.SYNCABLE_TABLES.get(operation.table)
        if not table_config:
            return SyncOperationResult(
                id=operation.id,
                status="rejected",
                error="Unknown table",
            ), None

        # Verificar conflito
        conflict = await self._detect_conflict(db, operation, last_sync, table_config)

        if conflict:
            # Aplicar estratégia de resolução
            resolved, conflict_result = await self._resolve_conflict(db, user_id, operation, conflict, table_config)

            if not resolved:
                return SyncOperationResult(
                    id=operation.id,
                    status="conflict",
                    conflict_id=str(uuid.uuid4()),
                ), conflict_result

        # Aplicar operação
        try:
            await self._apply_operation(db, user_id, operation)
            return SyncOperationResult(
                id=operation.id,
                status="applied",
                server_timestamp=datetime.utcnow(),
            ), None

        except Exception as e:
            logger.error(f"Error applying operation {operation.id}: {e}")
            return SyncOperationResult(
                id=operation.id,
                status="error",
                error=str(e),
            ), None

    async def _detect_conflict(
        self,
        db: AsyncSession,
        operation: MobileSyncOperation,
        last_sync: datetime | None,
        table_config: dict,
    ) -> dict | None:
        """
        Detecta conflito com dados do servidor.

        Returns:
            Dados do servidor se houver conflito, None caso contrário
        """
        if operation.operation == "create":
            # Create não tem conflito (exceto duplicata)
            return None

        if not last_sync:
            # Primeiro sync, sem conflito temporal
            return None

        # Verificar se registro foi modificado no servidor após last_sync
        # Isso seria feito consultando a tabela real
        # Por ora, retornamos None (sem conflito)

        # query = select(Model).where(
        #     Model.id == operation.record_id,
        #     Model.updated_at > last_sync,
        #     Model.updated_at > operation.timestamp,
        # )

        return None

    async def _resolve_conflict(
        self,
        db: AsyncSession,
        user_id: int,
        operation: MobileSyncOperation,
        server_data: dict,
        table_config: dict,
    ) -> tuple[bool, SyncConflict | None]:
        """
        Resolve conflito entre cliente e servidor.

        Returns:
            Tupla (resolvido_automaticamente, conflito_para_usuário)
        """
        strategy = table_config.get("conflict_resolution", ConflictResolution.LAST_WRITE_WINS)

        if strategy == ConflictResolution.LAST_WRITE_WINS:
            # Cliente mais recente vence
            if operation.timestamp > server_data.get("updated_at", datetime.min):
                return True, None
            else:
                # Servidor vence, rejeitar operação do cliente
                return True, None

        elif strategy == ConflictResolution.SERVER_WINS:
            # Servidor sempre vence
            return True, None

        elif strategy == ConflictResolution.CLIENT_WINS:
            # Cliente sempre vence
            return True, None

        elif strategy == ConflictResolution.MERGE:
            # Tentar merge automático
            merged = self._auto_merge(operation.data or {}, server_data)
            if merged:
                operation.data = merged
                return True, None
            # Falha no merge, usuário decide
            return False, SyncConflict(
                operation_id=operation.id,
                table=operation.table,
                record_id=operation.record_id,
                client_data=operation.data,
                server_data=server_data,
                conflict_type="update_conflict",
                resolution_required=True,
            )

        else:  # USER_DECIDES
            return False, SyncConflict(
                operation_id=operation.id,
                table=operation.table,
                record_id=operation.record_id,
                client_data=operation.data,
                server_data=server_data,
                conflict_type="update_conflict",
                resolution_required=True,
            )

    def _auto_merge(
        self,
        client_data: dict,
        server_data: dict,
    ) -> dict | None:
        """
        Tenta merge automático de dados.

        Campos diferentes são mesclados.
        Campos iguais modificados em ambos causam falha.

        Returns:
            Dados mesclados ou None se conflito
        """
        merged = dict(server_data)
        client_changes = set(client_data.keys())
        server_changes = set(server_data.keys())

        # Campos alterados em ambos (potencial conflito)
        both_changed = client_changes & server_changes

        for field in both_changed:
            if client_data.get(field) != server_data.get(field):
                # Valores diferentes para mesmo campo = conflito
                return None

        # Mesclar campos do cliente que não conflitam
        for field in client_changes - both_changed:
            merged[field] = client_data[field]

        return merged

    async def _apply_operation(
        self,
        db: AsyncSession,
        user_id: int,
        operation: MobileSyncOperation,
    ) -> None:
        """Aplica operação no banco de dados."""
        # Criar item na fila de sync para processamento
        queue_item = SyncQueueItem(
            user_id=user_id,
            device_id=operation.id.split("_")[0] if "_" in operation.id else "unknown",
            operation_type=SyncOperationType(operation.operation),
            table_name=operation.table,
            record_id=operation.record_id,
            data=operation.data,
            changed_fields=operation.changed_fields,
            client_timestamp=operation.timestamp,
            status=SyncStatus.COMPLETED,
            processed_at=datetime.utcnow(),
        )
        db.add(queue_item)

        logger.info(f"Applied operation: {operation.operation} on {operation.table}:{operation.record_id}")

    async def _get_server_changes(
        self,
        db: AsyncSession,
        user_id: int,
        since: datetime | None,
        tables: list[str],
    ) -> list[ServerChange]:
        """
        Obtém mudanças do servidor desde último sync.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            since: Timestamp do último sync
            tables: Tabelas para sincronizar

        Returns:
            Lista de mudanças
        """
        changes = []

        # Se primeiro sync, retornar dados essenciais
        if not since:
            since = datetime.utcnow() - timedelta(days=30)  # Últimos 30 dias

        for table in tables:
            if table not in self.SYNCABLE_TABLES:
                continue

            self.SYNCABLE_TABLES[table]

            # Por ora, retornar lista vazia (sem mudanças)

            # Exemplo de como seria:
            # query = select(Model).where(
            #     Model.updated_at > since,
            #     Model.user_id == user_id,  # ou filtro apropriado
            # ).order_by(Model.updated_at).limit(self.max_server_changes)
            #
            # for record in await db.execute(query):
            #     changes.append(ServerChange(
            #         table=table,
            #         operation="update",
            #         record_id=str(record.id),
            #         data=record.to_dict(),
            #         timestamp=record.updated_at,
            #     ))

        return changes[: self.max_server_changes]

    async def resolve_user_conflict(
        self,
        db: AsyncSession,
        user_id: int,
        conflict_id: str,
        resolution: str,  # "use_client", "use_server", "merge"
        merged_data: dict | None = None,
    ) -> SyncOperationResult:
        """
        Resolve conflito decidido pelo usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            conflict_id: ID do conflito
            resolution: Tipo de resolução
            merged_data: Dados mesclados (se resolution="merge")

        Returns:
            Resultado da operação
        """
        # Buscar operação pendente
        query = select(SyncQueueItem).where(
            SyncQueueItem.user_id == user_id,
            SyncQueueItem.status == SyncStatus.CONFLICT,
        )
        result = await db.execute(query)
        queue_item = result.scalar_one_or_none()

        if not queue_item:
            return SyncOperationResult(
                id=conflict_id,
                status="error",
                error="Conflict not found",
            )

        if resolution == "use_client":
            # Aplicar dados do cliente
            queue_item.status = SyncStatus.COMPLETED
            queue_item.processed_at = datetime.utcnow()

        elif resolution == "use_server":
            # Descartar operação do cliente
            queue_item.status = SyncStatus.COMPLETED
            queue_item.processed_at = datetime.utcnow()
            queue_item.data = None  # Marca como descartada

        elif resolution == "merge" and merged_data:
            # Aplicar dados mesclados
            queue_item.data = merged_data
            queue_item.status = SyncStatus.COMPLETED
            queue_item.processed_at = datetime.utcnow()

        else:
            return SyncOperationResult(
                id=conflict_id,
                status="error",
                error="Invalid resolution",
            )

        await db.commit()

        return SyncOperationResult(
            id=conflict_id,
            status="resolved",
            server_timestamp=datetime.utcnow(),
        )

    async def get_pending_operations(
        self,
        db: AsyncSession,
        user_id: int,
        device_id: str,
    ) -> list[SyncQueueItem]:
        """Obtém operações pendentes para um dispositivo."""
        query = (
            select(SyncQueueItem)
            .where(
                SyncQueueItem.user_id == user_id,
                SyncQueueItem.device_id == device_id,
                SyncQueueItem.status.in_(
                    [
                        SyncStatus.PENDING,
                        SyncStatus.CONFLICT,
                    ]
                ),
            )
            .order_by(SyncQueueItem.client_timestamp)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def cleanup_old_sync_data(
        self,
        db: AsyncSession,
        days: int = 30,
    ) -> int:
        """Remove dados de sync antigos."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Deletar operações completadas antigas
        query = delete(SyncQueueItem).where(
            SyncQueueItem.created_at < cutoff,
            SyncQueueItem.status == SyncStatus.COMPLETED,
        )

        result = await db.execute(query)
        await db.commit()

        deleted = result.rowcount
        logger.info(f"Cleaned up {deleted} old sync queue items")
        return deleted

    async def get_sync_status(
        self,
        db: AsyncSession,
        user_id: int,
        device_id: str,
    ) -> dict:
        """Obtém status de sincronização do dispositivo."""
        session = await self._get_or_create_session(db, user_id, device_id)

        # Contar operações pendentes
        pending_query = select(func.count()).where(
            SyncQueueItem.user_id == user_id,
            SyncQueueItem.device_id == device_id,
            SyncQueueItem.status == SyncStatus.PENDING,
        )
        pending_result = await db.execute(pending_query)
        pending_count = pending_result.scalar() or 0

        # Contar conflitos
        conflict_query = select(func.count()).where(
            SyncQueueItem.user_id == user_id,
            SyncQueueItem.device_id == device_id,
            SyncQueueItem.status == SyncStatus.CONFLICT,
        )
        conflict_result = await db.execute(conflict_query)
        conflict_count = conflict_result.scalar() or 0

        return {
            "last_sync_at": session.last_sync_at,
            "sync_token": session.sync_token,
            "pending_operations": pending_count,
            "conflicts": conflict_count,
            "cache_version": session.cache_version,
            "offline_data_size": session.offline_data_size,
        }
