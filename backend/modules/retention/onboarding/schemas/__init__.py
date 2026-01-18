"""
Schemas do módulo de Onboarding Digital.

Este pacote exporta todos os schemas Pydantic para validação
e serialização de dados nas operações de API.
"""

from .onboarding_schemas import (
    # Base
    MessageResponse,
    PaginationParams,
    PaginatedResponse,
    # Step
    StepBase,
    StepCreate,
    StepUpdate,
    StepResponse,
    # Checklist
    ChecklistBase,
    ChecklistCreate,
    ChecklistUpdate,
    ChecklistResponse,
    ChecklistDetailResponse,
    ChecklistListResponse,
    # Progress
    ProgressBase,
    ProgressCreate,
    ProgressUpdate,
    ProgressComplete,
    ProgressResponse,
    ProgressDetailResponse,
    ProgressListResponse,
    # Funcionário
    FuncionarioOnboardingCreate,
    FuncionarioOnboardingResponse,
    # Dashboard e Métricas
    OnboardingAlert,
    OnboardingStats,
    OnboardingDashboard,
    OnboardingFilter,
    BulkProgressUpdate,
    OnboardingReport,
)

__all__ = [
    # Base
    "MessageResponse",
    "PaginationParams",
    "PaginatedResponse",
    # Step
    "StepBase",
    "StepCreate",
    "StepUpdate",
    "StepResponse",
    # Checklist
    "ChecklistBase",
    "ChecklistCreate",
    "ChecklistUpdate",
    "ChecklistResponse",
    "ChecklistDetailResponse",
    "ChecklistListResponse",
    # Progress
    "ProgressBase",
    "ProgressCreate",
    "ProgressUpdate",
    "ProgressComplete",
    "ProgressResponse",
    "ProgressDetailResponse",
    "ProgressListResponse",
    # Funcionário
    "FuncionarioOnboardingCreate",
    "FuncionarioOnboardingResponse",
    # Dashboard e Métricas
    "OnboardingAlert",
    "OnboardingStats",
    "OnboardingDashboard",
    "OnboardingFilter",
    "BulkProgressUpdate",
    "OnboardingReport",
]
