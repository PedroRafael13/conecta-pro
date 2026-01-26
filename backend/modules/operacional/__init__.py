"""
Module: operacional
Description: Modulo Operacional Completo - Conecta PRO
Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100

Este modulo fornece gestao operacional completa:

CORE:
- Gestao de Postos (criacao, tipos, status)
- Geracao e gestao de Escalas de trabalho
- Controle de Turnos (shifts)
- Alocacao de funcionarios
- Gestao de Substituicoes
- Banco de Horas (Time Bank)
- Gestao de Diaristas (submodulo)

NOVOS SUBMODULOS (v3.0.0):
- Ocorrencias: Registro e gestao de incidentes operacionais com IA
- Medidas Administrativas: Workflow disciplinar com assinatura digital
- Comunicacao: Comunicados, notificacoes e alertas em tempo real
- IA Operacional: Otimizadores e analisadores inteligentes
- Relatorios: Cobertura, HE, disciplinar com export PDF/Excel
- Ponto Avancado: Geolocalizacao, biometria, validacao multi-fator

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio e validacoes
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
- diaristas/: Submodulo de Gestao de Diaristas
- occurrences/: Gestao de Ocorrencias
- disciplinary/: Medidas Administrativas
- communication/: Comunicacao Operacional
- ai/: Inteligencia Artificial Operacional
- reports/: Relatorios Avancados
"""

from fastapi import APIRouter

# =============================================================================
# CORE ROUTERS
# =============================================================================

from .controllers import (
    post_router,
    scale_router,
    scale_template_router,
    shift_router,
    allocation_router,
    substitution_router,
    time_bank_router,
    dashboard_router,
)

# Router de diaristas
from .diaristas import diarist_router, diarists_router

# =============================================================================
# NOVOS SUBMODULOS - ROUTERS
# =============================================================================

# Ocorrencias
from .occurrences import occurrence_router

# Medidas Administrativas
from .disciplinary import disciplinary_router

# Comunicacao
from .communication import communication_router

# Rondas de Inspecao
from .inspection_rounds import inspection_round_router

# =============================================================================
# ROUTER PRINCIPAL
# =============================================================================

operacional_router = APIRouter(prefix="/operacional", tags=["Operacional"])

# Core routers
operacional_router.include_router(
    post_router, prefix="/postos", tags=["Operacional - Postos"]
)
operacional_router.include_router(
    scale_router, prefix="/escalas", tags=["Operacional - Escalas"]
)
operacional_router.include_router(
    scale_template_router, tags=["Operacional - Templates de Escalas"]
)
operacional_router.include_router(
    shift_router, prefix="/turnos", tags=["Operacional - Turnos"]
)
operacional_router.include_router(
    allocation_router, prefix="/alocacoes", tags=["Operacional - Alocacoes"]
)
operacional_router.include_router(
    substitution_router, prefix="/substituicoes", tags=["Operacional - Substituicoes"]
)
operacional_router.include_router(
    time_bank_router, prefix="/banco-horas", tags=["Operacional - Banco de Horas"]
)

# Diaristas
operacional_router.include_router(
    diarist_router, prefix="/diaristas", tags=["Operacional - Diaristas"]
)

# Dashboard unificado
operacional_router.include_router(
    dashboard_router, tags=["Operacional - Dashboard"]
)

# Novos submodulos
operacional_router.include_router(
    occurrence_router, prefix="/ocorrencias", tags=["Operacional - Ocorrencias"]
)
operacional_router.include_router(
    disciplinary_router, prefix="/medidas-administrativas", tags=["Operacional - Disciplinar"]
)
operacional_router.include_router(
    communication_router, tags=["Operacional - Comunicacao"]
)
operacional_router.include_router(
    inspection_round_router, prefix="/rondas", tags=["Operacional - Rondas de Inspecao"]
)

# Alias para compatibilidade
router = operacional_router
operations_router = operacional_router

# =============================================================================
# CORE MODELS
# =============================================================================

from .models import (
    Post,
    PostType,
    PostStatus,
    ShiftType,
    Scale,
    ScaleType,
    ScaleStatus,
    ScaleTemplate,
    Shift,
    ShiftStatus,
    Allocation,
    AllocationStatus,
    Substitution,
    SubstitutionStatus,
    SubstitutionReason,
    TimeBank,
    TimeBankEntryType,
    TimeBankStatus,
)

# =============================================================================
# CORE SERVICES
# =============================================================================

from .services import (
    ScaleGenerator,
    scale_generator,
    ScaleTemplateService,
    SubstitutionService,
    substitution_service,
    TimeBankService,
    time_bank_service,
    IntegrationService,
    get_integration_service,
    # Novos services - Ponto Avancado
    GeolocationService,
    GeoPoint,
    GeolocationValidation,
    BiometricService,
    FaceValidationResult,
    PhotoMetadata,
    CheckInValidator,
    CheckInData,
    ValidationConfig,
    ValidationResult,
)

# =============================================================================
# CORE REPOSITORIES
# =============================================================================

from .repositories import (
    PostRepository,
    ScaleRepository,
    ScaleTemplateRepository,
    ShiftRepository,
    AllocationRepository,
    SubstitutionRepository,
    TimeBankRepository,
)

# =============================================================================
# DIARISTAS SUBMODULE
# =============================================================================

from .diaristas import (
    Diarist,
    DiaristAssignment,
    DiaristSchedule,
    DiaristPayment,
    DiaristEvaluation,
    DiaristType,
    DiaristStatus,
    DiaristService,
    DiaristRepository,
)

# =============================================================================
# OCCURRENCES SUBMODULE
# =============================================================================

from .occurrences import (
    # Models
    Occurrence,
    OccurrenceStatus,
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceType,
    # Schemas
    OccurrenceCreate,
    OccurrenceUpdate,
    OccurrenceResponse,
    OccurrenceListResponse,
    OccurrenceFilter,
    # Repository
    OccurrenceRepository,
)

# =============================================================================
# DISCIPLINARY SUBMODULE
# =============================================================================

from .disciplinary import (
    # Models
    DisciplinaryAction,
    DisciplinaryActionType,
    DisciplinaryActionStatus,
    ReasonCategory,
    DisciplinaryTemplate,
    DigitalSignature,
    SignerType,
    # Services
    DisciplinaryService,
    TemplateService,
    SignatureService,
    DisciplinaryAdvisor,
    get_disciplinary_service,
    get_template_service,
    get_signature_service,
    get_disciplinary_advisor,
    # Repositories
    DisciplinaryRepository,
    TemplateRepository,
    SignatureRepository,
    # Schemas
    DisciplinaryActionCreate,
    DisciplinaryActionUpdate,
    DisciplinaryActionResponse,
)

# =============================================================================
# COMMUNICATION SUBMODULE
# =============================================================================

from .communication import (
    # Models
    Announcement,
    AnnouncementStatus,
    AnnouncementPriority,
    AnnouncementCategory,
    AnnouncementTargetType,
    AnnouncementRead,
    Notification,
    NotificationType,
    NotificationChannel,
    Alert,
    AlertType,
    AlertSeverity,
    # Services
    AnnouncementService,
    NotificationService,
    AlertService,
    PushProvider,
    PushProviderFactory,
    # Repositories
    AnnouncementRepository,
    NotificationRepository,
    AlertRepository,
    # Schemas
    AnnouncementCreate,
    AnnouncementResponse,
    NotificationCreate,
    NotificationResponse,
    AlertCreate,
    AlertResponse,
    WebSocketMessage,
)

# =============================================================================
# AI SUBMODULE
# =============================================================================

from .ai import (
    # Scale Optimizer
    ScaleOptimizer,
    ShiftSlot,
    EmployeeAvailability,
    EmployeePreference,
    OptimizationConstraints,
    OptimizationResult,
    # Substitution Optimizer
    SubstitutionOptimizer,
    SubstituteSuggestion,
    SubstitutionRequest,
    # Predictive Analyzer
    PredictiveAnalyzer,
    AbsencePrediction,
    TurnoverRisk,
    OvertimeForecast,
    AnomalyPattern,
    # Occurrence Analyzer
    OccurrenceAnalyzer,
    OccurrenceAnalysis,
    OccurrenceClassification,
    ActionSuggestion,
    SimilarOccurrence,
)

# =============================================================================
# REPORTS SUBMODULE
# =============================================================================

from .reports import (
    # Coverage Report
    CoverageReportService,
    CoverageReport,
    PostCoverage,
    EmployeeCoverage,
    # Overtime Report
    OvertimeReportService,
    OvertimeReport,
    EmployeeOvertime,
    ClientOvertime,
    # Disciplinary Report
    DisciplinaryReportService,
    DisciplinaryReport,
    DisciplinaryStats,
    EmployeeDisciplinary,
    ReasonBreakdown,
)

# =============================================================================
# INSPECTION ROUNDS SUBMODULE
# =============================================================================

from .inspection_rounds import (
    # Models
    InspectionRound,
    InspectionRoundStatus,
    InspectorRole,
    InspectionCheckpoint,
    CheckpointType,
    CheckpointStatus,
    # Schemas
    InspectionRoundCreate,
    InspectionRoundResponse,
    # Services
    InspectionRoundService,
    # Repositories
    InspectionRoundRepository,
)

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
    "diarist_router",
    "diarists_router",
    # New routers
    "occurrence_router",
    "disciplinary_router",
    "communication_router",
    "inspection_round_router",
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
