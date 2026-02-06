"""
Modulo de Monitoramento - Early Warning System.

Este modulo implementa o sistema de alerta antecipado (Early Warning System)
baseado na analise Pre-Mortem do projeto Conecta PRO.

Componentes:
- EarlyWarningService: Servico principal de monitoramento
- MetricCollectorService: Coleta de metricas do sistema
- AlertManagerService: Gerenciamento de alertas e notificacoes
- DashboardService: Dashboard de monitoramento

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

from .controllers import router
from .models import Alert, AlertLevel, AlertStatus, MetricThreshold, ThresholdType
from .services import (
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
