"""Módulo GED - Gestão Eletrônica de Documentos.

Este módulo fornece funcionalidades para:
- Gerenciamento de pastas e documentos
- Controle de versões
- Compartilhamento com controle de acesso
- Sistema de tags
- Assinaturas digitais
- Classificação por IA
- OCR e extração de texto
"""

from modules.ged.models import (
    Folder,
    Document,
    DocumentVersion,
    DocumentShare,
    DocumentTag,
    DocumentSignature,
    FolderType,
    FolderStatus,
    FolderPermission,
    DocumentType,
    DocumentStatus,
    DocumentCategory,
    DocumentConfidentiality,
    FileType,
    VersionType,
    VersionStatus,
    ShareType,
    SharePermission,
    ShareStatus,
    TagType,
    TagColor,
    SignatureType,
    SignatureStatus,
    SignatureRole,
)
from modules.ged.services import (
    FolderService,
    DocumentService,
    DocumentAIService,
    DocumentShareService,
    DocumentTagService,
    DocumentSignatureService,
)
from modules.ged.controllers import (
    folder_router,
    document_router,
    version_router,
    share_router,
    tag_router,
    signature_router,
)


__all__ = [
    # Models
    "Folder",
    "Document",
    "DocumentVersion",
    "DocumentShare",
    "DocumentTag",
    "DocumentSignature",
    # Enums
    "FolderType",
    "FolderStatus",
    "FolderPermission",
    "DocumentType",
    "DocumentStatus",
    "DocumentCategory",
    "DocumentConfidentiality",
    "FileType",
    "VersionType",
    "VersionStatus",
    "ShareType",
    "SharePermission",
    "ShareStatus",
    "TagType",
    "TagColor",
    "SignatureType",
    "SignatureStatus",
    "SignatureRole",
    # Services
    "FolderService",
    "DocumentService",
    "DocumentAIService",
    "DocumentShareService",
    "DocumentTagService",
    "DocumentSignatureService",
    # Routers
    "folder_router",
    "document_router",
    "version_router",
    "share_router",
    "tag_router",
    "signature_router",
]
