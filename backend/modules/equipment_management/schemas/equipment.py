"""
Schemas Pydantic para Equipment.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.equipment_management.models.equipment import (
    EquipmentCategory,
    EquipmentStatus,
    EquipmentType,
)


class EquipmentCreate(BaseModel):
    """Schema para criar equipamento."""

    equipment_type: EquipmentType = Field(..., description="Tipo do equipamento")
    category: EquipmentCategory = Field(..., description="Categoria")
    brand: str = Field(..., min_length=1, max_length=100, description="Marca")
    model: str = Field(..., min_length=1, max_length=100, description="Modelo")
    name: str = Field(..., min_length=1, max_length=200, description="Nome/descrição")
    serial_number: str | None = Field(None, max_length=100, description="Número de série")
    part_number: str | None = Field(None, max_length=100, description="Part number")
    description: str | None = Field(None, description="Descrição detalhada")

    # Fornecedor
    supplier_id: str | None = Field(None, description="ID do fornecedor")
    supplier_name: str | None = Field(None, max_length=200, description="Nome do fornecedor")
    purchase_date: datetime | None = Field(None, description="Data de aquisição")
    purchase_value: float | None = Field(None, ge=0, description="Valor de compra")
    invoice_number: str | None = Field(None, max_length=50, description="Número da NF")

    # Garantia
    warranty_months: int | None = Field(None, ge=0, description="Meses de garantia")
    warranty_start: datetime | None = Field(None, description="Início da garantia")
    warranty_end: datetime | None = Field(None, description="Fim da garantia")

    # Configuração técnica
    ip_address: str | None = Field(None, max_length=50, description="Endereço IP")
    mac_address: str | None = Field(None, max_length=50, description="MAC Address")
    port: int | None = Field(None, ge=1, le=65535, description="Porta")
    technical_config: dict | None = Field(None, description="Configurações técnicas")

    # Manutenção
    maintenance_interval_days: int | None = Field(
        None,
        ge=1,
        description="Intervalo de manutenção em dias",
    )

    # Depreciação
    depreciation_rate: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Taxa de depreciação anual (%)",
    )
    useful_life_months: int | None = Field(
        None,
        ge=1,
        description="Vida útil em meses",
    )

    # Metadados
    images: list | None = Field(None, description="URLs das imagens")
    tags: list | None = Field(None, description="Tags")
    notes: str | None = Field(None, description="Observações")
    metadata_extra: dict | None = Field(None, description="Metadados adicionais")

    model_config = ConfigDict(use_enum_values=True)


class EquipmentUpdate(BaseModel):
    """Schema para atualizar equipamento."""

    status: EquipmentStatus | None = Field(None, description="Status")
    firmware_version: str | None = Field(None, max_length=50, description="Versão firmware")
    description: str | None = Field(None, description="Descrição")

    # Localização
    location_type: str | None = Field(None, description="Tipo de localização")
    location_id: str | None = Field(None, description="ID do local")
    location_name: str | None = Field(None, max_length=200, description="Nome do local")
    location_details: str | None = Field(None, description="Detalhes do local")

    # Cliente
    client_id: str | None = Field(None, description="ID do cliente")
    client_name: str | None = Field(None, max_length=200, description="Nome do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    post_id: str | None = Field(None, description="ID do posto")

    # Configuração
    ip_address: str | None = Field(None, max_length=50, description="Endereço IP")
    mac_address: str | None = Field(None, max_length=50, description="MAC Address")
    port: int | None = Field(None, ge=1, le=65535, description="Porta")
    technical_config: dict | None = Field(None, description="Configurações técnicas")

    # Manutenção
    next_maintenance_at: datetime | None = Field(
        None,
        description="Próxima manutenção",
    )

    # Metadados
    images: list | None = Field(None, description="URLs das imagens")
    tags: list | None = Field(None, description="Tags")
    notes: str | None = Field(None, description="Observações")
    metadata_extra: dict | None = Field(None, description="Metadados adicionais")

    model_config = ConfigDict(use_enum_values=True)


class EquipmentResponse(BaseModel):
    """Schema de resposta para equipamento."""

    id: str
    equipment_code: str
    equipment_type: str
    category: str
    status: str
    brand: str
    model: str
    name: str
    serial_number: str | None
    part_number: str | None
    firmware_version: str | None
    description: str | None

    # Aquisição
    supplier_id: str | None
    supplier_name: str | None
    purchase_date: datetime | None
    purchase_value: float | None
    invoice_number: str | None

    # Garantia
    warranty_start: datetime | None
    warranty_end: datetime | None
    warranty_months: int | None
    has_extended_warranty: bool
    is_in_warranty: bool
    days_until_warranty_end: int | None

    # Localização
    location_type: str
    location_id: str | None
    location_name: str | None
    location_details: str | None

    # Cliente
    client_id: str | None
    client_name: str | None
    contract_id: str | None
    post_id: str | None

    # Instalação
    installation_id: str | None
    installed_at: datetime | None
    installed_location: str | None
    gps_latitude: float | None
    gps_longitude: float | None

    # Configuração
    ip_address: str | None
    mac_address: str | None
    port: int | None
    technical_config: dict | None

    # Status operacional
    is_online: bool
    last_online_at: datetime | None
    last_offline_at: datetime | None
    uptime_percent: float | None

    # Manutenção
    last_maintenance_at: datetime | None
    next_maintenance_at: datetime | None
    needs_maintenance: bool
    days_until_maintenance: int | None
    total_maintenances: int

    # Depreciação
    depreciation_rate: float | None
    current_value: float | None
    useful_life_months: int | None

    # Metadados
    images: list | None
    qr_code_url: str | None
    tags: list | None
    notes: str | None

    # Flags
    is_installed: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentFilter(BaseModel):
    """Schema para filtrar equipamentos."""

    search: str | None = Field(None, description="Busca textual")
    equipment_type: EquipmentType | None = Field(None, description="Tipo")
    category: EquipmentCategory | None = Field(None, description="Categoria")
    status: EquipmentStatus | None = Field(None, description="Status")
    brand: str | None = Field(None, description="Marca")
    client_id: str | None = Field(None, description="Cliente")
    contract_id: str | None = Field(None, description="Contrato")
    location_type: str | None = Field(None, description="Tipo de localização")
    is_online: bool | None = Field(None, description="Online/Offline")
    is_in_warranty: bool | None = Field(None, description="Em garantia")
    needs_maintenance: bool | None = Field(None, description="Precisa manutenção")

    model_config = ConfigDict(use_enum_values=True)


class EquipmentListResponse(BaseModel):
    """Schema para lista paginada de equipamentos."""

    items: list[EquipmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EquipmentStats(BaseModel):
    """Estatísticas de equipamentos."""

    total: int = Field(default=0, description="Total de equipamentos")
    by_status: dict[str, int] = Field(default_factory=dict, description="Por status")
    by_type: dict[str, int] = Field(default_factory=dict, description="Por tipo")
    by_category: dict[str, int] = Field(default_factory=dict, description="Por categoria")
    in_stock: int = Field(default=0, description="Em estoque")
    installed: int = Field(default=0, description="Instalados")
    in_maintenance: int = Field(default=0, description="Em manutenção")
    defective: int = Field(default=0, description="Defeituosos")
    online: int = Field(default=0, description="Online")
    offline: int = Field(default=0, description="Offline")
    in_warranty: int = Field(default=0, description="Em garantia")
    needs_maintenance: int = Field(default=0, description="Precisam manutenção")
    total_value: float = Field(default=0.0, description="Valor total do parque")
    avg_age_months: float = Field(default=0.0, description="Idade média em meses")
