"""Módulo GED - Gestão Eletrônica de Documentos.

DEPRECATED: Use 'modules.pessoas' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.ged' is deprecated. "
    "Use 'modules.pessoas' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.ged.controllers import (  # noqa: E402
    document_router,
    folder_router,
    share_router,
    signature_router,
    stats_router,
    tag_router,
    version_router,
)
from modules.ged.models import (  # noqa: E402
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
from modules.ged.services import (  # noqa: E402
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
