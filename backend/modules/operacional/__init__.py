"""
Module: operacional
Description: Modulo Operacional Completo - Conecta PRO
Author: Conecta PRO Team
Date: 2026-01-18

DEPRECATED: Use 'modules.operacoes' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.operacional' is deprecated. "
    "Use 'modules.operacoes' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from fastapi import APIRouter  # noqa: E402

# AI SUBMODULE
from .ai import (  # noqa: E402
    AbsencePrediction,
    ActionSuggestion,
    AnomalyPattern,
    AutomaticFeedback,
    ContingencyPlan,
    CoveragePredictorAgent,
    CoverageRisk,
    EmployeeAbsenceRisk,
    EmployeeAvailability,
    EmployeePreference,
    OccurrenceAnalysis,
    OccurrenceAnalyzer,
    OccurrenceClassification,
    OptimizationConstraints,
    OptimizationResult,
    OvertimeForecast,
    PerformanceAlert,
    PerformanceAnalyzerAgent,
    PerformanceDimension,
    PerformanceScore,
    PredictiveAnalyzer,
    ScaleOptimizer,
    ShiftSlot,
    SimilarOccurrence,
    SubstituteSuggestion,
    SubstitutionOptimizer,
    SubstitutionRequest,
    TopPerformer,
    TurnoverRisk,
    WeeklyRiskMap,
    ai_router,
)

# COMMUNICATION SUBMODULE
from .communication import (  # noqa: E402
    Alert,
    AlertCreate,
    AlertRepository,
    AlertResponse,
    AlertService,
    AlertSeverity,
    AlertType,
    Announcement,
    AnnouncementCategory,
    AnnouncementCreate,
    AnnouncementPriority,
    AnnouncementRead,
    AnnouncementRepository,
    AnnouncementResponse,
    AnnouncementService,
    AnnouncementStatus,
    AnnouncementTargetType,
    Notification,
    NotificationChannel,
    NotificationCreate,
    NotificationRepository,
    NotificationResponse,
    NotificationService,
    NotificationType,
    PushProvider,
    PushProviderFactory,
    WebSocketMessage,
    communication_router,
)

# Comunicacao
# =============================================================================
# CORE ROUTERS
# =============================================================================
from .controllers import (  # noqa: E402
    allocation_router,
    dashboard_router,
    employee_router,
    post_router,
    scale_router,
    scale_template_router,
    shift_router,
    substitution_router,
    time_bank_router,
)

# DIARISTAS SUBMODULE
from .diaristas import (  # noqa: E402
    Diarist,
    DiaristAssignment,
    DiaristEvaluation,
    DiaristPayment,
    DiaristRepository,
    DiaristSchedule,
    DiaristService,
    DiaristStatus,
    DiaristType,
    diarist_router,
    diarists_router,
)

# DISCIPLINARY SUBMODULE
from .disciplinary import (  # noqa: E402
    DigitalSignature,
    DisciplinaryAction,
    DisciplinaryActionCreate,
    DisciplinaryActionResponse,
    DisciplinaryActionStatus,
    DisciplinaryActionType,
    DisciplinaryActionUpdate,
    DisciplinaryAdvisor,
    DisciplinaryRepository,
    DisciplinaryService,
    DisciplinaryTemplate,
    ReasonCategory,
    SignatureRepository,
    SignatureService,
    SignerType,
    TemplateRepository,
    TemplateService,
    disciplinary_router,
    get_disciplinary_advisor,
    get_disciplinary_service,
    get_signature_service,
    get_template_service,
)

# INSPECTION ROUNDS SUBMODULE
from .inspection_rounds import (  # noqa: E402
    CheckpointStatus,
    CheckpointType,
    InspectionCheckpoint,
    InspectionRound,
    InspectionRoundCreate,
    InspectionRoundRepository,
    InspectionRoundResponse,
    InspectionRoundService,
    InspectionRoundStatus,
    InspectorRole,
    inspection_round_router,
)

# CORE MODELS
from .models import (  # noqa: E402
    Allocation,
    AllocationStatus,
    Post,
    PostStatus,
    PostType,
    Scale,
    ScaleStatus,
    ScaleTemplate,
    ScaleType,
    Shift,
    ShiftStatus,
    ShiftType,
    Substitution,
    SubstitutionReason,
    SubstitutionStatus,
    TimeBank,
    TimeBankEntryType,
    TimeBankStatus,
)

# OCCURRENCES SUBMODULE
from .occurrences import (  # noqa: E402
    Occurrence,
    OccurrenceCategory,
    OccurrenceCreate,
    OccurrenceFilter,
    OccurrenceListResponse,
    OccurrenceRepository,
    OccurrenceResponse,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
    OccurrenceUpdate,
    occurrence_router,
)

# REPORTS SUBMODULE
from .reports import (  # noqa: E402
    ClientOvertime,
    CoverageReport,
    CoverageReportService,
    DisciplinaryReport,
    DisciplinaryReportService,
    DisciplinaryStats,
    EmployeeCoverage,
    EmployeeDisciplinary,
    EmployeeOvertime,
    OvertimeReport,
    OvertimeReportService,
    PostCoverage,
    ReasonBreakdown,
)

# CORE REPOSITORIES
from .repositories import (  # noqa: E402
    AllocationRepository,
    PostRepository,
    ScaleRepository,
    ScaleTemplateRepository,
    ShiftRepository,
    SubstitutionRepository,
    TimeBankRepository,
)

# CORE SERVICES
from .services import (  # noqa: E402
    BiometricService,
    CheckInData,
    CheckInValidator,
    FaceValidationResult,
    GeolocationService,
    GeolocationValidation,
    GeoPoint,
    IntegrationService,
    PhotoMetadata,
    ScaleGenerator,
    ScaleTemplateService,
    SubstitutionService,
    TimeBankService,
    ValidationConfig,
    ValidationResult,
    get_integration_service,
    scale_generator,
    substitution_service,
    time_bank_service,
)

# VACATIONS SUBMODULE
from .vacations import (  # noqa: E402
    vacation_router,
)

# WEBSOCKET SUBMODULE
from .websockets import manager  # noqa: E402
from .websockets import websocket_router as ws_router  # noqa: E402

# =============================================================================
# ROUTER PRINCIPAL
# =============================================================================

operacional_router = APIRouter(prefix="/operacional", tags=["Operacional"])

# Core routers
operacional_router.include_router(post_router, prefix="/postos", tags=["Operacional - Postos"])
operacional_router.include_router(scale_router, prefix="/escalas", tags=["Operacional - Escalas"])
operacional_router.include_router(scale_template_router, tags=["Operacional - Templates de Escalas"])
operacional_router.include_router(shift_router, prefix="/turnos", tags=["Operacional - Turnos"])
operacional_router.include_router(allocation_router, prefix="/alocacoes", tags=["Operacional - Alocacoes"])
operacional_router.include_router(substitution_router, prefix="/substituicoes", tags=["Operacional - Substituicoes"])
operacional_router.include_router(time_bank_router, prefix="/banco-horas", tags=["Operacional - Banco de Horas"])

# Diaristas
operacional_router.include_router(diarist_router, tags=["Operacional - Diaristas"])

# Employees
operacional_router.include_router(employee_router, tags=["Operacional - Employees"])

# Dashboard unificado
operacional_router.include_router(dashboard_router, tags=["Operacional - Dashboard"])

# Novos submodulos
operacional_router.include_router(occurrence_router, prefix="/ocorrencias", tags=["Operacional - Ocorrencias"])
operacional_router.include_router(
    disciplinary_router, prefix="/medidas-administrativas", tags=["Operacional - Disciplinar"]
)
operacional_router.include_router(communication_router, tags=["Operacional - Comunicacao"])
operacional_router.include_router(inspection_round_router, prefix="/rondas", tags=["Operacional - Rondas de Inspecao"])
operacional_router.include_router(vacation_router, tags=["Operacional - Férias"])
operacional_router.include_router(ai_router, tags=["Operacional - AI"])
operacional_router.include_router(ws_router, tags=["Operacional - WebSocket"])

# Alias para compatibilidade
router = operacional_router
operations_router = operacional_router

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # =========================================================================
    # ROUTERS
    # =========================================================================
    "operacional_router",
    "operations_router",
    "router",
    # Core routers
    "post_router",
    "scale_router",
    "scale_template_router",
    "shift_router",
    "allocation_router",
    "substitution_router",
    "time_bank_router",
    "dashboard_router",
    "employee_router",
    "diarist_router",
    "diarists_router",
    # New routers
    "occurrence_router",
    "disciplinary_router",
    "communication_router",
    "inspection_round_router",
    "vacation_router",
    "ai_router",
    "ws_router",
    "manager",
    # =========================================================================
    # CORE MODELS
    # =========================================================================
    "Post",
    "PostType",
    "PostStatus",
    "ShiftType",
    "Scale",
    "ScaleType",
    "ScaleStatus",
    "ScaleTemplate",
    "Shift",
    "ShiftStatus",
    "Allocation",
    "AllocationStatus",
    "Substitution",
    "SubstitutionStatus",
    "SubstitutionReason",
    "TimeBank",
    "TimeBankEntryType",
    "TimeBankStatus",
    # =========================================================================
    # CORE SERVICES
    # =========================================================================
    "ScaleGenerator",
    "scale_generator",
    "ScaleTemplateService",
    "SubstitutionService",
    "substitution_service",
    "TimeBankService",
    "time_bank_service",
    "IntegrationService",
    "get_integration_service",
    # Ponto Avancado
    "GeolocationService",
    "GeoPoint",
    "GeolocationValidation",
    "BiometricService",
    "FaceValidationResult",
    "PhotoMetadata",
    "CheckInValidator",
    "CheckInData",
    "ValidationConfig",
    "ValidationResult",
    # =========================================================================
    # CORE REPOSITORIES
    # =========================================================================
    "PostRepository",
    "ScaleRepository",
    "ScaleTemplateRepository",
    "ShiftRepository",
    "AllocationRepository",
    "SubstitutionRepository",
    "TimeBankRepository",
    # =========================================================================
    # DIARISTAS
    # =========================================================================
    "Diarist",
    "DiaristAssignment",
    "DiaristSchedule",
    "DiaristPayment",
    "DiaristEvaluation",
    "DiaristType",
    "DiaristStatus",
    "DiaristService",
    "DiaristRepository",
    # =========================================================================
    # OCCURRENCES
    # =========================================================================
    "Occurrence",
    "OccurrenceStatus",
    "OccurrenceCategory",
    "OccurrenceSeverity",
    "OccurrenceType",
    "OccurrenceCreate",
    "OccurrenceUpdate",
    "OccurrenceResponse",
    "OccurrenceListResponse",
    "OccurrenceFilter",
    "OccurrenceRepository",
    # =========================================================================
    # DISCIPLINARY
    # =========================================================================
    "DisciplinaryAction",
    "DisciplinaryActionType",
    "DisciplinaryActionStatus",
    "ReasonCategory",
    "DisciplinaryTemplate",
    "DigitalSignature",
    "SignerType",
    "DisciplinaryService",
    "TemplateService",
    "SignatureService",
    "DisciplinaryAdvisor",
    "get_disciplinary_service",
    "get_template_service",
    "get_signature_service",
    "get_disciplinary_advisor",
    "DisciplinaryRepository",
    "TemplateRepository",
    "SignatureRepository",
    "DisciplinaryActionCreate",
    "DisciplinaryActionUpdate",
    "DisciplinaryActionResponse",
    # =========================================================================
    # COMMUNICATION
    # =========================================================================
    "Announcement",
    "AnnouncementStatus",
    "AnnouncementPriority",
    "AnnouncementCategory",
    "AnnouncementTargetType",
    "AnnouncementRead",
    "Notification",
    "NotificationType",
    "NotificationChannel",
    "Alert",
    "AlertType",
    "AlertSeverity",
    "AnnouncementService",
    "NotificationService",
    "AlertService",
    "PushProvider",
    "PushProviderFactory",
    "AnnouncementRepository",
    "NotificationRepository",
    "AlertRepository",
    "AnnouncementCreate",
    "AnnouncementResponse",
    "NotificationCreate",
    "NotificationResponse",
    "AlertCreate",
    "AlertResponse",
    "WebSocketMessage",
    # =========================================================================
    # AI AGENTS
    # =========================================================================
    "ScaleOptimizer",
    "ShiftSlot",
    "EmployeeAvailability",
    "EmployeePreference",
    "OptimizationConstraints",
    "OptimizationResult",
    "SubstitutionOptimizer",
    "SubstituteSuggestion",
    "SubstitutionRequest",
    "PredictiveAnalyzer",
    "AbsencePrediction",
    "TurnoverRisk",
    "OvertimeForecast",
    "AnomalyPattern",
    "OccurrenceAnalyzer",
    "OccurrenceAnalysis",
    "OccurrenceClassification",
    "ActionSuggestion",
    "SimilarOccurrence",
    # Coverage Predictor
    "CoveragePredictorAgent",
    "CoverageRisk",
    "EmployeeAbsenceRisk",
    "WeeklyRiskMap",
    "ContingencyPlan",
    # Performance Analyzer
    "PerformanceAnalyzerAgent",
    "PerformanceScore",
    "PerformanceDimension",
    "TopPerformer",
    "PerformanceAlert",
    "AutomaticFeedback",
    # =========================================================================
    # REPORTS
    # =========================================================================
    "CoverageReportService",
    "CoverageReport",
    "PostCoverage",
    "EmployeeCoverage",
    "OvertimeReportService",
    "OvertimeReport",
    "EmployeeOvertime",
    "ClientOvertime",
    "DisciplinaryReportService",
    "DisciplinaryReport",
    "DisciplinaryStats",
    "EmployeeDisciplinary",
    "ReasonBreakdown",
    # =========================================================================
    # INSPECTION ROUNDS
    # =========================================================================
    "InspectionRound",
    "InspectionRoundStatus",
    "InspectorRole",
    "InspectionCheckpoint",
    "CheckpointType",
    "CheckpointStatus",
    "InspectionRoundCreate",
    "InspectionRoundResponse",
    "InspectionRoundService",
    "InspectionRoundRepository",
]

__version__ = "3.1.0"
