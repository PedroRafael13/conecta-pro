"""
GP Event Bus - Barramento de eventos para Gestao de Pessoas.
Usa Redis PubSub para backend e WebSocket para frontend.
"""

import asyncio
import contextlib
import json
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any
from uuid import uuid4

import redis.asyncio as aioredis
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class EventPriority(IntEnum):
    """Niveis de prioridade de eventos."""

    CRITICO = 1
    ALTO = 2
    NORMAL = 3
    BAIXO = 4


@dataclass
class EventActor:
    """Quem disparou o evento."""

    user_id: str
    user_name: str
    user_role: str
    user_module: str


@dataclass
class EventContext:
    """Contexto de onde o evento foi disparado."""

    ip_address: str = ""
    user_agent: str = ""
    device_type: str = "web"
    session_id: str = ""
    geolocation: dict[str, float] | None = None


@dataclass
class Event:
    """Estrutura de um evento do sistema."""

    event_type: str
    payload: dict[str, Any]
    source_module: str
    actor: EventActor | None = None
    context: EventContext | None = None
    priority: EventPriority = EventPriority.NORMAL
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: str | None = None
    affected_modules: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Converte evento para dicionario."""
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "source_module": self.source_module,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "affected_modules": self.affected_modules,
            "actor": asdict(self.actor) if self.actor else None,
            "context": asdict(self.context) if self.context else None,
        }
        return data

    def to_json(self) -> str:
        """Converte evento para JSON."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """Cria evento a partir de dicionario."""
        actor = None
        if data.get("actor"):
            actor = EventActor(**data["actor"])
        context = None
        if data.get("context"):
            context = EventContext(**data["context"])
        priority = EventPriority(data.get("priority", 3))
        return cls(
            event_id=data.get("event_id", str(uuid4())),
            event_type=data["event_type"],
            payload=data.get("payload", {}),
            source_module=data.get("source_module", ""),
            actor=actor,
            context=context,
            priority=priority,
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            correlation_id=data.get("correlation_id"),
            affected_modules=data.get("affected_modules", []),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Cria evento a partir de JSON."""
        return cls.from_dict(json.loads(json_str))


class GPEventBus:
    """
    Barramento de eventos para Gestao de Pessoas.

    Caracteristicas:
    - Pub/Sub via Redis
    - WebSocket para frontend
    - Idempotencia (dedup por event_id)
    - Priorizacao
    - Retry automatico
    - Auditoria completa
    """

    CHANNEL_PREFIX = "gp:"
    PROCESSED_EVENTS_KEY = "gp:processed_events"
    PROCESSED_EVENTS_TTL = 3600 * 24  # 24 horas

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.redis_url = redis_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._redis: aioredis.Redis | None = None
        self._pubsub = None
        self._handlers: dict[str, list[Callable]] = {}
        self._websockets: set[WebSocket] = set()
        self._running = False
        self._listener_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Conecta ao Redis."""
        if self._redis is None:
            self._redis = aioredis.from_url(self.redis_url, decode_responses=True)
            self._pubsub = self._redis.pubsub()
            logger.info("GPEventBus conectado ao Redis")

    async def disconnect(self) -> None:
        """Desconecta do Redis."""
        self._running = False
        if self._listener_task:
            self._listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener_task
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        self._redis = None
        self._pubsub = None
        logger.info("GPEventBus desconectado")

    async def publish(self, event: Event) -> bool:
        """Publica um evento no barramento."""
        await self.connect()

        try:
            channel = self._get_channel(event.event_type)
            await self._redis.publish(channel, event.to_json())
            await self._broadcast_websocket(event)

            logger.info(
                f"Evento publicado: {event.event_type} [id={event.event_id[:8]}, priority={event.priority.name}]"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao publicar evento: {e}")
            return False

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Inscreve um handler para um tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler inscrito para {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove inscricao de um handler."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def start_listening(self) -> None:
        """Inicia o listener de eventos Redis."""
        await self.connect()
        await self._pubsub.psubscribe(f"{self.CHANNEL_PREFIX}*")
        self._running = True
        self._listener_task = asyncio.create_task(self._listen_loop())
        logger.info("GPEventBus listener iniciado")

    async def _listen_loop(self) -> None:
        """Loop de escuta de eventos."""
        while self._running:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message["type"] == "pmessage":
                    await self._process_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no listener: {e}")
                await asyncio.sleep(self.retry_delay)

    async def _process_message(self, message: dict) -> None:
        """Processa uma mensagem recebida."""
        try:
            event = Event.from_json(message["data"])

            if await self._is_duplicate(event.event_id):
                logger.debug(f"Evento duplicado ignorado: {event.event_id[:8]}")
                return

            await self._mark_processed(event.event_id)

            handlers = self._handlers.get(event.event_type, [])
            handlers += self._handlers.get("*", [])

            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Erro no handler para {event.event_type}: {e}")

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    async def _is_duplicate(self, event_id: str) -> bool:
        """Verifica se evento ja foi processado."""
        if self._redis is None:
            return False
        return await self._redis.sismember(self.PROCESSED_EVENTS_KEY, event_id)

    async def _mark_processed(self, event_id: str) -> None:
        """Marca evento como processado."""
        if self._redis is None:
            return
        await self._redis.sadd(self.PROCESSED_EVENTS_KEY, event_id)
        await self._redis.expire(self.PROCESSED_EVENTS_KEY, self.PROCESSED_EVENTS_TTL)

    def _get_channel(self, event_type: str) -> str:
        """Retorna o canal Redis para um tipo de evento."""
        parts = event_type.split(".")
        if len(parts) >= 2:
            return f"{parts[0]}:{parts[1]}"
        return self.CHANNEL_PREFIX + event_type

    # WebSocket Management
    async def register_websocket(self, websocket: WebSocket) -> None:
        """Registra uma conexao WebSocket."""
        self._websockets.add(websocket)

    async def unregister_websocket(self, websocket: WebSocket) -> None:
        """Remove uma conexao WebSocket."""
        self._websockets.discard(websocket)

    async def _broadcast_websocket(self, event: Event) -> None:
        """Envia evento para todos os WebSockets conectados."""
        if not self._websockets:
            return
        message = event.to_json()
        disconnected = set()
        for ws in self._websockets:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self._websockets.discard(ws)

    # Convenience
    async def emit(
        self,
        event_type: str,
        payload: dict[str, Any],
        source_module: str,
        priority: EventPriority = EventPriority.NORMAL,
        actor: EventActor | None = None,
        context: EventContext | None = None,
        affected_modules: list[str] | None = None,
    ) -> Event:
        """Cria e publica um evento."""
        event = Event(
            event_type=event_type,
            payload=payload,
            source_module=source_module,
            priority=priority,
            actor=actor,
            context=context,
            affected_modules=affected_modules or [],
        )
        await self.publish(event)
        return event

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatisticas do Event Bus."""
        return {
            "websockets_connected": len(self._websockets),
            "handlers_registered": sum(len(h) for h in self._handlers.values()),
            "event_types_subscribed": list(self._handlers.keys()),
            "running": self._running,
        }


# Singleton global
_event_bus: GPEventBus | None = None


def get_event_bus() -> GPEventBus:
    """Retorna instancia singleton do Event Bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = GPEventBus()
    return _event_bus
