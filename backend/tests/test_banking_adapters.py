"""
Testes dos Adapters de Integracao Bancaria.

Testa os adapters de bancos (BB, Itau, Bradesco)
para operacoes Open Banking.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from modules.integrations.banking.adapters import (
    AccountBalance,
    AccountType,
    AuthenticationError,
    BankCredentials,
    BankingAdapterError,
    BankStatement,
    BBAdapter,
    BradescoAdapter,
    ItauAdapter,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PixKey,
    RateLimitError,
    TransactionType,
)


class TestBankCredentials:
    """Testes de BankCredentials."""

    def test_create_minimal_credentials(self) -> None:
        """Testa criacao de credenciais minimas."""
        creds = BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
        )

        assert creds.client_id == "test_id"
        assert creds.client_secret == "test_secret"
        assert creds.environment == "sandbox"

    def test_create_full_credentials(self) -> None:
        """Testa criacao de credenciais completas."""
        creds = BankCredentials(
            client_id="test_id",
            client_secret="test_secret",
            certificate_path="/path/to/cert.pem",
            private_key_path="/path/to/key.pem",
            environment="production",
            agency="1234",
            account="56789-0",
        )

        assert creds.environment == "production"
        assert creds.agency == "1234"
        assert creds.account == "56789-0"


class TestAccountBalance:
    """Testes de AccountBalance."""

    def test_create_balance(self) -> None:
        """Testa criacao de saldo."""
        balance = AccountBalance(
            available=Decimal("1000.50"),
            blocked=Decimal("200.00"),
            total=Decimal("1200.50"),
        )

        assert balance.available == Decimal("1000.50")
        assert balance.blocked == Decimal("200.00")
        assert balance.total == Decimal("1200.50")
        assert balance.currency == "BRL"

    def test_balance_has_updated_at(self) -> None:
        """Testa que saldo tem data de atualizacao."""
        balance = AccountBalance(
            available=Decimal("100.00"),
            blocked=Decimal("0.00"),
            total=Decimal("100.00"),
        )

        assert balance.updated_at is not None


class TestTransactionType:
    """Testes de TransactionType."""

    def test_all_types_defined(self) -> None:
        """Testa que todos os tipos estao definidos."""
        expected_types = ["CREDIT", "DEBIT", "TED", "DOC", "PIX", "BOLETO", "TARIFA"]

        for tx_type in expected_types:
            assert hasattr(TransactionType, tx_type)

    def test_types_are_string_enum(self) -> None:
        """Testa que tipos sao string enum."""
        assert TransactionType.CREDIT.value == "CREDITO"
        assert TransactionType.PIX.value == "PIX"


class TestPaymentStatus:
    """Testes de PaymentStatus."""

    def test_all_statuses_defined(self) -> None:
        """Testa que todos os status estao definidos."""
        expected = ["PENDING", "PROCESSING", "COMPLETED", "FAILED", "CANCELLED", "SCHEDULED"]

        for status in expected:
            assert hasattr(PaymentStatus, status)

    def test_status_are_string_enum(self) -> None:
        """Testa que status sao string enum."""
        assert PaymentStatus.PENDING.value == "PENDENTE"
        assert PaymentStatus.COMPLETED.value == "CONCLUIDO"


class TestBBAdapter:
    """Testes do adapter Banco do Brasil."""

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture de credenciais."""
        return BankCredentials(
            client_id="bb_client_id",
            client_secret="bb_client_secret",
            agency="1234",
            account="56789-0",
        )

    @pytest.fixture
    def adapter(self, credentials: BankCredentials) -> BBAdapter:
        """Fixture do adapter."""
        return BBAdapter(credentials)

    def test_bank_code(self, adapter: BBAdapter) -> None:
        """Testa codigo do banco."""
        assert adapter.BANK_CODE == "001"

    def test_bank_name(self, adapter: BBAdapter) -> None:
        """Testa nome do banco."""
        assert adapter.BANK_NAME == "Banco do Brasil"

    def test_base_url_sandbox(self, adapter: BBAdapter) -> None:
        """Testa URL base sandbox."""
        assert adapter.base_url == "https://api.sandbox.bb.com.br"

    def test_base_url_production(self, credentials: BankCredentials) -> None:
        """Testa URL base producao."""
        credentials.environment = "production"
        adapter = BBAdapter(credentials)

        assert adapter.base_url == "https://api.bb.com.br"

    def test_is_authenticated_initially_false(self, adapter: BBAdapter) -> None:
        """Testa que nao esta autenticado inicialmente."""
        assert adapter.is_authenticated is False

    def test_generate_signature(self, adapter: BBAdapter) -> None:
        """Testa geracao de assinatura."""
        # pylint: disable=protected-access
        signature = adapter._generate_signature("2024-01-01T00:00:00")

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex

    def test_transaction_type_map(self, adapter: BBAdapter) -> None:
        """Testa mapeamento de tipos."""
        assert adapter.TRANSACTION_TYPE_MAP["CREDITO"] == TransactionType.CREDIT
        assert adapter.TRANSACTION_TYPE_MAP["PIX"] == TransactionType.PIX

    def test_parse_amount(self, adapter: BBAdapter) -> None:
        """Testa conversao de valor."""
        result = adapter._parse_amount("1234.56")  # pylint: disable=protected-access
        assert result == Decimal("1234.56")

    def test_format_document_cpf(self, adapter: BBAdapter) -> None:
        """Testa formatacao de CPF."""
        result = adapter._format_document("123.456.789-00")  # pylint: disable=protected-access
        assert result == "12345678900"

    def test_format_document_cnpj(self, adapter: BBAdapter) -> None:
        """Testa formatacao de CNPJ."""
        result = adapter._format_document("12.345.678/0001-90")  # pylint: disable=protected-access
        assert result == "12345678000190"


class TestItauAdapter:
    """Testes do adapter Itau."""

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture de credenciais."""
        return BankCredentials(
            client_id="itau_client_id",
            client_secret="itau_client_secret",
            agency="0001",
            account="12345-6",
        )

    @pytest.fixture
    def adapter(self, credentials: BankCredentials) -> ItauAdapter:
        """Fixture do adapter."""
        return ItauAdapter(credentials)

    def test_bank_code(self, adapter: ItauAdapter) -> None:
        """Testa codigo do banco."""
        assert adapter.BANK_CODE == "341"

    def test_bank_name(self, adapter: ItauAdapter) -> None:
        """Testa nome do banco."""
        assert adapter.BANK_NAME == "Itau Unibanco"

    def test_base_url_sandbox(self, adapter: ItauAdapter) -> None:
        """Testa URL base sandbox."""
        assert "sandbox" in adapter.base_url

    def test_generate_correlation_id(self, adapter: ItauAdapter) -> None:
        """Testa geracao de correlation ID."""
        corr_id = adapter._generate_correlation_id()  # pylint: disable=protected-access

        assert corr_id.startswith("erp-")
        assert len(corr_id) > 10

    def test_get_ispb(self, adapter: ItauAdapter) -> None:
        """Testa obtencao de ISPB."""
        ispb_itau = adapter._get_ispb("341")  # pylint: disable=protected-access
        ispb_bb = adapter._get_ispb("001")  # pylint: disable=protected-access

        assert ispb_itau == "60701190"
        assert ispb_bb == "00000000"

    def test_map_account_type(self, adapter: ItauAdapter) -> None:
        """Testa mapeamento de tipo de conta."""
        result = adapter._map_account_type(AccountType.CHECKING)  # pylint: disable=protected-access
        assert result == "CACC"

        result = adapter._map_account_type(AccountType.SAVINGS)  # pylint: disable=protected-access
        assert result == "SVGS"

    def test_get_person_type_cpf(self, adapter: ItauAdapter) -> None:
        """Testa identificacao de pessoa fisica."""
        result = adapter._get_person_type("12345678900")  # pylint: disable=protected-access
        assert result == "PESSOA_NATURAL"

    def test_get_person_type_cnpj(self, adapter: ItauAdapter) -> None:
        """Testa identificacao de pessoa juridica."""
        result = adapter._get_person_type("12345678000190")  # pylint: disable=protected-access
        assert result == "PESSOA_JURIDICA"

    def test_parse_payment_status(self, adapter: ItauAdapter) -> None:
        """Testa conversao de status."""
        # pylint: disable=protected-access
        assert adapter._parse_payment_status("ACCC") == PaymentStatus.COMPLETED
        assert adapter._parse_payment_status("PDNG") == PaymentStatus.PENDING
        assert adapter._parse_payment_status("RJCT") == PaymentStatus.FAILED


class TestBradescoAdapter:
    """Testes do adapter Bradesco."""

    @pytest.fixture
    def credentials(self) -> BankCredentials:
        """Fixture de credenciais."""
        return BankCredentials(
            client_id="bradesco_client_id",
            client_secret="bradesco_client_secret",
            agency="0001",
            account="12345-6",
        )

    @pytest.fixture
    def adapter(self, credentials: BankCredentials) -> BradescoAdapter:
        """Fixture do adapter."""
        return BradescoAdapter(credentials)

    def test_bank_code(self, adapter: BradescoAdapter) -> None:
        """Testa codigo do banco."""
        assert adapter.BANK_CODE == "237"

    def test_bank_name(self, adapter: BradescoAdapter) -> None:
        """Testa nome do banco."""
        assert adapter.BANK_NAME == "Bradesco"

    def test_base_url_sandbox(self, adapter: BradescoAdapter) -> None:
        """Testa URL base sandbox."""
        assert "sandbox" in adapter.base_url or "prebanco" in adapter.base_url

    def test_generate_basic_auth(self, adapter: BradescoAdapter) -> None:
        """Testa geracao de Basic Auth."""
        auth = adapter._generate_basic_auth()  # pylint: disable=protected-access

        assert auth.startswith("Basic ")
        assert len(auth) > 10

    def test_generate_signature(self, adapter: BradescoAdapter) -> None:
        """Testa geracao de assinatura."""
        signature = adapter._generate_signature()  # pylint: disable=protected-access

        assert isinstance(signature, str)
        assert len(signature) == 64

    def test_map_account_type(self, adapter: BradescoAdapter) -> None:
        """Testa mapeamento de tipo de conta."""
        result = adapter._map_account_type(AccountType.CHECKING)  # pylint: disable=protected-access
        assert result == "CC"

        result = adapter._map_account_type(AccountType.SAVINGS)  # pylint: disable=protected-access
        assert result == "PP"

    def test_parse_payment_status(self, adapter: BradescoAdapter) -> None:
        """Testa conversao de status."""
        # pylint: disable=protected-access
        assert adapter._parse_payment_status("EFETIVADO") == PaymentStatus.COMPLETED
        assert adapter._parse_payment_status("PENDENTE") == PaymentStatus.PENDING
        assert adapter._parse_payment_status("REJEITADO") == PaymentStatus.FAILED

    def test_transaction_type_map(self, adapter: BradescoAdapter) -> None:
        """Testa mapeamento de tipos."""
        assert adapter.TRANSACTION_TYPE_MAP["C"] == TransactionType.CREDIT
        assert adapter.TRANSACTION_TYPE_MAP["D"] == TransactionType.DEBIT
        assert adapter.TRANSACTION_TYPE_MAP["PIX"] == TransactionType.PIX


class TestPaymentRequest:
    """Testes de PaymentRequest."""

    def test_create_payment_request(self) -> None:
        """Testa criacao de requisicao de pagamento."""
        payment = PaymentRequest(
            amount=Decimal("1000.00"),
            beneficiary_name="Fulano de Tal",
            beneficiary_document="12345678900",
            beneficiary_bank="001",
            beneficiary_agency="1234",
            beneficiary_account="56789-0",
        )

        assert payment.amount == Decimal("1000.00")
        assert payment.beneficiary_name == "Fulano de Tal"
        assert payment.beneficiary_account_type == AccountType.CHECKING

    def test_create_scheduled_payment(self) -> None:
        """Testa criacao de pagamento agendado."""
        tomorrow = date.today() + timedelta(days=1)

        payment = PaymentRequest(
            amount=Decimal("500.00"),
            beneficiary_name="Empresa XYZ",
            beneficiary_document="12345678000190",
            beneficiary_bank="341",
            beneficiary_agency="0001",
            beneficiary_account="12345-6",
            scheduled_date=tomorrow,
        )

        assert payment.scheduled_date == tomorrow


class TestPaymentResponse:
    """Testes de PaymentResponse."""

    def test_create_payment_response(self) -> None:
        """Testa criacao de resposta de pagamento."""
        response = PaymentResponse(
            payment_id="PAY123456",
            status=PaymentStatus.PENDING,
            amount=Decimal("1000.00"),
        )

        assert response.payment_id == "PAY123456"
        assert response.status == PaymentStatus.PENDING

    def test_payment_response_with_error(self) -> None:
        """Testa resposta com erro."""
        response = PaymentResponse(
            payment_id="PAY123456",
            status=PaymentStatus.FAILED,
            amount=Decimal("1000.00"),
            error_message="Saldo insuficiente",
        )

        assert response.status == PaymentStatus.FAILED
        assert response.error_message == "Saldo insuficiente"


class TestPixKey:
    """Testes de PixKey."""

    def test_create_pix_key_cpf(self) -> None:
        """Testa criacao de chave PIX CPF."""
        pix_key = PixKey(
            key_type="CPF",
            key_value="12345678900",
            owner_name="Fulano de Tal",
        )

        assert pix_key.key_type == "CPF"
        assert pix_key.key_value == "12345678900"

    def test_create_pix_key_email(self) -> None:
        """Testa criacao de chave PIX email."""
        pix_key = PixKey(
            key_type="EMAIL",
            key_value="teste@email.com",
        )

        assert pix_key.key_type == "EMAIL"

    def test_create_pix_key_phone(self) -> None:
        """Testa criacao de chave PIX telefone."""
        pix_key = PixKey(
            key_type="PHONE",
            key_value="+5511999999999",
        )

        assert pix_key.key_type == "PHONE"

    def test_create_pix_key_evp(self) -> None:
        """Testa criacao de chave PIX aleatoria."""
        pix_key = PixKey(
            key_type="EVP",
            key_value="123e4567-e89b-12d3-a456-426614174000",
        )

        assert pix_key.key_type == "EVP"


class TestBankingErrors:
    """Testes de erros bancarios."""

    def test_banking_adapter_error(self) -> None:
        """Testa erro generico."""
        error = BankingAdapterError(
            "Erro de conexao",
            code="CONNECTION_ERROR",
            details={"host": "api.banco.com.br"},
        )

        assert str(error) == "Erro de conexao"
        assert error.code == "CONNECTION_ERROR"
        assert "host" in error.details

    def test_authentication_error(self) -> None:
        """Testa erro de autenticacao."""
        error = AuthenticationError("Credenciais invalidas")

        assert isinstance(error, BankingAdapterError)

    def test_rate_limit_error(self) -> None:
        """Testa erro de rate limit."""
        error = RateLimitError("Limite excedido")

        assert isinstance(error, BankingAdapterError)


class TestBankStatement:
    """Testes de BankStatement."""

    def test_create_statement(self) -> None:
        """Testa criacao de extrato."""
        statement = BankStatement(
            account_agency="1234",
            account_number="56789-0",
            account_type=AccountType.CHECKING,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            opening_balance=Decimal("1000.00"),
            closing_balance=Decimal("1500.00"),
            transactions=[],
            bank_code="001",
            bank_name="Banco do Brasil",
        )

        assert statement.account_agency == "1234"
        assert statement.opening_balance == Decimal("1000.00")
        assert len(statement.transactions) == 0

    def test_statement_period(self) -> None:
        """Testa periodo do extrato."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)

        statement = BankStatement(
            account_agency="1234",
            account_number="56789-0",
            account_type=AccountType.CHECKING,
            start_date=start,
            end_date=end,
            opening_balance=Decimal("0.00"),
            closing_balance=Decimal("0.00"),
            transactions=[],
            bank_code="001",
            bank_name="Banco do Brasil",
        )

        assert statement.start_date == start
        assert statement.end_date == end
