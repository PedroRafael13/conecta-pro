"""
Schemas de usuário.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from core.models.user import UserRole


class UserBase(BaseModel):
    """Schema base de usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    name: str = Field(..., min_length=2, max_length=100, description="Nome completo")
    phone: str | None = Field(None, max_length=20, description="Telefone")
    role: UserRole = Field(default=UserRole.OPERATOR, description="Role do usuário")


class UserCreate(UserBase):
    """Schema para criação de usuário."""

    password: str = Field(..., min_length=12, description="Senha do usuário")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida força da senha usando validador centralizado."""
        from core.security.password_validator import validate_password_strength

        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError("; ".join(errors))
        return v


class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""

    name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, max_length=20)
    role: UserRole | None = None
    is_active: bool | None = None
    permissions: list[str] | None = None


class UserResponse(UserBase):
    """Schema de resposta de usuário."""

    id: UUID = Field(..., description="ID do usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    permissions: list[str] = Field(default_factory=list, description="Permissões extras")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    last_login: str | None = Field(None, description="Último login")

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    """Schema para listagem de usuários."""

    items: list[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
