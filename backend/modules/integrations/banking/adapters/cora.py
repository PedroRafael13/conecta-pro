"""
Adapter Cora - Open Banking.

Documentação: https://developers.cora.com.br/
API: https://api.cora.com.br/

Autenticação: OAuth2 Client Credentials
"""

import logging
import ssl
from datetime import date, datetime, timedelta
from decimal import Decimal

import httpx

from .base import (
    AccountBalance,
    AccountType,
    AuthenticationError,
    BankCode,
    BankCredentials,
    BankingAdapterError,
    BankStatement,
    BankTransaction,
    BaseBankingAdapter,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PixKey,
    TransactionType,
)

logger = logging.getLogger(__name__)


class CoraAdapter(BaseBankingAdapter):
    """
    Adapter para Cora.

    Funcionalidades:
    - Consulta de saldo
    - Consulta de extrato
    - Transferências PIX
    - Emissão de boletos (cobrança)
    - Pagamento de boletos

    Banco digital focado em PJ com API moderna.
    Usa mTLS para autenticação (Integração Direta).
    """

    BANK_CODE = BankCode.CORA
    BANK_NAME = "Cora"
    # URLs para Integração Direta (mTLS)
    API_BASE_URL_SANDBOX = "https://matls-clients.api.stage.cora.com.br"
    API_BASE_URL_PRODUCTION = "https://matls-clients.api.cora.com.br"

    def __init__(self, credentials: BankCredentials) -> None:
        """Inicializa adapter Cora."""
        super().__init__(credentials)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP com certificado mTLS."""
        if self._client is None:
            # Configura SSL com certificado para mTLS
            ssl_context = ssl.create_default_context()

            if self.credentials.certificate_path:
                ssl_context.load_cert_chain(
                    certfile=self.credentials.certificate_path,
                    keyfile=self.credentials.private_key_path,
                )

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                verify=ssl_context,
                timeout=30.0,
            )
        return self._client

    async def authenticate(self) -> bool:
        """
        Autentica via OAuth2 Client Credentials com mTLS.

        Returns:
            True se autenticado com sucesso.
        """
        try:
            client = await self._get_client()

            # Integração Direta usa apenas client_id (certificado faz autenticação)
            response = await client.post(
                "/token",
                data={
                    "client_id": self.credentials.client_id,
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error("Erro autenticação Cora: %s", response.text)
                raise AuthenticationError(
                    f"Falha na autenticação: {response.status_code}",
                    code="AUTH_FAILED",
                )

            data = response.json()
            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Autenticado na Cora com sucesso")
            return True

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error("Erro ao autenticar na Cora: %s", str(e))
            raise AuthenticationError(f"Erro de autenticação: {str(e)}")

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict:
        """Faz requisição autenticada."""
        await self.ensure_authenticated()

        client = await self._get_client()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._access_token}"
        headers["Content-Type"] = "application/json"

        response = await client.request(method, endpoint, headers=headers, **kwargs)

        if response.status_code == 401:
            # Token expirado, reautentica
            self._access_token = None
            await self.authenticate()
            headers["Authorization"] = f"Bearer {self._access_token}"
            response = await client.request(method, endpoint, headers=headers, **kwargs)

        if response.status_code >= 400:
            raise BankingAdapterError(
                f"Erro na API Cora: {response.status_code}",
                code=str(response.status_code),
                details={"response": response.text},
            )

        return response.json() if response.text else {}

    async def get_balance(self) -> AccountBalance:
        """Consulta saldo da conta Cora."""
        data = await self._request("GET", "/third-party/account/balance")

        # Valores em centavos
        balance = self._parse_amount(data.get("balance", 0) / 100)
        blocked = self._parse_amount(data.get("blockedBalance", 0) / 100)

        return AccountBalance(
            available=balance,
            blocked=blocked,
            total=balance + blocked,
            currency="BRL",
            updated_at=datetime.now(),
        )

    async def get_statement(
        self,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """Consulta extrato da conta Cora."""
        data = await self._request(
            "GET",
            "/bank-statement/statement",
            params={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        )

        transactions = []
        for item in data.get("entries", []):
            # Determina tipo de transação
            entry_type = item.get("type", "").upper()
            tx_type = TransactionType.CREDIT if entry_type == "CREDIT" else TransactionType.DEBIT

            # Mapeia tipo específico da transação
            transaction = item.get("transaction", {})
            tx_category = transaction.get("type", "").upper()
            if "PIX" in tx_category:
                tx_type = TransactionType.PIX
            elif "TRANSFER" in tx_category:
                tx_type = TransactionType.TED
            elif "INVOICE" in tx_category or "PAYMENT" in tx_category:
                tx_type = TransactionType.BOLETO

            # Valor em centavos
            amount = self._parse_amount(item.get("amount", 0) / 100)

            counterparty = transaction.get("counterParty", {})

            transactions.append(
                BankTransaction(
                    transaction_id=item.get("id", ""),
                    date=datetime.fromisoformat(item.get("createdAt", "").replace("+00", "+00:00")),
                    amount=amount,
                    transaction_type=tx_type,
                    description=transaction.get("description", ""),
                    counterpart_name=counterparty.get("name"),
                    counterpart_document=counterparty.get("identity"),
                )
            )

        # Saldos inicial e final em centavos
        opening = self._parse_amount(data.get("start", {}).get("balance", 0) / 100)
        closing = self._parse_amount(data.get("end", {}).get("balance", 0) / 100)

        return BankStatement(
            account_agency=self.credentials.agency or "0001",
            account_number=self.credentials.account or "",
            account_type=AccountType.PAYMENT,
            start_date=start_date,
            end_date=end_date,
            opening_balance=opening,
            closing_balance=closing,
            transactions=transactions,
            bank_code=self.BANK_CODE,
            bank_name=self.BANK_NAME,
        )

    async def initiate_payment(
        self,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """Inicia pagamento de boleto."""
        # Valor em centavos
        amount_cents = int(payment.amount * 100)

        data = await self._request(
            "POST",
            "/v1/payments/invoices",
            json={
                "barcode": payment.barcode,
                "amount": amount_cents,
                "scheduled_date": (payment.scheduled_date or date.today()).isoformat(),
            },
        )

        return PaymentResponse(
            payment_id=data.get("id", ""),
            status=PaymentStatus.PROCESSING,
            amount=payment.amount,
            scheduled_date=payment.scheduled_date,
        )

    async def get_payment_status(
        self,
        payment_id: str,
    ) -> PaymentResponse:
        """Consulta status de pagamento."""
        data = await self._request(
            "GET",
            f"/v1/payments/{payment_id}",
        )

        status_map = {
            "COMPLETED": PaymentStatus.COMPLETED,
            "PROCESSING": PaymentStatus.PROCESSING,
            "SCHEDULED": PaymentStatus.SCHEDULED,
            "FAILED": PaymentStatus.FAILED,
            "CANCELLED": PaymentStatus.CANCELLED,
            "PENDING": PaymentStatus.PENDING,
        }

        amount = self._parse_amount(data.get("amount", {}).get("value", 0) / 100)

        return PaymentResponse(
            payment_id=payment_id,
            status=status_map.get(data.get("status", ""), PaymentStatus.PENDING),
            amount=amount,
        )

    async def cancel_payment(
        self,
        payment_id: str,
    ) -> bool:
        """Cancela pagamento agendado."""
        try:
            await self._request(
                "DELETE",
                f"/v1/payments/{payment_id}",
            )
            return True
        except BankingAdapterError:
            return False

    async def validate_pix_key(
        self,
        key: str,
    ) -> PixKey | None:
        """Valida chave PIX."""
        try:
            data = await self._request(
                "GET",
                "/v1/pix/keys/decode",
                params={"key": key},
            )

            return PixKey(
                key_type=data.get("key_type", ""),
                key_value=key,
                owner_name=data.get("owner", {}).get("name", ""),
                owner_document=data.get("owner", {}).get("document", ""),
                bank_code=data.get("account", {}).get("participant", ""),
                agency=data.get("account", {}).get("branch", ""),
                account=data.get("account", {}).get("number", ""),
            )
        except BankingAdapterError:
            return None

    async def initiate_pix(
        self,
        pix_key: str,
        amount: Decimal,
        description: str | None = None,
    ) -> PaymentResponse:
        """Inicia transferência PIX."""
        # Valor em centavos
        amount_cents = int(amount * 100)

        data = await self._request(
            "POST",
            "/v1/pix/payments",
            json={
                "key": pix_key,
                "amount": amount_cents,
                "description": description or "",
            },
        )

        status = PaymentStatus.COMPLETED if data.get("status") == "COMPLETED" else PaymentStatus.PROCESSING

        return PaymentResponse(
            payment_id=data.get("id", ""),
            status=status,
            amount=amount,
            authentication_code=data.get("end_to_end_id"),
        )

    async def generate_invoice(
        self,
        amount: Decimal,
        due_date: date,
        payer_name: str,
        payer_document: str,
        description: str,
    ) -> dict:
        """Gera boleto/invoice de cobrança."""
        # Valor em centavos
        amount_cents = int(amount * 100)

        data = await self._request(
            "POST",
            "/v1/invoices",
            json={
                "amount": amount_cents,
                "due_date": due_date.isoformat(),
                "customer": {
                    "name": payer_name,
                    "document": self._format_document(payer_document),
                },
                "description": description,
                "payment_options": ["BANK_SLIP", "PIX"],
            },
        )

        return {
            "invoice_id": data.get("id", ""),
            "barcode": data.get("bank_slip", {}).get("barcode", ""),
            "digitable_line": data.get("bank_slip", {}).get("digitable_line", ""),
            "pdf_url": data.get("bank_slip", {}).get("url", ""),
            "pix_qrcode": data.get("pix", {}).get("qr_code", ""),
            "pix_copy_paste": data.get("pix", {}).get("copy_and_paste", ""),
        }

    async def generate_pix_charge(
        self,
        amount: Decimal,
        description: str,
        payer_name: str | None = None,
        payer_document: str | None = None,
        expiracao_segundos: int = 86400,
    ) -> dict:
        """Gera cobrança PIX avulsa (QR Code dinâmico) via Cora."""
        amount_cents = int(amount * 100)

        body: dict = {
            "amount": amount_cents,
            "description": description,
            "payment_options": ["PIX"],
            "expiration_seconds": expiracao_segundos,
        }
        if payer_name:
            body["customer"] = {"name": payer_name}
            if payer_document:
                body["customer"]["document"] = self._format_document(payer_document)

        data = await self._request("POST", "/v1/invoices", json=body)

        return {
            "charge_id": data.get("id", ""),
            "pix_qrcode": data.get("pix", {}).get("qr_code", ""),
            "pix_copy_paste": data.get("pix", {}).get("copy_and_paste", ""),
            "amount": float(amount),
        }

    async def list_invoices(
        self,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        """Lista boletos/invoices emitidos."""
        params = {}
        if status:
            params["status"] = status
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        data = await self._request(
            "GET",
            "/v1/invoices",
            params=params,
        )

        return data.get("items", [])

    async def close(self) -> None:
        """Fecha conexão."""
        if self._client:
            await self._client.aclose()
            self._client = None
