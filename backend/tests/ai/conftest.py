"""
Fixtures de teste para o módulo AI Bartolo.

Mocks de banco de dados, repositórios e dependências
para testar os componentes do Bartolo isoladamente.
"""

from dataclasses import dataclass
from datetime import date, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

# ========================================================================
# Mock Models
# ========================================================================


@dataclass
class MockUser:
    """Mock do modelo User."""

    id: UUID
    name: str
    email: str
    role: str
    is_active: bool = True
    permissions: list = None
    created_at: datetime = None

    def __post_init__(self):
        self.permissions = self.permissions or []
        self.created_at = self.created_at or datetime(2024, 1, 1)


@dataclass
class MockEmployee:
    """Mock do modelo Employee."""

    id: UUID
    nome: str
    is_active: bool = True
    created_at: datetime = None


@dataclass
class MockShift:
    """Mock do modelo Shift."""

    id: UUID
    employee_id: UUID
    shift_date: date
    is_night_shift: bool = False
    planned_start_time: str | None = None
    planned_end_time: str | None = None
    employee: MockEmployee | None = None


# ========================================================================
# Fixtures
# ========================================================================


@pytest.fixture
def mock_users():
    """Lista de usuários mock para testes."""
    return [
        MockUser(
            id=UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890"),
            name="Jordan Admin",
            email="admin@conectapro.com.br",
            role="super_admin",
            created_at=datetime(2024, 1, 1),
        ),
        MockUser(
            id=UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901"),
            name="Maria Supervisora",
            email="maria@conectapro.com.br",
            role="supervisor",
            created_at=datetime(2024, 2, 1),
        ),
        MockUser(
            id=UUID("c3d4e5f6-a7b8-9012-cdef-012345678902"),
            name="João Operador",
            email="joao@conectapro.com.br",
            role="operator",
            created_at=datetime(2024, 3, 1),
        ),
    ]


@pytest.fixture
def mock_employees():
    """Lista de funcionários mock."""
    names = [
        "KALEL SILVA DE JESUS",
        "ROBERTO PEREIRA MENEZES",
        "ANDREW COSTA VASCONCELOS",
        "ORLAILSON PAIVA PEREIRA",
        "MAURICIO ALVES CHAGAS",
        "ANTONIO DINIZ ASSIS DOS SANTOS",
        "ERIKA CRISTINA MAQUINE PEREIRA",
        "TELMA MARIA LAGES MEIRA",
        "ANTONIO CARLOS VIEIRA",
    ]
    return [MockEmployee(id=uuid4(), nome=name, is_active=True) for name in names]


@pytest.fixture
def mock_db_session():
    """Mock da sessão async do banco de dados."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session
