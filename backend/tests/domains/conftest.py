"""
tests/domains/conftest.py - DOMAIN TESTS FIXTURES
=================================================
Enterprise pytest fixtures for domain testing
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest

# =============================================================================
# Common Fixtures
# =============================================================================


@pytest.fixture
def tenant_id() -> UUID:
    """Fixture para tenant ID."""
    return uuid4()


@pytest.fixture
def user_id() -> str:
    """Fixture para user ID."""
    return "test-user-001"


@pytest.fixture
def current_date() -> date:
    """Fixture para data atual."""
    return date.today()


# =============================================================================
# Financial Fixtures
# =============================================================================


@pytest.fixture
def sample_account_data(tenant_id: UUID, user_id: str) -> dict[str, Any]:
    """Fixture para dados de conta contabil."""
    return {
        "account_code": "1.1.1.01",
        "account_name": "Caixa",
        "account_type": "asset_current",
        "level": 4,
        "is_analytical": True,
        "currency": "BRL",
        "tenant_id": tenant_id,
        "created_by": user_id,
    }


@pytest.fixture
def sample_journal_lines() -> list:
    """Fixture para linhas de lancamento."""
    from domains.financial import JournalLine

    return [
        JournalLine(
            account_id=uuid4(),
            account_code="1.1.1.01",
            account_name="Caixa",
            debit_amount=Decimal("1000.00"),
            credit_amount=Decimal("0"),
            description="Recebimento de venda",
        ),
        JournalLine(
            account_id=uuid4(),
            account_code="3.1.1.01",
            account_name="Receita de Vendas",
            debit_amount=Decimal("0"),
            credit_amount=Decimal("1000.00"),
            description="Venda de mercadorias",
        ),
    ]


# =============================================================================
# HR Fixtures
# =============================================================================


@pytest.fixture
def sample_address() -> dict[str, Any]:
    """Fixture para endereco."""
    return {
        "street": "Rua das Flores",
        "number": "123",
        "complement": "Apto 101",
        "neighborhood": "Centro",
        "city": "Sao Paulo",
        "state": "SP",
        "postal_code": "01234-567",
        "country": "BR",
    }


@pytest.fixture
def sample_bank_account() -> dict[str, Any]:
    """Fixture para conta bancaria."""
    return {
        "bank_code": "001",
        "bank_name": "Banco do Brasil",
        "agency": "1234-5",
        "account_number": "12345-6",
        "account_type": "corrente",
    }


@pytest.fixture
def sample_employee_data(
    tenant_id: UUID, user_id: str, sample_address: dict[str, Any], sample_bank_account: dict[str, Any]
) -> dict[str, Any]:
    """Fixture para dados de colaborador."""
    return {
        "employee_code": "EMP-000001",
        "full_name": "Joao da Silva",
        "cpf": "123.456.789-00",
        "birth_date": date(1990, 5, 15),
        "gender": "M",
        "marital_status": "married",
        "email": "joao.silva@empresa.com",
        "phone": "(11) 99999-8888",
        "address": sample_address,
        "employment_type": "clt",
        "hire_date": date(2023, 1, 15),
        "department_id": uuid4(),
        "department_name": "Tecnologia",
        "position_id": uuid4(),
        "position_name": "Desenvolvedor Senior",
        "work_schedule": "full_time",
        "base_salary": Decimal("8500.00"),
        "bank_account": sample_bank_account,
        "tenant_id": tenant_id,
        "created_by": user_id,
    }


# =============================================================================
# Inventory Fixtures
# =============================================================================


@pytest.fixture
def sample_pricing() -> dict[str, Any]:
    """Fixture para precificacao."""
    return {
        "cost_price": Decimal("50.00"),
        "average_cost": Decimal("50.00"),
        "last_purchase_price": Decimal("48.00"),
        "sale_price": Decimal("89.90"),
        "minimum_price": Decimal("70.00"),
        "currency": "BRL",
    }


@pytest.fixture
def sample_stock_level() -> dict[str, Any]:
    """Fixture para niveis de estoque."""
    return {
        "minimum_stock": Decimal("10"),
        "maximum_stock": Decimal("1000"),
        "reorder_point": Decimal("50"),
        "reorder_quantity": Decimal("100"),
        "safety_stock": Decimal("20"),
        "lead_time_days": 7,
    }


@pytest.fixture
def sample_product_data(
    tenant_id: UUID, user_id: str, sample_pricing: dict[str, Any], sample_stock_level: dict[str, Any]
) -> dict[str, Any]:
    """Fixture para dados de produto."""
    return {
        "sku": "PROD-000001",
        "barcode": "7891234567890",
        "name": "Produto Teste",
        "description": "Descricao do produto teste",
        "product_type": "finished_goods",
        "category_id": uuid4(),
        "category_name": "Categoria Teste",
        "unit_of_measure": "UN",
        "pricing": sample_pricing,
        "stock_level": sample_stock_level,
        "tax_classification": {
            "ncm": "12345678",
            "cfop_sale": "5102",
            "cfop_purchase": "1102",
            "origin": "0",
            "icms_cst": "00",
            "pis_cst": "01",
            "cofins_cst": "01",
        },
        "tenant_id": tenant_id,
        "created_by": user_id,
    }


# =============================================================================
# Procurement Fixtures
# =============================================================================


@pytest.fixture
def sample_budget_allocation(tenant_id: UUID) -> dict[str, Any]:
    """Fixture para alocacao orcamentaria."""
    from domains.procurement import Money

    return {
        "budget_id": uuid4(),
        "account_code": "3.3.90.039",
        "allocated_amount": Money(Decimal("500000.00")),
        "available_amount": Money(Decimal("350000.00")),
        "fiscal_year": 2024,
        "cost_center": "TI-001",
    }


@pytest.fixture
def sample_contract_terms() -> dict[str, Any]:
    """Fixture para termos contratuais."""
    return {
        "payment_terms": "net_30",
        "payment_description": "Pagamento em 30 dias apos entrega",
        "delivery_deadline_days": 60,
        "warranty_months": 12,
        "penalty_rate_percent": Decimal("0.5"),
        "contract_type": "fixed_price",
        "acceptance_criteria": "Conforme especificacoes tecnicas do edital",
        "sla_requirements": {"uptime": "99.9%"},
        "quality_standards": ["ISO 9001", "ISO 27001"],
    }
