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

# =============================================================================
# CAMPO - Checklists
# =============================================================================
from .checklist import (
    AlertaConfig,
    # Response
    ChecklistComItens,
    ChecklistConcluirRequest,
    # Actions
    ChecklistIniciarRequest,
    # Item
    ChecklistItemCreate,
    ChecklistItemRead,
    ChecklistItemUpdate,
    ChecklistPreenchidoCompleto,
    # Preenchido
    ChecklistPreenchidoCreate,
    ChecklistPreenchidoRead,
    ChecklistResponderRequest,
    # Resposta
    ChecklistRespostaCreate,
    ChecklistRespostaRead,
    ChecklistRespostaUpdate,
    # Template
    ChecklistTemplateCreate,
    ChecklistTemplateListItem,
    ChecklistTemplateRead,
    ChecklistTemplateUpdate,
    # Auxiliares
    OpcaoItem,
    ReordenarItensRequest,
    TemplateFiltro,
    TemplatePaginatedResponse,
    ValidacaoResult,
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
    DocumentoItem,
    FotoItem,
    # Auxiliares
    MaterialItem,
    # Create/Update
    OrdemServicoCreate,
    OrdemServicoListItem,
    # Read
    OrdemServicoRead,
    OrdemServicoUpdate,
    # Actions
    OSAgendarRequest,
    OSAssinaturaRequest,
    OSAvaliacaoRequest,
    OSCancelarRequest,
    OSCheckinRequest,
    OSCheckoutRequest,
    OSConcluirRequest,
    OSDashboardStats,
    # Filters/Response
    OSFiltro,
    OSFotoRequest,
    OSPaginatedResponse,
    OSReagendarRequest,
)

# =============================================================================
# CAMPO - Visitas
# =============================================================================
from .visita import (
    FotoVisita,
    # Auxiliares
    InteresseServico,
    LevantamentoTecnico,
    NecessidadeItem,
    VisitaCancelarRequest,
    VisitaCheckinRequest,
    VisitaCheckoutRequest,
    # Actions
    VisitaConfirmarRequest,
    # Create/Update
    VisitaCreate,
    VisitaDashboardStats,
    # Filters/Response
    VisitaFiltro,
    VisitaFollowupRequest,
    VisitaFotoRequest,
    VisitaInteresseRequest,
    VisitaLevantamentoRequest,
    VisitaListItem,
    VisitaNecessidadeRequest,
    VisitaPaginatedResponse,
    VisitaPropostaRequest,
    # Read
    VisitaRead,
    VisitaReagendarRequest,
    VisitaResultadoRequest,
    VisitaUpdate,
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
