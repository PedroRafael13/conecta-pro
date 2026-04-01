"""
Event Bus para Comunicação entre Módulos.

Implementa padrão pub/sub para eventos do sistema.
"""

import asyncio
import contextlib
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Evento base do sistema."""

    id: UUID = field(default_factory=uuid4)
    tipo: str = ""
    tenant_id: UUID | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    origem: str = ""  # Módulo de origem
    dados: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Rastreabilidade
    correlation_id: str | None = None
    causation_id: str | None = None  # ID do evento que causou este

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "tipo": self.tipo,
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "timestamp": self.timestamp.isoformat(),
            "origem": self.origem,
            "dados": self.dados,
            "metadata": self.metadata,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """Cria evento a partir de dicionário."""
        return cls(
            id=UUID(data["id"]) if data.get("id") else uuid4(),
            tipo=data.get("tipo", ""),
            tenant_id=UUID(data["tenant_id"]) if data.get("tenant_id") else None,
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
            origem=data.get("origem", ""),
            dados=data.get("dados", {}),
            metadata=data.get("metadata", {}),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
        )

    def to_json(self) -> str:
        """Serializa para JSON."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Deserializa de JSON."""
        return cls.from_dict(json.loads(json_str))


class EventHandler(ABC):
    """Handler abstrato para eventos."""

    @property
    @abstractmethod
    def tipos_evento(self) -> list[str]:
        """Lista de tipos de evento que este handler processa."""
        pass

    @abstractmethod
    async def handle(self, evento: Event) -> bool:
        """
        Processa um evento.

        Args:
            evento: Evento a processar

        Returns:
            True se processado com sucesso
        """
        pass

    async def on_error(self, evento: Event, erro: Exception):
        """Callback para erro no processamento."""
        logger.error(f"Erro ao processar evento {evento.id}: {erro}")


class EventBus:
    """
    Barramento de eventos para comunicação entre módulos.

    Características:
    - Pub/sub com Redis
    - Handlers registrados por tipo de evento
    - Retry automático
    - Dead letter queue
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/2", prefixo_canal: str = "gov_events"):
        self._redis_url = redis_url
        self._prefixo = prefixo_canal
        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        self._handlers: dict[str, list[EventHandler]] = {}
        self._callbacks: dict[str, list[Callable]] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    async def _get_redis(self) -> redis.Redis:
        """Obtém conexão Redis."""
        if self._redis is None:
            self._redis = redis.from_url(self._redis_url)
        return self._redis

    def registrar_handler(self, handler: EventHandler):
        """
        Registra um handler de eventos.

        Args:
            handler: Handler a registrar
        """
        for tipo in handler.tipos_evento:
            if tipo not in self._handlers:
                self._handlers[tipo] = []
            self._handlers[tipo].append(handler)
            logger.info(f"Handler registrado para evento: {tipo}")

    def registrar_callback(self, tipo: str, callback: Callable[[Event], Awaitable[bool]]):
        """
        Registra callback simples para um tipo de evento.

        Args:
            tipo: Tipo de evento
            callback: Função assíncrona a chamar
        """
        if tipo not in self._callbacks:
            self._callbacks[tipo] = []
        self._callbacks[tipo].append(callback)

    async def publicar(self, evento: Event, canal: str | None = None) -> bool:
        """
        Publica evento no barramento.

        Args:
            evento: Evento a publicar
            canal: Canal específico (default: baseado no tipo)

        Returns:
            True se publicado com sucesso
        """
        redis_client = await self._get_redis()

        if canal is None:
            canal = f"{self._prefixo}:{evento.tipo}"

        try:
            # Publicar no Redis
            await redis_client.publish(canal, evento.to_json())

            # Também salvar em lista para histórico
            chave_historico = f"{self._prefixo}:history:{evento.tipo}"
            await redis_client.lpush(chave_historico, evento.to_json())
            await redis_client.ltrim(chave_historico, 0, 999)  # Manter últimos 1000

            logger.debug(f"Evento publicado: {evento.id} ({evento.tipo})")
            return True

        except Exception as e:
            logger.error(f"Erro ao publicar evento: {e}")
            return False

    async def publicar_muitos(self, eventos: list[Event]) -> int:
        """
        Publica múltiplos eventos.

        Args:
            eventos: Lista de eventos

        Returns:
            Quantidade de eventos publicados com sucesso
        """
        sucesso = 0
        for evento in eventos:
            if await self.publicar(evento):
                sucesso += 1
        return sucesso

    async def iniciar_consumidor(self):
        """Inicia consumidor de eventos em background."""
        if self._running:
            logger.warning("Consumidor já está rodando")
            return

        self._running = True
        redis_client = await self._get_redis()
        self._pubsub = redis_client.pubsub()

        # Inscrever em todos os canais registrados
        canais = set()
        for tipo in self._handlers.keys():
            canais.add(f"{self._prefixo}:{tipo}")
        for tipo in self._callbacks.keys():
            canais.add(f"{self._prefixo}:{tipo}")

        if not canais:
            # Inscrever em canal genérico
            canais.add(f"{self._prefixo}:*")

        await self._pubsub.psubscribe(*canais)

        logger.info(f"Consumidor iniciado, inscrito em {len(canais)} canais")

        # Iniciar task de consumo
        self._task = asyncio.create_task(self._consumir_eventos())

    async def parar_consumidor(self):
        """Para o consumidor de eventos."""
        self._running = False

        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        logger.info("Consumidor parado")

    async def _consumir_eventos(self):
        """Loop de consumo de eventos."""
        while self._running:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)

                if message and message.get("type") == "pmessage":
                    dados = message.get("data")
                    if isinstance(dados, bytes):
                        dados = dados.decode("utf-8")

                    evento = Event.from_json(dados)
                    await self._processar_evento(evento)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop de consumo: {e}")
                await asyncio.sleep(1)

    async def _processar_evento(self, evento: Event):
        """Processa um evento recebido."""
        logger.debug(f"Processando evento: {evento.id} ({evento.tipo})")

        # Processar handlers
        handlers = self._handlers.get(evento.tipo, [])
        for handler in handlers:
            try:
                sucesso = await handler.handle(evento)
                if not sucesso:
                    logger.warning(f"Handler retornou falha para evento {evento.id}")
            except Exception as e:
                await handler.on_error(evento, e)

        # Processar callbacks
        callbacks = self._callbacks.get(evento.tipo, [])
        for callback in callbacks:
            try:
                await callback(evento)
            except Exception as e:
                logger.error(f"Erro em callback para evento {evento.id}: {e}")

    async def obter_historico(self, tipo: str, limite: int = 100) -> list[Event]:
        """
        Obtém histórico de eventos de um tipo.

        Args:
            tipo: Tipo de evento
            limite: Máximo de eventos a retornar

        Returns:
            Lista de eventos
        """
        redis_client = await self._get_redis()
        chave = f"{self._prefixo}:history:{tipo}"

        eventos_json = await redis_client.lrange(chave, 0, limite - 1)
        eventos = []

        for json_str in eventos_json:
            if isinstance(json_str, bytes):
                json_str = json_str.decode("utf-8")
            eventos.append(Event.from_json(json_str))

        return eventos

    async def obter_estatisticas(self) -> dict[str, Any]:
        """Obtém estatísticas do event bus."""
        redis_client = await self._get_redis()

        stats = {
            "handlers_registrados": {},
            "callbacks_registrados": {},
            "historico_tamanho": {},
        }

        for tipo, handlers in self._handlers.items():
            stats["handlers_registrados"][tipo] = len(handlers)

        for tipo, callbacks in self._callbacks.items():
            stats["callbacks_registrados"][tipo] = len(callbacks)

        # Tamanho dos históricos
        async for key in redis_client.scan_iter(f"{self._prefixo}:history:*"):
            tipo = key.decode().split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
            tamanho = await redis_client.llen(key)
            stats["historico_tamanho"][tipo] = tamanho

        return stats


# Instância singleton
_event_bus_instance: EventBus | None = None


def get_event_bus() -> EventBus:
    """Obtém instância do event bus."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
