"""Sistema de scoring de leads com ML."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.ml.registry.model_registry import (
    ModelFramework,
    ModelRegistry,
    ModelStage,
    ModelType,
)
from modules.analytics.ml.training.training_pipeline import (
    TrainingConfig,
    TrainingPipeline,
)

logger = logging.getLogger(__name__)


class LeadQuality(Enum):
    """Qualidade do lead."""

    HOT = "hot"
    WARM = "warm"
    LUKEWARM = "lukewarm"
    COLD = "cold"
    UNQUALIFIED = "unqualified"


class LeadStage(Enum):
    """Estágio do lead no funil."""

    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"


class ConversionProbability(Enum):
    """Probabilidade de conversão."""

    VERY_HIGH = "very_high"  # >80%
    HIGH = "high"  # 60-80%
    MEDIUM = "medium"  # 40-60%
    LOW = "low"  # 20-40%
    VERY_LOW = "very_low"  # <20%


@dataclass
class ScoreFactor:
    """Fator que contribui para o score."""

    name: str
    value: Any
    score_impact: float  # -100 a +100
    weight: float  # 0 a 1
    category: str  # demographic, behavioral, engagement, firmographic
    description: str


@dataclass
class LeadInsight:
    """Insight sobre o lead."""

    insight_type: str
    title: str
    description: str
    action_recommended: str
    priority: int  # 1-5
    confidence: float


@dataclass
class LeadScore:
    """Score completo de um lead."""

    id: UUID
    lead_id: str
    total_score: float  # 0-100
    quality: LeadQuality
    conversion_probability: float
    conversion_level: ConversionProbability
    stage: LeadStage
    factors: list[ScoreFactor]
    insights: list[LeadInsight]
    next_best_action: str
    estimated_value: float
    time_to_conversion: int | None  # dias
    model_version: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScoringAnalytics:
    """Analytics de scoring."""

    period_start: datetime
    period_end: datetime
    total_leads_scored: int
    average_score: float
    score_distribution: dict[str, int]
    quality_distribution: dict[str, int]
    conversion_rate_by_score: dict[str, float]
    top_scoring_factors: list[dict[str, Any]]
    model_accuracy: float
    pipeline_value: float


class LeadScorer:
    """
    Sistema de scoring de leads.

    Funcionalidades:
    - Scoring preditivo com ML
    - Qualificação automática
    - Identificação de fatores
    - Recomendação de próxima ação
    - Estimativa de valor e tempo
    """

    # Features para scoring
    LEAD_FEATURES = [
        "company_size",
        "industry_fit",
        "budget_range",
        "decision_timeline",
        "website_visits",
        "page_views",
        "time_on_site",
        "email_opens",
        "email_clicks",
        "content_downloads",
        "demo_requests",
        "form_submissions",
        "social_engagement",
        "event_attendance",
        "product_interest_score",
    ]

    # Pesos por categoria
    CATEGORY_WEIGHTS = {
        "demographic": 0.20,
        "firmographic": 0.25,
        "behavioral": 0.30,
        "engagement": 0.25,
    }

    # Thresholds de qualidade
    QUALITY_THRESHOLDS = {
        LeadQuality.HOT: 80,
        LeadQuality.WARM: 60,
        LeadQuality.LUKEWARM: 40,
        LeadQuality.COLD: 20,
        LeadQuality.UNQUALIFIED: 0,
    }

    def __init__(
        self,
        model_registry: ModelRegistry | None = None,
    ) -> None:
        """
        Inicializa o Lead Scorer.

        Args:
            model_registry: Registry de modelos
        """
        self.model_registry = model_registry or ModelRegistry()
        self.training_pipeline = TrainingPipeline(self.model_registry)
        self._model = None
        self._model_version = None

    async def score_lead(
        self,
        db: AsyncSession,
        lead_data: dict[str, Any],
    ) -> LeadScore:
        """
        Calcula score de um lead.

        Args:
            db: Sessão do banco
            lead_data: Dados do lead

        Returns:
            LeadScore com análise completa
        """
        lead_id = lead_data.get("id", str(uuid4()))
        logger.info(f"Scoring lead: {lead_id}")

        # Extrair features
        features = self._extract_features(lead_data)

        # Calcular scores por categoria
        demographic_score = self._calculate_demographic_score(lead_data)
        firmographic_score = self._calculate_firmographic_score(lead_data)
        behavioral_score = self._calculate_behavioral_score(lead_data)
        engagement_score = self._calculate_engagement_score(lead_data)

        # Coletar fatores
        factors = []
        factors.extend(self._get_demographic_factors(lead_data))
        factors.extend(self._get_firmographic_factors(lead_data))
        factors.extend(self._get_behavioral_factors(lead_data))
        factors.extend(self._get_engagement_factors(lead_data))

        # Score ponderado
        total_score = (
            demographic_score * self.CATEGORY_WEIGHTS["demographic"]
            + firmographic_score * self.CATEGORY_WEIGHTS["firmographic"]
            + behavioral_score * self.CATEGORY_WEIGHTS["behavioral"]
            + engagement_score * self.CATEGORY_WEIGHTS["engagement"]
        )

        # Ajuste com modelo ML se disponível
        model = self._load_model()
        if model:
            ml_score = self._predict_with_model(model, features)
            total_score = total_score * 0.4 + ml_score * 100 * 0.6

        total_score = min(100, max(0, total_score))

        # Classificar qualidade
        quality = self._classify_quality(total_score)

        # Calcular probabilidade de conversão
        conversion_prob = self._calculate_conversion_probability(total_score, lead_data)
        conversion_level = self._classify_conversion_level(conversion_prob)

        # Identificar estágio no funil
        stage = self._identify_stage(lead_data)

        # Gerar insights
        insights = self._generate_insights(quality, factors, lead_data, conversion_prob)

        # Próxima melhor ação
        next_action = self._determine_next_action(quality, stage, insights)

        # Estimativas
        estimated_value = self._estimate_deal_value(lead_data)
        time_to_conversion = self._estimate_time_to_conversion(stage, conversion_prob)

        return LeadScore(
            id=uuid4(),
            lead_id=lead_id,
            total_score=round(total_score, 2),
            quality=quality,
            conversion_probability=round(conversion_prob, 4),
            conversion_level=conversion_level,
            stage=stage,
            factors=factors,
            insights=insights,
            next_best_action=next_action,
            estimated_value=estimated_value,
            time_to_conversion=time_to_conversion,
            model_version=self._model_version or "rules_v1",
        )

    async def score_leads_batch(
        self,
        db: AsyncSession,
        leads: list[dict[str, Any]],
    ) -> list[LeadScore]:
        """
        Score múltiplos leads em batch.

        Args:
            db: Sessão do banco
            leads: Lista de dados de leads

        Returns:
            Lista de scores
        """
        scores = []
        for lead in leads:
            try:
                score = await self.score_lead(db, lead)
                scores.append(score)
            except Exception as e:
                logger.error(f"Erro ao scorar lead {lead.get('id')}: {e}")
        return scores

    async def get_top_leads(
        self,
        db: AsyncSession,
        limit: int = 50,
        min_quality: LeadQuality = LeadQuality.WARM,
    ) -> list[LeadScore]:
        """
        Obtém leads com melhor score.

        Args:
            db: Sessão do banco
            limit: Máximo de leads
            min_quality: Qualidade mínima

        Returns:
            Lista de leads ordenados
        """
        # Em produção, buscaria do banco
        # Simulação com leads sintéticos
        sample_leads = self._generate_sample_leads(limit * 2)
        scores = await self.score_leads_batch(db, sample_leads)

        # Filtrar por qualidade
        quality_order = list(LeadQuality)
        min_index = quality_order.index(min_quality)

        filtered = [s for s in scores if quality_order.index(s.quality) <= min_index]

        # Ordenar por score
        filtered.sort(key=lambda x: x.total_score, reverse=True)
        return filtered[:limit]

    async def get_scoring_analytics(
        self,
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> ScoringAnalytics:
        """
        Obtém analytics de scoring.

        Args:
            db: Sessão do banco
            start_date: Data inicial
            end_date: Data final

        Returns:
            ScoringAnalytics com métricas
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=30))

        # Simulação para desenvolvimento
        sample_leads = self._generate_sample_leads(200)
        scores = await self.score_leads_batch(db, sample_leads)

        # Score distribution
        score_dist = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
        for score in scores:
            if score.total_score < 20:
                score_dist["0-20"] += 1
            elif score.total_score < 40:
                score_dist["20-40"] += 1
            elif score.total_score < 60:
                score_dist["40-60"] += 1
            elif score.total_score < 80:
                score_dist["60-80"] += 1
            else:
                score_dist["80-100"] += 1

        # Quality distribution
        quality_dist = {q.value: 0 for q in LeadQuality}
        for score in scores:
            quality_dist[score.quality.value] += 1

        # Top factors
        all_factors = []
        for score in scores:
            all_factors.extend(score.factors)

        factor_impacts = {}
        for f in all_factors:
            if f.name not in factor_impacts:
                factor_impacts[f.name] = []
            factor_impacts[f.name].append(f.score_impact)

        top_factors = [
            {
                "factor": name,
                "avg_impact": round(np.mean(impacts), 2),
                "frequency": len(impacts),
            }
            for name, impacts in sorted(factor_impacts.items(), key=lambda x: abs(np.mean(x[1])), reverse=True)[:5]
        ]

        # Pipeline value
        pipeline_value = sum(s.estimated_value for s in scores)

        return ScoringAnalytics(
            period_start=start_date,
            period_end=end_date,
            total_leads_scored=len(scores),
            average_score=round(np.mean([s.total_score for s in scores]), 2),
            score_distribution=score_dist,
            quality_distribution=quality_dist,
            conversion_rate_by_score={
                "0-20": 2.5,
                "20-40": 8.0,
                "40-60": 18.5,
                "60-80": 35.0,
                "80-100": 62.0,
            },
            top_scoring_factors=top_factors,
            model_accuracy=85.5,
            pipeline_value=round(pipeline_value, 2),
        )

    async def train_model(
        self,
        db: AsyncSession,
        training_data: pd.DataFrame | None = None,
        version: str = "1.0.0",
    ) -> dict[str, Any]:
        """
        Treina modelo de lead scoring.

        Args:
            db: Sessão do banco
            training_data: Dados de treinamento
            version: Versão do modelo

        Returns:
            Resultado do treinamento
        """
        logger.info("Treinando modelo de lead scoring")

        if training_data is None:
            training_data = self._generate_training_data()

        config = TrainingConfig(
            model_name="lead_scorer",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            target_column="converted",
            feature_columns=self.LEAD_FEATURES,
            test_size=0.2,
            val_size=0.1,
            cv_folds=5,
            metrics=["accuracy", "precision", "recall", "f1_score", "auc_roc"],
        )

        self.training_pipeline.prepare_data(training_data, config)

        models = [
            ("logistic", LogisticRegression(max_iter=1000)),
            ("random_forest", RandomForestClassifier(n_estimators=100)),
            ("gradient_boosting", GradientBoostingClassifier(n_estimators=100)),
        ]

        results = self.training_pipeline.train_with_automl(training_data, config, models, version)

        if results and results[0].status == "success":
            self.model_registry.promote_model(
                name="lead_scorer",
                version=version,
                target_stage=ModelStage.PRODUCTION,
            )
            self._model = None
            self._model_version = version

        return {
            "status": "success" if results else "failed",
            "metrics": results[0].metrics.to_dict() if results else {},
            "version": version,
        }

    def _extract_features(self, lead_data: dict) -> dict[str, float]:
        """Extrai features do lead."""
        features = {}
        for feature in self.LEAD_FEATURES:
            features[feature] = lead_data.get(feature, 0)
        return features

    def _calculate_demographic_score(self, lead_data: dict) -> float:
        """Calcula score demográfico."""
        score = 50  # Base

        # Título do cargo
        title = lead_data.get("title", "").lower()
        if any(t in title for t in ["ceo", "cto", "cfo", "director", "vp"]):
            score += 30
        elif any(t in title for t in ["manager", "head", "lead"]):
            score += 20
        elif any(t in title for t in ["analyst", "specialist"]):
            score += 10

        # Região
        if lead_data.get("region") in ["SP", "RJ", "MG"]:
            score += 10

        return min(100, score)

    def _calculate_firmographic_score(self, lead_data: dict) -> float:
        """Calcula score firmográfico."""
        score = 50

        # Tamanho da empresa
        company_size = lead_data.get("company_size", 0)
        if company_size > 500:
            score += 30
        elif company_size > 100:
            score += 20
        elif company_size > 20:
            score += 10

        # Indústria
        industry_fit = lead_data.get("industry_fit", 0.5)
        score += industry_fit * 20

        # Budget
        budget = lead_data.get("budget_range", 0)
        if budget > 50000:
            score += 20
        elif budget > 20000:
            score += 10

        return min(100, score)

    def _calculate_behavioral_score(self, lead_data: dict) -> float:
        """Calcula score comportamental."""
        score = 30

        # Visitas ao site
        visits = lead_data.get("website_visits", 0)
        score += min(20, visits * 2)

        # Page views
        page_views = lead_data.get("page_views", 0)
        score += min(15, page_views)

        # Tempo no site
        time_on_site = lead_data.get("time_on_site", 0)
        score += min(15, time_on_site / 60)  # minutos

        # Downloads
        downloads = lead_data.get("content_downloads", 0)
        score += min(20, downloads * 5)

        return min(100, score)

    def _calculate_engagement_score(self, lead_data: dict) -> float:
        """Calcula score de engagement."""
        score = 30

        # Email
        opens = lead_data.get("email_opens", 0)
        clicks = lead_data.get("email_clicks", 0)
        score += min(20, opens * 2)
        score += min(20, clicks * 5)

        # Demos
        demos = lead_data.get("demo_requests", 0)
        score += min(20, demos * 10)

        # Forms
        forms = lead_data.get("form_submissions", 0)
        score += min(10, forms * 3)

        return min(100, score)

    def _get_demographic_factors(self, lead_data: dict) -> list[ScoreFactor]:
        """Obtém fatores demográficos."""
        factors = []

        title = lead_data.get("title", "")
        if title:
            impact = 0
            if any(t in title.lower() for t in ["ceo", "cto", "director"]):
                impact = 30
            elif any(t in title.lower() for t in ["manager", "lead"]):
                impact = 15

            factors.append(
                ScoreFactor(
                    name="job_title",
                    value=title,
                    score_impact=impact,
                    weight=0.15,
                    category="demographic",
                    description=f"Cargo: {title}",
                )
            )

        return factors

    def _get_firmographic_factors(self, lead_data: dict) -> list[ScoreFactor]:
        """Obtém fatores firmográficos."""
        factors = []

        company_size = lead_data.get("company_size", 0)
        size_impact = 0
        if company_size > 500:
            size_impact = 30
        elif company_size > 100:
            size_impact = 20
        elif company_size > 20:
            size_impact = 10

        factors.append(
            ScoreFactor(
                name="company_size",
                value=company_size,
                score_impact=size_impact,
                weight=0.2,
                category="firmographic",
                description=f"Empresa com {company_size} funcionários",
            )
        )

        budget = lead_data.get("budget_range", 0)
        if budget > 0:
            budget_impact = min(25, budget / 2000)
            factors.append(
                ScoreFactor(
                    name="budget_range",
                    value=budget,
                    score_impact=budget_impact,
                    weight=0.15,
                    category="firmographic",
                    description=f"Budget: R$ {budget:,.0f}",
                )
            )

        return factors

    def _get_behavioral_factors(self, lead_data: dict) -> list[ScoreFactor]:
        """Obtém fatores comportamentais."""
        factors = []

        visits = lead_data.get("website_visits", 0)
        if visits > 0:
            factors.append(
                ScoreFactor(
                    name="website_visits",
                    value=visits,
                    score_impact=min(20, visits * 2),
                    weight=0.1,
                    category="behavioral",
                    description=f"{visits} visitas ao site",
                )
            )

        downloads = lead_data.get("content_downloads", 0)
        if downloads > 0:
            factors.append(
                ScoreFactor(
                    name="content_downloads",
                    value=downloads,
                    score_impact=min(25, downloads * 5),
                    weight=0.15,
                    category="behavioral",
                    description=f"{downloads} downloads de conteúdo",
                )
            )

        return factors

    def _get_engagement_factors(self, lead_data: dict) -> list[ScoreFactor]:
        """Obtém fatores de engagement."""
        factors = []

        demos = lead_data.get("demo_requests", 0)
        if demos > 0:
            factors.append(
                ScoreFactor(
                    name="demo_requests",
                    value=demos,
                    score_impact=min(30, demos * 15),
                    weight=0.2,
                    category="engagement",
                    description=f"{demos} solicitação(ões) de demo",
                )
            )

        email_clicks = lead_data.get("email_clicks", 0)
        if email_clicks > 0:
            factors.append(
                ScoreFactor(
                    name="email_clicks",
                    value=email_clicks,
                    score_impact=min(20, email_clicks * 4),
                    weight=0.1,
                    category="engagement",
                    description=f"{email_clicks} cliques em emails",
                )
            )

        return factors

    def _classify_quality(self, score: float) -> LeadQuality:
        """Classifica qualidade do lead."""
        for quality, threshold in self.QUALITY_THRESHOLDS.items():
            if score >= threshold:
                return quality
        return LeadQuality.UNQUALIFIED

    def _calculate_conversion_probability(
        self,
        score: float,
        lead_data: dict,
    ) -> float:
        """Calcula probabilidade de conversão."""
        # Base probability from score
        base_prob = score / 100 * 0.7

        # Ajustes
        if lead_data.get("demo_requests", 0) > 0:
            base_prob += 0.15

        if lead_data.get("decision_timeline", "") == "immediate":
            base_prob += 0.1

        return min(0.95, base_prob)

    def _classify_conversion_level(self, prob: float) -> ConversionProbability:
        """Classifica nível de probabilidade de conversão."""
        if prob >= 0.8:
            return ConversionProbability.VERY_HIGH
        elif prob >= 0.6:
            return ConversionProbability.HIGH
        elif prob >= 0.4:
            return ConversionProbability.MEDIUM
        elif prob >= 0.2:
            return ConversionProbability.LOW
        return ConversionProbability.VERY_LOW

    def _identify_stage(self, lead_data: dict) -> LeadStage:
        """Identifica estágio no funil."""
        demos = lead_data.get("demo_requests", 0)
        downloads = lead_data.get("content_downloads", 0)
        visits = lead_data.get("website_visits", 0)

        if demos > 0:
            return LeadStage.EVALUATION
        elif downloads > 2:
            return LeadStage.CONSIDERATION
        elif downloads > 0 or visits > 5:
            return LeadStage.INTEREST
        elif visits > 0:
            return LeadStage.AWARENESS
        return LeadStage.AWARENESS

    def _generate_insights(
        self,
        quality: LeadQuality,
        factors: list[ScoreFactor],
        lead_data: dict,
        conversion_prob: float,
    ) -> list[LeadInsight]:
        """Gera insights sobre o lead."""
        insights = []

        # Insight de qualidade
        if quality in [LeadQuality.HOT, LeadQuality.WARM]:
            insights.append(
                LeadInsight(
                    insight_type="quality",
                    title="Lead qualificado",
                    description=f"Este lead tem alta qualificação ({quality.value})",
                    action_recommended="Priorizar contato imediato",
                    priority=1,
                    confidence=0.9,
                )
            )

        # Insight de engagement
        if lead_data.get("demo_requests", 0) > 0:
            insights.append(
                LeadInsight(
                    insight_type="engagement",
                    title="Alto interesse demonstrado",
                    description="Lead solicitou demonstração do produto",
                    action_recommended="Agendar demo o mais rápido possível",
                    priority=1,
                    confidence=0.95,
                )
            )

        # Insight de timing
        timeline = lead_data.get("decision_timeline", "")
        if timeline == "immediate":
            insights.append(
                LeadInsight(
                    insight_type="timing",
                    title="Decisão urgente",
                    description="Lead indicou necessidade imediata",
                    action_recommended="Acelerar processo de vendas",
                    priority=1,
                    confidence=0.85,
                )
            )

        # Insight de budget
        budget = lead_data.get("budget_range", 0)
        if budget > 50000:
            insights.append(
                LeadInsight(
                    insight_type="value",
                    title="Alto potencial de valor",
                    description=f"Budget indicado: R$ {budget:,.0f}",
                    action_recommended="Preparar proposta premium",
                    priority=2,
                    confidence=0.8,
                )
            )

        # Gaps
        if lead_data.get("content_downloads", 0) == 0:
            insights.append(
                LeadInsight(
                    insight_type="gap",
                    title="Baixo consumo de conteúdo",
                    description="Lead não baixou nenhum material",
                    action_recommended="Enviar conteúdo relevante",
                    priority=3,
                    confidence=0.7,
                )
            )

        return insights

    def _determine_next_action(
        self,
        quality: LeadQuality,
        stage: LeadStage,
        insights: list[LeadInsight],
    ) -> str:
        """Determina próxima melhor ação."""
        if quality == LeadQuality.HOT:
            return "Agendar call de fechamento"
        elif quality == LeadQuality.WARM:
            if stage == LeadStage.EVALUATION:
                return "Enviar proposta comercial"
            else:
                return "Agendar demonstração personalizada"
        elif quality == LeadQuality.LUKEWARM:
            return "Enviar conteúdo educacional relevante"
        elif quality == LeadQuality.COLD:
            return "Incluir em nurturing automation"
        else:
            return "Manter em lista de nutrição passiva"

    def _estimate_deal_value(self, lead_data: dict) -> float:
        """Estima valor potencial do deal."""
        base_value = 10000

        # Ajuste por tamanho da empresa
        company_size = lead_data.get("company_size", 0)
        size_multiplier = 1 + (company_size / 100) * 0.5

        # Ajuste por budget
        budget = lead_data.get("budget_range", 0)
        if budget > 0:
            return min(budget, base_value * size_multiplier * 2)

        return base_value * size_multiplier

    def _estimate_time_to_conversion(
        self,
        stage: LeadStage,
        conversion_prob: float,
    ) -> int | None:
        """Estima tempo até conversão em dias."""
        stage_times = {
            LeadStage.AWARENESS: 90,
            LeadStage.INTEREST: 60,
            LeadStage.CONSIDERATION: 45,
            LeadStage.INTENT: 30,
            LeadStage.EVALUATION: 14,
            LeadStage.PURCHASE: 7,
        }

        base_time = stage_times.get(stage, 60)

        # Ajuste por probabilidade
        if conversion_prob > 0.7:
            return int(base_time * 0.6)
        elif conversion_prob > 0.5:
            return int(base_time * 0.8)
        return base_time

    def _load_model(self) -> Any | None:
        """Carrega modelo de produção."""
        if self._model is None:
            self._model = self.model_registry.get_production_model("lead_scorer")
            if self._model:
                version = self.model_registry.get_model_version("lead_scorer", stage=ModelStage.PRODUCTION)
                self._model_version = version.version if version else None
        return self._model

    def _predict_with_model(
        self,
        model: Any,
        features: dict,
    ) -> float:
        """Faz predição com modelo ML."""
        x_features = pd.DataFrame([features])
        if hasattr(model, "predict_proba"):
            return model.predict_proba(x_features)[0][1]
        return model.predict(x_features)[0]

    def _generate_sample_leads(self, n: int) -> list[dict]:
        """Gera leads de exemplo."""
        np.random.seed(42)
        leads = []

        for i in range(n):
            leads.append(
                {
                    "id": f"lead_{i}",
                    "title": np.random.choice(["CEO", "CTO", "Manager", "Analyst", "Director"]),
                    "company_size": np.random.randint(10, 1000),
                    "industry_fit": np.random.uniform(0.3, 1.0),
                    "budget_range": np.random.randint(5000, 100000),
                    "decision_timeline": np.random.choice(["immediate", "1-3 months", "6+ months"]),
                    "website_visits": np.random.randint(0, 20),
                    "page_views": np.random.randint(0, 50),
                    "time_on_site": np.random.randint(0, 600),
                    "email_opens": np.random.randint(0, 10),
                    "email_clicks": np.random.randint(0, 5),
                    "content_downloads": np.random.randint(0, 5),
                    "demo_requests": np.random.randint(0, 2),
                    "form_submissions": np.random.randint(0, 3),
                    "social_engagement": np.random.randint(0, 10),
                    "event_attendance": np.random.randint(0, 2),
                    "product_interest_score": np.random.uniform(0, 1),
                }
            )

        return leads

    def _generate_training_data(self, n: int = 1000) -> pd.DataFrame:
        """Gera dados de treinamento sintéticos."""
        leads = self._generate_sample_leads(n)
        df = pd.DataFrame(leads)

        # Adicionar coluna target
        df["converted"] = 0

        # Simular conversões baseado em features
        high_score_mask = (df["demo_requests"] > 0) & (df["company_size"] > 100) & (df["budget_range"] > 30000)
        df.loc[high_score_mask, "converted"] = np.random.binomial(1, 0.7, high_score_mask.sum())

        medium_mask = (df["content_downloads"] > 2) & (df["website_visits"] > 5)
        df.loc[medium_mask & ~high_score_mask, "converted"] = np.random.binomial(
            1, 0.3, (medium_mask & ~high_score_mask).sum()
        )

        return df
