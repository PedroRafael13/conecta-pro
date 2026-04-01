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
# Controllers
from .controllers import onboarding_router
from .models import (
    OnboardingChecklist,
    OnboardingProgress,
    OnboardingStep,
    ProgressStatus,
    StepType,
)

# Repositories
from .repositories import OnboardingRepository

# Schemas
from .schemas import (
    # Checklist
    ChecklistCreate,
    ChecklistDetailResponse,
    ChecklistListResponse,
    ChecklistResponse,
    ChecklistUpdate,
    # Funcionário
    FuncionarioOnboardingCreate,
    FuncionarioOnboardingResponse,
    OnboardingAlert,
    # Dashboard
    OnboardingDashboard,
    OnboardingFilter,
    OnboardingReport,
    OnboardingStats,
    ProgressComplete,
    # Progress
    ProgressCreate,
    ProgressDetailResponse,
    ProgressListResponse,
    ProgressResponse,
    ProgressUpdate,
    # Step
    StepCreate,
    StepResponse,
    StepUpdate,
)

# Services
from .services import OnboardingError, OnboardingService

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
    "OnboardingError",
    # Router
    "onboarding_router",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
