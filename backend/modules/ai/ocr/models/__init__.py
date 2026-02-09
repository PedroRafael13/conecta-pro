"""OCR Models."""

from modules.ai.ocr.models.document_scan import (
    DocumentScan,
    DocumentScanStatus,
    DocumentScanType,
)
from modules.ai.ocr.models.document_template import (
    DocumentTemplate,
    ExtractionRule,
    RuleType,
    TemplateField,
)
from modules.ai.ocr.models.extracted_field import (
    ExtractedField,
    FieldType,
    FieldValidationStatus,
)
from modules.ai.ocr.models.ocr_result import (
    OCRLine,
    OCRProvider,
    OCRResult,
    OCRWord,
)
from modules.ai.ocr.models.validation_result import (
    ValidationAction,
    ValidationResult,
    ValidationStatus,
)

__all__ = [
    # Document Scan
    "DocumentScan",
    "DocumentScanStatus",
    "DocumentScanType",
    # OCR Result
    "OCRResult",
    "OCRProvider",
    "OCRLine",
    "OCRWord",
    # Extracted Field
    "ExtractedField",
    "FieldType",
    "FieldValidationStatus",
    # Document Template
    "DocumentTemplate",
    "TemplateField",
    "ExtractionRule",
    "RuleType",
    # Validation Result
    "ValidationResult",
    "ValidationStatus",
    "ValidationAction",
]
