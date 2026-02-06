"""
Document Intelligence Module.

Este modulo fornece processamento inteligente de documentos com OCR,
extracao de dados estruturados, classificacao automatica e validacao.

Componentes:
- DocumentScanner: Upload e pre-processamento de imagens
- OCREngine: Motor OCR multi-provider (Tesseract, Google Vision, AWS Textract)
- DataExtractor: Extracao de campos estruturados
- DocumentClassifier: Classificacao automatica de tipos de documento
- ValidationEngine: Validacao de dados extraidos
- TemplateManager: Templates de extracao personalizados

Tipos de Documentos Suportados:
- Boletos bancarios
- Notas Fiscais (NFe, NFSe)
- Contratos
- RG/CPF/CNH
- Comprovantes de endereco
- Holerites
- Faturas
- Recibos
"""

from modules.documents.models import (
    Document,
    DocumentType,
    DocumentStatus,
    OCRResult,
    ExtractedField,
    ExtractionTemplate,
    ValidationResult,
)
from modules.documents.services import (
    DocumentScanner,
    OCREngine,
    DataExtractor,
    DocumentClassifier,
    ValidationEngine,
    TemplateManager,
)
from modules.documents.controllers import router

__all__ = [
    # Models
    "Document",
    "DocumentType",
    "DocumentStatus",
    "OCRResult",
    "ExtractedField",
    "ExtractionTemplate",
    "ValidationResult",
    # Services
    "DocumentScanner",
    "OCREngine",
    "DataExtractor",
    "DocumentClassifier",
    "ValidationEngine",
    "TemplateManager",
    # Router
    "router",
]

__version__ = "1.0.0"
