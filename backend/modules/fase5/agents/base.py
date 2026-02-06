"""
modules/fase5/agents/base.py - Base Agent
=========================================
Classe base para agentes do sistema multi-agente
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Tipos de agentes disponíveis."""
    EMAIL_INTELLIGENCE = "email_intelligence"
    CCT_COMPLIANCE = "cct_compliance"
    INTEGRATION_HUB = "integration_hub"
    ANALYTICS = "analytics"
    SECURITY_MANAGER = "security_manager"


class AgentStatus(str, Enum):
    """Status do agente."""
    IDLE = "idle"
    RUNNING = "running"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentMessage:
    """Mensagem entre agentes."""
    from_agent: AgentType
    to_agent: AgentType
    message_type: str
    message_id: UUID = field(default_factory=uuid4)
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    reply_to: Optional[UUID] = None


@dataclass
class AgentTask:
    """Tarefa a ser processada pelo agente."""
    task_type: str
    task_id: UUID = field(default_factory=uuid4)
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, menor = mais prioritario
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Classe base para todos os agentes.

    Cada agente deve implementar:
    - process_task: Processar uma tarefa
    - handle_message: Lidar com mensagens de outros agentes
    """

    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        self.agent_id = uuid4()
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.stats = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "messages_received": 0,
            "messages_sent": 0,
            "started_at": None,
            "last_activity": None
        }
        self._message_handlers: Dict[str, Callable] = {}

    async def start(self) -> None:
        """Inicia o agente."""
        logger.info(f"Starting agent {self.agent_type.value} ({self.agent_id})")
        self.running = True
        self.status = AgentStatus.RUNNING
        self.stats["started_at"] = datetime.now(timezone.utc)

        # Iniciar processadores
        await asyncio.gather(
            self._task_processor(),
            self._message_processor()
        )

    async def stop(self) -> None:
        """Para o agente."""
        logger.info(f"Stopping agent {self.agent_type.value}")
        self.running = False
        self.status = AgentStatus.STOPPED

    async def submit_task(self, task: AgentTask) -> None:
        """Submete tarefa para processamento."""
        await self.task_queue.put(task)
        logger.debug(f"Task {task.task_id} submitted to {self.agent_type.value}")

    async def send_message(self, message: AgentMessage) -> None:
        """Envia mensagem para outro agente."""
        # Em produção, usar message broker (Redis, RabbitMQ)
        self.stats["messages_sent"] += 1
        logger.debug(f"Message sent from {self.agent_type.value} to {message.to_agent.value}")

    async def receive_message(self, message: AgentMessage) -> None:
        """Recebe mensagem de outro agente."""
        await self.message_queue.put(message)
        self.stats["messages_received"] += 1

    async def _task_processor(self) -> None:
        """Processador de tarefas."""
        while self.running:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                self.status = AgentStatus.PROCESSING
                task.started_at = datetime.now(timezone.utc)

                try:
                    result = await self.process_task(task)
                    task.result = result
                    task.completed_at = datetime.now(timezone.utc)
                    self.stats["tasks_processed"] += 1

                except Exception as e:
                    task.error = str(e)
                    task.completed_at = datetime.now(timezone.utc)
                    self.stats["tasks_failed"] += 1
                    logger.error(f"Task {task.task_id} failed: {e}")

                finally:
                    self.status = AgentStatus.RUNNING
                    self.stats["last_activity"] = datetime.now(timezone.utc)

            except asyncio.TimeoutError:
                continue

    async def _message_processor(self) -> None:
        """Processador de mensagens."""
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                await self.handle_message(message)
                self.stats["last_activity"] = datetime.now(timezone.utc)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Message processing error: {e}")

    @abstractmethod
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Processa uma tarefa. Deve ser implementado por subclasses."""
        pass

    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> None:
        """Lida com mensagem recebida. Deve ser implementado por subclasses."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do agente."""
        return {
            "agent_id": str(self.agent_id),
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "stats": {
                **self.stats,
                "started_at": self.stats["started_at"].isoformat() if self.stats["started_at"] else None,
                "last_activity": self.stats["last_activity"].isoformat() if self.stats["last_activity"] else None
            },
            "queue_sizes": {
                "tasks": self.task_queue.qsize(),
                "messages": self.message_queue.qsize()
            }
        }
