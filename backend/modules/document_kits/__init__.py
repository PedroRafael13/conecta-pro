"""Módulo de Kits Documentais.

DEPRECATED: Use 'modules.tecnico' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import warnings

warnings.warn(
    "Importing from 'modules.document_kits' is deprecated. "
    "Use 'modules.tecnico' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from modules.document_kits.controllers import router  # noqa: E402
from modules.document_kits.models import (  # noqa: E402
    AssignmentStatus,
    DocumentKit,
    DocumentKitAssignment,
    DocumentKitItem,
    DocumentKitItemStatus,
    EntityType,
    ItemPriority,
    ItemStatusEnum,
    ItemType,
    KitStatus,
    KitType,
)
from modules.document_kits.services import DocumentKitAIService, DocumentKitService  # noqa: E402

__all__ = [
    "DocumentKit",
    "DocumentKitItem",
    "DocumentKitAssignment",
    "DocumentKitItemStatus",
    "KitType",
    "KitStatus",
    "ItemType",
    "ItemPriority",
    "AssignmentStatus",
    "ItemStatusEnum",
    "EntityType",
    "DocumentKitService",
    "DocumentKitAIService",
    "router",
]
