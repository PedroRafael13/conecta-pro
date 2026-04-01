"""Schemas para exportação de folha de pagamento."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.payroll_integration.models import ExportFormat


class ExportScopeSchema(BaseModel):
    """Escopo da exportação."""

    employees: list[str] | None = Field(
        default=["all"],
        description="IDs de funcionários ou 'all'",
    )
    departments: list[str] | None = Field(
        default=["all"],
        description="IDs de departamentos ou 'all'",
    )
    event_types: list[str] | None = None
    event_categories: list[str] | None = None
    date_range: dict | None = None


class FileConfigSchema(BaseModel):
    """Configuração de arquivo."""

    encoding: str = Field(default="utf-8")
    delimiter: str = Field(default=";")
    line_ending: str = Field(default="\r\n")
    include_header: bool = True
    decimal_separator: str = Field(default=",")
    date_format: str = Field(default="dd/mm/yyyy")


class PayrollExportBase(BaseModel):
    """Schema base para exportação."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    export_format: ExportFormat
    export_type: str | None = None
    scope: ExportScopeSchema | None = None
    file_config: FileConfigSchema | None = None


class PayrollExportCreate(PayrollExportBase):
    """Schema para criação de exportação."""

    period_id: UUID | None = None
    integration_id: UUID | None = None

    @field_validator("period_id", "integration_id")
    @classmethod
    def validate_source(cls, v, info):  # pylint: disable=unused-argument
        """Valida que pelo menos um source foi informado."""
        return v


class PayrollExportUpdate(BaseModel):
    """Schema para atualização de exportação."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    scope: ExportScopeSchema | None = None
    file_config: FileConfigSchema | None = None


class PayrollExportResponse(BaseModel):
    """Schema de resposta para exportação."""

    id: UUID
    condominio_id: UUID
    period_id: UUID | None
    integration_id: UUID | None
    export_code: str
    name: str
    description: str | None
    export_format: str
    export_type: str | None
    scope: dict | None
    file_config: dict | None
    file_name: str | None
    file_path: str | None
    file_size: int | None
    file_hash: str | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    processing_time_ms: int | None
    total_records: int
    processed_records: int
    success_records: int
    error_records: int
    warning_records: int
    transmission_id: str | None
    transmission_date: datetime | None
    receipt_number: str | None
    receipt_date: datetime | None
    errors: list[dict] | None
    warnings: list[dict] | None
    download_url: str | None
    download_expires_at: datetime | None
    download_count: int
    retry_count: int
    is_completed: bool
    is_failed: bool
    can_retry: bool
    progress_percentage: float
    success_rate: float
    is_esocial_export: bool
    is_bank_export: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PayrollExportListResponse(BaseModel):
    """Lista paginada de exportações."""

    items: list["PayrollExportResponse"]
    total: int
    page: int
    page_size: int
    pages: int


class ExportProgressResponse(BaseModel):
    """Resposta de progresso da exportação."""

    export_id: UUID
    export_code: str
    status: str
    total_records: int
    processed_records: int
    success_records: int
    error_records: int
    progress_percentage: float
    started_at: datetime | None
    estimated_completion: datetime | None
    current_step: str | None


class ExportDownloadResponse(BaseModel):
    """Resposta para download de exportação."""

    export_id: UUID
    file_name: str
    file_size: int
    content_type: str
    download_url: str
    expires_at: datetime


class ExportErrorDetail(BaseModel):
    """Detalhe de erro de exportação."""

    record: int
    field: str
    code: str
    message: str
    employee_id: str | None
    timestamp: datetime


class ExportValidationResponse(BaseModel):
    """Resposta de validação de exportação."""

    export_id: UUID
    is_valid: bool
    total_records: int
    valid_records: int
    invalid_records: int
    errors: list[ExportErrorDetail]
    warnings: list[ExportErrorDetail]


class BankExportRequest(BaseModel):
    """Request para exportação bancária."""

    period_id: UUID
    bank_code: str = Field(..., min_length=3, max_length=3)
    account_number: str
    account_digit: str
    branch_number: str
    branch_digit: str | None = None
    company_name: str
    company_document: str = Field(..., min_length=14, max_length=14)
    payment_date: date
    export_format: str = Field(
        default="cnab240",
        pattern="^(cnab240|cnab400|febraban)$",
    )


class ESocialExportRequest(BaseModel):
    """Request para exportação eSocial."""

    period_id: UUID
    event_type: str = Field(
        ...,
        pattern="^S-(1200|1210|1260|1270|1280|1298|1299|2200|2299|2300|2399)$",
    )
    employees: list[UUID] | None = None
    test_mode: bool = Field(
        default=False,
        description="Modo de teste (ambiente restrito)",
    )


class ESocialTransmissionResponse(BaseModel):
    """Resposta de transmissão eSocial."""

    export_id: UUID
    protocol: str
    receipt: str | None
    status: str
    transmitted_at: datetime
    events_count: int
    accepted_count: int
    rejected_count: int
    pending_count: int
    rejections: list[dict] | None
