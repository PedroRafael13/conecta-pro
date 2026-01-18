"""
Controllers do módulo de Onboarding Digital.

Este pacote exporta os routers FastAPI para os endpoints da API.
"""

from .onboarding_controller import router as onboarding_router

__all__ = [
    "onboarding_router",
]
