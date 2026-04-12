"""
BankingService - Servico unificado para operacoes bancarias.

Abstrai a complexidade dos diferentes adapters e fornece
uma interface unica para operacoes bancarias Open Banking.
"""

from datetime import date
from decimal import Decimal

from core.logging import logger

from ..adapters import (
    AccountBalance,
    AccountType,
    BankCode,
    BankCredentials,
    BankingAdapterError,
    BankStatement,
    BaseBankingAdapter,
    BBAdapter,
    BradescoAdapter,
    InterAdapter,
    ItauAdapter,
    PaymentRequest,
    PaymentResponse,
    PixKey,
)


class BankingService:
    """
    Servico unificado para operacoes bancarias.

    Gerencia multiplas contas e bancos, fornecendo interface
    consistente para todas as operacoes.
    """

    # Mapeamento de codigo de banco para adapter
    ADAPTER_MAP: dict[str, type[BaseBankingAdapter]] = {
        BankCode.BB: BBAdapter,
        BankCode.ITAU: ItauAdapter,
        BankCode.BRADESCO: BradescoAdapter,
        BankCode.INTER: InterAdapter,
    }

    def __init__(self) -> None:
        """Inicializa o servico."""
        self._adapters: dict[str, BaseBankingAdapter] = {}

    def register_account(
        self,
        account_id: str,
        bank_code: str,
        credentials: BankCredentials,
    ) -> None:
        """
        Registra uma conta bancaria para uso.

        Args:
            account_id: ID unico para identificar a conta
            bank_code: Codigo do banco (001, 341, 237, etc)
            credentials: Credenciais de acesso
        """
        adapter_class = self.ADAPTER_MAP.get(bank_code)

        if not adapter_class:
            raise BankingAdapterError(
                f"Banco nao suportado: {bank_code}",
                code="UNSUPPORTED_BANK",
            )

        adapter = adapter_class(credentials)
        self._adapters[account_id] = adapter

        logger.info(
            "Conta registrada",
            extra={
                "account_id": account_id,
                "bank_code": bank_code,
            },
        )

    def unregister_account(self, account_id: str) -> None:
        """
        Remove uma conta registrada.

        Args:
            account_id: ID da conta
        """
        if account_id in self._adapters:
            del self._adapters[account_id]
            logger.info("Conta removida", extra={"account_id": account_id})

    def get_adapter(self, account_id: str) -> BaseBankingAdapter:
        """
        Retorna adapter para a conta.

        Args:
            account_id: ID da conta

        Returns:
            Adapter configurado

        Raises:
            BankingAdapterError: Se conta nao registrada
        """
        adapter = self._adapters.get(account_id)

        if not adapter:
            raise BankingAdapterError(
                f"Conta nao registrada: {account_id}",
                code="ACCOUNT_NOT_FOUND",
            )

        return adapter

    async def get_balance(self, account_id: str) -> AccountBalance:
        """
        Consulta saldo de uma conta.

        Args:
            account_id: ID da conta registrada

        Returns:
            Saldo da conta
        """
        adapter = self.get_adapter(account_id)
        return await adapter.get_balance()

    async def get_statement(
        self,
        account_id: str,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """
        Consulta extrato de uma conta.

        Args:
            account_id: ID da conta
            start_date: Data inicial
            end_date: Data final

        Returns:
            Extrato com transacoes
        """
        adapter = self.get_adapter(account_id)
        return await adapter.get_statement(start_date, end_date)

    async def transfer(
        self,
        account_id: str,
        amount: Decimal,
        beneficiary_name: str,
        beneficiary_document: str,
        beneficiary_bank: str,
        beneficiary_agency: str,
        beneficiary_account: str,
        beneficiary_account_type: AccountType = AccountType.CHECKING,
        description: str | None = None,
        scheduled_date: date | None = None,
    ) -> PaymentResponse:
        """
        Realiza transferencia TED/DOC.

        Args:
            account_id: ID da conta origem
            amount: Valor da transferencia
            beneficiary_name: Nome do beneficiario
            beneficiary_document: CPF/CNPJ do beneficiario
            beneficiary_bank: Codigo do banco do beneficiario
            beneficiary_agency: Agencia do beneficiario
            beneficiary_account: Conta do beneficiario
            beneficiary_account_type: Tipo da conta
            description: Descricao da transferencia
            scheduled_date: Data para agendamento

        Returns:
            Resposta com status do pagamento
        """
        adapter = self.get_adapter(account_id)

        payment = PaymentRequest(
            amount=amount,
            beneficiary_name=beneficiary_name,
            beneficiary_document=beneficiary_document,
            beneficiary_bank=beneficiary_bank,
            beneficiary_agency=beneficiary_agency,
            beneficiary_account=beneficiary_account,
            beneficiary_account_type=beneficiary_account_type,
            description=description,
            scheduled_date=scheduled_date,
        )

        return await adapter.initiate_payment(payment)

    async def pix_transfer(
        self,
        account_id: str,
        pix_key: str,
        amount: Decimal,
        description: str | None = None,
    ) -> PaymentResponse:
        """
        Realiza transferencia PIX.

        Args:
            account_id: ID da conta origem
            pix_key: Chave PIX do destinatario
            amount: Valor da transferencia
            description: Descricao

        Returns:
            Resposta com status do pagamento
        """
        adapter = self.get_adapter(account_id)
        return await adapter.initiate_pix(pix_key, amount, description)

    async def validate_pix_key(
        self,
        account_id: str,
        key: str,
    ) -> PixKey | None:
        """
        Valida uma chave PIX.

        Args:
            account_id: ID da conta (para usar o adapter)
            key: Chave PIX a validar

        Returns:
            Dados da chave ou None se invalida
        """
        adapter = self.get_adapter(account_id)
        return await adapter.validate_pix_key(key)

    async def get_payment_status(
        self,
        account_id: str,
        payment_id: str,
    ) -> PaymentResponse:
        """
        Consulta status de um pagamento.

        Args:
            account_id: ID da conta
            payment_id: ID do pagamento

        Returns:
            Status atualizado
        """
        adapter = self.get_adapter(account_id)
        return await adapter.get_payment_status(payment_id)

    async def cancel_payment(
        self,
        account_id: str,
        payment_id: str,
    ) -> bool:
        """
        Cancela um pagamento agendado.

        Args:
            account_id: ID da conta
            payment_id: ID do pagamento

        Returns:
            True se cancelado
        """
        adapter = self.get_adapter(account_id)
        return await adapter.cancel_payment(payment_id)

    async def close_all(self) -> None:
        """Fecha todas as conexoes."""
        for adapter in self._adapters.values():
            await adapter.close()

        self._adapters.clear()
        logger.info("Todas as conexoes fechadas")

    @staticmethod
    def get_supported_banks() -> list[dict[str, str]]:
        """
        Retorna lista de bancos suportados.

        Returns:
            Lista com codigo e nome dos bancos
        """
        return [
            {"code": BankCode.BB, "name": "Banco do Brasil"},
            {"code": BankCode.ITAU, "name": "Itau Unibanco"},
            {"code": BankCode.BRADESCO, "name": "Bradesco"},
        ]

    async def get_consolidated_balance(
        self,
        account_ids: list[str],
    ) -> dict[str, AccountBalance]:
        """
        Consulta saldo de multiplas contas.

        Args:
            account_ids: Lista de IDs de contas

        Returns:
            Dicionario com saldos por conta
        """
        balances = {}

        for account_id in account_ids:
            try:
                balance = await self.get_balance(account_id)
                balances[account_id] = balance
            except BankingAdapterError as exc:
                logger.warning(
                    "Erro ao consultar saldo",
                    extra={
                        "account_id": account_id,
                        "error": str(exc),
                    },
                )

        return balances

    def calculate_total_balance(
        self,
        balances: dict[str, AccountBalance],
    ) -> Decimal:
        """
        Calcula saldo total consolidado.

        Args:
            balances: Dicionario com saldos

        Returns:
            Soma dos saldos disponiveis
        """
        return sum(
            (b.available for b in balances.values()),
            Decimal("0"),
        )
