"""Schemas para exportação de folha de pagamento."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from modules.hr.payroll_integration.models import ExportFormat


class ExportScopeSchema(BaseModel):
    """Escopo da exportação."""

    employees: Optional[List[str]] = Field(
        default=["all"],
        description="IDs de funcionários ou 'all'",
    )
    departments: Optional[List[str]] = Field(
        default=["all"],
        description="IDs de departamentos ou 'all'",
    )
    event_types: Optional[List[str]] = None
    event_categories: Optional[List[str]] = None
    date_range: Optional[dict] = None


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
    description: Optional[str] = None
    export_format: ExportFormat
    export_type: Optional[str] = None
    scope: Optional[ExportScopeSchema] = None
    file_config: Optional[FileConfigSchema] = None


class PayrollExportCreate(PayrollExportBase):
    """Schema para criação de exportação."""

    period_id: Optional[UUID] = None
    integration_id: Optional[UUID] = None

    @field_validator("period_id", "integration_id")
    @classmethod
    def validate_source(cls, v, info):  # pylint: disable=unused-argument
        """Valida que pelo menos um source foi informado."""
        return v


class PayrollExportUpdate(BaseModel):
    """Schema para atualização de exportação."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scope: Optional[ExportScopeSchema] = None
    file_config: Optional[FileConfigSchema] = None


class PayrollExportResponse(BaseModel):
    """Schema de resposta para exportação."""

    id: UUID
    condominio_id: UUID
    period_id: Optional[UUID]
    integration_id: Optional[UUID]
    export_code: str
    name: str
    description: Optional[str]
    export_format: str
    export_type: Optional[str]
    scope: Optional[dict]
    file_config: Optional[dict]
    file_name: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    file_hash: Optional[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time_ms: Optional[int]
    total_records: int
    processed_records: int
    success_records: int
    error_records: int
    warning_records: int
    transmission_id: Optional[str]
    transmission_date: Optional[datetime]
    receipt_number: Optional[str]
    receipt_date: Optional[datetime]
    errors: Optional[List[dict]]
    warnings: Optional[List[dict]]
    download_url: Optional[str]
    download_expires_at: Optional[datetime]
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
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PayrollExportListResponse(BaseModel):
    """Lista paginada de exportações."""

    items: List["PayrollExportResponse"]
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
    started_at: Optional[datetime]
    estimated_completion: Optional[datetime]
    current_step: Optional[str]


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
    employee_id: Optional[str]
    timestamp: datetime


class ExportValidationResponse(BaseModel):
    """Resposta de validação de exportação."""

    export_id: UUID
    is_valid: bool
    total_records: int
    valid_records: int
    invalid_records: int
    errors: List[ExportErrorDetail]
    warnings: List[ExportErrorDetail]


class BankExportRequest(BaseModel):
    """Request para exportação bancária."""

    period_id: UUID
    bank_code: str = Field(..., min_length=3, max_length=3)
    account_number: str
    account_digit: str
    branch_number: str
    branch_digit: Optional[str] = None
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
    employees: Optional[List[UUID]] = None
    test_mode: bool = Field(
        default=False,
        description="Modo de teste (ambiente restrito)",
    )


class ESocialTransmissionResponse(BaseModel):
    """Resposta de transmissão eSocial."""

    export_id: UUID
    protocol: str
    receipt: Optional[str]
    status: str
    transmitted_at: datetime
    events_count: int
    accepted_count: int
    rejected_count: int
    pending_count: int
    rejections: Optional[List[dict]]
