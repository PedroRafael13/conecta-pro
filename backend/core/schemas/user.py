"""
Schemas de usuário.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from core.models.user import UserRole


class UserBase(BaseModel):
    """Schema base de usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    role: UserRole = Field(default=UserRole.OPERATOR, description="Role do usuário")


class UserCreate(UserBase):
    """Schema para criação de usuário."""

    password: str = Field(..., min_length=8, description="Senha do usuário")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida força da senha."""
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    permissions: Optional[list[str]] = None


class UserResponse(UserBase):
    """Schema de resposta de usuário."""

    id: UUID = Field(..., description="ID do usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    permissions: list[str] = Field(
        default_factory=list, description="Permissões extras"
    )
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    last_login: Optional[str] = Field(None, description="Último login")

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    """Schema para listagem de usuários."""

    items: list[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
