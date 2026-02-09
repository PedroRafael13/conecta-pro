"""
Schemas comuns para integrações governamentais.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    """Response padrão da API."""

    success: bool = Field(..., description="Sucesso da operacao")
    message: str = Field(..., description="Mensagem descritiva")
    data: dict[str, Any] | None = Field(default=None, description="Dados")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp",
    )
