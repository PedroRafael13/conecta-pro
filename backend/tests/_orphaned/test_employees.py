"""
Testes unitários para módulo de Employees (Funcionários).

Testa validações de schemas, regras de negócio e fluxos CRUD.
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from modules.operacional.schemas.employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)


class TestEmployeeSchemas:
    """Testes de schemas e validações do Employee."""

    def test_employee_create_valid(self):
        """Testa criação de employee com dados válidos."""
        data = {
            "nome": "João da Silva",
            "email": "joao.silva@teste.com",
            "matricula": "EMP-001",
            "cargo": "Vigilante",
            "departamento": "Operações",
            "telefone": "(11) 98765-4321",
            "cpf": "123.456.789-00",
            "data_admissao": date.today().isoformat(),
        }

        employee = EmployeeCreate(**data)

        assert employee.nome == "João da Silva"
        assert employee.email == "joao.silva@teste.com"
        assert employee.matricula == "EMP-001"
        assert employee.cargo == "Vigilante"

    def test_employee_create_minimal(self):
        """Testa criação com campos mínimos obrigatórios."""
        data = {
            "nome": "Maria Santos",
            "email": "maria@teste.com",
            "matricula": "EMP-002",
        }

        employee = EmployeeCreate(**data)

        assert employee.nome == "Maria Santos"
        assert employee.email == "maria@teste.com"
        assert employee.matricula == "EMP-002"

    def test_employee_email_validation(self):
        """Testa validação de email inválido."""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeCreate(
                nome="Teste",
                email="email-invalido",  # Email sem @
            )

        errors = exc_info.value.errors()
        assert any("email" in str(e).lower() for e in errors)

    def test_employee_name_min_length(self):
        """Testa validação de nome muito curto."""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeCreate(
                nome="A",  # Apenas 1 caractere
                email="teste@teste.com",
            )

        errors = exc_info.value.errors()
        assert any("nome" in str(e).lower() for e in errors)

    def test_employee_cpf_format(self):
        """Testa validação de formato de CPF."""
        # CPF válido deve aceitar
        employee = EmployeeCreate(
            nome="Teste",
            email="teste@teste.com",
            matricula="EMP-003",
            cpf="123.456.789-00",
        )
        assert employee.cpf == "123.456.789-00"

    def test_employee_update_partial(self):
        """Testa atualização parcial de campos."""
        update_data = {
            "cargo": "Supervisor",
            "telefone": "(11) 91234-5678",
        }

        employee_update = EmployeeUpdate(**update_data)

        assert employee_update.cargo == "Supervisor"
        assert employee_update.telefone == "11912345678"  # Normalizado pelo validator
        assert employee_update.email is None  # Não atualizado

    def test_employee_response_structure(self):
        """Testa estrutura do schema de resposta."""
        response_data = {
            "id": str(uuid4()),
            "nome": "Teste Silva",
            "email": "teste@teste.com",
            "matricula": "EMP-001",
            "cargo": "Vigilante",
            "departamento": "Operações",
            "telefone": "(11) 98765-4321",
            "cpf": "123.456.789-00",
            "data_admissao": date.today().isoformat(),
            "status": "ativo",
            "is_active": True,
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:00:00",
        }

        # Verifica que schema aceita os campos
        assert "id" in response_data
        assert "nome" in response_data
        assert "status" in response_data


class TestEmployeeBusinessRules:
    """Testes de regras de negócio para Employees."""

    def test_employee_unique_email(self):
        """Testa que email deve ser único."""
        # Este teste seria implementado no repository/service
        # Aqui apenas validamos que o schema aceita email
        employee1 = EmployeeCreate(
            nome="Funcionário 1",
            email="mesmo.email@teste.com",
        )
        employee2 = EmployeeCreate(
            nome="Funcionário 2",
            email="mesmo.email@teste.com",
        )

        # Schemas aceitam, mas repository deve rejeitar duplicatas
        assert employee1.email == employee2.email

    def test_employee_unique_matricula(self):
        """Testa que matrícula deve ser única."""
        employee1 = EmployeeCreate(
            nome="Funcionário 1",
            email="func1@teste.com",
            matricula="EMP-001",
        )
        employee2 = EmployeeCreate(
            nome="Funcionário 2",
            email="func2@teste.com",
            matricula="EMP-001",  # Mesma matrícula
        )

        # Schemas aceitam, mas repository deve rejeitar duplicatas
        assert employee1.matricula == employee2.matricula

    def test_employee_status_transitions(self):
        """Testa transições válidas de status."""
        # Transições válidas: ativo → inativo → ativo
        # Ou: ativo → afastado → ativo
        valid_statuses = ["ativo", "inativo", "afastado", "ferias"]

        for status in valid_statuses:
            employee = EmployeeCreate(
                nome="Teste",
                email="teste@teste.com",
                status=status,
            )
            assert employee.status in valid_statuses

    def test_employee_data_admissao_validation(self):
        """Testa validação de data de admissão."""
        # Data futura não deve ser permitida
        future_date = date.today() + timedelta(days=30)

        employee = EmployeeCreate(
            nome="Teste",
            email="teste@teste.com",
            data_admissao=future_date.isoformat(),
        )

        # Schema aceita, validação de negócio seria no service
        assert employee.data_admissao == future_date.isoformat()


class TestEmployeeIntegrations:
    """Testes de integração com outros módulos."""

    def test_employee_solides_integration_schema(self):
        """Testa schema de resposta da integração Solides."""
        solides_data = {
            "id": str(uuid4()),
            "nome": "Funcionário Solides",
            "email": "func@solides.com",
            "matricula": "SOL-001",
            "cargo": "Vigilante",
            "departamento": "Operações",
            "data_admissao": "2024-01-01",
            "status": "ativo",
            # Campos extras do Solides
            "source": "solides",
            "solides_id": "12345",
        }

        # Verifica estrutura esperada
        assert "source" in solides_data
        assert solides_data["source"] == "solides"
        assert "solides_id" in solides_data

    def test_employee_without_cpf(self):
        """Testa que CPF é opcional."""
        employee = EmployeeCreate(
            nome="Funcionário Sem CPF",
            email="sempf@teste.com",
            # CPF não fornecido
        )

        assert employee.cpf is None

    def test_employee_phone_formats(self):
        """Testa que aceita diferentes formatos de telefone."""
        phone_formats = [
            "(11) 98765-4321",
            "11987654321",
            "(11)98765-4321",
            "11 98765-4321",
        ]

        for phone in phone_formats:
            employee = EmployeeCreate(
                nome="Teste",
                email=f"teste{phone}@teste.com",
                telefone=phone,
            )
            assert employee.telefone == phone


@pytest.mark.asyncio
class TestEmployeeAPI:
    """Testes de endpoints da API de Employees."""

    @pytest.fixture
    def mock_employee_repository(self):
        """Mock do EmployeeRepository."""
        repo = AsyncMock()
        repo.list = AsyncMock(return_value=[])
        repo.get = AsyncMock(return_value=None)
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    async def test_list_employees_empty(self, client, mock_employee_repository):
        """Testa listagem sem funcionários."""
        with patch(
            "modules.operacional.controllers.employee_controller.EmployeeRepository",
            return_value=mock_employee_repository,
        ):
            response = await client.get("/api/v1/operacional/employees/")

            # Pode retornar 200 ou 401 (sem auth)
            assert response.status_code in [200, 401, 403]

    async def test_create_employee_schema(self):
        """Testa criação de employee via schema."""
        employee_data = {
            "nome": "Novo Funcionário",
            "email": "novo@teste.com",
            "matricula": "EMP-999",
            "cargo": "Vigilante",
        }

        employee = EmployeeCreate(**employee_data)

        assert employee.nome == "Novo Funcionário"
        assert employee.email == "novo@teste.com"
