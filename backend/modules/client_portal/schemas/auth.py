"""
Schemas de autenticacao do Portal do Cliente.

Define os modelos de request/response para login, refresh e logout.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortalLoginRequest(BaseModel):
    """Request para login no portal do cliente."""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Login do portal (configurado pelo admin)",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Senha do portal",
    )


class PortalLoginResponse(BaseModel):
    """Response apos login bem-sucedido no portal."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="Token JWT de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_at: datetime = Field(..., description="Data/hora de expiracao do token")
    client_id: str = Field(..., description="UUID do cliente autenticado")
    client_name: str = Field(..., description="Nome do cliente autenticado")


class PortalTokenRefresh(BaseModel):
    """Request para renovar token do portal."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="Token JWT atual para renovacao")
