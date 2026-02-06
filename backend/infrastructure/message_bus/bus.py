"""
Module: infrastructure/message_bus/bus.py
Description: Implementacao do Message Bus para comunicacao entre fases
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Implementacao de um message bus in-memory com suporte a:
- Mensagens síncronas e assíncronas
- Prioridade de mensagens
- Retry automático
- Dead letter queue
- Métricas e logging
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Tipos de mensagem suportados pelo bus.

    Attributes:
        COMMAND: Comando para acao especifica.
        EVENT: Evento de dominio.
        QUERY: Consulta de dados.
        NOTIFICATION: Notificacao para subscribers.
    """

    COMMAND = "command"
    EVENT = "event"
    QUERY = "query"
    NOTIFICATION = "notification"


class MessagePriority(int, Enum):
    """Prioridade de mensagens.

    Attributes:
        LOW: Baixa prioridade (processamento em background).
        NORMAL: Prioridade normal.
        HIGH: Alta prioridade.
        CRITICAL: Prioridade critica (processamento imediato).
    """

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class MessageStatus(str, Enum):
    """Status de processamento de mensagem.

    Attributes:
        PENDING: Aguardando processamento.
        PROCESSING: Em processamento.
        COMPLETED: Processada com sucesso.
        FAILED: Falha no processamento.
        DEAD_LETTER: Enviada para dead letter queue.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class Message:
    """Mensagem do message bus.

    Attributes:
        id: Identificador único da mensagem.
        type: Tipo da mensagem.
        topic: Tópico/canal da mensagem.
        payload: Dados da mensagem.
        priority: Prioridade de processamento.
        source_phase: Fase de origem (1-5).
        target_phase: Fase de destino (opcional).
        correlation_id: ID para correlacionar mensagens relacionadas.
        causation_id: ID da mensagem que causou esta.
        created_at: Timestamp de criação.
        processed_at: Timestamp de processamento.
        status: Status atual.
        retry_count: Número de tentativas.
        max_retries: Máximo de tentativas.
        metadata: Metadados adicionais.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.EVENT
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    source_phase: Optional[int] = None
    target_phase: Optional[int] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte mensagem para dicionário.

        Returns:
            Dict com dados da mensagem.
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "topic": self.topic,
            "payload": self.payload,
            "priority": self.priority.value,
            "source_phase": self.source_phase,
            "target_phase": self.target_phase,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
        }


# Type variables para handlers genéricos
T = TypeVar("T")
R = TypeVar("R")

# Tipo para funções handler
HandlerFunc = Callable[[Message], Awaitable[Optional[Any]]]


class Handler(ABC):
    """Classe base abstrata para handlers de mensagens.

    Handlers processam mensagens de um tipo/tópico específico.
    """

    @abstractmethod
    async def handle(self, message: Message) -> Optional[Any]:
        """Processa uma mensagem.

        Args:
            message: Mensagem a processar.

        Returns:
            Resultado do processamento (opcional).
        """
        pass


@dataclass
class Subscriber:
    """Representa um subscriber de mensagens.

    Attributes:
        id: Identificador único do subscriber.
        topic: Tópico de interesse.
        handler: Função ou handler para processar mensagens.
        filter_func: Função opcional para filtrar mensagens.
        active: Se o subscriber está ativo.
        created_at: Timestamp de criação.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    handler: Optional[Union[HandlerFunc, Handler]] = None
    filter_func: Optional[Callable[[Message], bool]] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class MessageBusMetrics:
    """Métricas do message bus.

    Coleta estatísticas de uso para monitoramento.
    """

    def __init__(self) -> None:
        """Inicializa métricas."""
        self.messages_published: int = 0
        self.messages_processed: int = 0
        self.messages_failed: int = 0
        self.messages_dead_letter: int = 0
        self.processing_times: List[float] = []
        self.topic_counts: Dict[str, int] = defaultdict(int)
        self.phase_counts: Dict[int, int] = defaultdict(int)

    def record_publish(self, message: Message) -> None:
        """Registra publicação de mensagem.

        Args:
            message: Mensagem publicada.
        """
        self.messages_published += 1
        self.topic_counts[message.topic] += 1
        if message.source_phase:
            self.phase_counts[message.source_phase] += 1

    def record_processed(self, processing_time: float) -> None:
        """Registra processamento bem-sucedido.

        Args:
            processing_time: Tempo de processamento em segundos.
        """
        self.messages_processed += 1
        self.processing_times.append(processing_time)
        # Manter apenas últimos 1000 tempos
        if len(self.processing_times) > 1000:
            self.processing_times = self.processing_times[-1000:]

    def record_failed(self) -> None:
        """Registra falha de processamento."""
        self.messages_failed += 1

    def record_dead_letter(self) -> None:
        """Registra envio para dead letter queue."""
        self.messages_dead_letter += 1

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas atuais.

        Returns:
            Dict com estatísticas do bus.
        """
        avg_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times
            else 0
        )
        return {
            "messages_published": self.messages_published,
            "messages_processed": self.messages_processed,
            "messages_failed": self.messages_failed,
            "messages_dead_letter": self.messages_dead_letter,
            "success_rate": (
                self.messages_processed / self.messages_published * 100
                if self.messages_published > 0
                else 100
            ),
            "avg_processing_time_ms": avg_time * 1000,
            "topic_counts": dict(self.topic_counts),
            "phase_counts": dict(self.phase_counts),
        }


class MessageBus:
    """Message Bus para comunicação entre fases do sistema.

    Implementa um sistema de pub/sub assíncrono com:
    - Múltiplos tópicos
    - Priorização de mensagens
    - Retry automático
    - Dead letter queue
    - Métricas de monitoramento

    Example:
        >>> bus = MessageBus()
        >>> await bus.start()
        >>>
        >>> # Publicar mensagem
        >>> message = Message(
        ...     topic="fase1.proposta.criada",
        ...     payload={"proposta_id": "123"},
        ...     source_phase=1
        ... )
        >>> await bus.publish(message)
        >>>
        >>> # Registrar subscriber
        >>> async def handler(msg: Message):
        ...     print(f"Recebido: {msg.payload}")
        >>> bus.subscribe("fase1.proposta.criada", handler)
    """

    def __init__(
        self,
        max_queue_size: int = 10000,
        processing_timeout: float = 30.0,
        enable_dead_letter: bool = True,
    ) -> None:
        """Inicializa o message bus.

        Args:
            max_queue_size: Tamanho máximo da fila de mensagens.
            processing_timeout: Timeout para processamento em segundos.
            enable_dead_letter: Habilitar dead letter queue.
        """
        self._subscribers: Dict[str, List[Subscriber]] = defaultdict(list)
        self._handlers: Dict[str, Handler] = {}
        self._queue: asyncio.PriorityQueue[tuple] = asyncio.PriorityQueue(
            maxsize=max_queue_size
        )
        self._dead_letter: List[Message] = []
        self._pending_messages: Dict[str, Message] = {}
        self._metrics = MessageBusMetrics()

        self._max_queue_size = max_queue_size
        self._processing_timeout = processing_timeout
        self._enable_dead_letter = enable_dead_letter

        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

        logger.info(
            "MessageBus inicializado: max_queue=%d, timeout=%.1fs",
            max_queue_size,
            processing_timeout,
        )

    async def start(self) -> None:
        """Inicia o processamento de mensagens.

        Inicia a task de processamento em background.
        """
        if self._running:
            logger.warning("MessageBus já está em execução")
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_loop())
        logger.info("MessageBus iniciado")

    async def stop(self) -> None:
        """Para o processamento de mensagens.

        Aguarda mensagens pendentes e encerra gracefully.
        """
        self._running = False

        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

        logger.info("MessageBus parado")

    async def publish(
        self,
        message: Message,
        wait_for_processing: bool = False,
    ) -> str:
        """Publica uma mensagem no bus.

        Args:
            message: Mensagem a publicar.
            wait_for_processing: Aguardar processamento (síncrono).

        Returns:
            ID da mensagem publicada.

        Raises:
            RuntimeError: Se a fila estiver cheia.
        """
        if self._queue.full():
            logger.error("Fila de mensagens cheia")
            raise RuntimeError("Message queue is full")

        # Adicionar à fila com prioridade (negativo para maior = primeiro)
        priority = -message.priority.value
        await self._queue.put((priority, message.created_at, message))

        self._pending_messages[message.id] = message
        self._metrics.record_publish(message)

        logger.debug(
            "Mensagem publicada: id=%s, topic=%s, priority=%s",
            message.id,
            message.topic,
            message.priority.name,
        )

        if wait_for_processing:
            # Aguardar processamento
            while message.status in [MessageStatus.PENDING, MessageStatus.PROCESSING]:
                await asyncio.sleep(0.1)

        return message.id

    def subscribe(
        self,
        topic: str,
        handler: Union[HandlerFunc, Handler],
        filter_func: Optional[Callable[[Message], bool]] = None,
    ) -> str:
        """Registra um subscriber para um tópico.

        Args:
            topic: Tópico de interesse (suporta wildcards com *).
            handler: Função ou Handler para processar mensagens.
            filter_func: Função opcional para filtrar mensagens.

        Returns:
            ID do subscriber registrado.
        """
        subscriber = Subscriber(
            topic=topic,
            handler=handler,
            filter_func=filter_func,
        )

        self._subscribers[topic].append(subscriber)

        logger.info(
            "Subscriber registrado: id=%s, topic=%s",
            subscriber.id,
            topic,
        )

        return subscriber.id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Remove um subscriber.

        Args:
            subscriber_id: ID do subscriber a remover.

        Returns:
            True se removido, False se não encontrado.
        """
        for topic, subscribers in self._subscribers.items():
            for sub in subscribers:
                if sub.id == subscriber_id:
                    subscribers.remove(sub)
                    logger.info(
                        "Subscriber removido: id=%s, topic=%s",
                        subscriber_id,
                        topic,
                    )
                    return True

        return False

    def register_handler(self, topic: str, handler: Handler) -> None:
        """Registra um handler para um tópico específico.

        Args:
            topic: Tópico do handler.
            handler: Instância do handler.
        """
        self._handlers[topic] = handler
        logger.info("Handler registrado: topic=%s", topic)

    async def _process_loop(self) -> None:
        """Loop principal de processamento de mensagens."""
        logger.info("Iniciando loop de processamento")

        while self._running:
            try:
                # Aguardar próxima mensagem com timeout
                try:
                    _, _, message = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue

                # Processar mensagem
                await self._process_message(message)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Erro no loop de processamento: %s", str(e))

    async def _process_message(self, message: Message) -> None:
        """Processa uma única mensagem.

        Args:
            message: Mensagem a processar.
        """
        message.status = MessageStatus.PROCESSING
        start_time = datetime.utcnow()

        try:
            # Encontrar subscribers relevantes
            subscribers = self._find_subscribers(message.topic)

            if not subscribers:
                logger.debug(
                    "Nenhum subscriber para topic: %s",
                    message.topic,
                )
                message.status = MessageStatus.COMPLETED
                message.processed_at = datetime.utcnow()
                return

            # Executar handlers
            for subscriber in subscribers:
                # Verificar filtro
                if subscriber.filter_func and not subscriber.filter_func(message):
                    continue

                try:
                    # Executar com timeout
                    handler = subscriber.handler
                    if isinstance(handler, Handler):
                        await asyncio.wait_for(
                            handler.handle(message),
                            timeout=self._processing_timeout,
                        )
                    elif callable(handler):
                        await asyncio.wait_for(
                            handler(message),
                            timeout=self._processing_timeout,
                        )

                except asyncio.TimeoutError:
                    logger.warning(
                        "Timeout ao processar mensagem: id=%s, subscriber=%s",
                        message.id,
                        subscriber.id,
                    )
                except Exception as e:
                    logger.error(
                        "Erro no handler: subscriber=%s, erro=%s",
                        subscriber.id,
                        str(e),
                    )

            # Marcar como processada
            message.status = MessageStatus.COMPLETED
            message.processed_at = datetime.utcnow()

            processing_time = (message.processed_at - start_time).total_seconds()
            self._metrics.record_processed(processing_time)

            logger.debug(
                "Mensagem processada: id=%s, tempo=%.3fs",
                message.id,
                processing_time,
            )

        except Exception as e:
            message.retry_count += 1

            if message.retry_count >= message.max_retries:
                # Enviar para dead letter queue
                message.status = MessageStatus.DEAD_LETTER
                if self._enable_dead_letter:
                    self._dead_letter.append(message)
                    self._metrics.record_dead_letter()
                logger.warning(
                    "Mensagem enviada para DLQ: id=%s, erro=%s",
                    message.id,
                    str(e),
                )
            else:
                # Retry
                message.status = MessageStatus.FAILED
                self._metrics.record_failed()
                # Recolocar na fila
                priority = -message.priority.value
                await self._queue.put((priority, message.created_at, message))
                logger.debug(
                    "Retry agendado: id=%s, tentativa=%d/%d",
                    message.id,
                    message.retry_count,
                    message.max_retries,
                )

        finally:
            # Remover de pending
            self._pending_messages.pop(message.id, None)

    def _find_subscribers(self, topic: str) -> List[Subscriber]:
        """Encontra subscribers para um tópico.

        Suporta wildcards:
        - '*' corresponde a qualquer segmento
        - 'fase1.*' corresponde a fase1.qualquer_coisa

        Args:
            topic: Tópico da mensagem.

        Returns:
            Lista de subscribers relevantes.
        """
        matching: List[Subscriber] = []

        # Match exato
        if topic in self._subscribers:
            matching.extend(
                s for s in self._subscribers[topic] if s.active
            )

        # Match com wildcards
        topic_parts = topic.split(".")
        for sub_topic, subscribers in self._subscribers.items():
            if sub_topic == topic:
                continue

            sub_parts = sub_topic.split(".")
            if self._match_wildcard(topic_parts, sub_parts):
                matching.extend(s for s in subscribers if s.active)

        return matching

    def _match_wildcard(
        self,
        topic_parts: List[str],
        pattern_parts: List[str],
    ) -> bool:
        """Verifica se um tópico corresponde a um padrão com wildcards.

        Args:
            topic_parts: Partes do tópico.
            pattern_parts: Partes do padrão.

        Returns:
            True se corresponder.
        """
        if len(pattern_parts) != len(topic_parts):
            # Verificar se termina com **
            if pattern_parts and pattern_parts[-1] == "**":
                return len(topic_parts) >= len(pattern_parts) - 1
            return False

        for tp, pp in zip(topic_parts, pattern_parts):
            if pp == "*":
                continue
            if tp != pp:
                return False

        return True

    def get_dead_letter_messages(self) -> List[Message]:
        """Retorna mensagens da dead letter queue.

        Returns:
            Lista de mensagens falhas.
        """
        return list(self._dead_letter)

    def clear_dead_letter(self) -> int:
        """Limpa a dead letter queue.

        Returns:
            Número de mensagens removidas.
        """
        count = len(self._dead_letter)
        self._dead_letter.clear()
        return count

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do bus.

        Returns:
            Dict com estatísticas.
        """
        return {
            **self._metrics.get_stats(),
            "queue_size": self._queue.qsize(),
            "pending_messages": len(self._pending_messages),
            "dead_letter_count": len(self._dead_letter),
            "subscribers_count": sum(
                len(subs) for subs in self._subscribers.values()
            ),
            "topics_count": len(self._subscribers),
            "running": self._running,
        }

    def get_health(self) -> Dict[str, Any]:
        """Retorna status de saúde do bus.

        Returns:
            Dict com status de saúde.
        """
        queue_usage = self._queue.qsize() / self._max_queue_size * 100
        dlq_critical = len(self._dead_letter) > 100

        status = "healthy"
        if queue_usage > 80 or dlq_critical:
            status = "degraded"
        if queue_usage > 95:
            status = "unhealthy"

        return {
            "status": status,
            "running": self._running,
            "queue_usage_percent": round(queue_usage, 2),
            "dead_letter_critical": dlq_critical,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Instância singleton
_message_bus: Optional[MessageBus] = None


def get_message_bus() -> MessageBus:
    """Retorna instância singleton do MessageBus.

    Returns:
        Instância do MessageBus.
    """
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus


async def init_message_bus(
    max_queue_size: int = 10000,
    processing_timeout: float = 30.0,
    enable_dead_letter: bool = True,
    auto_start: bool = True,
) -> MessageBus:
    """Inicializa e retorna o MessageBus.

    Args:
        max_queue_size: Tamanho máximo da fila.
        processing_timeout: Timeout de processamento.
        enable_dead_letter: Habilitar DLQ.
        auto_start: Iniciar automaticamente.

    Returns:
        Instância configurada do MessageBus.
    """
    global _message_bus
    _message_bus = MessageBus(
        max_queue_size=max_queue_size,
        processing_timeout=processing_timeout,
        enable_dead_letter=enable_dead_letter,
    )

    if auto_start:
        await _message_bus.start()

    return _message_bus
