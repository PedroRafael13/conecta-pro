"""
Schemas Pydantic para Equipment.
"""

from datetime import datetime
from typing import Optional

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
    serial_number: Optional[str] = Field(None, max_length=100, description="Número de série")
    part_number: Optional[str] = Field(None, max_length=100, description="Part number")
    description: Optional[str] = Field(None, description="Descrição detalhada")

    # Fornecedor
    supplier_id: Optional[str] = Field(None, description="ID do fornecedor")
    supplier_name: Optional[str] = Field(None, max_length=200, description="Nome do fornecedor")
    purchase_date: Optional[datetime] = Field(None, description="Data de aquisição")
    purchase_value: Optional[float] = Field(None, ge=0, description="Valor de compra")
    invoice_number: Optional[str] = Field(None, max_length=50, description="Número da NF")

    # Garantia
    warranty_months: Optional[int] = Field(None, ge=0, description="Meses de garantia")
    warranty_start: Optional[datetime] = Field(None, description="Início da garantia")
    warranty_end: Optional[datetime] = Field(None, description="Fim da garantia")

    # Configuração técnica
    ip_address: Optional[str] = Field(None, max_length=50, description="Endereço IP")
    mac_address: Optional[str] = Field(None, max_length=50, description="MAC Address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Porta")
    technical_config: Optional[dict] = Field(None, description="Configurações técnicas")

    # Manutenção
    maintenance_interval_days: Optional[int] = Field(
        None,
        ge=1,
        description="Intervalo de manutenção em dias",
    )

    # Depreciação
    depreciation_rate: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Taxa de depreciação anual (%)",
    )
    useful_life_months: Optional[int] = Field(
        None,
        ge=1,
        description="Vida útil em meses",
    )

    # Metadados
    images: Optional[list] = Field(None, description="URLs das imagens")
    tags: Optional[list] = Field(None, description="Tags")
    notes: Optional[str] = Field(None, description="Observações")
    metadata_extra: Optional[dict] = Field(None, description="Metadados adicionais")

    model_config = ConfigDict(use_enum_values=True)


class EquipmentUpdate(BaseModel):
    """Schema para atualizar equipamento."""

    status: Optional[EquipmentStatus] = Field(None, description="Status")
    firmware_version: Optional[str] = Field(None, max_length=50, description="Versão firmware")
    description: Optional[str] = Field(None, description="Descrição")

    # Localização
    location_type: Optional[str] = Field(None, description="Tipo de localização")
    location_id: Optional[str] = Field(None, description="ID do local")
    location_name: Optional[str] = Field(None, max_length=200, description="Nome do local")
    location_details: Optional[str] = Field(None, description="Detalhes do local")

    # Cliente
    client_id: Optional[str] = Field(None, description="ID do cliente")
    client_name: Optional[str] = Field(None, max_length=200, description="Nome do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    post_id: Optional[str] = Field(None, description="ID do posto")

    # Configuração
    ip_address: Optional[str] = Field(None, max_length=50, description="Endereço IP")
    mac_address: Optional[str] = Field(None, max_length=50, description="MAC Address")
    port: Optional[int] = Field(None, ge=1, le=65535, description="Porta")
    technical_config: Optional[dict] = Field(None, description="Configurações técnicas")

    # Manutenção
    next_maintenance_at: Optional[datetime] = Field(
        None,
        description="Próxima manutenção",
    )

    # Metadados
    images: Optional[list] = Field(None, description="URLs das imagens")
    tags: Optional[list] = Field(None, description="Tags")
    notes: Optional[str] = Field(None, description="Observações")
    metadata_extra: Optional[dict] = Field(None, description="Metadados adicionais")

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
    serial_number: Optional[str]
    part_number: Optional[str]
    firmware_version: Optional[str]
    description: Optional[str]

    # Aquisição
    supplier_id: Optional[str]
    supplier_name: Optional[str]
    purchase_date: Optional[datetime]
    purchase_value: Optional[float]
    invoice_number: Optional[str]

    # Garantia
    warranty_start: Optional[datetime]
    warranty_end: Optional[datetime]
    warranty_months: Optional[int]
    has_extended_warranty: bool
    is_in_warranty: bool
    days_until_warranty_end: Optional[int]

    # Localização
    location_type: str
    location_id: Optional[str]
    location_name: Optional[str]
    location_details: Optional[str]

    # Cliente
    client_id: Optional[str]
    client_name: Optional[str]
    contract_id: Optional[str]
    post_id: Optional[str]

    # Instalação
    installation_id: Optional[str]
    installed_at: Optional[datetime]
    installed_location: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]

    # Configuração
    ip_address: Optional[str]
    mac_address: Optional[str]
    port: Optional[int]
    technical_config: Optional[dict]

    # Status operacional
    is_online: bool
    last_online_at: Optional[datetime]
    last_offline_at: Optional[datetime]
    uptime_percent: Optional[float]

    # Manutenção
    last_maintenance_at: Optional[datetime]
    next_maintenance_at: Optional[datetime]
    needs_maintenance: bool
    days_until_maintenance: Optional[int]
    total_maintenances: int

    # Depreciação
    depreciation_rate: Optional[float]
    current_value: Optional[float]
    useful_life_months: Optional[int]

    # Metadados
    images: Optional[list]
    qr_code_url: Optional[str]
    tags: Optional[list]
    notes: Optional[str]

    # Flags
    is_installed: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentFilter(BaseModel):
    """Schema para filtrar equipamentos."""

    search: Optional[str] = Field(None, description="Busca textual")
    equipment_type: Optional[EquipmentType] = Field(None, description="Tipo")
    category: Optional[EquipmentCategory] = Field(None, description="Categoria")
    status: Optional[EquipmentStatus] = Field(None, description="Status")
    brand: Optional[str] = Field(None, description="Marca")
    client_id: Optional[str] = Field(None, description="Cliente")
    contract_id: Optional[str] = Field(None, description="Contrato")
    location_type: Optional[str] = Field(None, description="Tipo de localização")
    is_online: Optional[bool] = Field(None, description="Online/Offline")
    is_in_warranty: Optional[bool] = Field(None, description="Em garantia")
    needs_maintenance: Optional[bool] = Field(None, description="Precisa manutenção")

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
