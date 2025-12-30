"""
Schemas Pydantic para EquipmentComodato.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from modules.equipment_management.models.comodato import ComodatoStatus


class ComodatoCreate(BaseModel):
    """Schema para criar comodato."""

    equipment_id: str = Field(..., description="ID do equipamento")
    equipment_code: str = Field(..., description="Código do equipamento")
    equipment_name: str = Field(..., max_length=200, description="Nome do equipamento")
    equipment_type: str = Field(..., max_length=50, description="Tipo do equipamento")
    serial_number: Optional[str] = Field(None, max_length=100, description="Número de série")
    equipment_value: float = Field(..., gt=0, description="Valor do equipamento")
    equipment_condition: str = Field(default="novo", description="Condição")

    client_id: str = Field(..., description="ID do cliente")
    client_name: str = Field(..., max_length=200, description="Nome do cliente")
    client_document: Optional[str] = Field(None, max_length=20, description="CNPJ/CPF")
    contract_id: Optional[str] = Field(None, description="ID do contrato principal")

    responsible_name: Optional[str] = Field(None, max_length=200, description="Responsável")
    responsible_document: Optional[str] = Field(None, max_length=20, description="Doc responsável")
    responsible_phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    responsible_email: Optional[str] = Field(None, max_length=200, description="E-mail")

    start_date: datetime = Field(..., description="Data início")
    end_date: Optional[datetime] = Field(None, description="Data fim")
    duration_months: Optional[int] = Field(None, ge=1, description="Duração em meses")
    auto_renewal: bool = Field(default=True, description="Renovação automática")
    renewal_period_months: int = Field(default=12, ge=1, description="Período renovação")
    notice_period_days: int = Field(default=30, ge=1, description="Aviso prévio (dias)")

    usage_location: str = Field(..., min_length=1, description="Local de uso")
    usage_address: Optional[str] = Field(None, description="Endereço")
    gps_latitude: Optional[float] = Field(None, description="Latitude")
    gps_longitude: Optional[float] = Field(None, description="Longitude")

    terms: Optional[str] = Field(None, description="Termos e condições")
    special_conditions: Optional[str] = Field(None, description="Condições especiais")
    usage_restrictions: Optional[list] = Field(None, description="Restrições de uso")
    maintenance_responsibility: str = Field(
        default="comodante",
        description="Responsável manutenção",
    )

    damage_penalty_percent: Optional[float] = Field(None, ge=0, le=100, description="% multa dano")
    loss_penalty_percent: float = Field(default=100.0, ge=0, le=100, description="% multa perda")
    early_return_penalty: Optional[float] = Field(None, ge=0, description="Multa devolução antecipada")

    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class ComodatoUpdate(BaseModel):
    """Schema para atualizar comodato."""

    status: Optional[ComodatoStatus] = Field(None, description="Status")

    responsible_name: Optional[str] = Field(None, max_length=200, description="Responsável")
    responsible_document: Optional[str] = Field(None, max_length=20, description="Doc responsável")
    responsible_phone: Optional[str] = Field(None, max_length=20, description="Telefone")
    responsible_email: Optional[str] = Field(None, max_length=200, description="E-mail")

    end_date: Optional[datetime] = Field(None, description="Data fim")
    auto_renewal: Optional[bool] = Field(None, description="Renovação automática")

    usage_location: Optional[str] = Field(None, description="Local de uso")
    usage_address: Optional[str] = Field(None, description="Endereço")

    terms: Optional[str] = Field(None, description="Termos e condições")
    special_conditions: Optional[str] = Field(None, description="Condições especiais")

    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class ComodatoResponse(BaseModel):
    """Schema de resposta para comodato."""

    id: str
    comodato_code: str
    status: str

    equipment_id: str
    equipment_code: str
    equipment_name: str
    equipment_type: str
    serial_number: Optional[str]
    equipment_value: float
    equipment_condition: str

    client_id: str
    client_name: str
    client_document: Optional[str]
    contract_id: Optional[str]

    responsible_name: Optional[str]
    responsible_document: Optional[str]
    responsible_phone: Optional[str]
    responsible_email: Optional[str]

    start_date: datetime
    end_date: Optional[datetime]
    duration_months: Optional[int]
    auto_renewal: bool
    renewal_period_months: int
    notice_period_days: int

    usage_location: str
    usage_address: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]

    terms: Optional[str]
    special_conditions: Optional[str]
    usage_restrictions: Optional[list]
    maintenance_responsibility: str

    damage_penalty_percent: Optional[float]
    loss_penalty_percent: Optional[float]
    early_return_penalty: Optional[float]

    signed_at: Optional[datetime]
    signed_by_client: Optional[str]
    signed_by_company: Optional[str]

    contract_pdf_url: Optional[str]
    delivery_term_url: Optional[str]
    return_term_url: Optional[str]
    photos_delivery: Optional[list]
    photos_return: Optional[list]

    delivered_at: Optional[datetime]
    delivered_by: Optional[str]
    received_by: Optional[str]
    delivery_notes: Optional[str]

    return_requested_at: Optional[datetime]
    return_scheduled_at: Optional[datetime]
    returned_at: Optional[datetime]
    returned_by: Optional[str]
    return_condition: Optional[str]
    return_notes: Optional[str]

    has_damages: bool
    damage_description: Optional[str]
    damage_cost: Optional[float]
    penalty_applied: Optional[float]
    is_lost: bool

    transferred_to_client_id: Optional[str]
    transferred_at: Optional[datetime]
    transfer_reason: Optional[str]
    new_comodato_id: Optional[str]

    terminated_at: Optional[datetime]
    termination_reason: Optional[str]

    history: Optional[list]
    notes: Optional[str]
    tags: Optional[list]

    is_signed: bool
    is_active_contract: bool
    is_expired: bool
    days_until_expiry: Optional[int]
    is_delivered: bool
    is_returned: bool

    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComodatoFilter(BaseModel):
    """Schema para filtrar comodatos."""

    search: Optional[str] = Field(None, description="Busca textual")
    status: Optional[ComodatoStatus] = Field(None, description="Status")
    client_id: Optional[str] = Field(None, description="Cliente")
    equipment_id: Optional[str] = Field(None, description="Equipamento")
    is_signed: Optional[bool] = Field(None, description="Assinado")
    is_delivered: Optional[bool] = Field(None, description="Entregue")
    is_expired: Optional[bool] = Field(None, description="Expirado")
    has_damages: Optional[bool] = Field(None, description="Com danos")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")

    model_config = ConfigDict(use_enum_values=True)


class ComodatoListResponse(BaseModel):
    """Schema para lista paginada de comodatos."""

    items: list[ComodatoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
