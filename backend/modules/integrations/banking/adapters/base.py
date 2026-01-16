"""
Base Adapter para integracoes bancarias Open Banking.

Define a interface padrao para todos os adapters de bancos,
seguindo os padroes Open Banking Brasil.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class BankCode(str, Enum):
    """Codigos dos bancos suportados."""

    BB = "001"  # Banco do Brasil
    ITAU = "341"  # Itau Unibanco
    BRADESCO = "237"  # Bradesco
    SANTANDER = "033"  # Santander
    CAIXA = "104"  # Caixa Economica
    SICOOB = "756"  # Sicoob
    SICREDI = "748"  # Sicredi
    INTER = "077"  # Banco Inter
    CORA = "403"  # Cora SCD


class AccountType(str, Enum):
    """Tipos de conta bancaria."""

    CHECKING = "CONTA_CORRENTE"
    SAVINGS = "POUPANCA"
    SALARY = "CONTA_SALARIO"
    PAYMENT = "CONTA_PAGAMENTO"


class TransactionType(str, Enum):
    """Tipos de transacao."""

    CREDIT = "CREDITO"
    DEBIT = "DEBITO"
    TED = "TED"
    DOC = "DOC"
    PIX = "PIX"
    BOLETO = "BOLETO"
    TARIFA = "TARIFA"
    IOF = "IOF"


class PaymentStatus(str, Enum):
    """Status de pagamento."""

    PENDING = "PENDENTE"
    PROCESSING = "PROCESSANDO"
    COMPLETED = "CONCLUIDO"
    FAILED = "FALHOU"
    CANCELLED = "CANCELADO"
    SCHEDULED = "AGENDADO"


@dataclass
class BankCredentials:
    """Credenciais de acesso ao banco."""

    client_id: str
    client_secret: str
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    environment: str = "sandbox"  # sandbox ou production
    agency: Optional[str] = None
    account: Optional[str] = None


@dataclass
class AccountBalance:
    """Saldo da conta bancaria."""

    available: Decimal
    blocked: Decimal
    total: Decimal
    currency: str = "BRL"
    updated_at: datetime = None

    def __post_init__(self) -> None:
        """Inicializa data se nao informada."""
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class BankTransaction:
    """Transacao bancaria."""

    transaction_id: str
    date: datetime
    amount: Decimal
    transaction_type: TransactionType
    description: str
    balance_after: Optional[Decimal] = None
    counterpart_name: Optional[str] = None
    counterpart_document: Optional[str] = None
    counterpart_bank: Optional[str] = None
    counterpart_agency: Optional[str] = None
    counterpart_account: Optional[str] = None
    category: Optional[str] = None
    reference: Optional[str] = None


@dataclass
class BankStatement:
    """Extrato bancario."""

    account_agency: str
    account_number: str
    account_type: AccountType
    start_date: date
    end_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    transactions: list[BankTransaction]
    bank_code: str
    bank_name: str


@dataclass
class PaymentRequest:
    """Solicitacao de pagamento."""

    amount: Decimal
    beneficiary_name: str
    beneficiary_document: str
    beneficiary_bank: str
    beneficiary_agency: str
    beneficiary_account: str
    beneficiary_account_type: AccountType = AccountType.CHECKING
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    pix_key: Optional[str] = None
    barcode: Optional[str] = None


@dataclass
class PaymentResponse:
    """Resposta de pagamento."""

    payment_id: str
    status: PaymentStatus
    amount: Decimal
    scheduled_date: Optional[date] = None
    processed_at: Optional[datetime] = None
    receipt_url: Optional[str] = None
    authentication_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PixKey:
    """Chave PIX."""

    key_type: str  # CPF, CNPJ, EMAIL, PHONE, EVP
    key_value: str
    owner_name: Optional[str] = None
    owner_document: Optional[str] = None
    bank_code: Optional[str] = None
    bank_name: Optional[str] = None
    agency: Optional[str] = None
    account: Optional[str] = None
    account_type: Optional[AccountType] = None


class BankingAdapterError(Exception):
    """Erro generico de adapter bancario."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Inicializa erro."""
        super().__init__(message)
        self.code = code
        self.details = details or {}


class AuthenticationError(BankingAdapterError):
    """Erro de autenticacao."""


class RateLimitError(BankingAdapterError):
    """Erro de limite de requisicoes."""


class InsufficientFundsError(BankingAdapterError):
    """Erro de saldo insuficiente."""


class InvalidAccountError(BankingAdapterError):
    """Erro de conta invalida."""


class BaseBankingAdapter(ABC):
    """
    Adapter base para integracoes bancarias.

    Define a interface padrao que todos os adapters
    de bancos devem implementar.
    """

    # Configuracoes do banco
    BANK_CODE: str = ""
    BANK_NAME: str = ""
    API_BASE_URL_SANDBOX: str = ""
    API_BASE_URL_PRODUCTION: str = ""

    def __init__(self, credentials: BankCredentials) -> None:
        """
        Inicializa o adapter.

        Args:
            credentials: Credenciais de acesso ao banco
        """
        self.credentials = credentials
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    @property
    def base_url(self) -> str:
        """Retorna URL base conforme ambiente."""
        if self.credentials.environment == "production":
            return self.API_BASE_URL_PRODUCTION
        return self.API_BASE_URL_SANDBOX

    @property
    def is_authenticated(self) -> bool:
        """Verifica se esta autenticado e token valido."""
        if not self._access_token:
            return False
        if self._token_expires_at and datetime.now() >= self._token_expires_at:
            return False
        return True

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Autentica no banco e obtem token de acesso.

        Returns:
            True se autenticado com sucesso
        """

    @abstractmethod
    async def get_balance(self) -> AccountBalance:
        """
        Consulta saldo da conta.

        Returns:
            Saldo da conta
        """

    @abstractmethod
    async def get_statement(
        self,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """
        Consulta extrato da conta.

        Args:
            start_date: Data inicial
            end_date: Data final

        Returns:
            Extrato com transacoes
        """

    @abstractmethod
    async def initiate_payment(
        self,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """
        Inicia um pagamento.

        Args:
            payment: Dados do pagamento

        Returns:
            Resposta com status do pagamento
        """

    @abstractmethod
    async def get_payment_status(
        self,
        payment_id: str,
    ) -> PaymentResponse:
        """
        Consulta status de um pagamento.

        Args:
            payment_id: ID do pagamento

        Returns:
            Status atualizado do pagamento
        """

    @abstractmethod
    async def cancel_payment(
        self,
        payment_id: str,
    ) -> bool:
        """
        Cancela um pagamento agendado.

        Args:
            payment_id: ID do pagamento

        Returns:
            True se cancelado com sucesso
        """

    @abstractmethod
    async def validate_pix_key(
        self,
        key: str,
    ) -> Optional[PixKey]:
        """
        Valida e consulta dados de uma chave PIX.

        Args:
            key: Chave PIX

        Returns:
            Dados da chave ou None se invalida
        """

    @abstractmethod
    async def initiate_pix(
        self,
        pix_key: str,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> PaymentResponse:
        """
        Inicia transferencia PIX.

        Args:
            pix_key: Chave PIX do destinatario
            amount: Valor
            description: Descricao

        Returns:
            Resposta do pagamento
        """

    async def ensure_authenticated(self) -> None:
        """Garante que esta autenticado."""
        if not self.is_authenticated:
            await self.authenticate()

    def _parse_amount(self, value: str | int | float | Decimal) -> Decimal:
        """Converte valor para Decimal."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value)).quantize(Decimal("0.01"))

    def _format_document(self, document: str) -> str:
        """Remove formatacao de documento (CPF/CNPJ)."""
        return "".join(filter(str.isdigit, document))

    def _format_phone(self, phone: str) -> str:
        """Formata telefone para padrao E.164."""
        digits = "".join(filter(str.isdigit, phone))
        if not digits.startswith("55"):
            digits = "55" + digits
        return "+" + digits
