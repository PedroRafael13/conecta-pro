"""Testes para os models do módulo Occurrences."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from modules.occurrences.models.occurrence import (
    Occurrence,
    OccurrenceType,
    OccurrenceStatus,
    OccurrencePriority,
    ReporterType,
)
from modules.occurrences.models.category import OccurrenceCategory
from modules.occurrences.models.comment import OccurrenceComment, CommentVisibility
from modules.occurrences.models.attachment import OccurrenceAttachment, AttachmentType


class TestOccurrenceModel:
    """Testes para Occurrence model."""

    def test_occurrence_creation(self):
        """Testa criacao de ocorrencia."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Vazamento no apartamento 101",
            description="Agua vazando do teto",
            type=OccurrenceType.INCIDENTE,
            priority=OccurrencePriority.ALTA,
            reporter_type=ReporterType.MORADOR,
            reporter_id=str(uuid4()),
            reporter_name="Joao Silva",
        )

        assert occurrence.title == "Vazamento no apartamento 101"
        assert occurrence.type == OccurrenceType.INCIDENTE
        assert occurrence.priority == OccurrencePriority.ALTA
        assert occurrence.status == OccurrenceStatus.ABERTA

    def test_occurrence_code_generation(self):
        """Testa geracao automatica de codigo."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.RECLAMACAO,
        )

        assert occurrence.code is not None
        assert occurrence.code.startswith("OCC-")

    def test_occurrence_start_analysis(self):
        """Testa inicio de analise."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.RECLAMACAO,
        )

        assert occurrence.status == OccurrenceStatus.ABERTA
        occurrence.start_analysis()
        assert occurrence.status == OccurrenceStatus.EM_ANALISE

    def test_occurrence_assign(self):
        """Testa atribuicao de responsavel."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.SOLICITACAO,
        )

        user_id = str(uuid4())
        occurrence.assign(user_id, "Maria", str(uuid4()), "Admin")

        assert occurrence.assigned_to_id == user_id
        assert occurrence.assigned_to_name == "Maria"
        assert occurrence.assigned_at is not None
        assert occurrence.status == OccurrenceStatus.EM_ANDAMENTO

    def test_occurrence_resolve(self):
        """Testa resolucao de ocorrencia."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.RECLAMACAO,
        )
        occurrence.start_analysis()

        user_id = str(uuid4())
        occurrence.resolve(user_id, "Tecnico", "Problema resolvido")

        assert occurrence.status == OccurrenceStatus.RESOLVIDA
        assert occurrence.resolved_by_id == user_id
        assert occurrence.resolved_at is not None
        assert occurrence.resolution_description == "Problema resolvido"

    def test_occurrence_escalate(self):
        """Testa escalonamento."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.EMERGENCIA,
            priority=OccurrencePriority.ALTA,
        )

        manager_id = str(uuid4())
        occurrence.escalate(manager_id, "Gerente", "Urgente")

        assert occurrence.is_escalated is True
        assert occurrence.escalated_to_id == manager_id
        assert occurrence.escalation_reason == "Urgente"

    def test_occurrence_reopen(self):
        """Testa reabertura."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.RECLAMACAO,
        )
        occurrence.resolve(str(uuid4()), "Tecnico", "Resolvido")

        occurrence.reopen("Problema persistiu", "Morador")

        assert occurrence.status == OccurrenceStatus.REABERTA
        assert occurrence.reopen_count == 1

    def test_occurrence_rate(self):
        """Testa avaliacao."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.SOLICITACAO,
        )
        occurrence.resolve(str(uuid4()), "Tecnico", "Resolvido")

        occurrence.rate(5, "Otimo atendimento!")

        assert occurrence.rating == 5
        assert occurrence.rating_comment == "Otimo atendimento!"
        assert occurrence.rated_at is not None

    def test_occurrence_sla(self):
        """Testa configuracao de SLA."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.RECLAMACAO,
        )

        occurrence.set_sla(4, 24)

        assert occurrence.sla_response_hours == 4
        assert occurrence.sla_resolution_hours == 24
        assert occurrence.sla_response_deadline is not None
        assert occurrence.sla_resolution_deadline is not None

    def test_occurrence_is_open(self):
        """Testa propriedade is_open."""
        occurrence = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.RECLAMACAO,
        )

        assert occurrence.is_open is True
        occurrence.resolve(str(uuid4()), "Tecnico", "Resolvido")
        assert occurrence.is_open is False

    def test_occurrence_priority_score(self):
        """Testa propriedade priority_score."""
        occurrence_baixa = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.SUGESTAO,
            priority=OccurrencePriority.BAIXA,
        )

        occurrence_critica = Occurrence(
            condominium_id=uuid4(),
            title="Teste",
            type=OccurrenceType.EMERGENCIA,
            priority=OccurrencePriority.CRITICA,
        )

        assert occurrence_baixa.priority_score < occurrence_critica.priority_score


class TestOccurrenceCategoryModel:
    """Testes para OccurrenceCategory model."""

    def test_category_creation(self):
        """Testa criacao de categoria."""
        category = OccurrenceCategory(
            name="Manutencao",
            description="Solicitacoes de manutencao",
            icon="wrench",
            color="#FF5733",
        )

        assert category.name == "Manutencao"
        assert category.code is not None
        assert category.is_active is True

    def test_category_hierarchy(self):
        """Testa hierarquia de categorias."""
        parent = OccurrenceCategory(name="Infraestrutura")
        child = OccurrenceCategory(name="Eletrica")

        child.set_parent(parent)

        assert child.parent_id == parent.id
        assert child.level == 1
        assert "infraestrutura" in child.path.lower()

    def test_category_sla_defaults(self):
        """Testa SLA padrao da categoria."""
        category = OccurrenceCategory(
            name="Emergencia",
            sla_response_hours=1,
            sla_resolution_hours=4,
        )

        assert category.sla_response_hours == 1
        assert category.sla_resolution_hours == 4


class TestOccurrenceCommentModel:
    """Testes para OccurrenceComment model."""

    def test_comment_creation(self):
        """Testa criacao de comentario."""
        comment = OccurrenceComment(
            occurrence_id=uuid4(),
            content="Este e um comentario de teste",
            author_id=str(uuid4()),
            author_name="Joao",
        )

        assert comment.content == "Este e um comentario de teste"
        assert comment.visibility == CommentVisibility.PUBLIC
        assert comment.is_deleted is False

    def test_comment_staff_flag(self):
        """Testa flag de staff."""
        comment = OccurrenceComment(
            occurrence_id=uuid4(),
            content="Resposta do administrador",
            author_id=str(uuid4()),
            author_name="Admin",
            is_staff=True,
        )

        assert comment.is_staff is True

    def test_comment_solution(self):
        """Testa marcacao como solucao."""
        comment = OccurrenceComment(
            occurrence_id=uuid4(),
            content="Esta e a solucao",
            author_id=str(uuid4()),
            author_name="Tecnico",
        )

        comment.mark_as_solution()

        assert comment.is_solution is True
        assert comment.solution_marked_at is not None

    def test_comment_pin(self):
        """Testa fixacao de comentario."""
        comment = OccurrenceComment(
            occurrence_id=uuid4(),
            content="Aviso importante",
            author_id=str(uuid4()),
            author_name="Sindico",
        )

        comment.pin()

        assert comment.is_pinned is True
        assert comment.pinned_at is not None

    def test_comment_soft_delete(self):
        """Testa soft delete."""
        comment = OccurrenceComment(
            occurrence_id=uuid4(),
            content="Comentario a deletar",
            author_id=str(uuid4()),
            author_name="Usuario",
        )

        user_id = str(uuid4())
        comment.soft_delete(user_id)

        assert comment.is_deleted is True
        assert comment.deleted_by_id == user_id
        assert comment.deleted_at is not None

    def test_comment_likes(self):
        """Testa sistema de likes."""
        comment = OccurrenceComment(
            occurrence_id=uuid4(),
            content="Comentario util",
            author_id=str(uuid4()),
            author_name="Usuario",
        )

        assert comment.likes_count == 0
        comment.increment_likes()
        assert comment.likes_count == 1
        comment.decrement_likes()
        assert comment.likes_count == 0


class TestOccurrenceAttachmentModel:
    """Testes para OccurrenceAttachment model."""

    def test_attachment_creation(self):
        """Testa criacao de anexo."""
        attachment = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="foto.jpg",
            original_filename="foto_vazamento.jpg",
            file_path="/uploads/foto.jpg",
            file_url="/api/uploads/foto.jpg",
            file_type=AttachmentType.IMAGE,
            mime_type="image/jpeg",
            file_size=1024000,
            uploaded_by_id=str(uuid4()),
            uploaded_by_name="Morador",
        )

        assert attachment.filename == "foto.jpg"
        assert attachment.file_type == AttachmentType.IMAGE
        assert attachment.is_public is True

    def test_attachment_type_detection(self):
        """Testa diferentes tipos de anexo."""
        image = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="foto.png",
            file_type=AttachmentType.IMAGE,
            uploaded_by_id=str(uuid4()),
        )
        assert image.file_type == AttachmentType.IMAGE

        video = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="video.mp4",
            file_type=AttachmentType.VIDEO,
            uploaded_by_id=str(uuid4()),
        )
        assert video.file_type == AttachmentType.VIDEO

        doc = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="contrato.pdf",
            file_type=AttachmentType.DOCUMENT,
            uploaded_by_id=str(uuid4()),
        )
        assert doc.file_type == AttachmentType.DOCUMENT

    def test_attachment_size_formatted(self):
        """Testa formatacao de tamanho."""
        attachment = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="arquivo.pdf",
            file_type=AttachmentType.DOCUMENT,
            file_size=1048576,  # 1 MB
            uploaded_by_id=str(uuid4()),
        )

        assert attachment.file_size_formatted == "1.00 MB"

    def test_attachment_privacy(self):
        """Testa visibilidade do anexo."""
        public_attachment = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="foto.jpg",
            file_type=AttachmentType.IMAGE,
            is_public=True,
            uploaded_by_id=str(uuid4()),
        )
        assert public_attachment.is_public is True

        private_attachment = OccurrenceAttachment(
            occurrence_id=uuid4(),
            filename="laudo.pdf",
            file_type=AttachmentType.DOCUMENT,
            is_public=False,
            uploaded_by_id=str(uuid4()),
        )
        assert private_attachment.is_public is False
