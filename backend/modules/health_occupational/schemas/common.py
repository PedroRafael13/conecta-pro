"""
Schemas Comuns - Saude Ocupacional
==================================

Schemas compartilhados entre os dominios.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class StandardResponse(BaseModel):
    """Response padrao da API."""
    success: bool = Field(..., description="Sucesso da operacao")
    message: str = Field(..., description="Mensagem descritiva")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Dados retornados")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp da resposta",
    )


class PaginationParams(BaseModel):
    """Parametros de paginacao."""
    page: int = Field(default=1, ge=1, description="Numero da pagina")
    size: int = Field(default=20, ge=1, le=100, description="Itens por pagina")


class PaginatedResponse(BaseModel):
    """Response com paginacao."""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

    @property
    def has_next(self) -> bool:
        """Verifica se ha proxima pagina."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Verifica se ha pagina anterior."""
        return self.page > 1


class ErrorResponse(BaseModel):
    """Response de erro."""
    success: bool = Field(default=False)
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
