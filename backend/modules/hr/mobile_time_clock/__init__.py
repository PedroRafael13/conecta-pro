"""Módulo Mobile Time Clock - Registro de ponto via app mobile.

Este módulo fornece:
- Registro de dispositivos móveis (smartphones/tablets)
- Check-in/check-out via app com validação de localização (geofencing)
- Suporte offline com sincronização posterior
- Validação por biometria, foto selfie, WiFi, beacon, NFC, QR code
- Push notifications para lembretes e confirmações

Estrutura:
- models: Modelos SQLAlchemy (MobileDevice, MobileCheckIn, GeofenceZone, OfflineQueue)
- schemas: Schemas Pydantic para validação de dados
- repositories: Camada de acesso a dados
- services: Lógica de negócio (geofencing, validação, sync, push)
- controllers: Endpoints REST da API
"""

from .controllers import (
    checkin_router,
    device_router,
    geofence_router,
    offline_router,
)

__all__ = [
    "device_router",
    "checkin_router",
    "geofence_router",
    "offline_router",
]
