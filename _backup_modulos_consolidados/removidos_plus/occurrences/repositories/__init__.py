"""Repositories do módulo de Ocorrências."""

from modules.occurrences.repositories.occurrence_repository import OccurrenceRepository
from modules.occurrences.repositories.category_repository import CategoryRepository
from modules.occurrences.repositories.comment_repository import CommentRepository
from modules.occurrences.repositories.attachment_repository import AttachmentRepository

__all__ = [
    "OccurrenceRepository",
    "CategoryRepository",
    "CommentRepository",
    "AttachmentRepository",
]
