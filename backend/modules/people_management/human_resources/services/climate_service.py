"""
Re-exportacao do service de Clima Organizacional.

Permite acesso ao ClimateService a partir do modulo de Recursos Humanos.
"""

try:
    from modules.retention.climate.services.climate_service import ClimateService
except ImportError:
    ClimateService = None  # type: ignore[assignment, misc]

__all__ = ["ClimateService"]
