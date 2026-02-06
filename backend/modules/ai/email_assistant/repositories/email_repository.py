"""
Email Repository - Sprint 54.

Repositorio para persistencia de emails e entidades relacionadas.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta

from modules.ai.email_assistant.models import (
    Email,
    EmailResponse,
    EmailTemplate,
    EmailRule,
    EmailStatusEnum,
    EmailCategoryEnum,
    EmailPriorityEnum,
)


class EmailRepository:
    """Repositorio para operacoes com emails."""

    def __init__(self, session: AsyncSession):
        """Inicializa repositorio."""
        self.session = session

    # =========================================================================
    # Email CRUD
    # =========================================================================

    async def create_email(self, email_data: Dict[str, Any]) -> Email:
        """Cria novo email."""
        email = Email(**email_data)
        self.session.add(email)
        await self.session.commit()
        await self.session.refresh(email)
        return email

    async def get_email_by_id(
        self,
        email_id: UUID,
        include_responses: bool = False,
    ) -> Optional[Email]:
        """Busca email por ID."""
        query = select(Email).where(Email.id == email_id)

        if include_responses:
            query = query.options(selectinload(Email.responses))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_email_by_message_id(self, message_id: str) -> Optional[Email]:
        """Busca email por message_id."""
        query = select(Email).where(Email.message_id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_emails(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[EmailStatusEnum] = None,
        category: Optional[EmailCategoryEnum] = None,
        priority: Optional[EmailPriorityEnum] = None,
        is_spam: Optional[bool] = None,
        condominio_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Email], int]:
        """Lista emails com filtros."""
        query = select(Email).where(Email.ativo == True)

        # Filtros
        if status:
            query = query.where(Email.status == status)
        if category:
            query = query.where(Email.category == category)
        if priority:
            query = query.where(Email.priority == priority)
        if is_spam is not None:
            query = query.where(Email.is_spam == is_spam)
        if condominio_id:
            query = query.where(Email.condominio_id == condominio_id)
        if assigned_to:
            query = query.where(Email.assigned_to == assigned_to)
        if from_date:
            query = query.where(Email.received_at >= from_date)
        if to_date:
            query = query.where(Email.received_at <= to_date)
        if search:
            search_filter = or_(
                Email.subject.ilike(f"%{search}%"),
                Email.from_address.ilike(f"%{search}%"),
                Email.body_preview.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Contagem
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Paginacao
        query = query.order_by(desc(Email.received_at)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        emails = result.scalars().all()

        return list(emails), total

    async def update_email(
        self,
        email_id: UUID,
        update_data: Dict[str, Any],
    ) -> Optional[Email]:
        """Atualiza email."""
        email = await self.get_email_by_id(email_id)
        if not email:
            return None

        for key, value in update_data.items():
            if hasattr(email, key):
                setattr(email, key, value)

        email.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(email)
        return email

    async def update_email_classification(
        self,
        email_id: UUID,
        classification: Dict[str, Any],
    ) -> Optional[Email]:
        """Atualiza classificacao do email."""
        update_data = {
            "status": EmailStatusEnum.CLASSIFIED,
            "category": classification.get("category"),
            "category_confidence": classification.get("category_confidence", 0),
            "priority": classification.get("priority"),
            "priority_score": classification.get("priority_score", 0),
            "priority_factors": classification.get("priority_factors", {}),
            "sentiment": classification.get("sentiment"),
            "sentiment_score": classification.get("sentiment_score", 0),
            "emotions": classification.get("emotions", {}),
            "intent": classification.get("intent"),
            "intent_confidence": classification.get("intent_confidence", 0),
            "keywords": classification.get("keywords", []),
            "entities": classification.get("entities", []),
            "topics": classification.get("topics", []),
            "action_items": classification.get("action_items", []),
            "questions": classification.get("questions", []),
            "is_spam": classification.get("is_spam", False),
            "spam_score": classification.get("spam_score", 0),
            "is_phishing": classification.get("is_phishing", False),
            "phishing_indicators": classification.get("phishing_indicators", []),
            "security_score": classification.get("security_score", 1.0),
            "processing_time_ms": classification.get("processing_time_ms", 0),
            "processed_at": datetime.utcnow(),
        }
        return await self.update_email(email_id, update_data)

    async def mark_as_spam(self, email_id: UUID) -> Optional[Email]:
        """Marca email como spam."""
        return await self.update_email(email_id, {
            "is_spam": True,
            "status": EmailStatusEnum.SPAM,
        })

    async def mark_as_phishing(self, email_id: UUID) -> Optional[Email]:
        """Marca email como phishing."""
        return await self.update_email(email_id, {
            "is_phishing": True,
            "category": EmailCategoryEnum.PHISHING,
            "status": EmailStatusEnum.SPAM,
        })

    async def assign_email(
        self,
        email_id: UUID,
        user_id: Optional[UUID] = None,
        team: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Optional[Email]:
        """Atribui email a usuario/equipe."""
        return await self.update_email(email_id, {
            "assigned_to": user_id,
            "assigned_team": team,
            "routing_reason": reason,
        })

    async def archive_email(self, email_id: UUID) -> Optional[Email]:
        """Arquiva email."""
        return await self.update_email(email_id, {
            "status": EmailStatusEnum.ARCHIVED,
        })

    async def delete_email(self, email_id: UUID, soft: bool = True) -> bool:
        """Deleta email."""
        if soft:
            email = await self.update_email(email_id, {
                "ativo": False,
                "status": EmailStatusEnum.DELETED,
            })
            return email is not None
        else:
            email = await self.get_email_by_id(email_id)
            if email:
                await self.session.delete(email)
                await self.session.commit()
                return True
            return False

    # =========================================================================
    # Email Response CRUD
    # =========================================================================

    async def create_response(
        self,
        response_data: Dict[str, Any],
    ) -> EmailResponse:
        """Cria resposta de email."""
        response = EmailResponse(**response_data)
        self.session.add(response)
        await self.session.commit()
        await self.session.refresh(response)
        return response

    async def get_response_by_id(
        self,
        response_id: UUID,
    ) -> Optional[EmailResponse]:
        """Busca resposta por ID."""
        query = select(EmailResponse).where(EmailResponse.id == response_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_responses_by_email(
        self,
        email_id: UUID,
    ) -> List[EmailResponse]:
        """Lista respostas de um email."""
        query = (
            select(EmailResponse)
            .where(EmailResponse.email_id == email_id)
            .order_by(desc(EmailResponse.created_at))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_response(
        self,
        response_id: UUID,
        update_data: Dict[str, Any],
    ) -> Optional[EmailResponse]:
        """Atualiza resposta."""
        response = await self.get_response_by_id(response_id)
        if not response:
            return None

        for key, value in update_data.items():
            if hasattr(response, key):
                setattr(response, key, value)

        response.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(response)
        return response

    async def mark_response_sent(
        self,
        response_id: UUID,
    ) -> Optional[EmailResponse]:
        """Marca resposta como enviada."""
        return await self.update_response(response_id, {
            "is_sent": True,
            "is_draft": False,
            "sent_at": datetime.utcnow(),
        })

    # =========================================================================
    # Email Template CRUD
    # =========================================================================

    async def create_template(
        self,
        template_data: Dict[str, Any],
    ) -> EmailTemplate:
        """Cria template."""
        template = EmailTemplate(**template_data)
        self.session.add(template)
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def get_template_by_id(
        self,
        template_id: UUID,
    ) -> Optional[EmailTemplate]:
        """Busca template por ID."""
        query = select(EmailTemplate).where(
            and_(EmailTemplate.id == template_id, EmailTemplate.ativo == True)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_template_by_code(
        self,
        code: str,
    ) -> Optional[EmailTemplate]:
        """Busca template por codigo."""
        query = select(EmailTemplate).where(
            and_(EmailTemplate.code == code, EmailTemplate.ativo == True)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[EmailCategoryEnum] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[EmailTemplate], int]:
        """Lista templates."""
        query = select(EmailTemplate).where(EmailTemplate.ativo == True)

        if category:
            query = query.where(EmailTemplate.category == category)
        if is_active is not None:
            query = query.where(EmailTemplate.is_active == is_active)
        if search:
            search_filter = or_(
                EmailTemplate.name.ilike(f"%{search}%"),
                EmailTemplate.code.ilike(f"%{search}%"),
                EmailTemplate.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.order_by(EmailTemplate.name).offset(skip).limit(limit)

        result = await self.session.execute(query)
        templates = result.scalars().all()

        return list(templates), total

    async def find_templates_by_keywords(
        self,
        keywords: List[str],
    ) -> List[EmailTemplate]:
        """Busca templates por keywords."""
        query = (
            select(EmailTemplate)
            .where(
                and_(
                    EmailTemplate.ativo == True,
                    EmailTemplate.is_active == True,
                    EmailTemplate.trigger_keywords.overlap(keywords),
                )
            )
            .order_by(desc(EmailTemplate.usage_count))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def find_templates_by_intent(
        self,
        intent: str,
    ) -> List[EmailTemplate]:
        """Busca templates por intent."""
        query = (
            select(EmailTemplate)
            .where(
                and_(
                    EmailTemplate.ativo == True,
                    EmailTemplate.is_active == True,
                    EmailTemplate.trigger_intents.contains([intent]),
                )
            )
            .order_by(desc(EmailTemplate.success_rate))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_template(
        self,
        template_id: UUID,
        update_data: Dict[str, Any],
    ) -> Optional[EmailTemplate]:
        """Atualiza template."""
        template = await self.get_template_by_id(template_id)
        if not template:
            return None

        for key, value in update_data.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def increment_template_usage(
        self,
        template_id: UUID,
        success: bool = True,
    ) -> None:
        """Incrementa uso do template."""
        template = await self.get_template_by_id(template_id)
        if template:
            template.usage_count += 1
            if success:
                total = template.usage_count
                current_rate = template.success_rate
                template.success_rate = (current_rate * (total - 1) + 1.0) / total
            else:
                total = template.usage_count
                current_rate = template.success_rate
                template.success_rate = (current_rate * (total - 1)) / total
            await self.session.commit()

    async def delete_template(
        self,
        template_id: UUID,
        soft: bool = True,
    ) -> bool:
        """Deleta template."""
        if soft:
            template = await self.update_template(template_id, {"ativo": False})
            return template is not None
        else:
            template = await self.get_template_by_id(template_id)
            if template:
                await self.session.delete(template)
                await self.session.commit()
                return True
            return False

    # =========================================================================
    # Email Rule CRUD
    # =========================================================================

    async def create_rule(self, rule_data: Dict[str, Any]) -> EmailRule:
        """Cria regra."""
        rule = EmailRule(**rule_data)
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def get_rule_by_id(self, rule_id: UUID) -> Optional[EmailRule]:
        """Busca regra por ID."""
        query = select(EmailRule).where(
            and_(EmailRule.id == rule_id, EmailRule.ativo == True)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_rules(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        condominio_id: Optional[UUID] = None,
    ) -> Tuple[List[EmailRule], int]:
        """Lista regras."""
        query = select(EmailRule).where(EmailRule.ativo == True)

        if is_active is not None:
            query = query.where(EmailRule.is_active == is_active)
        if condominio_id:
            query = query.where(
                or_(
                    EmailRule.condominio_id == condominio_id,
                    EmailRule.condominio_id.is_(None),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        query = query.order_by(EmailRule.priority).offset(skip).limit(limit)

        result = await self.session.execute(query)
        rules = result.scalars().all()

        return list(rules), total

    async def get_active_rules(
        self,
        condominio_id: Optional[UUID] = None,
    ) -> List[EmailRule]:
        """Busca regras ativas ordenadas por prioridade."""
        query = (
            select(EmailRule)
            .where(
                and_(
                    EmailRule.ativo == True,
                    EmailRule.is_active == True,
                )
            )
        )

        if condominio_id:
            query = query.where(
                or_(
                    EmailRule.condominio_id == condominio_id,
                    EmailRule.condominio_id.is_(None),
                )
            )

        query = query.order_by(EmailRule.priority)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_rule(
        self,
        rule_id: UUID,
        update_data: Dict[str, Any],
    ) -> Optional[EmailRule]:
        """Atualiza regra."""
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return None

        for key, value in update_data.items():
            if hasattr(rule, key):
                setattr(rule, key, value)

        rule.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def increment_rule_match(self, rule_id: UUID) -> None:
        """Incrementa contador de match da regra."""
        rule = await self.get_rule_by_id(rule_id)
        if rule:
            rule.match_count += 1
            rule.last_match_at = datetime.utcnow()
            await self.session.commit()

    async def delete_rule(self, rule_id: UUID, soft: bool = True) -> bool:
        """Deleta regra."""
        if soft:
            rule = await self.update_rule(rule_id, {"ativo": False})
            return rule is not None
        else:
            rule = await self.get_rule_by_id(rule_id)
            if rule:
                await self.session.delete(rule)
                await self.session.commit()
                return True
            return False

    # =========================================================================
    # Statistics & Dashboard
    # =========================================================================

    async def get_email_stats(
        self,
        condominio_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Obtem estatisticas de emails."""
        base_query = select(Email).where(Email.ativo == True)

        if condominio_id:
            base_query = base_query.where(Email.condominio_id == condominio_id)
        if from_date:
            base_query = base_query.where(Email.received_at >= from_date)
        if to_date:
            base_query = base_query.where(Email.received_at <= to_date)

        # Total
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.session.execute(total_query)
        total = total_result.scalar()

        # Por status
        status_query = (
            select(Email.status, func.count())
            .where(Email.ativo == True)
            .group_by(Email.status)
        )
        if condominio_id:
            status_query = status_query.where(Email.condominio_id == condominio_id)
        status_result = await self.session.execute(status_query)
        by_status = {str(row[0].value): row[1] for row in status_result}

        # Por categoria
        category_query = (
            select(Email.category, func.count())
            .where(and_(Email.ativo == True, Email.category.isnot(None)))
            .group_by(Email.category)
        )
        if condominio_id:
            category_query = category_query.where(Email.condominio_id == condominio_id)
        category_result = await self.session.execute(category_query)
        by_category = {str(row[0].value): row[1] for row in category_result if row[0]}

        # Por prioridade
        priority_query = (
            select(Email.priority, func.count())
            .where(Email.ativo == True)
            .group_by(Email.priority)
        )
        if condominio_id:
            priority_query = priority_query.where(Email.condominio_id == condominio_id)
        priority_result = await self.session.execute(priority_query)
        by_priority = {str(row[0].value): row[1] for row in priority_result if row[0]}

        # Spam e Phishing
        spam_query = select(func.count()).where(
            and_(Email.ativo == True, Email.is_spam == True)
        )
        if condominio_id:
            spam_query = spam_query.where(Email.condominio_id == condominio_id)
        spam_result = await self.session.execute(spam_query)
        spam_count = spam_result.scalar()

        phishing_query = select(func.count()).where(
            and_(Email.ativo == True, Email.is_phishing == True)
        )
        if condominio_id:
            phishing_query = phishing_query.where(Email.condominio_id == condominio_id)
        phishing_result = await self.session.execute(phishing_query)
        phishing_count = phishing_result.scalar()

        # Media de tempo de processamento
        avg_time_query = select(func.avg(Email.processing_time_ms)).where(
            and_(Email.ativo == True, Email.processing_time_ms > 0)
        )
        if condominio_id:
            avg_time_query = avg_time_query.where(Email.condominio_id == condominio_id)
        avg_time_result = await self.session.execute(avg_time_query)
        avg_processing_time = avg_time_result.scalar() or 0

        # Por sentimento
        sentiment_query = (
            select(Email.sentiment, func.count())
            .where(and_(Email.ativo == True, Email.sentiment.isnot(None)))
            .group_by(Email.sentiment)
        )
        if condominio_id:
            sentiment_query = sentiment_query.where(Email.condominio_id == condominio_id)
        sentiment_result = await self.session.execute(sentiment_query)
        by_sentiment = {str(row[0].value): row[1] for row in sentiment_result if row[0]}

        return {
            "total_emails": total,
            "total_processed": by_status.get("classified", 0) + by_status.get("responded", 0),
            "total_unprocessed": by_status.get("received", 0) + by_status.get("processing", 0),
            "total_spam": spam_count,
            "total_phishing": phishing_count,
            "emails_by_status": by_status,
            "emails_by_category": by_category,
            "emails_by_priority": by_priority,
            "avg_processing_time_ms": float(avg_processing_time),
            "sentiment_distribution": by_sentiment,
        }

    async def get_email_trend(
        self,
        days: int = 30,
        condominio_id: Optional[UUID] = None,
    ) -> List[Dict[str, Any]]:
        """Obtem tendencia de emails nos ultimos dias."""
        from_date = datetime.utcnow() - timedelta(days=days)

        query = (
            select(
                func.date(Email.received_at).label("date"),
                func.count().label("count"),
            )
            .where(
                and_(
                    Email.ativo == True,
                    Email.received_at >= from_date,
                )
            )
            .group_by(func.date(Email.received_at))
            .order_by(func.date(Email.received_at))
        )

        if condominio_id:
            query = query.where(Email.condominio_id == condominio_id)

        result = await self.session.execute(query)
        return [
            {"date": str(row.date), "count": row.count}
            for row in result
        ]

    async def get_top_templates(
        self,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Obtem templates mais usados."""
        query = (
            select(EmailTemplate)
            .where(
                and_(
                    EmailTemplate.ativo == True,
                    EmailTemplate.is_active == True,
                )
            )
            .order_by(desc(EmailTemplate.usage_count))
            .limit(limit)
        )

        result = await self.session.execute(query)
        templates = result.scalars().all()

        return [
            {
                "id": str(t.id),
                "name": t.name,
                "code": t.code,
                "usage_count": t.usage_count,
                "success_rate": t.success_rate,
            }
            for t in templates
        ]
