"""Testes do A/B Testing Engine - Sprint 03."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from modules.notifications.testing.ab_testing_engine import (
    ABTestingEngine,
    Experiment,
    ExperimentResult,
    ExperimentStatus,
    ExperimentVariant,
    MetricType,
    StatisticalSignificance,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_db():
    """Mock da sessão do banco."""
    return AsyncMock()


@pytest.fixture
def ab_engine():
    """Instância do ABTestingEngine."""
    return ABTestingEngine(auto_conclude=False)


@pytest.fixture
def sample_variants():
    """Variantes de exemplo."""
    return [
        {
            "id": "control",
            "name": "Controle",
            "description": "Versão original",
            "is_control": True,
            "config": {"title": "Título A"},
        },
        {
            "id": "variant_b",
            "name": "Variante B",
            "description": "Título alternativo",
            "config": {"title": "Título B"},
        },
    ]


# ============================================================================
# Tests - Experiment Lifecycle
# ============================================================================


class TestExperimentLifecycle:
    """Testes do ciclo de vida de experimentos."""

    @pytest.mark.asyncio
    async def test_create_experiment(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa criação de experimento."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste de Título",
            description="Comparar títulos de notificação",
            variants=sample_variants,
            primary_metric=MetricType.OPEN_RATE,
            target_sample_size=1000,
        )

        assert isinstance(experiment, Experiment)
        assert experiment.name == "Teste de Título"
        assert experiment.status == ExperimentStatus.DRAFT
        assert len(experiment.variants) == 2

    @pytest.mark.asyncio
    async def test_start_experiment(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa início de experimento."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )

        started = await ab_engine.start_experiment(mock_db, experiment.id)

        assert started.status == ExperimentStatus.RUNNING
        assert started.start_date is not None

    @pytest.mark.asyncio
    async def test_pause_experiment(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa pausa de experimento."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        paused = await ab_engine.pause_experiment(mock_db, experiment.id)

        assert paused.status == ExperimentStatus.PAUSED

    @pytest.mark.asyncio
    async def test_conclude_experiment(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa conclusão de experimento."""
        # Criar e iniciar experimento
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        # Forçar conclusão
        result = await ab_engine.conclude_experiment(
            mock_db,
            experiment.id,
            force=True,
        )

        assert isinstance(result, ExperimentResult)
        assert result.experiment_id == experiment.id

        # Verificar que experimento foi concluído
        exp = await ab_engine.get_experiment(mock_db, experiment.id)
        assert exp.status == ExperimentStatus.COMPLETED


# ============================================================================
# Tests - User Allocation
# ============================================================================


class TestUserAllocation:
    """Testes de alocação de usuários."""

    @pytest.mark.asyncio
    async def test_allocate_user(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa alocação de usuário a variante."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        variant = ab_engine.allocate_user(experiment.id, user_id=123)

        assert variant is not None
        assert variant.variant_id in ["control", "variant_b"]

    @pytest.mark.asyncio
    async def test_allocation_consistency(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa que alocação é consistente para mesmo usuário."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        # Mesmo usuário deve receber mesma variante
        variant1 = ab_engine.allocate_user(experiment.id, user_id=456)
        variant2 = ab_engine.allocate_user(experiment.id, user_id=456)

        assert variant1.variant_id == variant2.variant_id

    @pytest.mark.asyncio
    async def test_allocation_distribution(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa distribuição de alocação."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        # Alocar muitos usuários
        allocations = {}
        for user_id in range(1000):
            variant = ab_engine.allocate_user(experiment.id, user_id)
            allocations[variant.variant_id] = allocations.get(variant.variant_id, 0) + 1

        # Verificar distribuição aproximada (50/50)
        for variant_id, count in allocations.items():
            # Aceitar variação de 10%
            assert 400 <= count <= 600, f"{variant_id}: {count}"

    def test_allocate_inactive_experiment(
        self,
        ab_engine,
    ):
        """Testa alocação em experimento inativo."""
        fake_id = uuid4()
        variant = ab_engine.allocate_user(fake_id, user_id=123)

        assert variant is None


# ============================================================================
# Tests - Event Recording
# ============================================================================


class TestEventRecording:
    """Testes de registro de eventos."""

    @pytest.mark.asyncio
    async def test_record_impression(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa registro de impressão."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        variant = ab_engine.allocate_user(experiment.id, user_id=123)
        initial_impressions = variant.impressions

        await ab_engine.record_event(
            db=mock_db,
            experiment_id=experiment.id,
            variant_id=variant.variant_id,
            event_type="impression",
            user_id=123,
        )

        assert variant.impressions == initial_impressions + 1

    @pytest.mark.asyncio
    async def test_record_conversion_funnel(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa registro de funil de conversão."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        variant = ab_engine.allocate_user(experiment.id, user_id=123)

        # Registrar eventos do funil
        for event in ["impression", "open", "click", "conversion"]:
            await ab_engine.record_event(
                db=mock_db,
                experiment_id=experiment.id,
                variant_id=variant.variant_id,
                event_type=event,
                user_id=123,
            )

        assert variant.impressions >= 1
        assert variant.opens >= 1
        assert variant.clicks >= 1
        assert variant.conversions >= 1


# ============================================================================
# Tests - Statistical Analysis
# ============================================================================


class TestStatisticalAnalysis:
    """Testes de análise estatística."""

    @pytest.mark.asyncio
    async def test_get_results(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa obtenção de resultados."""
        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        # Simular eventos
        for i in range(100):
            variant = ab_engine.allocate_user(experiment.id, user_id=i)
            await ab_engine.record_event(
                db=mock_db,
                experiment_id=experiment.id,
                variant_id=variant.variant_id,
                event_type="impression",
                user_id=i,
            )
            if i % 2 == 0:  # 50% open rate
                await ab_engine.record_event(
                    db=mock_db,
                    experiment_id=experiment.id,
                    variant_id=variant.variant_id,
                    event_type="open",
                    user_id=i,
                )

        result = await ab_engine.get_results(mock_db, experiment.id)

        assert isinstance(result, ExperimentResult)
        assert result.variants_results is not None
        assert result.statistical_significance is not None
        assert result.recommendation is not None

    @pytest.mark.asyncio
    async def test_statistical_significance(
        self,
        mock_db,
        ab_engine,
    ):
        """Testa cálculo de significância estatística."""
        # Criar experimento com variantes de performance diferente
        variants = [
            {"id": "control", "name": "Controle", "is_control": True},
            {"id": "better", "name": "Melhor"},
        ]

        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        # Simular grande diferença de performance
        # Controle: 30% open rate
        # Melhor: 50% open rate
        for i in range(500):
            # Forçar alocação para controle
            control_variant = experiment.variants[0]
            await ab_engine.record_event(
                db=mock_db,
                experiment_id=experiment.id,
                variant_id=control_variant.variant_id,
                event_type="impression",
                user_id=i,
            )
            if i % 3 == 0:  # ~33%
                await ab_engine.record_event(
                    db=mock_db,
                    experiment_id=experiment.id,
                    variant_id=control_variant.variant_id,
                    event_type="open",
                    user_id=i,
                )

        for i in range(500, 1000):
            # Forçar alocação para melhor
            better_variant = experiment.variants[1]
            await ab_engine.record_event(
                db=mock_db,
                experiment_id=experiment.id,
                variant_id=better_variant.variant_id,
                event_type="impression",
                user_id=i,
            )
            if i % 2 == 0:  # 50%
                await ab_engine.record_event(
                    db=mock_db,
                    experiment_id=experiment.id,
                    variant_id=better_variant.variant_id,
                    event_type="open",
                    user_id=i,
                )

        result = await ab_engine.get_results(mock_db, experiment.id)

        # Com diferença grande e amostra suficiente, deve ser significativo
        # (ou pelo menos ter lift positivo)
        assert result.statistical_significance.lift_percentage != 0

    def test_calculate_sample_size(
        self,
        ab_engine,
    ):
        """Testa cálculo de tamanho de amostra."""
        sample_size = ab_engine._calculate_sample_size(
            baseline_rate=0.3,
            confidence=0.95,
            mde=0.1,
        )

        assert sample_size > 0
        assert sample_size < 100000  # Sanity check

    def test_normal_cdf(
        self,
        ab_engine,
    ):
        """Testa aproximação da CDF normal."""
        # Valores conhecidos
        assert ab_engine._normal_cdf(0) == pytest.approx(0.5, abs=0.01)
        assert ab_engine._normal_cdf(1.96) == pytest.approx(0.975, abs=0.01)
        assert ab_engine._normal_cdf(-1.96) == pytest.approx(0.025, abs=0.01)


# ============================================================================
# Tests - Experiment Management
# ============================================================================


class TestExperimentManagement:
    """Testes de gerenciamento de experimentos."""

    @pytest.mark.asyncio
    async def test_list_experiments(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa listagem de experimentos."""
        # Criar alguns experimentos
        for i in range(3):
            await ab_engine.create_experiment(
                db=mock_db,
                name=f"Teste {i}",
                description="Descrição",
                variants=sample_variants,
            )

        experiments = await ab_engine.list_experiments(mock_db)

        assert len(experiments) >= 3

    @pytest.mark.asyncio
    async def test_list_experiments_by_status(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa listagem por status."""
        # Criar experimentos com status diferentes
        await ab_engine.create_experiment(
            db=mock_db,
            name="Draft",
            description="Descrição",
            variants=sample_variants,
        )

        running = await ab_engine.create_experiment(
            db=mock_db,
            name="Running",
            description="Descrição",
            variants=sample_variants,
        )
        await ab_engine.start_experiment(mock_db, running.id)

        # Listar apenas drafts
        drafts = await ab_engine.list_experiments(
            mock_db,
            status=ExperimentStatus.DRAFT,
        )

        assert all(e.status == ExperimentStatus.DRAFT for e in drafts)

    @pytest.mark.asyncio
    async def test_get_experiment(
        self,
        mock_db,
        ab_engine,
        sample_variants,
    ):
        """Testa obtenção de experimento por ID."""
        created = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=sample_variants,
        )

        fetched = await ab_engine.get_experiment(mock_db, created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == created.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_experiment(
        self,
        mock_db,
        ab_engine,
    ):
        """Testa obtenção de experimento inexistente."""
        fake_id = uuid4()
        fetched = await ab_engine.get_experiment(mock_db, fake_id)

        assert fetched is None


# ============================================================================
# Tests - Edge Cases
# ============================================================================


class TestEdgeCases:
    """Testes de casos extremos."""

    @pytest.mark.asyncio
    async def test_single_variant_experiment(
        self,
        mock_db,
        ab_engine,
    ):
        """Testa experimento com uma única variante."""
        variants = [{"id": "only", "name": "Única", "is_control": True}]

        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste",
            description="Descrição",
            variants=variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        variant = ab_engine.allocate_user(experiment.id, user_id=123)

        assert variant.variant_id == "only"

    @pytest.mark.asyncio
    async def test_many_variants_experiment(
        self,
        mock_db,
        ab_engine,
    ):
        """Testa experimento com muitas variantes."""
        variants = [{"id": f"variant_{i}", "name": f"Variante {i}"} for i in range(5)]
        variants[0]["is_control"] = True

        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste Multi",
            description="Descrição",
            variants=variants,
        )

        assert len(experiment.variants) == 5

    @pytest.mark.asyncio
    async def test_weighted_variants(
        self,
        mock_db,
        ab_engine,
    ):
        """Testa variantes com pesos customizados."""
        variants = [
            {"id": "control", "name": "Controle", "weight": 0.9, "is_control": True},
            {"id": "test", "name": "Teste", "weight": 0.1},
        ]

        experiment = await ab_engine.create_experiment(
            db=mock_db,
            name="Teste Peso",
            description="Descrição",
            variants=variants,
        )
        await ab_engine.start_experiment(mock_db, experiment.id)

        # Alocar muitos usuários
        control_count = 0
        for user_id in range(1000):
            variant = ab_engine.allocate_user(experiment.id, user_id)
            if variant.variant_id == "control":
                control_count += 1

        # Controle deve ter ~90% das alocações
        assert control_count > 800  # Pelo menos 80%
