"""
Mobile API Module - APIs otimizadas para dispositivos móveis.

Sprint 02 - API Mobile Nativa

Este módulo implementa:
- Mobile Gateway com otimizações de rede e compressão
- Push Notifications (FCM/APNs)
- Offline Sync Manager com resolução de conflitos
- Batch Operations para combinação de requisições
- Mobile Security com rate limiting e validação
- Mobile Metrics para analytics

Endpoints:
- GET  /mobile/health         - Health check
- GET  /mobile/config         - Configuração do app
- GET  /mobile/dashboard      - Dashboard otimizado
- POST /mobile/sync           - Sincronização offline
- GET  /mobile/sync/status    - Status de sync
- POST /mobile/batch          - Operações em batch
- POST /mobile/devices/register   - Registrar dispositivo
- GET  /mobile/notifications  - Listar notificações
- POST /mobile/notifications/{id}/read  - Marcar como lida
"""

from modules.mobile.gateway import MobileGateway, CompressionMiddleware, DeviceDetector
from modules.mobile.services import (
    PushNotificationService,
    OfflineSyncManager,
    MobileSecurity,
    MobileMetrics,
    get_metrics,
)
from modules.mobile.controllers import router as mobile_router

__all__ = [
    # Gateway
    "MobileGateway",
    "CompressionMiddleware",
    "DeviceDetector",
    # Services
    "PushNotificationService",
    "OfflineSyncManager",
    "MobileSecurity",
    "MobileMetrics",
    "get_metrics",
    # Router
    "mobile_router",
]
