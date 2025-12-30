"""Controllers do módulo de Ocorrências."""

from modules.occurrences.controllers.occurrence_controller import router as occurrence_router
from modules.occurrences.controllers.category_controller import router as category_router
from modules.occurrences.controllers.comment_controller import router as comment_router
from modules.occurrences.controllers.attachment_controller import router as attachment_router

__all__ = [
    "occurrence_router",
    "category_router",
    "comment_router",
    "attachment_router",
]
