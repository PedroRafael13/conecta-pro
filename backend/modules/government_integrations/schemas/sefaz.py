"""
Schemas para integrações com SEFAZ (NFe/NFCe).
"""

from typing import Any

from pydantic import BaseModel, Field


class NFERequest(BaseModel):
    """Request para emissão de NFe.

    Attributes:
        tipo: Tipo do documento (nfe ou nfce).
        destinatario: Dados do destinatário.
        produtos: Lista de produtos.
        pagamento: Dados de pagamento.
    """

    tipo: str = Field(
        default="nfe",
        description="Tipo do documento",
        pattern=r"^(nfe|nfce)$",
    )
    destinatario: dict[str, Any] = Field(..., description="Dados do destinatario")
    produtos: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=990,
        description="Lista de produtos",
    )
    pagamento: dict[str, Any] = Field(..., description="Dados de pagamento")
    observacoes: str | None = Field(
        default=None,
        max_length=5000,
        description="Observacoes",
    )
