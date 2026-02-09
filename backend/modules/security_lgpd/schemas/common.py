"""
Schemas comuns do modulo de seguranca LGPD.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    """Response padrao da API.

    Attributes:
        success: Indica se operacao foi bem sucedida.
        message: Mensagem descritiva.
        data: Dados retornados (opcional).
        timestamp: Timestamp da resposta.
    """

    success: bool = Field(..., description="Sucesso da operacao")
    message: str = Field(..., description="Mensagem descritiva")
    data: dict[str, Any] | None = Field(default=None, description="Dados")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Operacao realizada com sucesso",
                "data": {"key": "value"},
                "timestamp": "2026-01-10T12:00:00Z",
            }
        }
    }
