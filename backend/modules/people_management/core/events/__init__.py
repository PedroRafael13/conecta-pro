"""
GP Event Bus — agora aponta para o ConectaEventBus unificado.
Retrocompatibilidade total: GPEventBus, Event, get_event_bus mantidos.
"""

# Importar do barramento unificado
from infrastructure.event_bus import (
    ConectaEvent as Event,  # alias retrocompat
)
from infrastructure.event_bus import (
    ConectaEventBus as GPEventBus,  # alias retrocompat
)
from infrastructure.event_bus import (
    EventActor,
    EventContext,
    EventPriority,
    EventTypes,
    event_bus,
    get_event_bus,
)

from .event_types import GPEventTypes
from .handlers import EventHandler

__all__ = [
    "GPEventBus",
    "Event",
    "EventPriority",
    "EventActor",
    "EventContext",
    "EventTypes",
    "GPEventTypes",
    "EventHandler",
    "event_bus",
    "get_event_bus",
]
