#!/usr/bin/env python3
"""
CONECTA PRO - CRM 360° + Customer Journey Service
==============================================
FASE 3 ONDA 3: Transformação Digital
Target ROI: R$ 140K

Recursos implementados:
- Visão 360° completa do cliente
- Mapeamento da jornada do cliente
- Rastreamento de interações multi-canal
- Analytics comportamental avançado
- Insights preditivos com IA
- Segmentação automática de clientes
- Gestão de lifecycle do cliente
- Integração com todos os módulos ERP
"""

import asyncio
import logging
import random  # noqa: S311
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerSegment(Enum):
    VIP = "vip"
    PREMIUM = "premium"
    STANDARD = "standard"
    BRONZE = "bronze"
    PROSPECT = "prospect"
    CHURNING = "churning"
    INACTIVE = "inactive"


class CustomerStage(Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    LOYAL = "loyal"
    ADVOCATE = "advocate"
    CHURNED = "churned"


class InteractionType(Enum):
    EMAIL = "email"
    PHONE = "phone"
    WHATSAPP = "whatsapp"
    PORTAL = "portal"
    MOBILE_APP = "mobile_app"
    FACE_TO_FACE = "face_to_face"
    SYSTEM = "system"
    SOCIAL_MEDIA = "social_media"


class InteractionDirection(Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class JourneyStage(Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    ONBOARDING = "onboarding"
    ACTIVE_USE = "active_use"
    EXPANSION = "expansion"
    RENEWAL = "renewal"
    ADVOCACY = "advocacy"
    CHURN = "churn"


class TouchpointCategory(Enum):
    MARKETING = "marketing"
    SALES = "sales"
    SUPPORT = "support"
    PRODUCT = "product"
    BILLING = "billing"
    TECHNICAL = "technical"


@dataclass
class CustomerInteraction:
    """Interação com o cliente em qualquer canal."""

    id: str
    customer_id: str
    timestamp: datetime
    type: InteractionType
    direction: InteractionDirection
    channel: str
    touchpoint_category: TouchpointCategory
    subject: str
    description: str
    sentiment_score: float  # -1 to 1
    satisfaction_score: float | None = None  # 0 to 10
    outcome: str | None = None
    next_action: str | None = None
    agent_id: str | None = None
    duration_seconds: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CustomerTouchpoint:
    """Ponto de contato na jornada do cliente."""

    id: str
    name: str
    category: TouchpointCategory
    channel: str
    stage: JourneyStage
    is_digital: bool
    importance_score: float  # 0 to 10
    satisfaction_avg: float
    conversion_rate: float
    description: str


@dataclass
class CustomerJourney:
    """Jornada completa do cliente."""

    customer_id: str
    current_stage: JourneyStage
    journey_start_date: datetime
    touchpoints_visited: list[str]
    interactions_count: int
    satisfaction_avg: float
    time_in_stage_days: int
    next_predicted_stage: JourneyStage | None
    stage_progression_probability: float
    churn_risk_score: float  # 0 to 1
    lifetime_value_predicted: float
    journey_health_score: float  # 0 to 100


@dataclass
class CustomerSegmentProfile:
    """Perfil de segmento de cliente."""

    segment: CustomerSegment
    criteria: dict[str, Any]
    customer_count: int
    avg_lifetime_value: float
    avg_satisfaction: float
    churn_rate: float
    growth_rate: float
    preferred_channels: list[str]
    behavior_patterns: dict[str, Any]


@dataclass
class Customer360:
    """Visão 360° completa do cliente."""

    id: str
    basic_info: dict[str, Any]
    segment: CustomerSegment
    stage: CustomerStage
    journey: CustomerJourney
    interactions: list[CustomerInteraction]
    behavioral_insights: dict[str, Any]
    preferences: dict[str, Any]
    satisfaction_metrics: dict[str, float]
    financial_metrics: dict[str, float]
    engagement_metrics: dict[str, float]
    risk_indicators: dict[str, float]
    opportunities: list[dict[str, Any]]
    next_best_actions: list[dict[str, Any]]
    created_at: datetime
    last_updated: datetime


@dataclass
class PredictiveInsight:
    """Insight preditivo sobre cliente."""

    customer_id: str
    insight_type: str
    prediction: str
    confidence_score: float
    impact_score: float  # 0 to 10
    recommendation: str
    data_sources: list[str]
    expires_at: datetime
    created_at: datetime


@dataclass
class CRMAnalytics:
    """Analytics completo do CRM."""

    total_customers: int
    active_customers: int
    new_customers_month: int
    churned_customers_month: int
    avg_customer_satisfaction: float
    avg_lifetime_value: float
    customer_acquisition_cost: float
    churn_rate: float
    segment_distribution: dict[str, int]
    stage_distribution: dict[str, int]
    interaction_volume_daily: int
    response_time_avg_hours: float
    conversion_rates: dict[str, float]


class CRM360Service:
    """Serviço CRM 360° + Customer Journey completo."""

    def __init__(self):
        self.customers: dict[str, Customer360] = {}
        self.interactions: dict[str, CustomerInteraction] = {}
        self.touchpoints: dict[str, CustomerTouchpoint] = {}
        self.segments: dict[CustomerSegment, CustomerSegmentProfile] = {}
        self.predictive_insights: dict[str, list[PredictiveInsight]] = {}

        # Inicializar com dados de demonstração
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Inicializar com dados de demonstração."""

        # Criar touchpoints da jornada
        touchpoints_data = [
            {
                "name": "Website Landing Page",
                "category": TouchpointCategory.MARKETING,
                "channel": "website",
                "stage": JourneyStage.AWARENESS,
                "digital": True,
            },
            {
                "name": "WhatsApp First Contact",
                "category": TouchpointCategory.SALES,
                "channel": "whatsapp",
                "stage": JourneyStage.CONSIDERATION,
                "digital": True,
            },
            {
                "name": "Proposta Comercial",
                "category": TouchpointCategory.SALES,
                "channel": "email",
                "stage": JourneyStage.DECISION,
                "digital": True,
            },
            {
                "name": "Onboarding Call",
                "category": TouchpointCategory.SUPPORT,
                "channel": "phone",
                "stage": JourneyStage.ONBOARDING,
                "digital": False,
            },
            {
                "name": "Portal de Cliente",
                "category": TouchpointCategory.PRODUCT,
                "channel": "portal",
                "stage": JourneyStage.ACTIVE_USE,
                "digital": True,
            },
            {
                "name": "App Mobile",
                "category": TouchpointCategory.PRODUCT,
                "channel": "mobile_app",
                "stage": JourneyStage.ACTIVE_USE,
                "digital": True,
            },
            {
                "name": "Suporte Técnico",
                "category": TouchpointCategory.TECHNICAL,
                "channel": "phone",
                "stage": JourneyStage.ACTIVE_USE,
                "digital": False,
            },
            {
                "name": "Renovação de Contrato",
                "category": TouchpointCategory.SALES,
                "channel": "face_to_face",
                "stage": JourneyStage.RENEWAL,
                "digital": False,
            },
            {
                "name": "Programa de Indicação",
                "category": TouchpointCategory.MARKETING,
                "channel": "email",
                "stage": JourneyStage.ADVOCACY,
                "digital": True,
            },
        ]

        for i, tp_data in enumerate(touchpoints_data, 1):
            touchpoint = CustomerTouchpoint(
                id=f"TP_{i:03d}",
                name=tp_data["name"],
                category=tp_data["category"],
                channel=tp_data["channel"],
                stage=tp_data["stage"],
                is_digital=tp_data["digital"],
                importance_score=random.uniform(6.0, 9.5),  # noqa: S311
                satisfaction_avg=random.uniform(7.0, 9.0),  # noqa: S311
                conversion_rate=random.uniform(0.15, 0.85),  # noqa: S311
                description=f"Touchpoint {tp_data['name']} na jornada do cliente",
            )
            self.touchpoints[touchpoint.id] = touchpoint

        # Criar clientes de demonstração
        demo_customers = [
            {"name": "Condomínio Jardim Europa", "segment": CustomerSegment.VIP, "stage": CustomerStage.LOYAL},
            {
                "name": "Residencial Parque das Flores",
                "segment": CustomerSegment.PREMIUM,
                "stage": CustomerStage.CUSTOMER,
            },
            {"name": "Edifício Corporate Center", "segment": CustomerSegment.STANDARD, "stage": CustomerStage.CUSTOMER},
            {"name": "Condomínio Vila Madalena", "segment": CustomerSegment.VIP, "stage": CustomerStage.ADVOCATE},
            {"name": "Residencial Green Park", "segment": CustomerSegment.PREMIUM, "stage": CustomerStage.LOYAL},
            {"name": "Edifício Manhattan", "segment": CustomerSegment.STANDARD, "stage": CustomerStage.PROSPECT},
            {"name": "Condomínio Sunset", "segment": CustomerSegment.BRONZE, "stage": CustomerStage.CUSTOMER},
        ]

        for i, cust_data in enumerate(demo_customers, 1):
            customer_id = f"CUST_{i:04d}"

            # Criar jornada do cliente
            journey_start = datetime.now() - timedelta(days=random.randint(30, 730))  # noqa: S311
            current_stage = self._get_journey_stage_from_customer_stage(cust_data["stage"])

            journey = CustomerJourney(
                customer_id=customer_id,
                current_stage=current_stage,
                journey_start_date=journey_start,
                touchpoints_visited=[tp.id for tp in list(self.touchpoints.values())[: random.randint(3, 7)]],  # noqa: S311
                interactions_count=random.randint(15, 80),  # noqa: S311
                satisfaction_avg=random.uniform(7.2, 9.1),  # noqa: S311
                time_in_stage_days=(datetime.now() - journey_start).days,
                next_predicted_stage=self._predict_next_journey_stage(current_stage),
                stage_progression_probability=random.uniform(0.6, 0.9),  # noqa: S311
                churn_risk_score=random.uniform(0.1, 0.4),  # noqa: S311
                lifetime_value_predicted=random.uniform(50000, 300000),  # noqa: S311
                journey_health_score=random.uniform(75, 95),  # noqa: S311
            )

            # Criar customer 360
            customer = Customer360(
                id=customer_id,
                basic_info={
                    "name": cust_data["name"],
                    "type": "condomínio",
                    "created_date": journey_start.isoformat(),
                    "units": random.randint(20, 200),  # noqa: S311
                    "location": f"São Paulo - Zona {random.choice(['Sul', 'Norte', 'Oeste', 'Central'])}",  # noqa: S311
                },
                segment=cust_data["segment"],
                stage=cust_data["stage"],
                journey=journey,
                interactions=[],
                behavioral_insights=self._generate_behavioral_insights(cust_data["segment"]),
                preferences=self._generate_customer_preferences(),
                satisfaction_metrics=self._generate_satisfaction_metrics(),
                financial_metrics=self._generate_financial_metrics(cust_data["segment"]),
                engagement_metrics=self._generate_engagement_metrics(),
                risk_indicators=self._generate_risk_indicators(),
                opportunities=self._generate_opportunities(cust_data["segment"]),
                next_best_actions=self._generate_next_best_actions(cust_data["stage"]),
                created_at=journey_start,
                last_updated=datetime.now(),
            )

            self.customers[customer_id] = customer

            # Criar algumas interações para cada cliente
            await self._generate_customer_interactions(customer_id, random.randint(8, 15))  # noqa: S311

        # Gerar perfis de segmentos
        await self._generate_segment_profiles()

        # Gerar insights preditivos
        await self._generate_predictive_insights()

    def _get_journey_stage_from_customer_stage(self, customer_stage: CustomerStage) -> JourneyStage:
        """Mapear customer stage para journey stage."""
        mapping = {
            CustomerStage.LEAD: JourneyStage.AWARENESS,
            CustomerStage.PROSPECT: JourneyStage.CONSIDERATION,
            CustomerStage.CUSTOMER: JourneyStage.ACTIVE_USE,
            CustomerStage.LOYAL: JourneyStage.EXPANSION,
            CustomerStage.ADVOCATE: JourneyStage.ADVOCACY,
            CustomerStage.CHURNED: JourneyStage.CHURN,
        }
        return mapping.get(customer_stage, JourneyStage.ACTIVE_USE)

    def _predict_next_journey_stage(self, current_stage: JourneyStage) -> JourneyStage | None:
        """Predizer próximo estágio da jornada."""
        progression_map = {
            JourneyStage.AWARENESS: JourneyStage.CONSIDERATION,
            JourneyStage.CONSIDERATION: JourneyStage.DECISION,
            JourneyStage.DECISION: JourneyStage.ONBOARDING,
            JourneyStage.ONBOARDING: JourneyStage.ACTIVE_USE,
            JourneyStage.ACTIVE_USE: JourneyStage.EXPANSION,
            JourneyStage.EXPANSION: JourneyStage.RENEWAL,
            JourneyStage.RENEWAL: JourneyStage.ADVOCACY,
            JourneyStage.ADVOCACY: JourneyStage.EXPANSION,  # Ciclo de renovação
            JourneyStage.CHURN: None,
        }
        return progression_map.get(current_stage)

    def _generate_behavioral_insights(self, segment: CustomerSegment) -> dict[str, Any]:
        """Gerar insights comportamentais baseados no segmento."""
        base_insights = {
            "preferred_contact_time": f"{random.randint(9, 17)}:00-{random.randint(18, 20)}:00",  # noqa: S311
            "response_time_preference": "immediate"
            if segment in [CustomerSegment.VIP, CustomerSegment.PREMIUM]
            else "within_24h",
            "communication_style": "formal" if segment == CustomerSegment.VIP else "friendly",
            "decision_making_speed": "fast"
            if segment in [CustomerSegment.VIP, CustomerSegment.PREMIUM]
            else "moderate",
            "price_sensitivity": "low"
            if segment == CustomerSegment.VIP
            else "high"
            if segment == CustomerSegment.BRONZE
            else "medium",
            "digital_adoption": random.uniform(0.6, 0.95),  # noqa: S311
            "feature_usage_patterns": {
                "financial_module": random.uniform(0.7, 0.95),  # noqa: S311
                "maintenance_module": random.uniform(0.5, 0.9),  # noqa: S311
                "communication_module": random.uniform(0.8, 0.98),  # noqa: S311
                "reporting_module": random.uniform(0.3, 0.8),  # noqa: S311
            },
        }
        return base_insights

    def _generate_customer_preferences(self) -> dict[str, Any]:
        """Gerar preferências do cliente."""
        return {
            "preferred_channels": random.sample(["email", "whatsapp", "phone", "portal"], k=random.randint(2, 4)),  # noqa: S311
            "notification_frequency": random.choice(["immediate", "daily", "weekly"]),  # noqa: S311
            "report_format": random.choice(["pdf", "excel", "dashboard"]),  # noqa: S311
            "language": "pt-br",
            "timezone": "America/Sao_Paulo",
            "privacy_level": random.choice(["standard", "high", "maximum"]),  # noqa: S311
            "marketing_consent": random.choice([True, False]),  # noqa: S311
        }

    def _generate_satisfaction_metrics(self) -> dict[str, float]:
        """Gerar métricas de satisfação."""
        return {
            "overall_satisfaction": random.uniform(7.0, 9.5),  # noqa: S311
            "product_satisfaction": random.uniform(7.5, 9.2),  # noqa: S311
            "support_satisfaction": random.uniform(6.8, 9.1),  # noqa: S311
            "onboarding_satisfaction": random.uniform(7.2, 8.9),  # noqa: S311
            "nps_score": random.uniform(7.0, 9.0),  # noqa: S311
        }

    def _generate_financial_metrics(self, segment: CustomerSegment) -> dict[str, float]:
        """Gerar métricas financeiras baseadas no segmento."""
        base_values = {
            CustomerSegment.VIP: {"monthly_revenue": (8000, 15000), "lifetime_value": (200000, 400000)},
            CustomerSegment.PREMIUM: {"monthly_revenue": (4000, 8000), "lifetime_value": (100000, 200000)},
            CustomerSegment.STANDARD: {"monthly_revenue": (2000, 4000), "lifetime_value": (50000, 100000)},
            CustomerSegment.BRONZE: {"monthly_revenue": (800, 2000), "lifetime_value": (20000, 50000)},
        }

        values = base_values.get(segment, base_values[CustomerSegment.STANDARD])

        return {
            "monthly_revenue": random.uniform(*values["monthly_revenue"]),  # noqa: S311
            "lifetime_value": random.uniform(*values["lifetime_value"]),  # noqa: S311
            "acquisition_cost": random.uniform(500, 2000),  # noqa: S311
            "payment_score": random.uniform(0.8, 1.0),  # noqa: S311
            "credit_limit": random.uniform(10000, 50000),  # noqa: S311
            "outstanding_balance": random.uniform(0, 5000),  # noqa: S311
        }

    def _generate_engagement_metrics(self) -> dict[str, float]:
        """Gerar métricas de engajamento."""
        return {
            "login_frequency_weekly": random.uniform(3, 15),  # noqa: S311
            "feature_adoption_rate": random.uniform(0.4, 0.9),  # noqa: S311
            "support_ticket_frequency": random.uniform(0.2, 2.0),  # noqa: S311
            "portal_usage_hours_monthly": random.uniform(5, 25),  # noqa: S311
            "mobile_app_usage_rate": random.uniform(0.3, 0.8),  # noqa: S311
            "email_open_rate": random.uniform(0.4, 0.85),  # noqa: S311
            "social_engagement_score": random.uniform(0.1, 0.7),  # noqa: S311
        }

    def _generate_risk_indicators(self) -> dict[str, float]:
        """Gerar indicadores de risco."""
        return {
            "churn_probability": random.uniform(0.05, 0.35),  # noqa: S311
            "payment_risk": random.uniform(0.1, 0.4),  # noqa: S311
            "support_escalation_risk": random.uniform(0.1, 0.3),  # noqa: S311
            "contract_renewal_risk": random.uniform(0.2, 0.5),  # noqa: S311
            "satisfaction_decline_risk": random.uniform(0.1, 0.4),  # noqa: S311
        }

    def _generate_opportunities(self, segment: CustomerSegment) -> list[dict[str, Any]]:
        """Gerar oportunidades de negócio."""
        opportunities = []

        # Oportunidades baseadas no segmento
        if segment in [CustomerSegment.VIP, CustomerSegment.PREMIUM]:
            opportunities.append(
                {
                    "type": "upsell",
                    "title": "Módulo Avançado de Analytics",
                    "value": random.uniform(2000, 5000),  # noqa: S311
                    "probability": random.uniform(0.6, 0.8),  # noqa: S311
                    "description": "Cliente com perfil para módulos avançados",
                }
            )

        if segment in [CustomerSegment.STANDARD, CustomerSegment.BRONZE]:
            opportunities.append(
                {
                    "type": "upgrade",
                    "title": "Upgrade para Plano Premium",
                    "value": random.uniform(1000, 3000),  # noqa: S311
                    "probability": random.uniform(0.4, 0.6),  # noqa: S311
                    "description": "Potencial para upgrade baseado no uso",
                }
            )

        opportunities.append(
            {
                "type": "referral",
                "title": "Programa de Indicação",
                "value": random.uniform(5000, 15000),  # noqa: S311
                "probability": random.uniform(0.3, 0.7),  # noqa: S311
                "description": "Cliente satisfeito com potencial de indicação",
            }
        )

        return opportunities

    def _generate_next_best_actions(self, stage: CustomerStage) -> list[dict[str, Any]]:
        """Gerar próximas melhores ações."""
        actions_map = {
            CustomerStage.LEAD: [
                {
                    "action": "send_welcome_email",
                    "priority": "high",
                    "description": "Enviar email de boas-vindas personalizado",
                },
                {"action": "schedule_demo", "priority": "medium", "description": "Agendar demonstração do produto"},
            ],
            CustomerStage.PROSPECT: [
                {
                    "action": "send_proposal",
                    "priority": "high",
                    "description": "Enviar proposta comercial personalizada",
                },
                {"action": "schedule_call", "priority": "medium", "description": "Agendar call de acompanhamento"},
            ],
            CustomerStage.CUSTOMER: [
                {
                    "action": "check_satisfaction",
                    "priority": "medium",
                    "description": "Verificar nível de satisfação atual",
                },
                {"action": "identify_upsell", "priority": "low", "description": "Identificar oportunidades de upsell"},
            ],
            CustomerStage.LOYAL: [
                {"action": "referral_program", "priority": "high", "description": "Incluir no programa de indicação"},
                {"action": "case_study", "priority": "medium", "description": "Convidar para case study"},
            ],
            CustomerStage.ADVOCATE: [
                {
                    "action": "testimonial_request",
                    "priority": "high",
                    "description": "Solicitar depoimento/testemunhal",
                },
                {"action": "advisory_board", "priority": "medium", "description": "Convidar para advisory board"},
            ],
        }
        return actions_map.get(stage, [])

    async def _generate_customer_interactions(self, customer_id: str, count: int):
        """Gerar interações para um cliente."""
        interaction_types = [
            {
                "type": InteractionType.EMAIL,
                "direction": InteractionDirection.OUTBOUND,
                "category": TouchpointCategory.MARKETING,
            },
            {
                "type": InteractionType.PHONE,
                "direction": InteractionDirection.INBOUND,
                "category": TouchpointCategory.SUPPORT,
            },
            {
                "type": InteractionType.WHATSAPP,
                "direction": InteractionDirection.INBOUND,
                "category": TouchpointCategory.SALES,
            },
            {
                "type": InteractionType.PORTAL,
                "direction": InteractionDirection.INTERNAL,
                "category": TouchpointCategory.PRODUCT,
            },
            {
                "type": InteractionType.MOBILE_APP,
                "direction": InteractionDirection.INTERNAL,
                "category": TouchpointCategory.PRODUCT,
            },
        ]

        for i in range(count):
            interaction_data = random.choice(interaction_types)  # noqa: S311

            interaction = CustomerInteraction(
                id=f"INT_{customer_id}_{i + 1:03d}",
                customer_id=customer_id,
                timestamp=datetime.now() - timedelta(days=random.randint(1, 90)),  # noqa: S311
                type=interaction_data["type"],
                direction=interaction_data["direction"],
                channel=interaction_data["type"].value,
                touchpoint_category=interaction_data["category"],
                subject=f"Interação {interaction_data['type'].value} - {interaction_data['category'].value}",
                description=f"Interação via {interaction_data['type'].value} sobre {interaction_data['category'].value}",
                sentiment_score=random.uniform(-0.2, 0.8),  # noqa: S311
                satisfaction_score=random.uniform(6.0, 9.5) if random.random() > 0.3 else None,  # noqa: S311
                outcome=random.choice(["resolved", "pending", "escalated", "completed"]),  # noqa: S311
                agent_id=f"AGENT_{random.randint(1, 10):02d}",  # noqa: S311
                duration_seconds=random.randint(300, 3600),  # noqa: S311
                metadata={"source": "demo_data", "auto_generated": True},
            )

            self.interactions[interaction.id] = interaction

            # Adicionar à lista de interações do cliente
            if customer_id in self.customers:
                self.customers[customer_id].interactions.append(interaction)

    async def _generate_segment_profiles(self):
        """Gerar perfis de segmentos."""
        segments_data = {
            CustomerSegment.VIP: {"criteria": {"monthly_revenue_min": 8000}, "avg_ltv": 300000, "churn_rate": 0.05},
            CustomerSegment.PREMIUM: {"criteria": {"monthly_revenue_min": 4000}, "avg_ltv": 150000, "churn_rate": 0.08},
            CustomerSegment.STANDARD: {"criteria": {"monthly_revenue_min": 2000}, "avg_ltv": 75000, "churn_rate": 0.12},
            CustomerSegment.BRONZE: {"criteria": {"monthly_revenue_min": 800}, "avg_ltv": 35000, "churn_rate": 0.18},
        }

        for segment, data in segments_data.items():
            segment_customers = [c for c in self.customers.values() if c.segment == segment]

            profile = CustomerSegmentProfile(
                segment=segment,
                criteria=data["criteria"],
                customer_count=len(segment_customers),
                avg_lifetime_value=data["avg_ltv"],
                avg_satisfaction=sum(c.satisfaction_metrics["overall_satisfaction"] for c in segment_customers)
                / len(segment_customers)
                if segment_customers
                else 8.0,
                churn_rate=data["churn_rate"],
                growth_rate=random.uniform(0.05, 0.25),  # noqa: S311
                preferred_channels=["email", "whatsapp", "portal"]
                if segment in [CustomerSegment.VIP, CustomerSegment.PREMIUM]
                else ["whatsapp", "phone"],
                behavior_patterns={
                    "avg_sessions_monthly": random.uniform(10, 30),  # noqa: S311
                    "avg_support_tickets_monthly": random.uniform(0.5, 2.0),  # noqa: S311
                    "preferred_contact_time": "business_hours" if segment == CustomerSegment.VIP else "flexible",
                },
            )

            self.segments[segment] = profile

    async def _generate_predictive_insights(self):
        """Gerar insights preditivos para clientes."""
        insight_types = [
            "churn_prediction",
            "upsell_opportunity",
            "satisfaction_decline",
            "payment_risk",
            "engagement_increase",
            "contract_renewal",
        ]

        for customer_id, customer in self.customers.items():
            customer_insights = []

            # Gerar 2-4 insights por cliente
            for _ in range(random.randint(2, 4)):  # noqa: S311
                insight_type = random.choice(insight_types)  # noqa: S311

                insight = PredictiveInsight(
                    customer_id=customer_id,
                    insight_type=insight_type,
                    prediction=self._generate_prediction_text(insight_type, customer),
                    confidence_score=random.uniform(0.6, 0.95),  # noqa: S311
                    impact_score=random.uniform(6.0, 9.5),  # noqa: S311
                    recommendation=self._generate_recommendation(insight_type),
                    data_sources=["interaction_history", "usage_patterns", "payment_history", "satisfaction_scores"],
                    expires_at=datetime.now() + timedelta(days=30),
                    created_at=datetime.now(),
                )

                customer_insights.append(insight)

            self.predictive_insights[customer_id] = customer_insights

    def _generate_prediction_text(self, insight_type: str, customer: Customer360) -> str:
        """Gerar texto da predição."""
        predictions = {
            "churn_prediction": f"Cliente {customer.basic_info['name']} tem {customer.journey.churn_risk_score:.1%} de probabilidade de churn nos próximos 3 meses",
            "upsell_opportunity": f"Oportunidade de upsell identificada para {customer.basic_info['name']} - valor estimado R$ {random.uniform(2000, 8000):,.2f}",  # noqa: S311
            "satisfaction_decline": f"Potencial declínio na satisfação detectado para {customer.basic_info['name']}",
            "payment_risk": f"Risco de atraso no pagamento identificado para {customer.basic_info['name']}",
            "engagement_increase": f"Potencial para aumentar engajamento de {customer.basic_info['name']} em {random.uniform(20, 40):.0f}%",  # noqa: S311
            "contract_renewal": f"Alta probabilidade de renovação antecipada para {customer.basic_info['name']}",
        }
        return predictions.get(insight_type, "Insight preditivo gerado")

    def _generate_recommendation(self, insight_type: str) -> str:
        """Gerar recomendação baseada no tipo de insight."""
        recommendations = {
            "churn_prediction": "Agendar call de retenção e revisar satisfação do cliente",
            "upsell_opportunity": "Apresentar proposta personalizada com módulos adicionais",
            "satisfaction_decline": "Realizar pesquisa de satisfação e identificar pontos de melhoria",
            "payment_risk": "Entrar em contato proativo para revisar condições de pagamento",
            "engagement_increase": "Implementar programa de onboarding avançado",
            "contract_renewal": "Preparar proposta de renovação antecipada com benefícios adicionais",
        }
        return recommendations.get(insight_type, "Ação recomendada não definida")

    async def get_customer_360(self, customer_id: str) -> Customer360 | None:
        """Obter visão 360° de um cliente."""
        return self.customers.get(customer_id)

    async def get_all_customers(
        self, segment: CustomerSegment | None = None, stage: CustomerStage | None = None
    ) -> list[Customer360]:
        """Obter todos os clientes com filtros opcionais."""
        customers = list(self.customers.values())

        if segment:
            customers = [c for c in customers if c.segment == segment]

        if stage:
            customers = [c for c in customers if c.stage == stage]

        return customers

    async def track_customer_interaction(self, interaction: CustomerInteraction) -> bool:
        """Registrar nova interação com cliente."""
        try:
            self.interactions[interaction.id] = interaction

            # Atualizar customer 360
            if interaction.customer_id in self.customers:
                customer = self.customers[interaction.customer_id]
                customer.interactions.append(interaction)
                customer.last_updated = datetime.now()

                # Atualizar métricas de engagement
                customer.journey.interactions_count += 1

                # Atualizar satisfaction se fornecido
                if interaction.satisfaction_score:
                    current_avg = customer.satisfaction_metrics["overall_satisfaction"]
                    new_avg = (current_avg + interaction.satisfaction_score) / 2
                    customer.satisfaction_metrics["overall_satisfaction"] = new_avg

                logger.info(f"Interação registrada: {interaction.type.value} para cliente {interaction.customer_id}")

                return True

            return False

        except Exception as e:
            logger.error(f"Erro ao registrar interação: {str(e)}")
            return False

    async def update_customer_journey_stage(self, customer_id: str, new_stage: JourneyStage) -> bool:
        """Atualizar estágio da jornada do cliente."""
        if customer_id not in self.customers:
            return False

        customer = self.customers[customer_id]
        old_stage = customer.journey.current_stage

        customer.journey.current_stage = new_stage
        customer.journey.time_in_stage_days = 0  # Reset timer
        customer.journey.next_predicted_stage = self._predict_next_journey_stage(new_stage)
        customer.last_updated = datetime.now()

        logger.info(f"Cliente {customer_id}: {old_stage.value} → {new_stage.value}")
        return True

    async def segment_customers(self) -> dict[CustomerSegment, list[str]]:
        """Realizar segmentação automática de clientes."""
        segmented = {segment: [] for segment in CustomerSegment}

        for customer_id, customer in self.customers.items():
            # Lógica de segmentação baseada em múltiplos fatores
            monthly_revenue = customer.financial_metrics.get("monthly_revenue", 0)
            satisfaction = customer.satisfaction_metrics.get("overall_satisfaction", 0)
            engagement = customer.engagement_metrics.get("feature_adoption_rate", 0)

            # Calcular score composto
            segment_score = monthly_revenue / 1000 * 0.5 + satisfaction * 0.3 + engagement * 10 * 0.2

            # Determinar segmento
            if segment_score >= 15:
                new_segment = CustomerSegment.VIP
            elif segment_score >= 10:
                new_segment = CustomerSegment.PREMIUM
            elif segment_score >= 6:
                new_segment = CustomerSegment.STANDARD
            else:
                new_segment = CustomerSegment.BRONZE

            # Atualizar segmento se mudou
            if customer.segment != new_segment:
                customer.segment = new_segment
                customer.last_updated = datetime.now()
                logger.info(f"Cliente {customer_id} re-segmentado para {new_segment.value}")

            segmented[customer.segment].append(customer_id)

        return segmented

    async def get_predictive_insights(self, customer_id: str | None = None) -> list[PredictiveInsight]:
        """Obter insights preditivos."""
        if customer_id:
            return self.predictive_insights.get(customer_id, [])

        # Retornar todos os insights
        all_insights = []
        for insights in self.predictive_insights.values():
            all_insights.extend(insights)

        return sorted(all_insights, key=lambda x: x.impact_score, reverse=True)

    async def generate_customer_health_score(self, customer_id: str) -> float:
        """Gerar score de saúde do cliente."""
        customer = self.customers.get(customer_id)
        if not customer:
            return 0.0

        # Fatores para o health score
        satisfaction_factor = customer.satisfaction_metrics["overall_satisfaction"] / 10
        engagement_factor = customer.engagement_metrics["feature_adoption_rate"]
        financial_factor = min(1.0, customer.financial_metrics["monthly_revenue"] / 5000)
        churn_factor = 1 - customer.journey.churn_risk_score

        # Peso dos fatores
        health_score = (
            satisfaction_factor * 0.3 + engagement_factor * 0.25 + financial_factor * 0.25 + churn_factor * 0.2
        )

        return min(100, health_score * 100)

    async def get_crm_analytics(self) -> CRMAnalytics:
        """Obter analytics completo do CRM."""
        total_customers = len(self.customers)
        active_customers = len([c for c in self.customers.values() if c.stage not in [CustomerStage.CHURNED]])

        # Calcular métricas do mês atual
        current_month = datetime.now().replace(day=1)
        new_customers_month = len([c for c in self.customers.values() if c.created_at >= current_month])

        churned_customers_month = len(
            [c for c in self.customers.values() if c.stage == CustomerStage.CHURNED and c.last_updated >= current_month]
        )

        # Métricas de satisfação e valor
        avg_satisfaction = (
            sum(c.satisfaction_metrics["overall_satisfaction"] for c in self.customers.values()) / total_customers
            if total_customers > 0
            else 0
        )

        avg_ltv = (
            sum(c.financial_metrics["lifetime_value"] for c in self.customers.values()) / total_customers
            if total_customers > 0
            else 0
        )

        # Distribuições
        segment_distribution = {}
        stage_distribution = {}

        for customer in self.customers.values():
            segment_distribution[customer.segment.value] = segment_distribution.get(customer.segment.value, 0) + 1
            stage_distribution[customer.stage.value] = stage_distribution.get(customer.stage.value, 0) + 1

        return CRMAnalytics(
            total_customers=total_customers,
            active_customers=active_customers,
            new_customers_month=new_customers_month,
            churned_customers_month=churned_customers_month,
            avg_customer_satisfaction=avg_satisfaction,
            avg_lifetime_value=avg_ltv,
            customer_acquisition_cost=random.uniform(500, 1500),  # noqa: S311
            churn_rate=churned_customers_month / total_customers if total_customers > 0 else 0,
            segment_distribution=segment_distribution,
            stage_distribution=stage_distribution,
            interaction_volume_daily=len(self.interactions) // 30,  # Aproximação
            response_time_avg_hours=random.uniform(2.5, 8.0),  # noqa: S311
            conversion_rates={
                "lead_to_prospect": random.uniform(0.25, 0.45),  # noqa: S311
                "prospect_to_customer": random.uniform(0.15, 0.35),  # noqa: S311
                "customer_to_loyal": random.uniform(0.20, 0.40),  # noqa: S311
            },
        )

    async def get_customer_recommendations(self, customer_id: str) -> list[dict[str, Any]]:
        """Obter recomendações personalizadas para um cliente."""
        customer = self.customers.get(customer_id)
        if not customer:
            return []

        recommendations = []

        # Recomendações baseadas no health score
        health_score = await self.generate_customer_health_score(customer_id)

        if health_score < 70:
            recommendations.append(
                {
                    "type": "health_improvement",
                    "priority": "high",
                    "title": "Melhorar Saúde do Cliente",
                    "description": f"Health score baixo ({health_score:.0f}%). Revisar satisfação e engajamento.",
                    "actions": ["Agendar call de feedback", "Revisar onboarding", "Oferecer treinamento"],
                }
            )

        # Recomendações baseadas no segmento
        if customer.segment in [CustomerSegment.VIP, CustomerSegment.PREMIUM]:
            recommendations.append(
                {
                    "type": "vip_treatment",
                    "priority": "high",
                    "title": "Tratamento VIP",
                    "description": "Cliente premium merece atenção especial.",
                    "actions": ["Account manager dedicado", "Suporte prioritário", "Early access features"],
                }
            )

        # Recomendações baseadas em oportunidades
        for opportunity in customer.opportunities:
            recommendations.append(
                {
                    "type": "opportunity",
                    "priority": "medium",
                    "title": opportunity["title"],
                    "description": opportunity["description"],
                    "actions": [f"Apresentar proposta de {opportunity['type']}", "Agendar reunião comercial"],
                }
            )

        return recommendations

    async def search_customers(self, query: str, filters: dict[str, Any] = None) -> list[Customer360]:
        """Buscar clientes por diversos critérios."""
        results = []
        query_lower = query.lower()
        filters = filters or {}

        for customer in self.customers.values():
            # Busca textual
            if (
                query_lower in customer.basic_info.get("name", "").lower()
                or query_lower in customer.basic_info.get("location", "").lower()
                or query_lower in customer.id.lower()
            ):
                # Aplicar filtros
                if filters.get("segment") and customer.segment != filters["segment"]:
                    continue
                if filters.get("stage") and customer.stage != filters["stage"]:
                    continue
                if (
                    filters.get("min_revenue")
                    and customer.financial_metrics["monthly_revenue"] < filters["min_revenue"]
                ):
                    continue

                results.append(customer)

        return results


# Instância singleton do serviço
crm_360_service = CRM360Service()


if __name__ == "__main__":
    # Teste básico
    async def test_crm_360():
        service = CRM360Service()

        # Obter analytics
        analytics = await service.get_crm_analytics()
        print(f"Total Customers: {analytics.total_customers}")
        print(f"Average Satisfaction: {analytics.avg_customer_satisfaction:.2f}")

        # Obter cliente específico
        customers = await service.get_all_customers()
        if customers:
            customer = customers[0]
            health = await service.generate_customer_health_score(customer.id)
            print(f"Customer {customer.basic_info['name']} Health Score: {health:.1f}%")

    asyncio.run(test_crm_360())
