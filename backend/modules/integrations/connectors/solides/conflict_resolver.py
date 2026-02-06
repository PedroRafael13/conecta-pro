"""
Resolvedor de conflitos para sincronização Sólides.
Sprint 33: Integration Framework

Implementa estratégias de resolução de conflitos entre dados
do Sólides e Conecta PRO.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from modules.integrations.connectors.solides.models import (
    SolidesSyncConflict,
    ConflictStatus,
    ConflictStrategy,
    SyncSource,
)
from modules.integrations.connectors.solides.mappers import detect_changes

logger = logging.getLogger(__name__)


class ConflictResolver:
    """
    Resolvedor de conflitos de sincronização.

    Estratégias disponíveis:
    - SOLIDES_WINS: Dados do Sólides sempre prevalecem
    - CONECTA_WINS: Dados do Conecta sempre prevalecem
    - MOST_RECENT: Dados mais recentes prevalecem
    - MANUAL: Requer resolução manual
    """

    def __init__(
        self,
        default_strategy: ConflictStrategy = ConflictStrategy.MOST_RECENT,
        field_strategies: Optional[Dict[str, ConflictStrategy]] = None,
        protected_fields: Optional[List[str]] = None
    ):
        """
        Inicializa o resolvedor.

        Args:
            default_strategy: Estratégia padrão para resolver conflitos
            field_strategies: Estratégias específicas por campo
            protected_fields: Campos que nunca devem ser sobrescritos
        """
        self.default_strategy = default_strategy
        self.field_strategies = field_strategies or {}
        self.protected_fields = protected_fields or []

    def has_conflict(
        self,
        solides_data: Dict[str, Any],
        conecta_data: Dict[str, Any],
        entity_type: str,
        last_sync_source: Optional[SyncSource] = None
    ) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
        """
        Detecta se há conflito entre dados.

        Args:
            solides_data: Dados do Sólides
            conecta_data: Dados do Conecta
            entity_type: Tipo da entidade
            last_sync_source: Fonte da última sincronização

        Returns:
            Tuple (tem_conflito, campos_alterados)
        """
        changes = detect_changes(conecta_data, solides_data, entity_type)

        if not changes:
            return False, {}

        # Se a última alteração foi do Sólides, não é conflito
        if last_sync_source == SyncSource.SOLIDES:
            return False, changes

        # Se foi alterado localmente desde última sync, é conflito
        if last_sync_source == SyncSource.CONECTA:
            return True, changes

        # Verificar campos específicos
        conflict_changes = {}
        for field, change in changes.items():
            if field in self.protected_fields:
                # Campos protegidos sempre geram conflito
                conflict_changes[field] = change
            elif conecta_data.get(field) is not None:
                # Campo foi modificado localmente
                conflict_changes[field] = change

        return bool(conflict_changes), conflict_changes

    def resolve(
        self,
        solides_data: Dict[str, Any],
        conecta_data: Dict[str, Any],
        entity_type: str,
        solides_updated_at: Optional[datetime] = None,
        conecta_updated_at: Optional[datetime] = None,
        strategy: Optional[ConflictStrategy] = None
    ) -> Tuple[Dict[str, Any], str]:
        """
        Resolve conflito entre dados.

        Args:
            solides_data: Dados do Sólides
            conecta_data: Dados do Conecta
            entity_type: Tipo da entidade
            solides_updated_at: Data de atualização no Sólides
            conecta_updated_at: Data de atualização no Conecta
            strategy: Estratégia a usar (ou default)

        Returns:
            Tuple (dados_resolvidos, strategy_used)
        """
        strategy = strategy or self.default_strategy

        if strategy == ConflictStrategy.MANUAL:
            # Retorna dados do Conecta sem alteração (conflito pendente)
            return conecta_data.copy(), "manual"

        if strategy == ConflictStrategy.SOLIDES_WINS:
            return self._merge_solides_wins(solides_data, conecta_data)

        if strategy == ConflictStrategy.CONECTA_WINS:
            return self._merge_conecta_wins(solides_data, conecta_data)

        if strategy == ConflictStrategy.MOST_RECENT:
            return self._merge_most_recent(
                solides_data, conecta_data,
                solides_updated_at, conecta_updated_at
            )

        # Fallback: Sólides wins
        return self._merge_solides_wins(solides_data, conecta_data)

    def _merge_solides_wins(
        self,
        solides_data: Dict[str, Any],
        conecta_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str]:
        """
        Merge onde Sólides prevalece (exceto campos protegidos).
        """
        result = conecta_data.copy()

        for key, value in solides_data.items():
            if key in self.protected_fields:
                continue  # Manter valor do Conecta

            # Usar estratégia específica do campo se existir
            field_strategy = self.field_strategies.get(key)
            if field_strategy == ConflictStrategy.CONECTA_WINS:
                continue

            result[key] = value

        return result, "solides_wins"

    def _merge_conecta_wins(
        self,
        solides_data: Dict[str, Any],
        conecta_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str]:
        """
        Merge onde Conecta prevalece (novos campos do Sólides são adicionados).
        """
        result = conecta_data.copy()

        for key, value in solides_data.items():
            # Adicionar apenas campos que não existem no Conecta
            if key not in result or result[key] is None:
                result[key] = value

            # Usar estratégia específica do campo se existir
            field_strategy = self.field_strategies.get(key)
            if field_strategy == ConflictStrategy.SOLIDES_WINS:
                result[key] = value

        return result, "conecta_wins"

    def _merge_most_recent(
        self,
        solides_data: Dict[str, Any],
        conecta_data: Dict[str, Any],
        solides_updated_at: Optional[datetime],
        conecta_updated_at: Optional[datetime]
    ) -> Tuple[Dict[str, Any], str]:
        """
        Merge onde dados mais recentes prevalecem.
        """
        # Se não tem timestamps, usa Sólides
        if not solides_updated_at and not conecta_updated_at:
            return self._merge_solides_wins(solides_data, conecta_data)

        # Se só tem um, usa esse
        if not solides_updated_at:
            return self._merge_conecta_wins(solides_data, conecta_data)
        if not conecta_updated_at:
            return self._merge_solides_wins(solides_data, conecta_data)

        # Comparar timestamps
        if solides_updated_at >= conecta_updated_at:
            return self._merge_solides_wins(solides_data, conecta_data)
        else:
            return self._merge_conecta_wins(solides_data, conecta_data)

    def resolve_conflict_record(
        self,
        db,
        conflict: SolidesSyncConflict,
        strategy: ConflictStrategy,
        resolved_by: Optional[UUID] = None,
        resolution_notes: Optional[str] = None
    ) -> Tuple[Dict[str, Any], SolidesSyncConflict]:
        """
        Resolve um registro de conflito salvo no banco.

        Args:
            db: Sessão do banco de dados
            conflict: Registro de conflito
            strategy: Estratégia a usar
            resolved_by: ID do usuário que resolveu
            resolution_notes: Notas sobre a resolução

        Returns:
            Tuple (dados_resolvidos, conflict_atualizado)
        """
        if conflict.status == ConflictStatus.RESOLVED:
            logger.warning(f"Conflito {conflict.id} já foi resolvido")
            return conflict.resolution_data, conflict

        resolved_data, strategy_used = self.resolve(
            solides_data=conflict.solides_data,
            conecta_data=conflict.conecta_data,
            entity_type=conflict.entity_type,
            solides_updated_at=conflict.solides_updated_at,
            conecta_updated_at=conflict.conecta_updated_at,
            strategy=strategy
        )

        # Atualizar registro
        conflict.status = ConflictStatus.RESOLVED
        conflict.resolved_at = datetime.utcnow()
        conflict.resolved_by = resolved_by
        conflict.resolution_strategy = strategy
        conflict.resolution_data = resolved_data
        conflict.resolution_notes = resolution_notes

        db.commit()
        db.refresh(conflict)

        logger.info(
            f"Conflito {conflict.id} resolvido usando estratégia {strategy_used}"
        )

        return resolved_data, conflict

    def ignore_conflict(
        self,
        db,
        conflict: SolidesSyncConflict,
        ignored_by: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> SolidesSyncConflict:
        """
        Marca conflito como ignorado.

        Args:
            db: Sessão do banco de dados
            conflict: Registro de conflito
            ignored_by: ID do usuário
            notes: Notas

        Returns:
            Conflict atualizado
        """
        conflict.status = ConflictStatus.IGNORED
        conflict.resolved_at = datetime.utcnow()
        conflict.resolved_by = ignored_by
        conflict.resolution_notes = notes

        db.commit()
        db.refresh(conflict)

        logger.info(f"Conflito {conflict.id} marcado como ignorado")

        return conflict


# ==================== ESTRATÉGIAS PRÉ-CONFIGURADAS ====================

def get_employee_conflict_resolver() -> ConflictResolver:
    """
    Retorna resolver configurado para colaboradores.

    Campos protegidos (nunca sobrescritos do Sólides):
    - Nenhum por padrão

    Campos que Sólides sempre ganha:
    - situacao (status)
    - data_demissao
    - cargo_id, departamento_id
    """
    return ConflictResolver(
        default_strategy=ConflictStrategy.MOST_RECENT,
        field_strategies={
            "situacao": ConflictStrategy.SOLIDES_WINS,
            "status": ConflictStrategy.SOLIDES_WINS,
            "data_demissao": ConflictStrategy.SOLIDES_WINS,
            "termination_date": ConflictStrategy.SOLIDES_WINS,
            "cargo_id": ConflictStrategy.SOLIDES_WINS,
            "departamento_id": ConflictStrategy.SOLIDES_WINS,
            "salario": ConflictStrategy.SOLIDES_WINS,
        },
        protected_fields=[
            # Campos que nunca devem ser sobrescritos
        ]
    )


def get_department_conflict_resolver() -> ConflictResolver:
    """
    Retorna resolver configurado para departamentos.
    Sólides sempre ganha para departamentos.
    """
    return ConflictResolver(
        default_strategy=ConflictStrategy.SOLIDES_WINS,
        protected_fields=[]
    )


def get_occurrence_conflict_resolver() -> ConflictResolver:
    """
    Retorna resolver configurado para ocorrências.
    Dados mais recentes prevalecem.
    """
    return ConflictResolver(
        default_strategy=ConflictStrategy.MOST_RECENT,
        field_strategies={
            "tipo": ConflictStrategy.SOLIDES_WINS,
            "data": ConflictStrategy.SOLIDES_WINS,
        }
    )


def get_resolver_for_entity(entity_type: str) -> ConflictResolver:
    """
    Retorna resolver apropriado para tipo de entidade.

    Args:
        entity_type: Tipo da entidade

    Returns:
        ConflictResolver configurado
    """
    resolvers = {
        "colaboradores": get_employee_conflict_resolver,
        "departamentos": get_department_conflict_resolver,
        "cargos": get_department_conflict_resolver,  # Mesmo comportamento
        "ocorrencias": get_occurrence_conflict_resolver,
        "absenteismos": get_occurrence_conflict_resolver,
    }

    resolver_factory = resolvers.get(entity_type)
    if resolver_factory:
        return resolver_factory()

    # Default: Most recent
    return ConflictResolver(default_strategy=ConflictStrategy.MOST_RECENT)
