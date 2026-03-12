"""
Base Agent - Classe base para todos os agentes de licitacao
============================================================
Fornece estrutura comum: logging, config, retry, status tracking.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AgentStatus(StrEnum):
    """Status de implementacao do agente."""

    OPERATIONAL = "operational"
    DEVELOPMENT = "development"
    PLANNED = "planned"


class ExecutionStatus(StrEnum):
    """Status de execucao de uma tarefa do agente."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class AgentConfig:
    """Configuracao base de um agente."""

    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    retry_backoff_factor: float = 2.0
    timeout_seconds: float = 120.0
    enabled: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Resultado padrao de execucao de um agente."""

    agent_name: str
    status: ExecutionStatus
    data: Any = None
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: float = 0.0
    retries_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_ms": self.duration_ms,
            "retries_used": self.retries_used,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Classe base para todos os agentes do sistema de licitacoes.

    Cada agente herda desta classe e implementa o metodo execute().
    A base fornece: logging, configuracao, retry com backoff, tracking de status.
    """

    # Subclasses devem sobrescrever
    AGENT_NAME: str = "base"
    AGENT_DESCRIPTION: str = ""
    AGENT_STATUS: AgentStatus = AgentStatus.PLANNED

    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig()
        self.logger = logging.getLogger(f"bidding.agents.{self.AGENT_NAME}")
        self._last_result: ExecutionResult | None = None

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Metodo principal de execucao do agente.

        Subclasses DEVEM implementar este metodo com a logica especifica.
        Retorna dados especificos do agente.
        """
        ...

    async def run(self, **kwargs) -> ExecutionResult:
        """
        Executa o agente com retry, logging e tracking.

        Este metodo envolve execute() com toda a infraestrutura.
        Use run() ao inves de execute() diretamente.
        """
        if not self.config.enabled:
            self.logger.warning(f"Agente {self.AGENT_NAME} esta desabilitado.")
            return ExecutionResult(
                agent_name=self.AGENT_NAME,
                status=ExecutionStatus.CANCELLED,
                error="Agente desabilitado",
            )

        started_at = datetime.utcnow()
        start_time = time.monotonic()
        retries = 0
        last_error: str | None = None

        while retries <= self.config.max_retries:
            try:
                if retries > 0:
                    delay = self.config.retry_delay_seconds * (self.config.retry_backoff_factor ** (retries - 1))
                    self.logger.info(f"[{self.AGENT_NAME}] Retry {retries}/{self.config.max_retries} em {delay:.1f}s")
                    await asyncio.sleep(delay)

                self.logger.info(f"[{self.AGENT_NAME}] Iniciando execucao (tentativa {retries + 1})")

                result_data = await asyncio.wait_for(
                    self.execute(**kwargs),
                    timeout=self.config.timeout_seconds,
                )

                elapsed = (time.monotonic() - start_time) * 1000
                result = ExecutionResult(
                    agent_name=self.AGENT_NAME,
                    status=ExecutionStatus.SUCCESS,
                    data=result_data,
                    started_at=started_at,
                    finished_at=datetime.utcnow(),
                    duration_ms=round(elapsed, 2),
                    retries_used=retries,
                )
                self._last_result = result
                self.logger.info(f"[{self.AGENT_NAME}] Concluido com sucesso em {elapsed:.0f}ms ({retries} retries)")
                return result

            except TimeoutError:
                last_error = f"Timeout apos {self.config.timeout_seconds}s"
                self.logger.error(f"[{self.AGENT_NAME}] {last_error}")
                retries += 1

            except asyncio.CancelledError:
                elapsed = (time.monotonic() - start_time) * 1000
                result = ExecutionResult(
                    agent_name=self.AGENT_NAME,
                    status=ExecutionStatus.CANCELLED,
                    error="Execucao cancelada",
                    started_at=started_at,
                    finished_at=datetime.utcnow(),
                    duration_ms=round(elapsed, 2),
                    retries_used=retries,
                )
                self._last_result = result
                return result

            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                self.logger.error(f"[{self.AGENT_NAME}] Erro: {last_error}")
                retries += 1

        # Esgotou retries
        elapsed = (time.monotonic() - start_time) * 1000
        result = ExecutionResult(
            agent_name=self.AGENT_NAME,
            status=ExecutionStatus.FAILED,
            error=last_error,
            started_at=started_at,
            finished_at=datetime.utcnow(),
            duration_ms=round(elapsed, 2),
            retries_used=retries - 1,
        )
        self._last_result = result
        self.logger.error(f"[{self.AGENT_NAME}] Falhou apos {retries - 1} retries: {last_error}")
        return result

    @property
    def last_result(self) -> ExecutionResult | None:
        """Ultimo resultado de execucao."""
        return self._last_result

    def info(self) -> dict[str, Any]:
        """Retorna informacoes do agente."""
        return {
            "name": self.AGENT_NAME,
            "description": self.AGENT_DESCRIPTION,
            "status": self.AGENT_STATUS.value,
            "enabled": self.config.enabled,
            "max_retries": self.config.max_retries,
            "timeout_seconds": self.config.timeout_seconds,
        }
