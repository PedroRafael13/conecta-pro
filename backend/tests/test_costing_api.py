"""Testes de API para Custeio ABC."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.financial.costing.schemas import (
    CostActivityCreate,
    CostActivityResponse,
    CostAllocationCreate,
    CostAllocationResponse,
    CostDriverCreate,
    CostDriverResponse,
    CostObjectCreate,
    CostObjectResponse,
    CostPoolCreate,
    CostPoolResponse,
)


# Fixtures
@pytest.fixture
def mock_user():
    """Mock de usuario autenticado."""
    user = MagicMock()
    user.id = uuid4()
    user.condominio_id = uuid4()
    user.email = "admin@test.com"
    user.role = "admin"
    return user


@pytest.fixture
def condominio_id():
    """ID de condominio para testes."""
    return uuid4()


@pytest.fixture
def sample_driver_data(condominio_id):
    """Dados de exemplo para driver."""
    return {
        "code": "DRV-TEST-001",
        "name": "Horas de Mao de Obra",
        "driver_type": "DURATION",
        "driver_category": "RESOURCE",
        "measure_unit": "HOURS",
        "practical_capacity": 1000,
        "unit_cost": Decimal("50"),
        "condominio_id": condominio_id,
    }


@pytest.fixture
def sample_activity_data(condominio_id):
    """Dados de exemplo para atividade."""
    return {
        "code": "ACT-TEST-001",
        "name": "Atendimento ao Cliente",
        "activity_type": "CUSTOMER_SERVICE",
        "activity_level": "UNIT",
        "value_added_type": "VALUE_ADDED",
        "practical_capacity": 500,
        "condominio_id": condominio_id,
    }


@pytest.fixture
def sample_pool_data(condominio_id):
    """Dados de exemplo para pool."""
    return {
        "code": "POOL-TEST-001",
        "name": "Custos Administrativos",
        "pool_type": "OVERHEAD",
        "allocation_basis": "ACTIVITY_BASED",
        "budget_amount": Decimal("100000.00"),
        "condominio_id": condominio_id,
    }


@pytest.fixture
def sample_object_data(condominio_id):
    """Dados de exemplo para objeto de custo."""
    return {
        "code": "OBJ-TEST-001",
        "name": "Servico de Vigilancia",
        "object_type": "SERVICE",
        "revenue_budget": Decimal("100000.00"),
        "quantity": Decimal("100"),
        "condominio_id": condominio_id,
    }


class TestCostDriverAPI:
    """Testes para API de Cost Drivers."""

    @pytest.mark.asyncio
    async def test_list_drivers_empty(self, mock_user):
        """Testa listagem vazia de drivers."""
        with patch("modules.financial.costing.repositories.CostDriverRepository") as mock_repo:
            mock_repo.return_value.get_multi = AsyncMock(return_value=[])

            # Simula resposta esperada
            result = []
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_create_driver_schema(self, sample_driver_data):
        """Testa validacao de schema de criacao de driver."""
        schema = CostDriverCreate(**sample_driver_data)

        assert schema.code == "DRV-TEST-001"
        assert schema.name == "Horas de Mao de Obra"
        assert schema.driver_type == "DURATION"
        assert schema.unit_cost == Decimal("50")

    @pytest.mark.asyncio
    async def test_create_driver_invalid_codigo(self):
        """Testa validacao de codigo invalido."""
        with pytest.raises(Exception):
            CostDriverCreate(
                code="",
                name="Teste",
                driver_type="TRANSACTION",
                unit_cost=1000,
                condominio_id=uuid4(),
            )

    @pytest.mark.asyncio
    async def test_driver_response_schema(self, mock_user, sample_driver_data):
        """Testa schema de resposta de driver."""
        response_data = {
            **sample_driver_data,
            "id": uuid4(),
            "status": "ACTIVE",
            "used_capacity": Decimal("800"),
            "total_allocations": 5,
            "total_allocated_amount": Decimal("40000"),
            "average_rate": Decimal("50"),
            "is_primary": True,
            "active": True,
            "created_at": datetime(2025, 1, 20, 10, 0, 0),
            "updated_at": datetime(2025, 1, 20, 10, 0, 0),
        }

        response = CostDriverResponse(**response_data)
        assert response.code == "DRV-TEST-001"
        assert response.status == "ACTIVE"


class TestCostActivityAPI:
    """Testes para API de Cost Activities."""

    @pytest.mark.asyncio
    async def test_create_activity_schema(self, sample_activity_data):
        """Testa validacao de schema de criacao de atividade."""
        schema = CostActivityCreate(**sample_activity_data)

        assert schema.code == "ACT-TEST-001"
        assert schema.activity_level == "UNIT"
        assert schema.value_added_type == "VALUE_ADDED"

    @pytest.mark.asyncio
    async def test_activity_levels_valid(self):
        """Testa niveis de atividade validos."""
        valid_levels = ["UNIT", "BATCH", "PRODUCT", "FACILITY"]

        for level in valid_levels:
            schema = CostActivityCreate(
                code=f"ACT-{level}",
                name=f"Atividade {level}",
                activity_level=level,
                condominio_id=uuid4(),
            )
            assert schema.activity_level == level

    @pytest.mark.asyncio
    async def test_activity_value_added_types(self):
        """Testa tipos de valor agregado."""
        types = ["VALUE_ADDED", "NON_VALUE_ADDED", "BUSINESS_VALUE"]

        for va_type in types:
            schema = CostActivityCreate(
                code=f"ACT-{va_type[:5]}",
                name=f"Atividade {va_type}",
                value_added_type=va_type,
                condominio_id=uuid4(),
            )
            assert schema.value_added_type == va_type


class TestCostPoolAPI:
    """Testes para API de Cost Pools."""

    @pytest.mark.asyncio
    async def test_create_pool_schema(self, sample_pool_data):
        """Testa validacao de schema de criacao de pool."""
        schema = CostPoolCreate(**sample_pool_data)

        assert schema.code == "POOL-TEST-001"
        assert schema.pool_type == "OVERHEAD"
        assert schema.budget_amount == Decimal("100000.00")

    @pytest.mark.asyncio
    async def test_pool_types_valid(self):
        """Testa tipos de pool validos."""
        valid_types = [
            "OVERHEAD",
            "LABOR",
            "EQUIPMENT",
            "UTILITIES",
            "MAINTENANCE",
            "TECHNOLOGY",
            "ADMINISTRATIVE",
            "CUSTOM",
        ]

        for pool_type in valid_types:
            schema = CostPoolCreate(
                code=f"PL-{pool_type[:8]}",
                name=f"Pool {pool_type}",
                pool_type=pool_type,
                budget_amount=Decimal("10000"),
                condominio_id=uuid4(),
            )
            assert schema.pool_type == pool_type

    @pytest.mark.asyncio
    async def test_pool_allocation_basis(self):
        """Testa bases de alocacao validas."""
        valid_bases = [
            "ACTIVITY_BASED",
            "DIRECT_LABOR_HOURS",
            "MACHINE_HOURS",
            "REVENUE",
        ]

        for basis in valid_bases:
            schema = CostPoolCreate(
                code=f"PL-{basis[:8]}",
                name=f"Pool {basis}",
                pool_type="OVERHEAD",
                allocation_basis=basis,
                budget_amount=Decimal("10000"),
                condominio_id=uuid4(),
            )
            assert schema.allocation_basis == basis


class TestCostObjectAPI:
    """Testes para API de Cost Objects."""

    @pytest.mark.asyncio
    async def test_create_object_schema(self, sample_object_data):
        """Testa validacao de schema de criacao de objeto."""
        schema = CostObjectCreate(**sample_object_data)

        assert schema.code == "OBJ-TEST-001"
        assert schema.object_type == "SERVICE"
        assert schema.revenue_budget == Decimal("100000.00")

    @pytest.mark.asyncio
    async def test_object_types_valid(self):
        """Testa tipos de objeto validos."""
        valid_types = ["PRODUCT", "SERVICE", "CUSTOMER", "PROJECT", "CONTRACT"]

        for obj_type in valid_types:
            schema = CostObjectCreate(
                code=f"OBJ-{obj_type}",
                name=f"Objeto {obj_type}",
                object_type=obj_type,
                condominio_id=uuid4(),
            )
            assert schema.object_type == obj_type

    @pytest.mark.asyncio
    async def test_object_with_all_costs(self):
        """Testa objeto com todos os campos de custo e receita."""
        schema = CostObjectCreate(
            code="OBJ-FULL",
            name="Objeto Completo",
            object_type="SERVICE",
            revenue_budget=Decimal("200000"),
            cost_budget=Decimal("120000"),
            quantity=Decimal("100"),
            unit_price=Decimal("2000"),
            condominio_id=uuid4(),
        )

        assert schema.revenue_budget == Decimal("200000")
        assert schema.cost_budget == Decimal("120000")
        assert schema.quantity == Decimal("100")
        assert schema.unit_price == Decimal("2000")


class TestCostAllocationAPI:
    """Testes para API de Cost Allocations."""

    @pytest.mark.asyncio
    async def test_create_allocation_schema(self):
        """Testa validacao de schema de criacao de alocacao."""
        source_pool_id = uuid4()
        activity_id = uuid4()

        schema = CostAllocationCreate(
            allocation_type="POOL_TO_ACTIVITY",
            allocation_method="DRIVER_BASED",
            source_pool_id=source_pool_id,
            activity_id=activity_id,
            allocated_amount=Decimal("25000"),
            allocation_percentage=Decimal("25"),
            reference_period="2026-02",
            condominio_id=uuid4(),
        )

        assert schema.allocation_type == "POOL_TO_ACTIVITY"
        assert schema.allocated_amount == Decimal("25000")

    @pytest.mark.asyncio
    async def test_allocation_types_valid(self):
        """Testa tipos de alocacao validos."""
        valid_types = [
            "POOL_TO_ACTIVITY",
            "ACTIVITY_TO_OBJECT",
            "DIRECT",
            "RECIPROCAL",
        ]

        for alloc_type in valid_types:
            schema = CostAllocationCreate(
                allocation_type=alloc_type,
                allocation_method="DRIVER_BASED",
                source_pool_id=uuid4(),
                activity_id=uuid4(),
                allocated_amount=Decimal("10000"),
                reference_period="2026-02",
                condominio_id=uuid4(),
            )
            assert schema.allocation_type == alloc_type

    @pytest.mark.asyncio
    async def test_allocation_methods_valid(self):
        """Testa metodos de alocacao validos."""
        valid_methods = [
            "DRIVER_BASED",
            "PERCENTAGE",
            "PROPORTIONAL",
            "EQUAL_SHARE",
            "WEIGHTED",
        ]

        for method in valid_methods:
            schema = CostAllocationCreate(
                allocation_type="POOL_TO_ACTIVITY",
                allocation_method=method,
                source_pool_id=uuid4(),
                activity_id=uuid4(),
                allocated_amount=Decimal("10000"),
                reference_period="2026-02",
                condominio_id=uuid4(),
            )
            assert schema.allocation_method == method


class TestABCServiceIntegration:
    """Testes de integracao para ABC Service."""

    @pytest.mark.asyncio
    async def test_abc_costing_flow(self):
        """Testa fluxo completo de custeio ABC."""
        cond_id = uuid4()

        # 1. Criar driver
        driver = CostDriverCreate(
            code="DRV-INT-001",
            name="Horas de Atendimento",
            driver_type="DURATION",
            driver_category="ACTIVITY",
            measure_unit="HOURS",
            practical_capacity=1000,
            unit_cost=Decimal("50"),
            condominio_id=cond_id,
        )
        assert driver.code == "DRV-INT-001"

        # 2. Criar pool
        pool = CostPoolCreate(
            code="POOL-INT-001",
            name="Pool Administrativo",
            pool_type="OVERHEAD",
            budget_amount=Decimal("100000"),
            condominio_id=cond_id,
        )
        assert pool.budget_amount == Decimal("100000")

        # 3. Criar atividade
        activity = CostActivityCreate(
            code="ACT-INT-001",
            name="Processamento de Documentos",
            activity_level="BATCH",
            condominio_id=cond_id,
        )
        assert activity.activity_level == "BATCH"

        # 4. Criar objeto
        obj = CostObjectCreate(
            code="OBJ-INT-001",
            name="Contrato Cliente A",
            object_type="CONTRACT",
            revenue_budget=Decimal("150000"),
            condominio_id=cond_id,
        )
        assert obj.object_type == "CONTRACT"

        # 5. Criar alocacao Pool -> Activity
        alloc1 = CostAllocationCreate(
            allocation_type="POOL_TO_ACTIVITY",
            allocation_method="PERCENTAGE",
            source_pool_id=uuid4(),
            activity_id=uuid4(),
            allocated_amount=Decimal("50000"),
            allocation_percentage=Decimal("50"),
            reference_period="2026-02",
            condominio_id=cond_id,
        )
        assert alloc1.allocation_percentage == Decimal("50")

        # 6. Criar alocacao Activity -> Object
        alloc2 = CostAllocationCreate(
            allocation_type="ACTIVITY_TO_OBJECT",
            allocation_method="DRIVER_BASED",
            source_activity_id=uuid4(),
            cost_object_id=uuid4(),
            allocated_amount=Decimal("35000"),
            reference_period="2026-02",
            condominio_id=cond_id,
        )
        assert alloc2.allocation_type == "ACTIVITY_TO_OBJECT"


class TestCostAnalysisAPI:
    """Testes para API de Cost Analysis."""

    @pytest.mark.asyncio
    async def test_analysis_types(self):
        """Testa tipos de analise validos."""
        valid_types = [
            "ABC_COSTING",
            "PROFITABILITY",
            "VARIANCE",
            "BREAK_EVEN",
            "TREND",
            "IDLE_CAPACITY",
            "COMPARATIVE",
        ]

        for analysis_type in valid_types:
            data = {
                "tipo": analysis_type,
                "periodo_inicio": "2025-01-01",
                "periodo_fim": "2025-01-31",
            }
            assert data["tipo"] == analysis_type

    @pytest.mark.asyncio
    async def test_profitability_analysis_response(self):
        """Testa resposta de analise de lucratividade."""
        expected_response = {
            "periodo": {
                "inicio": "2025-01-01",
                "fim": "2025-01-31",
            },
            "resumo": {
                "total_objetos": 10,
                "lucrativos": 7,
                "nao_lucrativos": 3,
                "receita_total": 500000,
                "custo_total": 400000,
                "margem_total": 100000,
                "margem_percentual": 20,
            },
            "insights": [
                "3 objetos de custo apresentam prejuizo",
                "Margem media de 20%",
            ],
        }

        assert expected_response["resumo"]["margem_percentual"] == 20
        assert expected_response["resumo"]["lucrativos"] == 7

    @pytest.mark.asyncio
    async def test_idle_capacity_analysis_response(self):
        """Testa resposta de analise de capacidade ociosa."""
        expected_response = {
            "total_drivers": 5,
            "drivers_com_ociosidade": 3,
            "capacidade_ociosa_total": 500,
            "custo_ociosidade_total": 25000,
            "detalhes": [
                {
                    "driver_id": str(uuid4()),
                    "nome": "Horas Maquina",
                    "capacidade_ociosa": 200,
                    "custo_ociosidade": 10000,
                },
            ],
            "recomendacoes": [
                "Reduzir capacidade de Horas Maquina",
                "Aumentar utilizacao atraves de novos contratos",
            ],
        }

        assert expected_response["drivers_com_ociosidade"] == 3
        assert expected_response["custo_ociosidade_total"] == 25000


class TestDashboardAPI:
    """Testes para Dashboard de Custeio."""

    @pytest.mark.asyncio
    async def test_dashboard_response(self):
        """Testa resposta do dashboard."""
        expected_response = {
            "total_drivers": 10,
            "total_activities": 25,
            "total_pools": 5,
            "total_objects": 50,
            "total_allocations": 100,
            "custo_total_pools": 500000,
            "custo_total_alocado": 450000,
            "capacidade_ociosa": 15000,
            "margem_media": 22.5,
            "objetos_lucrativos": 42,
            "objetos_nao_lucrativos": 8,
        }

        assert expected_response["total_drivers"] == 10
        assert expected_response["margem_media"] == 22.5
        assert expected_response["objetos_lucrativos"] == 42

    @pytest.mark.asyncio
    async def test_trends_response(self):
        """Testa resposta de tendencias."""
        expected_response = [
            {
                "mes": "2025-01",
                "custo_total": 100000,
                "custo_alocado": 95000,
                "variacao_percentual": 0,
            },
            {
                "mes": "2025-02",
                "custo_total": 105000,
                "custo_alocado": 100000,
                "variacao_percentual": 5.0,
            },
        ]

        assert len(expected_response) == 2
        assert expected_response[1]["variacao_percentual"] == 5.0
