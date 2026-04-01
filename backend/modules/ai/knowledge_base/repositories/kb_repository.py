"""
Knowledge Base Repository - Sprint 53.

Repositorio para acesso a dados da base de conhecimento.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from modules.ai.knowledge_base.models import (
    FAQ,
    Article,
    ArticleFeedback,
    ArticleStatusEnum,
    ArticleVersion,
    FAQFeedback,
    FAQStatusEnum,
    KBCategory,
    KnowledgeBase,
    KnowledgeBaseStatusEnum,
    QAInteraction,
    QASession,
    QASessionStatusEnum,
)

logger = logging.getLogger(__name__)


class KnowledgeBaseRepository:
    """Repositorio para Knowledge Base."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # Knowledge Base CRUD
    # =========================================================================

    def create_knowledge_base(
        self,
        name: str,
        slug: str,
        kb_type: str,
        visibility: str = "internal",
        description: str = None,
        condominio_id: UUID = None,
        owner_id: UUID = None,
        settings: dict[str, Any] = None,
    ) -> KnowledgeBase:
        """Cria nova base de conhecimento."""
        kb = KnowledgeBase(
            name=name,
            slug=slug,
            description=description,
            kb_type=kb_type,
            visibility=visibility,
            condominio_id=condominio_id,
            owner_id=owner_id,
            settings=settings or {},
        )
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        logger.info(f"KnowledgeBase created: {kb.id} - {kb.name}")
        return kb

    def get_knowledge_base(self, kb_id: UUID) -> KnowledgeBase | None:
        """Busca base de conhecimento por ID."""
        return (
            self.db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.id == kb_id,
                KnowledgeBase.ativo,
            )
            .first()
        )

    def get_knowledge_base_by_slug(self, slug: str) -> KnowledgeBase | None:
        """Busca base de conhecimento por slug."""
        return (
            self.db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.slug == slug,
                KnowledgeBase.ativo,
            )
            .first()
        )

    def list_knowledge_bases(
        self,
        condominio_id: UUID = None,
        status: str = None,
        kb_type: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[KnowledgeBase], int]:
        """Lista bases de conhecimento com filtros."""
        query = self.db.query(KnowledgeBase).filter(KnowledgeBase.ativo)

        if condominio_id:
            query = query.filter(KnowledgeBase.condominio_id == condominio_id)
        if status:
            query = query.filter(KnowledgeBase.status == status)
        if kb_type:
            query = query.filter(KnowledgeBase.kb_type == kb_type)

        total = query.count()
        items = query.order_by(desc(KnowledgeBase.created_at)).offset(skip).limit(limit).all()

        return items, total

    def update_knowledge_base(
        self,
        kb_id: UUID,
        **kwargs,
    ) -> KnowledgeBase | None:
        """Atualiza base de conhecimento."""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return None

        for key, value in kwargs.items():
            if hasattr(kb, key) and value is not None:
                setattr(kb, key, value)

        kb.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(kb)
        return kb

    def delete_knowledge_base(self, kb_id: UUID) -> bool:
        """Remove base de conhecimento (soft delete)."""
        kb = self.get_knowledge_base(kb_id)
        if not kb:
            return False

        kb.ativo = False
        kb.status = KnowledgeBaseStatusEnum.ARCHIVED
        self.db.commit()
        return True

    # =========================================================================
    # Category CRUD
    # =========================================================================

    def create_category(
        self,
        knowledge_base_id: UUID,
        name: str,
        slug: str,
        description: str = None,
        parent_id: UUID = None,
        icon: str = None,
        color: str = None,
        order: int = 0,
    ) -> KBCategory:
        """Cria nova categoria."""
        # Calcula nivel e path
        level = 0
        path = f"/{slug}"

        if parent_id:
            parent = self.db.query(KBCategory).filter(KBCategory.id == parent_id).first()
            if parent:
                level = parent.level + 1
                path = f"{parent.path}/{slug}"

        category = KBCategory(
            knowledge_base_id=knowledge_base_id,
            name=name,
            slug=slug,
            description=description,
            parent_id=parent_id,
            level=level,
            path=path,
            icon=icon,
            color=color,
            order=order,
        )
        self.db.add(category)

        # Atualiza contador da KB
        kb = self.get_knowledge_base(knowledge_base_id)
        if kb:
            kb.total_categories = (kb.total_categories or 0) + 1

        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: UUID) -> KBCategory | None:
        """Busca categoria por ID."""
        return (
            self.db.query(KBCategory)
            .filter(
                KBCategory.id == category_id,
                KBCategory.ativo,
            )
            .first()
        )

    def list_categories(
        self,
        knowledge_base_id: UUID,
        parent_id: UUID = None,
    ) -> list[KBCategory]:
        """Lista categorias de uma KB."""
        query = self.db.query(KBCategory).filter(
            KBCategory.knowledge_base_id == knowledge_base_id,
            KBCategory.ativo,
        )

        if parent_id:
            query = query.filter(KBCategory.parent_id == parent_id)
        else:
            query = query.filter(KBCategory.parent_id is None)

        return query.order_by(KBCategory.order, KBCategory.name).all()

    # =========================================================================
    # Article CRUD
    # =========================================================================

    def create_article(
        self,
        knowledge_base_id: UUID,
        title: str,
        slug: str,
        content: str,
        article_type: str = "guide",
        category_id: UUID = None,
        author_id: UUID = None,
        tags: list[str] = None,
        keywords: list[str] = None,
        metadata: dict[str, Any] = None,
    ) -> Article:
        """Cria novo artigo."""
        article = Article(
            knowledge_base_id=knowledge_base_id,
            title=title,
            slug=slug,
            content=content,
            article_type=article_type,
            category_id=category_id,
            author_id=author_id,
            tags=tags or [],
            keywords=keywords or [],
            metadata=metadata or {},
        )
        self.db.add(article)

        # Atualiza contadores
        kb = self.get_knowledge_base(knowledge_base_id)
        if kb:
            kb.total_articles = (kb.total_articles or 0) + 1

        if category_id:
            category = self.get_category(category_id)
            if category:
                category.article_count = (category.article_count or 0) + 1

        self.db.commit()
        self.db.refresh(article)
        logger.info(f"Article created: {article.id} - {article.title[:50]}")
        return article

    def get_article(self, article_id: UUID) -> Article | None:
        """Busca artigo por ID."""
        return (
            self.db.query(Article)
            .filter(
                Article.id == article_id,
                Article.ativo,
            )
            .first()
        )

    def get_article_by_slug(
        self,
        knowledge_base_id: UUID,
        slug: str,
    ) -> Article | None:
        """Busca artigo por slug."""
        return (
            self.db.query(Article)
            .filter(
                Article.knowledge_base_id == knowledge_base_id,
                Article.slug == slug,
                Article.ativo,
            )
            .first()
        )

    def list_articles(
        self,
        knowledge_base_id: UUID = None,
        category_id: UUID = None,
        status: str = None,
        article_type: str = None,
        tags: list[str] = None,
        search: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Article], int]:
        """Lista artigos com filtros."""
        query = self.db.query(Article).filter(Article.ativo)

        if knowledge_base_id:
            query = query.filter(Article.knowledge_base_id == knowledge_base_id)
        if category_id:
            query = query.filter(Article.category_id == category_id)
        if status:
            query = query.filter(Article.status == status)
        if article_type:
            query = query.filter(Article.article_type == article_type)
        if tags:
            query = query.filter(Article.tags.overlap(tags))
        if search:
            search_filter = or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        total = query.count()
        items = query.order_by(desc(Article.created_at)).offset(skip).limit(limit).all()

        return items, total

    def update_article(
        self,
        article_id: UUID,
        updated_by: UUID = None,
        **kwargs,
    ) -> Article | None:
        """Atualiza artigo."""
        article = self.get_article(article_id)
        if not article:
            return None

        # Salva versao anterior se houve mudanca de conteudo
        if "content" in kwargs and kwargs["content"] != article.content:
            version = ArticleVersion(
                article_id=article.id,
                version_number=article.version,
                title=article.title,
                content=article.content,
                summary=article.summary,
                created_by=updated_by,
            )
            self.db.add(version)
            article.version = (article.version or 1) + 1

        for key, value in kwargs.items():
            if hasattr(article, key) and value is not None:
                setattr(article, key, value)

        article.updated_at = datetime.utcnow()
        article.updated_by = updated_by
        self.db.commit()
        self.db.refresh(article)
        return article

    def increment_article_view(self, article_id: UUID) -> None:
        """Incrementa visualizacoes do artigo."""
        article = self.get_article(article_id)
        if article:
            article.view_count = (article.view_count or 0) + 1
            article.last_viewed_at = datetime.utcnow()
            self.db.commit()

    def add_article_feedback(
        self,
        article_id: UUID,
        is_helpful: bool = None,
        rating: int = None,
        comment: str = None,
        user_id: UUID = None,
        search_query: str = None,
    ) -> ArticleFeedback:
        """Adiciona feedback ao artigo."""
        feedback = ArticleFeedback(
            article_id=article_id,
            is_helpful=is_helpful,
            rating=rating,
            comment=comment,
            user_id=user_id,
            search_query=search_query,
        )
        self.db.add(feedback)

        # Atualiza contadores do artigo
        article = self.get_article(article_id)
        if article:
            if is_helpful is True:
                article.helpful_count = (article.helpful_count or 0) + 1
            elif is_helpful is False:
                article.not_helpful_count = (article.not_helpful_count or 0) + 1

            if rating:
                article.rating_sum = (article.rating_sum or 0) + rating
                article.rating_count = (article.rating_count or 0) + 1
                article.average_rating = article.rating_sum / article.rating_count

        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    # =========================================================================
    # FAQ CRUD
    # =========================================================================

    def create_faq(
        self,
        knowledge_base_id: UUID,
        question: str,
        answer: str,
        source: str = "manual",
        category_id: UUID = None,
        author_id: UUID = None,
        tags: list[str] = None,
        keywords: list[str] = None,
        question_variations: list[str] = None,
        metadata: dict[str, Any] = None,
    ) -> FAQ:
        """Cria nova FAQ."""
        faq = FAQ(
            knowledge_base_id=knowledge_base_id,
            question=question,
            answer=answer,
            source=source,
            category_id=category_id,
            author_id=author_id,
            tags=tags or [],
            keywords=keywords or [],
            question_variations=question_variations or [],
            metadata=metadata or {},
        )
        self.db.add(faq)

        # Atualiza contadores
        kb = self.get_knowledge_base(knowledge_base_id)
        if kb:
            kb.total_faqs = (kb.total_faqs or 0) + 1

        if category_id:
            category = self.get_category(category_id)
            if category:
                category.faq_count = (category.faq_count or 0) + 1

        self.db.commit()
        self.db.refresh(faq)
        logger.info(f"FAQ created: {faq.id} - {faq.question[:50]}")
        return faq

    def get_faq(self, faq_id: UUID) -> FAQ | None:
        """Busca FAQ por ID."""
        return (
            self.db.query(FAQ)
            .filter(
                FAQ.id == faq_id,
                FAQ.ativo,
            )
            .first()
        )

    def list_faqs(
        self,
        knowledge_base_id: UUID = None,
        category_id: UUID = None,
        status: str = None,
        tags: list[str] = None,
        search: str = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FAQ], int]:
        """Lista FAQs com filtros."""
        query = self.db.query(FAQ).filter(FAQ.ativo)

        if knowledge_base_id:
            query = query.filter(FAQ.knowledge_base_id == knowledge_base_id)
        if category_id:
            query = query.filter(FAQ.category_id == category_id)
        if status:
            query = query.filter(FAQ.status == status)
        if tags:
            query = query.filter(FAQ.tags.overlap(tags))
        if search:
            search_filter = or_(
                FAQ.question.ilike(f"%{search}%"),
                FAQ.answer.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        total = query.count()
        items = query.order_by(FAQ.order, desc(FAQ.created_at)).offset(skip).limit(limit).all()

        return items, total

    def update_faq(
        self,
        faq_id: UUID,
        updated_by: UUID = None,
        **kwargs,
    ) -> FAQ | None:
        """Atualiza FAQ."""
        faq = self.get_faq(faq_id)
        if not faq:
            return None

        for key, value in kwargs.items():
            if hasattr(faq, key) and value is not None:
                setattr(faq, key, value)

        faq.updated_at = datetime.utcnow()
        faq.updated_by = updated_by
        self.db.commit()
        self.db.refresh(faq)
        return faq

    def increment_faq_view(self, faq_id: UUID) -> None:
        """Incrementa visualizacoes da FAQ."""
        faq = self.get_faq(faq_id)
        if faq:
            faq.view_count = (faq.view_count or 0) + 1
            self.db.commit()

    def add_faq_feedback(
        self,
        faq_id: UUID,
        is_helpful: bool = None,
        rating: int = None,
        comment: str = None,
        user_id: UUID = None,
    ) -> FAQFeedback:
        """Adiciona feedback a FAQ."""
        feedback = FAQFeedback(
            faq_id=faq_id,
            is_helpful=is_helpful,
            rating=rating,
            comment=comment,
            user_id=user_id,
        )
        self.db.add(feedback)

        # Atualiza contadores
        faq = self.get_faq(faq_id)
        if faq:
            if is_helpful is True:
                faq.helpful_count = (faq.helpful_count or 0) + 1
            elif is_helpful is False:
                faq.not_helpful_count = (faq.not_helpful_count or 0) + 1

            # Recalcula helpfulness score
            total = (faq.helpful_count or 0) + (faq.not_helpful_count or 0)
            if total > 0:
                faq.helpfulness_score = (faq.helpful_count or 0) / total

        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    # =========================================================================
    # QA Session CRUD
    # =========================================================================

    def create_qa_session(
        self,
        session_key: str,
        source: str = "web_widget",
        knowledge_base_id: UUID = None,
        user_id: UUID = None,
        condominio_id: UUID = None,
        context: dict[str, Any] = None,
    ) -> QASession:
        """Cria nova sessao Q&A."""
        session = QASession(
            session_key=session_key,
            source=source,
            knowledge_base_id=knowledge_base_id,
            user_id=user_id,
            condominio_id=condominio_id,
            context=context or {},
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_qa_session(self, session_id: UUID) -> QASession | None:
        """Busca sessao Q&A por ID."""
        return self.db.query(QASession).filter(QASession.id == session_id).first()

    def get_qa_session_by_key(self, session_key: str) -> QASession | None:
        """Busca sessao Q&A por chave."""
        return self.db.query(QASession).filter(QASession.session_key == session_key).first()

    def add_qa_interaction(
        self,
        session_id: UUID,
        question: str,
        interaction_type: str = "question",
        response_type: str = None,
        response: str = None,
        confidence_score: float = 0.0,
        matched_articles: list[dict[str, Any]] = None,
        matched_faqs: list[dict[str, Any]] = None,
        response_time_ms: int = 0,
    ) -> QAInteraction:
        """Adiciona interacao a sessao."""
        interaction = QAInteraction(
            session_id=session_id,
            interaction_type=interaction_type,
            question=question,
            response_type=response_type,
            response=response,
            confidence_score=confidence_score,
            matched_articles=matched_articles or [],
            matched_faqs=matched_faqs or [],
            response_time_ms=response_time_ms,
        )
        self.db.add(interaction)

        # Atualiza estatisticas da sessao
        session = self.get_qa_session(session_id)
        if session:
            session.interaction_count = (session.interaction_count or 0) + 1
            session.question_count = (session.question_count or 0) + 1
            session.last_interaction_at = datetime.utcnow()

            if response:
                session.answered_count = (session.answered_count or 0) + 1
            else:
                session.unanswered_count = (session.unanswered_count or 0) + 1

        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def update_qa_interaction_feedback(
        self,
        interaction_id: UUID,
        is_helpful: bool = None,
        rating: int = None,
        feedback_text: str = None,
    ) -> QAInteraction | None:
        """Atualiza feedback de interacao."""
        interaction = self.db.query(QAInteraction).filter(QAInteraction.id == interaction_id).first()

        if not interaction:
            return None

        interaction.is_helpful = is_helpful
        interaction.rating = rating
        interaction.feedback_text = feedback_text
        interaction.feedback_at = datetime.utcnow()
        interaction.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def end_qa_session(
        self,
        session_id: UUID,
        resolved: bool = False,
        escalated: bool = False,
        escalation_reason: str = None,
    ) -> QASession | None:
        """Encerra sessao Q&A."""
        session = self.get_qa_session(session_id)
        if not session:
            return None

        session.status = QASessionStatusEnum.COMPLETED
        session.ended_at = datetime.utcnow()
        session.resolved = resolved
        session.escalated = escalated
        session.escalation_reason = escalation_reason

        if session.started_at:
            delta = session.ended_at - session.started_at
            session.total_duration_seconds = int(delta.total_seconds())

        self.db.commit()
        self.db.refresh(session)
        return session

    # =========================================================================
    # Dashboard e Estatisticas
    # =========================================================================

    def get_dashboard_stats(
        self,
        knowledge_base_id: UUID = None,
        condominio_id: UUID = None,
    ) -> dict[str, Any]:
        """Retorna estatisticas do dashboard."""
        # Filtros base
        kb_filter = []
        if knowledge_base_id:
            kb_filter.append(KnowledgeBase.id == knowledge_base_id)
        if condominio_id:
            kb_filter.append(KnowledgeBase.condominio_id == condominio_id)

        # Contagens
        total_kbs = (
            self.db.query(KnowledgeBase)
            .filter(
                KnowledgeBase.ativo,
                *kb_filter,
            )
            .count()
        )

        total_articles = self.db.query(Article).filter(Article.ativo).count()
        total_faqs = self.db.query(FAQ).filter(FAQ.ativo).count()
        total_categories = self.db.query(KBCategory).filter(KBCategory.ativo).count()

        # Sessoes Q&A
        total_sessions = self.db.query(QASession).count()
        total_interactions = self.db.query(QAInteraction).count()

        # Artigos por status
        articles_by_status = {}
        for status in ArticleStatusEnum:
            count = (
                self.db.query(Article)
                .filter(
                    Article.ativo,
                    Article.status == status,
                )
                .count()
            )
            articles_by_status[status.value] = count

        # FAQs por status
        faqs_by_status = {}
        for status in FAQStatusEnum:
            count = (
                self.db.query(FAQ)
                .filter(
                    FAQ.ativo,
                    FAQ.status == status,
                )
                .count()
            )
            faqs_by_status[status.value] = count

        # Top artigos
        top_articles = (
            self.db.query(Article)
            .filter(
                Article.ativo,
            )
            .order_by(desc(Article.view_count))
            .limit(5)
            .all()
        )

        # Top FAQs
        top_faqs = (
            self.db.query(FAQ)
            .filter(
                FAQ.ativo,
            )
            .order_by(desc(FAQ.view_count))
            .limit(5)
            .all()
        )

        return {
            "total_knowledge_bases": total_kbs,
            "total_articles": total_articles,
            "total_faqs": total_faqs,
            "total_categories": total_categories,
            "total_searches": 0,
            "total_views": 0,
            "total_qa_sessions": total_sessions,
            "total_questions_answered": total_interactions,
            "average_confidence": 0.0,
            "average_helpful_rate": 0.0,
            "average_response_time_ms": 0,
            "articles_by_status": articles_by_status,
            "faqs_by_status": faqs_by_status,
            "top_articles": top_articles,
            "top_faqs": top_faqs,
            "recent_questions": [],
            "searches_trend": [],
            "questions_trend": [],
        }
