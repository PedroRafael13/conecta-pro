"""
Testes para executores de acao do Bartolo.

Testa:
- resolve_employee() e resolve_post() no BaseActionExecutor
- EmployeeRepository: search_by_name, get_by_matricula, get_by_cpf
- AllocationActionExecutor: previews com nome de funcionário
- ShiftActionExecutor: previews com nome de funcionário
"""

import sys
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from uuid import uuid4

import pytest

sys.path.insert(0, "/app")

from modules.operacional.models.employee import Employee
from modules.operacional.models.post import Post

# ── Fixtures ──────────────────────────────────────────────────────────────


def _make_employee(nome="João Silva", matricula="12345", employee_id=None):
    """Cria mock de Employee."""
    emp = MagicMock(spec=Employee)
    emp.id = employee_id or uuid4()
    emp.nome = nome
    emp.nome_social = None
    emp.matricula = matricula
    emp.cpf = "12345678901"
    emp.cargo = "Vigilante"
    emp.is_active = True
    emp.email = "joao@test.com"
    return emp


def _make_post(name="Condomínio Prime Arena", code="POST-0001", post_id=None):
    """Cria mock de Post."""
    post = MagicMock(spec=Post)
    post.id = post_id or str(uuid4())
    post.name = name
    post.code = code
    post.is_active = True
    return post


# ══════════════════════════════════════════════════════════════════════════
# Testes de resolve_employee
# ══════════════════════════════════════════════════════════════════════════


class TestResolveEmployee:
    """Testa resolve_employee() do BaseActionExecutor."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def executor(self, mock_db):
        """Cria executor concreto para teste (não pode instanciar ABC diretamente)."""
        from modules.ai.bartolo.actions.executors.allocation_executor import AllocationActionExecutor

        return AllocationActionExecutor(mock_db)

    @pytest.mark.asyncio
    async def test_resolve_by_id(self, executor):
        """Testa resolução por UUID."""
        emp = _make_employee()
        with patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_repo:
            mock_repo.return_value.get_by_id = AsyncMock(return_value=emp)
            result, warnings = await executor.resolve_employee({"employee_id": str(emp.id)})

        assert result is not None
        assert result.nome == "João Silva"
        assert len(warnings) == 0

    @pytest.mark.asyncio
    async def test_resolve_by_matricula(self, executor):
        """Testa resolução por matrícula."""
        emp = _make_employee(matricula="54321")
        with patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_repo:
            mock_repo.return_value.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value.get_by_matricula = AsyncMock(return_value=emp)
            result, warnings = await executor.resolve_employee(
                {
                    "employee_id": "invalid-id",
                    "employee_matricula": "54321",
                }
            )

        assert result is not None
        assert result.matricula == "54321"

    @pytest.mark.asyncio
    async def test_resolve_by_name_single(self, executor):
        """Testa resolução por nome com match único."""
        emp = _make_employee(nome="Maria Oliveira")
        with patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            result, warnings = await executor.resolve_employee({"employee_name": "Maria"})

        assert result is not None
        assert result.nome == "Maria Oliveira"
        assert len(warnings) == 0

    @pytest.mark.asyncio
    async def test_resolve_by_name_multiple(self, executor):
        """Testa resolução por nome com múltiplos matches."""
        emp1 = _make_employee(nome="Carlos Santos", matricula="111")
        emp2 = _make_employee(nome="Carlos Oliveira", matricula="222")
        with patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[emp1, emp2])
            result, warnings = await executor.resolve_employee({"employee_name": "Carlos"})

        assert result is not None
        assert result.nome == "Carlos Santos"  # retorna o primeiro
        assert any("Múltiplos" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_resolve_not_found(self, executor):
        """Testa que retorna None quando não encontra."""
        with patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[])
            result, warnings = await executor.resolve_employee({"employee_name": "Inexistente"})

        assert result is None
        assert len(warnings) > 0

    @pytest.mark.asyncio
    async def test_resolve_no_params(self, executor):
        """Testa que retorna warning quando nenhum param é fornecido."""
        result, warnings = await executor.resolve_employee({})

        assert result is None
        assert any("não informado" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_resolve_id_fallback_to_name(self, executor):
        """Testa fallback de ID para nome."""
        emp = _make_employee(nome="Roberto Lima")
        with patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_repo:
            mock_repo.return_value.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            result, warnings = await executor.resolve_employee(
                {
                    "employee_id": "id-invalido",
                    "employee_name": "Roberto",
                }
            )

        assert result is not None
        assert result.nome == "Roberto Lima"
        assert any("não encontrado por ID" in w for w in warnings)


# ══════════════════════════════════════════════════════════════════════════
# Testes de resolve_post (cobertura adicional)
# ══════════════════════════════════════════════════════════════════════════


class TestResolvePost:
    """Testa resolve_post() do BaseActionExecutor."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def executor(self, mock_db):
        from modules.ai.bartolo.actions.executors.allocation_executor import AllocationActionExecutor

        return AllocationActionExecutor(mock_db)

    @pytest.mark.asyncio
    async def test_resolve_by_code(self, executor):
        """Testa resolução por código."""
        post = _make_post()
        with patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_repo:
            mock_repo.return_value.get_by_code = AsyncMock(return_value=post)
            result, warnings = await executor.resolve_post({"post_code": "POST-0001"})

        assert result is not None
        assert result.code == "POST-0001"
        assert len(warnings) == 0

    @pytest.mark.asyncio
    async def test_resolve_by_name(self, executor):
        """Testa resolução por nome."""
        post = _make_post(name="Residencial Villa Fiori")
        with patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[post])
            result, warnings = await executor.resolve_post({"post_name": "villa fiori"})

        assert result is not None
        assert "Villa Fiori" in result.name

    @pytest.mark.asyncio
    async def test_resolve_code_fallback_to_name(self, executor):
        """Testa fallback de código para nome."""
        post = _make_post()
        with patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_repo:
            mock_repo.return_value.get_by_code = AsyncMock(return_value=None)
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[post])
            result, warnings = await executor.resolve_post(
                {
                    "post_code": "POST-9999",
                    "post_name": "prime",
                }
            )

        assert result is not None
        assert any("não encontrado por código" in w for w in warnings)


# ══════════════════════════════════════════════════════════════════════════
# Testes de AllocationActionExecutor
# ══════════════════════════════════════════════════════════════════════════


class TestAllocationExecutor:
    """Testa AllocationActionExecutor com resolve_employee."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def executor(self, mock_db):
        from modules.ai.bartolo.actions.executors.allocation_executor import AllocationActionExecutor

        exec_ = AllocationActionExecutor(mock_db)
        exec_.user_role = "admin"
        return exec_

    @pytest.mark.asyncio
    async def test_allocate_preview_with_name(self, executor):
        """Testa preview de alocação usando nome do funcionário."""
        emp = _make_employee(nome="Ana Beatriz")
        post = _make_post()
        from modules.ai.bartolo.actions.action_schemas import ActionRequest
        from modules.ai.bartolo.actions.action_types import ActionCategory, ActionType

        request = ActionRequest(
            action_type=ActionType.ALLOCATE_EMPLOYEE,
            category=ActionCategory.OPERATIONAL,
            parameters={"employee_name": "Ana", "post_code": "POST-0001"},
            detected_from_message="alocar funcionária Ana no posto 1",
            confidence=0.9,
            user_id="u1",
            session_id="s1",
        )

        with (
            patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_emp_repo,
            patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_post_repo,
            patch("modules.ai.bartolo.actions.executors.allocation_executor.AllocationRepository") as mock_alloc_repo,
        ):
            mock_emp_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            mock_post_repo.return_value.get_by_code = AsyncMock(return_value=post)
            mock_alloc_repo.return_value.get_current_by_employee = AsyncMock(return_value=[])

            preview = await executor.create_preview(request)

        assert preview is not None
        assert "Ana Beatriz" in preview.title
        assert any("Ana Beatriz" in s for s in preview.changes_summary)
        # resolve_employee propagou employee_id
        assert request.parameters.get("employee_id") == str(emp.id)

    @pytest.mark.asyncio
    async def test_transfer_preview_with_employee_name(self, executor):
        """Testa preview de transferência usando nome do funcionário."""
        emp = _make_employee(nome="Pedro Henrique")
        target_post = _make_post(name="Posto Central", code="POST-0002")
        from modules.ai.bartolo.actions.action_schemas import ActionRequest
        from modules.ai.bartolo.actions.action_types import ActionCategory, ActionType

        request = ActionRequest(
            action_type=ActionType.TRANSFER_EMPLOYEE,
            category=ActionCategory.OPERATIONAL,
            parameters={"employee_name": "Pedro", "post_code": "POST-0002"},
            detected_from_message="transferir o Pedro para posto central",
            confidence=0.9,
            user_id="u1",
            session_id="s1",
        )

        with (
            patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_emp_repo,
            patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_post_repo,
            patch("modules.ai.bartolo.actions.executors.allocation_executor.AllocationRepository") as mock_alloc_repo,
        ):
            mock_emp_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            mock_post_repo.return_value.get_by_code = AsyncMock(return_value=target_post)
            mock_alloc_repo.return_value.get_current_by_employee = AsyncMock(return_value=[])

            preview = await executor.create_preview(request)

        assert preview is not None
        assert "Pedro Henrique" in preview.title


# ══════════════════════════════════════════════════════════════════════════
# Testes de ShiftActionExecutor
# ══════════════════════════════════════════════════════════════════════════


class TestShiftExecutor:
    """Testa ShiftActionExecutor com resolve_employee."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def executor(self, mock_db):
        from modules.ai.bartolo.actions.executors.shift_executor import ShiftActionExecutor

        exec_ = ShiftActionExecutor(mock_db)
        exec_.user_role = "admin"
        return exec_

    @pytest.mark.asyncio
    async def test_create_shift_preview_with_name(self, executor):
        """Testa preview de criação de turno com nome do funcionário."""
        emp = _make_employee(nome="Roberto Lima")
        post = _make_post()
        from modules.ai.bartolo.actions.action_schemas import ActionRequest
        from modules.ai.bartolo.actions.action_types import ActionCategory, ActionType

        request = ActionRequest(
            action_type=ActionType.CREATE_SHIFT,
            category=ActionCategory.OPERATIONAL,
            parameters={
                "employee_name": "Roberto",
                "post_code": "POST-0001",
                "scale_id": str(uuid4()),
                "shift_date": date.today().isoformat(),
            },
            detected_from_message="criar turno vigilante Roberto no posto 1",
            confidence=0.9,
            user_id="u1",
            session_id="s1",
        )

        with (
            patch("modules.ai.bartolo.actions.executors.base_executor.EmployeeRepository") as mock_emp_repo,
            patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_post_repo,
            patch("modules.ai.bartolo.actions.executors.shift_executor.ShiftRepository") as mock_shift_repo,
        ):
            mock_emp_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            mock_post_repo.return_value.get_by_code = AsyncMock(return_value=post)
            mock_shift_repo.return_value.get_by_employee_and_date = AsyncMock(return_value=[])

            preview = await executor.create_preview(request)

        assert preview is not None
        assert "Roberto Lima" in preview.title
        assert any("Roberto Lima" in s for s in preview.changes_summary)

    @pytest.mark.asyncio
    async def test_create_shift_preview_no_employee(self, executor):
        """Testa preview de turno vago (sem funcionário)."""
        post = _make_post()
        from modules.ai.bartolo.actions.action_schemas import ActionRequest
        from modules.ai.bartolo.actions.action_types import ActionCategory, ActionType

        request = ActionRequest(
            action_type=ActionType.CREATE_SHIFT,
            category=ActionCategory.OPERATIONAL,
            parameters={
                "post_code": "POST-0001",
                "scale_id": str(uuid4()),
            },
            detected_from_message="criar turno no posto 1",
            confidence=0.9,
            user_id="u1",
            session_id="s1",
        )

        with patch("modules.ai.bartolo.actions.executors.base_executor.PostRepository") as mock_post_repo:
            mock_post_repo.return_value.get_by_code = AsyncMock(return_value=post)

            preview = await executor.create_preview(request)

        assert preview is not None
        assert any("Não alocado" in s for s in preview.changes_summary)


# ══════════════════════════════════════════════════════════════════════════
# Testes de EmployeeRepository
# ══════════════════════════════════════════════════════════════════════════


class TestEmployeeRepository:
    """Testa EmployeeRepository (lógica de construção de queries)."""

    def test_import(self):
        """Testa que EmployeeRepository importa corretamente."""
        from modules.operacional.repositories.employee_repository import EmployeeRepository

        assert EmployeeRepository is not None

    def test_in_init(self):
        """Testa que EmployeeRepository está no __init__.py."""
        from modules.operacional.repositories import EmployeeRepository

        assert EmployeeRepository is not None

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Testa get_by_id quando não encontra."""
        from modules.operacional.repositories.employee_repository import EmployeeRepository

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = EmployeeRepository(mock_db)
        result = await repo.get_by_id("invalid-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_search_by_name_empty(self):
        """Testa search_by_name com string vazia."""
        from modules.operacional.repositories.employee_repository import EmployeeRepository

        mock_db = AsyncMock()
        repo = EmployeeRepository(mock_db)
        result = await repo.search_by_name("")
        assert result == []
        # Não deve ter chamado o banco
        mock_db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_by_name_short_words_ignored(self):
        """Testa que palavras com menos de 2 caracteres são ignoradas."""
        from modules.operacional.repositories.employee_repository import EmployeeRepository

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        repo = EmployeeRepository(mock_db)
        result = await repo.search_by_name("a")  # palavra muito curta
        # Com apenas 1 char, não gera filtro ILIKE mas ainda executa query base
        assert result == []


# ══════════════════════════════════════════════════════════════════════════
# Testes de DataConnector.search_entity
# ══════════════════════════════════════════════════════════════════════════


class TestSearchEntity:
    """Testa search_entity() do DataConnector."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.fixture
    def connector(self, mock_db):
        from modules.ai.bartolo.services.data_connector import DataConnector

        dc = DataConnector(db_session=mock_db)
        return dc

    @pytest.mark.asyncio
    async def test_search_employee_uses_employee_repo(self, connector):
        """Testa que busca de funcionário usa EmployeeRepository.search_by_name."""
        emp = _make_employee(nome="Carlos Santos")
        with patch("modules.ai.bartolo.services.data_connector.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            result = await connector.search_entity("funcionario", "Carlos")
        assert len(result) == 1
        assert result[0].nome == "Carlos Santos"
        mock_repo.return_value.search_by_name.assert_called_once_with("Carlos", limit=5)

    @pytest.mark.asyncio
    async def test_search_colaborador_uses_employee_repo(self, connector):
        """Testa que 'colaborador' também roteia para EmployeeRepository."""
        emp = _make_employee(nome="Ana Lima")
        with patch("modules.ai.bartolo.services.data_connector.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            result = await connector.search_entity("colaborador", "Ana")
        assert len(result) == 1
        assert result[0].nome == "Ana Lima"

    @pytest.mark.asyncio
    async def test_search_post_uses_post_repo(self, connector):
        """Testa que busca de posto usa PostRepository.search_by_name."""
        post = _make_post(name="Condomínio Laranjeiras")
        with patch("modules.ai.bartolo.services.data_connector.PostRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[post])
            result = await connector.search_entity("posto", "Laranjeiras")
        assert len(result) == 1
        assert result[0].name == "Condomínio Laranjeiras"
        mock_repo.return_value.search_by_name.assert_called_once_with("Laranjeiras", limit=5)

    @pytest.mark.asyncio
    async def test_search_postos_plural(self, connector):
        """Testa que 'postos' (plural) também funciona."""
        post = _make_post(name="Base Conecta")
        with patch("modules.ai.bartolo.services.data_connector.PostRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[post])
            result = await connector.search_entity("postos", "Conecta")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_search_diarist_generic_ilike(self, connector, mock_db):
        """Testa busca genérica de diarista via ILIKE."""
        from modules.operacional.diaristas.models.diarist import Diarist

        diarist = MagicMock(spec=Diarist)
        diarist.nome = "Maria Souza"
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [diarist]
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await connector.search_entity("diarista", "Maria")
        assert len(result) == 1
        assert result[0].nome == "Maria Souza"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_entity_not_mapped(self, connector):
        """Testa entidade não mapeada retorna lista vazia."""
        result = await connector.search_entity("xyz_invalido", "teste")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_empty_term(self, connector):
        """Testa termo vazio retorna lista vazia."""
        result = await connector.search_entity("funcionario", "")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_whitespace_term(self, connector):
        """Testa termo com espaços retorna lista vazia."""
        result = await connector.search_entity("funcionario", "   ")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_no_db(self):
        """Testa sem db_session retorna lista vazia."""
        from modules.ai.bartolo.services.data_connector import DataConnector

        dc = DataConnector(db_session=None)
        result = await dc.search_entity("funcionario", "Carlos")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_with_custom_limit(self, connector):
        """Testa limite customizado é passado para o repository."""
        emp = _make_employee()
        with patch("modules.ai.bartolo.services.data_connector.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(return_value=[emp])
            await connector.search_entity("funcionarios", "João", limit=10)
        mock_repo.return_value.search_by_name.assert_called_once_with("João", limit=10)

    @pytest.mark.asyncio
    async def test_search_repository_type_returns_empty(self, connector):
        """Testa que entidades tipo repository sem search_by_name retornam []."""
        result = await connector.search_entity("ocorrencia", "teste")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_entity_exception_handling(self, connector):
        """Testa que exceções são tratadas e retornam []."""
        with patch("modules.ai.bartolo.services.data_connector.EmployeeRepository") as mock_repo:
            mock_repo.return_value.search_by_name = AsyncMock(side_effect=Exception("DB error"))
            result = await connector.search_entity("funcionario", "Carlos")
        assert result == []
