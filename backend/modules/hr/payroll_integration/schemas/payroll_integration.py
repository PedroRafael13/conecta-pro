"""Schemas para integração com sistemas externos."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.payroll_integration.models import IntegrationType, IntegrationStatus


class ESocialConfigSchema(BaseModel):
    """Configuração específica do eSocial."""

    ambiente: str = Field(
        default="producao_restrita",
        pattern="^(producao|producao_restrita)$",
    )
    tipo_inscricao: int = Field(default=1, ge=1, le=2)
    nr_inscricao: str = Field(..., min_length=11, max_length=14)
    transmissor_cnpj: Optional[str] = Field(None, min_length=14, max_length=14)
    certificado_tipo: str = Field(default="A1", pattern="^(A1|A3)$")
    certificado_path: Optional[str] = None
    procurador_cnpj: Optional[str] = Field(None, min_length=14, max_length=14)


class CredentialsSchema(BaseModel):
    """Schema para credenciais (entrada)."""

    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    certificate_password: Optional[str] = None


class SyncConfigSchema(BaseModel):
    """Configuração de sincronização."""

    auto_sync: bool = False
    sync_interval_hours: int = Field(default=24, ge=1, le=168)
    sync_direction: str = Field(
        default="export",
        pattern="^(import|export|both)$",
    )
    sync_events: List[str] = Field(default_factory=list)
    batch_size: int = Field(default=100, ge=1, le=1000)


class PayrollIntegrationBase(BaseModel):
    """Schema base para integração."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    integration_type: IntegrationType
    endpoint_url: Optional[str] = Field(None, max_length=500)
    api_version: Optional[str] = Field(None, max_length=20)
    auth_type: Optional[str] = Field(
        None,
        pattern="^(oauth2|basic|certificate|apikey)$",
    )
    webhook_url: Optional[str] = Field(None, max_length=500)
    webhook_events: Optional[List[str]] = Field(default_factory=list)


class PayrollIntegrationCreate(PayrollIntegrationBase):
    """Schema para criação de integração."""

    credentials: Optional[CredentialsSchema] = None
    esocial_config: Optional[ESocialConfigSchema] = None
    field_mapping: Optional[dict] = Field(default_factory=dict)
    rubrica_mapping: Optional[dict] = Field(default_factory=dict)
    sync_config: Optional[SyncConfigSchema] = None


class PayrollIntegrationUpdate(BaseModel):
    """Schema para atualização de integração."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    endpoint_url: Optional[str] = Field(None, max_length=500)
    api_version: Optional[str] = Field(None, max_length=20)
    auth_type: Optional[str] = None
    credentials: Optional[CredentialsSchema] = None
    esocial_config: Optional[ESocialConfigSchema] = None
    field_mapping: Optional[dict] = None
    rubrica_mapping: Optional[dict] = None
    sync_config: Optional[SyncConfigSchema] = None
    webhook_url: Optional[str] = Field(None, max_length=500)
    webhook_events: Optional[List[str]] = None
    status: Optional[IntegrationStatus] = None


class PayrollIntegrationResponse(BaseModel):
    """Schema de resposta para integração."""

    id: UUID
    condominio_id: UUID
    name: str
    description: Optional[str]
    integration_type: str
    endpoint_url: Optional[str]
    api_version: Optional[str]
    auth_type: Optional[str]
    esocial_config: Optional[dict]
    field_mapping: Optional[dict]
    rubrica_mapping: Optional[dict]
    sync_config: Optional[dict]
    status: str
    last_sync_at: Optional[datetime]
    last_sync_status: Optional[str]
    last_sync_message: Optional[str]
    last_sync_records: int
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    success_rate: float
    webhook_url: Optional[str]
    webhook_events: Optional[List[str]]
    is_active: bool
    is_esocial: bool
    needs_certificate: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class IntegrationSyncRequest(BaseModel):
    """Request para sincronização."""

    sync_type: str = Field(
        default="full",
        pattern="^(full|incremental|specific)$",
    )
    period_ids: Optional[List[UUID]] = None
    employee_ids: Optional[List[UUID]] = None
    event_types: Optional[List[str]] = None
    force: bool = False


class IntegrationSyncResponse(BaseModel):
    """Resposta de sincronização."""

    integration_id: UUID
    sync_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    records_processed: int
    records_success: int
    records_failed: int
    errors: List[dict] = Field(default_factory=list)
    warnings: List[dict] = Field(default_factory=list)


class IntegrationTestRequest(BaseModel):
    """Request para teste de integração."""

    test_type: str = Field(
        default="connection",
        pattern="^(connection|authentication|certificate|mapping)$",
    )


class IntegrationTestResponse(BaseModel):
    """Resposta de teste de integração."""

    success: bool
    test_type: str
    message: str
    details: Optional[dict] = None
    duration_ms: int


class RubricaMappingEntry(BaseModel):
    """Entrada de mapeamento de rubrica."""

    internal_code: str = Field(..., min_length=1, max_length=20)
    external_code: str = Field(..., min_length=1, max_length=20)
    external_name: Optional[str] = None


class BulkRubricaMappingRequest(BaseModel):
    """Request para mapeamento em lote de rubricas."""

    mappings: List[RubricaMappingEntry]

    @field_validator("mappings")
    @classmethod
    def validate_mappings(
        cls,
        v: List[RubricaMappingEntry],
    ) -> List[RubricaMappingEntry]:
        """Valida lista de mapeamentos."""
        if not v:
            raise ValueError("Lista de mapeamentos não pode estar vazia")
        return v
