"""
Models do módulo de Onboarding Digital.

Este pacote exporta todos os modelos SQLAlchemy necessários para
o gerenciamento do processo de integração de novos funcionários.
"""

from .onboarding_models import (
    OnboardingChecklist,
    OnboardingStep,
    OnboardingProgress,
    StepType,
    ProgressStatus,
)

__all__ = [
    # Models
    "OnboardingChecklist",
    "OnboardingStep",
    "OnboardingProgress",
    # Enums
    "StepType",
    "ProgressStatus",
]
