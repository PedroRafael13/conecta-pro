"""Schemas do módulo GED (Gestão Eletrônica de Documentos)."""

from modules.ged.schemas.folder import (
    FolderBase,
    FolderCreate,
    FolderUpdate,
    FolderResponse,
    FolderListResponse,
    FolderFilter,
    FolderTreeNode,
    FolderPermissionRequest,
    FolderStats,
)

from modules.ged.schemas.document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentFilter,
    DocumentMoveRequest,
    DocumentApprovalRequest,
    DocumentSearchRequest,
    DocumentStats,
    DocumentUploadRequest,
    DocumentOCRResult,
)

from modules.ged.schemas.document_version import (
    DocumentVersionBase,
    DocumentVersionCreate,
    DocumentVersionResponse,
    DocumentVersionListResponse,
    DocumentVersionCompare,
    DocumentVersionRestoreRequest,
)

from modules.ged.schemas.document_share import (
    DocumentShareBase,
    DocumentShareCreate,
    DocumentShareUpdate,
    DocumentShareResponse,
    DocumentShareListResponse,
    DocumentShareFilter,
    DocumentShareLinkRequest,
    DocumentShareLinkResponse,
    DocumentShareAccessRequest,
    DocumentShareStats,
)

from modules.ged.schemas.document_tag import (
    DocumentTagBase,
    DocumentTagCreate,
    DocumentTagUpdate,
    DocumentTagResponse,
    DocumentTagListResponse,
    DocumentTagFilter,
    DocumentTagTreeNode,
    DocumentTagAssignment,
    DocumentTagBulkCreate,
    DocumentTagStats,
)

from modules.ged.schemas.document_signature import (
    DocumentSignatureBase,
    DocumentSignatureCreate,
    DocumentSignatureUpdate,
    DocumentSignatureResponse,
    DocumentSignatureListResponse,
    DocumentSignatureFilter,
    SignatureRequest,
    SignatureRefusalRequest,
    SignatureVerifyRequest,
    SignatureBulkCreate,
    SignatureReminderRequest,
    SignatureStats,
    SignaturePositionRequest,
)


__all__ = [
    # Folder
    "FolderBase",
    "FolderCreate",
    "FolderUpdate",
    "FolderResponse",
    "FolderListResponse",
    "FolderFilter",
    "FolderTreeNode",
    "FolderPermissionRequest",
    "FolderStats",
    # Document
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    "DocumentFilter",
    "DocumentMoveRequest",
    "DocumentApprovalRequest",
    "DocumentSearchRequest",
    "DocumentStats",
    "DocumentUploadRequest",
    "DocumentOCRResult",
    # Version
    "DocumentVersionBase",
    "DocumentVersionCreate",
    "DocumentVersionResponse",
    "DocumentVersionListResponse",
    "DocumentVersionCompare",
    "DocumentVersionRestoreRequest",
    # Share
    "DocumentShareBase",
    "DocumentShareCreate",
    "DocumentShareUpdate",
    "DocumentShareResponse",
    "DocumentShareListResponse",
    "DocumentShareFilter",
    "DocumentShareLinkRequest",
    "DocumentShareLinkResponse",
    "DocumentShareAccessRequest",
    "DocumentShareStats",
    # Tag
    "DocumentTagBase",
    "DocumentTagCreate",
    "DocumentTagUpdate",
    "DocumentTagResponse",
    "DocumentTagListResponse",
    "DocumentTagFilter",
    "DocumentTagTreeNode",
    "DocumentTagAssignment",
    "DocumentTagBulkCreate",
    "DocumentTagStats",
    # Signature
    "DocumentSignatureBase",
    "DocumentSignatureCreate",
    "DocumentSignatureUpdate",
    "DocumentSignatureResponse",
    "DocumentSignatureListResponse",
    "DocumentSignatureFilter",
    "SignatureRequest",
    "SignatureRefusalRequest",
    "SignatureVerifyRequest",
    "SignatureBulkCreate",
    "SignatureReminderRequest",
    "SignatureStats",
    "SignaturePositionRequest",
]
