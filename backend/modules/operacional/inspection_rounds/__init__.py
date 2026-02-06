"""
Modulo de Rondas de Inspecao.

Este modulo permite que gerentes, supervisores, inspetores e lideres
realizem rondas de inspecao nos postos de trabalho, registrando:
- Verificacoes de conformidade
- Ocorrencias de falhas operacionais
- Medidas disciplinares (advertencias, suspensoes)

Author: Conecta PRO Team
Date: 2026-01-23
Version: 1.0.0
"""

# Models
from .models import (
    InspectionRound,
    InspectionRoundStatus,
    InspectorRole,
    InspectionCheckpoint,
    CheckpointType,
    CheckpointStatus,
)

# Schemas
from .schemas import (
    InspectionRoundCreate,
    InspectionRoundUpdate,
    InspectionRoundResponse,
    InspectionRoundListResponse,
    InspectionRoundFilter,
    InspectionRoundSummary,
    CheckpointCreate,
    CheckpointUpdate,
    CheckpointResponse,
    CheckpointWithOccurrence,
    StartRoundRequest,
    CompleteRoundRequest,
    RegisterOccurrenceRequest,
    ApplyDisciplinaryRequest,
    InspectionDashboardStats,
    InspectorStats,
)

# Services
from .services import (
    InspectionRoundService,
    InspectionRoundNotFoundError,
    InspectionRoundValidationError,
)

# Repositories
from .repositories import InspectionRoundRepository

# Controllers
from .controllers import inspection_round_router

__all__ = [
    # Models
    "InspectionRound",
    "InspectionRoundStatus",
    "InspectorRole",
    "InspectionCheckpoint",
    "CheckpointType",
    "CheckpointStatus",
    # Schemas
    "InspectionRoundCreate",
    "InspectionRoundUpdate",
    "InspectionRoundResponse",
    "InspectionRoundListResponse",
    "InspectionRoundFilter",
    "InspectionRoundSummary",
    "CheckpointCreate",
    "CheckpointUpdate",
    "CheckpointResponse",
    "CheckpointWithOccurrence",
    "StartRoundRequest",
    "CompleteRoundRequest",
    "RegisterOccurrenceRequest",
    "ApplyDisciplinaryRequest",
    "InspectionDashboardStats",
    "InspectorStats",
    # Services
    "InspectionRoundService",
    "InspectionRoundNotFoundError",
    "InspectionRoundValidationError",
    # Repositories
    "InspectionRoundRepository",
    # Router
    "inspection_round_router",
]

__version__ = "1.0.0"
