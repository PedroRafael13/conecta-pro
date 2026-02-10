"""Testes unitarios para Models de Custeio ABC."""

from datetime import datetime
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
        """Testa criacao de cost driver."""
        driver = CostDriver(
            condominio_id=uuid4(),
            code="DRV-001",
            name="Horas de Mao de Obra",
            driver_type=DriverType.TRANSACTION,
            driver_category=DriverCategory.RESOURCE,
            status=DriverStatus.ACTIVE,
            measure_unit=DriverMeasureUnit.HOURS,
            practical_capacity=Decimal("1000"),
            used_capacity=Decimal("800"),
            unit_cost=Decimal("50"),
        )

        assert driver.code == "DRV-001"
        assert driver.driver_type == DriverType.TRANSACTION
        assert driver.status == DriverStatus.ACTIVE

    def test_capacity_usage_percent(self):
        """Testa calculo de percentual de uso de capacidade."""
        driver = CostDriver(
            condominio_id=uuid4(),
            code="DRV-002",
            name="Horas Maquina",
            driver_type=DriverType.DURATION,
            practical_capacity=Decimal("1000"),
            used_capacity=Decimal("800"),
            unit_cost=Decimal("50"),
        )

        assert driver.capacity_usage_percent == Decimal("80")

    def test_idle_capacity(self):
        """Testa calculo de capacidade ociosa."""
        driver = CostDriver(
            condominio_id=uuid4(),
            code="DRV-003",
            name="Horas Maquina",
            driver_type=DriverType.DURATION,
            practical_capacity=Decimal("1000"),
            used_capacity=Decimal("800"),
            unit_cost=Decimal("50"),
        )

        assert driver.idle_capacity == Decimal("200")

    def test_idle_capacity_cost(self):
        """Testa calculo do custo de ociosidade."""
        driver = CostDriver(
            condominio_id=uuid4(),
            code="DRV-004",
            name="Horas Maquina",
            driver_type=DriverType.DURATION,
            practical_capacity=Decimal("1000"),
            used_capacity=Decimal("800"),
            unit_cost=Decimal("50"),
        )

        # idle_capacity=200, unit_cost=50 -> 200*50 = 10000
        assert driver.idle_capacity_cost == Decimal("10000")


class TestCostActivityModel:
    """Testes para CostActivity."""

    def test_create_activity(self):
        """Testa criacao de atividade."""
        activity = CostActivity(
            condominio_id=uuid4(),
            code="ACT-001",
            name="Atendimento ao Cliente",
            activity_type=ActivityType.PRIMARY,
            activity_level=ActivityLevel.UNIT,
            status=ActivityStatus.ACTIVE,
            value_added_type=ValueAddedType.VALUE_ADDED,
            total_cost=Decimal("10000.00"),
            practical_capacity=Decimal("500"),
            used_capacity=Decimal("400"),
        )

        assert activity.code == "ACT-001"
        assert activity.activity_level == ActivityLevel.UNIT
        assert activity.value_added_type == ValueAddedType.VALUE_ADDED

    def test_is_value_added(self):
        """Testa verificacao de valor agregado via value_added_type."""
        activity_va = CostActivity(
            condominio_id=uuid4(),
            code="ACT-VA",
            name="Atividade VA",
            value_added_type=ValueAddedType.VALUE_ADDED,
        )
        activity_nva = CostActivity(
            condominio_id=uuid4(),
            code="ACT-NVA",
            name="Atividade NVA",
            value_added_type=ValueAddedType.NON_VALUE_ADDED,
        )

        assert activity_va.value_added_type == ValueAddedType.VALUE_ADDED
        assert activity_nva.value_added_type == ValueAddedType.NON_VALUE_ADDED


class TestCostPoolModel:
    """Testes para CostPool."""

    def test_create_pool(self):
        """Testa criacao de pool."""
        pool = CostPool(
            condominio_id=uuid4(),
            code="POOL-001",
            name="Custos Administrativos",
            pool_type=PoolType.OVERHEAD,
            status=PoolStatus.ACTIVE,
            allocation_basis=AllocationBasis.ACTIVITY_BASED,
            total_cost=Decimal("100000.00"),
            allocated_cost=Decimal("80000.00"),
        )

        assert pool.code == "POOL-001"
        assert pool.pool_type == PoolType.OVERHEAD
        assert pool.total_cost == Decimal("100000.00")

    def test_unallocated_value(self):
        """Testa calculo de valor nao alocado via unallocated_cost."""
        pool = CostPool(
            condominio_id=uuid4(),
            code="POOL-002",
            name="Pool Teste",
            pool_type=PoolType.OVERHEAD,
            total_cost=Decimal("100000.00"),
            allocated_cost=Decimal("80000.00"),
            unallocated_cost=Decimal("20000.00"),
        )

        assert pool.unallocated_cost == Decimal("20000.00")

    def test_allocation_percent(self):
        """Testa calculo de percentual alocado."""
        pool = CostPool(
            condominio_id=uuid4(),
            code="POOL-003",
            name="Pool Teste",
            pool_type=PoolType.LABOR,
            total_cost=Decimal("100000.00"),
            allocated_cost=Decimal("75000.00"),
            allocation_base_quantity=Decimal("100"),
        )

        # allocation_rate = total_cost / allocation_base_quantity
        rate = pool.calculate_rate()
        assert rate == Decimal("1000")


class TestCostObjectModel:
    """Testes para CostObject."""

    def test_create_object(self):
        """Testa criacao de objeto de custo."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-001",
            name="Servico de Vigilancia",
            object_type=CostObjectType.SERVICE,
            total_direct_cost=Decimal("50000.00"),
            total_indirect_cost=Decimal("20000.00"),
            revenue=Decimal("100000.00"),
            quantity=Decimal("100"),
        )

        assert obj.code == "OBJ-001"
        assert obj.object_type == CostObjectType.SERVICE
        assert obj.revenue == Decimal("100000.00")

    def test_total_cost(self):
        """Testa calculo de custo total via calculate_margins."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-002",
            name="Objeto Teste",
            object_type=CostObjectType.SERVICE,
            direct_material_cost=Decimal("30000.00"),
            direct_labor_cost=Decimal("20000.00"),
            other_direct_cost=Decimal("0"),
            allocated_overhead=Decimal("20000.00"),
            allocated_activity_cost=Decimal("0"),
            revenue=Decimal("0"),
            quantity=Decimal("0"),
            cost_budget=Decimal("0"),
        )
        obj.calculate_margins()

        assert obj.total_cost == Decimal("70000.00")

    def test_gross_margin(self):
        """Testa calculo de margem bruta via calculate_margins."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-003",
            name="Objeto Teste",
            object_type=CostObjectType.SERVICE,
            direct_material_cost=Decimal("30000.00"),
            direct_labor_cost=Decimal("20000.00"),
            other_direct_cost=Decimal("0"),
            allocated_overhead=Decimal("20000.00"),
            allocated_activity_cost=Decimal("0"),
            revenue=Decimal("100000.00"),
            quantity=Decimal("0"),
            cost_budget=Decimal("0"),
        )
        obj.calculate_margins()

        # gross_margin = revenue - total_direct_cost = 100000 - 50000 = 50000
        assert obj.gross_margin == Decimal("50000.00")

    def test_gross_margin_percent(self):
        """Testa calculo de percentual de margem bruta."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-004",
            name="Objeto Teste",
            object_type=CostObjectType.SERVICE,
            direct_material_cost=Decimal("30000.00"),
            direct_labor_cost=Decimal("20000.00"),
            other_direct_cost=Decimal("0"),
            allocated_overhead=Decimal("20000.00"),
            allocated_activity_cost=Decimal("0"),
            revenue=Decimal("100000.00"),
            quantity=Decimal("0"),
            cost_budget=Decimal("0"),
        )
        obj.calculate_margins()

        # gross_margin_percent = (50000/100000)*100 = 50
        assert obj.gross_margin_percent == Decimal("50")

    def test_unit_cost(self):
        """Testa calculo de custo unitario via calculate_margins."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-005",
            name="Objeto Teste",
            object_type=CostObjectType.PRODUCT,
            direct_material_cost=Decimal("30000.00"),
            direct_labor_cost=Decimal("20000.00"),
            other_direct_cost=Decimal("0"),
            allocated_overhead=Decimal("20000.00"),
            allocated_activity_cost=Decimal("0"),
            revenue=Decimal("0"),
            quantity=Decimal("100"),
            cost_budget=Decimal("0"),
        )
        obj.calculate_margins()

        # unit_cost = total_cost / quantity = 70000 / 100 = 700
        assert obj.unit_cost == Decimal("700")

    def test_profitability_level_high(self):
        """Testa classificacao de lucratividade alta."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-HIGH",
            name="Alta Lucratividade",
            object_type=CostObjectType.SERVICE,
            direct_material_cost=Decimal("30000.00"),
            direct_labor_cost=Decimal("0"),
            other_direct_cost=Decimal("0"),
            allocated_overhead=Decimal("0"),
            allocated_activity_cost=Decimal("0"),
            revenue=Decimal("100000.00"),
            quantity=Decimal("1"),
            cost_budget=Decimal("0"),
        )
        obj.calculate_margins()

        # net_margin_percent = ((100000-30000)/100000)*100 = 70 -> >= 20 -> HIGHLY_PROFITABLE
        assert obj.profitability_level == ProfitabilityLevel.HIGHLY_PROFITABLE

    def test_profitability_level_negative(self):
        """Testa classificacao de lucratividade negativa."""
        obj = CostObject(
            condominio_id=uuid4(),
            code="OBJ-NEG",
            name="Negativo",
            object_type=CostObjectType.SERVICE,
            direct_material_cost=Decimal("120000.00"),
            direct_labor_cost=Decimal("0"),
            other_direct_cost=Decimal("0"),
            allocated_overhead=Decimal("0"),
            allocated_activity_cost=Decimal("0"),
            revenue=Decimal("100000.00"),
            quantity=Decimal("1"),
            cost_budget=Decimal("0"),
        )
        obj.calculate_margins()

        # net_margin_percent = ((100000-120000)/100000)*100 = -20 -> < -5 -> UNPROFITABLE
        assert obj.profitability_level == ProfitabilityLevel.UNPROFITABLE


class TestCostAllocationModel:
    """Testes para CostAllocation."""

    def test_create_allocation(self):
        """Testa criacao de alocacao."""
        allocation = CostAllocation(
            condominio_id=uuid4(),
            allocation_number="ALLOC-001",
            allocation_type=AllocationType.POOL_TO_ACTIVITY,
            allocation_method=AllocationMethod.DRIVER_BASED,
            source_pool_id=uuid4(),
            activity_id=uuid4(),
            allocated_amount=Decimal("25000.00"),
            allocation_percentage=Decimal("25"),
            allocation_date=datetime.utcnow(),
            reference_period="2025-01",
            status=AllocationStatus.PENDING,
        )

        assert allocation.allocation_number == "ALLOC-001"
        assert allocation.allocation_type == AllocationType.POOL_TO_ACTIVITY
        assert allocation.status == AllocationStatus.PENDING

    def test_is_executed(self):
        """Testa propriedade is_executed."""
        allocation_pending = CostAllocation(
            condominio_id=uuid4(),
            allocation_number="ALLOC-P",
            allocation_type=AllocationType.DIRECT,
            source_pool_id=uuid4(),
            cost_object_id=uuid4(),
            allocated_amount=Decimal("10000.00"),
            allocation_date=datetime.utcnow(),
            reference_period="2025-01",
            status=AllocationStatus.PENDING,
        )
        allocation_executed = CostAllocation(
            condominio_id=uuid4(),
            allocation_number="ALLOC-E",
            allocation_type=AllocationType.DIRECT,
            source_pool_id=uuid4(),
            cost_object_id=uuid4(),
            allocated_amount=Decimal("10000.00"),
            allocation_date=datetime.utcnow(),
            reference_period="2025-01",
            status=AllocationStatus.EXECUTED,
        )

        assert allocation_pending.is_executed is False
        assert allocation_executed.is_executed is True


class TestCostAnalysisModel:
    """Testes para CostAnalysis."""

    def test_create_analysis(self):
        """Testa criacao de analise."""
        analysis = CostAnalysis(
            condominio_id=uuid4(),
            code="ANAL-001",
            name="Analise ABC Janeiro 2025",
            analysis_type=AnalysisType.ABC_COSTING,
            status=AnalysisStatus.DRAFT,
            period_start=datetime(2025, 1, 1),
            period_end=datetime(2025, 1, 31),
            parameters={"metodo": "ABC", "incluir_ociosidade": True},
        )

        assert analysis.code == "ANAL-001"
        assert analysis.analysis_type == AnalysisType.ABC_COSTING
        assert analysis.status == AnalysisStatus.DRAFT

    def test_analysis_types(self):
        """Testa todos os tipos de analise."""
        types = [
            AnalysisType.ABC_COSTING,
            AnalysisType.PROFITABILITY,
            AnalysisType.VARIANCE,
            AnalysisType.BREAK_EVEN,
            AnalysisType.TREND,
            AnalysisType.COST_VOLUME_PROFIT,
            AnalysisType.IDLE_CAPACITY,
        ]

        for analysis_type in types:
            analysis = CostAnalysis(
                condominio_id=uuid4(),
                code=f"ANAL-{analysis_type.value}",
                name=f"Analise {analysis_type.value}",
                analysis_type=analysis_type,
                period_start=datetime(2025, 1, 1),
                period_end=datetime(2025, 1, 31),
            )
            assert analysis.analysis_type == analysis_type


class TestEnums:
    """Testes para Enums."""

    def test_driver_types(self):
        """Testa tipos de driver."""
        assert DriverType.TRANSACTION.value == "TRANSACTION"
        assert DriverType.DURATION.value == "DURATION"

    def test_activity_levels(self):
        """Testa niveis de atividade ABC."""
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
        """Testa tipos de alocacao."""
        assert AllocationType.POOL_TO_ACTIVITY.value == "POOL_TO_ACTIVITY"
        assert AllocationType.ACTIVITY_TO_OBJECT.value == "ACTIVITY_TO_OBJECT"
        assert AllocationType.DIRECT.value == "DIRECT"
        assert AllocationType.RECIPROCAL.value == "RECIPROCAL"

    def test_allocation_methods(self):
        """Testa metodos de alocacao."""
        assert AllocationMethod.DRIVER_BASED.value == "DRIVER_BASED"
        assert AllocationMethod.PERCENTAGE.value == "PERCENTAGE"
        assert AllocationMethod.PROPORTIONAL.value == "PROPORTIONAL"
        assert AllocationMethod.EQUAL_SHARE.value == "EQUAL_SHARE"
        assert AllocationMethod.WEIGHTED.value == "WEIGHTED"

    def test_profitability_levels(self):
        """Testa niveis de lucratividade."""
        assert ProfitabilityLevel.HIGHLY_PROFITABLE.value == "HIGHLY_PROFITABLE"
        assert ProfitabilityLevel.PROFITABLE.value == "PROFITABLE"
        assert ProfitabilityLevel.MARGINAL.value == "MARGINAL"
        assert ProfitabilityLevel.BREAK_EVEN.value == "BREAK_EVEN"
        assert ProfitabilityLevel.UNPROFITABLE.value == "UNPROFITABLE"
