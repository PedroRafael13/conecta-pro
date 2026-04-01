"""
Schemas Pydantic para GedClient (Clientes do GED).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.people_management.ged.models.client import GedClientType


class GedClientBase(BaseModel):
    """Campos compartilhados entre criação e resposta."""

    name: str = Field(..., min_length=2, max_length=255, description="Razão social ou nome do condomínio")
    type: GedClientType = Field(
        default=GedClientType.CONDOMINIO,
        description="Tipo de cliente: condominio ou administradora",
    )
    cnpj: str | None = Field(None, max_length=18, description="CNPJ formatado")
    address: str | None = Field(None, description="Endereço completo")
    contact_name: str | None = Field(None, max_length=255, description="Nome do contato principal")
    contact_email: str | None = Field(None, max_length=255, description="E-mail do contato principal")
    contact_phone: str | None = Field(None, max_length=20, description="Telefone do contato")

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str | None) -> str | None:
        """Valida formato básico do CNPJ (XX.XXX.XXX/XXXX-XX ou apenas dígitos)."""
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 14:
            raise ValueError("CNPJ deve conter exatamente 14 dígitos")
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"


class GedClientCreate(GedClientBase):
    """Schema para criação de cliente GED."""

    google_drive_folder_id: str | None = Field(None, description="ID da pasta no Google Drive")
    portal_access_enabled: bool = Field(False, description="Habilitar acesso ao portal")
    portal_username: str | None = Field(None, max_length=100, description="Login do portal")
    portal_password: str | None = Field(None, min_length=6, description="Senha do portal (será hasheada)")


class GedClientUpdate(BaseModel):
    """Schema para atualização parcial de cliente GED."""

    name: str | None = Field(None, min_length=2, max_length=255)
    type: GedClientType | None = None
    cnpj: str | None = Field(None, max_length=18)
    address: str | None = None
    contact_name: str | None = Field(None, max_length=255)
    contact_email: str | None = Field(None, max_length=255)
    contact_phone: str | None = Field(None, max_length=20)
    google_drive_folder_id: str | None = None
    portal_access_enabled: bool | None = None
    portal_username: str | None = Field(None, max_length=100)
    portal_password: str | None = Field(None, min_length=6)

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 14:
            raise ValueError("CNPJ deve conter exatamente 14 dígitos")
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:14]}"


class GedClientResponse(BaseModel):
    """Schema de resposta para cliente GED."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    cnpj: str | None = None
    address: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    google_drive_folder_id: str | None = None
    portal_access_enabled: bool = False
    portal_username: str | None = None
    active_kits_count: int = Field(0, description="Quantidade de kits em montagem ou enviados")
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime


class GedClientList(BaseModel):
    """Schema de listagem paginada de clientes GED."""

    items: list[GedClientResponse]
    total: int = Field(..., description="Total de registros")
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0, description="Total de páginas")
