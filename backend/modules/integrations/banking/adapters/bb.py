"""
Adapter para integracao com Banco do Brasil.

Implementa a API Open Banking do BB para consultas
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


class BBAdapter(BaseBankingAdapter):
    """
    Adapter para Banco do Brasil.

    Implementa integracao com APIs Open Banking do BB:
    - Consulta de saldo
    - Consulta de extrato
    - Iniciacao de pagamentos (TED, PIX, Boleto)
    - Consulta de status de pagamentos
    """

    BANK_CODE = "001"
    BANK_NAME = "Banco do Brasil"
    API_BASE_URL_SANDBOX = "https://api.sandbox.bb.com.br"
    API_BASE_URL_PRODUCTION = "https://api.bb.com.br"

    # Endpoints
    OAUTH_ENDPOINT = "/oauth/token"
    BALANCE_ENDPOINT = "/accounts/v1/balance"
    STATEMENT_ENDPOINT = "/accounts/v1/transactions"
    PAYMENT_ENDPOINT = "/payments/v1/transfers"
    PIX_ENDPOINT = "/pix/v1"

    # Mapeamento de tipos de transacao do BB
    TRANSACTION_TYPE_MAP = {
        "CREDITO": TransactionType.CREDIT,
        "DEBITO": TransactionType.DEBIT,
        "TED": TransactionType.TED,
        "DOC": TransactionType.DOC,
        "PIX": TransactionType.PIX,
        "BOLETO": TransactionType.BOLETO,
        "TARIFA": TransactionType.TARIFA,
    }

    def __init__(self, credentials: BankCredentials) -> None:
        """Inicializa adapter BB."""
        super().__init__(credentials)
        self._client: httpx.AsyncClient | None = None

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
        Autentica no BB usando OAuth2 Client Credentials.

        Returns:
            True se autenticado com sucesso
        """
        try:
            client = await self._get_client()

            # Gera assinatura HMAC se em producao
            timestamp = datetime.now().isoformat()
            signature = self._generate_signature(timestamp)

            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scope": "accounts payments pix",
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Timestamp": timestamp,
                "X-Signature": signature,
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

                logger.info(
                    "BB: Autenticacao realizada",
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
            logger.error("BB: Erro de conexao", extra={"error": str(exc)})
            raise BankingAdapterError(
                "Erro de conexao com BB",
                code="CONNECTION_ERROR",
                details={"error": str(exc)},
            ) from exc

    def _generate_signature(self, timestamp: str) -> str:
        """Gera assinatura HMAC para requisicao."""
        message = f"{self.credentials.client_id}{timestamp}"
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

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "gw-dev-app-key": self.credentials.client_id,
        }

        if self.credentials.agency and self.credentials.account:
            headers["X-Agency"] = self.credentials.agency
            headers["X-Account"] = self.credentials.account

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
            error_code = error_data.get("code", "UNKNOWN")
            error_msg = error_data.get("message", response.text)
        except Exception:  # pylint: disable=broad-except
            error_code = str(response.status_code)
            error_msg = response.text

        if "saldo insuficiente" in error_msg.lower():
            raise InsufficientFundsError(error_msg, code=error_code)

        if "conta" in error_msg.lower() and "invalida" in error_msg.lower():
            raise InvalidAccountError(error_msg, code=error_code)

        raise BankingAdapterError(error_msg, code=error_code)

    async def get_balance(self) -> AccountBalance:
        """Consulta saldo da conta."""
        data = await self._make_request("GET", self.BALANCE_ENDPOINT)

        return AccountBalance(
            available=self._parse_amount(data.get("availableAmount", 0)),
            blocked=self._parse_amount(data.get("blockedAmount", 0)),
            total=self._parse_amount(data.get("totalAmount", 0)),
            currency=data.get("currency", "BRL"),
            updated_at=datetime.fromisoformat(data.get("updateDateTime", datetime.now().isoformat())),
        )

    async def get_statement(
        self,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """Consulta extrato da conta."""
        params = {
            "fromDate": start_date.isoformat(),
            "toDate": end_date.isoformat(),
            "limit": 100,
        }

        data = await self._make_request(
            "GET",
            self.STATEMENT_ENDPOINT,
            params=params,
        )

        transactions = []
        for tx in data.get("transactions", []):
            transactions.append(self._parse_transaction(tx))

        return BankStatement(
            account_agency=self.credentials.agency or "",
            account_number=self.credentials.account or "",
            account_type=AccountType.CHECKING,
            start_date=start_date,
            end_date=end_date,
            opening_balance=self._parse_amount(data.get("openingBalance", 0)),
            closing_balance=self._parse_amount(data.get("closingBalance", 0)),
            transactions=transactions,
            bank_code=self.BANK_CODE,
            bank_name=self.BANK_NAME,
        )

    def _parse_transaction(self, tx: dict) -> BankTransaction:
        """Converte transacao do formato BB."""
        tx_type_str = tx.get("type", "CREDITO")
        tx_type = self.TRANSACTION_TYPE_MAP.get(tx_type_str, TransactionType.CREDIT)

        return BankTransaction(
            transaction_id=tx.get("transactionId", ""),
            date=datetime.fromisoformat(tx.get("transactionDateTime", "")),
            amount=self._parse_amount(tx.get("amount", 0)),
            transaction_type=tx_type,
            description=tx.get("description", ""),
            balance_after=self._parse_amount(tx.get("balanceAfter", 0)),
            counterpart_name=tx.get("counterpartName"),
            counterpart_document=tx.get("counterpartDocument"),
            counterpart_bank=tx.get("counterpartBank"),
            counterpart_agency=tx.get("counterpartAgency"),
            counterpart_account=tx.get("counterpartAccount"),
            reference=tx.get("reference"),
        )

    async def initiate_payment(
        self,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """Inicia pagamento TED/DOC."""
        payload = {
            "amount": float(payment.amount),
            "beneficiary": {
                "name": payment.beneficiary_name,
                "document": self._format_document(payment.beneficiary_document),
                "bank": payment.beneficiary_bank,
                "agency": payment.beneficiary_agency,
                "account": payment.beneficiary_account,
                "accountType": payment.beneficiary_account_type.value,
            },
            "description": payment.description or "Transferencia",
        }

        if payment.scheduled_date:
            payload["scheduledDate"] = payment.scheduled_date.isoformat()

        data = await self._make_request("POST", self.PAYMENT_ENDPOINT, data=payload)

        return PaymentResponse(
            payment_id=data.get("paymentId", ""),
            status=self._parse_payment_status(data.get("status", "")),
            amount=payment.amount,
            scheduled_date=payment.scheduled_date,
            authentication_code=data.get("authenticationCode"),
        )

    def _parse_payment_status(self, status: str) -> PaymentStatus:
        """Converte status do BB."""
        status_map = {
            "PENDENTE": PaymentStatus.PENDING,
            "PROCESSANDO": PaymentStatus.PROCESSING,
            "CONCLUIDO": PaymentStatus.COMPLETED,
            "AGENDADO": PaymentStatus.SCHEDULED,
            "CANCELADO": PaymentStatus.CANCELLED,
            "FALHOU": PaymentStatus.FAILED,
        }
        return status_map.get(status.upper(), PaymentStatus.PENDING)

    async def get_payment_status(
        self,
        payment_id: str,
    ) -> PaymentResponse:
        """Consulta status de pagamento."""
        endpoint = f"{self.PAYMENT_ENDPOINT}/{payment_id}"
        data = await self._make_request("GET", endpoint)

        scheduled = None
        if data.get("scheduledDate"):
            scheduled = date.fromisoformat(data["scheduledDate"])

        processed = None
        if data.get("processedDateTime"):
            processed = datetime.fromisoformat(data["processedDateTime"])

        return PaymentResponse(
            payment_id=payment_id,
            status=self._parse_payment_status(data.get("status", "")),
            amount=self._parse_amount(data.get("amount", 0)),
            scheduled_date=scheduled,
            processed_at=processed,
            receipt_url=data.get("receiptUrl"),
            authentication_code=data.get("authenticationCode"),
            error_message=data.get("errorMessage"),
        )

    async def cancel_payment(
        self,
        payment_id: str,
    ) -> bool:
        """Cancela pagamento agendado."""
        endpoint = f"{self.PAYMENT_ENDPOINT}/{payment_id}/cancel"
        data = await self._make_request("POST", endpoint)
        return data.get("cancelled", False)

    async def validate_pix_key(
        self,
        key: str,
    ) -> PixKey | None:
        """Valida chave PIX."""
        endpoint = f"{self.PIX_ENDPOINT}/dict/{key}"

        try:
            data = await self._make_request("GET", endpoint)

            return PixKey(
                key_type=data.get("keyType", ""),
                key_value=key,
                owner_name=data.get("ownerName"),
                owner_document=data.get("ownerDocument"),
                bank_code=data.get("bankCode"),
                bank_name=data.get("bankName"),
                agency=data.get("agency"),
                account=data.get("account"),
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
        payload = {
            "pixKey": pix_key,
            "amount": float(amount),
            "description": description or "Transferencia PIX",
        }

        data = await self._make_request(
            "POST",
            f"{self.PIX_ENDPOINT}/transfers",
            data=payload,
        )

        return PaymentResponse(
            payment_id=data.get("e2eId", ""),
            status=self._parse_payment_status(data.get("status", "")),
            amount=amount,
            processed_at=datetime.now() if data.get("status") == "CONCLUIDO" else None,
            authentication_code=data.get("e2eId"),
        )

    async def close(self) -> None:
        """Fecha cliente HTTP."""
        if self._client:
            await self._client.aclose()
            self._client = None
