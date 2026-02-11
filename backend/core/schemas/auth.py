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


class ForgotPasswordRequest(BaseModel):
    """Schema para solicitar reset de senha."""

    email: EmailStr = Field(..., description="Email do usuário")


class ResetPasswordRequest(BaseModel):
    """Schema para redefinir senha com token."""

    token: str = Field(..., description="Token de reset recebido por email")
    new_password: str = Field(..., min_length=8, description="Nova senha (mínimo 8 caracteres)")


# Aliases para compatibilidade
Token = TokenResponse
TokenRefresh = TokenRefreshRequest
