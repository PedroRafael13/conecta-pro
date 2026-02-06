"""
Schemas para integrações com eSocial.
"""

from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class ESocialEventRequest(BaseModel):
    """Request para evento eSocial.

    Attributes:
        tipo_evento: Tipo do evento (S-2200, S-2299, S-2220).
        funcionario_id: ID do funcionário.
        dados: Dados específicos do evento.
        ambiente: Ambiente (produção ou homologação).
    """

    tipo_evento: str = Field(
        ...,
        description="Tipo do evento eSocial",
        pattern=r"^S-(2200|2299|2220|2230|2240|2210)$",
    )
    funcionario_id: UUID = Field(..., description="ID do funcionario")
    dados: Dict[str, Any] = Field(..., description="Dados do evento")
    ambiente: str = Field(
        default="homologacao",
        description="Ambiente",
        pattern=r"^(producao|homologacao)$",
    )
