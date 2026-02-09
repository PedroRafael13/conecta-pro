"""
Modelos do Document Intelligence.
"""

from modules.documents.models.document import (
    Document,
    DocumentSource,
    DocumentStatus,
    DocumentType,
    ProcessingStatus,
)
from modules.documents.models.extracted_field import (
    ExtractedField,
    ExtractionMethod,
    FieldConfidence,
    FieldType,
)
from modules.documents.models.extraction_template import (
    ExtractionTemplate,
    TemplateCategory,
    TemplateField,
    TemplateRule,
)
from modules.documents.models.ocr_result import (
    OCRBlock,
    OCRLine,
    OCRProvider,
    OCRResult,
    OCRWord,
)
from modules.documents.models.validation_result import (
    ValidationResult,
    ValidationRule,
    ValidationStatus,
    ValidationType,
)

__all__ = [
    # Document
    "Document",
    "DocumentType",
    "DocumentStatus",
    "DocumentSource",
    "ProcessingStatus",
    # OCR
    "OCRResult",
    "OCRLine",
    "OCRWord",
    "OCRBlock",
    "OCRProvider",
    # Extracted Field
    "ExtractedField",
    "FieldType",
    "FieldConfidence",
    "ExtractionMethod",
    # Template
    "ExtractionTemplate",
    "TemplateField",
    "TemplateRule",
    "TemplateCategory",
    # Validation
    "ValidationResult",
    "ValidationRule",
    "ValidationStatus",
    "ValidationType",
]
