"""
Re-exportacao do service de Onboarding Digital.

Permite acesso ao OnboardingService a partir do modulo de Recursos Humanos.
"""

try:
    from modules.retention.onboarding.services.onboarding_service import OnboardingService
except ImportError:
    OnboardingService = None  # type: ignore[assignment, misc]

__all__ = ["OnboardingService"]
