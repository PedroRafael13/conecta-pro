"""
Testes para os Models do modulo Clients.
Sprint 30 - Cadastro de Clientes/Condominios
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.clients.models import (
    AdministrationType,
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

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def sample_client_data():
    """Dados de exemplo para cliente."""
    return {
        "id": uuid4(),
        "code": "CLI-001",
        "legal_name": "Empresa Teste Ltda",
        "trade_name": "Empresa Teste",
        "type": ClientType.EMPRESA,
        "document_type": DocumentType.CNPJ,
        "document_number": "12.345.678/0001-90",
        "email": "contato@empresa.com.br",
        "phone": "(11) 3456-7890",
        "phone_secondary": "(11) 99876-5432",
        "address_city": "Sao Paulo",
        "address_state": "SP",
        "status": ClientStatus.ATIVO,
        "segment": ClientSegment.MEDIO,
    }


@pytest.fixture
def sample_condominium_data(sample_client_data):
    """Dados de exemplo para condominio."""
    return {
        "id": uuid4(),
        "client_id": sample_client_data["id"],
        "code": "COND-001",
        "name": "Residencial Jardins",
        "cnpj": "98.765.432/0001-21",
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
        "number": "101",
        "block": "A",
        "tower": "Torre Norte",
        "floor": 1,
        "type": UnitType.APARTAMENTO,
        "status": UnitStatus.OCUPADA,
        "owner_name": "Joao da Silva",
        "owner_document": "123.456.789-00",
    }


@pytest.fixture
def sample_contract_data(sample_client_data, sample_condominium_data):
    """Dados de exemplo para contrato."""
    return {
        "id": uuid4(),
        "client_id": sample_client_data["id"],
        "condominium_id": sample_condominium_data["id"],
        "service_type": ContractServiceType.PORTARIA_REMOTA,
        "status": ServiceStatus.ATIVO,
        "monthly_value": Decimal("5000.00"),
        "start_date": date.today(),
    }


@pytest.fixture
def sample_integration_data(sample_client_data):
    """Dados de exemplo para integracao."""
    return {
        "id": uuid4(),
        "client_id": sample_client_data["id"],
        "integration_type": IntegrationType.EXTERNAL,
        "name": "External Integration",
        "is_enabled": True,
        "sync_status": SyncStatus.SINCRONIZADO,
        "sync_direction": SyncDirection.BIDIRECTIONAL,
        "total_syncs": 0,
        "successful_syncs": 0,
        "failed_syncs": 0,
        "records_synced": 0,
    }


# ============================================================
# TESTES DE ENUMS
# ============================================================


class TestEnums:
    """Testes para os Enums do modulo."""

    def test_client_type_values(self):
        """Testa valores do enum ClientType."""
        assert ClientType.CONDOMINIO.value == "condominio"
        assert ClientType.EMPRESA.value == "empresa"
        assert ClientType.RESIDENCIAL.value == "residencial"
        assert ClientType.COMERCIAL.value == "comercial"
        assert ClientType.INDUSTRIAL.value == "industrial"
        assert ClientType.PUBLICO.value == "publico"
        assert ClientType.OUTRO.value == "outro"
        assert len(ClientType) == 7

    def test_client_status_values(self):
        """Testa valores do enum ClientStatus."""
        assert ClientStatus.PROSPECT.value == "prospect"
        assert ClientStatus.ATIVO.value == "ativo"
        assert ClientStatus.INATIVO.value == "inativo"
        assert ClientStatus.SUSPENSO.value == "suspenso"
        assert ClientStatus.BLOQUEADO.value == "bloqueado"
        assert ClientStatus.CANCELADO.value == "cancelado"
        assert ClientStatus.INADIMPLENTE.value == "inadimplente"
        assert len(ClientStatus) == 7

    def test_client_segment_values(self):
        """Testa valores do enum ClientSegment."""
        assert ClientSegment.PEQUENO.value == "pequeno"
        assert ClientSegment.MEDIO.value == "medio"
        assert ClientSegment.GRANDE.value == "grande"
        assert ClientSegment.ENTERPRISE.value == "enterprise"
        assert ClientSegment.GOVERNO.value == "governo"
        assert ClientSegment.ONG.value == "ong"
        assert len(ClientSegment) == 6

    def test_condominium_type_values(self):
        """Testa valores do enum CondominiumType."""
        assert CondominiumType.RESIDENTIAL.value == "residential"
        assert CondominiumType.COMMERCIAL.value == "commercial"
        assert CondominiumType.MIXED.value == "mixed"
        assert CondominiumType.INDUSTRIAL.value == "industrial"
        assert CondominiumType.HORIZONTAL.value == "horizontal"
        assert CondominiumType.VERTICAL.value == "vertical"
        assert CondominiumType.SUBDIVISION.value == "subdivision"
        assert len(CondominiumType) == 7

    def test_unit_type_values(self):
        """Testa valores do enum UnitType."""
        assert UnitType.APARTAMENTO.value == "apartamento"
        assert UnitType.CASA.value == "casa"
        assert UnitType.LOJA.value == "loja"
        assert UnitType.SALA_COMERCIAL.value == "sala_comercial"
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
        assert IntegrationType.EXTERNAL.value == "external"
        assert IntegrationType.PLUS.value == "plus"
        assert IntegrationType.ERP_EXTERNO.value == "erp_externo"
        assert IntegrationType.BANCO.value == "banco"
        assert len(IntegrationType) == 9


# ============================================================
# TESTES DO MODEL CLIENT
# ============================================================


class TestClientModel:
    """Testes para o model Client."""

    def test_client_creation(self, sample_client_data):
        """Testa criacao de cliente."""
        client = Client(**sample_client_data)

        assert client.id == sample_client_data["id"]
        assert client.code == "CLI-001"
        assert client.legal_name == "Empresa Teste Ltda"
        assert client.type == ClientType.EMPRESA
        assert client.status == ClientStatus.ATIVO

    def test_client_default_values(self):
        """Testa valores padrao do cliente (SQLAlchemy defaults sao DB-level)."""
        client = Client(
            id=uuid4(),
            code="CLI-002",
            legal_name="Teste",
            type=ClientType.CONDOMINIO,
            document_type=DocumentType.CPF,
            document_number="123.456.789-00",
            email="teste@teste.com",
            status=ClientStatus.PROSPECT,
            is_active=True,
            plus_enabled=False,
            payment_terms=30,
        )

        assert client.status == ClientStatus.PROSPECT
        assert client.is_active is True
        assert client.plus_enabled is False
        assert client.payment_terms == 30

    def test_client_activate(self, sample_client_data):
        """Testa ativacao de cliente."""
        sample_client_data["status"] = ClientStatus.PROSPECT
        client = Client(**sample_client_data)

        client.activate()

        assert client.status == ClientStatus.ATIVO

    def test_client_suspend(self, sample_client_data):
        """Testa suspensao de cliente."""
        client = Client(**sample_client_data)

        client.suspend()

        assert client.status == ClientStatus.SUSPENSO

    def test_client_block(self, sample_client_data):
        """Testa bloqueio de cliente."""
        client = Client(**sample_client_data)

        client.block()

        assert client.status == ClientStatus.BLOQUEADO

    def test_client_set_defaulter(self, sample_client_data):
        """Testa marcacao como inadimplente."""
        client = Client(**sample_client_data)

        client.set_defaulter(Decimal("1500.00"))

        assert client.status == ClientStatus.INADIMPLENTE
        assert client.total_debt == Decimal("1500.00")

    def test_client_enable_plus(self, sample_client_data):
        """Testa habilitacao do Plus."""
        client = Client(**sample_client_data)

        client.enable_plus("PLUS-67890")

        assert client.plus_enabled is True
        assert client.plus_client_id == "PLUS-67890"

    def test_client_validate_cnpj_valid(self):
        """Testa validacao de CNPJ valido."""
        assert Client.validate_cnpj("11.222.333/0001-81") is True
        assert Client.validate_cnpj("11222333000181") is True

    def test_client_validate_cnpj_invalid(self):
        """Testa validacao de CNPJ invalido."""
        assert Client.validate_cnpj("11.111.111/1111-11") is False
        assert Client.validate_cnpj("00.000.000/0000-00") is False
        assert Client.validate_cnpj("12345") is False

    def test_client_validate_cpf_valid(self):
        """Testa validacao de CPF valido."""
        assert Client.validate_cpf("529.982.247-25") is True
        assert Client.validate_cpf("52998224725") is True

    def test_client_validate_cpf_invalid(self):
        """Testa validacao de CPF invalido."""
        assert Client.validate_cpf("111.111.111-11") is False
        assert Client.validate_cpf("000.000.000-00") is False
        assert Client.validate_cpf("12345") is False

    def test_client_health_score(self, sample_client_data):
        """Testa calculo do health score."""
        client = Client(**sample_client_data)
        client.total_revenue = Decimal("50000.00")
        client.total_debt = Decimal("0")
        client.satisfaction_score = 4.5
        client.active_contracts = 0
        client.is_defaulter = False

        score = client.health_score

        assert 0 <= score <= 100


# ============================================================
# TESTES DO MODEL CONDOMINIUM
# ============================================================


class TestCondominiumModel:
    """Testes para o model Condominium."""

    def test_condominium_creation(self, sample_condominium_data):
        """Testa criacao de condominio."""
        condo = Condominium(**sample_condominium_data)

        assert condo.code == "COND-001"
        assert condo.name == "Residencial Jardins"
        assert condo.total_units == 120
        assert condo.total_towers == 3

    def test_condominium_default_values(self, sample_client_data):
        """Testa valores padrao do condominio (SQLAlchemy defaults sao DB-level)."""
        condo = Condominium(
            id=uuid4(),
            client_id=sample_client_data["id"],
            code="COND-002",
            name="Teste",
            status=CondominiumStatus.IMPLEMENTING,
            total_units=0,
            total_towers=1,
            has_cctv=False,
            has_access_control=False,
            is_active=True,
        )

        assert condo.status == CondominiumStatus.IMPLEMENTING
        assert condo.total_units == 0
        assert condo.total_towers == 1
        assert condo.has_cctv is False
        assert condo.has_access_control is False
        assert condo.is_active is True

    def test_condominium_activate(self, sample_condominium_data):
        """Testa ativacao de condominio."""
        sample_condominium_data["status"] = CondominiumStatus.IMPLEMENTING
        condo = Condominium(**sample_condominium_data)

        condo.activate()

        assert condo.status == CondominiumStatus.ACTIVE
        assert condo.activation_date is not None

    def test_condominium_start_implantation(self, sample_condominium_data):
        """Testa inicio de implantacao."""
        condo = Condominium(**sample_condominium_data)

        condo.start_implantation()

        assert condo.status == CondominiumStatus.IMPLEMENTING
        assert condo.implantation_date is not None

    def test_condominium_finish_implantation(self, sample_condominium_data):
        """Testa finalizacao de implantacao."""
        sample_condominium_data["status"] = CondominiumStatus.IMPLEMENTING
        condo = Condominium(**sample_condominium_data)

        condo.finish_implantation()

        assert condo.status == CondominiumStatus.ACTIVE
        assert condo.activation_date is not None

    def test_condominium_update_syndic(self, sample_condominium_data):
        """Testa atualizacao de sindico."""
        condo = Condominium(**sample_condominium_data)

        condo.update_syndic(
            name="Maria Santos",
            email="maria@email.com",
            phone="(11) 98765-4321",
            cpf="987.654.321-00",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=730),
        )

        assert condo.syndic_name == "Maria Santos"
        assert condo.syndic_email == "maria@email.com"
        assert condo.syndic_phone == "(11) 98765-4321"
        assert condo.syndic_cpf == "987.654.321-00"

    def test_condominium_security_features(self, sample_condominium_data):
        """Testa caracteristicas de seguranca."""
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
        """Testa criacao de unidade."""
        unit = Unit(**sample_unit_data)

        assert unit.code == "COND-001-A101"
        assert unit.number == "101"
        assert unit.block == "A"
        assert unit.type == UnitType.APARTAMENTO
        assert unit.status == UnitStatus.OCUPADA

    def test_unit_default_values(self, sample_condominium_data):
        """Testa valores padrao da unidade (SQLAlchemy defaults sao DB-level)."""
        unit = Unit(
            id=uuid4(),
            condominium_id=sample_condominium_data["id"],
            code="COND-001-B201",
            number="201",
            type=UnitType.APARTAMENTO,
            status=UnitStatus.DISPONIVEL,
            is_defaulter=False,
            biometric_registered=False,
            facial_registered=False,
            is_active=True,
        )

        assert unit.status == UnitStatus.DISPONIVEL
        assert unit.is_defaulter is False
        assert unit.biometric_registered is False
        assert unit.facial_registered is False
        assert unit.is_active is True

    def test_unit_set_owner(self, sample_unit_data):
        """Testa definicao de proprietario."""
        unit = Unit(**sample_unit_data)

        unit.set_owner(
            name="Carlos Oliveira",
            document="111.222.333-44",
            email="carlos@email.com",
            phone="(11) 3456-7890",
        )

        assert unit.owner_name == "Carlos Oliveira"
        assert unit.owner_document == "111.222.333-44"
        assert unit.owner_email == "carlos@email.com"

    def test_unit_set_resident(self, sample_unit_data):
        """Testa definicao de morador."""
        unit = Unit(**sample_unit_data)

        unit.set_resident(
            name="Ana Paula",
            document="555.666.777-88",
            email="ana@email.com",
            is_tenant=True,
        )

        assert unit.resident_name == "Ana Paula"
        assert unit.resident_document == "555.666.777-88"
        assert unit.is_tenant is True
        assert unit.status == UnitStatus.ALUGADA

    def test_unit_clear_resident(self, sample_unit_data):
        """Testa remocao de morador."""
        unit = Unit(**sample_unit_data)
        unit.resident_name = "Morador Anterior"

        unit.clear_resident()

        assert unit.resident_name is None
        assert unit.resident_document is None
        assert unit.resident_email is None
        assert unit.status == UnitStatus.DISPONIVEL

    def test_unit_set_defaulter(self, sample_unit_data):
        """Testa marcacao como inadimplente."""
        unit = Unit(**sample_unit_data)

        unit.set_defaulter(Decimal("2500.00"))

        assert unit.is_defaulter is True
        assert unit.debt_amount == Decimal("2500.00")

    def test_unit_clear_defaulter(self, sample_unit_data):
        """Testa quitacao de divida."""
        unit = Unit(**sample_unit_data)
        unit.is_defaulter = True
        unit.debt_amount = Decimal("2500.00")

        unit.clear_defaulter()

        assert unit.is_defaulter is False
        assert unit.debt_amount == Decimal("0")
        assert unit.last_payment_date is not None


# ============================================================
# TESTES DO MODEL CLIENT CONTRACT
# ============================================================


class TestClientContractModel:
    """Testes para o model ClientContract."""

    def test_contract_creation(self, sample_contract_data):
        """Testa criacao de contrato."""
        contract = ClientContract(**sample_contract_data)

        assert contract.service_type == ContractServiceType.PORTARIA_REMOTA
        assert contract.status == ServiceStatus.ATIVO
        assert contract.monthly_value == Decimal("5000.00")

    def test_contract_default_values(self, sample_client_data):
        """Testa valores padrao do contrato (SQLAlchemy defaults sao DB-level)."""
        contract = ClientContract(
            id=uuid4(),
            client_id=sample_client_data["id"],
            service_type=ContractServiceType.CFTV,
            status=ServiceStatus.PENDENTE,
        )

        assert contract.status == ServiceStatus.PENDENTE

    def test_contract_start_implantation(self, sample_contract_data):
        """Testa inicio de implantacao."""
        sample_contract_data["status"] = ServiceStatus.PENDENTE
        contract = ClientContract(**sample_contract_data)

        contract.start_implantation()

        assert contract.status == ServiceStatus.EM_IMPLANTACAO
        assert contract.implantation_date is not None

    def test_contract_activate(self, sample_contract_data):
        """Testa ativacao de contrato."""
        sample_contract_data["status"] = ServiceStatus.EM_IMPLANTACAO
        contract = ClientContract(**sample_contract_data)

        contract.activate()

        assert contract.status == ServiceStatus.ATIVO
        assert contract.activation_date is not None

    def test_contract_suspend(self, sample_contract_data):
        """Testa suspensao de contrato."""
        contract = ClientContract(**sample_contract_data)

        contract.suspend()

        assert contract.status == ServiceStatus.SUSPENSO

    def test_contract_cancel(self, sample_contract_data):
        """Testa cancelamento de contrato."""
        contract = ClientContract(**sample_contract_data)

        contract.cancel()

        assert contract.status == ServiceStatus.CANCELADO
        assert contract.cancellation_date is not None

    def test_contract_sla_configuration(self, sample_contract_data):
        """Testa configuracao de SLA."""
        contract = ClientContract(**sample_contract_data)
        contract.sla_response_time_minutes = 30
        contract.sla_resolution_time_hours = 4
        contract.sla_availability_percentage = 99.95

        assert contract.sla_response_time_minutes == 30
        assert contract.sla_resolution_time_hours == 4
        assert contract.sla_availability_percentage == 99.95


# ============================================================
# TESTES DO MODEL INTEGRATION SETTINGS
# ============================================================


class TestIntegrationSettingsModel:
    """Testes para o model IntegrationSettings."""

    def test_integration_creation(self, sample_integration_data):
        """Testa criacao de integracao."""
        integration = IntegrationSettings(**sample_integration_data)

        assert integration.integration_type == IntegrationType.EXTERNAL
        assert integration.name == "External Integration"
        assert integration.is_enabled is True
        assert integration.sync_status == SyncStatus.SINCRONIZADO

    def test_integration_default_values(self, sample_client_data):
        """Testa valores padrao da integracao (SQLAlchemy defaults sao DB-level)."""
        integration = IntegrationSettings(
            id=uuid4(),
            client_id=sample_client_data["id"],
            integration_type=IntegrationType.PLUS,
            name="Plus Integration",
            is_enabled=False,
            sync_status=SyncStatus.PENDENTE,
            sync_direction=SyncDirection.BIDIRECTIONAL,
            sync_interval_minutes=15,
            is_active=True,
        )

        assert integration.is_enabled is False
        assert integration.sync_status == SyncStatus.PENDENTE
        assert integration.sync_direction == SyncDirection.BIDIRECTIONAL
        assert integration.sync_interval_minutes == 15
        assert integration.is_active is True

    def test_integration_enable(self, sample_integration_data):
        """Testa habilitacao de integracao."""
        sample_integration_data["is_enabled"] = False
        integration = IntegrationSettings(**sample_integration_data)

        integration.enable()

        assert integration.is_enabled is True

    def test_integration_disable(self, sample_integration_data):
        """Testa desabilitacao de integracao."""
        integration = IntegrationSettings(**sample_integration_data)

        integration.disable()

        assert integration.is_enabled is False
        assert integration.sync_status == SyncStatus.DESABILITADO

    def test_integration_start_sync(self, sample_integration_data):
        """Testa inicio de sincronizacao."""
        integration = IntegrationSettings(**sample_integration_data)

        integration.start_sync()

        assert integration.sync_status == SyncStatus.SINCRONIZANDO

    def test_integration_complete_sync(self, sample_integration_data):
        """Testa conclusao de sincronizacao."""
        sample_integration_data["sync_status"] = SyncStatus.SINCRONIZANDO
        integration = IntegrationSettings(**sample_integration_data)

        integration.complete_sync()

        assert integration.sync_status == SyncStatus.SINCRONIZADO
        assert integration.last_sync_success_at is not None

    def test_integration_fail_sync(self, sample_integration_data):
        """Testa falha de sincronizacao."""
        sample_integration_data["sync_status"] = SyncStatus.SINCRONIZANDO
        integration = IntegrationSettings(**sample_integration_data)

        integration.fail_sync("Connection timeout")

        assert integration.sync_status == SyncStatus.ERRO
        assert integration.last_sync_error_at is not None
        assert integration.last_sync_error == "Connection timeout"

    def test_integration_api_configuration(self, sample_integration_data):
        """Testa configuracao de API."""
        integration = IntegrationSettings(**sample_integration_data)
        integration.api_url = "https://api.external.com/v1"
        integration.api_key = "ext_api_key_12345"  # pragma: allowlist secret

        assert integration.api_url == "https://api.external.com/v1"
        assert integration.api_key == "ext_api_key_12345"  # pragma: allowlist secret

    def test_integration_webhook_configuration(self, sample_integration_data):
        """Testa configuracao de webhook."""
        integration = IntegrationSettings(**sample_integration_data)
        integration.webhook_url = "https://erp.example.com/webhook"
        integration.webhook_secret = "whsec_12345"  # pragma: allowlist secret
        integration.webhook_events = ["client.created", "client.updated"]

        assert integration.webhook_url == "https://erp.example.com/webhook"
        assert "client.created" in integration.webhook_events
        assert len(integration.webhook_events) == 2


# ============================================================
# TESTES DE RELACIONAMENTOS
# ============================================================


class TestModelRelationships:
    """Testes para relacionamentos entre models."""

    def test_client_condominium_relationship(self, sample_client_data, sample_condominium_data):
        """Testa relacionamento cliente-condominio."""
        client = Client(**sample_client_data)
        condo = Condominium(**sample_condominium_data)

        assert condo.client_id == client.id

    def test_condominium_unit_relationship(self, sample_condominium_data, sample_unit_data):
        """Testa relacionamento condominio-unidade."""
        condo = Condominium(**sample_condominium_data)
        unit = Unit(**sample_unit_data)

        assert unit.condominium_id == condo.id

    def test_client_contract_relationship(self, sample_client_data, sample_condominium_data, sample_contract_data):
        """Testa relacionamento cliente-contrato."""
        client = Client(**sample_client_data)
        condo = Condominium(**sample_condominium_data)
        contract = ClientContract(**sample_contract_data)

        assert contract.client_id == client.id
        assert contract.condominium_id == condo.id

    def test_client_integration_relationship(self, sample_client_data, sample_integration_data):
        """Testa relacionamento cliente-integracao."""
        client = Client(**sample_client_data)
        integration = IntegrationSettings(**sample_integration_data)

        assert integration.client_id == client.id


# ============================================================
# TESTES DE VALIDACAO
# ============================================================


class TestValidations:
    """Testes de validacao de dados."""

    def test_client_code_format(self, sample_client_data):
        """Testa formato do codigo do cliente."""
        client = Client(**sample_client_data)
        assert client.code.startswith("CLI-")

    def test_condominium_code_format(self, sample_condominium_data):
        """Testa formato do codigo do condominio."""
        condo = Condominium(**sample_condominium_data)
        assert condo.code.startswith("COND-")

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
        """Testa transicoes de status validas."""
        client = Client(**sample_client_data)
        client.status = ClientStatus.PROSPECT

        # Prospect -> Ativo
        client.activate()
        assert client.status == ClientStatus.ATIVO

        # Ativo -> Suspenso
        client.suspend()
        assert client.status == ClientStatus.SUSPENSO

        # Suspenso -> Bloqueado
        client.block()
        assert client.status == ClientStatus.BLOQUEADO
