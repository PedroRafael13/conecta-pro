"""
Module: infrastructure/message_bus
Description: Sistema de message bus para comunicacao entre fases do Conecta PRO
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo implementa um sistema de message bus assíncrono para:
- Comunicacao entre fases (1-5)
- Event sourcing
- Pub/Sub para notificacoes
- Dead letter queue para mensagens falhas
"""

from .bus import (
    Handler,
    Message,
    MessageBus,
    MessagePriority,
    MessageStatus,
    MessageType,
    Subscriber,
    get_message_bus,
    init_message_bus,
)
from .events import (
    DomainEvent,
    Event,
    EventType,
    IntegrationEvent,
    publish_event,
    subscribe_to_event,
)
from .queues import (
    DeadLetterQueue,
    Queue,
    QueueConfig,
    create_queue,
    get_queue,
)

__all__ = [
    # Bus
    "MessageBus",
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageStatus",
    "Handler",
    "Subscriber",
    "get_message_bus",
    "init_message_bus",
    # Events
    "Event",
    "EventType",
    "DomainEvent",
    "IntegrationEvent",
    "publish_event",
    "subscribe_to_event",
    # Queues
    "Queue",
    "QueueConfig",
    "DeadLetterQueue",
    "get_queue",
    "create_queue",
]

__version__ = "1.0.0"
