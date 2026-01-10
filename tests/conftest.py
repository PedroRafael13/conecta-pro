"""
Pytest Configuration and Fixtures for FASE 3 Tests.

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import asyncio
import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest

# Add fase3 to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# ASYNC FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def async_mock():
    """Create async mock helper."""
    return AsyncMock


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.query = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_async_session():
    """Mock async database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    return session


# =============================================================================
# SECURITY LGPD FIXTURES
# =============================================================================

@pytest.fixture
def sample_encryption_key():
    """Sample encryption key for tests."""
    return os.urandom(32)


@pytest.fixture
def sample_sensitive_data():
    """Sample sensitive data for encryption tests."""
    return {
        "cpf": "12345678901",
        "email": "test@example.com",
        "phone": "11999998888",
        "name": "Joao da Silva",
        "address": "Rua Teste, 123",
        "credit_card": "4111111111111111"
    }


@pytest.fixture
def sample_consent_data():
    """Sample consent data."""
    return {
        "titular_id": str(uuid.uuid4()),
        "titular_cpf": "12345678901",
        "titular_nome": "Maria Santos",
        "titular_email": "maria@example.com",
        "purposes": ["marketing", "analytics"],
        "legal_basis": "consent"
    }


# =============================================================================
# HEALTH OCCUPATIONAL FIXTURES
# =============================================================================

@pytest.fixture
def sample_employee():
    """Sample employee data."""
    return {
        "id": str(uuid.uuid4()),
        "cpf": "12345678901",
        "nome": "Carlos Oliveira",
        "data_nascimento": date(1985, 5, 15),
        "data_admissao": date(2020, 3, 1),
        "cargo": "Operador de Maquinas",
        "setor": "Producao",
        "empresa_id": str(uuid.uuid4())
    }


@pytest.fixture
def sample_risk_data():
    """Sample occupational risk data."""
    return {
        "tipo": "fisico",
        "agente": "Ruido",
        "fonte": "Maquinas industriais",
        "nivel_exposicao": 85,  # dB
        "tempo_exposicao": 8,  # horas
        "medidas_controle": ["Protetor auricular", "Enclausuramento"]
    }


@pytest.fixture
def sample_epi_data():
    """Sample EPI data."""
    return {
        "descricao": "Protetor Auricular Tipo Concha",
        "ca_numero": "12345",
        "ca_validade": date(2027, 12, 31),
        "fabricante": "3M do Brasil",
        "quantidade": 100,
        "preco_unitario": Decimal("45.90")
    }


# =============================================================================
# GOVERNMENT INTEGRATIONS FIXTURES
# =============================================================================

@pytest.fixture
def sample_company():
    """Sample company data."""
    return {
        "id": str(uuid.uuid4()),
        "cnpj": "12345678000199",
        "razao_social": "Empresa Teste Ltda",
        "nome_fantasia": "Teste Corp",
        "inscricao_estadual": "123456789",
        "endereco": {
            "logradouro": "Av. Brasil",
            "numero": "1000",
            "bairro": "Centro",
            "cidade": "Sao Paulo",
            "uf": "SP",
            "cep": "01310100"
        }
    }


@pytest.fixture
def sample_worker():
    """Sample worker data for FGTS/INSS."""
    return {
        "id": str(uuid.uuid4()),
        "cpf": "12345678901",
        "pis_pasep": "12345678901",
        "nome": "Jose Ferreira",
        "data_admissao": date(2020, 1, 15),
        "data_nascimento": date(1990, 6, 20),
        "cargo": "Analista",
        "salario": Decimal("5500.00")
    }


@pytest.fixture
def sample_remuneracao():
    """Sample remuneration data."""
    return {
        "salario_base": Decimal("5500.00"),
        "horas_extras": Decimal("550.00"),
        "adicional_noturno": Decimal("0"),
        "comissoes": Decimal("0"),
        "dsr": Decimal("183.33"),
        "competencia": date(2026, 1, 1)
    }


@pytest.fixture
def sample_nfe_data():
    """Sample NFe data."""
    return {
        "destinatario": {
            "cnpj": "98765432000188",
            "razao_social": "Cliente Teste SA",
            "endereco": {
                "logradouro": "Rua Cliente",
                "numero": "500",
                "bairro": "Industrial",
                "cidade": "Campinas",
                "uf": "SP",
                "cep": "13000000"
            }
        },
        "produtos": [
            {
                "codigo": "PROD001",
                "descricao": "Produto Teste 1",
                "ncm": "84713012",
                "cfop": "5102",
                "unidade": "UN",
                "quantidade": Decimal("10"),
                "valor_unitario": Decimal("150.00"),
                "valor_total": Decimal("1500.00")
            }
        ],
        "pagamento": {
            "forma": "01",  # Dinheiro
            "valor": Decimal("1500.00")
        }
    }


# =============================================================================
# VALIDATION FIXTURES
# =============================================================================

@pytest.fixture
def valid_cpfs():
    """List of valid CPF numbers for testing."""
    return [
        "52998224725",  # Valid CPF
        "11144477735",  # Valid CPF
        "98765432100",  # Valid CPF (generated)
    ]


@pytest.fixture
def invalid_cpfs():
    """List of invalid CPF numbers for testing."""
    return [
        "00000000000",  # All zeros
        "11111111111",  # All same digit
        "12345678901",  # Invalid checksum
        "123",          # Too short
        "123456789012", # Too long
        "abcdefghijk",  # Non-numeric
    ]


@pytest.fixture
def valid_cnpjs():
    """List of valid CNPJ numbers for testing."""
    return [
        "11222333000181",  # Valid CNPJ
        "11444777000161",  # Valid CNPJ
    ]


@pytest.fixture
def invalid_cnpjs():
    """List of invalid CNPJ numbers for testing."""
    return [
        "00000000000000",  # All zeros
        "11111111111111",  # All same digit
        "12345678000199",  # Invalid checksum
        "123",             # Too short
    ]


@pytest.fixture
def valid_pis():
    """List of valid PIS/PASEP numbers."""
    return [
        "12345678901",  # Example (would need real valid ones)
    ]


# =============================================================================
# DATE FIXTURES
# =============================================================================

@pytest.fixture
def current_competencia():
    """Current competency month."""
    today = date.today()
    return today.replace(day=1)


@pytest.fixture
def previous_competencia():
    """Previous competency month."""
    today = date.today()
    first_of_month = today.replace(day=1)
    return (first_of_month - timedelta(days=1)).replace(day=1)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_valid_cpf() -> str:
    """Generate a valid CPF for testing."""
    def calc_digit(cpf_partial: list, weights: list) -> int:
        total = sum(d * w for d, w in zip(cpf_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    base = [5, 2, 9, 9, 8, 2, 2, 4, 7]
    d1 = calc_digit(base, [10, 9, 8, 7, 6, 5, 4, 3, 2])
    base.append(d1)
    d2 = calc_digit(base, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2])
    base.append(d2)
    return ''.join(map(str, base))


def generate_valid_cnpj() -> str:
    """Generate a valid CNPJ for testing."""
    def calc_digit(cnpj_partial: list, weights: list) -> int:
        total = sum(d * w for d, w in zip(cnpj_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    base = [1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0, 1]
    d1 = calc_digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    base.append(d1)
    d2 = calc_digit(base, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    base.append(d2)
    return ''.join(map(str, base))


@pytest.fixture
def generated_cpf():
    """Generate valid CPF."""
    return generate_valid_cpf()


@pytest.fixture
def generated_cnpj():
    """Generate valid CNPJ."""
    return generate_valid_cnpj()
