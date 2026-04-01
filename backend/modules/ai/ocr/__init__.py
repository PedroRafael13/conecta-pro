"""OCR Module - Processamento Inteligente de Documentos.

Sprint 39 - Document OCR.

Features:
- OCR processing (Tesseract, Google Vision, AWS Textract)
- Data extraction from invoices, receipts, contracts
- Template-based extraction
- Validation workflows
- Integration with GED module
"""

from modules.ai.ocr.models import (
    DocumentScan,
    DocumentScanStatus,
    DocumentScanType,
    DocumentTemplate,
    ExtractedField,
    ExtractionRule,
    FieldType,
    OCRProvider,
    OCRResult,
    TemplateField,
    ValidationResult,
)

__all__ = [
    "DocumentScan",
    "DocumentScanStatus",
    "DocumentScanType",
    "OCRResult",
    "OCRProvider",
    "ExtractedField",
    "FieldType",
    "DocumentTemplate",
    "TemplateField",
    "ExtractionRule",
    "ValidationResult",
]
