"""Models do módulo GED (Gestão Eletrônica de Documentos)."""

from modules.ged.models.folder import (
    Folder,
    FolderType,
    FolderStatus,
    FolderPermission,
)

from modules.ged.models.document import (
    Document,
    DocumentType,
    DocumentStatus,
    DocumentCategory,
    DocumentConfidentiality,
    FileType,
)

from modules.ged.models.document_version import (
    DocumentVersion,
    VersionType,
    VersionStatus,
)

from modules.ged.models.document_share import (
    DocumentShare,
    ShareType,
    SharePermission,
    ShareStatus,
)

from modules.ged.models.document_tag import (
    DocumentTag,
    TagType,
    TagColor,
    document_tag_association,
)

from modules.ged.models.document_signature import (
    DocumentSignature,
    SignatureType,
    SignatureStatus,
    SignatureRole,
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
]
