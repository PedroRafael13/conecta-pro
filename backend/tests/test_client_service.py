"""
Testes para os Services do módulo Clients.
Sprint 30 - Cadastro de Clientes/Condomínios
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.clients.models import (
    Client,
    ClientContract,
    ClientSegment,
    ClientStatus,
    ClientType,
    Condominium,
    CondominiumStatus,
    CondominiumType,
    ContractServiceType,
    DocumentType,
    IntegrationSettings,
    IntegrationType,
    ServiceStatus,
    SyncDirection,
    SyncStatus,
    Unit,
    UnitStatus,
    UnitType,
)
from modules.clients.services import ClientAIService, ClientService

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def mock_repository():
    """Mock do ClientRepository."""
    return MagicMock()


@pytest.fixture
def mock_db():
    """Mock da sessão de banco de dados."""
    return MagicMock()


@pytest.fixture
def client_service(mock_db):
    """Instância do ClientService com mocks."""
    return ClientService(mock_db)


@pytest.fixture
def client_ai_service(mock_db):
    """Instância do ClientAIService com mocks."""
    return ClientAIService(mock_db)


@pytest.fixture
def sample_client():
    """Cliente de exemplo."""
    return Client(
        id=uuid4(),
        code="CLI-001",
        name="Empresa Teste Ltda",
        trading_name="Empresa Teste",
        client_type=ClientType.CONDOMINIO,
        document_type=DocumentType.CNPJ,
        document_number="12.345.678/0001-90",
        email="contato@empresa.com.br",
        phone="(11) 3456-7890",
        status=ClientStatus.ATIVO,
        segment=ClientSegment.PEQUENO,
        total_revenue=Decimal("150000.00"),
        total_debt=Decimal("0"),
        health_score=85.0,
        satisfaction_score=4.5,
        engagement_score=0.75,
        guardian_enabled=True,
        plus_enabled=False,
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_condominium(sample_client):
    """Condomínio de exemplo."""
    return Condominium(
        id=uuid4(),
        client_id=sample_client.id,
        code="COND-001",
        name="Residencial Jardins",
        cnpj="98.765.432/0001-21",
        condominium_type=CondominiumType.RESIDENTIAL,
        status=CondominiumStatus.ACTIVE,
        total_units=120,
        total_towers=3,
        total_floors=20,
        has_cctv=True,
        has_access_control=True,
        has_24h_security=True,
        total_cameras=32,
        total_access_points=8,
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_unit(sample_condominium):
    """Unidade de exemplo."""
    return Unit(
        id=uuid4(),
        condominium_id=sample_condominium.id,
        code="COND-001-A101",
        unit_number="101",
        block="A",
        tower="Torre Norte",
        floor=1,
        unit_type=UnitType.APARTAMENTO,
        status=UnitStatus.DISPONIVEL,
        owner_name="João da Silva",
        owner_document="123.456.789-00",
        owner_email="joao@email.com",
        resident_name="João da Silva",
        resident_type="owner",
        condominium_fee=Decimal("800.00"),
        is_defaulter=False,
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_contract(sample_client, sample_condominium):
    """Contrato de exemplo."""
    return ClientContract(
        id=uuid4(),
        client_id=sample_client.id,
        condominium_id=sample_condominium.id,
        contract_number="CTR-2026-001",
        service_type=ContractServiceType.PORTARIA_REMOTA,
        status=ServiceStatus.ATIVO,
        monthly_value=Decimal("5000.00"),
        start_date=date.today() - timedelta(days=180),
        activation_date=date.today() - timedelta(days=150),
        sla_availability=99.9,
        auto_renewal=True,
        ativo=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# ============================================================
# TESTES DO CLIENT SERVICE
# ============================================================


class TestClientService:
    """Testes para o ClientService."""

    def test_create_client_success(self, client_service, mock_repository):
        """Testa criação de cliente com sucesso."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.create_client.return_value = MagicMock(
                id=uuid4(),
                code="CLI-001",
                name="Novo Cliente",
            )

            result = client_service.create_client(
                {
                    "name": "Novo Cliente",
                    "client_type": "pj",
                    "document_type": "cnpj",
                    "document_number": "11.222.333/0001-44",
                    "email": "novo@cliente.com",
                }
            )

        assert result is not None
        mock_repository.create_client.assert_called_once()

    def test_create_client_duplicate_document(self, client_service, mock_repository):
        """Testa criação de cliente com documento duplicado."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client_by_document.return_value = MagicMock()

            with pytest.raises(ValueError) as exc_info:
                client_service.create_client(
                    {
                        "name": "Cliente Duplicado",
                        "document_number": "11.111.111/0001-11",
                    }
                )

        assert "Documento já cadastrado" in str(exc_info.value)

    def test_get_client_by_id(self, client_service, mock_repository, sample_client):
        """Testa busca de cliente por ID."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client

            result = client_service.get_client(sample_client.id)

        assert result.id == sample_client.id
        assert result.code == "CLI-001"

    def test_get_client_not_found(self, client_service, mock_repository):
        """Testa busca de cliente não encontrado."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = None

            result = client_service.get_client(uuid4())

        assert result is None

    def test_list_clients_with_pagination(self, client_service, mock_repository):
        """Testa listagem de clientes com paginação."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.list_clients.return_value = ([MagicMock()], 10)

            result = client_service.list_clients(skip=0, limit=50)

        assert "items" in result
        assert "total" in result
        mock_repository.list_clients.assert_called_once()

    def test_update_client_success(self, client_service, mock_repository, sample_client):
        """Testa atualização de cliente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            updated_client = MagicMock()
            updated_client.name = "Empresa Atualizada"
            mock_repository.update_client.return_value = updated_client

            result = client_service.update_client(
                sample_client.id,
                {"name": "Empresa Atualizada"},
            )

        assert result.name == "Empresa Atualizada"

    def test_delete_client_success(self, client_service, mock_repository, sample_client):
        """Testa exclusão de cliente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.delete_client.return_value = True

            result = client_service.delete_client(sample_client.id)

        assert result is True

    def test_activate_client(self, client_service, mock_repository, sample_client):
        """Testa ativação de cliente."""
        sample_client.status = ClientStatus.PROSPECT

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.update_client.return_value = sample_client

            result = client_service.activate_client(sample_client.id)

        assert result.status == ClientStatus.ATIVO

    def test_suspend_client(self, client_service, mock_repository, sample_client):
        """Testa suspensão de cliente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.update_client.return_value = sample_client

            result = client_service.suspend_client(sample_client.id)

        assert result.status == ClientStatus.SUSPENSO

    def test_block_client(self, client_service, mock_repository, sample_client):
        """Testa bloqueio de cliente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.update_client.return_value = sample_client

            result = client_service.block_client(sample_client.id)

        assert result.status == ClientStatus.PROSPECT

    def test_set_client_defaulter(self, client_service, mock_repository, sample_client):
        """Testa marcação de cliente como inadimplente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.update_client.return_value = sample_client

            result = client_service.set_client_defaulter(sample_client.id, Decimal("5000.00"))

        assert result.status == ClientStatus.PROSPECT
        assert result.total_debt == Decimal("5000.00")

    def test_enable_guardian(self, client_service, mock_repository, sample_client):
        """Testa habilitação do Guardian."""
        sample_client.guardian_enabled = False

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.update_client.return_value = sample_client

            result = client_service.enable_guardian(sample_client.id, "GRD-12345")

        assert result.guardian_enabled is True
        assert result.guardian_client_id == "GRD-12345"

    def test_enable_plus(self, client_service, mock_repository, sample_client):
        """Testa habilitação do Plus."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.update_client.return_value = sample_client

            result = client_service.enable_plus(sample_client.id, "PLUS-67890")

        assert result.plus_enabled is True
        assert result.plus_client_id == "PLUS-67890"


# ============================================================
# TESTES DO CONDOMINIUM SERVICE
# ============================================================


class TestCondominiumService:
    """Testes para operações de condomínio no ClientService."""

    def test_create_condominium_success(self, client_service, mock_repository, sample_client):
        """Testa criação de condomínio."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.create_condominium.return_value = MagicMock(
                id=uuid4(),
                code="COND-001",
                name="Novo Residencial",
            )

            result = client_service.create_condominium(
                {
                    "client_id": sample_client.id,
                    "name": "Novo Residencial",
                    "condominium_type": "residential",
                }
            )

        assert result is not None
        mock_repository.create_condominium.assert_called_once()

    def test_create_condominium_client_not_found(self, client_service, mock_repository):
        """Testa criação de condomínio com cliente inexistente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = None

            with pytest.raises(ValueError) as exc_info:
                client_service.create_condominium(
                    {
                        "client_id": uuid4(),
                        "name": "Teste",
                    }
                )

        assert "Cliente não encontrado" in str(exc_info.value)

    def test_start_condominium_implantation(self, client_service, mock_repository, sample_condominium):
        """Testa início de implantação de condomínio."""
        sample_condominium.status = CondominiumStatus.ACTIVE

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_condominium.return_value = sample_condominium
            mock_repository.update_condominium.return_value = sample_condominium

            result = client_service.start_condominium_implantation(sample_condominium.id)

        assert result.status == CondominiumStatus.ACTIVE
        assert result.implantation_start_date is not None

    def test_finish_condominium_implantation(self, client_service, mock_repository, sample_condominium):
        """Testa finalização de implantação de condomínio."""
        sample_condominium.status = CondominiumStatus.ACTIVE

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_condominium.return_value = sample_condominium
            mock_repository.update_condominium.return_value = sample_condominium

            result = client_service.finish_condominium_implantation(sample_condominium.id)

        assert result.status == CondominiumStatus.ACTIVE
        assert result.activation_date is not None


# ============================================================
# TESTES DO UNIT SERVICE
# ============================================================


class TestUnitService:
    """Testes para operações de unidade no ClientService."""

    def test_create_unit_success(self, client_service, mock_repository, sample_condominium):
        """Testa criação de unidade."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_condominium.return_value = sample_condominium
            mock_repository.create_unit.return_value = MagicMock(
                id=uuid4(),
                code="COND-001-B201",
                unit_number="201",
            )

            result = client_service.create_unit(
                {
                    "condominium_id": sample_condominium.id,
                    "unit_number": "201",
                    "block": "B",
                    "unit_type": "apartment",
                }
            )

        assert result is not None
        mock_repository.create_unit.assert_called_once()

    def test_set_unit_owner(self, client_service, mock_repository, sample_unit):
        """Testa definição de proprietário da unidade."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_unit.return_value = sample_unit
            mock_repository.update_unit.return_value = sample_unit

            result = client_service.set_unit_owner(
                sample_unit.id,
                name="Novo Proprietário",
                document="999.888.777-66",
                email="novo@email.com",
            )

        assert result.owner_name == "Novo Proprietário"
        assert result.owner_document == "999.888.777-66"

    def test_set_unit_resident(self, client_service, mock_repository, sample_unit):
        """Testa definição de morador da unidade."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_unit.return_value = sample_unit
            mock_repository.update_unit.return_value = sample_unit

            result = client_service.set_unit_resident(
                sample_unit.id,
                name="Inquilino",
                document="111.222.333-44",
                resident_type="tenant",
            )

        assert result.resident_name == "Inquilino"
        assert result.resident_type == "tenant"
        assert result.status == UnitStatus.DISPONIVEL

    def test_set_unit_defaulter(self, client_service, mock_repository, sample_unit):
        """Testa marcação de unidade como inadimplente."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_unit.return_value = sample_unit
            mock_repository.update_unit.return_value = sample_unit

            result = client_service.set_unit_defaulter(sample_unit.id, Decimal("1500.00"))

        assert result.is_defaulter is True
        assert result.debt_amount == Decimal("1500.00")
        assert result.status == UnitStatus.DISPONIVEL

    def test_clear_unit_debt(self, client_service, mock_repository, sample_unit):
        """Testa quitação de dívida da unidade."""
        sample_unit.is_defaulter = True
        sample_unit.debt_amount = Decimal("1500.00")
        sample_unit.status = UnitStatus.DISPONIVEL

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_unit.return_value = sample_unit
            mock_repository.update_unit.return_value = sample_unit

            result = client_service.clear_unit_debt(sample_unit.id)

        assert result.is_defaulter is False
        assert result.debt_amount == Decimal("0")


# ============================================================
# TESTES DO CONTRACT SERVICE
# ============================================================


class TestContractService:
    """Testes para operações de contrato no ClientService."""

    def test_create_contract_success(self, client_service, mock_repository, sample_client):
        """Testa criação de contrato."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.create_contract.return_value = MagicMock(
                id=uuid4(),
                contract_number="CTR-2026-002",
                service_type=ContractServiceType.CFTV,
            )

            result = client_service.create_contract(
                {
                    "client_id": sample_client.id,
                    "service_type": "cftv",
                    "monthly_value": 3000.00,
                }
            )

        assert result is not None
        mock_repository.create_contract.assert_called_once()

    def test_activate_contract(self, client_service, mock_repository, sample_contract):
        """Testa ativação de contrato."""
        sample_contract.status = ServiceStatus.RASCUNHO

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_contract.return_value = sample_contract
            mock_repository.update_contract.return_value = sample_contract

            result = client_service.activate_contract(sample_contract.id)

        assert result.status == ServiceStatus.ATIVO
        assert result.activation_date is not None

    def test_suspend_contract(self, client_service, mock_repository, sample_contract):
        """Testa suspensão de contrato."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_contract.return_value = sample_contract
            mock_repository.update_contract.return_value = sample_contract

            result = client_service.suspend_contract(sample_contract.id)

        assert result.status == ServiceStatus.RASCUNHO

    def test_cancel_contract(self, client_service, mock_repository, sample_contract):
        """Testa cancelamento de contrato."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_contract.return_value = sample_contract
            mock_repository.update_contract.return_value = sample_contract

            result = client_service.cancel_contract(sample_contract.id)

        assert result.status == ServiceStatus.RASCUNHO
        assert result.cancellation_date is not None


# ============================================================
# TESTES DO CLIENT AI SERVICE
# ============================================================


class TestClientAIService:
    """Testes para o ClientAIService."""

    def test_analyze_client_profile(self, client_ai_service, mock_repository, sample_client):
        """Testa análise de perfil do cliente."""
        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.get_client_contracts.return_value = [MagicMock()]
            mock_repository.get_client_condominiums.return_value = [MagicMock()]

            result = client_ai_service.analyze_client_profile(sample_client.id)

        assert "health_score" in result
        assert "engagement_score" in result
        assert "value_score" in result
        assert "risk_level" in result

    def test_suggest_segmentation(self, client_ai_service, mock_repository, sample_client):
        """Testa sugestão de segmentação."""
        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client

            result = client_ai_service.suggest_segmentation(sample_client.id)

        assert "suggested_segment" in result
        assert "confidence" in result
        assert "justification" in result

    def test_predict_churn_risk(self, client_ai_service, mock_repository, sample_client):
        """Testa predição de risco de churn."""
        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client

            result = client_ai_service.predict_churn_risk(sample_client.id)

        assert "churn_probability" in result
        assert "risk_level" in result
        assert "risk_factors" in result
        assert "retention_actions" in result

    def test_predict_churn_risk_high(self, client_ai_service, mock_repository, sample_client):
        """Testa predição de alto risco de churn."""
        sample_client.health_score = 30.0
        sample_client.engagement_score = 0.2
        sample_client.satisfaction_score = 2.0

        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client

            result = client_ai_service.predict_churn_risk(sample_client.id)

        assert result["churn_probability"] > 0.5
        assert result["risk_level"] in ["medium", "high", "critical"]

    def test_recommend_services(self, client_ai_service, mock_repository, sample_client):
        """Testa recomendação de serviços."""
        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.get_client_contracts.return_value = []
            mock_repository.get_client_condominiums.return_value = [
                MagicMock(
                    has_cctv=False,
                    has_access_control=True,
                    total_units=100,
                )
            ]

            result = client_ai_service.recommend_services(sample_client.id)

        assert "recommendations" in result
        assert "potential_revenue" in result
        assert len(result["recommendations"]) > 0

    def test_analyze_condominium_health(self, client_ai_service, mock_repository, sample_condominium):
        """Testa análise de saúde do condomínio."""
        mock_units = [
            MagicMock(status=UnitStatus.DISPONIVEL, is_defaulter=False),
            MagicMock(status=UnitStatus.DISPONIVEL, is_defaulter=False),
            MagicMock(status=UnitStatus.DISPONIVEL, is_defaulter=False),
            MagicMock(status=UnitStatus.DISPONIVEL, is_defaulter=True),
        ]

        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_condominium.return_value = sample_condominium
            mock_repository.get_condominium_units.return_value = mock_units

            result = client_ai_service.analyze_condominium_health(sample_condominium.id)

        assert "overall_score" in result
        assert "occupancy_rate" in result
        assert "defaulter_rate" in result
        assert 0 <= result["occupancy_rate"] <= 1
        assert 0 <= result["defaulter_rate"] <= 1

    def test_get_dashboard_insights(self, client_ai_service, mock_repository):
        """Testa geração de insights do dashboard."""
        with patch.object(client_ai_service, "repository", mock_repository):
            mock_repository.get_client_stats.return_value = {
                "total": 100,
                "active": 85,
            }
            mock_repository.get_condominium_stats.return_value = {
                "total": 150,
                "total_units": 12000,
            }
            mock_repository.get_at_risk_clients.return_value = [MagicMock() for _ in range(5)]

            result = client_ai_service.get_dashboard_insights()

        assert "total_clients" in result
        assert "total_condominiums" in result
        assert "total_units" in result
        assert "top_insights" in result


# ============================================================
# TESTES DE VALIDAÇÃO
# ============================================================


class TestServiceValidations:
    """Testes de validação nos services."""

    def test_validate_cnpj_on_create(self, client_service, mock_repository):
        """Testa validação de CNPJ na criação."""
        with patch.object(client_service, "repository", mock_repository), pytest.raises(ValueError) as exc_info:
            client_service.create_client(
                {
                    "name": "Teste",
                    "client_type": "pj",
                    "document_type": "cnpj",
                    "document_number": "11.111.111/1111-11",  # CNPJ inválido
                    "email": "teste@teste.com",
                }
            )

        assert "CNPJ inválido" in str(exc_info.value)

    def test_validate_cpf_on_create(self, client_service, mock_repository):
        """Testa validação de CPF na criação."""
        with patch.object(client_service, "repository", mock_repository), pytest.raises(ValueError) as exc_info:
            client_service.create_client(
                {
                    "name": "Teste",
                    "client_type": "pf",
                    "document_type": "cpf",
                    "document_number": "111.111.111-11",  # CPF inválido
                    "email": "teste@teste.com",
                }
            )

        assert "CPF inválido" in str(exc_info.value)

    def test_validate_email_format(self, client_service, mock_repository):
        """Testa validação de formato de email."""
        with patch.object(client_service, "repository", mock_repository), pytest.raises(ValueError) as exc_info:
            client_service.create_client(
                {
                    "name": "Teste",
                    "client_type": "pj",
                    "document_type": "cnpj",
                    "document_number": "11.222.333/0001-81",
                    "email": "email-invalido",  # Email inválido
                }
            )

        assert "Email inválido" in str(exc_info.value)

    def test_cannot_activate_blocked_client(self, client_service, mock_repository, sample_client):
        """Testa que não pode ativar cliente bloqueado diretamente."""
        sample_client.status = ClientStatus.PROSPECT

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client

            with pytest.raises(ValueError) as exc_info:
                client_service.activate_client(sample_client.id)

        assert "Cliente bloqueado" in str(exc_info.value)


# ============================================================
# TESTES DE INTEGRAÇÃO
# ============================================================


class TestIntegrationService:
    """Testes para operações de integração no ClientService."""

    def test_create_integration_success(self, client_service, mock_repository, sample_client):
        """Testa criação de integração."""
        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_client.return_value = sample_client
            mock_repository.create_integration.return_value = MagicMock(
                id=uuid4(),
                integration_type=IntegrationType.API_REST,
                enabled=False,
            )

            result = client_service.create_integration(
                {
                    "client_id": sample_client.id,
                    "integration_type": "guardian",
                    "name": "Guardian Integration",
                }
            )

        assert result is not None
        mock_repository.create_integration.assert_called_once()

    def test_enable_integration(self, client_service, mock_repository):
        """Testa habilitação de integração."""
        integration = MagicMock()
        integration.enabled = False

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_integration.return_value = integration
            mock_repository.update_integration.return_value = integration

            result = client_service.enable_integration(uuid4())

        assert result.enabled is True

    def test_disable_integration(self, client_service, mock_repository):
        """Testa desabilitação de integração."""
        integration = MagicMock()
        integration.enabled = True

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_integration.return_value = integration
            mock_repository.update_integration.return_value = integration

            result = client_service.disable_integration(uuid4())

        assert result.enabled is False
        assert result.sync_status == SyncStatus.IDLE

    def test_trigger_sync(self, client_service, mock_repository):
        """Testa disparo de sincronização."""
        integration = MagicMock()
        integration.enabled = True
        integration.sync_status = SyncStatus.IDLE

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_integration.return_value = integration
            mock_repository.update_integration.return_value = integration

            result = client_service.trigger_sync(uuid4())

        assert result.sync_status == SyncStatus.IDLE

    def test_trigger_sync_disabled_integration(self, client_service, mock_repository):
        """Testa disparo de sync em integração desabilitada."""
        integration = MagicMock()
        integration.enabled = False

        with patch.object(client_service, "repository", mock_repository):
            mock_repository.get_integration.return_value = integration

            with pytest.raises(ValueError) as exc_info:
                client_service.trigger_sync(uuid4())

        assert "Integração desabilitada" in str(exc_info.value)
