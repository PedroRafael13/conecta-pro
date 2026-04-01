"""
Modulo de Monitoramento - Early Warning System.

DEPRECATED: Use 'modules.inteligencia' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.

Niveis de Alerta:
- GREEN: Operacao normal, metricas dentro do esperado
- YELLOW: Atencao necessaria, tendencia preocupante
- ORANGE: Acao corretiva necessaria em 24-48h
- RED: Intervencao imediata, risco critico

Uso:
    from modules.monitoring import router
    app.include_router(router, prefix="/api/v1")

    # Ou para usar os services diretamente:
    from modules.monitoring.services import EarlyWarningService
    service = EarlyWarningService(db)
    await service.check_metric("cpu_usage", 85.5)
"""

import warnings

warnings.warn(
    "Importing from 'modules.monitoring' is deprecated. "
    "Use 'modules.inteligencia' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from fastapi import APIRouter as _APIRouter  # noqa: E402

from .controllers import router as _monitoring_router  # noqa: E402
from .models import Alert, AlertLevel, AlertStatus, MetricThreshold, ThresholdType  # noqa: E402

# Combined router: monitoring (/monitoring/...) + search (/search/...)
# Injected here to avoid modifying main_production.py (ZONA PROIBIDA).
try:
    from modules.search.controller import router as _search_router

    router = _APIRouter()
    router.include_router(_monitoring_router)
    router.include_router(_search_router)
except Exception:  # noqa: BLE001
    router = _monitoring_router
from .services import (  # noqa: E402
    AlertManagerService,
    DashboardService,
    EarlyWarningService,
    MetricCollectorService,
)

__all__ = [
    # Router
    "router",
    # Models
    "Alert",
    "AlertLevel",
    "AlertStatus",
    "MetricThreshold",
    "ThresholdType",
    # Services
    "EarlyWarningService",
    "MetricCollectorService",
    "AlertManagerService",
    "DashboardService",
]

__version__ = "1.0.0"
