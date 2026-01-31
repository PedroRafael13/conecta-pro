"""
Classe base abstrata para executores de ações.
"""
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from ..action_schemas import ActionRequest, ActionPreview, ActionResult


class BaseActionExecutor(ABC):
    """Classe abstrata para executores de ação."""

    def __init__(self, db: AsyncSession):
        """
        Inicializa executor.

        Args:
            db: Sessão async do SQLAlchemy
        """
        self.db = db

    @abstractmethod
    async def create_preview(self, request: ActionRequest) -> ActionPreview:
        """
        Cria preview da ação para confirmação do usuário.

        Args:
            request: Request de ação

        Returns:
            Preview com detalhes da ação
        """
        pass

    @abstractmethod
    async def execute(self, request: ActionRequest, action_id: str) -> ActionResult:
        """
        Executa a ação confirmada.

        Args:
            request: Request de ação
            action_id: ID da ação

        Returns:
            Resultado da execução
        """
        pass
