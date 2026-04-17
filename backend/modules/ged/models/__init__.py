"""Models do módulo GED (Gestão Eletrônica de Documentos)."""

from modules.ged.models.document import (
    Document,
    DocumentCategory,
    DocumentConfidentiality,
    DocumentStatus,
    DocumentType,
    FileType,
)
from modules.ged.models.document_share import (
    DocumentShare,
    SharePermission,
    ShareStatus,
    ShareType,
)
from modules.ged.models.document_signature import (
    DocumentSignature,
    SignatureRole,
    SignatureStatus,
    SignatureType,
)
from modules.ged.models.document_tag import (
    DocumentTag,
    TagColor,
    TagType,
    document_tag_association,
)
from modules.ged.models.document_version import (
    DocumentVersion,
    VersionStatus,
    VersionType,
)
from modules.ged.models.folder import (
    Folder,
    FolderPermission,
    FolderStatus,
    FolderType,
)
from modules.ged.models.onvio_models import (
    FgtsGuia,
    InssGuia,
    OnvioDocCategory,
    OnvioDocument,
    OnvioSyncLog,
    OnvioSyncStatus,
)

__all__ = [
    # Folder
    "Folder",
    "FolderType",
    "FolderStatus",
    "FolderPermission",
    # Document
    "Document",
    "DocumentType",
    "DocumentStatus",
    "DocumentCategory",
    "DocumentConfidentiality",
    "FileType",
    # Version
    "DocumentVersion",
    "VersionType",
    "VersionStatus",
    # Share
    "DocumentShare",
    "ShareType",
    "SharePermission",
    "ShareStatus",
    # Tag
    "DocumentTag",
    "TagType",
    "TagColor",
    "document_tag_association",
    # Signature
    "DocumentSignature",
    "SignatureType",
    "SignatureStatus",
    "SignatureRole",
    # Onvio Sync
    "OnvioSyncLog",
    "OnvioSyncStatus",
    "OnvioDocument",
    "OnvioDocCategory",
    "FgtsGuia",
    "InssGuia",
]
