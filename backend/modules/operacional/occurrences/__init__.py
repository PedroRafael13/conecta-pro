"""
Module: occurrences
Description: Modulo de Gestao de Ocorrencias Operacionais
Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100

Este modulo fornece:
- Registro e gestao de ocorrencias operacionais
- Classificacao automatica por IA
- Controle de SLA e escalacao
- Anexos e comentarios
- Dashboard e metricas
- Integracao com medidas administrativas

Estrutura:
- models/: Modelos SQLAlchemy
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

from fastapi import APIRouter

# Models
from .models import (
    Occurrence,
    OccurrenceAttachment,
    OccurrenceComment,
    OccurrenceCategoryConfig,
    OccurrenceStatus,
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceType,
    OccurrencePriority,
    ResolutionType,
    AttachmentType,
    DEFAULT_SLA_HOURS,
)

# Schemas
from .schemas import (
    OccurrenceCreate,
    OccurrenceUpdate,
    OccurrenceResponse,
    OccurrenceListResponse,
    OccurrenceFilter,
    AttachmentCreate,
    AttachmentResponse,
    CommentCreate,
    CommentResponse,
    EscalateRequest,
    ResolveRequest,
    ReopenRequest,
    DashboardStats,
    CategoryConfigCreate,
    CategoryConfigResponse,
)

# Services
from .services import (
    OccurrenceService,
    OccurrenceServiceError,
    OccurrenceNotFoundError,
    OccurrenceValidationError,
    OccurrenceAIAnalyzer,
    ClassificationResult,
    PatternAnalysis,
)

# Repository
from .repositories import OccurrenceRepository

# Controllers
from .controllers import occurrence_router

__all__ = [
    # Router
    "occurrence_router",
    # Models
    "Occurrence",
    "OccurrenceAttachment",
    "OccurrenceComment",
    "OccurrenceCategoryConfig",
    # Enums
    "OccurrenceStatus",
    "OccurrenceCategory",
    "OccurrenceSeverity",
    "OccurrenceType",
    "OccurrencePriority",
    "ResolutionType",
    "AttachmentType",
    # Constants
    "DEFAULT_SLA_HOURS",
    # Schemas
    "OccurrenceCreate",
    "OccurrenceUpdate",
    "OccurrenceResponse",
    "OccurrenceListResponse",
    "OccurrenceFilter",
    "AttachmentCreate",
    "AttachmentResponse",
    "CommentCreate",
    "CommentResponse",
    "EscalateRequest",
    "ResolveRequest",
    "ReopenRequest",
    "DashboardStats",
    "CategoryConfigCreate",
    "CategoryConfigResponse",
    # Services
    "OccurrenceService",
    "OccurrenceServiceError",
    "OccurrenceNotFoundError",
    "OccurrenceValidationError",
    "OccurrenceAIAnalyzer",
    "ClassificationResult",
    "PatternAnalysis",
    # Repository
    "OccurrenceRepository",
]

__version__ = "1.0.0"
