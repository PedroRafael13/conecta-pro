"""
Controllers do modulo de Pesquisa de Clima Operacional.

Exporta o router FastAPI para registro na aplicacao.
"""

from modules.retention.climate.controllers.climate_controller import router

__all__ = [
    "router",
]
