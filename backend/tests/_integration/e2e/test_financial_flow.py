"""
Testes E2E - Fluxo Financeiro.

Testa os módulos financeiros: Contas a Pagar/Receber, Bancos, Contabilidade.
Rotas usam padrão: /api/v1/financial/{module}/{module}/
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestFinancialAccounting:
    """Testes de Contabilidade."""

    async def test_accounting_accounts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de contas contábeis existe."""
        response = await client.get("/api/v1/financial/accounting/accounting/accounts")
        assert response.status_code in [200, 401, 403, 422]

    async def test_accounting_charts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de planos de contas existe."""
        response = await client.get("/api/v1/financial/accounting/accounting/charts")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestFinancialPayables:
    """Testes de Contas a Pagar."""

    async def test_payables_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de contas a pagar existe."""
        response = await client.get("/api/v1/financial/payables/payables/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_suppliers_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de fornecedores existe."""
        response = await client.get("/api/v1/financial/suppliers/suppliers/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestFinancialReceivables:
    """Testes de Contas a Receber."""

    async def test_receivables_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de contas a receber existe."""
        response = await client.get("/api/v1/financial/receivables/receivables/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_customers_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de clientes existe."""
        response = await client.get("/api/v1/financial/customers/customers/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestFinancialBanking:
    """Testes de Bancos."""

    async def test_bank_accounts_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de contas bancárias existe."""
        response = await client.get("/api/v1/financial/bank-accounts/bank-accounts/")
        assert response.status_code in [200, 401, 403, 422]

    async def test_bank_transactions_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de transações bancárias existe."""
        response = await client.get("/api/v1/financial/bank-transactions/bank-transactions/")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestFinancialCashflow:
    """Testes de Fluxo de Caixa."""

    async def test_cashflow_entries_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de fluxo de caixa existe."""
        response = await client.get("/api/v1/financial/cashflow/cashflow/entries")
        assert response.status_code in [200, 401, 403, 422]


@pytest.mark.asyncio
class TestFinancialPurchases:
    """Testes de Compras."""

    async def test_purchases_products_endpoint_exists(self, client: AsyncClient):
        """Verifica que o endpoint de produtos existe."""
        response = await client.get("/api/v1/financial/purchases/purchases/products")
        assert response.status_code in [200, 401, 403, 422]
