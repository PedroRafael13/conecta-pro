"""Services do módulo de Ocorrências."""

from modules.occurrences.services.occurrence_service import OccurrenceService
from modules.occurrences.services.category_service import CategoryService
from modules.occurrences.services.comment_service import CommentService
from modules.occurrences.services.attachment_service import AttachmentService
from modules.occurrences.services.classification_ai_service import ClassificationAIService

__all__ = [
    "OccurrenceService",
    "CategoryService",
    "CommentService",
    "AttachmentService",
    "ClassificationAIService",
]
