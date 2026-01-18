"""
Módulo de Onboarding Digital - Conecta PRO.

Este módulo gerencia o processo completo de integração de novos funcionários,
incluindo checklists personalizáveis, etapas configuráveis e acompanhamento
de progresso em tempo real.

Funcionalidades:
    - Checklists de onboarding por cargo ou genéricos
    - Etapas com tipos variados (documento, treinamento, feedback, etc)
    - Acompanhamento de progresso individual
    - Dashboard com métricas e alertas
    - Notificações de atrasos
    - Avaliações de etapas

Estrutura:
    models/: Modelos SQLAlchemy para persistência
    schemas/: Schemas Pydantic para validação
    repositories/: Padrão Repository para acesso a dados
    services/: Lógica de negócio
    controllers/: Endpoints FastAPI

Exemplo de uso:
    >>> from modules.retention.onboarding import OnboardingService
    >>> service = OnboardingService(session)
    >>> checklist = await service.create_checklist(data)
"""

# Models
from .models import (
    OnboardingChecklist,
    OnboardingStep,
    OnboardingProgress,
    StepType,
    ProgressStatus,
)

# Schemas
from .schemas import (
    # Checklist
    ChecklistCreate,
    ChecklistUpdate,
    ChecklistResponse,
    ChecklistDetailResponse,
    ChecklistListResponse,
    # Step
    StepCreate,
    StepUpdate,
    StepResponse,
    # Progress
    ProgressCreate,
    ProgressUpdate,
    ProgressComplete,
    ProgressResponse,
    ProgressDetailResponse,
    ProgressListResponse,
    # Funcionário
    FuncionarioOnboardingCreate,
    FuncionarioOnboardingResponse,
    # Dashboard
    OnboardingDashboard,
    OnboardingStats,
    OnboardingAlert,
    OnboardingFilter,
    OnboardingReport,
)

# Repositories
from .repositories import OnboardingRepository

# Services
from .services import OnboardingService, OnboardingException

# Controllers
from .controllers import onboarding_router

__all__ = [
    # Models
    "OnboardingChecklist",
    "OnboardingStep",
    "OnboardingProgress",
    "StepType",
    "ProgressStatus",
    # Schemas - Checklist
    "ChecklistCreate",
    "ChecklistUpdate",
    "ChecklistResponse",
    "ChecklistDetailResponse",
    "ChecklistListResponse",
    # Schemas - Step
    "StepCreate",
    "StepUpdate",
    "StepResponse",
    # Schemas - Progress
    "ProgressCreate",
    "ProgressUpdate",
    "ProgressComplete",
    "ProgressResponse",
    "ProgressDetailResponse",
    "ProgressListResponse",
    # Schemas - Funcionário
    "FuncionarioOnboardingCreate",
    "FuncionarioOnboardingResponse",
    # Schemas - Dashboard
    "OnboardingDashboard",
    "OnboardingStats",
    "OnboardingAlert",
    "OnboardingFilter",
    "OnboardingReport",
    # Repository
    "OnboardingRepository",
    # Service
    "OnboardingService",
    "OnboardingException",
    # Router
    "onboarding_router",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
