"""Schemas do módulo de Ocorrências."""

from modules.occurrences.schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceUpdate,
    OccurrenceResponse,
    OccurrenceListResponse,
    OccurrenceFilter,
    OccurrenceStats,
    OccurrenceAssign,
    OccurrenceResolve,
    OccurrenceEscalate,
    OccurrenceRate,
)
from modules.occurrences.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryTree,
)
from modules.occurrences.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
)
from modules.occurrences.schemas.attachment import (
    AttachmentCreate,
    AttachmentResponse,
    AttachmentListResponse,
)

__all__ = [
    # Occurrence
    "OccurrenceCreate",
    "OccurrenceUpdate",
    "OccurrenceResponse",
    "OccurrenceListResponse",
    "OccurrenceFilter",
    "OccurrenceStats",
    "OccurrenceAssign",
    "OccurrenceResolve",
    "OccurrenceEscalate",
    "OccurrenceRate",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryListResponse",
    "CategoryTree",
    # Comment
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentListResponse",
    # Attachment
    "AttachmentCreate",
    "AttachmentResponse",
    "AttachmentListResponse",
]
