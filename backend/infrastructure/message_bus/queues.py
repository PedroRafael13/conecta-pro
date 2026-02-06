"""
Module: infrastructure/message_bus/queues.py
Description: Sistema de filas para o message bus
Author: Conecta PRO Team
Date: 2026-01-10
Quality Score Target: 99+/100

Este modulo implementa:
- Filas nomeadas para processamento especifico
- Dead Letter Queue (DLQ)
- Configuracoes de fila
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .bus import Message, MessagePriority, MessageStatus

logger = logging.getLogger(__name__)


class QueueConfig(BaseModel):
    """Configuracao de uma fila.

    Attributes:
        name: Nome da fila.
        max_size: Tamanho maximo.
        processing_timeout: Timeout de processamento em segundos.
        max_retries: Maximo de tentativas por mensagem.
        enable_dlq: Habilitar dead letter queue.
        dlq_name: Nome da DLQ (default: {name}_dlq).
        priority_enabled: Habilitar priorização.
    """

    name: str = Field(..., min_length=1, max_length=100)
    max_size: int = Field(default=10000, ge=1, le=1000000)
    processing_timeout: float = Field(default=30.0, ge=1.0, le=600.0)
    max_retries: int = Field(default=3, ge=0, le=10)
    enable_dlq: bool = Field(default=True)
    dlq_name: Optional[str] = None
    priority_enabled: bool = Field(default=True)

    def __init__(self, **data: Any) -> None:
        """Inicializa configuracao com valores default calculados."""
        super().__init__(**data)
        if self.dlq_name is None:
            self.dlq_name = f"{self.name}_dlq"


@dataclass
class QueueStats:
    """Estatisticas de uma fila.

    Attributes:
        messages_enqueued: Total de mensagens adicionadas.
        messages_processed: Total de mensagens processadas.
        messages_failed: Total de mensagens falhas.
        messages_dlq: Total enviadas para DLQ.
        current_size: Tamanho atual.
        avg_processing_time: Tempo medio de processamento (ms).
    """

    messages_enqueued: int = 0
    messages_processed: int = 0
    messages_failed: int = 0
    messages_dlq: int = 0
    current_size: int = 0
    avg_processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario.

        Returns:
            Dict com estatisticas.
        """
        return {
            "messages_enqueued": self.messages_enqueued,
            "messages_processed": self.messages_processed,
            "messages_failed": self.messages_failed,
            "messages_dlq": self.messages_dlq,
            "current_size": self.current_size,
            "avg_processing_time_ms": round(self.avg_processing_time, 2),
            "success_rate": (
                round(self.messages_processed / self.messages_enqueued * 100, 2)
                if self.messages_enqueued > 0
                else 100.0
            ),
        }


class Queue:
    """Fila de mensagens nomeada.

    Fornece uma fila independente para processamento especifico
    com suporte a priorização e dead letter queue.

    Example:
        >>> config = QueueConfig(name="emails")
        >>> queue = Queue(config)
        >>> await queue.enqueue(message)
        >>> message = await queue.dequeue()
    """

    def __init__(self, config: QueueConfig) -> None:
        """Inicializa a fila.

        Args:
            config: Configuracao da fila.
        """
        self.config = config
        self._queue: asyncio.PriorityQueue[tuple] = asyncio.PriorityQueue(
            maxsize=config.max_size
        )
        self._dlq: List[Message] = []
        self._stats = QueueStats()
        self._processing_times: List[float] = []
        self._lock = asyncio.Lock()

        logger.info(
            "Fila criada: name=%s, max_size=%d",
            config.name,
            config.max_size,
        )

    @property
    def name(self) -> str:
        """Nome da fila.

        Returns:
            Nome configurado.
        """
        return self.config.name

    @property
    def size(self) -> int:
        """Tamanho atual da fila.

        Returns:
            Numero de mensagens na fila.
        """
        return self._queue.qsize()

    @property
    def is_full(self) -> bool:
        """Verifica se a fila esta cheia.

        Returns:
            True se cheia.
        """
        return self._queue.full()

    @property
    def is_empty(self) -> bool:
        """Verifica se a fila esta vazia.

        Returns:
            True se vazia.
        """
        return self._queue.empty()

    async def enqueue(
        self,
        message: Message,
        priority: Optional[MessagePriority] = None,
    ) -> bool:
        """Adiciona mensagem na fila.

        Args:
            message: Mensagem a adicionar.
            priority: Prioridade (sobrescreve a da mensagem).

        Returns:
            True se adicionada com sucesso.

        Raises:
            RuntimeError: Se a fila estiver cheia.
        """
        if self.is_full:
            logger.warning("Fila %s cheia", self.name)
            raise RuntimeError(f"Queue {self.name} is full")

        effective_priority = priority or message.priority
        # Negativo para maior prioridade = primeiro
        queue_priority = -effective_priority.value

        async with self._lock:
            await self._queue.put((queue_priority, message.created_at, message))
            self._stats.messages_enqueued += 1
            self._stats.current_size = self.size

        logger.debug(
            "Mensagem adicionada: queue=%s, id=%s, priority=%s",
            self.name,
            message.id,
            effective_priority.name,
        )

        return True

    async def dequeue(self, timeout: Optional[float] = None) -> Optional[Message]:
        """Remove e retorna a proxima mensagem da fila.

        Args:
            timeout: Timeout em segundos (None = espera indefinidamente).

        Returns:
            Proxima mensagem ou None se timeout.
        """
        try:
            effective_timeout = timeout or self.config.processing_timeout

            _, _, message = await asyncio.wait_for(
                self._queue.get(),
                timeout=effective_timeout,
            )

            async with self._lock:
                self._stats.current_size = self.size

            return message

        except asyncio.TimeoutError:
            return None

    async def peek(self) -> Optional[Message]:
        """Retorna a proxima mensagem sem remove-la.

        Returns:
            Proxima mensagem ou None se vazia.
        """
        if self.is_empty:
            return None

        # Nao ha metodo peek nativo, entao fazemos get/put
        try:
            priority, timestamp, message = await asyncio.wait_for(
                self._queue.get(),
                timeout=0.1,
            )
            await self._queue.put((priority, timestamp, message))
            return message
        except asyncio.TimeoutError:
            return None

    def record_success(self, processing_time: float) -> None:
        """Registra processamento bem sucedido.

        Args:
            processing_time: Tempo de processamento em segundos.
        """
        self._stats.messages_processed += 1
        self._processing_times.append(processing_time * 1000)  # Convert to ms

        # Manter apenas ultimos 100 tempos
        if len(self._processing_times) > 100:
            self._processing_times = self._processing_times[-100:]

        self._stats.avg_processing_time = (
            sum(self._processing_times) / len(self._processing_times)
        )

    def record_failure(self, message: Message) -> None:
        """Registra falha de processamento.

        Args:
            message: Mensagem que falhou.
        """
        self._stats.messages_failed += 1

        if message.retry_count >= self.config.max_retries:
            self._send_to_dlq(message)

    def _send_to_dlq(self, message: Message) -> None:
        """Envia mensagem para dead letter queue.

        Args:
            message: Mensagem para DLQ.
        """
        if not self.config.enable_dlq:
            return

        message.status = MessageStatus.DEAD_LETTER
        self._dlq.append(message)
        self._stats.messages_dlq += 1

        logger.warning(
            "Mensagem enviada para DLQ: queue=%s, id=%s",
            self.name,
            message.id,
        )

    def get_dlq_messages(self) -> List[Message]:
        """Retorna mensagens da DLQ.

        Returns:
            Lista de mensagens na DLQ.
        """
        return list(self._dlq)

    def clear_dlq(self) -> int:
        """Limpa a DLQ.

        Returns:
            Numero de mensagens removidas.
        """
        count = len(self._dlq)
        self._dlq.clear()
        return count

    async def reprocess_dlq(self) -> int:
        """Reprocessa mensagens da DLQ.

        Move mensagens da DLQ de volta para a fila principal.

        Returns:
            Numero de mensagens reprocessadas.
        """
        count = 0
        messages_to_reprocess = list(self._dlq)
        self._dlq.clear()

        for message in messages_to_reprocess:
            message.status = MessageStatus.PENDING
            message.retry_count = 0
            await self.enqueue(message)
            count += 1

        logger.info(
            "DLQ reprocessada: queue=%s, mensagens=%d",
            self.name,
            count,
        )

        return count

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas da fila.

        Returns:
            Dict com estatisticas.
        """
        return {
            "name": self.name,
            "config": {
                "max_size": self.config.max_size,
                "processing_timeout": self.config.processing_timeout,
                "max_retries": self.config.max_retries,
                "enable_dlq": self.config.enable_dlq,
            },
            "stats": self._stats.to_dict(),
            "dlq_size": len(self._dlq),
        }

    def get_health(self) -> Dict[str, Any]:
        """Retorna status de saude da fila.

        Returns:
            Dict com status.
        """
        usage = self.size / self.config.max_size * 100

        status = "healthy"
        if usage > 80:
            status = "degraded"
        if usage > 95:
            status = "unhealthy"

        return {
            "status": status,
            "queue_name": self.name,
            "size": self.size,
            "max_size": self.config.max_size,
            "usage_percent": round(usage, 2),
            "dlq_size": len(self._dlq),
            "timestamp": datetime.utcnow().isoformat(),
        }


class DeadLetterQueue:
    """Dead Letter Queue centralizada.

    Armazena mensagens que falharam apos todas as tentativas.
    Permite analise e reprocessamento.
    """

    def __init__(self, max_size: int = 10000) -> None:
        """Inicializa a DLQ.

        Args:
            max_size: Tamanho maximo.
        """
        self._messages: List[Message] = []
        self._max_size = max_size
        self._lock = asyncio.Lock()

        logger.info("DeadLetterQueue criada: max_size=%d", max_size)

    @property
    def size(self) -> int:
        """Tamanho atual da DLQ.

        Returns:
            Numero de mensagens.
        """
        return len(self._messages)

    async def add(self, message: Message) -> bool:
        """Adiciona mensagem na DLQ.

        Args:
            message: Mensagem a adicionar.

        Returns:
            True se adicionada.
        """
        async with self._lock:
            if len(self._messages) >= self._max_size:
                # Remove mais antiga
                self._messages.pop(0)

            message.status = MessageStatus.DEAD_LETTER
            self._messages.append(message)

            logger.warning(
                "Mensagem adicionada na DLQ: id=%s, topic=%s",
                message.id,
                message.topic,
            )

            return True

    async def get_all(self) -> List[Message]:
        """Retorna todas as mensagens.

        Returns:
            Lista de mensagens.
        """
        async with self._lock:
            return list(self._messages)

    async def get_by_topic(self, topic: str) -> List[Message]:
        """Retorna mensagens de um topico.

        Args:
            topic: Topico a filtrar.

        Returns:
            Lista de mensagens do topico.
        """
        async with self._lock:
            return [m for m in self._messages if m.topic == topic]

    async def clear(self) -> int:
        """Limpa a DLQ.

        Returns:
            Numero de mensagens removidas.
        """
        async with self._lock:
            count = len(self._messages)
            self._messages.clear()
            return count

    async def remove(self, message_id: str) -> bool:
        """Remove uma mensagem especifica.

        Args:
            message_id: ID da mensagem.

        Returns:
            True se removida.
        """
        async with self._lock:
            for i, msg in enumerate(self._messages):
                if msg.id == message_id:
                    self._messages.pop(i)
                    return True
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas da DLQ.

        Returns:
            Dict com estatisticas.
        """
        topic_counts: Dict[str, int] = {}
        for msg in self._messages:
            topic_counts[msg.topic] = topic_counts.get(msg.topic, 0) + 1

        return {
            "size": self.size,
            "max_size": self._max_size,
            "usage_percent": round(self.size / self._max_size * 100, 2),
            "topics": topic_counts,
        }


# Registry de filas
_queues: Dict[str, Queue] = {}
_global_dlq: Optional[DeadLetterQueue] = None


def get_queue(name: str) -> Optional[Queue]:
    """Retorna uma fila pelo nome.

    Args:
        name: Nome da fila.

    Returns:
        Fila ou None se nao existir.
    """
    return _queues.get(name)


def create_queue(config: QueueConfig) -> Queue:
    """Cria e registra uma nova fila.

    Args:
        config: Configuracao da fila.

    Returns:
        Fila criada.

    Raises:
        ValueError: Se fila ja existir.
    """
    if config.name in _queues:
        raise ValueError(f"Queue {config.name} already exists")

    queue = Queue(config)
    _queues[config.name] = queue

    logger.info("Fila registrada: %s", config.name)

    return queue


def list_queues() -> List[str]:
    """Lista nomes de filas registradas.

    Returns:
        Lista de nomes.
    """
    return list(_queues.keys())


def get_all_queues_stats() -> Dict[str, Any]:
    """Retorna estatisticas de todas as filas.

    Returns:
        Dict com estatisticas por fila.
    """
    return {name: queue.get_stats() for name, queue in _queues.items()}


def get_global_dlq() -> DeadLetterQueue:
    """Retorna a DLQ global.

    Returns:
        Instancia da DLQ global.
    """
    global _global_dlq
    if _global_dlq is None:
        _global_dlq = DeadLetterQueue()
    return _global_dlq
