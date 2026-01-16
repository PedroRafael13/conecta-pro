"""
Adapter Banco Inter - Open Banking.

Documentação: https://developers.inter.co/
API: https://cdpj.partners.bancointer.com.br/

Autenticação: OAuth2 + mTLS (certificado digital)
"""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
import ssl

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


class InterAdapter(BaseBankingAdapter):
    """
    Adapter para Banco Inter.

    Funcionalidades:
    - Consulta de saldo
    - Consulta de extrato
    - Transferências PIX
    - Pagamento de boletos
    - Emissão de boletos (cobrança)

    Requer certificado digital para autenticação mTLS.
    """

    BANK_CODE = BankCode.INTER
    BANK_NAME = "Banco Inter"
    API_BASE_URL_SANDBOX = "https://cdpj-sandbox.partners.bancointer.com.br"
    API_BASE_URL_PRODUCTION = "https://cdpj.partners.bancointer.com.br"

    # Scopes disponíveis
    SCOPES = {
        "extrato": "extrato.read",
        "saldo": "cob.read",
        "pix": "pix.write pix.read",
        "boleto": "boleto-cobranca.write boleto-cobranca.read",
        "pagamento": "pagamento-boleto.write pagamento-boleto.read",
    }

    def __init__(self, credentials: BankCredentials) -> None:
        """Inicializa adapter Inter."""
        super().__init__(credentials)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP com certificado mTLS."""
        if self._client is None:
            # Configura SSL com certificado
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
        Autentica via OAuth2 com certificado mTLS.

        Returns:
            True se autenticado com sucesso.
        """
        try:
            client = await self._get_client()

            # Monta scopes necessários
            scopes = " ".join([
                self.SCOPES["extrato"],
                self.SCOPES["saldo"],
                self.SCOPES["pix"],
                self.SCOPES["boleto"],
                self.SCOPES["pagamento"],
            ])

            response = await client.post(
                "/oauth/v2/token",
                data={
                    "client_id": self.credentials.client_id,
                    "client_secret": self.credentials.client_secret,
                    "grant_type": "client_credentials",
                    "scope": scopes,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error("Erro autenticação Inter: %s", response.text)
                raise AuthenticationError(
                    f"Falha na autenticação: {response.status_code}",
                    code="AUTH_FAILED",
                )

            data = response.json()
            self._access_token = data["access_token"]
            expires_in = data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            logger.info("Autenticado no Banco Inter com sucesso")
            return True

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error("Erro ao autenticar no Inter: %s", str(e))
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

        response = await client.request(method, endpoint, headers=headers, **kwargs)

        if response.status_code == 401:
            # Token expirado, reautentica
            self._access_token = None
            await self.authenticate()
            headers["Authorization"] = f"Bearer {self._access_token}"
            response = await client.request(method, endpoint, headers=headers, **kwargs)

        if response.status_code >= 400:
            raise BankingAdapterError(
                f"Erro na API Inter: {response.status_code}",
                code=str(response.status_code),
                details={"response": response.text},
            )

        return response.json() if response.text else {}

    async def get_balance(self) -> AccountBalance:
        """Consulta saldo da conta Inter."""
        data = await self._request("GET", "/banking/v2/saldo")

        return AccountBalance(
            available=self._parse_amount(data.get("disponivel", 0)),
            blocked=self._parse_amount(data.get("bloqueadoCheque", 0)),
            total=self._parse_amount(data.get("disponivel", 0)),
            currency="BRL",
            updated_at=datetime.now(),
        )

    async def get_statement(
        self,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """Consulta extrato da conta Inter."""
        data = await self._request(
            "GET",
            "/banking/v2/extrato",
            params={
                "dataInicio": start_date.strftime("%Y-%m-%d"),
                "dataFim": end_date.strftime("%Y-%m-%d"),
            },
        )

        transactions = []
        for item in data.get("transacoes", []):
            tx_type = TransactionType.CREDIT if item.get("tipoOperacao") == "C" else TransactionType.DEBIT

            # Mapeia tipo específico
            tipo = item.get("tipoTransacao", "").upper()
            if "PIX" in tipo:
                tx_type = TransactionType.PIX
            elif "TED" in tipo:
                tx_type = TransactionType.TED
            elif "BOLETO" in tipo:
                tx_type = TransactionType.BOLETO

            transactions.append(BankTransaction(
                transaction_id=item.get("idTransacao", ""),
                date=datetime.fromisoformat(item.get("dataEntrada", "")),
                amount=self._parse_amount(item.get("valor", 0)),
                transaction_type=tx_type,
                description=item.get("descricao", ""),
                balance_after=self._parse_amount(item.get("saldo", 0)) if item.get("saldo") else None,
            ))

        return BankStatement(
            account_agency=self.credentials.agency or "",
            account_number=self.credentials.account or "",
            account_type=AccountType.CHECKING,
            start_date=start_date,
            end_date=end_date,
            opening_balance=Decimal("0"),
            closing_balance=Decimal("0"),
            transactions=transactions,
            bank_code=self.BANK_CODE,
            bank_name=self.BANK_NAME,
        )

    async def initiate_payment(
        self,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """Inicia pagamento de boleto."""
        data = await self._request(
            "POST",
            "/banking/v2/pagamento",
            json={
                "codBarraLinhaDigitavel": payment.barcode,
                "valorPagar": float(payment.amount),
                "dataPagamento": (payment.scheduled_date or date.today()).strftime("%Y-%m-%d"),
            },
        )

        return PaymentResponse(
            payment_id=data.get("codigoTransacao", ""),
            status=PaymentStatus.PROCESSING,
            amount=payment.amount,
            scheduled_date=payment.scheduled_date,
            authentication_code=data.get("autenticacao"),
        )

    async def get_payment_status(
        self,
        payment_id: str,
    ) -> PaymentResponse:
        """Consulta status de pagamento."""
        data = await self._request(
            "GET",
            f"/banking/v2/pagamento/{payment_id}",
        )

        status_map = {
            "APROVADO": PaymentStatus.COMPLETED,
            "PROCESSANDO": PaymentStatus.PROCESSING,
            "AGENDADO": PaymentStatus.SCHEDULED,
            "REJEITADO": PaymentStatus.FAILED,
            "CANCELADO": PaymentStatus.CANCELLED,
        }

        return PaymentResponse(
            payment_id=payment_id,
            status=status_map.get(data.get("situacao", ""), PaymentStatus.PENDING),
            amount=self._parse_amount(data.get("valor", 0)),
        )

    async def cancel_payment(
        self,
        payment_id: str,
    ) -> bool:
        """Cancela pagamento agendado."""
        try:
            await self._request(
                "DELETE",
                f"/banking/v2/pagamento/{payment_id}",
            )
            return True
        except BankingAdapterError:
            return False

    async def validate_pix_key(
        self,
        key: str,
    ) -> Optional[PixKey]:
        """Valida chave PIX."""
        try:
            data = await self._request(
                "GET",
                "/pix/v2/dict/key",
                params={"chave": key},
            )

            return PixKey(
                key_type=data.get("tipoChave", ""),
                key_value=key,
                owner_name=data.get("nome", ""),
                owner_document=data.get("cpfCnpj", ""),
                bank_code=data.get("ispb", ""),
                agency=data.get("agencia", ""),
                account=data.get("conta", ""),
            )
        except BankingAdapterError:
            return None

    async def initiate_pix(
        self,
        pix_key: str,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> PaymentResponse:
        """Inicia transferência PIX."""
        data = await self._request(
            "POST",
            "/pix/v2/pix",
            json={
                "chave": pix_key,
                "valor": str(amount),
                "descricao": description or "",
            },
        )

        return PaymentResponse(
            payment_id=data.get("endToEndId", ""),
            status=PaymentStatus.COMPLETED if data.get("status") == "CONCLUIDO" else PaymentStatus.PROCESSING,
            amount=amount,
            authentication_code=data.get("endToEndId"),
        )

    async def generate_boleto(
        self,
        amount: Decimal,
        due_date: date,
        payer_name: str,
        payer_document: str,
        description: str,
    ) -> dict:
        """Gera boleto de cobrança."""
        data = await self._request(
            "POST",
            "/cobranca/v3/cobrancas",
            json={
                "seuNumero": f"COB{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "valorNominal": float(amount),
                "dataVencimento": due_date.strftime("%Y-%m-%d"),
                "numDiasAgenda": 30,
                "pagador": {
                    "nome": payer_name,
                    "cpfCnpj": self._format_document(payer_document),
                },
                "mensagem": {
                    "linha1": description[:78] if description else "",
                },
            },
        )

        return {
            "boleto_id": data.get("codigoSolicitacao", ""),
            "barcode": data.get("codigoBarras", ""),
            "digitable_line": data.get("linhaDigitavel", ""),
            "pdf_url": data.get("pdfBoleto", ""),
            "pix_qrcode": data.get("pixCopiaECola", ""),
        }

    async def close(self) -> None:
        """Fecha conexão."""
        if self._client:
            await self._client.aclose()
            self._client = None
