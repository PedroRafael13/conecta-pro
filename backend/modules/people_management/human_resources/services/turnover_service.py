"""
Re-exportacao do service de Predicao de Turnover.

Permite acesso ao TurnoverService a partir do modulo de Recursos Humanos.
"""

try:
    from modules.retention.turnover.services.turnover_service import TurnoverService
except ImportError:
    TurnoverService = None  # type: ignore[assignment, misc]

__all__ = ["TurnoverService"]
