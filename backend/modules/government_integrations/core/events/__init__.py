"""
Sistema de Eventos para Integração entre Módulos.

Implementa:
- Event-driven architecture para comunicação entre módulos
- Pub/sub com Redis
- Outbox pattern para garantia de entrega
- Handlers por tipo de evento
"""

from .event_bus import (
    EventBus,
    Event,
    EventHandler,
    get_event_bus,
)
from .event_types import (
    TipoEvento,
    EventoDocumentoFiscal,
    EventoFolhaPagamento,
    EventoSincronizacao,
    EventoSistema,
    EventoErro,
)
from .outbox import (
    OutboxManager,
    OutboxEntry,
    get_outbox_manager,
)

__all__ = [
    # Event Bus
    "EventBus",
    "Event",
    "EventHandler",
    "get_event_bus",
    # Event Types
    "TipoEvento",
    "EventoDocumentoFiscal",
    "EventoFolhaPagamento",
    "EventoSincronizacao",
    "EventoSistema",
    "EventoErro",
    # Outbox
    "OutboxManager",
    "OutboxEntry",
    "get_outbox_manager",
]
