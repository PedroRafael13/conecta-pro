"""BaseAgent - Classe base para todos os agentes financeiros de IA."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent(ABC):
    """Classe base para agentes financeiros de IA."""

    name: str = "base_agent"

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(f"agents.{self.name}")

    async def execute(self, *args, **kwargs) -> Any:
        """Executa o agente com logging e fallback automático."""
        start = time.time()
        self.logger.info(f"[{self.name}] Iniciando execução")
        try:
            result = await self._execute(*args, **kwargs)
            elapsed = time.time() - start
            self.logger.info(f"[{self.name}] Concluído em {elapsed:.2f}s")
            return result
        except Exception as exc:
            self.logger.warning(f"[{self.name}] Erro na execução IA: {exc}. Usando fallback.")
            return await self._fallback(*args, **kwargs)

    @abstractmethod
    async def _execute(self, *args, **kwargs) -> Any:
        pass

    async def _fallback(self, *args, **kwargs) -> Any:
        """Fallback padrão - retorna None."""
        return None
