"""
Schemas de consentimento do modulo de seguranca LGPD.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class ConsentRequest(BaseModel):
    """Request para registro de consentimento.

    Attributes:
        titular_id: UUID do titular dos dados.
        titular_email: Email do titular.
        purpose: Finalidade do consentimento.
        legal_basis: Base legal LGPD.
        description: Descricao detalhada.
        expiration_days: Dias ate expirar (default 365).
    """

    titular_id: UUID = Field(..., description="UUID do titular dos dados")
    titular_email: EmailStr = Field(..., description="Email do titular")
    purpose: str = Field(
        ...,
        description="Finalidade do consentimento",
        pattern=r"^(marketing|analytics|personalization|service_provision|legal_obligation|vital_interest|public_interest|legitimate_interest)$",
    )
    legal_basis: str = Field(
        ...,
        description="Base legal LGPD (Art. 7)",
        pattern=r"^(consent|contract|legal_obligation|vital_interest|public_policy|research|legitimate_interest|credit_protection)$",
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Descricao detalhada do consentimento",
    )
    expiration_days: int = Field(
        default=365,
        ge=1,
        le=3650,
        description="Dias ate expirar",
    )

    @field_validator("titular_email")
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        """Valida que email tem dominio valido."""
        if not v or "@" not in v:
            raise ValueError("Email invalido")
        return v.lower()

    model_config = {
        "json_schema_extra": {
            "example": {
                "titular_id": "123e4567-e89b-12d3-a456-426614174000",
                "titular_email": "usuario@exemplo.com",
                "purpose": "marketing",
                "legal_basis": "consent",
                "description": "Consentimento para envio de emails promocionais",
                "expiration_days": 365,
            }
        }
    }


class ConsentResponse(BaseModel):
    """Response de operacoes de consentimento."""

    consent_id: str = Field(..., description="ID do consentimento")
    titular_id: str = Field(..., description="ID do titular")
    purpose: str = Field(..., description="Finalidade")
    legal_basis: str = Field(..., description="Base legal")
    status: str = Field(..., description="Status do consentimento")


class ConsentListResponse(BaseModel):
    """Response com lista de consentimentos."""

    titular_id: str = Field(..., description="ID do titular")
    consents: list[dict[str, Any]] = Field(..., description="Lista de consentimentos")
    total: int = Field(..., description="Total de consentimentos")
