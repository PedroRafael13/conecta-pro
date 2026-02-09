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

from modules.ged.controllers import (
    document_router,
    folder_router,
    share_router,
    signature_router,
    stats_router,
    tag_router,
    version_router,
)
from modules.ged.models import (
    Document,
    DocumentCategory,
    DocumentConfidentiality,
    DocumentShare,
    DocumentSignature,
    DocumentStatus,
    DocumentTag,
    DocumentType,
    DocumentVersion,
    FileType,
    Folder,
    FolderPermission,
    FolderStatus,
    FolderType,
    SharePermission,
    ShareStatus,
    ShareType,
    SignatureRole,
    SignatureStatus,
    SignatureType,
    TagColor,
    TagType,
    VersionStatus,
    VersionType,
)
from modules.ged.services import (
    DocumentAIService,
    DocumentService,
    DocumentShareService,
    DocumentSignatureService,
    DocumentTagService,
    FolderService,
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
    "stats_router",
]
