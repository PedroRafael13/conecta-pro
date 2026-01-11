"""
Schemas de exclusao de dados (direito ao esquecimento) do modulo de seguranca LGPD.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ErasureRequestSchema(BaseModel):
    """Request para direito ao esquecimento.

    Attributes:
        titular_id: UUID do titular solicitante.
        titular_email: Email para confirmacao.
        reason: Motivo da solicitacao.
        scope: Escopo da exclusao (all, personal, marketing).
    """

    titular_id: UUID = Field(..., description="UUID do titular")
    titular_email: EmailStr = Field(..., description="Email para confirmacao")
    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo da solicitacao de exclusao",
    )
    scope: str = Field(
        default="all",
        description="Escopo da exclusao",
        pattern=r"^(all|personal|marketing|analytics)$",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "titular_id": "123e4567-e89b-12d3-a456-426614174000",
                "titular_email": "usuario@exemplo.com",
                "reason": "Solicitacao do titular para remocao completa de dados",
                "scope": "all",
            }
        }
    }


class ErasureStatusResponse(BaseModel):
    """Response com status de solicitacao de exclusao."""

    request_id: str = Field(..., description="ID da solicitacao")
    titular_id: str = Field(..., description="ID do titular")
    scope: str = Field(..., description="Escopo da exclusao")
    status: str = Field(..., description="Status atual")
    estimated_completion: Optional[str] = Field(None, description="Prazo estimado")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")
