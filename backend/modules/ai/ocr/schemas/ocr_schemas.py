"""OCR Schemas - Pydantic schemas para a API.

Sprint 39 - Document OCR.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from modules.ai.ocr.models.document_scan import DocumentScanStatus, DocumentScanType
from modules.ai.ocr.models.ocr_result import OCRProvider
from modules.ai.ocr.models.extracted_field import FieldType, FieldValidationStatus
from modules.ai.ocr.models.validation_result import ValidationStatus


# ============================================================
# Document Scan Schemas
# ============================================================


class DocumentScanCreate(BaseModel):
    """Schema para criar scan de documento."""

    file_name: str = Field(..., min_length=1, max_length=500)
    document_type: Optional[DocumentScanType] = None
    template_id: Optional[str] = None
    tags: Optional[List[str]] = []
    category: Optional[str] = None
    priority: Optional[str] = "normal"
    source_module: Optional[str] = None
    source_entity: Optional[str] = None
    source_id: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = {}

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

    document_type: Optional[DocumentScanType] = None
    template_id: Optional[str] = None
    status: Optional[DocumentScanStatus] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    review_notes: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class DocumentScanResponse(BaseModel):
    """Schema de resposta para scan de documento."""

    id: str
    scan_id: str
    file_name: str
    file_size: Optional[int] = None
    document_type: Optional[str] = None
    detected_type: Optional[str] = None
    type_confidence: Optional[float] = None
    status: str
    status_message: Optional[str] = None
    page_count: int = 1
    ocr_provider: Optional[str] = None
    ocr_confidence: Optional[float] = None
    fields_extracted: int = 0
    fields_validated: int = 0
    fields_with_errors: int = 0
    validation_score: Optional[float] = None
    requires_review: bool = False
    tags: List[str] = []
    category: Optional[str] = None
    priority: str = "normal"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Configuracao do schema."""

        from_attributes = True


class DocumentScanList(BaseModel):
    """Schema para lista de scans."""

    items: List[DocumentScanResponse]
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
    raw_text: Optional[str] = None
    text_length: Optional[int] = None
    overall_confidence: Optional[float] = None
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    line_count: Optional[int] = None
    detected_language: Optional[str] = None
    processing_time_ms: Optional[int] = None
    tables: List[Dict[str, Any]] = []
    key_value_pairs: List[Dict[str, Any]] = []
    has_errors: bool = False
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
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
    field_label: Optional[str] = None
    field_type: str
    field_group: Optional[str] = None
    raw_value: Optional[str] = None
    extracted_value: Optional[str] = None
    normalized_value: Optional[str] = None
    formatted_value: Optional[str] = None
    confidence: Optional[float] = None
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
    correction_reason: Optional[str] = None


# ============================================================
# Document Template Schemas
# ============================================================


class TemplateFieldCreate(BaseModel):
    """Schema para criar campo de template."""

    name: str = Field(..., min_length=1, max_length=100)
    label: Optional[str] = None
    field_type: FieldType
    field_group: Optional[str] = None
    extraction_rules: List[Dict[str, Any]] = []
    is_required: bool = False
    validation_rules: List[Dict[str, Any]] = []
    transformations: List[Dict[str, Any]] = []
    target_entity: Optional[str] = None
    target_field: Optional[str] = None
    extraction_order: int = 0


class DocumentTemplateCreate(BaseModel):
    """Schema para criar template de documento."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    document_type: DocumentScanType
    document_subtype: Optional[str] = None
    detection_keywords: List[str] = []
    detection_threshold: float = 0.8
    ocr_settings: Optional[Dict[str, Any]] = {}
    preprocessing_steps: List[str] = []
    fields: List[TemplateFieldCreate] = []
    validation_rules: List[Dict[str, Any]] = []
    field_mapping: Optional[Dict[str, Any]] = {}
    tags: List[str] = []
    category: Optional[str] = None

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
    description: Optional[str] = None
    document_type: str
    document_subtype: Optional[str] = None
    version: str = "1.0.0"
    detection_keywords: List[str] = []
    detection_threshold: float = 0.8
    times_used: int = 0
    success_rate: Optional[float] = None
    avg_confidence: Optional[float] = None
    is_latest: bool = True
    tags: List[str] = []
    category: Optional[str] = None
    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    overall_score: Optional[float] = None
    needs_review: bool = False
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    auto_corrections: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        """Configuracao do schema."""

        from_attributes = True


# ============================================================
# Processing Schemas
# ============================================================


class ProcessDocumentRequest(BaseModel):
    """Schema para requisicao de processamento."""

    provider: Optional[OCRProvider] = None
    language: Optional[str] = "por"
    template_id: Optional[str] = None
    auto_detect_type: bool = True
    skip_validation: bool = False
    options: Optional[Dict[str, Any]] = {}

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
    document_type: Optional[str] = None
    ocr_confidence: Optional[float] = None
    fields_extracted: int = 0
    validation_status: Optional[str] = None
    validation_score: Optional[float] = None
    requires_review: bool = False
    processing_time_ms: int = 0
    fields: List[ExtractedFieldResponse] = []
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []


class BatchProcessRequest(BaseModel):
    """Schema para processamento em lote."""

    scan_ids: List[str] = Field(..., min_items=1, max_items=100)
    provider: Optional[OCRProvider] = None
    language: Optional[str] = "por"
    template_id: Optional[str] = None
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
