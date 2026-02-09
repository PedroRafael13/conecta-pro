"""
Schemas Pydantic para EquipmentComodato.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.equipment_management.models.comodato import ComodatoStatus


class ComodatoCreate(BaseModel):
    """Schema para criar comodato."""

    equipment_id: str = Field(..., description="ID do equipamento")
    equipment_code: str = Field(..., description="Código do equipamento")
    equipment_name: str = Field(..., max_length=200, description="Nome do equipamento")
    equipment_type: str = Field(..., max_length=50, description="Tipo do equipamento")
    serial_number: str | None = Field(None, max_length=100, description="Número de série")
    equipment_value: float = Field(..., gt=0, description="Valor do equipamento")
    equipment_condition: str = Field(default="novo", description="Condição")

    client_id: str = Field(..., description="ID do cliente")
    client_name: str = Field(..., max_length=200, description="Nome do cliente")
    client_document: str | None = Field(None, max_length=20, description="CNPJ/CPF")
    contract_id: str | None = Field(None, description="ID do contrato principal")

    responsible_name: str | None = Field(None, max_length=200, description="Responsável")
    responsible_document: str | None = Field(None, max_length=20, description="Doc responsável")
    responsible_phone: str | None = Field(None, max_length=20, description="Telefone")
    responsible_email: str | None = Field(None, max_length=200, description="E-mail")

    start_date: datetime = Field(..., description="Data início")
    end_date: datetime | None = Field(None, description="Data fim")
    duration_months: int | None = Field(None, ge=1, description="Duração em meses")
    auto_renewal: bool = Field(default=True, description="Renovação automática")
    renewal_period_months: int = Field(default=12, ge=1, description="Período renovação")
    notice_period_days: int = Field(default=30, ge=1, description="Aviso prévio (dias)")

    usage_location: str = Field(..., min_length=1, description="Local de uso")
    usage_address: str | None = Field(None, description="Endereço")
    gps_latitude: float | None = Field(None, description="Latitude")
    gps_longitude: float | None = Field(None, description="Longitude")

    terms: str | None = Field(None, description="Termos e condições")
    special_conditions: str | None = Field(None, description="Condições especiais")
    usage_restrictions: list | None = Field(None, description="Restrições de uso")
    maintenance_responsibility: str = Field(
        default="comodante",
        description="Responsável manutenção",
    )

    damage_penalty_percent: float | None = Field(None, ge=0, le=100, description="% multa dano")
    loss_penalty_percent: float = Field(default=100.0, ge=0, le=100, description="% multa perda")
    early_return_penalty: float | None = Field(None, ge=0, description="Multa devolução antecipada")

    notes: str | None = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class ComodatoUpdate(BaseModel):
    """Schema para atualizar comodato."""

    status: ComodatoStatus | None = Field(None, description="Status")

    responsible_name: str | None = Field(None, max_length=200, description="Responsável")
    responsible_document: str | None = Field(None, max_length=20, description="Doc responsável")
    responsible_phone: str | None = Field(None, max_length=20, description="Telefone")
    responsible_email: str | None = Field(None, max_length=200, description="E-mail")

    end_date: datetime | None = Field(None, description="Data fim")
    auto_renewal: bool | None = Field(None, description="Renovação automática")

    usage_location: str | None = Field(None, description="Local de uso")
    usage_address: str | None = Field(None, description="Endereço")

    terms: str | None = Field(None, description="Termos e condições")
    special_conditions: str | None = Field(None, description="Condições especiais")

    notes: str | None = Field(None, description="Observações")

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
    serial_number: str | None
    equipment_value: float
    equipment_condition: str

    client_id: str
    client_name: str
    client_document: str | None
    contract_id: str | None

    responsible_name: str | None
    responsible_document: str | None
    responsible_phone: str | None
    responsible_email: str | None

    start_date: datetime
    end_date: datetime | None
    duration_months: int | None
    auto_renewal: bool
    renewal_period_months: int
    notice_period_days: int

    usage_location: str
    usage_address: str | None
    gps_latitude: float | None
    gps_longitude: float | None

    terms: str | None
    special_conditions: str | None
    usage_restrictions: list | None
    maintenance_responsibility: str

    damage_penalty_percent: float | None
    loss_penalty_percent: float | None
    early_return_penalty: float | None

    signed_at: datetime | None
    signed_by_client: str | None
    signed_by_company: str | None

    contract_pdf_url: str | None
    delivery_term_url: str | None
    return_term_url: str | None
    photos_delivery: list | None
    photos_return: list | None

    delivered_at: datetime | None
    delivered_by: str | None
    received_by: str | None
    delivery_notes: str | None

    return_requested_at: datetime | None
    return_scheduled_at: datetime | None
    returned_at: datetime | None
    returned_by: str | None
    return_condition: str | None
    return_notes: str | None

    has_damages: bool
    damage_description: str | None
    damage_cost: float | None
    penalty_applied: float | None
    is_lost: bool

    transferred_to_client_id: str | None
    transferred_at: datetime | None
    transfer_reason: str | None
    new_comodato_id: str | None

    terminated_at: datetime | None
    termination_reason: str | None

    history: list | None
    notes: str | None
    tags: list | None

    is_signed: bool
    is_active_contract: bool
    is_expired: bool
    days_until_expiry: int | None
    is_delivered: bool
    is_returned: bool

    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComodatoFilter(BaseModel):
    """Schema para filtrar comodatos."""

    search: str | None = Field(None, description="Busca textual")
    status: ComodatoStatus | None = Field(None, description="Status")
    client_id: str | None = Field(None, description="Cliente")
    equipment_id: str | None = Field(None, description="Equipamento")
    is_signed: bool | None = Field(None, description="Assinado")
    is_delivered: bool | None = Field(None, description="Entregue")
    is_expired: bool | None = Field(None, description="Expirado")
    has_damages: bool | None = Field(None, description="Com danos")
    date_from: datetime | None = Field(None, description="Data inicial")
    date_to: datetime | None = Field(None, description="Data final")

    model_config = ConfigDict(use_enum_values=True)


class ComodatoListResponse(BaseModel):
    """Schema para lista paginada de comodatos."""

    items: list[ComodatoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
