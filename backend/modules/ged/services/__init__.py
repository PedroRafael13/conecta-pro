"""Services do módulo GED (Gestão Eletrônica de Documentos)."""

from modules.ged.services.document_ai_service import DocumentAIService
from modules.ged.services.document_service import DocumentService
from modules.ged.services.document_share_service import DocumentShareService
from modules.ged.services.document_signature_service import DocumentSignatureService
from modules.ged.services.document_tag_service import DocumentTagService
from modules.ged.services.folder_service import FolderService

__all__ = [
    "FolderService",
    "DocumentService",
    "DocumentAIService",
    "DocumentShareService",
    "DocumentTagService",
    "DocumentSignatureService",
]
