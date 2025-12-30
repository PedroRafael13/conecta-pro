"""
Schemas de autenticação.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema de requisição de login."""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, description="Senha do usuário")


class TokenResponse(BaseModel):
    """Schema de resposta com tokens."""

    access_token: str = Field(..., description="Token de acesso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field(default="bearer", description="Tipo do token")


class LoginResponse(TokenResponse):
    """Schema de resposta de login."""

    user_id: str = Field(..., description="ID do usuário autenticado")
    email: str = Field(..., description="Email do usuário")
    role: str = Field(..., description="Role/perfil do usuário")


class TokenRefreshRequest(BaseModel):
    """Schema de requisição de refresh de token."""

    refresh_token: str = Field(..., description="Token de refresh")


# Aliases para compatibilidade
Token = TokenResponse
TokenRefresh = TokenRefreshRequest
