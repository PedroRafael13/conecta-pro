"""
Modelos do Document Intelligence.
"""

from modules.documents.models.document import (
    Document,
    DocumentType,
    DocumentStatus,
    DocumentSource,
    ProcessingStatus,
)
from modules.documents.models.ocr_result import (
    OCRResult,
    OCRLine,
    OCRWord,
    OCRBlock,
    OCRProvider,
)
from modules.documents.models.extracted_field import (
    ExtractedField,
    FieldType,
    FieldConfidence,
    ExtractionMethod,
)
from modules.documents.models.extraction_template import (
    ExtractionTemplate,
    TemplateField,
    TemplateRule,
    TemplateCategory,
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
