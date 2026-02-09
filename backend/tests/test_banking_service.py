"""
Testes do BankingService.

Testa o servico unificado de operacoes bancarias
com multiplos adapters.
"""

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from modules.integrations.banking import (
    AccountBalance,
    BankCredentials,
    BankingAdapterError,
    PaymentResponse,
    PaymentStatus,
    PixKey,
)
from modules.integrations.banking.services import BankingService


class TestBankingServiceBasic:
    """Testes basicos do BankingService."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    @pytest.fixture
    def bb_credentials(self) -> BankCredentials:
        """Fixture de credenciais BB."""
        return BankCredentials(
            client_id="bb_test_id",
            client_secret="bb_test_secret",
            agency="1234",
            account="56789-0",
        )

    @pytest.fixture
    def itau_credentials(self) -> BankCredentials:
        """Fixture de credenciais Itau."""
        return BankCredentials(
            client_id="itau_test_id",
            client_secret="itau_test_secret",
            agency="0001",
            account="12345-6",
        )

    def test_service_creation(self, service: BankingService) -> None:
        """Testa criacao do servico."""
        assert service is not None
        assert isinstance(service._adapters, dict)  # pylint: disable=protected-access

    def test_register_bb_account(self, service: BankingService, bb_credentials: BankCredentials) -> None:
        """Testa registro de conta BB."""
        service.register_account("conta_bb", "001", bb_credentials)

        adapter = service.get_adapter("conta_bb")
        assert adapter.BANK_CODE == "001"

    def test_register_itau_account(self, service: BankingService, itau_credentials: BankCredentials) -> None:
        """Testa registro de conta Itau."""
        service.register_account("conta_itau", "341", itau_credentials)

        adapter = service.get_adapter("conta_itau")
        assert adapter.BANK_CODE == "341"

    def test_register_bradesco_account(self, service: BankingService, bb_credentials: BankCredentials) -> None:
        """Testa registro de conta Bradesco."""
        service.register_account("conta_bradesco", "237", bb_credentials)

        adapter = service.get_adapter("conta_bradesco")
        assert adapter.BANK_CODE == "237"

    def test_register_unsupported_bank(self, service: BankingService, bb_credentials: BankCredentials) -> None:
        """Testa registro de banco nao suportado."""
        with pytest.raises(BankingAdapterError, match="Banco nao suportado"):
            service.register_account("conta_xyz", "999", bb_credentials)

    def test_unregister_account(self, service: BankingService, bb_credentials: BankCredentials) -> None:
        """Testa remocao de conta."""
        service.register_account("conta_bb", "001", bb_credentials)
        service.unregister_account("conta_bb")

        with pytest.raises(BankingAdapterError, match="Conta nao registrada"):
            service.get_adapter("conta_bb")

    def test_get_adapter_not_found(self, service: BankingService) -> None:
        """Testa obter adapter de conta nao registrada."""
        with pytest.raises(BankingAdapterError, match="Conta nao registrada"):
            service.get_adapter("conta_inexistente")


class TestBankingServiceSupportedBanks:
    """Testes de bancos suportados."""

    def test_get_supported_banks(self) -> None:
        """Testa lista de bancos suportados."""
        banks = BankingService.get_supported_banks()

        assert len(banks) == 3
        codes = [b["code"] for b in banks]
        assert "001" in codes
        assert "341" in codes
        assert "237" in codes

    def test_supported_banks_have_names(self) -> None:
        """Testa que bancos tem nomes."""
        banks = BankingService.get_supported_banks()

        for bank in banks:
            assert "name" in bank
            assert len(bank["name"]) > 0


class TestBankingServiceBalance:
    """Testes de consulta de saldo."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    @pytest.fixture
    def mock_balance(self) -> AccountBalance:
        """Fixture de saldo mock."""
        return AccountBalance(
            available=Decimal("10000.00"),
            blocked=Decimal("500.00"),
            total=Decimal("10500.00"),
        )

    @pytest.mark.asyncio
    async def test_get_balance(self, service: BankingService, mock_balance: AccountBalance) -> None:
        """Testa consulta de saldo."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)

        with patch.object(service.get_adapter("conta_bb"), "get_balance", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = mock_balance

            balance = await service.get_balance("conta_bb")

            assert balance.available == Decimal("10000.00")
            mock_method.assert_called_once()


class TestBankingServiceTransfer:
    """Testes de transferencias."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    @pytest.fixture
    def mock_payment_response(self) -> PaymentResponse:
        """Fixture de resposta de pagamento."""
        return PaymentResponse(
            payment_id="PAY123456",
            status=PaymentStatus.PENDING,
            amount=Decimal("1000.00"),
        )

    @pytest.mark.asyncio
    async def test_transfer(self, service: BankingService, mock_payment_response: PaymentResponse) -> None:
        """Testa transferencia TED."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)

        with patch.object(service.get_adapter("conta_bb"), "initiate_payment", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = mock_payment_response

            response = await service.transfer(
                account_id="conta_bb",
                amount=Decimal("1000.00"),
                beneficiary_name="Fulano",
                beneficiary_document="12345678900",
                beneficiary_bank="341",
                beneficiary_agency="0001",
                beneficiary_account="12345-6",
            )

            assert response.payment_id == "PAY123456"
            assert response.status == PaymentStatus.PENDING


class TestBankingServicePix:
    """Testes de PIX."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    @pytest.fixture
    def mock_pix_key(self) -> PixKey:
        """Fixture de chave PIX."""
        return PixKey(
            key_type="CPF",
            key_value="12345678900",
            owner_name="Fulano de Tal",
        )

    @pytest.fixture
    def mock_pix_response(self) -> PaymentResponse:
        """Fixture de resposta PIX."""
        return PaymentResponse(
            payment_id="E123456789",
            status=PaymentStatus.COMPLETED,
            amount=Decimal("100.00"),
        )

    @pytest.mark.asyncio
    async def test_validate_pix_key(self, service: BankingService, mock_pix_key: PixKey) -> None:
        """Testa validacao de chave PIX."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)

        with patch.object(service.get_adapter("conta_bb"), "validate_pix_key", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = mock_pix_key

            result = await service.validate_pix_key("conta_bb", "12345678900")

            assert result.key_type == "CPF"
            assert result.owner_name == "Fulano de Tal"

    @pytest.mark.asyncio
    async def test_pix_transfer(self, service: BankingService, mock_pix_response: PaymentResponse) -> None:
        """Testa transferencia PIX."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)

        with patch.object(service.get_adapter("conta_bb"), "initiate_pix", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = mock_pix_response

            response = await service.pix_transfer(
                account_id="conta_bb",
                pix_key="12345678900",
                amount=Decimal("100.00"),
            )

            assert response.status == PaymentStatus.COMPLETED


class TestBankingServicePaymentStatus:
    """Testes de status de pagamento."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    @pytest.mark.asyncio
    async def test_get_payment_status(self, service: BankingService) -> None:
        """Testa consulta de status."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)

        mock_response = PaymentResponse(
            payment_id="PAY123",
            status=PaymentStatus.COMPLETED,
            amount=Decimal("500.00"),
        )

        with patch.object(
            service.get_adapter("conta_bb"),
            "get_payment_status",
            new_callable=AsyncMock,
        ) as mock_method:
            mock_method.return_value = mock_response

            response = await service.get_payment_status("conta_bb", "PAY123")

            assert response.status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_cancel_payment(self, service: BankingService) -> None:
        """Testa cancelamento de pagamento."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)

        with patch.object(service.get_adapter("conta_bb"), "cancel_payment", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = True

            result = await service.cancel_payment("conta_bb", "PAY123")

            assert result is True


class TestBankingServiceConsolidated:
    """Testes de operacoes consolidadas."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    def test_calculate_total_balance(self, service: BankingService) -> None:
        """Testa calculo de saldo total."""
        balances = {
            "conta_bb": AccountBalance(
                available=Decimal("1000.00"),
                blocked=Decimal("0.00"),
                total=Decimal("1000.00"),
            ),
            "conta_itau": AccountBalance(
                available=Decimal("2000.00"),
                blocked=Decimal("500.00"),
                total=Decimal("2500.00"),
            ),
        }

        total = service.calculate_total_balance(balances)

        assert total == Decimal("3000.00")

    def test_calculate_total_balance_empty(self, service: BankingService) -> None:
        """Testa calculo com lista vazia."""
        balances: dict[str, AccountBalance] = {}

        total = service.calculate_total_balance(balances)

        assert total == Decimal("0")


class TestBankingServiceCleanup:
    """Testes de limpeza de recursos."""

    @pytest.fixture
    def service(self) -> BankingService:
        """Fixture do servico."""
        return BankingService()

    @pytest.mark.asyncio
    async def test_close_all(self, service: BankingService) -> None:
        """Testa fechamento de todas as conexoes."""
        credentials = BankCredentials(client_id="test", client_secret="test", agency="1234", account="56789-0")
        service.register_account("conta_bb", "001", credentials)
        service.register_account("conta_itau", "341", credentials)

        await service.close_all()

        # Apos close, nao deve haver adapters
        assert len(service._adapters) == 0  # pylint: disable=protected-access
