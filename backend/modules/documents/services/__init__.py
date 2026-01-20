"""
Servicos do modulo Document Intelligence.

Contem todos os servicos para processamento de documentos.
"""

from .document_scanner import DocumentScanner
from .ocr_engine import OCREngine, OCRConfig
from .data_extractor import DataExtractor
from .document_classifier import DocumentClassifier
from .validation_engine import ValidationEngine
from .template_manager import TemplateManager

__all__ = [
    "DocumentScanner",
    "OCREngine",
    "OCRConfig",
    "DataExtractor",
    "DocumentClassifier",
    "ValidationEngine",
    "TemplateManager",
]
