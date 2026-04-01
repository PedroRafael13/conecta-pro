"""Schemas para integração com sistemas externos."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.payroll_integration.models import IntegrationStatus, IntegrationType


class ESocialConfigSchema(BaseModel):
    """Configuração específica do eSocial."""

    ambiente: str = Field(
        default="producao_restrita",
        pattern="^(producao|producao_restrita)$",
    )
    tipo_inscricao: int = Field(default=1, ge=1, le=2)
    nr_inscricao: str = Field(..., min_length=11, max_length=14)
    transmissor_cnpj: str | None = Field(None, min_length=14, max_length=14)
    certificado_tipo: str = Field(default="A1", pattern="^(A1|A3)$")
    certificado_path: str | None = None
    procurador_cnpj: str | None = Field(None, min_length=14, max_length=14)


class CredentialsSchema(BaseModel):
    """Schema para credenciais (entrada)."""

    client_id: str | None = None
    client_secret: str | None = None
    api_key: str | None = None
    username: str | None = None
    password: str | None = None
    certificate_password: str | None = None


class SyncConfigSchema(BaseModel):
    """Configuração de sincronização."""

    auto_sync: bool = False
    sync_interval_hours: int = Field(default=24, ge=1, le=168)
    sync_direction: str = Field(
        default="export",
        pattern="^(import|export|both)$",
    )
    sync_events: list[str] = Field(default_factory=list)
    batch_size: int = Field(default=100, ge=1, le=1000)


class PayrollIntegrationBase(BaseModel):
    """Schema base para integração."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    integration_type: IntegrationType
    endpoint_url: str | None = Field(None, max_length=500)
    api_version: str | None = Field(None, max_length=20)
    auth_type: str | None = Field(
        None,
        pattern="^(oauth2|basic|certificate|apikey)$",
    )
    webhook_url: str | None = Field(None, max_length=500)
    webhook_events: list[str] | None = Field(default_factory=list)


class PayrollIntegrationCreate(PayrollIntegrationBase):
    """Schema para criação de integração."""

    credentials: CredentialsSchema | None = None
    esocial_config: ESocialConfigSchema | None = None
    field_mapping: dict | None = Field(default_factory=dict)
    rubrica_mapping: dict | None = Field(default_factory=dict)
    sync_config: SyncConfigSchema | None = None


class PayrollIntegrationUpdate(BaseModel):
    """Schema para atualização de integração."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    endpoint_url: str | None = Field(None, max_length=500)
    api_version: str | None = Field(None, max_length=20)
    auth_type: str | None = None
    credentials: CredentialsSchema | None = None
    esocial_config: ESocialConfigSchema | None = None
    field_mapping: dict | None = None
    rubrica_mapping: dict | None = None
    sync_config: SyncConfigSchema | None = None
    webhook_url: str | None = Field(None, max_length=500)
    webhook_events: list[str] | None = None
    status: IntegrationStatus | None = None


class PayrollIntegrationResponse(BaseModel):
    """Schema de resposta para integração."""

    id: UUID
    condominio_id: UUID
    name: str
    description: str | None
    integration_type: str
    endpoint_url: str | None
    api_version: str | None
    auth_type: str | None
    esocial_config: dict | None
    field_mapping: dict | None
    rubrica_mapping: dict | None
    sync_config: dict | None
    status: str
    last_sync_at: datetime | None
    last_sync_status: str | None
    last_sync_message: str | None
    last_sync_records: int
    total_syncs: int
    successful_syncs: int
    failed_syncs: int
    success_rate: float
    webhook_url: str | None
    webhook_events: list[str] | None
    is_active: bool
    is_esocial: bool
    needs_certificate: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class IntegrationSyncRequest(BaseModel):
    """Request para sincronização."""

    sync_type: str = Field(
        default="full",
        pattern="^(full|incremental|specific)$",
    )
    period_ids: list[UUID] | None = None
    employee_ids: list[UUID] | None = None
    event_types: list[str] | None = None
    force: bool = False


class IntegrationSyncResponse(BaseModel):
    """Resposta de sincronização."""

    integration_id: UUID
    sync_id: UUID
    status: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    records_processed: int
    records_success: int
    records_failed: int
    errors: list[dict] = Field(default_factory=list)
    warnings: list[dict] = Field(default_factory=list)


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
    details: dict | None = None
    duration_ms: int


class RubricaMappingEntry(BaseModel):
    """Entrada de mapeamento de rubrica."""

    internal_code: str = Field(..., min_length=1, max_length=20)
    external_code: str = Field(..., min_length=1, max_length=20)
    external_name: str | None = None


class BulkRubricaMappingRequest(BaseModel):
    """Request para mapeamento em lote de rubricas."""

    mappings: list[RubricaMappingEntry]

    @field_validator("mappings")
    @classmethod
    def validate_mappings(
        cls,
        v: list[RubricaMappingEntry],
    ) -> list[RubricaMappingEntry]:
        """Valida lista de mapeamentos."""
        if not v:
            raise ValueError("Lista de mapeamentos não pode estar vazia")
        return v
