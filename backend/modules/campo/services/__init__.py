"""Services do modulo Campo v3.0.0."""

# =============================================================================
# Legacy - Portaria Remota
# =============================================================================
from .checklist_service import ChecklistService
from .estoque_integration import (
    EstoqueIntegrationService,
    StatusRequisicao,
    TipoMovimentacao,
    get_estoque_integration_service,
)
from .guardian_sync_service import GuardianSyncService
from .occurrence_analyzer import OccurrenceAnalyzer

# =============================================================================
# CAMPO - Ordens de Servico, Visitas, Checklists
# =============================================================================
from .ordem_servico_service import OrdemServicoService
from .roteirizacao_service import (
    PontoRota,
    RoteirizacaoService,
    RoteiroOtimizado,
    StatusRoteiro,
    TipoOtimizacao,
    get_roteirizacao_service,
)
from .visita_service import VisitaService

__all__ = [
    # Legacy
    "GuardianSyncService",
    "OccurrenceAnalyzer",
    # CAMPO
    "OrdemServicoService",
    "VisitaService",
    "ChecklistService",
    # Roteirizacao
    "RoteirizacaoService",
    "TipoOtimizacao",
    "StatusRoteiro",
    "PontoRota",
    "RoteiroOtimizado",
    "get_roteirizacao_service",
    # Estoque
    "EstoqueIntegrationService",
    "TipoMovimentacao",
    "StatusRequisicao",
    "get_estoque_integration_service",
]
