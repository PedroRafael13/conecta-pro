"""
Módulo de Ocorrências - Sistema de gestão de ocorrências condominiais.

Este módulo fornece funcionalidades completas para:
- Registro e acompanhamento de ocorrências
- Categorização hierárquica com SLA
- Sistema de comentários com visibilidade
- Anexos de arquivos (imagens, documentos, mídia)
- Classificação automática por IA
- Workflow completo de atendimento

Models:
    - Occurrence: Ocorrência principal
    - OccurrenceCategory: Categorias hierárquicas
    - OccurrenceComment: Comentários
    - OccurrenceAttachment: Anexos

Enums:
    - OccurrenceType: 14 tipos de ocorrência
    - OccurrenceStatus: 9 status possíveis
    - OccurrencePriority: 5 níveis de prioridade
    - ReporterType: 8 tipos de reportador
    - CommentVisibility: público/interno/privado
    - AttachmentType: 8 tipos de arquivo

Services:
    - OccurrenceService: CRUD e workflow
    - CategoryService: Gestão de categorias
    - CommentService: Gestão de comentários
    - AttachmentService: Gestão de anexos
    - ClassificationAIService: IA para classificação
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.occurrences.models import (
        Occurrence,
        OccurrenceCategory,
        OccurrenceComment,
        OccurrenceAttachment,
        OccurrenceType,
        OccurrenceStatus,
        OccurrencePriority,
        ReporterType,
        CommentVisibility,
        AttachmentType,
    )
    from modules.occurrences.services import (
        OccurrenceService,
        CategoryService,
        CommentService,
        AttachmentService,
        ClassificationAIService,
    )
    from modules.occurrences.controllers import (
        occurrence_router,
        category_router,
        comment_router,
        attachment_router,
    )


def __getattr__(name: str):
    """Lazy loading de componentes do módulo."""
    # Models
    if name in (
        "Occurrence",
        "OccurrenceCategory",
        "OccurrenceComment",
        "OccurrenceAttachment",
        "OccurrenceType",
        "OccurrenceStatus",
        "OccurrencePriority",
        "ReporterType",
        "CommentVisibility",
        "AttachmentType",
    ):
        from modules.occurrences import models  # pylint: disable=import-outside-toplevel
        return getattr(models, name)

    # Services
    if name in (
        "OccurrenceService",
        "CategoryService",
        "CommentService",
        "AttachmentService",
        "ClassificationAIService",
    ):
        from modules.occurrences import services  # pylint: disable=import-outside-toplevel
        return getattr(services, name)

    # Controllers
    if name in (
        "occurrence_router",
        "category_router",
        "comment_router",
        "attachment_router",
    ):
        from modules.occurrences import controllers  # pylint: disable=import-outside-toplevel
        return getattr(controllers, name)

    raise AttributeError(f"module 'occurrences' has no attribute '{name}'")


__all__ = [
    # Models
    "Occurrence",
    "OccurrenceCategory",
    "OccurrenceComment",
    "OccurrenceAttachment",
    # Enums
    "OccurrenceType",
    "OccurrenceStatus",
    "OccurrencePriority",
    "ReporterType",
    "CommentVisibility",
    "AttachmentType",
    # Services
    "OccurrenceService",
    "CategoryService",
    "CommentService",
    "AttachmentService",
    "ClassificationAIService",
    # Routers
    "occurrence_router",
    "category_router",
    "comment_router",
    "attachment_router",
]
