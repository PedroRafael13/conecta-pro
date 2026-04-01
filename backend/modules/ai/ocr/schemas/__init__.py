"""OCR Schemas."""

from modules.ai.ocr.schemas.ocr_schemas import (
    BatchProcessRequest,
    # Document Scan
    DocumentScanCreate,
    DocumentScanList,
    DocumentScanResponse,
    DocumentScanUpdate,
    # Document Template
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    ExtractedFieldCorrection,
    # Extracted Field
    ExtractedFieldResponse,
    # OCR Result
    OCRResultResponse,
    # Processing
    ProcessDocumentRequest,
    ProcessDocumentResponse,
    TemplateFieldCreate,
    # Validation
    ValidationResultResponse,
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
