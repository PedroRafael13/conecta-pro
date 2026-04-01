"""
Adapter para integracao com Itau Unibanco.

Implementa a API Open Banking do Itau para consultas
e operacoes bancarias.
"""

import hashlib
import hmac
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx

from core.logging import logger

from .base import (
    AccountBalance,
    AccountType,
    AuthenticationError,
    BankCredentials,
    BankingAdapterError,
    BankStatement,
    BankTransaction,
    BaseBankingAdapter,
    InsufficientFundsError,
    InvalidAccountError,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PixKey,
    RateLimitError,
    TransactionType,
)


class ItauAdapter(BaseBankingAdapter):
    """
    Adapter para Itau Unibanco.

    Implementa integracao com APIs Open Banking do Itau:
    - Consulta de saldo
    - Consulta de extrato
    - Iniciacao de pagamentos (TED, PIX, Boleto)
    - Consulta de status de pagamentos
    """

    BANK_CODE = "341"
    BANK_NAME = "Itau Unibanco"
    API_BASE_URL_SANDBOX = "https://sandbox.devportal.itau.com.br"
    API_BASE_URL_PRODUCTION = "https://api.itau.com.br"

    # Endpoints Itau
    OAUTH_ENDPOINT = "/api/oauth/token"
    BALANCE_ENDPOINT = "/open-banking/accounts/v1/accounts/{account_id}/balances"
    STATEMENT_ENDPOINT = "/open-banking/accounts/v1/accounts/{account_id}/transactions"
    PAYMENT_ENDPOINT = "/open-banking/payments/v1/pix/payments"
    PIX_ENDPOINT = "/open-banking/payments/v1/pix"

    # Mapeamento de tipos de transacao do Itau
    TRANSACTION_TYPE_MAP = {
        "CREDIT": TransactionType.CREDIT,
        "DEBIT": TransactionType.DEBIT,
        "TED_CREDIT": TransactionType.TED,
        "TED_DEBIT": TransactionType.TED,
        "DOC_CREDIT": TransactionType.DOC,
        "DOC_DEBIT": TransactionType.DOC,
        "PIX_CREDIT": TransactionType.PIX,
        "PIX_DEBIT": TransactionType.PIX,
        "BOLETO": TransactionType.BOLETO,
        "FEE": TransactionType.TARIFA,
    }

    def __init__(self, credentials: BankCredentials) -> None:
        """Inicializa adapter Itau."""
        super().__init__(credentials)
        self._client: httpx.AsyncClient | None = None
        self._account_id: str | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP configurado."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def authenticate(self) -> bool:
        """
        Autentica no Itau usando OAuth2 Client Credentials.

        Returns:
            True se autenticado com sucesso
        """
        try:
            client = await self._get_client()

            # Itau usa certificado mTLS em producao
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scope": "accounts payments pix-dict",
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "x-itau-correlationID": self._generate_correlation_id(),
            }

            response = await client.post(
                self.OAUTH_ENDPOINT,
                data=auth_data,
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                # Itau retorna account_id no token
                self._account_id = data.get("account_id")

                logger.info(
                    "Itau: Autenticacao realizada",
                    extra={"expires_in": expires_in},
                )
                return True

            if response.status_code == 401:
                raise AuthenticationError(
                    "Credenciais invalidas",
                    code="AUTH_FAILED",
                    details={"response": response.text},
                )

            if response.status_code == 429:
                raise RateLimitError(
                    "Limite de requisicoes excedido",
                    code="RATE_LIMIT",
                )

            raise BankingAdapterError(
                f"Erro na autenticacao: {response.status_code}",
                code="AUTH_ERROR",
                details={"response": response.text},
            )

        except httpx.RequestError as exc:
            logger.error("Itau: Erro de conexao", extra={"error": str(exc)})
            raise BankingAdapterError(
                "Erro de conexao com Itau",
                code="CONNECTION_ERROR",
                details={"error": str(exc)},
            ) from exc

    def _generate_correlation_id(self) -> str:
        """Gera ID de correlacao para rastreamento."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"erp-{timestamp}"

    def _generate_signature(self, payload: str) -> str:
        """Gera assinatura HMAC para requisicao."""
        message = f"{self.credentials.client_id}{payload}"
        signature = hmac.new(
            self.credentials.client_secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return signature

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict[str, Any]:
        """Faz requisicao autenticada."""
        await self.ensure_authenticated()

        client = await self._get_client()

        # Substitui placeholders no endpoint
        if self._account_id:
            endpoint = endpoint.replace("{account_id}", self._account_id)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "x-itau-correlationID": self._generate_correlation_id(),
        }

        try:
            if method.upper() == "GET":
                response = await client.get(
                    endpoint,
                    headers=headers,
                    params=params,
                )
            elif method.upper() == "POST":
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=data,
                )
            else:
                raise ValueError(f"Metodo nao suportado: {method}")

            if response.status_code == 401:
                # Token expirado, reautentica
                self._access_token = None
                await self.authenticate()
                return await self._make_request(method, endpoint, data, params)

            if response.status_code == 429:
                raise RateLimitError("Limite de requisicoes excedido")

            if response.status_code >= 400:
                self._handle_error_response(response)

            return response.json()

        except httpx.RequestError as exc:
            raise BankingAdapterError(
                "Erro de conexao",
                code="CONNECTION_ERROR",
                details={"error": str(exc)},
            ) from exc

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Trata resposta de erro."""
        try:
            error_data = response.json()
            # Itau usa estrutura errors[]
            errors = error_data.get("errors", [])
            if errors:
                error_code = errors[0].get("code", "UNKNOWN")
                error_msg = errors[0].get("message", response.text)
            else:
                error_code = str(response.status_code)
                error_msg = response.text
        except Exception:  # pylint: disable=broad-except
            error_code = str(response.status_code)
            error_msg = response.text

        if "saldo" in error_msg.lower() and "insuficiente" in error_msg.lower():
            raise InsufficientFundsError(error_msg, code=error_code)

        conta_invalida = "invalida" in error_msg.lower()
        conta_nao_encontrada = "nao encontrada" in error_msg.lower()
        if "conta" in error_msg.lower() and (conta_invalida or conta_nao_encontrada):
            raise InvalidAccountError(error_msg, code=error_code)

        raise BankingAdapterError(error_msg, code=error_code)

    async def get_balance(self) -> AccountBalance:
        """Consulta saldo da conta."""
        data = await self._make_request("GET", self.BALANCE_ENDPOINT)

        # Itau retorna em data.balances[]
        balances = data.get("data", {}).get("balances", [])

        available = Decimal("0")
        blocked = Decimal("0")

        for balance in balances:
            amount = self._parse_amount(balance.get("amount", 0))
            balance_type = balance.get("balanceType", "")

            if balance_type == "AVAILABLE":
                available = amount
            elif balance_type == "BLOCKED":
                blocked = amount

        return AccountBalance(
            available=available,
            blocked=blocked,
            total=available + blocked,
            currency=data.get("data", {}).get("currency", "BRL"),
            updated_at=datetime.fromisoformat(data.get("data", {}).get("updateDateTime", datetime.now().isoformat())),
        )

    async def get_statement(
        self,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """Consulta extrato da conta."""
        params = {
            "fromBookingDate": start_date.isoformat(),
            "toBookingDate": end_date.isoformat(),
            "page-size": 100,
        }

        data = await self._make_request(
            "GET",
            self.STATEMENT_ENDPOINT,
            params=params,
        )

        transactions = []
        tx_data = data.get("data", {}).get("transactions", [])
        for tx_item in tx_data:
            transactions.append(self._parse_transaction(tx_item))

        return BankStatement(
            account_agency=self.credentials.agency or "",
            account_number=self.credentials.account or "",
            account_type=AccountType.CHECKING,
            start_date=start_date,
            end_date=end_date,
            opening_balance=self._parse_amount(data.get("data", {}).get("openingBalance", 0)),
            closing_balance=self._parse_amount(data.get("data", {}).get("closingBalance", 0)),
            transactions=transactions,
            bank_code=self.BANK_CODE,
            bank_name=self.BANK_NAME,
        )

    def _parse_transaction(self, tx_item: dict) -> BankTransaction:
        """Converte transacao do formato Itau."""
        tx_type_str = tx_item.get("transactionType", "CREDIT")
        tx_type = self.TRANSACTION_TYPE_MAP.get(tx_type_str, TransactionType.CREDIT)

        # Itau usa creditDebitType para indicar direcao
        credit_debit = tx_item.get("creditDebitType", "CREDIT")
        if credit_debit == "DEBIT" and tx_type == TransactionType.CREDIT:
            tx_type = TransactionType.DEBIT

        return BankTransaction(
            transaction_id=tx_item.get("transactionId", ""),
            date=datetime.fromisoformat(tx_item.get("transactionDateTime", datetime.now().isoformat())),
            amount=self._parse_amount(tx_item.get("amount", 0)),
            transaction_type=tx_type,
            description=tx_item.get("transactionName", ""),
            balance_after=self._parse_amount(tx_item.get("balanceAfterTransaction")),
            counterpart_name=tx_item.get("payeeMCC", {}).get("name"),
            counterpart_document=tx_item.get("completedAuthorisedPaymentType", {}).get("document"),
            counterpart_bank=tx_item.get("completedAuthorisedPaymentType", {}).get("bankCode"),
            counterpart_agency=tx_item.get("completedAuthorisedPaymentType", {}).get("branchCode"),
            counterpart_account=tx_item.get("completedAuthorisedPaymentType", {}).get("accountNumber"),
            reference=tx_item.get("endToEndIdentification"),
        )

    async def initiate_payment(
        self,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """Inicia pagamento TED/DOC."""
        payload = {
            "data": {
                "localInstrument": "MANU",  # Manual
                "payment": {
                    "amount": str(payment.amount),
                    "currency": "BRL",
                },
                "creditorAccount": {
                    "ispb": self._get_ispb(payment.beneficiary_bank),
                    "issuer": payment.beneficiary_agency,
                    "number": payment.beneficiary_account,
                    "accountType": self._map_account_type(payment.beneficiary_account_type),
                },
                "creditor": {
                    "personType": self._get_person_type(payment.beneficiary_document),
                    "name": payment.beneficiary_name,
                    "cpfCnpj": self._format_document(payment.beneficiary_document),
                },
                "remittanceInformation": payment.description or "Transferencia",
            }
        }

        if payment.scheduled_date:
            payload["data"]["date"] = payment.scheduled_date.isoformat()

        data = await self._make_request("POST", self.PAYMENT_ENDPOINT, data=payload)

        response_data = data.get("data", {})

        return PaymentResponse(
            payment_id=response_data.get("paymentId", ""),
            status=self._parse_payment_status(response_data.get("status", "")),
            amount=payment.amount,
            scheduled_date=payment.scheduled_date,
            authentication_code=response_data.get("endToEndId"),
        )

    def _get_ispb(self, bank_code: str) -> str:
        """Retorna ISPB do banco."""
        # Mapeamento de codigo COMPE para ISPB
        ispb_map = {
            "001": "00000000",  # BB
            "341": "60701190",  # Itau
            "237": "60746948",  # Bradesco
            "033": "90400888",  # Santander
            "104": "00360305",  # Caixa
        }
        return ispb_map.get(bank_code, bank_code)

    def _map_account_type(self, account_type: AccountType) -> str:
        """Mapeia tipo de conta para formato Itau."""
        type_map = {
            AccountType.CHECKING: "CACC",
            AccountType.SAVINGS: "SVGS",
            AccountType.SALARY: "SLRY",
            AccountType.PAYMENT: "TRAN",
        }
        return type_map.get(account_type, "CACC")

    def _get_person_type(self, document: str) -> str:
        """Retorna tipo de pessoa baseado no documento."""
        clean_doc = self._format_document(document)
        if len(clean_doc) == 11:
            return "PESSOA_NATURAL"
        return "PESSOA_JURIDICA"

    def _parse_payment_status(self, status: str) -> PaymentStatus:
        """Converte status do Itau."""
        status_map = {
            "PDNG": PaymentStatus.PENDING,
            "PART": PaymentStatus.PROCESSING,
            "ACSP": PaymentStatus.PROCESSING,
            "ACSC": PaymentStatus.COMPLETED,
            "ACCC": PaymentStatus.COMPLETED,
            "SCHD": PaymentStatus.SCHEDULED,
            "CANC": PaymentStatus.CANCELLED,
            "RJCT": PaymentStatus.FAILED,
        }
        return status_map.get(status.upper(), PaymentStatus.PENDING)

    async def get_payment_status(
        self,
        payment_id: str,
    ) -> PaymentResponse:
        """Consulta status de pagamento."""
        endpoint = f"{self.PAYMENT_ENDPOINT}/{payment_id}"
        data = await self._make_request("GET", endpoint)

        response_data = data.get("data", {})

        scheduled = None
        if response_data.get("date"):
            scheduled = date.fromisoformat(response_data["date"])

        processed = None
        if response_data.get("completionDateTime"):
            processed = datetime.fromisoformat(response_data["completionDateTime"])

        return PaymentResponse(
            payment_id=payment_id,
            status=self._parse_payment_status(response_data.get("status", "")),
            amount=self._parse_amount(response_data.get("payment", {}).get("amount", 0)),
            scheduled_date=scheduled,
            processed_at=processed,
            receipt_url=response_data.get("receiptUrl"),
            authentication_code=response_data.get("endToEndId"),
            error_message=response_data.get("rejectionReason", {}).get("detail"),
        )

    async def cancel_payment(
        self,
        payment_id: str,
    ) -> bool:
        """Cancela pagamento agendado."""
        endpoint = f"{self.PAYMENT_ENDPOINT}/{payment_id}"
        payload = {"data": {"status": "CANC"}}

        try:
            data = await self._make_request("PATCH", endpoint, data=payload)
            return data.get("data", {}).get("status") == "CANC"
        except BankingAdapterError:
            return False

    async def validate_pix_key(
        self,
        key: str,
    ) -> PixKey | None:
        """Valida chave PIX."""
        endpoint = f"{self.PIX_ENDPOINT}/dict/v1/dict/{key}"

        try:
            data = await self._make_request("GET", endpoint)

            key_data = data.get("data", {})

            return PixKey(
                key_type=key_data.get("keyType", ""),
                key_value=key,
                owner_name=key_data.get("owner", {}).get("name"),
                owner_document=key_data.get("owner", {}).get("taxIdNumber"),
                bank_code=key_data.get("account", {}).get("participant"),
                bank_name=key_data.get("account", {}).get("participantName"),
                agency=key_data.get("account", {}).get("branch"),
                account=key_data.get("account", {}).get("accountNumber"),
                account_type=AccountType.CHECKING,
            )

        except BankingAdapterError:
            return None

    async def initiate_pix(
        self,
        pix_key: str,
        amount: Decimal,
        description: str | None = None,
    ) -> PaymentResponse:
        """Inicia transferencia PIX."""
        # Primeiro valida a chave
        pix_info = await self.validate_pix_key(pix_key)
        if not pix_info:
            raise BankingAdapterError(
                "Chave PIX invalida ou nao encontrada",
                code="INVALID_PIX_KEY",
            )

        payload = {
            "data": {
                "localInstrument": "DICT",
                "payment": {
                    "amount": str(amount),
                    "currency": "BRL",
                },
                "proxy": pix_key,
                "remittanceInformation": description or "Transferencia PIX",
            }
        }

        data = await self._make_request(
            "POST",
            self.PAYMENT_ENDPOINT,
            data=payload,
        )

        response_data = data.get("data", {})

        return PaymentResponse(
            payment_id=response_data.get("paymentId", ""),
            status=self._parse_payment_status(response_data.get("status", "")),
            amount=amount,
            processed_at=(datetime.now() if response_data.get("status") == "ACCC" else None),
            authentication_code=response_data.get("endToEndId"),
        )

    async def close(self) -> None:
        """Fecha cliente HTTP."""
        if self._client:
            await self._client.aclose()
            self._client = None
