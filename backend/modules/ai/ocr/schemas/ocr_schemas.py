"""OCR Schemas - Pydantic schemas para a API.

Sprint 39 - Document OCR.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from modules.ai.ocr.models.document_scan import DocumentScanStatus, DocumentScanType
from modules.ai.ocr.models.extracted_field import FieldType
from modules.ai.ocr.models.ocr_result import OCRProvider

# ============================================================
# Document Scan Schemas
# ============================================================


class DocumentScanCreate(BaseModel):
    """Schema para criar scan de documento."""

    file_name: str = Field(..., min_length=1, max_length=500)
    document_type: DocumentScanType | None = None
    template_id: str | None = None
    tags: list[str] | None = []
    category: str | None = None
    priority: str | None = "normal"
    source_module: str | None = None
    source_entity: str | None = None
    source_id: str | None = None
    extra_data: dict[str, Any] | None = {}

    class Config:
        """Configuracao do schema."""

        json_schema_extra = {
            "example": {
                "file_name": "nota_fiscal_001.pdf",
                "document_type": "invoice",
                "tags": ["nfe", "fornecedor_x"],
                "priority": "high",
            }
        }


class DocumentScanUpdate(BaseModel):
    """Schema para atualizar scan de documento."""

    document_type: DocumentScanType | None = None
    template_id: str | None = None
    status: DocumentScanStatus | None = None
    tags: list[str] | None = None
    category: str | None = None
    priority: str | None = None
    review_notes: str | None = None
    extra_data: dict[str, Any] | None = None


class DocumentScanResponse(BaseModel):
    """Schema de resposta para scan de documento."""

    id: str
    scan_id: str
    file_name: str
    file_size: int | None = None
    document_type: str | None = None
    detected_type: str | None = None
    type_confidence: float | None = None
    status: str
    status_message: str | None = None
    page_count: int = 1
    ocr_provider: str | None = None
    ocr_confidence: float | None = None
    fields_extracted: int = 0
    fields_validated: int = 0
    fields_with_errors: int = 0
    validation_score: float | None = None
    requires_review: bool = False
    tags: list[str] = []
    category: str | None = None
    priority: str = "normal"
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class DocumentScanList(BaseModel):
    """Schema para lista de scans."""

    items: list[DocumentScanResponse]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int = 1


# ============================================================
# OCR Result Schemas
# ============================================================


class OCRResultResponse(BaseModel):
    """Schema de resposta para resultado OCR."""

    id: str
    result_id: str
    scan_id: str
    provider: str
    page_number: int = 1
    raw_text: str | None = None
    text_length: int | None = None
    overall_confidence: float | None = None
    min_confidence: float | None = None
    max_confidence: float | None = None
    line_count: int | None = None
    detected_language: str | None = None
    processing_time_ms: int | None = None
    tables: list[dict[str, Any]] = []
    key_value_pairs: list[dict[str, Any]] = []
    has_errors: bool = False
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


# ============================================================
# Extracted Field Schemas
# ============================================================


class ExtractedFieldResponse(BaseModel):
    """Schema de resposta para campo extraido."""

    id: str
    field_id: str
    scan_id: str
    field_name: str
    field_label: str | None = None
    field_type: str
    field_group: str | None = None
    raw_value: str | None = None
    extracted_value: str | None = None
    normalized_value: str | None = None
    formatted_value: str | None = None
    confidence: float | None = None
    validation_status: str
    was_corrected: bool = False
    is_required: bool = False
    is_key_field: bool = False
    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class ExtractedFieldCorrection(BaseModel):
    """Schema para correcao de campo."""

    field_id: str
    corrected_value: str
    correction_reason: str | None = None


# ============================================================
# Document Template Schemas
# ============================================================


class TemplateFieldCreate(BaseModel):
    """Schema para criar campo de template."""

    name: str = Field(..., min_length=1, max_length=100)
    label: str | None = None
    field_type: FieldType
    field_group: str | None = None
    extraction_rules: list[dict[str, Any]] = []
    is_required: bool = False
    validation_rules: list[dict[str, Any]] = []
    transformations: list[dict[str, Any]] = []
    target_entity: str | None = None
    target_field: str | None = None
    extraction_order: int = 0


class DocumentTemplateCreate(BaseModel):
    """Schema para criar template de documento."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    document_type: DocumentScanType
    document_subtype: str | None = None
    detection_keywords: list[str] = []
    detection_threshold: float = 0.8
    ocr_settings: dict[str, Any] | None = {}
    preprocessing_steps: list[str] = []
    fields: list[TemplateFieldCreate] = []
    validation_rules: list[dict[str, Any]] = []
    field_mapping: dict[str, Any] | None = {}
    tags: list[str] = []
    category: str | None = None

    class Config:
        """Configuracao do schema."""

        json_schema_extra = {
            "example": {
                "name": "Nota Fiscal Padrao",
                "document_type": "invoice",
                "detection_keywords": ["NOTA FISCAL", "NFe", "DANFE"],
                "fields": [
                    {
                        "name": "cnpj_emitente",
                        "label": "CNPJ do Emitente",
                        "field_type": "cnpj",
                        "is_required": True,
                    }
                ],
            }
        }


class DocumentTemplateResponse(BaseModel):
    """Schema de resposta para template."""

    id: str
    template_id: str
    name: str
    description: str | None = None
    document_type: str
    document_subtype: str | None = None
    version: str = "1.0.0"
    detection_keywords: list[str] = []
    detection_threshold: float = 0.8
    times_used: int = 0
    success_rate: float | None = None
    avg_confidence: float | None = None
    is_latest: bool = True
    tags: list[str] = []
    category: str | None = None
    active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        """Configuracao do schema."""

        from_attributes = True


# ============================================================
# Validation Schemas
# ============================================================


class ValidationResultResponse(BaseModel):
    """Schema de resposta para resultado de validacao."""

    id: str
    validation_id: str
    scan_id: str
    status: str
    total_fields: int = 0
    valid_fields: int = 0
    invalid_fields: int = 0
    warning_fields: int = 0
    overall_score: float | None = None
    needs_review: bool = False
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    auto_corrections: list[dict[str, Any]] = []
    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


# ============================================================
# Processing Schemas
# ============================================================


class ProcessDocumentRequest(BaseModel):
    """Schema para requisicao de processamento."""

    provider: OCRProvider | None = None
    language: str | None = "por"
    template_id: str | None = None
    auto_detect_type: bool = True
    skip_validation: bool = False
    options: dict[str, Any] | None = {}

    class Config:
        """Configuracao do schema."""

        json_schema_extra = {
            "example": {
                "provider": "tesseract",
                "language": "por",
                "auto_detect_type": True,
            }
        }


class ProcessDocumentResponse(BaseModel):
    """Schema de resposta para processamento."""

    scan_id: str
    status: str
    document_type: str | None = None
    ocr_confidence: float | None = None
    fields_extracted: int = 0
    validation_status: str | None = None
    validation_score: float | None = None
    requires_review: bool = False
    processing_time_ms: int = 0
    fields: list[ExtractedFieldResponse] = []
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []


class BatchProcessRequest(BaseModel):
    """Schema para processamento em lote."""

    scan_ids: list[str] = Field(..., min_items=1, max_items=100)
    provider: OCRProvider | None = None
    language: str | None = "por"
    template_id: str | None = None
    parallel: bool = True
    max_concurrent: int = 5

    class Config:
        """Configuracao do schema."""

        json_schema_extra = {
            "example": {
                "scan_ids": ["scan_001", "scan_002", "scan_003"],
                "provider": "google_vision",
                "parallel": True,
            }
        }
