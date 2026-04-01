"""
Mobile API Module - APIs otimizadas para dispositivos móveis.

DEPRECATED: Use 'modules.gestao' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.

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

import warnings

warnings.warn(
    "Importing from 'modules.mobile' is deprecated. "
    "Use 'modules.gestao' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.mobile.controllers import router as mobile_router  # noqa: E402
from modules.mobile.gateway import CompressionMiddleware, DeviceDetector, MobileGateway  # noqa: E402
from modules.mobile.services import (  # noqa: E402
    MobileMetrics,
    MobileSecurity,
    OfflineSyncManager,
    PushNotificationService,
    get_metrics,
)

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
