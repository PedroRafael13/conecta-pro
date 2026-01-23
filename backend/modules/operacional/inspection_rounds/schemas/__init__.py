"""
Schemas do modulo de Rondas de Inspecao.

Author: Conecta PRO Team
Date: 2026-01-23
"""

from .inspection_round_schemas import (
    # Round schemas
    InspectionRoundCreate,
    InspectionRoundUpdate,
    InspectionRoundResponse,
    InspectionRoundListResponse,
    InspectionRoundFilter,
    InspectionRoundSummary,
    # Checkpoint schemas
    CheckpointCreate,
    CheckpointUpdate,
    CheckpointResponse,
    CheckpointWithOccurrence,
    # Action schemas
    StartRoundRequest,
    CompleteRoundRequest,
    RegisterOccurrenceRequest,
    ApplyDisciplinaryRequest,
    # Dashboard
    InspectionDashboardStats,
    InspectorStats,
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
