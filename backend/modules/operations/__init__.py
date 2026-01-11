"""
Module: operations
Description: Modulo de Operacoes - Postos, Escalas e Gestao de Turnos
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo fornece:
- Gestao de Postos (criacao, tipos, status)
- Geracao e gestao de Escalas de trabalho
- Controle de Turnos (shifts)
- Alocacao de funcionarios
- Gestao de Substituicoes
- Banco de Horas (Time Bank)

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

from fastapi import APIRouter

# Importa routers dos controllers
from .controllers import (
    post_router,
    scale_router,
    shift_router,
    allocation_router,
    substitution_router,
    time_bank_router,
)

# Cria router principal que agrega todos os sub-routers
operations_router = APIRouter(prefix="/operations", tags=["Operations - Postos e Escalas"])

# Inclui todos os sub-routers
operations_router.include_router(post_router)
operations_router.include_router(scale_router)
operations_router.include_router(shift_router)
operations_router.include_router(allocation_router)
operations_router.include_router(substitution_router)
operations_router.include_router(time_bank_router)

# Exporta tambem o router antigo para compatibilidade
router = operations_router

# Re-export models principais
from .models import (
    Post,
    PostType,
    PostStatus,
    ShiftType,
    Scale,
    ScaleType,
    ScaleStatus,
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

# Re-export services principais
from .services import (
    ScaleGenerator,
    scale_generator,
    SubstitutionService,
    substitution_service,
    TimeBankService,
    time_bank_service,
)

# Re-export repositories
from .repositories import (
    PostRepository,
    ScaleRepository,
    ShiftRepository,
    AllocationRepository,
    SubstitutionRepository,
    TimeBankRepository,
)

__all__ = [
    # Router principal
    "operations_router",
    "router",
    # Routers individuais
    "post_router",
    "scale_router",
    "shift_router",
    "allocation_router",
    "substitution_router",
    "time_bank_router",
    # Models - Post
    "Post",
    "PostType",
    "PostStatus",
    "ShiftType",
    # Models - Scale
    "Scale",
    "ScaleType",
    "ScaleStatus",
    # Models - Shift
    "Shift",
    "ShiftStatus",
    # Models - Allocation
    "Allocation",
    "AllocationStatus",
    # Models - Substitution
    "Substitution",
    "SubstitutionStatus",
    "SubstitutionReason",
    # Models - TimeBank
    "TimeBank",
    "TimeBankEntryType",
    "TimeBankStatus",
    # Services
    "ScaleGenerator",
    "scale_generator",
    "SubstitutionService",
    "substitution_service",
    "TimeBankService",
    "time_bank_service",
    # Repositories
    "PostRepository",
    "ScaleRepository",
    "ShiftRepository",
    "AllocationRepository",
    "SubstitutionRepository",
    "TimeBankRepository",
]

__version__ = "1.0.0"
