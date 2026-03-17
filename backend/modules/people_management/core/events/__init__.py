"""
GP Event Bus - Sistema de eventos para Gestao de Pessoas.
Implementa comunicacao em tempo real entre os 7 modulos.
"""

from .event_bus import Event, EventActor, EventContext, EventPriority, GPEventBus, get_event_bus
from .event_types import GPEventTypes
from .handlers import EventHandler

__all__ = [
    "GPEventBus",
    "Event",
    "EventPriority",
    "EventActor",
    "EventContext",
    "GPEventTypes",
    "EventHandler",
    "get_event_bus",
]
