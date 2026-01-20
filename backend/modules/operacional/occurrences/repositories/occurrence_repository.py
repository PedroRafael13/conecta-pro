"""
Repository para operacoes de Ocorrencias.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from modules.operacional.occurrences.models import (
    Occurrence,
    OccurrenceAttachment,
    OccurrenceComment,
    OccurrenceCategoryConfig,
    OccurrenceStatus,
    OccurrenceSeverity,
    OccurrencePriority,
)
from modules.operacional.occurrences.schemas import OccurrenceFilter

logger = logging.getLogger(__name__)


class OccurrenceRepository:
    """
    Repository para operacoes de banco de dados de Ocorrencias.

    Fornece metodos CRUD e consultas especializadas para o modelo Occurrence
    e seus relacionados (Attachment, Comment, CategoryConfig).

    Attributes:
        db: Sessao do banco de dados SQLAlchemy.

    Example:
        >>> repo = OccurrenceRepository(db)
        >>> occurrence = repo.get_by_id(occurrence_id)
        >>> occurrences = repo.list_by_tenant(tenant_id)
    """

    __slots__ = ("db",)

    def __init__(self, db: Session) -> None:
        """Inicializa o repository.

        Args:
            db: Sessao do banco de dados.
        """
        self.db = db

    # ============================================================
    # OCCURRENCE CRUD
    # ============================================================

    def create(self, occurrence: Occurrence) -> Occurrence:
        """Cria uma nova ocorrencia.

        Args:
            occurrence: Instancia da ocorrencia a criar.

        Returns:
            Ocorrencia criada com ID.
        """
        self.db.add(occurrence)
        self.db.commit()
        self.db.refresh(occurrence)
        logger.info(f"Ocorrencia criada: {occurrence.code}")
        return occurrence

    def get_by_id(
        self,
        occurrence_id: str,
        include_inactive: bool = False,
    ) -> Optional[Occurrence]:
        """Busca ocorrencia por ID.

        Args:
            occurrence_id: ID da ocorrencia.
            include_inactive: Se deve incluir registros inativos.

        Returns:
            Ocorrencia encontrada ou None.
        """
        query = (
            select(Occurrence)
            .options(
                selectinload(Occurrence.attachments),
                selectinload(Occurrence.comments),
            )
            .where(Occurrence.id == occurrence_id)
        )

        if not include_inactive:
            query = query.where(Occurrence.is_active == True)

        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_by_code(
        self,
        code: str,
        include_inactive: bool = False,
    ) -> Optional[Occurrence]:
        """Busca ocorrencia por codigo.

        Args:
            code: Codigo da ocorrencia (OCC-2026-00001).
            include_inactive: Se deve incluir registros inativos.

        Returns:
            Ocorrencia encontrada ou None.
        """
        query = (
            select(Occurrence)
            .options(
                selectinload(Occurrence.attachments),
                selectinload(Occurrence.comments),
            )
            .where(Occurrence.code == code)
        )

        if not include_inactive:
            query = query.where(Occurrence.is_active == True)

        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def update(self, occurrence: Occurrence) -> Occurrence:
        """Atualiza uma ocorrencia.

        Args:
            occurrence: Instancia da ocorrencia com alteracoes.

        Returns:
            Ocorrencia atualizada.
        """
        self.db.commit()
        self.db.refresh(occurrence)
        logger.info(f"Ocorrencia atualizada: {occurrence.code}")
        return occurrence

    def delete(self, occurrence_id: str, soft: bool = True) -> bool:
        """Remove uma ocorrencia.

        Args:
            occurrence_id: ID da ocorrencia.
            soft: Se True, faz soft delete. Se False, remove permanentemente.

        Returns:
            True se removida com sucesso.
        """
        occurrence = self.get_by_id(occurrence_id, include_inactive=True)
        if not occurrence:
            return False

        if soft:
            occurrence.soft_delete()
            self.db.commit()
            logger.info(f"Ocorrencia soft deleted: {occurrence.code}")
        else:
            self.db.delete(occurrence)
            self.db.commit()
            logger.info(f"Ocorrencia hard deleted: {occurrence_id}")

        return True

    # ============================================================
    # LIST AND FILTER
    # ============================================================

    def list_by_tenant(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[OccurrenceFilter] = None,
    ) -> Tuple[List[Occurrence], int]:
        """Lista ocorrencias de um tenant com filtros e paginacao.

        Args:
            tenant_id: ID do tenant.
            skip: Registros a pular.
            limit: Limite de registros.
            filters: Filtros opcionais.

        Returns:
            Tupla com lista de ocorrencias e total.
        """
        query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
        )

        # Aplicar filtros
        if filters:
            query = self._apply_filters(query, filters)

        # Contar total
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        # Ordenar e paginar
        query = (
            query
            .order_by(Occurrence.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = self.db.execute(query)
        occurrences = list(result.scalars().all())

        return occurrences, total

    def _apply_filters(
        self,
        query: Any,
        filters: OccurrenceFilter,
    ) -> Any:
        """Aplica filtros a uma query.

        Args:
            query: Query base.
            filters: Filtros a aplicar.

        Returns:
            Query com filtros aplicados.
        """
        if filters.post_id:
            query = query.where(Occurrence.post_id == str(filters.post_id))

        if filters.client_id:
            query = query.where(Occurrence.client_id == str(filters.client_id))

        if filters.contract_id:
            query = query.where(Occurrence.contract_id == str(filters.contract_id))

        if filters.category:
            query = query.where(Occurrence.category == filters.category.value)

        if filters.severity:
            query = query.where(Occurrence.severity == filters.severity.value)

        if filters.type:
            query = query.where(Occurrence.type == filters.type.value)

        if filters.status:
            query = query.where(Occurrence.status == filters.status.value)

        if filters.priority:
            query = query.where(Occurrence.priority == filters.priority.value)

        if filters.reported_by_id:
            query = query.where(Occurrence.reported_by_id == str(filters.reported_by_id))

        if filters.employee_involved_id:
            query = query.where(
                Occurrence.employee_involved_id == str(filters.employee_involved_id)
            )

        if filters.escalated is not None:
            query = query.where(Occurrence.escalated == filters.escalated)

        if filters.sla_breached is not None:
            query = query.where(Occurrence.sla_breached == filters.sla_breached)

        if filters.created_at_start:
            query = query.where(Occurrence.created_at >= filters.created_at_start)

        if filters.created_at_end:
            query = query.where(Occurrence.created_at <= filters.created_at_end)

        if filters.occurred_at_start:
            query = query.where(Occurrence.occurred_at >= filters.occurred_at_start)

        if filters.occurred_at_end:
            query = query.where(Occurrence.occurred_at <= filters.occurred_at_end)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Occurrence.title.ilike(search_term),
                    Occurrence.description.ilike(search_term),
                    Occurrence.code.ilike(search_term),
                )
            )

        return query

    def list_open(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Occurrence]:
        """Lista ocorrencias abertas.

        Args:
            tenant_id: ID do tenant.
            skip: Registros a pular.
            limit: Limite de registros.

        Returns:
            Lista de ocorrencias abertas.
        """
        query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(
                Occurrence.status.in_([
                    OccurrenceStatus.ABERTA.value,
                    OccurrenceStatus.EM_ANALISE.value,
                    OccurrenceStatus.PENDENTE_ACAO.value,
                ])
            )
            .order_by(
                # Urgentes primeiro
                Occurrence.priority.desc(),
                Occurrence.created_at.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = self.db.execute(query)
        return list(result.scalars().all())

    def list_by_user(
        self,
        user_id: str,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Occurrence]:
        """Lista ocorrencias atribuidas ou escaladas para um usuario.

        Args:
            user_id: ID do usuario.
            tenant_id: ID do tenant.
            skip: Registros a pular.
            limit: Limite de registros.

        Returns:
            Lista de ocorrencias.
        """
        query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(
                or_(
                    Occurrence.reported_by_id == user_id,
                    Occurrence.escalated_to_id == user_id,
                    Occurrence.resolved_by_id == user_id,
                )
            )
            .order_by(Occurrence.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = self.db.execute(query)
        return list(result.scalars().all())

    def list_sla_breaching(
        self,
        tenant_id: str,
        hours_threshold: int = 4,
    ) -> List[Occurrence]:
        """Lista ocorrencias com SLA vencendo.

        Args:
            tenant_id: ID do tenant.
            hours_threshold: Horas antes do vencimento para alertar.

        Returns:
            Lista de ocorrencias com SLA em risco.
        """
        from datetime import timedelta

        threshold_time = datetime.utcnow() + timedelta(hours=hours_threshold)

        query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(Occurrence.sla_breached == False)
            .where(Occurrence.sla_deadline.isnot(None))
            .where(Occurrence.sla_deadline <= threshold_time)
            .where(
                Occurrence.status.in_([
                    OccurrenceStatus.ABERTA.value,
                    OccurrenceStatus.EM_ANALISE.value,
                    OccurrenceStatus.PENDENTE_ACAO.value,
                ])
            )
            .order_by(Occurrence.sla_deadline.asc())
        )

        result = self.db.execute(query)
        return list(result.scalars().all())

    def list_critical(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Occurrence]:
        """Lista ocorrencias criticas.

        Args:
            tenant_id: ID do tenant.
            skip: Registros a pular.
            limit: Limite de registros.

        Returns:
            Lista de ocorrencias criticas.
        """
        query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(
                or_(
                    Occurrence.severity == OccurrenceSeverity.CRITICA.value,
                    Occurrence.priority == OccurrencePriority.URGENTE.value,
                )
            )
            .where(
                Occurrence.status.in_([
                    OccurrenceStatus.ABERTA.value,
                    OccurrenceStatus.EM_ANALISE.value,
                    OccurrenceStatus.PENDENTE_ACAO.value,
                ])
            )
            .order_by(Occurrence.created_at.asc())
            .offset(skip)
            .limit(limit)
        )

        result = self.db.execute(query)
        return list(result.scalars().all())

    # ============================================================
    # SEQUENCE AND CODE GENERATION
    # ============================================================

    def get_next_sequence(self, tenant_id: str, year: int) -> int:
        """Obtem o proximo numero sequencial para o ano.

        Args:
            tenant_id: ID do tenant.
            year: Ano de referencia.

        Returns:
            Proximo numero sequencial.
        """
        # Busca o maior numero do ano
        year_prefix = f"OCC-{year}-"
        query = (
            select(func.max(Occurrence.code))
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.code.like(f"{year_prefix}%"))
        )

        result = self.db.execute(query)
        last_code = result.scalar()

        if last_code:
            # Extrai o numero do codigo (OCC-2026-00001 -> 1)
            try:
                last_number = int(last_code.split("-")[-1])
                return last_number + 1
            except (ValueError, IndexError):
                pass

        return 1

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Obtem estatisticas de ocorrencias.

        Args:
            tenant_id: ID do tenant.
            start_date: Data inicial.
            end_date: Data final.

        Returns:
            Dicionario com estatisticas.
        """
        base_query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
        )

        if start_date:
            base_query = base_query.where(Occurrence.created_at >= start_date)
        if end_date:
            base_query = base_query.where(Occurrence.created_at <= end_date)

        # Total
        total = self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        ).scalar() or 0

        # Por status
        status_counts = {}
        for status in OccurrenceStatus:
            count = self.db.execute(
                select(func.count())
                .select_from(base_query.where(Occurrence.status == status.value).subquery())
            ).scalar() or 0
            status_counts[status.value] = count

        # Por categoria
        category_counts = self.db.execute(
            select(Occurrence.category, func.count())
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .group_by(Occurrence.category)
        ).all()

        # Por severidade
        severity_counts = self.db.execute(
            select(Occurrence.severity, func.count())
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .group_by(Occurrence.severity)
        ).all()

        # Por prioridade
        priority_counts = self.db.execute(
            select(Occurrence.priority, func.count())
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .group_by(Occurrence.priority)
        ).all()

        # SLA breached
        sla_breached = self.db.execute(
            select(func.count())
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(Occurrence.sla_breached == True)
        ).scalar() or 0

        # Criticas abertas
        criticas = self.db.execute(
            select(func.count())
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(
                or_(
                    Occurrence.severity == OccurrenceSeverity.CRITICA.value,
                    Occurrence.priority == OccurrencePriority.URGENTE.value,
                )
            )
            .where(
                Occurrence.status.in_([
                    OccurrenceStatus.ABERTA.value,
                    OccurrenceStatus.EM_ANALISE.value,
                    OccurrenceStatus.PENDENTE_ACAO.value,
                ])
            )
        ).scalar() or 0

        return {
            "total": total,
            "abertas": status_counts.get(OccurrenceStatus.ABERTA.value, 0),
            "em_analise": status_counts.get(OccurrenceStatus.EM_ANALISE.value, 0),
            "pendentes": status_counts.get(OccurrenceStatus.PENDENTE_ACAO.value, 0),
            "resolvidas": status_counts.get(OccurrenceStatus.RESOLVIDA.value, 0),
            "arquivadas": status_counts.get(OccurrenceStatus.ARQUIVADA.value, 0),
            "criticas": criticas,
            "sla_breached": sla_breached,
            "by_category": {cat: count for cat, count in category_counts},
            "by_severity": {sev: count for sev, count in severity_counts},
            "by_priority": {pri: count for pri, count in priority_counts},
        }

    # ============================================================
    # ATTACHMENT OPERATIONS
    # ============================================================

    def add_attachment(self, attachment: OccurrenceAttachment) -> OccurrenceAttachment:
        """Adiciona anexo a uma ocorrencia.

        Args:
            attachment: Instancia do anexo.

        Returns:
            Anexo criado.
        """
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        logger.info(f"Anexo adicionado: {attachment.id}")
        return attachment

    def get_attachments(
        self,
        occurrence_id: str,
        include_inactive: bool = False,
    ) -> List[OccurrenceAttachment]:
        """Lista anexos de uma ocorrencia.

        Args:
            occurrence_id: ID da ocorrencia.
            include_inactive: Se deve incluir inativos.

        Returns:
            Lista de anexos.
        """
        query = (
            select(OccurrenceAttachment)
            .where(OccurrenceAttachment.occurrence_id == occurrence_id)
        )

        if not include_inactive:
            query = query.where(OccurrenceAttachment.is_active == True)

        query = query.order_by(OccurrenceAttachment.uploaded_at.desc())

        result = self.db.execute(query)
        return list(result.scalars().all())

    def delete_attachment(self, attachment_id: str) -> bool:
        """Remove um anexo (soft delete).

        Args:
            attachment_id: ID do anexo.

        Returns:
            True se removido.
        """
        query = select(OccurrenceAttachment).where(OccurrenceAttachment.id == attachment_id)
        result = self.db.execute(query)
        attachment = result.scalar_one_or_none()

        if not attachment:
            return False

        attachment.soft_delete()
        self.db.commit()
        logger.info(f"Anexo removido: {attachment_id}")
        return True

    # ============================================================
    # COMMENT OPERATIONS
    # ============================================================

    def add_comment(self, comment: OccurrenceComment) -> OccurrenceComment:
        """Adiciona comentario a uma ocorrencia.

        Args:
            comment: Instancia do comentario.

        Returns:
            Comentario criado.
        """
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        logger.info(f"Comentario adicionado: {comment.id}")
        return comment

    def get_comments(
        self,
        occurrence_id: str,
        include_internal: bool = True,
        include_inactive: bool = False,
    ) -> List[OccurrenceComment]:
        """Lista comentarios de uma ocorrencia.

        Args:
            occurrence_id: ID da ocorrencia.
            include_internal: Se deve incluir comentarios internos.
            include_inactive: Se deve incluir inativos.

        Returns:
            Lista de comentarios.
        """
        query = (
            select(OccurrenceComment)
            .where(OccurrenceComment.occurrence_id == occurrence_id)
        )

        if not include_internal:
            query = query.where(OccurrenceComment.is_internal == False)

        if not include_inactive:
            query = query.where(OccurrenceComment.is_active == True)

        query = query.order_by(OccurrenceComment.created_at.asc())

        result = self.db.execute(query)
        return list(result.scalars().all())

    def delete_comment(self, comment_id: str) -> bool:
        """Remove um comentario (soft delete).

        Args:
            comment_id: ID do comentario.

        Returns:
            True se removido.
        """
        query = select(OccurrenceComment).where(OccurrenceComment.id == comment_id)
        result = self.db.execute(query)
        comment = result.scalar_one_or_none()

        if not comment:
            return False

        comment.soft_delete()
        self.db.commit()
        logger.info(f"Comentario removido: {comment_id}")
        return True

    # ============================================================
    # CATEGORY CONFIG OPERATIONS
    # ============================================================

    def create_category_config(
        self,
        config: OccurrenceCategoryConfig,
    ) -> OccurrenceCategoryConfig:
        """Cria configuracao de categoria.

        Args:
            config: Instancia da configuracao.

        Returns:
            Configuracao criada.
        """
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        logger.info(f"Categoria configurada: {config.code}")
        return config

    def get_category_config(
        self,
        tenant_id: str,
        code: str,
    ) -> Optional[OccurrenceCategoryConfig]:
        """Busca configuracao de categoria.

        Args:
            tenant_id: ID do tenant.
            code: Codigo da categoria.

        Returns:
            Configuracao encontrada ou None.
        """
        query = (
            select(OccurrenceCategoryConfig)
            .where(OccurrenceCategoryConfig.tenant_id == tenant_id)
            .where(OccurrenceCategoryConfig.code == code)
            .where(OccurrenceCategoryConfig.is_active == True)
        )

        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def list_category_configs(
        self,
        tenant_id: str,
        include_inactive: bool = False,
    ) -> List[OccurrenceCategoryConfig]:
        """Lista configuracoes de categoria.

        Args:
            tenant_id: ID do tenant.
            include_inactive: Se deve incluir inativos.

        Returns:
            Lista de configuracoes.
        """
        query = (
            select(OccurrenceCategoryConfig)
            .where(OccurrenceCategoryConfig.tenant_id == tenant_id)
        )

        if not include_inactive:
            query = query.where(OccurrenceCategoryConfig.is_active == True)

        query = query.order_by(OccurrenceCategoryConfig.display_order)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def update_category_config(
        self,
        config: OccurrenceCategoryConfig,
    ) -> OccurrenceCategoryConfig:
        """Atualiza configuracao de categoria.

        Args:
            config: Configuracao com alteracoes.

        Returns:
            Configuracao atualizada.
        """
        self.db.commit()
        self.db.refresh(config)
        logger.info(f"Categoria atualizada: {config.code}")
        return config

    # ============================================================
    # SLA CHECK
    # ============================================================

    def check_and_update_sla_breaches(self, tenant_id: str) -> int:
        """Verifica e atualiza ocorrencias com SLA violado.

        Args:
            tenant_id: ID do tenant.

        Returns:
            Numero de ocorrencias atualizadas.
        """
        now = datetime.utcnow()

        query = (
            select(Occurrence)
            .where(Occurrence.tenant_id == tenant_id)
            .where(Occurrence.is_active == True)
            .where(Occurrence.sla_breached == False)
            .where(Occurrence.sla_deadline.isnot(None))
            .where(Occurrence.sla_deadline < now)
            .where(
                Occurrence.status.in_([
                    OccurrenceStatus.ABERTA.value,
                    OccurrenceStatus.EM_ANALISE.value,
                    OccurrenceStatus.PENDENTE_ACAO.value,
                ])
            )
        )

        result = self.db.execute(query)
        occurrences = list(result.scalars().all())

        count = 0
        for occurrence in occurrences:
            occurrence.sla_breached = True
            count += 1

        if count > 0:
            self.db.commit()
            logger.warning(f"SLA violado em {count} ocorrencias do tenant {tenant_id}")

        return count
