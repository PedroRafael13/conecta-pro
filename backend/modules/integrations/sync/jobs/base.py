"""
Base SyncJob para integrações.
Sprint 33: Integration Framework
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.connectors.base.connector import BaseConnector
from modules.integrations.models.id_map import IDMap
from modules.integrations.models.sync_state import SyncState

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class SyncJobResult:
    """Resultado de um sync job."""

    success: bool
    entity_type: str
    items_total: int = 0
    items_processed: int = 0
    items_created: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    items_failed: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)
    last_cursor: str | None = None
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class SyncJob[T](ABC):
    """
    Classe base abstrata para sync jobs.
    Um sync job processa uma entidade específica de um conector.
    """

    # Tipo de entidade (deve ser sobrescrito)
    ENTITY_TYPE: str = "unknown"

    def __init__(
        self,
        connector: BaseConnector,
        db: AsyncSession,
        tenant_id: UUID,
        account_id: UUID,
        correlation_id: str | None = None,
    ):
        """
        Inicializa o sync job.

        Args:
            connector: Conector configurado
            db: Sessão do banco de dados
            tenant_id: ID do tenant
            account_id: ID da conta de integração
            correlation_id: ID para correlação de logs
        """
        self.connector = connector
        self.db = db
        self.tenant_id = tenant_id
        self.account_id = account_id
        self.correlation_id = correlation_id or f"sync-{self.ENTITY_TYPE}"

        # Estatísticas
        self._items_created = 0
        self._items_updated = 0
        self._items_skipped = 0
        self._items_failed = 0
        self._errors: list[dict[str, Any]] = []

    @abstractmethod
    async def map_to_internal(self, external_data: dict[str, Any]) -> T:
        """
        Mapeia dados externos para modelo interno.

        Args:
            external_data: Dados do sistema externo

        Returns:
            Objeto do modelo interno
        """
        pass

    @abstractmethod
    async def save_entity(self, entity: T, external_id: str) -> UUID:
        """
        Salva entidade no banco de dados.

        Args:
            entity: Entidade mapeada
            external_id: ID no sistema externo

        Returns:
            ID interno da entidade
        """
        pass

    @abstractmethod
    async def get_existing_entity(self, internal_id: UUID) -> T | None:
        """
        Busca entidade existente pelo ID interno.

        Args:
            internal_id: ID interno

        Returns:
            Entidade ou None
        """
        pass

    def get_external_id(self, data: dict[str, Any]) -> str:
        """
        Extrai ID externo dos dados.
        Pode ser sobrescrito se o campo for diferente.
        """
        return str(data.get("id", data.get("codigo", data.get("ID", ""))))

    def get_external_updated_at(self, data: dict[str, Any]) -> datetime | None:
        """
        Extrai data de modificação dos dados.
        Pode ser sobrescrito.
        """
        updated = data.get("updated_at", data.get("dataAlteracao", data.get("modificado")))
        if updated:
            if isinstance(updated, datetime):
                return updated
            try:
                return datetime.fromisoformat(updated.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        return None

    async def get_id_mapping(self, external_id: str) -> IDMap | None:
        """Busca mapeamento de ID existente."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(IDMap).where(
                IDMap.tenant_id == self.tenant_id,
                IDMap.account_id == self.account_id,
                IDMap.entity_type == self.ENTITY_TYPE,
                IDMap.external_id == external_id,
                IDMap.ativo.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def create_id_mapping(self, external_id: str, internal_id: UUID, data_hash: str | None = None) -> IDMap:
        """Cria novo mapeamento de ID."""
        mapping = IDMap.create_mapping(
            tenant_id=str(self.tenant_id),
            account_id=str(self.account_id),
            connector_type=self.connector.NAME,
            entity_type=self.ENTITY_TYPE,
            external_id=external_id,
            internal_id=str(internal_id),
            data_hash=data_hash,
        )
        self.db.add(mapping)
        return mapping

    async def process_item(self, data: dict[str, Any]) -> bool:
        """
        Processa um item individual.

        Args:
            data: Dados do item externo

        Returns:
            True se processado com sucesso
        """
        external_id = self.get_external_id(data)

        if not external_id:
            logger.warning(f"[{self.correlation_id}] Item sem ID externo, pulando")
            self._items_skipped += 1
            return False

        try:
            # Verificar se já existe mapeamento
            existing_mapping = await self.get_id_mapping(external_id)

            if existing_mapping:
                # Atualizar entidade existente
                existing_entity = await self.get_existing_entity(existing_mapping.internal_id)

                if existing_entity:
                    # Mapear e atualizar
                    updated_entity = await self.map_to_internal(data)
                    internal_id = await self.save_entity(updated_entity, external_id)

                    # Atualizar mapeamento
                    existing_mapping.mark_synced(direction="inbound")
                    self._items_updated += 1

                    logger.debug(f"[{self.correlation_id}] Atualizado: {external_id} -> {internal_id}")
                else:
                    # Entidade foi deletada internamente, recriar
                    new_entity = await self.map_to_internal(data)
                    internal_id = await self.save_entity(new_entity, external_id)

                    existing_mapping.internal_id = internal_id
                    existing_mapping.mark_synced(direction="inbound")
                    self._items_created += 1

                    logger.debug(f"[{self.correlation_id}] Recriado: {external_id} -> {internal_id}")
            else:
                # Nova entidade
                new_entity = await self.map_to_internal(data)
                internal_id = await self.save_entity(new_entity, external_id)

                # Criar mapeamento
                await self.create_id_mapping(external_id, internal_id)
                self._items_created += 1

                logger.debug(f"[{self.correlation_id}] Criado: {external_id} -> {internal_id}")

            return True

        except Exception as e:
            self._items_failed += 1
            self._errors.append({"external_id": external_id, "error": str(e), "error_type": type(e).__name__})
            logger.error(f"[{self.correlation_id}] Erro ao processar {external_id}: {e}")
            return False

    async def run(
        self,
        sync_state: SyncState | None = None,
        full_sync: bool = False,
        page_size: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> SyncJobResult:
        """
        Executa o sync job.

        Args:
            sync_state: Estado de sync anterior (para incremental)
            full_sync: Forçar full sync
            page_size: Tamanho da página
            filters: Filtros adicionais

        Returns:
            SyncJobResult com estatísticas
        """
        import time

        start_time = time.monotonic()

        logger.info(f"[{self.correlation_id}] Iniciando sync de {self.ENTITY_TYPE} (full={full_sync})")

        # Determinar cursor e updated_since
        updated_since = None

        if not full_sync and sync_state and sync_state.has_valid_cursor:
            updated_since = sync_state.last_sync_timestamp

        items_total = 0
        last_cursor = None

        try:
            # Iterar páginas
            async for page_result in self.connector.fetch_all_entities(
                entity_type=self.ENTITY_TYPE, updated_since=updated_since, page_size=page_size, filters=filters
            ):
                if not page_result.success:
                    logger.warning(f"[{self.correlation_id}] Página retornou erro: {page_result.errors}")
                    self._errors.extend(page_result.errors)
                    continue

                if page_result.data:
                    items_total += len(page_result.data)

                    for item in page_result.data:
                        await self.process_item(item)

                last_cursor = page_result.cursor

            # Commit final
            await self.db.commit()

            duration_ms = int((time.monotonic() - start_time) * 1000)

            result = SyncJobResult(
                success=True,
                entity_type=self.ENTITY_TYPE,
                items_total=items_total,
                items_processed=self._items_created + self._items_updated,
                items_created=self._items_created,
                items_updated=self._items_updated,
                items_skipped=self._items_skipped,
                items_failed=self._items_failed,
                errors=self._errors,
                last_cursor=last_cursor,
                duration_ms=duration_ms,
            )

            logger.info(
                f"[{self.correlation_id}] Sync de {self.ENTITY_TYPE} concluído: "
                f"total={items_total}, criados={self._items_created}, "
                f"atualizados={self._items_updated}, falhas={self._items_failed}, "
                f"duração={duration_ms}ms"
            )

            return result

        except Exception as e:
            await self.db.rollback()
            duration_ms = int((time.monotonic() - start_time) * 1000)

            logger.error(f"[{self.correlation_id}] Erro no sync de {self.ENTITY_TYPE}: {e}")

            return SyncJobResult(
                success=False,
                entity_type=self.ENTITY_TYPE,
                items_total=items_total,
                items_processed=self._items_created + self._items_updated,
                items_created=self._items_created,
                items_updated=self._items_updated,
                items_skipped=self._items_skipped,
                items_failed=self._items_failed,
                errors=[*self._errors, {"error": str(e), "fatal": True}],
                last_cursor=last_cursor,
                duration_ms=duration_ms,
            )
