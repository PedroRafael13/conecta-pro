"""Schemas do modulo Campo v3.0.0."""

# =============================================================================
# Legacy - Portaria Remota
# =============================================================================
from .access_log import (
    AccessLogCreate,
    AccessLogFilter,
    AccessLogListResponse,
    AccessLogResponse,
    AccessLogStats,
)
from .equipment_status import (
    EquipmentStatusCreate,
    EquipmentStatusFilter,
    EquipmentStatusListResponse,
    EquipmentStatusResponse,
    EquipmentStatusStats,
    EquipmentStatusUpdate,
)
from .guardian_occurrence import (
    GuardianOccurrenceAcknowledge,
    GuardianOccurrenceCreate,
    GuardianOccurrenceEscalate,
    GuardianOccurrenceFilter,
    GuardianOccurrenceListResponse,
    GuardianOccurrenceResolve,
    GuardianOccurrenceResponse,
    GuardianOccurrenceStats,
)
from .guardian_sync import (
    GuardianSyncCreate,
    GuardianSyncFilter,
    GuardianSyncListResponse,
    GuardianSyncResponse,
    GuardianSyncRetry,
    GuardianSyncStats,
)

# =============================================================================
# CAMPO - Ordens de Servico
# =============================================================================
from .ordem_servico import (
    # Create/Update
    OrdemServicoCreate,
    OrdemServicoUpdate,
    # Read
    OrdemServicoRead,
    OrdemServicoListItem,
    # Actions
    OSAgendarRequest,
    OSCheckinRequest,
    OSCheckoutRequest,
    OSConcluirRequest,
    OSCancelarRequest,
    OSReagendarRequest,
    OSAvaliacaoRequest,
    OSAssinaturaRequest,
    OSFotoRequest,
    # Filters/Response
    OSFiltro,
    OSPaginatedResponse,
    OSDashboardStats,
    # Auxiliares
    MaterialItem,
    FotoItem,
    DocumentoItem,
)

# =============================================================================
# CAMPO - Visitas
# =============================================================================
from .visita import (
    # Create/Update
    VisitaCreate,
    VisitaUpdate,
    # Read
    VisitaRead,
    VisitaListItem,
    # Actions
    VisitaConfirmarRequest,
    VisitaCheckinRequest,
    VisitaCheckoutRequest,
    VisitaResultadoRequest,
    VisitaCancelarRequest,
    VisitaReagendarRequest,
    VisitaInteresseRequest,
    VisitaPropostaRequest,
    VisitaLevantamentoRequest,
    VisitaNecessidadeRequest,
    VisitaFollowupRequest,
    VisitaFotoRequest,
    # Filters/Response
    VisitaFiltro,
    VisitaPaginatedResponse,
    VisitaDashboardStats,
    # Auxiliares
    InteresseServico,
    NecessidadeItem,
    LevantamentoTecnico,
    FotoVisita,
)

# =============================================================================
# CAMPO - Checklists
# =============================================================================
from .checklist import (
    # Template
    ChecklistTemplateCreate,
    ChecklistTemplateUpdate,
    ChecklistTemplateRead,
    ChecklistTemplateListItem,
    # Item
    ChecklistItemCreate,
    ChecklistItemUpdate,
    ChecklistItemRead,
    # Resposta
    ChecklistRespostaCreate,
    ChecklistRespostaUpdate,
    ChecklistRespostaRead,
    # Preenchido
    ChecklistPreenchidoCreate,
    ChecklistPreenchidoRead,
    # Actions
    ChecklistIniciarRequest,
    ChecklistResponderRequest,
    ChecklistConcluirRequest,
    ReordenarItensRequest,
    # Response
    ChecklistComItens,
    ChecklistPreenchidoCompleto,
    ValidacaoResult,
    TemplatePaginatedResponse,
    TemplateFiltro,
    # Auxiliares
    OpcaoItem,
    AlertaConfig,
)

__all__ = [
    # === Legacy (Portaria Remota) ===
    # GuardianSync
    "GuardianSyncCreate",
    "GuardianSyncResponse",
    "GuardianSyncFilter",
    "GuardianSyncListResponse",
    "GuardianSyncRetry",
    "GuardianSyncStats",
    # AccessLog
    "AccessLogCreate",
    "AccessLogResponse",
    "AccessLogFilter",
    "AccessLogListResponse",
    "AccessLogStats",
    # GuardianOccurrence
    "GuardianOccurrenceCreate",
    "GuardianOccurrenceResponse",
    "GuardianOccurrenceFilter",
    "GuardianOccurrenceListResponse",
    "GuardianOccurrenceAcknowledge",
    "GuardianOccurrenceResolve",
    "GuardianOccurrenceEscalate",
    "GuardianOccurrenceStats",
    # EquipmentStatus
    "EquipmentStatusCreate",
    "EquipmentStatusUpdate",
    "EquipmentStatusResponse",
    "EquipmentStatusFilter",
    "EquipmentStatusListResponse",
    "EquipmentStatusStats",
    # === CAMPO - Ordens de Servico ===
    "OrdemServicoCreate",
    "OrdemServicoUpdate",
    "OrdemServicoRead",
    "OrdemServicoListItem",
    "OSAgendarRequest",
    "OSCheckinRequest",
    "OSCheckoutRequest",
    "OSConcluirRequest",
    "OSCancelarRequest",
    "OSReagendarRequest",
    "OSAvaliacaoRequest",
    "OSAssinaturaRequest",
    "OSFotoRequest",
    "OSFiltro",
    "OSPaginatedResponse",
    "OSDashboardStats",
    "MaterialItem",
    "FotoItem",
    "DocumentoItem",
    # === CAMPO - Visitas ===
    "VisitaCreate",
    "VisitaUpdate",
    "VisitaRead",
    "VisitaListItem",
    "VisitaConfirmarRequest",
    "VisitaCheckinRequest",
    "VisitaCheckoutRequest",
    "VisitaResultadoRequest",
    "VisitaCancelarRequest",
    "VisitaReagendarRequest",
    "VisitaInteresseRequest",
    "VisitaPropostaRequest",
    "VisitaLevantamentoRequest",
    "VisitaNecessidadeRequest",
    "VisitaFollowupRequest",
    "VisitaFotoRequest",
    "VisitaFiltro",
    "VisitaPaginatedResponse",
    "VisitaDashboardStats",
    "InteresseServico",
    "NecessidadeItem",
    "LevantamentoTecnico",
    "FotoVisita",
    # === CAMPO - Checklists ===
    "ChecklistTemplateCreate",
    "ChecklistTemplateUpdate",
    "ChecklistTemplateRead",
    "ChecklistTemplateListItem",
    "ChecklistItemCreate",
    "ChecklistItemUpdate",
    "ChecklistItemRead",
    "ChecklistRespostaCreate",
    "ChecklistRespostaUpdate",
    "ChecklistRespostaRead",
    "ChecklistPreenchidoCreate",
    "ChecklistPreenchidoRead",
    "ChecklistIniciarRequest",
    "ChecklistResponderRequest",
    "ChecklistConcluirRequest",
    "ReordenarItensRequest",
    "ChecklistComItens",
    "ChecklistPreenchidoCompleto",
    "ValidacaoResult",
    "TemplatePaginatedResponse",
    "TemplateFiltro",
    "OpcaoItem",
    "AlertaConfig",
]
