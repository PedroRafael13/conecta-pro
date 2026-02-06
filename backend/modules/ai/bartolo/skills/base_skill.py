"""
Base class para Skills do Bartolo
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging
import re

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """Classe base para todas as skills"""

    name: str = ""
    description: str = ""
    commands: List[str] = []

    def __init__(self, data_connector: Optional["DataConnector"] = None):
        """
        Inicializa a skill.

        Args:
            data_connector: Conector de dados para consultas reais.
                            Se None, a skill usa templates estaticos como fallback.
        """
        self.data_connector = data_connector

    @property
    def has_data_connector(self) -> bool:
        """Verifica se o data_connector esta disponivel."""
        return self.data_connector is not None

    @abstractmethod
    async def execute(self, command: str, args: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a skill com os argumentos fornecidos"""
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Retorna texto de ajuda da skill"""
        pass

    def parse_command(self, text: str) -> tuple[str, List[str]]:
        """Parse do comando e argumentos"""
        parts = text.strip().split()
        if not parts:
            return "", []

        # Remove o / inicial se existir
        cmd = parts[0].lstrip("/")
        args = parts[1:] if len(parts) > 1 else []

        return cmd, args
