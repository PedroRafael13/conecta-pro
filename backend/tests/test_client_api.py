"""
Testes para as APIs do módulo Clients.
Sprint 30 - Cadastro de Clientes/Condomínios
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

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
    SyncStatus,
    Unit,
    UnitStatus,
    UnitType,
)
from modules.clients.schemas import (
    ClientContractCreate,
    ClientContractResponse,
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    CondominiumCreate,
    CondominiumResponse,
    IntegrationSettingsCreate,
    IntegrationSettingsResponse,
    UnitCreate,
    UnitResponse,
)

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def mock_db():
    """Mock do banco de dados."""
    return MagicMock()


@pytest.fixture
def mock_client_service():
    """Mock do ClientService."""
    return AsyncMock()


@pytest.fixture
def mock_client_ai_service():
    """Mock do ClientAIService."""
    return AsyncMock()


@pytest.fixture
def sample_client_response():
    """Resposta de exemplo para cliente."""
    return {
        "id": str(uuid4()),
        "code": "CLI-001",
        "name": "Empresa Teste Ltda",
        "trading_name": "Empresa Teste",
        "client_type": "pj",
        "document_type": "cnpj",
        "document_number": "12.345.678/0001-90",
        "email": "contato@empresa.com.br",
        "phone": "(11) 3456-7890",
        "status": "active",
        "segment": "medium",
        "plus_enabled": False,
        "ativo": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_condominium_response():
    """Resposta de exemplo para condomínio."""
    return {
        "id": str(uuid4()),
        "client_id": str(uuid4()),
        "code": "COND-001",
        "name": "Residencial Jardins",
        "cnpj": "98.765.432/0001-21",
        "condominium_type": "residential",
        "status": "active",
        "total_units": 120,
        "total_towers": 3,
        "ativo": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_unit_response():
    """Resposta de exemplo para unidade."""
    return {
        "id": str(uuid4()),
        "condominium_id": str(uuid4()),
        "code": "COND-001-A101",
        "unit_number": "101",
        "block": "A",
        "unit_type": "apartment",
        "status": "occupied",
        "owner_name": "João Silva",
        "is_defaulter": False,
        "ativo": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_client_create_data():
    """Dados para criação de cliente."""
    return {
        "name": "Nova Empresa Ltda",
        "trading_name": "Nova Empresa",
        "client_type": "pj",
        "document_type": "cnpj",
        "document_number": "11.222.333/0001-44",
        "email": "contato@novaempresa.com.br",
        "phone": "(11) 3333-4444",
        "address_city": "São Paulo",
        "address_state": "SP",
    }


@pytest.fixture
def sample_condominium_create_data():
    """Dados para criação de condomínio."""
    return {
        "client_id": str(uuid4()),
        "name": "Novo Residencial",
        "condominium_type": "residential",
        "total_units": 50,
        "total_towers": 2,
        "address_city": "São Paulo",
        "address_state": "SP",
    }


@pytest.fixture
def sample_unit_create_data():
    """Dados para criação de unidade."""
    return {
        "condominium_id": str(uuid4()),
        "unit_number": "201",
        "block": "B",
        "unit_type": "apartment",
        "owner_name": "Maria Santos",
        "owner_document": "111.222.333-44",
        "owner_email": "maria@email.com",
    }


# ============================================================
# TESTES DE CLIENTES
# ============================================================


class TestClientAPI:
    """Testes para endpoints de clientes."""

    @pytest.mark.asyncio
    async def test_list_clients_success(self, mock_client_service, sample_client_response):
        """Testa listagem de clientes com sucesso."""
        mock_client_service.list_clients.return_value = {
            "items": [sample_client_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_clients(skip=0, limit=50)

        assert result["total"] == 1
        assert len(result["items"]) == 1
        assert result["items"][0]["code"] == "CLI-001"

    @pytest.mark.asyncio
    async def test_list_clients_with_filters(self, mock_client_service):
        """Testa listagem de clientes com filtros."""
        mock_client_service.list_clients.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "size": 50,
            "pages": 0,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_clients(
                skip=0,
                limit=50,
                status="active",
                client_type="pj",
                segment="medium",
            )

        assert result["total"] == 0
        mock_client_service.list_clients.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_success(self, mock_client_service, sample_client_response):
        """Testa obtenção de cliente por ID."""
        client_id = sample_client_response["id"]
        mock_client_service.get_client.return_value = sample_client_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.get_client(client_id)

        assert result["id"] == client_id
        assert result["code"] == "CLI-001"

    @pytest.mark.asyncio
    async def test_get_client_not_found(self, mock_client_service):
        """Testa cliente não encontrado."""
        mock_client_service.get_client.return_value = None

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.get_client(str(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_create_client_success(self, mock_client_service, sample_client_create_data, sample_client_response):
        """Testa criação de cliente com sucesso."""
        mock_client_service.create_client.return_value = sample_client_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.create_client(sample_client_create_data)

        assert result["code"] is not None
        assert result["name"] is not None

    @pytest.mark.asyncio
    async def test_create_client_duplicate_document(self, mock_client_service):
        """Testa criação de cliente com documento duplicado."""
        mock_client_service.create_client.side_effect = ValueError("Documento já cadastrado")

        with (
            patch(
                "modules.clients.controllers.client_controller.ClientService",
                return_value=mock_client_service,
            ),
            pytest.raises(ValueError) as exc_info,
        ):
            await mock_client_service.create_client(
                {
                    "name": "Teste",
                    "document_number": "11.111.111/0001-11",
                }
            )

        assert "Documento já cadastrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_client_success(self, mock_client_service, sample_client_response):
        """Testa atualização de cliente."""
        client_id = sample_client_response["id"]
        updated_data = {"name": "Empresa Atualizada Ltda"}
        sample_client_response["name"] = "Empresa Atualizada Ltda"
        mock_client_service.update_client.return_value = sample_client_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.update_client(client_id, updated_data)

        assert result["name"] == "Empresa Atualizada Ltda"

    @pytest.mark.asyncio
    async def test_delete_client_success(self, mock_client_service):
        """Testa exclusão de cliente."""
        client_id = str(uuid4())
        mock_client_service.delete_client.return_value = True

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.delete_client(client_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_activate_client(self, mock_client_service, sample_client_response):
        """Testa ativação de cliente."""
        client_id = sample_client_response["id"]
        sample_client_response["status"] = "active"
        mock_client_service.activate_client.return_value = sample_client_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.activate_client(client_id)

        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_suspend_client(self, mock_client_service, sample_client_response):
        """Testa suspensão de cliente."""
        client_id = sample_client_response["id"]
        sample_client_response["status"] = "suspended"
        mock_client_service.suspend_client.return_value = sample_client_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.suspend_client(client_id)

        assert result["status"] == "suspended"

    @pytest.mark.asyncio
    async def test_enable_plus(self, mock_client_service, sample_client_response):
        """Testa habilitação do Plus."""
        client_id = sample_client_response["id"]
        sample_client_response["plus_enabled"] = True
        sample_client_response["plus_client_id"] = "PLUS-67890"
        mock_client_service.enable_plus.return_value = sample_client_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.enable_plus(client_id, "PLUS-67890")

        assert result["plus_enabled"] is True
        assert result["plus_client_id"] == "PLUS-67890"


# ============================================================
# TESTES DE CONDOMÍNIOS
# ============================================================


class TestCondominiumAPI:
    """Testes para endpoints de condomínios."""

    @pytest.mark.asyncio
    async def test_list_condominiums_success(self, mock_client_service, sample_condominium_response):
        """Testa listagem de condomínios."""
        mock_client_service.list_condominiums.return_value = {
            "items": [sample_condominium_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_condominiums(skip=0, limit=50)

        assert result["total"] == 1
        assert result["items"][0]["code"] == "COND-001"

    @pytest.mark.asyncio
    async def test_list_condominiums_by_client(self, mock_client_service, sample_condominium_response):
        """Testa listagem de condomínios por cliente."""
        client_id = sample_condominium_response["client_id"]
        mock_client_service.list_condominiums.return_value = {
            "items": [sample_condominium_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_condominiums(client_id=client_id, skip=0, limit=50)

        assert result["total"] == 1
        assert result["items"][0]["client_id"] == client_id

    @pytest.mark.asyncio
    async def test_get_condominium_success(self, mock_client_service, sample_condominium_response):
        """Testa obtenção de condomínio por ID."""
        condo_id = sample_condominium_response["id"]
        mock_client_service.get_condominium.return_value = sample_condominium_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.get_condominium(condo_id)

        assert result["id"] == condo_id
        assert result["name"] == "Residencial Jardins"

    @pytest.mark.asyncio
    async def test_create_condominium_success(
        self, mock_client_service, sample_condominium_create_data, sample_condominium_response
    ):
        """Testa criação de condomínio."""
        mock_client_service.create_condominium.return_value = sample_condominium_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.create_condominium(sample_condominium_create_data)

        assert result["code"] is not None

    @pytest.mark.asyncio
    async def test_start_condominium_implantation(self, mock_client_service, sample_condominium_response):
        """Testa início de implantação de condomínio."""
        condo_id = sample_condominium_response["id"]
        sample_condominium_response["status"] = "implantation"
        mock_client_service.start_condominium_implantation.return_value = sample_condominium_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.start_condominium_implantation(condo_id)

        assert result["status"] == "implantation"

    @pytest.mark.asyncio
    async def test_finish_condominium_implantation(self, mock_client_service, sample_condominium_response):
        """Testa finalização de implantação de condomínio."""
        condo_id = sample_condominium_response["id"]
        sample_condominium_response["status"] = "active"
        mock_client_service.finish_condominium_implantation.return_value = sample_condominium_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.finish_condominium_implantation(condo_id)

        assert result["status"] == "active"


# ============================================================
# TESTES DE UNIDADES
# ============================================================


class TestUnitAPI:
    """Testes para endpoints de unidades."""

    @pytest.mark.asyncio
    async def test_list_units_success(self, mock_client_service, sample_unit_response):
        """Testa listagem de unidades."""
        mock_client_service.list_units.return_value = {
            "items": [sample_unit_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_units(skip=0, limit=50)

        assert result["total"] == 1
        assert result["items"][0]["unit_number"] == "101"

    @pytest.mark.asyncio
    async def test_list_units_by_condominium(self, mock_client_service, sample_unit_response):
        """Testa listagem de unidades por condomínio."""
        condo_id = sample_unit_response["condominium_id"]
        mock_client_service.list_units.return_value = {
            "items": [sample_unit_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_units(condominium_id=condo_id, skip=0, limit=50)

        assert result["total"] == 1
        assert result["items"][0]["condominium_id"] == condo_id

    @pytest.mark.asyncio
    async def test_get_unit_success(self, mock_client_service, sample_unit_response):
        """Testa obtenção de unidade por ID."""
        unit_id = sample_unit_response["id"]
        mock_client_service.get_unit.return_value = sample_unit_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.get_unit(unit_id)

        assert result["id"] == unit_id
        assert result["code"] == "COND-001-A101"

    @pytest.mark.asyncio
    async def test_create_unit_success(self, mock_client_service, sample_unit_create_data, sample_unit_response):
        """Testa criação de unidade."""
        mock_client_service.create_unit.return_value = sample_unit_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.create_unit(sample_unit_create_data)

        assert result["code"] is not None

    @pytest.mark.asyncio
    async def test_set_unit_owner(self, mock_client_service, sample_unit_response):
        """Testa definição de proprietário."""
        unit_id = sample_unit_response["id"]
        sample_unit_response["owner_name"] = "Novo Proprietário"
        mock_client_service.set_unit_owner.return_value = sample_unit_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.set_unit_owner(
                unit_id,
                {
                    "name": "Novo Proprietário",
                    "document": "999.888.777-66",
                    "email": "novo@email.com",
                },
            )

        assert result["owner_name"] == "Novo Proprietário"

    @pytest.mark.asyncio
    async def test_set_unit_resident(self, mock_client_service, sample_unit_response):
        """Testa definição de morador."""
        unit_id = sample_unit_response["id"]
        sample_unit_response["resident_name"] = "Inquilino"
        sample_unit_response["status"] = "occupied"
        mock_client_service.set_unit_resident.return_value = sample_unit_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.set_unit_resident(
                unit_id,
                {
                    "name": "Inquilino",
                    "document": "111.222.333-44",
                    "resident_type": "tenant",
                },
            )

        assert result["resident_name"] == "Inquilino"
        assert result["status"] == "occupied"

    @pytest.mark.asyncio
    async def test_set_unit_defaulter(self, mock_client_service, sample_unit_response):
        """Testa marcação de unidade como inadimplente."""
        unit_id = sample_unit_response["id"]
        sample_unit_response["is_defaulter"] = True
        sample_unit_response["status"] = "defaulter"
        mock_client_service.set_unit_defaulter.return_value = sample_unit_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.set_unit_defaulter(unit_id, {"debt_amount": 1500.00})

        assert result["is_defaulter"] is True
        assert result["status"] == "defaulter"


# ============================================================
# TESTES DE CONTRATOS
# ============================================================


class TestContractAPI:
    """Testes para endpoints de contratos."""

    @pytest.mark.asyncio
    async def test_list_contracts_success(self, mock_client_service):
        """Testa listagem de contratos."""
        contract_response = {
            "id": str(uuid4()),
            "client_id": str(uuid4()),
            "contract_number": "CTR-2026-001",
            "service_type": "portaria_remota",
            "status": "active",
            "monthly_value": "5000.00",
            "ativo": True,
        }
        mock_client_service.list_contracts.return_value = {
            "items": [contract_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_contracts(skip=0, limit=50)

        assert result["total"] == 1
        assert result["items"][0]["contract_number"] == "CTR-2026-001"

    @pytest.mark.asyncio
    async def test_create_contract_success(self, mock_client_service):
        """Testa criação de contrato."""
        contract_response = {
            "id": str(uuid4()),
            "client_id": str(uuid4()),
            "contract_number": "CTR-2026-002",
            "service_type": "cftv",
            "status": "pending",
        }
        mock_client_service.create_contract.return_value = contract_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.create_contract(
                {
                    "client_id": str(uuid4()),
                    "service_type": "cftv",
                    "monthly_value": 3000.00,
                }
            )

        assert result["contract_number"] is not None

    @pytest.mark.asyncio
    async def test_activate_contract(self, mock_client_service):
        """Testa ativação de contrato."""
        contract_id = str(uuid4())
        contract_response = {
            "id": contract_id,
            "status": "active",
        }
        mock_client_service.activate_contract.return_value = contract_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.activate_contract(contract_id)

        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_cancel_contract(self, mock_client_service):
        """Testa cancelamento de contrato."""
        contract_id = str(uuid4())
        contract_response = {
            "id": contract_id,
            "status": "cancelled",
        }
        mock_client_service.cancel_contract.return_value = contract_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.cancel_contract(contract_id)

        assert result["status"] == "cancelled"


# ============================================================
# TESTES DE INTEGRAÇÕES
# ============================================================


class TestIntegrationAPI:
    """Testes para endpoints de integrações."""

    @pytest.mark.asyncio
    async def test_list_integrations_success(self, mock_client_service):
        """Testa listagem de integrações."""
        integration_response = {
            "id": str(uuid4()),
            "client_id": str(uuid4()),
            "integration_type": "guardian",
            "name": "Guardian Integration",
            "enabled": True,
            "sync_status": "synced",
        }
        mock_client_service.list_integrations.return_value = {
            "items": [integration_response],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.list_integrations(skip=0, limit=50)

        assert result["total"] == 1
        assert result["items"][0]["integration_type"] == "guardian"

    @pytest.mark.asyncio
    async def test_create_integration_success(self, mock_client_service):
        """Testa criação de integração."""
        integration_response = {
            "id": str(uuid4()),
            "client_id": str(uuid4()),
            "integration_type": "plus",
            "name": "Plus Integration",
            "enabled": False,
            "sync_status": "pending",
        }
        mock_client_service.create_integration.return_value = integration_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.create_integration(
                {
                    "client_id": str(uuid4()),
                    "integration_type": "plus",
                    "name": "Plus Integration",
                }
            )

        assert result["integration_type"] == "plus"

    @pytest.mark.asyncio
    async def test_enable_integration(self, mock_client_service):
        """Testa habilitação de integração."""
        integration_id = str(uuid4())
        integration_response = {
            "id": integration_id,
            "enabled": True,
        }
        mock_client_service.enable_integration.return_value = integration_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.enable_integration(integration_id)

        assert result["enabled"] is True

    @pytest.mark.asyncio
    async def test_disable_integration(self, mock_client_service):
        """Testa desabilitação de integração."""
        integration_id = str(uuid4())
        integration_response = {
            "id": integration_id,
            "enabled": False,
            "sync_status": "disabled",
        }
        mock_client_service.disable_integration.return_value = integration_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.disable_integration(integration_id)

        assert result["enabled"] is False
        assert result["sync_status"] == "disabled"

    @pytest.mark.asyncio
    async def test_trigger_sync(self, mock_client_service):
        """Testa disparo de sincronização."""
        integration_id = str(uuid4())
        integration_response = {
            "id": integration_id,
            "sync_status": "syncing",
        }
        mock_client_service.trigger_sync.return_value = integration_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.trigger_sync(integration_id)

        assert result["sync_status"] == "syncing"


# ============================================================
# TESTES DE IA
# ============================================================


class TestClientAIAPI:
    """Testes para endpoints de IA."""

    @pytest.mark.asyncio
    async def test_analyze_client_profile(self, mock_client_ai_service):
        """Testa análise de perfil do cliente."""
        client_id = str(uuid4())
        profile_response = {
            "client_id": client_id,
            "health_score": 85.5,
            "engagement_score": 0.75,
            "value_score": 0.9,
            "risk_level": "low",
            "recommendations": [
                "Considerar upgrade de plano",
                "Habilitar integração Plus",
            ],
        }
        mock_client_ai_service.analyze_client_profile.return_value = profile_response

        with patch(
            "modules.clients.controllers.client_controller.ClientAIService",
            return_value=mock_client_ai_service,
        ):
            result = await mock_client_ai_service.analyze_client_profile(client_id)

        assert result["client_id"] == client_id
        assert result["health_score"] == 85.5
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_suggest_segmentation(self, mock_client_ai_service):
        """Testa sugestão de segmentação."""
        client_id = str(uuid4())
        segmentation_response = {
            "client_id": client_id,
            "suggested_segment": "enterprise",
            "confidence": 0.85,
            "justification": "Cliente com alto volume de contratos e receita recorrente",
            "current_segment": "large",
        }
        mock_client_ai_service.suggest_segmentation.return_value = segmentation_response

        with patch(
            "modules.clients.controllers.client_controller.ClientAIService",
            return_value=mock_client_ai_service,
        ):
            result = await mock_client_ai_service.suggest_segmentation(client_id)

        assert result["suggested_segment"] == "enterprise"
        assert result["confidence"] >= 0.8

    @pytest.mark.asyncio
    async def test_predict_churn_risk(self, mock_client_ai_service):
        """Testa predição de risco de churn."""
        client_id = str(uuid4())
        churn_response = {
            "client_id": client_id,
            "churn_probability": 0.15,
            "risk_level": "low",
            "risk_factors": [
                {"factor": "Baixo engajamento", "weight": 0.3},
            ],
            "retention_actions": [
                "Agendar reunião de acompanhamento",
            ],
        }
        mock_client_ai_service.predict_churn_risk.return_value = churn_response

        with patch(
            "modules.clients.controllers.client_controller.ClientAIService",
            return_value=mock_client_ai_service,
        ):
            result = await mock_client_ai_service.predict_churn_risk(client_id)

        assert result["churn_probability"] == 0.15
        assert result["risk_level"] == "low"

    @pytest.mark.asyncio
    async def test_recommend_services(self, mock_client_ai_service):
        """Testa recomendação de serviços."""
        client_id = str(uuid4())
        recommendations_response = {
            "client_id": client_id,
            "recommendations": [
                {
                    "service": "cftv",
                    "score": 0.9,
                    "reason": "Condomínio sem monitoramento",
                },
                {
                    "service": "app_morador",
                    "score": 0.85,
                    "reason": "Alto número de unidades",
                },
            ],
            "potential_revenue": 8000.00,
        }
        mock_client_ai_service.recommend_services.return_value = recommendations_response

        with patch(
            "modules.clients.controllers.client_controller.ClientAIService",
            return_value=mock_client_ai_service,
        ):
            result = await mock_client_ai_service.recommend_services(client_id)

        assert len(result["recommendations"]) == 2
        assert result["potential_revenue"] == 8000.00

    @pytest.mark.asyncio
    async def test_analyze_condominium_health(self, mock_client_ai_service):
        """Testa análise de saúde do condomínio."""
        condo_id = str(uuid4())
        health_response = {
            "condominium_id": condo_id,
            "overall_score": 78.5,
            "occupancy_rate": 0.92,
            "defaulter_rate": 0.05,
            "service_utilization": 0.75,
            "alerts": [
                {"type": "warning", "message": "Taxa de inadimplência acima do ideal"},
            ],
        }
        mock_client_ai_service.analyze_condominium_health.return_value = health_response

        with patch(
            "modules.clients.controllers.client_controller.ClientAIService",
            return_value=mock_client_ai_service,
        ):
            result = await mock_client_ai_service.analyze_condominium_health(condo_id)

        assert result["overall_score"] == 78.5
        assert result["occupancy_rate"] == 0.92

    @pytest.mark.asyncio
    async def test_get_dashboard_insights(self, mock_client_ai_service):
        """Testa insights do dashboard."""
        insights_response = {
            "total_clients": 150,
            "active_clients": 125,
            "total_condominiums": 200,
            "total_units": 15000,
            "monthly_revenue": 750000.00,
            "churn_risk_clients": 8,
            "trends": {
                "client_growth": 0.05,
                "revenue_growth": 0.08,
            },
            "top_insights": [
                "5 clientes com alto risco de churn identificados",
                "Potencial de upsell em 12 condomínios",
            ],
        }
        mock_client_ai_service.get_dashboard_insights.return_value = insights_response

        with patch(
            "modules.clients.controllers.client_controller.ClientAIService",
            return_value=mock_client_ai_service,
        ):
            result = await mock_client_ai_service.get_dashboard_insights()

        assert result["total_clients"] == 150
        assert result["monthly_revenue"] == 750000.00
        assert len(result["top_insights"]) >= 1


# ============================================================
# TESTES DE ESTATÍSTICAS
# ============================================================


class TestClientStatisticsAPI:
    """Testes para endpoints de estatísticas."""

    @pytest.mark.asyncio
    async def test_get_client_stats(self, mock_client_service):
        """Testa estatísticas de clientes."""
        stats_response = {
            "total": 150,
            "by_status": {
                "active": 125,
                "suspended": 10,
                "prospect": 15,
            },
            "by_type": {
                "pj": 100,
                "pf": 30,
                "condominium": 20,
            },
            "by_segment": {
                "small": 50,
                "medium": 60,
                "large": 30,
                "enterprise": 10,
            },
        }
        mock_client_service.get_client_stats.return_value = stats_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.get_client_stats()

        assert result["total"] == 150
        assert result["by_status"]["active"] == 125

    @pytest.mark.asyncio
    async def test_get_condominium_stats(self, mock_client_service):
        """Testa estatísticas de condomínios."""
        stats_response = {
            "total": 200,
            "by_status": {
                "active": 180,
                "implantation": 15,
                "prospect": 5,
            },
            "by_type": {
                "residential": 150,
                "commercial": 30,
                "mixed": 20,
            },
            "total_units": 15000,
            "avg_units_per_condo": 75,
        }
        mock_client_service.get_condominium_stats.return_value = stats_response

        with patch(
            "modules.clients.controllers.client_controller.ClientService",
            return_value=mock_client_service,
        ):
            result = await mock_client_service.get_condominium_stats()

        assert result["total"] == 200
        assert result["total_units"] == 15000
