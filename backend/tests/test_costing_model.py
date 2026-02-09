"""Testes unitários para Models de Custeio ABC."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.financial.costing.models import (
    CostActivity,
    CostAllocation,
    CostAnalysis,
    CostDriver,
    CostObject,
    CostPool,
)
from modules.financial.costing.models.cost_activity import (
    ActivityLevel,
    ActivityStatus,
    ActivityType,
    ValueAddedType,
)
from modules.financial.costing.models.cost_allocation import (
    AllocationMethod,
    AllocationStatus,
    AllocationType,
)
from modules.financial.costing.models.cost_analysis import (
    AnalysisStatus,
    AnalysisType,
)
from modules.financial.costing.models.cost_driver import (
    DriverCategory,
    DriverMeasureUnit,
    DriverStatus,
    DriverType,
)
from modules.financial.costing.models.cost_object import (
    CostObjectType,
    ProfitabilityLevel,
)
from modules.financial.costing.models.cost_pool import (
    AllocationBasis,
    PoolStatus,
    PoolType,
)


class TestCostDriverModel:
    """Testes para CostDriver."""

    def test_create_driver(self):
        """Testa criação de cost driver."""
        driver = CostDriver(
            condominio_id=uuid4(),
            codigo="DRV-001",
            nome="Horas de Mão de Obra",
            tipo=DriverType.RESOURCE,
            categoria=DriverCategory.LABOR,
            status=DriverStatus.ACTIVE,
            unidade_medida=DriverMeasureUnit.HOUR,
            capacidade_pratica=Decimal("1000"),
            quantidade_usada=Decimal("800"),
            custo_total=Decimal("50000.00"),
        )

        assert driver.codigo == "DRV-001"
        assert driver.tipo == DriverType.RESOURCE
        assert driver.status == DriverStatus.ACTIVE

    def test_capacity_usage_percent(self):
        """Testa cálculo de percentual de uso de capacidade."""
        driver = CostDriver(
            condominio_id=uuid4(),
            codigo="DRV-002",
            nome="Horas Máquina",
            tipo=DriverType.RESOURCE,
            capacidade_pratica=Decimal("1000"),
            quantidade_usada=Decimal("800"),
            custo_total=Decimal("50000.00"),
        )

        assert driver.capacity_usage_percent == Decimal("80")

    def test_idle_capacity(self):
        """Testa cálculo de capacidade ociosa."""
        driver = CostDriver(
            condominio_id=uuid4(),
            codigo="DRV-003",
            nome="Horas Máquina",
            tipo=DriverType.RESOURCE,
            capacidade_pratica=Decimal("1000"),
            quantidade_usada=Decimal("800"),
            custo_total=Decimal("50000.00"),
        )

        assert driver.idle_capacity == Decimal("200")

    def test_idle_capacity_cost(self):
        """Testa cálculo do custo de ociosidade."""
        driver = CostDriver(
            condominio_id=uuid4(),
            codigo="DRV-004",
            nome="Horas Máquina",
            tipo=DriverType.RESOURCE,
            capacidade_pratica=Decimal("1000"),
            quantidade_usada=Decimal("800"),
            custo_total=Decimal("50000.00"),
        )

        # 20% de ociosidade * R$ 50.000 = R$ 10.000
        assert driver.idle_capacity_cost == Decimal("10000.00")


class TestCostActivityModel:
    """Testes para CostActivity."""

    def test_create_activity(self):
        """Testa criação de atividade."""
        activity = CostActivity(
            condominio_id=uuid4(),
            codigo="ACT-001",
            nome="Atendimento ao Cliente",
            tipo=ActivityType.OPERATIONAL,
            nivel=ActivityLevel.UNIT,
            status=ActivityStatus.ACTIVE,
            tipo_valor_agregado=ValueAddedType.VALUE_ADDED,
            custo_direto=Decimal("10000.00"),
            capacidade_pratica=Decimal("500"),
            capacidade_usada=Decimal("400"),
        )

        assert activity.codigo == "ACT-001"
        assert activity.nivel == ActivityLevel.UNIT
        assert activity.tipo_valor_agregado == ValueAddedType.VALUE_ADDED

    def test_is_value_added(self):
        """Testa propriedade is_value_added."""
        activity_va = CostActivity(
            condominio_id=uuid4(),
            codigo="ACT-VA",
            nome="Atividade VA",
            tipo_valor_agregado=ValueAddedType.VALUE_ADDED,
        )
        activity_nva = CostActivity(
            condominio_id=uuid4(),
            codigo="ACT-NVA",
            nome="Atividade NVA",
            tipo_valor_agregado=ValueAddedType.NON_VALUE_ADDED,
        )

        assert activity_va.is_value_added is True
        assert activity_nva.is_value_added is False


class TestCostPoolModel:
    """Testes para CostPool."""

    def test_create_pool(self):
        """Testa criação de pool."""
        pool = CostPool(
            condominio_id=uuid4(),
            codigo="POOL-001",
            nome="Custos Administrativos",
            tipo=PoolType.OVERHEAD,
            status=PoolStatus.ACTIVE,
            base_alocacao=AllocationBasis.DRIVER,
            valor_total=Decimal("100000.00"),
            valor_alocado=Decimal("80000.00"),
        )

        assert pool.codigo == "POOL-001"
        assert pool.tipo == PoolType.OVERHEAD
        assert pool.valor_total == Decimal("100000.00")

    def test_unallocated_value(self):
        """Testa cálculo de valor não alocado."""
        pool = CostPool(
            condominio_id=uuid4(),
            codigo="POOL-002",
            nome="Pool Teste",
            tipo=PoolType.OVERHEAD,
            valor_total=Decimal("100000.00"),
            valor_alocado=Decimal("80000.00"),
        )

        assert pool.unallocated_value == Decimal("20000.00")

    def test_allocation_percent(self):
        """Testa cálculo de percentual alocado."""
        pool = CostPool(
            condominio_id=uuid4(),
            codigo="POOL-003",
            nome="Pool Teste",
            tipo=PoolType.LABOR,
            valor_total=Decimal("100000.00"),
            valor_alocado=Decimal("75000.00"),
        )

        assert pool.allocation_percent == Decimal("75")


class TestCostObjectModel:
    """Testes para CostObject."""

    def test_create_object(self):
        """Testa criação de objeto de custo."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-001",
            nome="Serviço de Vigilância",
            tipo=CostObjectType.SERVICE,
            custo_direto=Decimal("50000.00"),
            custo_indireto=Decimal("20000.00"),
            receita=Decimal("100000.00"),
            quantidade=Decimal("100"),
        )

        assert obj.codigo == "OBJ-001"
        assert obj.tipo == CostObjectType.SERVICE
        assert obj.receita == Decimal("100000.00")

    def test_total_cost(self):
        """Testa cálculo de custo total."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-002",
            nome="Objeto Teste",
            tipo=CostObjectType.SERVICE,
            custo_direto=Decimal("50000.00"),
            custo_indireto=Decimal("20000.00"),
        )

        assert obj.total_cost == Decimal("70000.00")

    def test_gross_margin(self):
        """Testa cálculo de margem bruta."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-003",
            nome="Objeto Teste",
            tipo=CostObjectType.SERVICE,
            custo_direto=Decimal("50000.00"),
            custo_indireto=Decimal("20000.00"),
            receita=Decimal("100000.00"),
        )

        assert obj.gross_margin == Decimal("30000.00")

    def test_gross_margin_percent(self):
        """Testa cálculo de percentual de margem bruta."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-004",
            nome="Objeto Teste",
            tipo=CostObjectType.SERVICE,
            custo_direto=Decimal("50000.00"),
            custo_indireto=Decimal("20000.00"),
            receita=Decimal("100000.00"),
        )

        assert obj.gross_margin_percent == Decimal("30")

    def test_unit_cost(self):
        """Testa cálculo de custo unitário."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-005",
            nome="Objeto Teste",
            tipo=CostObjectType.PRODUCT,
            custo_direto=Decimal("50000.00"),
            custo_indireto=Decimal("20000.00"),
            quantidade=Decimal("100"),
        )

        assert obj.unit_cost == Decimal("700")

    def test_profitability_level_high(self):
        """Testa classificação de lucratividade alta."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-HIGH",
            nome="Alta Lucratividade",
            tipo=CostObjectType.SERVICE,
            custo_direto=Decimal("30000.00"),
            receita=Decimal("100000.00"),
        )

        assert obj.profitability_level == ProfitabilityLevel.HIGH

    def test_profitability_level_negative(self):
        """Testa classificação de lucratividade negativa."""
        obj = CostObject(
            condominio_id=uuid4(),
            codigo="OBJ-NEG",
            nome="Negativo",
            tipo=CostObjectType.SERVICE,
            custo_direto=Decimal("120000.00"),
            receita=Decimal("100000.00"),
        )

        assert obj.profitability_level == ProfitabilityLevel.NEGATIVE


class TestCostAllocationModel:
    """Testes para CostAllocation."""

    def test_create_allocation(self):
        """Testa criação de alocação."""
        allocation = CostAllocation(
            condominio_id=uuid4(),
            codigo="ALLOC-001",
            tipo=AllocationType.POOL_TO_ACTIVITY,
            metodo=AllocationMethod.DRIVER_BASED,
            origem_tipo="pool",
            origem_id=uuid4(),
            destino_tipo="activity",
            destino_id=uuid4(),
            valor_alocado=Decimal("25000.00"),
            percentual_alocado=Decimal("25"),
            data_alocacao=date.today(),
            status=AllocationStatus.PENDING,
        )

        assert allocation.codigo == "ALLOC-001"
        assert allocation.tipo == AllocationType.POOL_TO_ACTIVITY
        assert allocation.status == AllocationStatus.PENDING

    def test_is_executed(self):
        """Testa propriedade is_executed."""
        allocation_pending = CostAllocation(
            condominio_id=uuid4(),
            codigo="ALLOC-P",
            tipo=AllocationType.DIRECT,
            origem_tipo="pool",
            origem_id=uuid4(),
            destino_tipo="object",
            destino_id=uuid4(),
            valor_alocado=Decimal("10000.00"),
            data_alocacao=date.today(),
            status=AllocationStatus.PENDING,
        )
        allocation_executed = CostAllocation(
            condominio_id=uuid4(),
            codigo="ALLOC-E",
            tipo=AllocationType.DIRECT,
            origem_tipo="pool",
            origem_id=uuid4(),
            destino_tipo="object",
            destino_id=uuid4(),
            valor_alocado=Decimal("10000.00"),
            data_alocacao=date.today(),
            status=AllocationStatus.EXECUTED,
        )

        assert allocation_pending.is_executed is False
        assert allocation_executed.is_executed is True


class TestCostAnalysisModel:
    """Testes para CostAnalysis."""

    def test_create_analysis(self):
        """Testa criação de análise."""
        analysis = CostAnalysis(
            condominio_id=uuid4(),
            codigo="ANAL-001",
            nome="Análise ABC Janeiro 2025",
            tipo=AnalysisType.ABC_COSTING,
            status=AnalysisStatus.PENDING,
            periodo_inicio=date(2025, 1, 1),
            periodo_fim=date(2025, 1, 31),
            parametros={"metodo": "ABC", "incluir_ociosidade": True},
        )

        assert analysis.codigo == "ANAL-001"
        assert analysis.tipo == AnalysisType.ABC_COSTING
        assert analysis.status == AnalysisStatus.PENDING

    def test_analysis_types(self):
        """Testa todos os tipos de análise."""
        types = [
            AnalysisType.ABC_COSTING,
            AnalysisType.PROFITABILITY,
            AnalysisType.VARIANCE,
            AnalysisType.BREAK_EVEN,
            AnalysisType.TREND,
            AnalysisType.FORECAST,
            AnalysisType.OPTIMIZATION,
        ]

        for analysis_type in types:
            analysis = CostAnalysis(
                condominio_id=uuid4(),
                codigo=f"ANAL-{analysis_type.value}",
                nome=f"Análise {analysis_type.value}",
                tipo=analysis_type,
            )
            assert analysis.tipo == analysis_type


class TestEnums:
    """Testes para Enums."""

    def test_driver_types(self):
        """Testa tipos de driver."""
        assert DriverType.RESOURCE.value == "RESOURCE"
        assert DriverType.ACTIVITY.value == "ACTIVITY"

    def test_activity_levels(self):
        """Testa níveis de atividade ABC."""
        assert ActivityLevel.UNIT.value == "UNIT"
        assert ActivityLevel.BATCH.value == "BATCH"
        assert ActivityLevel.PRODUCT.value == "PRODUCT"
        assert ActivityLevel.FACILITY.value == "FACILITY"

    def test_pool_types(self):
        """Testa tipos de pool."""
        assert PoolType.OVERHEAD.value == "OVERHEAD"
        assert PoolType.LABOR.value == "LABOR"
        assert PoolType.EQUIPMENT.value == "EQUIPMENT"
        assert PoolType.UTILITIES.value == "UTILITIES"
        assert PoolType.MAINTENANCE.value == "MAINTENANCE"

    def test_allocation_types(self):
        """Testa tipos de alocação."""
        assert AllocationType.POOL_TO_ACTIVITY.value == "POOL_TO_ACTIVITY"
        assert AllocationType.ACTIVITY_TO_OBJECT.value == "ACTIVITY_TO_OBJECT"
        assert AllocationType.DIRECT.value == "DIRECT"
        assert AllocationType.RECIPROCAL.value == "RECIPROCAL"

    def test_allocation_methods(self):
        """Testa métodos de alocação."""
        assert AllocationMethod.DRIVER_BASED.value == "DRIVER_BASED"
        assert AllocationMethod.PERCENTAGE.value == "PERCENTAGE"
        assert AllocationMethod.PROPORTIONAL.value == "PROPORTIONAL"
        assert AllocationMethod.EQUAL.value == "EQUAL"
        assert AllocationMethod.STEP_DOWN.value == "STEP_DOWN"

    def test_profitability_levels(self):
        """Testa níveis de lucratividade."""
        assert ProfitabilityLevel.HIGH.value == "HIGH"
        assert ProfitabilityLevel.MEDIUM.value == "MEDIUM"
        assert ProfitabilityLevel.LOW.value == "LOW"
        assert ProfitabilityLevel.BREAK_EVEN.value == "BREAK_EVEN"
        assert ProfitabilityLevel.NEGATIVE.value == "NEGATIVE"
