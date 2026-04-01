"""
Schemas de criptografia do modulo de seguranca LGPD.
"""

from typing import Any

from pydantic import BaseModel, Field


class EncryptDataRequest(BaseModel):
    """Request para criptografia de dados.

    Attributes:
        data: Dados a serem criptografados (string ou objeto JSON).
        algorithm: Algoritmo de criptografia (default: AES-256-GCM).
        key_id: ID da chave a usar (opcional, usa default se nao informado).
    """

    data: str = Field(
        ...,
        min_length=1,
        max_length=1_000_000,
        description="Dados a criptografar (max 1MB)",
    )
    algorithm: str = Field(
        default="aes-256-gcm",
        description="Algoritmo de criptografia",
        pattern=r"^(aes-256-gcm|aes-256-cbc|fernet|chacha20-poly1305)$",
    )
    key_id: str | None = Field(
        default=None,
        description="ID da chave (usa default se nao informado)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": "Dados sensiveis para criptografar",
                "algorithm": "aes-256-gcm",
                "key_id": None,
            }
        }
    }


class DecryptDataRequest(BaseModel):
    """Request para descriptografia de dados.

    Attributes:
        encrypted_data: Dados criptografados em base64.
        key_id: ID da chave usada na criptografia.
    """

    encrypted_data: str = Field(
        ...,
        min_length=1,
        description="Dados criptografados em base64",
    )
    key_id: str | None = Field(
        default=None,
        description="ID da chave usada na criptografia",
    )


class EncryptionResponse(BaseModel):
    """Response de operacoes de criptografia."""

    encrypted: dict[str, Any] = Field(..., description="Dados criptografados")
    algorithm: str = Field(..., description="Algoritmo utilizado")
    key_hint: str = Field(..., description="Hint da chave utilizada")
