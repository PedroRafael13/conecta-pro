"""Repositories do módulo GED (Gestão Eletrônica de Documentos)."""

from modules.ged.repositories.folder_repository import FolderRepository
from modules.ged.repositories.document_repository import DocumentRepository
from modules.ged.repositories.document_version_repository import (
    DocumentVersionRepository,
)
from modules.ged.repositories.document_share_repository import DocumentShareRepository
from modules.ged.repositories.document_tag_repository import DocumentTagRepository
from modules.ged.repositories.document_signature_repository import (
    DocumentSignatureRepository,
)


__all__ = [
    "FolderRepository",
    "DocumentRepository",
    "DocumentVersionRepository",
    "DocumentShareRepository",
    "DocumentTagRepository",
    "DocumentSignatureRepository",
]
