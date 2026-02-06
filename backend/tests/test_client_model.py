"""
Testes para os Models do módulo Clients.
Sprint 30 - Cadastro de Clientes/Condomínios
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from modules.clients.models import (
    Client, Condominium, Unit, ClientContract, IntegrationSettings,
    ClientType, ClientStatus, ClientSegment, DocumentType,
    CondominiumType, CondominiumStatus, AdministrationType,
    UnitType, UnitStatus,
    ContractServiceType, ServiceStatus,
    IntegrationType, SyncStatus, SyncDirection
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def sample_client_data():
    """Dados de exemplo para cliente."""
    return {
        "id": uuid4(),
        "code": "CLI-001",
        "name": "Empresa Teste Ltda",
        "trading_name": "Empresa Teste",
        "client_type": ClientType.PJ,
        "document_type": DocumentType.CNPJ,
        "document_number": "12.345.678/0001-90",
        "email": "contato@empresa.com.br",
        "phone": "(11) 3456-7890",
        "mobile": "(11) 99876-5432",
        "address_city": "São Paulo",
        "address_state": "SP",
        "status": ClientStatus.ACTIVE,
        "segment": ClientSegment.MEDIUM,
    }


@pytest.fixture
def sample_condominium_data(sample_client_data):
    """Dados de exemplo para condomínio."""
    return {
        "id": uuid4(),
        "client_id": sample_client_data["id"],
        "code": "COND-001",
        "name": "Residencial Jardins",
        "cnpj": "98.765.432/0001-21",
        "condominium_type": CondominiumType.RESIDENTIAL,
        "status": CondominiumStatus.ACTIVE,
        "total_units": 120,
        "total_towers": 3,
        "total_floors": 20,
        "has_cctv": True,
        "has_access_control": True,
    }


@pytest.fixture
def sample_unit_data(sample_condominium_data):
    """Dados de exemplo para unidade."""
    return {
        "id": uuid4(),
        "condominium_id": sample_condominium_data["id"],
        "code": "COND-001-A101",
        "unit_number": "101",
        "block": "A",
        "tower": "Torre Norte",
        "floor": 1,
        "unit_type": UnitType.APARTMENT,
        "status": UnitStatus.OCCUPIED,
        "owner_name": "João da Silva",
        "owner_document": "123.456.789-00",
    }


@pytest.fixture
def sample_contract_data(sample_client_data, sample_condominium_data):
    """Dados de exemplo para contrato."""
    return {
        "id": uuid4(),
        "client_id": sample_client_data["id"],
        "condominium_id": sample_condominium_data["id"],
        "contract_number": "CTR-2026-001",
        "service_type": ContractServiceType.PORTARIA_REMOTA,
        "status": ServiceStatus.ACTIVE,
        "monthly_value": Decimal("5000.00"),
        "start_date": date.today(),
    }


@pytest.fixture
def sample_integration_data(sample_client_data):
    """Dados de exemplo para integração."""
    return {
        "id": uuid4(),
        "client_id": sample_client_data["id"],
        "integration_type": IntegrationType.GUARDIAN,
        "name": "Guardian Integration",
        "enabled": True,
        "sync_status": SyncStatus.SYNCED,
        "sync_direction": SyncDirection.BIDIRECTIONAL,
    }


# ============================================================
# TESTES DE ENUMS
# ============================================================

class TestEnums:
    """Testes para os Enums do módulo."""

    def test_client_type_values(self):
        """Testa valores do enum ClientType."""
        assert ClientType.PF.value == "pf"
        assert ClientType.PJ.value == "pj"
        assert ClientType.CONDOMINIUM.value == "condominium"
        assert ClientType.HOLDING.value == "holding"
        assert ClientType.FRANCHISE.value == "franchise"
        assert ClientType.GOVERNMENT.value == "government"
        assert ClientType.OTHER.value == "other"
        assert len(ClientType) == 7

    def test_client_status_values(self):
        """Testa valores do enum ClientStatus."""
        assert ClientStatus.PROSPECT.value == "prospect"
        assert ClientStatus.ACTIVE.value == "active"
        assert ClientStatus.SUSPENDED.value == "suspended"
        assert ClientStatus.BLOCKED.value == "blocked"
        assert ClientStatus.CANCELLED.value == "cancelled"
        assert ClientStatus.DEFAULTER.value == "defaulter"
        assert ClientStatus.CHURNED.value == "churned"
        assert len(ClientStatus) == 7

    def test_client_segment_values(self):
        """Testa valores do enum ClientSegment."""
        assert ClientSegment.SMALL.value == "small"
        assert ClientSegment.MEDIUM.value == "medium"
        assert ClientSegment.LARGE.value == "large"
        assert ClientSegment.ENTERPRISE.value == "enterprise"
        assert ClientSegment.VIP.value == "vip"
        assert ClientSegment.STRATEGIC.value == "strategic"
        assert len(ClientSegment) == 6

    def test_condominium_type_values(self):
        """Testa valores do enum CondominiumType."""
        assert CondominiumType.RESIDENTIAL.value == "residential"
        assert CondominiumType.COMMERCIAL.value == "commercial"
        assert CondominiumType.MIXED.value == "mixed"
        assert CondominiumType.INDUSTRIAL.value == "industrial"
        assert CondominiumType.HORIZONTAL.value == "horizontal"
        assert CondominiumType.GATED_COMMUNITY.value == "gated_community"
        assert CondominiumType.SHOPPING.value == "shopping"
        assert len(CondominiumType) == 7

    def test_unit_type_values(self):
        """Testa valores do enum UnitType."""
        assert UnitType.APARTMENT.value == "apartment"
        assert UnitType.HOUSE.value == "house"
        assert UnitType.STORE.value == "store"
        assert UnitType.OFFICE.value == "office"
        assert len(UnitType) == 14

    def test_contract_service_type_values(self):
        """Testa valores do enum ContractServiceType."""
        assert ContractServiceType.PORTARIA_REMOTA.value == "portaria_remota"
        assert ContractServiceType.CONTROLE_ACESSO.value == "controle_acesso"
        assert ContractServiceType.CFTV.value == "cftv"
        assert ContractServiceType.ALARME.value == "alarme"
        assert len(ContractServiceType) == 15

    def test_integration_type_values(self):
        """Testa valores do enum IntegrationType."""
        assert IntegrationType.GUARDIAN.value == "guardian"
        assert IntegrationType.PLUS.value == "plus"
        assert IntegrationType.ERP_EXTERNAL.value == "erp_external"
        assert IntegrationType.BANKING.value == "banking"
        assert len(IntegrationType) == 9


# ============================================================
# TESTES DO MODEL CLIENT
# ============================================================

class TestClientModel:
    """Testes para o model Client."""

    def test_client_creation(self, sample_client_data):
        """Testa criação de cliente."""
        client = Client(**sample_client_data)

        assert client.id == sample_client_data["id"]
        assert client.code == "CLI-001"
        assert client.name == "Empresa Teste Ltda"
        assert client.client_type == ClientType.PJ
        assert client.status == ClientStatus.ACTIVE

    def test_client_default_values(self):
        """Testa valores padrão do cliente."""
        client = Client(
            id=uuid4(),
            code="CLI-002",
            name="Teste",
            client_type=ClientType.PF,
            document_type=DocumentType.CPF,
            document_number="123.456.789-00",
            email="teste@teste.com",
        )

        assert client.status == ClientStatus.PROSPECT
        assert client.ativo is True
        assert client.guardian_enabled is False
        assert client.plus_enabled is False
        assert client.payment_terms == 30
        assert client.billing_day == 10

    def test_client_activate(self, sample_client_data):
        """Testa ativação de cliente."""
        sample_client_data["status"] = ClientStatus.PROSPECT
        client = Client(**sample_client_data)

        client.activate()

        assert client.status == ClientStatus.ACTIVE

    def test_client_suspend(self, sample_client_data):
        """Testa suspensão de cliente."""
        client = Client(**sample_client_data)

        client.suspend()

        assert client.status == ClientStatus.SUSPENDED

    def test_client_block(self, sample_client_data):
        """Testa bloqueio de cliente."""
        client = Client(**sample_client_data)

        client.block()

        assert client.status == ClientStatus.BLOCKED

    def test_client_set_defaulter(self, sample_client_data):
        """Testa marcação como inadimplente."""
        client = Client(**sample_client_data)

        client.set_defaulter(Decimal("1500.00"))

        assert client.status == ClientStatus.DEFAULTER
        assert client.total_debt == Decimal("1500.00")

    def test_client_enable_guardian(self, sample_client_data):
        """Testa habilitação do Guardian."""
        client = Client(**sample_client_data)

        client.enable_guardian("GRD-12345")

        assert client.guardian_enabled is True
        assert client.guardian_client_id == "GRD-12345"

    def test_client_enable_plus(self, sample_client_data):
        """Testa habilitação do Plus."""
        client = Client(**sample_client_data)

        client.enable_plus("PLUS-67890")

        assert client.plus_enabled is True
        assert client.plus_client_id == "PLUS-67890"

    def test_client_validate_cnpj_valid(self):
        """Testa validação de CNPJ válido."""
        # CNPJ válido de teste
        assert Client.validate_cnpj("11.222.333/0001-81") is True
        assert Client.validate_cnpj("11222333000181") is True

    def test_client_validate_cnpj_invalid(self):
        """Testa validação de CNPJ inválido."""
        assert Client.validate_cnpj("11.111.111/1111-11") is False
        assert Client.validate_cnpj("00.000.000/0000-00") is False
        assert Client.validate_cnpj("12345") is False

    def test_client_validate_cpf_valid(self):
        """Testa validação de CPF válido."""
        # CPF válido de teste
        assert Client.validate_cpf("529.982.247-25") is True
        assert Client.validate_cpf("52998224725") is True

    def test_client_validate_cpf_invalid(self):
        """Testa validação de CPF inválido."""
        assert Client.validate_cpf("111.111.111-11") is False
        assert Client.validate_cpf("000.000.000-00") is False
        assert Client.validate_cpf("12345") is False

    def test_client_calculate_health_score(self, sample_client_data):
        """Testa cálculo do health score."""
        client = Client(**sample_client_data)
        client.total_revenue = Decimal("50000.00")
        client.total_debt = Decimal("0")
        client.satisfaction_score = 4.5
        client.engagement_score = 0.8

        score = client.calculate_health_score()

        assert 0 <= score <= 100
        assert client.health_score == score


# ============================================================
# TESTES DO MODEL CONDOMINIUM
# ============================================================

class TestCondominiumModel:
    """Testes para o model Condominium."""

    def test_condominium_creation(self, sample_condominium_data):
        """Testa criação de condomínio."""
        condo = Condominium(**sample_condominium_data)

        assert condo.code == "COND-001"
        assert condo.name == "Residencial Jardins"
        assert condo.condominium_type == CondominiumType.RESIDENTIAL
        assert condo.total_units == 120
        assert condo.total_towers == 3

    def test_condominium_default_values(self, sample_client_data):
        """Testa valores padrão do condomínio."""
        condo = Condominium(
            id=uuid4(),
            client_id=sample_client_data["id"],
            code="COND-002",
            name="Teste",
            condominium_type=CondominiumType.COMMERCIAL,
        )

        assert condo.status == CondominiumStatus.PROSPECT
        assert condo.total_units == 0
        assert condo.total_towers == 1
        assert condo.total_floors == 1
        assert condo.has_cctv is False
        assert condo.has_access_control is False
        assert condo.ativo is True

    def test_condominium_activate(self, sample_condominium_data):
        """Testa ativação de condomínio."""
        sample_condominium_data["status"] = CondominiumStatus.IMPLANTATION
        condo = Condominium(**sample_condominium_data)

        condo.activate()

        assert condo.status == CondominiumStatus.ACTIVE
        assert condo.activation_date is not None

    def test_condominium_start_implantation(self, sample_condominium_data):
        """Testa início de implantação."""
        sample_condominium_data["status"] = CondominiumStatus.PROSPECT
        condo = Condominium(**sample_condominium_data)

        condo.start_implantation()

        assert condo.status == CondominiumStatus.IMPLANTATION
        assert condo.implantation_start_date is not None

    def test_condominium_finish_implantation(self, sample_condominium_data):
        """Testa finalização de implantação."""
        sample_condominium_data["status"] = CondominiumStatus.IMPLANTATION
        condo = Condominium(**sample_condominium_data)

        condo.finish_implantation()

        assert condo.status == CondominiumStatus.ACTIVE
        assert condo.implantation_end_date is not None
        assert condo.activation_date is not None

    def test_condominium_update_syndic(self, sample_condominium_data):
        """Testa atualização de síndico."""
        condo = Condominium(**sample_condominium_data)

        condo.update_syndic(
            name="Maria Santos",
            email="maria@email.com",
            phone="(11) 98765-4321",
            cpf="987.654.321-00",
            mandate_start=date.today(),
            mandate_end=date.today() + timedelta(days=730),
        )

        assert condo.syndic_name == "Maria Santos"
        assert condo.syndic_email == "maria@email.com"
        assert condo.syndic_phone == "(11) 98765-4321"
        assert condo.syndic_cpf == "987.654.321-00"

    def test_condominium_security_features(self, sample_condominium_data):
        """Testa características de segurança."""
        condo = Condominium(**sample_condominium_data)
        condo.has_cctv = True
        condo.has_access_control = True
        condo.has_24h_security = True
        condo.has_electric_fence = True
        condo.total_cameras = 32
        condo.total_access_points = 8

        assert condo.has_cctv is True
        assert condo.has_access_control is True
        assert condo.has_24h_security is True
        assert condo.total_cameras == 32
        assert condo.total_access_points == 8


# ============================================================
# TESTES DO MODEL UNIT
# ============================================================

class TestUnitModel:
    """Testes para o model Unit."""

    def test_unit_creation(self, sample_unit_data):
        """Testa criação de unidade."""
        unit = Unit(**sample_unit_data)

        assert unit.code == "COND-001-A101"
        assert unit.unit_number == "101"
        assert unit.block == "A"
        assert unit.unit_type == UnitType.APARTMENT
        assert unit.status == UnitStatus.OCCUPIED

    def test_unit_default_values(self, sample_condominium_data):
        """Testa valores padrão da unidade."""
        unit = Unit(
            id=uuid4(),
            condominium_id=sample_condominium_data["id"],
            code="COND-001-B201",
            unit_number="201",
            unit_type=UnitType.APARTMENT,
        )

        assert unit.status == UnitStatus.AVAILABLE
        assert unit.is_defaulter is False
        assert unit.biometric_registered is False
        assert unit.facial_registered is False
        assert unit.app_registered is False
        assert unit.ativo is True

    def test_unit_set_owner(self, sample_unit_data):
        """Testa definição de proprietário."""
        unit = Unit(**sample_unit_data)

        unit.set_owner(
            name="Carlos Oliveira",
            document="111.222.333-44",
            email="carlos@email.com",
            phone="(11) 3456-7890",
            mobile="(11) 98765-4321",
        )

        assert unit.owner_name == "Carlos Oliveira"
        assert unit.owner_document == "111.222.333-44"
        assert unit.owner_email == "carlos@email.com"

    def test_unit_set_resident(self, sample_unit_data):
        """Testa definição de morador."""
        unit = Unit(**sample_unit_data)

        unit.set_resident(
            name="Ana Paula",
            document="555.666.777-88",
            email="ana@email.com",
            resident_type="tenant",
        )

        assert unit.resident_name == "Ana Paula"
        assert unit.resident_document == "555.666.777-88"
        assert unit.resident_type == "tenant"
        assert unit.status == UnitStatus.OCCUPIED

    def test_unit_clear_resident(self, sample_unit_data):
        """Testa remoção de morador."""
        unit = Unit(**sample_unit_data)
        unit.resident_name = "Morador Anterior"

        unit.clear_resident()

        assert unit.resident_name is None
        assert unit.resident_document is None
        assert unit.resident_email is None
        assert unit.status == UnitStatus.VACANT

    def test_unit_set_defaulter(self, sample_unit_data):
        """Testa marcação como inadimplente."""
        unit = Unit(**sample_unit_data)

        unit.set_defaulter(Decimal("2500.00"))

        assert unit.is_defaulter is True
        assert unit.debt_amount == Decimal("2500.00")
        assert unit.status == UnitStatus.DEFAULTER

    def test_unit_clear_debt(self, sample_unit_data):
        """Testa quitação de dívida."""
        sample_unit_data["is_defaulter"] = True
        sample_unit_data["debt_amount"] = Decimal("2500.00")
        sample_unit_data["status"] = UnitStatus.DEFAULTER
        unit = Unit(**sample_unit_data)

        unit.clear_debt()

        assert unit.is_defaulter is False
        assert unit.debt_amount == Decimal("0")
        assert unit.last_payment_date is not None
        assert unit.status == UnitStatus.OCCUPIED


# ============================================================
# TESTES DO MODEL CLIENT CONTRACT
# ============================================================

class TestClientContractModel:
    """Testes para o model ClientContract."""

    def test_contract_creation(self, sample_contract_data):
        """Testa criação de contrato."""
        contract = ClientContract(**sample_contract_data)

        assert contract.contract_number == "CTR-2026-001"
        assert contract.service_type == ContractServiceType.PORTARIA_REMOTA
        assert contract.status == ServiceStatus.ACTIVE
        assert contract.monthly_value == Decimal("5000.00")

    def test_contract_default_values(self, sample_client_data):
        """Testa valores padrão do contrato."""
        contract = ClientContract(
            id=uuid4(),
            client_id=sample_client_data["id"],
            contract_number="CTR-2026-002",
            service_type=ContractServiceType.CFTV,
        )

        assert contract.status == ServiceStatus.PENDING
        assert contract.billing_day == 10
        assert contract.sla_availability == 99.9
        assert contract.auto_renewal is True
        assert contract.renewal_period_months == 12
        assert contract.notice_period_days == 30
        assert contract.ativo is True

    def test_contract_start_implantation(self, sample_contract_data):
        """Testa início de implantação."""
        sample_contract_data["status"] = ServiceStatus.PENDING
        contract = ClientContract(**sample_contract_data)

        contract.start_implantation()

        assert contract.status == ServiceStatus.IMPLANTATION
        assert contract.implantation_start_date is not None

    def test_contract_activate(self, sample_contract_data):
        """Testa ativação de contrato."""
        sample_contract_data["status"] = ServiceStatus.IMPLANTATION
        contract = ClientContract(**sample_contract_data)

        contract.activate()

        assert contract.status == ServiceStatus.ACTIVE
        assert contract.activation_date is not None
        assert contract.implantation_end_date is not None

    def test_contract_suspend(self, sample_contract_data):
        """Testa suspensão de contrato."""
        contract = ClientContract(**sample_contract_data)

        contract.suspend()

        assert contract.status == ServiceStatus.SUSPENDED

    def test_contract_cancel(self, sample_contract_data):
        """Testa cancelamento de contrato."""
        contract = ClientContract(**sample_contract_data)

        contract.cancel()

        assert contract.status == ServiceStatus.CANCELLED
        assert contract.cancellation_date is not None

    def test_contract_sla_configuration(self, sample_contract_data):
        """Testa configuração de SLA."""
        contract = ClientContract(**sample_contract_data)
        contract.sla_response_time = 30  # 30 minutos
        contract.sla_resolution_time = 4  # 4 horas
        contract.sla_availability = 99.95
        contract.sla_config = {
            "max_incidents_month": 5,
            "penalty_percentage": 10,
        }

        assert contract.sla_response_time == 30
        assert contract.sla_resolution_time == 4
        assert contract.sla_availability == 99.95
        assert contract.sla_config["max_incidents_month"] == 5


# ============================================================
# TESTES DO MODEL INTEGRATION SETTINGS
# ============================================================

class TestIntegrationSettingsModel:
    """Testes para o model IntegrationSettings."""

    def test_integration_creation(self, sample_integration_data):
        """Testa criação de integração."""
        integration = IntegrationSettings(**sample_integration_data)

        assert integration.integration_type == IntegrationType.GUARDIAN
        assert integration.name == "Guardian Integration"
        assert integration.enabled is True
        assert integration.sync_status == SyncStatus.SYNCED

    def test_integration_default_values(self, sample_client_data):
        """Testa valores padrão da integração."""
        integration = IntegrationSettings(
            id=uuid4(),
            client_id=sample_client_data["id"],
            integration_type=IntegrationType.PLUS,
            name="Plus Integration",
        )

        assert integration.enabled is False
        assert integration.sync_status == SyncStatus.PENDING
        assert integration.sync_direction == SyncDirection.BIDIRECTIONAL
        assert integration.sync_interval_minutes == 60
        assert integration.ativo is True

    def test_integration_enable(self, sample_integration_data):
        """Testa habilitação de integração."""
        sample_integration_data["enabled"] = False
        integration = IntegrationSettings(**sample_integration_data)

        integration.enable()

        assert integration.enabled is True

    def test_integration_disable(self, sample_integration_data):
        """Testa desabilitação de integração."""
        integration = IntegrationSettings(**sample_integration_data)

        integration.disable()

        assert integration.enabled is False
        assert integration.sync_status == SyncStatus.DISABLED

    def test_integration_start_sync(self, sample_integration_data):
        """Testa início de sincronização."""
        integration = IntegrationSettings(**sample_integration_data)

        integration.start_sync()

        assert integration.sync_status == SyncStatus.SYNCING

    def test_integration_complete_sync(self, sample_integration_data):
        """Testa conclusão de sincronização."""
        sample_integration_data["sync_status"] = SyncStatus.SYNCING
        integration = IntegrationSettings(**sample_integration_data)

        integration.complete_sync()

        assert integration.sync_status == SyncStatus.SYNCED
        assert integration.last_sync_at is not None
        assert integration.last_sync_status == "success"

    def test_integration_fail_sync(self, sample_integration_data):
        """Testa falha de sincronização."""
        sample_integration_data["sync_status"] = SyncStatus.SYNCING
        integration = IntegrationSettings(**sample_integration_data)

        integration.fail_sync("Connection timeout")

        assert integration.sync_status == SyncStatus.ERROR
        assert integration.last_sync_at is not None
        assert integration.last_sync_status == "error"
        assert integration.last_sync_message == "Connection timeout"

    def test_integration_api_configuration(self, sample_integration_data):
        """Testa configuração de API."""
        integration = IntegrationSettings(**sample_integration_data)
        integration.api_url = "https://api.guardian.com/v1"
        integration.api_key = "grd_api_key_12345"
        integration.api_version = "v1"
        integration.auth_type = "api_key"
        integration.auth_config = {"header": "X-API-Key"}

        assert integration.api_url == "https://api.guardian.com/v1"
        assert integration.api_key == "grd_api_key_12345"
        assert integration.auth_type == "api_key"

    def test_integration_webhook_configuration(self, sample_integration_data):
        """Testa configuração de webhook."""
        integration = IntegrationSettings(**sample_integration_data)
        integration.webhook_url = "https://erp.example.com/webhook"
        integration.webhook_secret = "whsec_12345"
        integration.webhook_events = ["client.created", "client.updated"]

        assert integration.webhook_url == "https://erp.example.com/webhook"
        assert "client.created" in integration.webhook_events
        assert len(integration.webhook_events) == 2


# ============================================================
# TESTES DE RELACIONAMENTOS
# ============================================================

class TestModelRelationships:
    """Testes para relacionamentos entre models."""

    def test_client_condominium_relationship(
        self, sample_client_data, sample_condominium_data
    ):
        """Testa relacionamento cliente-condomínio."""
        client = Client(**sample_client_data)
        condo = Condominium(**sample_condominium_data)

        assert condo.client_id == client.id

    def test_condominium_unit_relationship(
        self, sample_condominium_data, sample_unit_data
    ):
        """Testa relacionamento condomínio-unidade."""
        condo = Condominium(**sample_condominium_data)
        unit = Unit(**sample_unit_data)

        assert unit.condominium_id == condo.id

    def test_client_contract_relationship(
        self, sample_client_data, sample_condominium_data, sample_contract_data
    ):
        """Testa relacionamento cliente-contrato."""
        client = Client(**sample_client_data)
        condo = Condominium(**sample_condominium_data)
        contract = ClientContract(**sample_contract_data)

        assert contract.client_id == client.id
        assert contract.condominium_id == condo.id

    def test_client_integration_relationship(
        self, sample_client_data, sample_integration_data
    ):
        """Testa relacionamento cliente-integração."""
        client = Client(**sample_client_data)
        integration = IntegrationSettings(**sample_integration_data)

        assert integration.client_id == client.id


# ============================================================
# TESTES DE VALIDAÇÃO
# ============================================================

class TestValidations:
    """Testes de validação de dados."""

    def test_client_code_format(self, sample_client_data):
        """Testa formato do código do cliente."""
        client = Client(**sample_client_data)
        assert client.code.startswith("CLI-")

    def test_condominium_code_format(self, sample_condominium_data):
        """Testa formato do código do condomínio."""
        condo = Condominium(**sample_condominium_data)
        assert condo.code.startswith("COND-")

    def test_contract_number_format(self, sample_contract_data):
        """Testa formato do número do contrato."""
        contract = ClientContract(**sample_contract_data)
        assert contract.contract_number.startswith("CTR-")

    def test_email_format(self, sample_client_data):
        """Testa formato de email."""
        client = Client(**sample_client_data)
        assert "@" in client.email
        assert "." in client.email

    def test_phone_can_be_none(self, sample_client_data):
        """Testa que telefone pode ser nulo."""
        sample_client_data["phone"] = None
        client = Client(**sample_client_data)
        assert client.phone is None

    def test_status_transitions(self, sample_client_data):
        """Testa transições de status válidas."""
        client = Client(**sample_client_data)
        client.status = ClientStatus.PROSPECT

        # Prospect -> Active
        client.activate()
        assert client.status == ClientStatus.ACTIVE

        # Active -> Suspended
        client.suspend()
        assert client.status == ClientStatus.SUSPENDED

        # Suspended -> Blocked
        client.block()
        assert client.status == ClientStatus.BLOCKED
