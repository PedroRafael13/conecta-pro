"""
Schemas Pydantic do módulo GED — Gestão Eletrônica de Documentos.
"""

from .client import (
    GedClientBase,
    GedClientCreate,
    GedClientList,
    GedClientResponse,
    GedClientUpdate,
)
from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentSignatureRequest,
    DocumentUpdate,
    DocumentUpload,
)
from .kit import (
    KitBase,
    KitCreate,
    KitListResponse,
    KitResponse,
    KitStatusUpdate,
    KitSummary,
    KitUpdate,
)

__all__ = [
    # Client
    "GedClientBase",
    "GedClientCreate",
    "GedClientUpdate",
    "GedClientResponse",
    "GedClientList",
    # Kit
    "KitBase",
    "KitCreate",
    "KitUpdate",
    "KitResponse",
    "KitListResponse",
    "KitStatusUpdate",
    "KitSummary",
    # Document
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentUpload",
    "DocumentSignatureRequest",
    "DocumentListResponse",
]
