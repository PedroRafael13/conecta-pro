"""
Schemas do modulo de Rondas de Inspecao.

Author: Conecta PRO Team
Date: 2026-01-23
"""

from .inspection_round_schemas import (
    ApplyDisciplinaryRequest,
    # Checkpoint schemas
    CheckpointCreate,
    CheckpointResponse,
    CheckpointUpdate,
    CheckpointWithOccurrence,
    CompleteRoundRequest,
    # Dashboard
    InspectionDashboardStats,
    # Round schemas
    InspectionRoundCreate,
    InspectionRoundFilter,
    InspectionRoundListResponse,
    InspectionRoundResponse,
    InspectionRoundSummary,
    InspectionRoundUpdate,
    InspectorStats,
    RegisterOccurrenceRequest,
    # Action schemas
    StartRoundRequest,
)

__all__ = [
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
]
