"""Models do módulo de Ocorrências."""

from modules.occurrences.models.occurrence import (
    Occurrence,
    OccurrencePriority,
    OccurrenceStatus,
    OccurrenceType,
    ReporterType,
)
from modules.occurrences.models.category import OccurrenceCategory
from modules.occurrences.models.comment import OccurrenceComment, CommentVisibility
from modules.occurrences.models.attachment import OccurrenceAttachment, AttachmentType

__all__ = [
    # Main model
    "Occurrence",
    # Category
    "OccurrenceCategory",
    # Comment
    "OccurrenceComment",
    "CommentVisibility",
    # Attachment
    "OccurrenceAttachment",
    "AttachmentType",
    # Enums
    "OccurrenceType",
    "OccurrenceStatus",
    "OccurrencePriority",
    "ReporterType",
]
