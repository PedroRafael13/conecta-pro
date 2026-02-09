"""Campaign Service - Servico de Campanhas.

Sprint 32 - Automacoes Email.
Responsavel por:
- Campanhas automaticas
- Drip campaigns
- A/B testing
- Segmentacao
"""

import random  # noqa: S311
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.email.models.email_campaign import (
    CampaignStatus,
    CampaignType,
    EmailCampaign,
)
from modules.integrations.email.models.email_queue import EmailPriority, EmailQueue, EmailStatus
from modules.integrations.email.models.email_subscription import (
    EmailSubscription,
    SubscriptionStatus,
)
from modules.integrations.email.models.email_template import EmailTemplate
from modules.integrations.email.models.email_tracking import EmailTracking, TrackingEventType


@dataclass
class CampaignStats:
    """Estatisticas de campanha."""

    total_recipients: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_bounced: int = 0
    total_unsubscribed: int = 0

    @property
    def delivery_rate(self) -> float:
        """Taxa de entrega."""
        if not self.total_sent:
            return 0.0
        return (self.total_delivered / self.total_sent) * 100

    @property
    def open_rate(self) -> float:
        """Taxa de abertura."""
        if not self.total_delivered:
            return 0.0
        return (self.total_opened / self.total_delivered) * 100

    @property
    def click_rate(self) -> float:
        """Taxa de clique."""
        if not self.total_delivered:
            return 0.0
        return (self.total_clicked / self.total_delivered) * 100

    @property
    def click_to_open_rate(self) -> float:
        """Taxa de clique por abertura (CTOR)."""
        if not self.total_opened:
            return 0.0
        return (self.total_clicked / self.total_opened) * 100


@dataclass
class ABTestResult:
    """Resultado de teste A/B."""

    variant_a_id: UUID
    variant_b_id: UUID
    variant_a_opens: int = 0
    variant_b_opens: int = 0
    variant_a_clicks: int = 0
    variant_b_clicks: int = 0
    variant_a_sent: int = 0
    variant_b_sent: int = 0
    winner_id: UUID | None = None
    winner_criteria: str = "open_rate"
    confidence: float = 0.0

    @property
    def variant_a_open_rate(self) -> float:
        """Taxa de abertura variante A."""
        if not self.variant_a_sent:
            return 0.0
        return (self.variant_a_opens / self.variant_a_sent) * 100

    @property
    def variant_b_open_rate(self) -> float:
        """Taxa de abertura variante B."""
        if not self.variant_b_sent:
            return 0.0
        return (self.variant_b_opens / self.variant_b_sent) * 100

    @property
    def variant_a_click_rate(self) -> float:
        """Taxa de clique variante A."""
        if not self.variant_a_sent:
            return 0.0
        return (self.variant_a_clicks / self.variant_a_sent) * 100

    @property
    def variant_b_click_rate(self) -> float:
        """Taxa de clique variante B."""
        if not self.variant_b_sent:
            return 0.0
        return (self.variant_b_clicks / self.variant_b_sent) * 100


@dataclass
class DripStep:
    """Passo de drip campaign."""

    step_number: int
    template_id: UUID
    delay_days: int = 0
    delay_hours: int = 0
    condition: dict | None = None  # Condicao para envio
    subject_override: str | None = None


class CampaignService:
    """Servico de Campanhas de Email."""

    def __init__(self, session: AsyncSession):
        """Inicializa o servico.

        Args:
            session: Sessao assincrona do banco de dados.
        """
        self.session = session

    async def create_campaign(
        self,
        tenant_id: UUID,
        config_id: UUID,
        name: str,
        template_id: UUID,
        campaign_type: CampaignType = CampaignType.REGULAR,
        segment_filters: dict | None = None,
        scheduled_at: datetime | None = None,
        description: str | None = None,
    ) -> EmailCampaign:
        """Cria nova campanha.

        Args:
            tenant_id: ID do tenant.
            config_id: ID da configuracao.
            name: Nome da campanha.
            template_id: ID do template.
            campaign_type: Tipo da campanha.
            segment_filters: Filtros de segmentacao.
            scheduled_at: Agendamento.
            description: Descricao.

        Returns:
            EmailCampaign criada.
        """
        campaign = EmailCampaign(
            tenant_id=tenant_id,
            config_id=config_id,
            template_id=template_id,
            name=name,
            description=description,
            campaign_type=campaign_type,
            segment_filters=segment_filters,
            status=CampaignStatus.DRAFT,
        )

        if scheduled_at:
            campaign.schedule(scheduled_at)

        self.session.add(campaign)
        await self.session.flush()

        return campaign

    async def schedule_campaign(
        self,
        campaign_id: UUID,
        send_at: datetime,
    ) -> bool:
        """Agenda campanha.

        Args:
            campaign_id: ID da campanha.
            send_at: Data/hora de envio.

        Returns:
            True se agendada.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return False

        if campaign.status not in (CampaignStatus.DRAFT, CampaignStatus.PAUSED):
            return False

        campaign.schedule(send_at)
        return True

    async def start_campaign(self, campaign_id: UUID) -> int:
        """Inicia envio de campanha.

        Args:
            campaign_id: ID da campanha.

        Returns:
            Quantidade de destinatarios.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return 0

        if campaign.status not in (CampaignStatus.DRAFT, CampaignStatus.SCHEDULED):
            return 0

        # Busca destinatarios
        recipients = await self._get_recipients(
            campaign.tenant_id,
            campaign.segment_filters,
            campaign.recipient_list_ids,
            campaign.exclude_list_ids,
        )

        if not recipients:
            return 0

        # Atualiza campanha
        campaign.total_recipients = len(recipients)
        campaign.start_sending()

        # Busca template
        template = await self._get_template(campaign.template_id)
        if not template:
            return 0

        # Cria emails na fila
        for recipient in recipients:
            # Seleciona variante se A/B test
            selected_template = template
            if campaign.is_ab_test and campaign.ab_variants:
                selected_template = await self._select_ab_variant(campaign, template)

            # Renderiza
            variables = self._build_variables(recipient)
            subject, html, text = selected_template.render(variables)

            if campaign.subject:
                subject = campaign.subject

            queue_entry = EmailQueue(
                tenant_id=campaign.tenant_id,
                config_id=campaign.config_id,
                template_id=selected_template.id,
                campaign_id=campaign.id,
                to_email=recipient.email,
                to_name=recipient.full_name,
                from_email=campaign.from_email,
                from_name=campaign.from_name,
                reply_to=campaign.reply_to,
                subject=subject,
                html_content=html,
                text_content=text,
                variables=variables,
                priority=EmailPriority.NORMAL,
            )
            self.session.add(queue_entry)

        await self.session.flush()

        return len(recipients)

    async def pause_campaign(self, campaign_id: UUID) -> bool:
        """Pausa campanha.

        Args:
            campaign_id: ID da campanha.

        Returns:
            True se pausada.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return False

        campaign.pause()
        return True

    async def resume_campaign(self, campaign_id: UUID) -> bool:
        """Retoma campanha.

        Args:
            campaign_id: ID da campanha.

        Returns:
            True se retomada.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return False

        campaign.resume()
        return True

    async def cancel_campaign(self, campaign_id: UUID) -> bool:
        """Cancela campanha.

        Args:
            campaign_id: ID da campanha.

        Returns:
            True se cancelada.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return False

        campaign.cancel()

        # Cancela emails pendentes
        await self._cancel_pending_emails(campaign_id)

        return True

    async def get_campaign_stats(self, campaign_id: UUID) -> CampaignStats:
        """Obtem estatisticas da campanha.

        Args:
            campaign_id: ID da campanha.

        Returns:
            CampaignStats.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return CampaignStats()

        return CampaignStats(
            total_recipients=campaign.total_recipients or 0,
            total_sent=campaign.total_sent or 0,
            total_delivered=campaign.total_delivered or 0,
            total_opened=campaign.total_opened or 0,
            total_clicked=campaign.total_clicked or 0,
            total_bounced=campaign.total_bounced or 0,
            total_unsubscribed=campaign.total_unsubscribed or 0,
        )

    async def create_ab_test(
        self,
        campaign_id: UUID,
        variant_b_template_id: UUID,
        test_size: int = 20,
        winner_criteria: str = "open_rate",
        winner_wait_hours: int = 4,
    ) -> bool:
        """Configura teste A/B.

        Args:
            campaign_id: ID da campanha.
            variant_b_template_id: ID do template variante B.
            test_size: Percentual para teste.
            winner_criteria: Criterio para vencedor.
            winner_wait_hours: Horas para determinar vencedor.

        Returns:
            True se configurado.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign:
            return False

        if campaign.status != CampaignStatus.DRAFT:
            return False

        campaign.is_ab_test = True
        campaign.ab_variants = {
            "variant_a": str(campaign.template_id),
            "variant_b": str(variant_b_template_id),
        }
        campaign.ab_test_size = test_size
        campaign.ab_winner_criteria = winner_criteria
        campaign.ab_winner_wait_hours = winner_wait_hours

        return True

    async def determine_ab_winner(self, campaign_id: UUID) -> ABTestResult | None:
        """Determina vencedor do teste A/B.

        Args:
            campaign_id: ID da campanha.

        Returns:
            ABTestResult ou None.
        """
        campaign = await self._get_campaign(campaign_id)
        if not campaign or not campaign.is_ab_test:
            return None

        if not campaign.ab_variants:
            return None

        variant_a_id = UUID(campaign.ab_variants["variant_a"])
        variant_b_id = UUID(campaign.ab_variants["variant_b"])

        # Busca metricas por variante
        stats_a = await self._get_variant_stats(campaign_id, variant_a_id)
        stats_b = await self._get_variant_stats(campaign_id, variant_b_id)

        result = ABTestResult(
            variant_a_id=variant_a_id,
            variant_b_id=variant_b_id,
            variant_a_opens=stats_a.get("opens", 0),
            variant_b_opens=stats_b.get("opens", 0),
            variant_a_clicks=stats_a.get("clicks", 0),
            variant_b_clicks=stats_b.get("clicks", 0),
            variant_a_sent=stats_a.get("sent", 0),
            variant_b_sent=stats_b.get("sent", 0),
            winner_criteria=campaign.ab_winner_criteria or "open_rate",
        )

        # Determina vencedor
        if result.winner_criteria == "click_rate":
            if result.variant_a_click_rate > result.variant_b_click_rate:
                result.winner_id = variant_a_id
            else:
                result.winner_id = variant_b_id
        else:  # open_rate
            if result.variant_a_open_rate > result.variant_b_open_rate:
                result.winner_id = variant_a_id
            else:
                result.winner_id = variant_b_id

        # Atualiza campanha
        campaign.ab_winner_id = result.winner_id

        return result

    async def create_drip_campaign(
        self,
        tenant_id: UUID,
        config_id: UUID,
        name: str,
        steps: list[DripStep],
        trigger_type: str = "signup",
        trigger_config: dict | None = None,
    ) -> EmailCampaign:
        """Cria drip campaign.

        Args:
            tenant_id: ID do tenant.
            config_id: ID da configuracao.
            name: Nome da campanha.
            steps: Lista de passos.
            trigger_type: Tipo de trigger.
            trigger_config: Configuracao do trigger.

        Returns:
            EmailCampaign principal.
        """
        # Cria campanha principal
        main_campaign = EmailCampaign(
            tenant_id=tenant_id,
            config_id=config_id,
            name=name,
            campaign_type=CampaignType.DRIP,
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            status=CampaignStatus.DRAFT,
        )
        self.session.add(main_campaign)
        await self.session.flush()

        # Cria passos
        for step in steps:
            step_campaign = EmailCampaign(
                tenant_id=tenant_id,
                config_id=config_id,
                template_id=step.template_id,
                name=f"{name} - Passo {step.step_number}",
                campaign_type=CampaignType.DRIP,
                is_drip_step=True,
                drip_parent_id=main_campaign.id,
                drip_step_number=step.step_number,
                drip_delay_days=step.delay_days,
                drip_delay_hours=step.delay_hours,
                drip_condition=step.condition,
                subject=step.subject_override,
                status=CampaignStatus.DRAFT,
            )
            self.session.add(step_campaign)

        await self.session.flush()

        return main_campaign

    async def process_drip_trigger(
        self,
        _tenant_id: UUID,
        drip_campaign_id: UUID,
        recipient_email: str,
        recipient_name: str | None = None,
        variables: dict | None = None,
    ) -> bool:
        """Processa trigger de drip campaign.

        Args:
            _tenant_id: ID do tenant (reservado para uso futuro).
            drip_campaign_id: ID da drip campaign.
            recipient_email: Email do destinatario.
            recipient_name: Nome do destinatario.
            variables: Variaveis adicionais.

        Returns:
            True se processado.
        """
        # Busca campanha principal
        campaign = await self._get_campaign(drip_campaign_id)
        if not campaign or campaign.campaign_type != CampaignType.DRIP:
            return False

        if campaign.status not in (CampaignStatus.DRAFT, CampaignStatus.SCHEDULED):
            return False

        # Busca primeiro passo
        first_step = await self._get_drip_step(drip_campaign_id, 1)
        if not first_step:
            return False

        # Agenda primeiro email
        scheduled_at = datetime.utcnow() + timedelta(
            days=first_step.drip_delay_days or 0,
            hours=first_step.drip_delay_hours or 0,
        )

        await self._schedule_drip_email(
            first_step,
            recipient_email,
            recipient_name,
            variables or {},
            scheduled_at,
        )

        return True

    async def get_scheduled_campaigns(
        self,
        tenant_id: UUID,
    ) -> list[EmailCampaign]:
        """Lista campanhas agendadas.

        Args:
            tenant_id: ID do tenant.

        Returns:
            Lista de campanhas.
        """
        query = (
            select(EmailCampaign)
            .where(
                and_(
                    EmailCampaign.tenant_id == tenant_id,
                    EmailCampaign.status == CampaignStatus.SCHEDULED,
                    EmailCampaign.scheduled_at <= datetime.utcnow(),
                )
            )
            .order_by(EmailCampaign.scheduled_at.asc())
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # --- Metodos privados ---

    async def _get_campaign(self, campaign_id: UUID) -> EmailCampaign | None:
        """Busca campanha."""
        query = select(EmailCampaign).where(EmailCampaign.id == campaign_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_template(self, template_id: UUID) -> EmailTemplate | None:
        """Busca template."""
        query = select(EmailTemplate).where(EmailTemplate.id == template_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_recipients(
        self,
        tenant_id: UUID,
        _segment_filters: dict | None,
        _include_lists: list | None,
        _exclude_lists: list | None,
    ) -> list[EmailSubscription]:
        """Busca destinatarios da campanha."""
        query = select(EmailSubscription).where(
            and_(
                EmailSubscription.tenant_id == tenant_id,
                EmailSubscription.status == SubscriptionStatus.ACTIVE,
                EmailSubscription.confirmed.is_(True),
            )
        )

        # Filtros de segmentacao serao implementados em sprint futura

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _select_ab_variant(
        self,
        campaign: EmailCampaign,
        default_template: EmailTemplate,
    ) -> EmailTemplate:
        """Seleciona variante para teste A/B."""
        if not campaign.ab_variants:
            return default_template

        # Selecao aleatoria baseada no peso (50/50 por padrao)
        if random.random() < 0.5:  # nosec B311  # noqa: S311
            return default_template

        variant_b_id = UUID(campaign.ab_variants["variant_b"])
        variant_b = await self._get_template(variant_b_id)
        return variant_b if variant_b else default_template

    async def _get_variant_stats(
        self,
        campaign_id: UUID,
        template_id: UUID,
    ) -> dict:
        """Busca estatisticas de variante."""
        # Contagem de enviados
        sent_query = select(func.count(EmailQueue.id)).where(
            and_(
                EmailQueue.campaign_id == campaign_id,
                EmailQueue.template_id == template_id,
            )
        )
        sent_result = await self.session.execute(sent_query)
        sent = sent_result.scalar() or 0

        # Contagem de aberturas
        opens_query = (
            select(func.count(EmailTracking.id))
            .join(EmailQueue, EmailTracking.queue_id == EmailQueue.id)
            .where(
                and_(
                    EmailQueue.campaign_id == campaign_id,
                    EmailQueue.template_id == template_id,
                    EmailTracking.event_type == TrackingEventType.OPENED,
                )
            )
        )
        opens_result = await self.session.execute(opens_query)
        opens = opens_result.scalar() or 0

        # Contagem de cliques
        clicks_query = (
            select(func.count(EmailTracking.id))
            .join(EmailQueue, EmailTracking.queue_id == EmailQueue.id)
            .where(
                and_(
                    EmailQueue.campaign_id == campaign_id,
                    EmailQueue.template_id == template_id,
                    EmailTracking.event_type == TrackingEventType.CLICKED,
                )
            )
        )
        clicks_result = await self.session.execute(clicks_query)
        clicks = clicks_result.scalar() or 0

        return {
            "sent": sent,
            "opens": opens,
            "clicks": clicks,
        }

    async def _get_drip_step(
        self,
        parent_id: UUID,
        step_number: int,
    ) -> EmailCampaign | None:
        """Busca passo de drip campaign."""
        query = select(EmailCampaign).where(
            and_(
                EmailCampaign.drip_parent_id == parent_id,
                EmailCampaign.drip_step_number == step_number,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _schedule_drip_email(
        self,
        step: EmailCampaign,
        recipient_email: str,
        recipient_name: str | None,
        variables: dict,
        scheduled_at: datetime,
    ) -> None:
        """Agenda email de drip campaign."""
        template = await self._get_template(step.template_id)
        if not template:
            return

        subject, html, text = template.render(variables)
        if step.subject:
            subject = step.subject

        queue_entry = EmailQueue(
            tenant_id=step.tenant_id,
            config_id=step.config_id,
            template_id=step.template_id,
            campaign_id=step.id,
            to_email=recipient_email,
            to_name=recipient_name,
            from_email=step.from_email,
            from_name=step.from_name,
            subject=subject,
            html_content=html,
            text_content=text,
            variables=variables,
            scheduled_at=scheduled_at,
            priority=EmailPriority.NORMAL,
        )
        self.session.add(queue_entry)

    async def _cancel_pending_emails(self, campaign_id: UUID) -> int:
        """Cancela emails pendentes de uma campanha."""
        query = select(EmailQueue).where(
            and_(
                EmailQueue.campaign_id == campaign_id,
                EmailQueue.status.in_([EmailStatus.QUEUED, EmailStatus.PROCESSING]),
            )
        )

        result = await self.session.execute(query)
        emails = list(result.scalars().all())

        for email in emails:
            email.cancel()

        return len(emails)

    @staticmethod
    def _build_variables(subscription: EmailSubscription) -> dict:
        """Constroi variaveis para template."""
        return {
            "email": subscription.email,
            "nome": subscription.full_name or subscription.email.split("@")[0],
            "primeiro_nome": subscription.first_name or "",
            "sobrenome": subscription.last_name or "",
            "empresa": subscription.company or "",
        }
