"""
Module: diarists
Description: Modulo de Gestao de Diaristas
Author: Conecta PRO Team
Date: 2026-01-11
Quality Score Target: 99+/100

Este modulo fornece:
- Cadastro e gestao de diaristas
- Agendamentos e escalas de trabalho
- Controle de pagamentos
- Avaliacoes de desempenho
- Inteligencia artificial para sugestoes e otimizacao

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

from fastapi import APIRouter

# Importa router dos controllers
from modules.diarists.controllers import router as diarist_router

# Importa models para re-export
from modules.diarists.models import (
    Diarist,
    DiaristAssignment,
    DiaristSchedule,
    DiaristPayment,
    DiaristEvaluation,
    DiaristType,
    DiaristStatus,
    DocumentType,
    AssignmentType,
    AssignmentStatus,
    RecurrenceType,
    ScheduleStatus,
    PaymentStatus,
    PaymentMethod,
    Weekday,
)

# Importa schemas para re-export
from modules.diarists.schemas import (
    DiaristBase,
    DiaristCreate,
    DiaristUpdate,
    DiaristResponse,
    DiaristListResponse,
    DiaristAssignmentBase,
    DiaristAssignmentCreate,
    DiaristAssignmentResponse,
    DiaristScheduleBase,
    DiaristScheduleCreate,
    DiaristScheduleResponse,
    DiaristPaymentBase,
    DiaristPaymentCreate,
    DiaristPaymentResponse,
    DiaristEvaluationBase,
    DiaristEvaluationCreate,
    DiaristEvaluationResponse,
    CheckinRequest,
    CheckoutRequest,
    DiaristSuggestionResponse,
    DiaristAvailabilityResponse,
    DiaristPerformanceResponse,
    ScheduleOptimizationResponse,
)

# Importa services para re-export
from modules.diarists.services import (
    DiaristService,
    DiaristAIService,
)

# Importa repositories para re-export
from modules.diarists.repositories import (
    DiaristRepository,
)

# Cria router principal que agrega todos os sub-routers
diarists_router = APIRouter(prefix="/diarists", tags=["Diaristas"])

# Inclui o router principal
diarists_router.include_router(diarist_router)

# Exporta tambem o router antigo para compatibilidade
router = diarists_router

__all__ = [
    # Routers
    "diarists_router",
    "router",
    "diarist_router",
    # Models
    "Diarist",
    "DiaristAssignment",
    "DiaristSchedule",
    "DiaristPayment",
    "DiaristEvaluation",
    "DiaristType",
    "DiaristStatus",
    "DocumentType",
    "AssignmentType",
    "AssignmentStatus",
    "RecurrenceType",
    "ScheduleStatus",
    "PaymentStatus",
    "PaymentMethod",
    "Weekday",
    # Schemas
    "DiaristBase",
    "DiaristCreate",
    "DiaristUpdate",
    "DiaristResponse",
    "DiaristListResponse",
    "DiaristAssignmentBase",
    "DiaristAssignmentCreate",
    "DiaristAssignmentResponse",
    "DiaristScheduleBase",
    "DiaristScheduleCreate",
    "DiaristScheduleResponse",
    "DiaristPaymentBase",
    "DiaristPaymentCreate",
    "DiaristPaymentResponse",
    "DiaristEvaluationBase",
    "DiaristEvaluationCreate",
    "DiaristEvaluationResponse",
    "CheckinRequest",
    "CheckoutRequest",
    "DiaristSuggestionResponse",
    "DiaristAvailabilityResponse",
    "DiaristPerformanceResponse",
    "ScheduleOptimizationResponse",
    # Services
    "DiaristService",
    "DiaristAIService",
    # Repositories
    "DiaristRepository",
]

__version__ = "1.0.0"
