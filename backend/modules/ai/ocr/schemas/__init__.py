"""OCR Schemas."""

from modules.ai.ocr.schemas.ocr_schemas import (
    # Document Scan
    DocumentScanCreate,
    DocumentScanUpdate,
    DocumentScanResponse,
    DocumentScanList,
    # OCR Result
    OCRResultResponse,
    # Extracted Field
    ExtractedFieldResponse,
    ExtractedFieldCorrection,
    # Document Template
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    TemplateFieldCreate,
    # Validation
    ValidationResultResponse,
    # Processing
    ProcessDocumentRequest,
    ProcessDocumentResponse,
    BatchProcessRequest,
)

__all__ = [
    "DocumentScanCreate",
    "DocumentScanUpdate",
    "DocumentScanResponse",
    "DocumentScanList",
    "OCRResultResponse",
    "ExtractedFieldResponse",
    "ExtractedFieldCorrection",
    "DocumentTemplateCreate",
    "DocumentTemplateResponse",
    "TemplateFieldCreate",
    "ValidationResultResponse",
    "ProcessDocumentRequest",
    "ProcessDocumentResponse",
    "BatchProcessRequest",
]
