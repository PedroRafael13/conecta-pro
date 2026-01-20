"""Models do modulo de Ocorrencias."""

from .occurrence import (
    Occurrence,
    OccurrenceStatus,
    OccurrenceCategory,
    OccurrenceSeverity,
    OccurrenceType,
    OccurrencePriority,
    ResolutionType,
    DEFAULT_SLA_HOURS,
)
from .occurrence_attachment import OccurrenceAttachment, AttachmentType
from .occurrence_comment import OccurrenceComment
from .occurrence_category import OccurrenceCategoryConfig

__all__ = [
    # Main model
    "Occurrence",
    # Enums
    "OccurrenceStatus",
    "OccurrenceCategory",
    "OccurrenceSeverity",
    "OccurrenceType",
    "OccurrencePriority",
    "ResolutionType",
    "AttachmentType",
    # Constants
    "DEFAULT_SLA_HOURS",
    # Related models
    "OccurrenceAttachment",
    "OccurrenceComment",
    "OccurrenceCategoryConfig",
]
