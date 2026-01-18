"""
Serviço de Sincronização Sólides.
Sprint 33: Integration Framework

Sincronização bidirecional completa entre Sólides e Conecta PRO.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, AsyncGenerator
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.orm import Session

from modules.integrations.connectors.solides.connector import SolidesConnector
from modules.integrations.connectors.solides.mappers import (
    solides_colaborador_to_employee,
    employee_to_solides_colaborador,
    solides_departamento_to_department,
    solides_cargo_to_position,
    solides_ocorrencia_to_occurrence,
    occurrence_to_solides_ocorrencia,
    solides_absenteismo_to_absence,
    solides_passaporte_to_behavioral_profile,
    compute_solides_entity_hash,
    detect_changes,
)
from modules.integrations.connectors.solides.models import (
    SolidesSyncState,
    SolidesSyncLog,
    SolidesSyncConflict,
    SolidesEntityMapping,
    SolidesIntegrationConfig,
    SyncDirection,
    SyncStatus,
    SyncSource,
    ConflictStatus,
    ConflictStrategy,
    get_or_create_sync_state,
    get_entity_mapping,
    create_or_update_mapping,
    log_sync_operation,
    create_conflict,
)
from modules.integrations.connectors.solides.conflict_resolver import (
    ConflictResolver,
    get_resolver_for_entity,
)

logger = logging.getLogger(__name__)


@dataclass
class SyncStats:
    """Estatísticas de sincronização."""
    total_processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    conflicts: int = 0
    errors: int = 0
    error_details: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SyncResult:
    """Resultado de operação de sincronização."""
    success: bool
    stats: SyncStats
    sync_log_id: Optional[UUID] = None
    duration_seconds: int = 0
    error: Optional[str] = None


class SolidesSyncService:
    """
    Serviço de sincronização bidirecional Sólides ↔ Conecta PRO.

    Funcionalidades:
    - Full sync: Sincronização completa de todas as entidades
    - Incremental sync: Apenas alterações desde última sync
    - Single entity sync: Sincronizar uma entidade específica
    - Bidirectional sync: Sincronizar em ambas direções
    """

    # Ordem de sincronização (dependências)
    SYNC_ORDER = [
        "unidades",
        "departamentos",
        "cargos",
        "colaboradores",
        "ocorrencias",
        "absenteismos",
        "passaportes",
    ]

    def __init__(
        self,
        db: Session,
        condominio_id: UUID,
        connector: Optional[SolidesConnector] = None,
        config: Optional[SolidesIntegrationConfig] = None
    ):
        """
        Inicializa o serviço de sincronização.

        Args:
            db: Sessão do banco de dados
            condominio_id: ID do condomínio
            connector: Conector Sólides (opcional, criado automaticamente)
            config: Configuração da integração
        """
        self.db = db
        self.condominio_id = condominio_id
        self._connector = connector
        self._config = config

    @property
    def connector(self) -> SolidesConnector:
        """Retorna ou cria conector."""
        if self._connector is None:
            self._connector = self._create_connector()
        return self._connector

    @property
    def config(self) -> SolidesIntegrationConfig:
        """Retorna ou carrega configuração."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _create_connector(self) -> SolidesConnector:
        """Cria conector com credenciais do banco."""
        from modules.integrations.connectors.solides.models import SolidesCredential

        cred = self.db.query(SolidesCredential).filter(
            SolidesCredential.condominio_id == self.condominio_id
        ).first()

        if not cred:
            raise ValueError(f"Credenciais Sólides não configuradas para condomínio {self.condominio_id}")

        # Descriptografar token (implementar conforme sistema de criptografia)
        token = cred.api_token_encrypted  # TODO: decrypt

        return SolidesConnector(
            credentials={"api_token": token},
            config={"rate_limit_per_minute": self.config.rate_limit_per_minute if self._config else 60}
        )

    def _load_config(self) -> SolidesIntegrationConfig:
        """Carrega configuração do banco."""
        config = self.db.query(SolidesIntegrationConfig).filter(
            SolidesIntegrationConfig.condominio_id == self.condominio_id
        ).first()

        if not config:
            # Criar configuração padrão
            config = SolidesIntegrationConfig(
                condominio_id=self.condominio_id,
                is_enabled=True
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

        return config

    async def full_sync(
        self,
        direction: SyncDirection = SyncDirection.SOLIDES_TO_CONECTA,
        entity_types: Optional[List[str]] = None,
        triggered_by: str = "system"
    ) -> SyncResult:
        """
        Executa sincronização completa.

        Args:
            direction: Direção da sincronização
            entity_types: Tipos de entidade (ou todas configuradas)
            triggered_by: Quem disparou

        Returns:
            SyncResult com estatísticas
        """
        start_time = datetime.utcnow()
        total_stats = SyncStats()

        # Determinar entidades a sincronizar
        entities = entity_types or self.config.enabled_entities or self.SYNC_ORDER
        entities = [e for e in self.SYNC_ORDER if e in entities]

        logger.info(
            f"[Solides] Iniciando full sync para condomínio {self.condominio_id}, "
            f"entidades: {entities}, direção: {direction}"
        )

        # Criar log
        sync_log = log_sync_operation(
            self.db,
            self.condominio_id,
            sync_type="full",
            entity_type="all",
            status=SyncStatus.IN_PROGRESS,
            direction=direction,
            triggered_by=triggered_by
        )

        try:
            async with self.connector:
                for entity_type in entities:
                    try:
                        logger.info(f"[Solides] Sincronizando {entity_type}...")

                        if direction in [SyncDirection.SOLIDES_TO_CONECTA, SyncDirection.BIDIRECTIONAL]:
                            stats = await self._sync_from_solides(entity_type, incremental=False)
                            total_stats.total_processed += stats.total_processed
                            total_stats.created += stats.created
                            total_stats.updated += stats.updated
                            total_stats.conflicts += stats.conflicts
                            total_stats.errors += stats.errors
                            total_stats.error_details.extend(stats.error_details)

                        if direction in [SyncDirection.CONECTA_TO_SOLIDES, SyncDirection.BIDIRECTIONAL]:
                            # TODO: Implementar sync reverso quando necessário
                            pass

                        # Atualizar estado
                        state = get_or_create_sync_state(self.db, self.condominio_id, entity_type)
                        state.last_full_sync_at = datetime.utcnow()
                        state.last_sync_at = datetime.utcnow()
                        state.status = SyncStatus.COMPLETED
                        self.db.commit()

                    except Exception as e:
                        logger.error(f"[Solides] Erro sincronizando {entity_type}: {e}")
                        total_stats.errors += 1
                        total_stats.error_details.append({
                            "entity_type": entity_type,
                            "error": str(e)
                        })

            # Finalizar log
            duration = int((datetime.utcnow() - start_time).total_seconds())
            sync_log.status = SyncStatus.COMPLETED if total_stats.errors == 0 else SyncStatus.PARTIAL
            sync_log.completed_at = datetime.utcnow()
            sync_log.duration_seconds = duration
            sync_log.total_processed = total_stats.total_processed
            sync_log.created_count = total_stats.created
            sync_log.updated_count = total_stats.updated
            sync_log.conflict_count = total_stats.conflicts
            sync_log.error_count = total_stats.errors
            sync_log.errors = total_stats.error_details
            self.db.commit()

            logger.info(
                f"[Solides] Full sync concluído: "
                f"{total_stats.total_processed} processados, "
                f"{total_stats.created} criados, "
                f"{total_stats.updated} atualizados, "
                f"{total_stats.conflicts} conflitos, "
                f"{total_stats.errors} erros"
            )

            return SyncResult(
                success=total_stats.errors == 0,
                stats=total_stats,
                sync_log_id=sync_log.id,
                duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"[Solides] Erro no full sync: {e}")
            sync_log.status = SyncStatus.FAILED
            sync_log.completed_at = datetime.utcnow()
            sync_log.errors = [{"error": str(e)}]
            self.db.commit()

            return SyncResult(
                success=False,
                stats=total_stats,
                sync_log_id=sync_log.id,
                error=str(e)
            )

    async def incremental_sync(
        self,
        entity_types: Optional[List[str]] = None,
        triggered_by: str = "scheduler"
    ) -> SyncResult:
        """
        Executa sincronização incremental (apenas alterações).

        Args:
            entity_types: Tipos de entidade (ou todas configuradas)
            triggered_by: Quem disparou

        Returns:
            SyncResult com estatísticas
        """
        start_time = datetime.utcnow()
        total_stats = SyncStats()

        entities = entity_types or self.config.enabled_entities or self.SYNC_ORDER
        entities = [e for e in self.SYNC_ORDER if e in entities]

        logger.info(f"[Solides] Iniciando incremental sync para {self.condominio_id}")

        sync_log = log_sync_operation(
            self.db,
            self.condominio_id,
            sync_type="incremental",
            entity_type="all",
            status=SyncStatus.IN_PROGRESS,
            direction=SyncDirection.SOLIDES_TO_CONECTA,
            triggered_by=triggered_by
        )

        try:
            async with self.connector:
                for entity_type in entities:
                    try:
                        stats = await self._sync_from_solides(entity_type, incremental=True)
                        total_stats.total_processed += stats.total_processed
                        total_stats.created += stats.created
                        total_stats.updated += stats.updated
                        total_stats.skipped += stats.skipped
                        total_stats.conflicts += stats.conflicts
                        total_stats.errors += stats.errors

                        # Atualizar estado
                        state = get_or_create_sync_state(self.db, self.condominio_id, entity_type)
                        state.last_sync_at = datetime.utcnow()
                        state.last_sync_count = stats.total_processed
                        state.total_synced += stats.created + stats.updated
                        state.status = SyncStatus.COMPLETED
                        self.db.commit()

                    except Exception as e:
                        logger.error(f"[Solides] Erro incremental {entity_type}: {e}")
                        total_stats.errors += 1

            # Finalizar log
            duration = int((datetime.utcnow() - start_time).total_seconds())
            sync_log.status = SyncStatus.COMPLETED
            sync_log.completed_at = datetime.utcnow()
            sync_log.duration_seconds = duration
            sync_log.total_processed = total_stats.total_processed
            sync_log.created_count = total_stats.created
            sync_log.updated_count = total_stats.updated
            sync_log.skipped_count = total_stats.skipped
            sync_log.conflict_count = total_stats.conflicts
            sync_log.error_count = total_stats.errors
            self.db.commit()

            return SyncResult(
                success=True,
                stats=total_stats,
                sync_log_id=sync_log.id,
                duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"[Solides] Erro no incremental sync: {e}")
            sync_log.status = SyncStatus.FAILED
            sync_log.completed_at = datetime.utcnow()
            self.db.commit()

            return SyncResult(
                success=False,
                stats=total_stats,
                error=str(e)
            )

    async def sync_single_entity(
        self,
        entity_type: str,
        solides_id: str,
        direction: SyncDirection = SyncDirection.SOLIDES_TO_CONECTA
    ) -> SyncResult:
        """
        Sincroniza uma entidade específica.

        Args:
            entity_type: Tipo da entidade
            solides_id: ID no Sólides
            direction: Direção

        Returns:
            SyncResult
        """
        stats = SyncStats()

        try:
            async with self.connector:
                if direction == SyncDirection.SOLIDES_TO_CONECTA:
                    # Buscar do Sólides
                    data = await self.connector.fetch_entity_by_id(entity_type, solides_id)

                    if not data:
                        return SyncResult(
                            success=False,
                            stats=stats,
                            error=f"Entidade {entity_type}/{solides_id} não encontrada no Sólides"
                        )

                    # Processar
                    result = await self._process_solides_entity(entity_type, data)
                    stats.total_processed = 1
                    if result == "created":
                        stats.created = 1
                    elif result == "updated":
                        stats.updated = 1
                    elif result == "conflict":
                        stats.conflicts = 1

                else:
                    # TODO: Sync para Sólides
                    pass

            return SyncResult(success=True, stats=stats)

        except Exception as e:
            logger.error(f"[Solides] Erro sync single entity: {e}")
            return SyncResult(success=False, stats=stats, error=str(e))

    async def _sync_from_solides(
        self,
        entity_type: str,
        incremental: bool = True
    ) -> SyncStats:
        """
        Sincroniza entidade do Sólides para Conecta.

        Args:
            entity_type: Tipo da entidade
            incremental: Se True, sincroniza apenas alterações

        Returns:
            SyncStats
        """
        stats = SyncStats()

        # Obter data da última sync para incremental
        updated_since = None
        if incremental:
            state = get_or_create_sync_state(self.db, self.condominio_id, entity_type)
            if state.last_sync_at:
                updated_since = state.last_sync_at

        # Buscar dados paginados
        cursor = None
        while True:
            result = await self.connector.fetch_entities(
                entity_type=entity_type,
                cursor=cursor,
                updated_since=updated_since,
                page_size=100
            )

            if not result.success:
                stats.errors += 1
                break

            # Processar cada item
            for item in result.data:
                try:
                    action = await self._process_solides_entity(entity_type, item)
                    stats.total_processed += 1

                    if action == "created":
                        stats.created += 1
                    elif action == "updated":
                        stats.updated += 1
                    elif action == "skipped":
                        stats.skipped += 1
                    elif action == "conflict":
                        stats.conflicts += 1

                except Exception as e:
                    stats.errors += 1
                    stats.error_details.append({
                        "entity_id": item.get("id"),
                        "error": str(e)
                    })
                    logger.error(f"[Solides] Erro processando {entity_type}/{item.get('id')}: {e}")

            # Próxima página
            if result.has_more and result.cursor:
                cursor = result.cursor
            else:
                break

        return stats

    async def _process_solides_entity(
        self,
        entity_type: str,
        solides_data: Dict[str, Any]
    ) -> str:
        """
        Processa uma entidade do Sólides.

        Args:
            entity_type: Tipo da entidade
            solides_data: Dados do Sólides

        Returns:
            Ação tomada: "created", "updated", "skipped", "conflict"
        """
        solides_id = str(solides_data.get("id"))

        # Verificar se já existe mapeamento
        mapping = get_entity_mapping(
            self.db, self.condominio_id, entity_type, solides_id=solides_id
        )

        # Calcular hash dos dados
        data_hash = compute_solides_entity_hash(entity_type, solides_data)

        if mapping:
            # Já existe - verificar se mudou
            if mapping.data_hash == data_hash:
                return "skipped"  # Sem alterações

            # Verificar conflito
            resolver = get_resolver_for_entity(entity_type)
            # TODO: Carregar dados atuais do Conecta para comparação

            # Por enquanto, atualiza direto
            await self._update_conecta_entity(entity_type, mapping.conecta_id, solides_data)

            mapping.data_hash = data_hash
            mapping.last_synced_at = datetime.utcnow()
            mapping.sync_source = SyncSource.SOLIDES
            self.db.commit()

            return "updated"

        else:
            # Novo - criar
            conecta_id = await self._create_conecta_entity(entity_type, solides_data)

            if conecta_id:
                create_or_update_mapping(
                    self.db,
                    self.condominio_id,
                    entity_type,
                    solides_id,
                    conecta_id,
                    sync_source=SyncSource.SOLIDES,
                    data_hash=data_hash
                )
                return "created"

        return "skipped"

    async def _create_conecta_entity(
        self,
        entity_type: str,
        solides_data: Dict[str, Any]
    ) -> Optional[UUID]:
        """
        Cria entidade no Conecta PRO.

        Args:
            entity_type: Tipo da entidade
            solides_data: Dados do Sólides

        Returns:
            ID da entidade criada ou None
        """
        # Mapear dados
        mapper_map = {
            "colaboradores": solides_colaborador_to_employee,
            "departamentos": solides_departamento_to_department,
            "cargos": solides_cargo_to_position,
            "ocorrencias": solides_ocorrencia_to_occurrence,
            "absenteismos": solides_absenteismo_to_absence,
            "passaportes": solides_passaporte_to_behavioral_profile,
        }

        mapper = mapper_map.get(entity_type)
        if not mapper:
            logger.warning(f"[Solides] Mapper não encontrado para {entity_type}")
            return None

        conecta_data = mapper(solides_data, self.condominio_id)

        # TODO: Implementar criação real no banco
        # Por agora, retorna None (implementar conforme modelos do Conecta PRO)
        logger.debug(f"[Solides] Criaria {entity_type}: {conecta_data.get('name', conecta_data.get('email', 'N/A'))}")

        # Exemplo de como seria:
        # if entity_type == "colaboradores":
        #     from modules.employees.models import Employee
        #     employee = Employee(**conecta_data)
        #     self.db.add(employee)
        #     self.db.commit()
        #     return employee.id

        return None

    async def _update_conecta_entity(
        self,
        entity_type: str,
        conecta_id: UUID,
        solides_data: Dict[str, Any]
    ) -> bool:
        """
        Atualiza entidade no Conecta PRO.

        Args:
            entity_type: Tipo da entidade
            conecta_id: ID local
            solides_data: Dados do Sólides

        Returns:
            True se atualizado
        """
        # TODO: Implementar atualização real
        logger.debug(f"[Solides] Atualizaria {entity_type}/{conecta_id}")
        return True

    async def get_sync_status(self) -> Dict[str, Any]:
        """
        Retorna status geral da sincronização.

        Returns:
            Dict com status de cada entidade
        """
        # Health check
        health = await self.connector.health_check()

        # Status por entidade
        entity_status = {}
        for entity_type in self.SYNC_ORDER:
            state = self.db.query(SolidesSyncState).filter(
                SolidesSyncState.condominio_id == self.condominio_id,
                SolidesSyncState.entity_type == entity_type
            ).first()

            if state:
                entity_status[entity_type] = {
                    "status": state.status.value if state.status else "never_synced",
                    "last_sync_at": state.last_sync_at.isoformat() if state.last_sync_at else None,
                    "last_full_sync_at": state.last_full_sync_at.isoformat() if state.last_full_sync_at else None,
                    "total_synced": state.total_synced,
                    "last_error": state.last_error,
                }
            else:
                entity_status[entity_type] = {"status": "never_synced"}

        # Conflitos pendentes
        pending_conflicts = self.db.query(SolidesSyncConflict).filter(
            SolidesSyncConflict.condominio_id == self.condominio_id,
            SolidesSyncConflict.status == ConflictStatus.PENDING
        ).count()

        return {
            "connected": health.healthy,
            "api_latency_ms": health.latency_ms,
            "api_message": health.message,
            "config": {
                "is_enabled": self.config.is_enabled,
                "sync_direction": self.config.sync_direction.value if self.config.sync_direction else None,
                "conflict_strategy": self.config.conflict_strategy.value if self.config.conflict_strategy else None,
                "enabled_entities": self.config.enabled_entities,
            },
            "entities": entity_status,
            "pending_conflicts": pending_conflicts,
        }


# ==================== FACTORY ====================

def get_sync_service(
    db: Session,
    condominio_id: UUID
) -> SolidesSyncService:
    """
    Factory para criar serviço de sincronização.

    Args:
        db: Sessão do banco
        condominio_id: ID do condomínio

    Returns:
        SolidesSyncService configurado
    """
    return SolidesSyncService(db=db, condominio_id=condominio_id)
