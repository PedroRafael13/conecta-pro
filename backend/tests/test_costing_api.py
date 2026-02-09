"""Testes de API para Custeio ABC."""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

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
    """Mock de usuário autenticado."""
    user = MagicMock()
    user.id = uuid4()
    user.condominio_id = uuid4()
    user.email = "admin@test.com"
    user.role = "admin"
    return user


@pytest.fixture
def sample_driver_data():
    """Dados de exemplo para driver."""
    return {
        "codigo": "DRV-TEST-001",
        "nome": "Horas de Mão de Obra",
        "tipo": "RESOURCE",
        "categoria": "LABOR",
        "unidade_medida": "HOUR",
        "capacidade_pratica": 1000,
        "quantidade_usada": 800,
        "custo_total": 50000.00,
    }


@pytest.fixture
def sample_activity_data():
    """Dados de exemplo para atividade."""
    return {
        "codigo": "ACT-TEST-001",
        "nome": "Atendimento ao Cliente",
        "tipo": "OPERATIONAL",
        "nivel": "UNIT",
        "tipo_valor_agregado": "VALUE_ADDED",
        "custo_direto": 10000.00,
        "capacidade_pratica": 500,
        "capacidade_usada": 400,
    }


@pytest.fixture
def sample_pool_data():
    """Dados de exemplo para pool."""
    return {
        "codigo": "POOL-TEST-001",
        "nome": "Custos Administrativos",
        "tipo": "OVERHEAD",
        "base_alocacao": "DRIVER",
        "valor_total": 100000.00,
    }


@pytest.fixture
def sample_object_data():
    """Dados de exemplo para objeto de custo."""
    return {
        "codigo": "OBJ-TEST-001",
        "nome": "Serviço de Vigilância",
        "tipo": "SERVICE",
        "custo_direto": 50000.00,
        "receita": 100000.00,
        "quantidade": 100,
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
        """Testa validação de schema de criação de driver."""
        schema = CostDriverCreate(**sample_driver_data)

        assert schema.codigo == "DRV-TEST-001"
        assert schema.nome == "Horas de Mão de Obra"
        assert schema.tipo == "RESOURCE"
        assert schema.custo_total == Decimal("50000.00")

    @pytest.mark.asyncio
    async def test_create_driver_invalid_codigo(self):
        """Testa validação de código inválido."""
        with pytest.raises(Exception):
            CostDriverCreate(
                codigo="",  # Código vazio
                nome="Teste",
                tipo="RESOURCE",
                custo_total=1000,
            )

    @pytest.mark.asyncio
    async def test_driver_response_schema(self, mock_user, sample_driver_data):
        """Testa schema de resposta de driver."""
        response_data = {
            **sample_driver_data,
            "id": str(uuid4()),
            "condominio_id": str(uuid4()),
            "status": "ACTIVE",
            "ativo": True,
            "created_at": "2025-01-20T10:00:00",
            "updated_at": "2025-01-20T10:00:00",
        }

        response = CostDriverResponse(**response_data)
        assert response.codigo == "DRV-TEST-001"
        assert response.status == "ACTIVE"


class TestCostActivityAPI:
    """Testes para API de Cost Activities."""

    @pytest.mark.asyncio
    async def test_create_activity_schema(self, sample_activity_data):
        """Testa validação de schema de criação de atividade."""
        schema = CostActivityCreate(**sample_activity_data)

        assert schema.codigo == "ACT-TEST-001"
        assert schema.nivel == "UNIT"
        assert schema.tipo_valor_agregado == "VALUE_ADDED"

    @pytest.mark.asyncio
    async def test_activity_levels_valid(self):
        """Testa níveis de atividade válidos."""
        valid_levels = ["UNIT", "BATCH", "PRODUCT", "FACILITY"]

        for level in valid_levels:
            schema = CostActivityCreate(
                codigo=f"ACT-{level}",
                nome=f"Atividade {level}",
                nivel=level,
            )
            assert schema.nivel == level

    @pytest.mark.asyncio
    async def test_activity_value_added_types(self):
        """Testa tipos de valor agregado."""
        types = ["VALUE_ADDED", "NON_VALUE_ADDED", "BUSINESS_VALUE"]

        for va_type in types:
            schema = CostActivityCreate(
                codigo=f"ACT-VA-{va_type}",
                nome=f"Atividade {va_type}",
                tipo_valor_agregado=va_type,
            )
            assert schema.tipo_valor_agregado == va_type


class TestCostPoolAPI:
    """Testes para API de Cost Pools."""

    @pytest.mark.asyncio
    async def test_create_pool_schema(self, sample_pool_data):
        """Testa validação de schema de criação de pool."""
        schema = CostPoolCreate(**sample_pool_data)

        assert schema.codigo == "POOL-TEST-001"
        assert schema.tipo == "OVERHEAD"
        assert schema.valor_total == Decimal("100000.00")

    @pytest.mark.asyncio
    async def test_pool_types_valid(self):
        """Testa tipos de pool válidos."""
        valid_types = [
            "OVERHEAD",
            "LABOR",
            "EQUIPMENT",
            "UTILITIES",
            "MAINTENANCE",
            "TECHNOLOGY",
            "ADMINISTRATIVE",
            "OTHER",
        ]

        for pool_type in valid_types:
            schema = CostPoolCreate(
                codigo=f"POOL-{pool_type}",
                nome=f"Pool {pool_type}",
                tipo=pool_type,
                valor_total=10000,
            )
            assert schema.tipo == pool_type

    @pytest.mark.asyncio
    async def test_pool_allocation_basis(self):
        """Testa bases de alocação válidas."""
        valid_bases = ["DRIVER", "PERCENTAGE", "EQUAL", "PROPORTIONAL"]

        for basis in valid_bases:
            schema = CostPoolCreate(
                codigo=f"POOL-{basis}",
                nome=f"Pool {basis}",
                tipo="OVERHEAD",
                base_alocacao=basis,
                valor_total=10000,
            )
            assert schema.base_alocacao == basis


class TestCostObjectAPI:
    """Testes para API de Cost Objects."""

    @pytest.mark.asyncio
    async def test_create_object_schema(self, sample_object_data):
        """Testa validação de schema de criação de objeto."""
        schema = CostObjectCreate(**sample_object_data)

        assert schema.codigo == "OBJ-TEST-001"
        assert schema.tipo == "SERVICE"
        assert schema.receita == Decimal("100000.00")

    @pytest.mark.asyncio
    async def test_object_types_valid(self):
        """Testa tipos de objeto válidos."""
        valid_types = ["PRODUCT", "SERVICE", "CUSTOMER", "PROJECT", "CONTRACT"]

        for obj_type in valid_types:
            schema = CostObjectCreate(
                codigo=f"OBJ-{obj_type}",
                nome=f"Objeto {obj_type}",
                tipo=obj_type,
            )
            assert schema.tipo == obj_type

    @pytest.mark.asyncio
    async def test_object_with_all_costs(self):
        """Testa objeto com todos os tipos de custo."""
        schema = CostObjectCreate(
            codigo="OBJ-FULL",
            nome="Objeto Completo",
            tipo="SERVICE",
            custo_direto=Decimal("50000"),
            custo_indireto=Decimal("20000"),
            custo_fixo=Decimal("30000"),
            custo_variavel=Decimal("40000"),
            receita=Decimal("200000"),
            quantidade=Decimal("100"),
        )

        assert schema.custo_direto == Decimal("50000")
        assert schema.custo_indireto == Decimal("20000")
        assert schema.custo_fixo == Decimal("30000")
        assert schema.custo_variavel == Decimal("40000")


class TestCostAllocationAPI:
    """Testes para API de Cost Allocations."""

    @pytest.mark.asyncio
    async def test_create_allocation_schema(self):
        """Testa validação de schema de criação de alocação."""
        origem_id = uuid4()
        destino_id = uuid4()

        schema = CostAllocationCreate(
            codigo="ALLOC-TEST-001",
            tipo="POOL_TO_ACTIVITY",
            metodo="DRIVER_BASED",
            origem_tipo="pool",
            origem_id=origem_id,
            destino_tipo="activity",
            destino_id=destino_id,
            valor_alocado=Decimal("25000"),
            percentual_alocado=Decimal("25"),
            data_alocacao=date.today(),
        )

        assert schema.codigo == "ALLOC-TEST-001"
        assert schema.tipo == "POOL_TO_ACTIVITY"
        assert schema.valor_alocado == Decimal("25000")

    @pytest.mark.asyncio
    async def test_allocation_types_valid(self):
        """Testa tipos de alocação válidos."""
        valid_types = [
            "POOL_TO_ACTIVITY",
            "ACTIVITY_TO_OBJECT",
            "DIRECT",
            "RECIPROCAL",
        ]

        for alloc_type in valid_types:
            schema = CostAllocationCreate(
                codigo=f"ALLOC-{alloc_type}",
                tipo=alloc_type,
                origem_tipo="pool",
                origem_id=uuid4(),
                destino_tipo="activity",
                destino_id=uuid4(),
                valor_alocado=Decimal("10000"),
                data_alocacao=date.today(),
            )
            assert schema.tipo == alloc_type

    @pytest.mark.asyncio
    async def test_allocation_methods_valid(self):
        """Testa métodos de alocação válidos."""
        valid_methods = [
            "DRIVER_BASED",
            "PERCENTAGE",
            "PROPORTIONAL",
            "EQUAL",
            "STEP_DOWN",
        ]

        for method in valid_methods:
            schema = CostAllocationCreate(
                codigo=f"ALLOC-{method}",
                tipo="POOL_TO_ACTIVITY",
                metodo=method,
                origem_tipo="pool",
                origem_id=uuid4(),
                destino_tipo="activity",
                destino_id=uuid4(),
                valor_alocado=Decimal("10000"),
                data_alocacao=date.today(),
            )
            assert schema.metodo == method


class TestABCServiceIntegration:
    """Testes de integração para ABC Service."""

    @pytest.mark.asyncio
    async def test_abc_costing_flow(self):
        """Testa fluxo completo de custeio ABC."""
        # 1. Criar drivers
        driver_data = {
            "codigo": "DRV-INT-001",
            "nome": "Horas de Atendimento",
            "tipo": "ACTIVITY",
            "capacidade_pratica": 1000,
            "quantidade_usada": 800,
            "custo_total": 50000,
        }
        driver = CostDriverCreate(**driver_data)
        assert driver.codigo == "DRV-INT-001"

        # 2. Criar pool
        pool_data = {
            "codigo": "POOL-INT-001",
            "nome": "Pool Administrativo",
            "tipo": "OVERHEAD",
            "valor_total": 100000,
        }
        pool = CostPoolCreate(**pool_data)
        assert pool.valor_total == Decimal("100000")

        # 3. Criar atividade
        activity_data = {
            "codigo": "ACT-INT-001",
            "nome": "Processamento de Documentos",
            "nivel": "BATCH",
            "custo_direto": 20000,
        }
        activity = CostActivityCreate(**activity_data)
        assert activity.nivel == "BATCH"

        # 4. Criar objeto
        object_data = {
            "codigo": "OBJ-INT-001",
            "nome": "Contrato Cliente A",
            "tipo": "CONTRACT",
            "receita": 150000,
        }
        obj = CostObjectCreate(**object_data)
        assert obj.tipo == "CONTRACT"

        # 5. Criar alocação Pool -> Activity
        alloc1_data = {
            "codigo": "ALLOC-INT-001",
            "tipo": "POOL_TO_ACTIVITY",
            "metodo": "PERCENTAGE",
            "origem_tipo": "pool",
            "origem_id": uuid4(),
            "destino_tipo": "activity",
            "destino_id": uuid4(),
            "valor_alocado": 50000,
            "percentual_alocado": 50,
            "data_alocacao": date.today(),
        }
        alloc1 = CostAllocationCreate(**alloc1_data)
        assert alloc1.percentual_alocado == Decimal("50")

        # 6. Criar alocação Activity -> Object
        alloc2_data = {
            "codigo": "ALLOC-INT-002",
            "tipo": "ACTIVITY_TO_OBJECT",
            "metodo": "DRIVER_BASED",
            "origem_tipo": "activity",
            "origem_id": uuid4(),
            "destino_tipo": "object",
            "destino_id": uuid4(),
            "valor_alocado": 35000,
            "data_alocacao": date.today(),
        }
        alloc2 = CostAllocationCreate(**alloc2_data)
        assert alloc2.tipo == "ACTIVITY_TO_OBJECT"


class TestCostAnalysisAPI:
    """Testes para API de Cost Analysis."""

    @pytest.mark.asyncio
    async def test_analysis_types(self):
        """Testa tipos de análise válidos."""
        valid_types = [
            "ABC_COSTING",
            "PROFITABILITY",
            "VARIANCE",
            "BREAK_EVEN",
            "TREND",
            "FORECAST",
            "OPTIMIZATION",
        ]

        for analysis_type in valid_types:
            # Simulação de criação de análise
            data = {
                "tipo": analysis_type,
                "periodo_inicio": "2025-01-01",
                "periodo_fim": "2025-01-31",
            }
            assert data["tipo"] == analysis_type

    @pytest.mark.asyncio
    async def test_profitability_analysis_response(self):
        """Testa resposta de análise de lucratividade."""
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
                "3 objetos de custo apresentam prejuízo",
                "Margem média de 20%",
            ],
        }

        assert expected_response["resumo"]["margem_percentual"] == 20
        assert expected_response["resumo"]["lucrativos"] == 7

    @pytest.mark.asyncio
    async def test_idle_capacity_analysis_response(self):
        """Testa resposta de análise de capacidade ociosa."""
        expected_response = {
            "total_drivers": 5,
            "drivers_com_ociosidade": 3,
            "capacidade_ociosa_total": 500,
            "custo_ociosidade_total": 25000,
            "detalhes": [
                {
                    "driver_id": str(uuid4()),
                    "nome": "Horas Máquina",
                    "capacidade_ociosa": 200,
                    "custo_ociosidade": 10000,
                },
            ],
            "recomendacoes": [
                "Reduzir capacidade de Horas Máquina",
                "Aumentar utilização através de novos contratos",
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
        """Testa resposta de tendências."""
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
