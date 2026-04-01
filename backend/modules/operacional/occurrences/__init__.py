"""
Module: occurrences
Description: Modulo de Gestao de Ocorrencias Disciplinares/Fiscalizacao
Author: Conecta PRO Team - Refatorado 2026-01-23
Quality Score Target: 99+/100

Este modulo fornece:
- Registro de ocorrências disciplinares (não conformidades)
- Controle de infrações dos funcionários
- Histórico disciplinar
- Ações corretivas
- Dashboard e métricas

CONTEXTO: Ocorrências são registradas por SUPERVISORES/GESTORES durante
fiscalizações e rondas nos postos. NÃO é para funcionários reportarem problemas.

Estrutura:
- models/: Modelos SQLAlchemy
- schemas/: Schemas Pydantic para validação
- repositories/: Acesso a dados
- controllers/: Endpoints FastAPI
"""

# Controllers
from .controllers import occurrence_router

# Models
from .models import (
    Occurrence,
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceStatus,
    OccurrenceType,
)

# Repository
from .repositories import OccurrenceRepository

# Schemas
from .schemas import (
    AttachmentSchema,
    OccurrenceCreate,
    OccurrenceFilter,
    OccurrenceListResponse,
    OccurrenceResolve,
    OccurrenceResponse,
    OccurrenceStats,
    OccurrenceUpdate,
)

__all__ = [
    # Router
    "occurrence_router",
    # Models
    "Occurrence",
    # Enums
    "OccurrenceStatus",
    "OccurrenceCategory",
    "OccurrenceSeverity",
    "OccurrenceType",
    # Schemas
    "OccurrenceCreate",
    "OccurrenceUpdate",
    "OccurrenceResolve",
    "OccurrenceResponse",
    "OccurrenceListResponse",
    "OccurrenceFilter",
    "OccurrenceStats",
    "AttachmentSchema",
    # Repository
    "OccurrenceRepository",
]

__version__ = "2.0.0-disciplinar"
