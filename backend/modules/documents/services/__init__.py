"""
Servicos do modulo Document Intelligence.

Contem todos os servicos para processamento de documentos.
"""

from .data_extractor import DataExtractor
from .document_classifier import DocumentClassifier
from .document_scanner import DocumentScanner
from .ocr_engine import OCRConfig, OCREngine
from .template_manager import TemplateManager
from .validation_engine import ValidationEngine

__all__ = [
    "DocumentScanner",
    "OCREngine",
    "OCRConfig",
    "DataExtractor",
    "DocumentClassifier",
    "ValidationEngine",
    "TemplateManager",
]
