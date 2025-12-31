"""Schemas Pydantic para AFDRecord."""

from datetime import datetime, date, time
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class AFDRecordBase(BaseModel):
    """Schema base para AFDRecord."""

    nsr: int = Field(
        ...,
        ge=1,
        description="Número Sequencial de Registro",
    )
    record_type: str = Field(
        ...,
        min_length=1,
        max_length=1,
        pattern="^[1-49]$",
        description="Tipo de registro AFD (1-4, 9)",
    )
    afd_line: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Linha AFD formatada",
    )


class AFDRecordCreate(AFDRecordBase):
    """Schema para criar AFDRecord."""

    device_id: UUID
    condominio_id: UUID
    record_date: Optional[date] = None
    record_time: Optional[time] = None
    pis_number: Optional[str] = None
    cnpj: Optional[str] = None
    cei: Optional[str] = None
    company_name: Optional[str] = None
    rep_serial: Optional[str] = None
    rep_manufacturer: Optional[str] = None
    rep_model: Optional[str] = None
    generation_date: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    original_date: Optional[date] = None
    original_time: Optional[time] = None
    adjusted_date: Optional[date] = None
    adjusted_time: Optional[time] = None
    event_id: Optional[UUID] = None
    line_hash: str


class AFDRecordResponse(AFDRecordBase):
    """Schema de resposta para AFDRecord."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    condominio_id: UUID
    record_date: Optional[date] = None
    record_time: Optional[time] = None
    pis_number: Optional[str] = None
    event_id: Optional[UUID] = None
    line_hash: str
    is_exported: bool
    exported_at: Optional[datetime] = None
    is_valid: bool
    validation_error: Optional[str] = None
    created_at: datetime


class AFDRecordList(BaseModel):
    """Schema para lista de registros AFD."""

    items: List[AFDRecordResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AFDRecordFilter(BaseModel):
    """Filtros para busca de registros AFD."""

    device_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    record_type: Optional[str] = None
    pis_number: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_exported: Optional[bool] = None
    is_valid: Optional[bool] = None
    nsr_from: Optional[int] = None
    nsr_to: Optional[int] = None


class AFDExportRequest(BaseModel):
    """Schema para exportar AFD."""

    device_id: UUID
    start_date: date = Field(
        ...,
        description="Data inicial do período",
    )
    end_date: date = Field(
        ...,
        description="Data final do período",
    )
    include_header: bool = Field(
        default=True,
        description="Incluir registro tipo 1 (cabeçalho)",
    )
    include_company: bool = Field(
        default=True,
        description="Incluir registro tipo 2 (empregador)",
    )
    include_trailer: bool = Field(
        default=True,
        description="Incluir registro tipo 9 (trailer)",
    )
    format: str = Field(
        default="txt",
        pattern="^(txt|csv)$",
        description="Formato de exportação",
    )


class AFDExportResponse(BaseModel):
    """Resposta da exportação AFD."""

    success: bool
    file_path: Optional[str] = None
    file_name: str
    total_records: int
    period_start: date
    period_end: date
    generated_at: datetime
    file_size_bytes: int
    checksum: str
    download_url: Optional[str] = None


class AFDValidationResult(BaseModel):
    """Resultado da validação de arquivo AFD."""

    is_valid: bool
    total_lines: int
    valid_lines: int
    invalid_lines: int
    errors: List[dict]
    warnings: List[dict]
    header_info: Optional[dict] = None
    company_info: Optional[dict] = None
    records_count: int
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


class AFDImportRequest(BaseModel):
    """Schema para importar arquivo AFD."""

    device_id: UUID
    file_content: str = Field(
        ...,
        description="Conteúdo do arquivo AFD",
    )
    validate_only: bool = Field(
        default=False,
        description="Apenas validar, não importar",
    )
    skip_duplicates: bool = Field(
        default=True,
        description="Ignorar registros já existentes",
    )


class AFDImportResponse(BaseModel):
    """Resposta da importação AFD."""

    success: bool
    total_lines: int
    imported_records: int
    skipped_records: int
    error_records: int
    errors: Optional[List[dict]] = None
    validation_result: Optional[AFDValidationResult] = None
