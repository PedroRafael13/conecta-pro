"""Engine de A/B Testing para notificações."""

import hashlib
import logging
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    """Status do experimento."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Tipos de métricas."""

    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION_RATE = "conversion_rate"
    RESPONSE_TIME = "response_time"
    UNSUBSCRIBE_RATE = "unsubscribe_rate"


@dataclass
class ExperimentVariant:
    """Variante de um experimento."""

    variant_id: str
    name: str
    description: str
    weight: float = 0.5
    is_control: bool = False
    config: dict[str, Any] = field(default_factory=dict)

    # Métricas acumuladas
    impressions: int = 0
    opens: int = 0
    clicks: int = 0
    conversions: int = 0
    unsubscribes: int = 0


@dataclass
class StatisticalSignificance:
    """Resultado de significância estatística."""

    is_significant: bool
    confidence_level: float
    p_value: float
    lift_percentage: float
    sample_size_needed: int
    current_sample_size: int
    power: float


@dataclass
class ExperimentResult:
    """Resultado de um experimento."""

    experiment_id: UUID
    winning_variant: Optional[str]
    variants_results: dict[str, dict[str, float]]
    statistical_significance: StatisticalSignificance
    recommendation: str
    insights: list[str]
    completed_at: Optional[datetime]


@dataclass
class Experiment:
    """Experimento A/B."""

    id: UUID
    name: str
    description: str
    status: ExperimentStatus
    variants: list[ExperimentVariant]
    primary_metric: MetricType
    secondary_metrics: list[MetricType]
    target_sample_size: int
    min_confidence_level: float
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    filters: dict[str, Any] = field(default_factory=dict)


class ABTestingEngine:
    """
    Engine de A/B Testing para notificações.

    Suporta:
    - Criação de experimentos multi-variante
    - Alocação de usuários com hashing consistente
    - Cálculo de significância estatística
    - Auto-conclusão baseada em resultados
    - Relatórios e insights
    """

    # Configurações padrão
    DEFAULT_CONFIDENCE = 0.95
    DEFAULT_SAMPLE_SIZE = 1000
    MIN_SAMPLE_PER_VARIANT = 100

    def __init__(
        self,
        auto_conclude: bool = True,
        min_runtime_hours: int = 24,
    ) -> None:
        """
        Inicializa o engine.

        Args:
            auto_conclude: Auto-concluir quando significativo
            min_runtime_hours: Tempo mínimo de execução
        """
        self.auto_conclude = auto_conclude
        self.min_runtime = timedelta(hours=min_runtime_hours)
        self._experiments: dict[UUID, Experiment] = {}

    async def create_experiment(
        self,
        db: AsyncSession,
        name: str,
        description: str,
        variants: list[dict[str, Any]],
        primary_metric: MetricType = MetricType.OPEN_RATE,
        secondary_metrics: Optional[list[MetricType]] = None,
        target_sample_size: int = DEFAULT_SAMPLE_SIZE,
        min_confidence: float = DEFAULT_CONFIDENCE,
        filters: Optional[dict[str, Any]] = None,
    ) -> Experiment:
        """
        Cria um novo experimento.

        Args:
            db: Sessão do banco
            name: Nome do experimento
            description: Descrição
            variants: Lista de variantes
            primary_metric: Métrica principal
            secondary_metrics: Métricas secundárias
            target_sample_size: Tamanho da amostra alvo
            min_confidence: Confiança mínima
            filters: Filtros de segmentação

        Returns:
            Experiment criado
        """
        experiment_id = uuid4()

        # Criar variantes
        variant_objects = []
        total_weight = sum(v.get("weight", 1.0) for v in variants)

        for i, v in enumerate(variants):
            variant_objects.append(
                ExperimentVariant(
                    variant_id=v.get("id", f"variant_{i}"),
                    name=v.get("name", f"Variante {chr(65 + i)}"),
                    description=v.get("description", ""),
                    weight=v.get("weight", 1.0) / total_weight,
                    is_control=v.get("is_control", i == 0),
                    config=v.get("config", {}),
                )
            )

        experiment = Experiment(
            id=experiment_id,
            name=name,
            description=description,
            status=ExperimentStatus.DRAFT,
            variants=variant_objects,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics or [],
            target_sample_size=target_sample_size,
            min_confidence_level=min_confidence,
            start_date=None,
            end_date=None,
            filters=filters or {},
        )

        self._experiments[experiment_id] = experiment
        await self._save_experiment(db, experiment)

        logger.info(f"Experimento criado: {experiment_id} - {name}")
        return experiment

    async def start_experiment(
        self,
        db: AsyncSession,
        experiment_id: UUID,
    ) -> Experiment:
        """Inicia um experimento."""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experimento não encontrado: {experiment_id}")

        if experiment.status != ExperimentStatus.DRAFT:
            raise ValueError(f"Experimento em status inválido: {experiment.status}")

        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.utcnow()
        experiment.updated_at = datetime.utcnow()

        await self._save_experiment(db, experiment)
        logger.info(f"Experimento iniciado: {experiment_id}")

        return experiment

    async def pause_experiment(
        self,
        db: AsyncSession,
        experiment_id: UUID,
    ) -> Experiment:
        """Pausa um experimento."""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experimento não encontrado: {experiment_id}")

        experiment.status = ExperimentStatus.PAUSED
        experiment.updated_at = datetime.utcnow()

        await self._save_experiment(db, experiment)
        return experiment

    async def conclude_experiment(
        self,
        db: AsyncSession,
        experiment_id: UUID,
        force: bool = False,
    ) -> ExperimentResult:
        """
        Conclui um experimento.

        Args:
            db: Sessão do banco
            experiment_id: ID do experimento
            force: Forçar conclusão mesmo sem significância

        Returns:
            ExperimentResult com análise final
        """
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experimento não encontrado: {experiment_id}")

        # Verificar runtime mínimo
        if experiment.start_date:
            runtime = datetime.utcnow() - experiment.start_date
            if runtime < self.min_runtime and not force:
                raise ValueError(f"Experimento precisa rodar por pelo menos {self.min_runtime}")

        # Calcular resultados
        result = await self.get_results(db, experiment_id)

        # Atualizar status
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_date = datetime.utcnow()
        experiment.updated_at = datetime.utcnow()

        await self._save_experiment(db, experiment)
        logger.info(f"Experimento concluído: {experiment_id}")

        return result

    def allocate_user(
        self,
        experiment_id: UUID,
        user_id: int,
    ) -> Optional[ExperimentVariant]:
        """
        Aloca usuário a uma variante usando hashing consistente.

        Args:
            experiment_id: ID do experimento
            user_id: ID do usuário

        Returns:
            ExperimentVariant alocada ou None
        """
        experiment = self._experiments.get(experiment_id)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return None

        # Hash consistente
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 10000) / 10000.0

        # Determinar variante
        cumulative_weight = 0.0
        for variant in experiment.variants:
            cumulative_weight += variant.weight
            if bucket < cumulative_weight:
                return variant

        return experiment.variants[-1]

    async def record_event(
        self,
        db: AsyncSession,
        experiment_id: UUID,
        variant_id: str,
        event_type: str,
        user_id: int,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Registra evento de um experimento.

        Args:
            db: Sessão do banco
            experiment_id: ID do experimento
            variant_id: ID da variante
            event_type: Tipo do evento (impression, open, click, conversion)
            user_id: ID do usuário
            metadata: Dados adicionais
        """
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return

        # Encontrar variante
        variant = next((v for v in experiment.variants if v.variant_id == variant_id), None)
        if not variant:
            return

        # Atualizar contadores
        if event_type == "impression":
            variant.impressions += 1
        elif event_type == "open":
            variant.opens += 1
        elif event_type == "click":
            variant.clicks += 1
        elif event_type == "conversion":
            variant.conversions += 1
        elif event_type == "unsubscribe":
            variant.unsubscribes += 1

        # Salvar evento
        await self._save_event(db, experiment_id, variant_id, event_type, user_id, metadata)

        # Verificar auto-conclusão
        if self.auto_conclude:
            await self._check_auto_conclude(db, experiment)

    async def get_results(
        self,
        db: AsyncSession,
        experiment_id: UUID,
    ) -> ExperimentResult:
        """
        Obtém resultados do experimento.

        Args:
            db: Sessão do banco
            experiment_id: ID do experimento

        Returns:
            ExperimentResult com análise completa
        """
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experimento não encontrado: {experiment_id}")

        # Calcular métricas por variante
        variants_results = {}
        control = None

        for variant in experiment.variants:
            impressions = max(variant.impressions, 1)
            metrics = {
                "impressions": variant.impressions,
                "opens": variant.opens,
                "clicks": variant.clicks,
                "conversions": variant.conversions,
                "open_rate": variant.opens / impressions,
                "click_rate": variant.clicks / impressions,
                "conversion_rate": variant.conversions / impressions,
                "unsubscribe_rate": variant.unsubscribes / impressions,
            }
            variants_results[variant.variant_id] = metrics

            if variant.is_control:
                control = variant

        # Calcular significância
        significance = self._calculate_significance(
            experiment,
            control,
            variants_results,
        )

        # Determinar vencedor
        winning_variant = self._determine_winner(
            experiment,
            variants_results,
            significance,
        )

        # Gerar insights
        insights = self._generate_insights(
            experiment,
            variants_results,
            significance,
        )

        # Gerar recomendação
        recommendation = self._generate_recommendation(
            winning_variant,
            significance,
            insights,
        )

        return ExperimentResult(
            experiment_id=experiment_id,
            winning_variant=winning_variant,
            variants_results=variants_results,
            statistical_significance=significance,
            recommendation=recommendation,
            insights=insights,
            completed_at=experiment.end_date,
        )

    def _calculate_significance(
        self,
        experiment: Experiment,
        control: Optional[ExperimentVariant],
        results: dict[str, dict[str, float]],
    ) -> StatisticalSignificance:
        """Calcula significância estatística."""
        if not control:
            control = experiment.variants[0]

        control_results = results.get(control.variant_id, {})
        best_variant_id = None
        best_lift = 0.0

        # Encontrar melhor variante vs controle
        metric_key = f"{experiment.primary_metric.value.replace('_rate', '')}_rate"
        control_rate = control_results.get(metric_key, 0)

        for variant_id, variant_results in results.items():
            if variant_id == control.variant_id:
                continue

            variant_rate = variant_results.get(metric_key, 0)
            if control_rate > 0:
                lift = (variant_rate - control_rate) / control_rate
                if lift > best_lift:
                    best_lift = lift
                    best_variant_id = variant_id

        # Calcular tamanho de amostra
        total_samples = sum(v.impressions for v in experiment.variants)
        needed_samples = self._calculate_sample_size(control_rate, experiment.min_confidence_level)

        # Calcular p-value (simplificado)
        p_value = self._calculate_p_value(
            control,
            experiment.variants,
            experiment.primary_metric,
        )

        is_significant = (
            p_value < (1 - experiment.min_confidence_level)
            and total_samples >= needed_samples
        )

        return StatisticalSignificance(
            is_significant=is_significant,
            confidence_level=1 - p_value if p_value < 1 else 0,
            p_value=p_value,
            lift_percentage=best_lift * 100,
            sample_size_needed=needed_samples,
            current_sample_size=total_samples,
            power=min(total_samples / needed_samples, 1.0) if needed_samples > 0 else 0,
        )

    def _calculate_sample_size(
        self,
        baseline_rate: float,
        confidence: float,
        mde: float = 0.1,  # Minimum Detectable Effect
    ) -> int:
        """Calcula tamanho de amostra necessário."""
        if baseline_rate <= 0:
            return self.DEFAULT_SAMPLE_SIZE

        # Fórmula simplificada para two-proportion z-test
        z_alpha = 1.96 if confidence >= 0.95 else 1.645
        z_beta = 0.84  # 80% power

        p1 = baseline_rate
        p2 = baseline_rate * (1 + mde)
        p_avg = (p1 + p2) / 2

        numerator = (z_alpha * math.sqrt(2 * p_avg * (1 - p_avg)) +
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
        denominator = (p2 - p1) ** 2

        if denominator <= 0:
            return self.DEFAULT_SAMPLE_SIZE

        return int(numerator / denominator)

    def _calculate_p_value(
        self,
        control: ExperimentVariant,
        variants: list[ExperimentVariant],
        metric: MetricType,
    ) -> float:
        """Calcula p-value simplificado."""
        if control.impressions < self.MIN_SAMPLE_PER_VARIANT:
            return 1.0

        # Taxa do controle
        if metric == MetricType.OPEN_RATE:
            control_rate = control.opens / max(control.impressions, 1)
        elif metric == MetricType.CLICK_RATE:
            control_rate = control.clicks / max(control.impressions, 1)
        elif metric == MetricType.CONVERSION_RATE:
            control_rate = control.conversions / max(control.impressions, 1)
        else:
            return 1.0

        min_p_value = 1.0

        for variant in variants:
            if variant.variant_id == control.variant_id:
                continue
            if variant.impressions < self.MIN_SAMPLE_PER_VARIANT:
                continue

            # Taxa da variante
            if metric == MetricType.OPEN_RATE:
                variant_rate = variant.opens / max(variant.impressions, 1)
            elif metric == MetricType.CLICK_RATE:
                variant_rate = variant.clicks / max(variant.impressions, 1)
            elif metric == MetricType.CONVERSION_RATE:
                variant_rate = variant.conversions / max(variant.impressions, 1)
            else:
                continue

            # Z-test simplificado
            p_pooled = (control_rate * control.impressions + variant_rate * variant.impressions) / (
                control.impressions + variant.impressions
            )

            if p_pooled <= 0 or p_pooled >= 1:
                continue

            se = math.sqrt(p_pooled * (1 - p_pooled) * (1/control.impressions + 1/variant.impressions))

            if se <= 0:
                continue

            z_score = abs(variant_rate - control_rate) / se

            # Aproximação do p-value (two-tailed)
            p_value = 2 * (1 - self._normal_cdf(z_score))
            min_p_value = min(min_p_value, p_value)

        return min_p_value

    def _normal_cdf(self, x: float) -> float:
        """Aproximação da CDF normal."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _determine_winner(
        self,
        experiment: Experiment,
        results: dict[str, dict[str, float]],
        significance: StatisticalSignificance,
    ) -> Optional[str]:
        """Determina variante vencedora."""
        if not significance.is_significant:
            return None

        metric_key = f"{experiment.primary_metric.value.replace('_rate', '')}_rate"
        best_variant = None
        best_rate = 0.0

        for variant_id, variant_results in results.items():
            rate = variant_results.get(metric_key, 0)
            if rate > best_rate:
                best_rate = rate
                best_variant = variant_id

        return best_variant

    def _generate_insights(
        self,
        experiment: Experiment,
        results: dict[str, dict[str, float]],
        significance: StatisticalSignificance,
    ) -> list[str]:
        """Gera insights do experimento."""
        insights = []

        # Insight de amostra
        if significance.current_sample_size < significance.sample_size_needed:
            pct = (significance.current_sample_size / significance.sample_size_needed) * 100
            insights.append(f"Amostra em {pct:.0f}% do necessário ({significance.current_sample_size}/{significance.sample_size_needed})")

        # Insight de lift
        if significance.lift_percentage > 0:
            insights.append(f"Melhor variante tem lift de +{significance.lift_percentage:.1f}% vs controle")
        elif significance.lift_percentage < 0:
            insights.append(f"Variantes performando {abs(significance.lift_percentage):.1f}% pior que controle")

        # Insight de significância
        if significance.is_significant:
            insights.append(f"Resultado estatisticamente significativo (p={significance.p_value:.4f})")
        else:
            insights.append(f"Sem significância estatística ainda (p={significance.p_value:.4f})")

        # Insights por variante
        for variant_id, variant_results in results.items():
            if variant_results.get("unsubscribe_rate", 0) > 0.02:
                insights.append(f"Variante {variant_id} tem alta taxa de unsubscribe")

        return insights

    def _generate_recommendation(
        self,
        winner: Optional[str],
        significance: StatisticalSignificance,
        insights: list[str],
    ) -> str:
        """Gera recomendação final."""
        if winner and significance.is_significant:
            return f"Implementar variante '{winner}' com {significance.confidence_level:.0%} de confiança"

        if significance.current_sample_size < significance.sample_size_needed * 0.5:
            return "Continuar experimento - amostra insuficiente"

        if significance.p_value < 0.1:
            return "Tendência positiva detectada - aguardar mais dados"

        return "Sem diferença significativa - considerar encerrar ou modificar variantes"

    async def _check_auto_conclude(
        self,
        db: AsyncSession,
        experiment: Experiment,
    ) -> None:
        """Verifica se deve concluir automaticamente."""
        if experiment.status != ExperimentStatus.RUNNING:
            return

        # Verificar tempo mínimo
        if experiment.start_date:
            runtime = datetime.utcnow() - experiment.start_date
            if runtime < self.min_runtime:
                return

        # Verificar significância
        result = await self.get_results(db, experiment.id)

        if result.statistical_significance.is_significant:
            total_samples = result.statistical_significance.current_sample_size
            if total_samples >= experiment.target_sample_size:
                logger.info(f"Auto-concluindo experimento {experiment.id}")
                await self.conclude_experiment(db, experiment.id)

    async def _save_experiment(
        self,
        db: AsyncSession,
        experiment: Experiment,
    ) -> None:
        """Salva experimento no banco."""
        # TODO: Implementar persistência real
        self._experiments[experiment.id] = experiment

    async def _save_event(
        self,
        db: AsyncSession,
        experiment_id: UUID,
        variant_id: str,
        event_type: str,
        user_id: int,
        metadata: Optional[dict],
    ) -> None:
        """Salva evento no banco."""
        # TODO: Implementar persistência real
        logger.debug(f"Event: {experiment_id}/{variant_id}/{event_type} user={user_id}")

    async def list_experiments(
        self,
        db: AsyncSession,
        status: Optional[ExperimentStatus] = None,
    ) -> list[Experiment]:
        """Lista experimentos."""
        experiments = list(self._experiments.values())
        if status:
            experiments = [e for e in experiments if e.status == status]
        return experiments

    async def get_experiment(
        self,
        db: AsyncSession,
        experiment_id: UUID,
    ) -> Optional[Experiment]:
        """Obtém experimento por ID."""
        return self._experiments.get(experiment_id)
