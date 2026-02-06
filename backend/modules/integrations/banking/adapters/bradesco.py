"""
Adapter para integracao com Bradesco.

Implementa a API Open Banking do Bradesco para consultas
e operacoes bancarias.
"""

import base64
import hashlib
import hmac
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

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


class BradescoAdapter(BaseBankingAdapter):
    """
    Adapter para Bradesco.

    Implementa integracao com APIs Open Banking do Bradesco:
    - Consulta de saldo
    - Consulta de extrato
    - Iniciacao de pagamentos (TED, PIX, Boleto)
    - Consulta de status de pagamentos
    """

    BANK_CODE = "237"
    BANK_NAME = "Bradesco"
    API_BASE_URL_SANDBOX = "https://proxy.api.prebanco.com.br/sandbox"
    API_BASE_URL_PRODUCTION = "https://proxy.api.bradesco.com.br"

    # Endpoints Bradesco
    OAUTH_ENDPOINT = "/oauth/token"
    BALANCE_ENDPOINT = "/v1/contas/{conta}/saldo"
    STATEMENT_ENDPOINT = "/v1/contas/{conta}/extrato"
    PAYMENT_ENDPOINT = "/v1/pagamentos"
    PIX_ENDPOINT = "/v1/pix"

    # Mapeamento de tipos de transacao do Bradesco
    TRANSACTION_TYPE_MAP = {
        "C": TransactionType.CREDIT,
        "D": TransactionType.DEBIT,
        "TED": TransactionType.TED,
        "DOC": TransactionType.DOC,
        "PIX": TransactionType.PIX,
        "BOL": TransactionType.BOLETO,
        "TAR": TransactionType.TARIFA,
    }

    def __init__(self, credentials: BankCredentials) -> None:
        """Inicializa adapter Bradesco."""
        super().__init__(credentials)
        self._client: Optional[httpx.AsyncClient] = None

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
        Autentica no Bradesco usando OAuth2 Client Credentials.

        Returns:
            True se autenticado com sucesso
        """
        try:
            client = await self._get_client()

            # Bradesco usa Basic Auth para token
            auth_header = self._generate_basic_auth()

            auth_data = {
                "grant_type": "client_credentials",
                "scope": "contas pagamentos pix",
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": auth_header,
                "X-Brad-Signature": self._generate_signature(),
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
                    "Bradesco: Autenticacao realizada",
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
            logger.error("Bradesco: Erro de conexao", extra={"error": str(exc)})
            raise BankingAdapterError(
                "Erro de conexao com Bradesco",
                code="CONNECTION_ERROR",
                details={"error": str(exc)},
            ) from exc

    def _generate_basic_auth(self) -> str:
        """Gera header Basic Auth."""
        credentials = f"{self.credentials.client_id}:{self.credentials.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _generate_signature(self) -> str:
        """Gera assinatura para requisicao Bradesco."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
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
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Faz requisicao autenticada."""
        await self.ensure_authenticated()

        client = await self._get_client()

        # Substitui placeholders no endpoint
        if self.credentials.account:
            endpoint = endpoint.replace("{conta}", self.credentials.account)

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "X-Brad-Signature": self._generate_signature(),
        }

        if self.credentials.agency:
            headers["X-Agencia"] = self.credentials.agency

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
            # Bradesco usa estrutura {codigo, mensagem}
            error_code = error_data.get("codigo", str(response.status_code))
            error_msg = error_data.get("mensagem", response.text)
        except Exception:  # pylint: disable=broad-except
            error_code = str(response.status_code)
            error_msg = response.text

        if "saldo" in error_msg.lower() and "insuficiente" in error_msg.lower():
            raise InsufficientFundsError(error_msg, code=error_code)

        conta_invalida = "invalida" in error_msg.lower()
        conta_nao_existe = "nao existe" in error_msg.lower()
        if "conta" in error_msg.lower() and (conta_invalida or conta_nao_existe):
            raise InvalidAccountError(error_msg, code=error_code)

        raise BankingAdapterError(error_msg, code=error_code)

    async def get_balance(self) -> AccountBalance:
        """Consulta saldo da conta."""
        data = await self._make_request("GET", self.BALANCE_ENDPOINT)

        return AccountBalance(
            available=self._parse_amount(data.get("saldoDisponivel", 0)),
            blocked=self._parse_amount(data.get("saldoBloqueado", 0)),
            total=self._parse_amount(data.get("saldoTotal", 0)),
            currency="BRL",
            updated_at=datetime.fromisoformat(
                data.get("dataHoraConsulta", datetime.now().isoformat())
            ),
        )

    async def get_statement(
        self,
        start_date: date,
        end_date: date,
    ) -> BankStatement:
        """Consulta extrato da conta."""
        params = {
            "dataInicio": start_date.strftime("%d%m%Y"),
            "dataFim": end_date.strftime("%d%m%Y"),
            "quantidade": 100,
        }

        data = await self._make_request(
            "GET",
            self.STATEMENT_ENDPOINT,
            params=params,
        )

        transactions = []
        for lancamento in data.get("lancamentos", []):
            transactions.append(self._parse_transaction(lancamento))

        return BankStatement(
            account_agency=self.credentials.agency or "",
            account_number=self.credentials.account or "",
            account_type=AccountType.CHECKING,
            start_date=start_date,
            end_date=end_date,
            opening_balance=self._parse_amount(data.get("saldoInicial", 0)),
            closing_balance=self._parse_amount(data.get("saldoFinal", 0)),
            transactions=transactions,
            bank_code=self.BANK_CODE,
            bank_name=self.BANK_NAME,
        )

    def _parse_transaction(self, lancamento: dict) -> BankTransaction:
        """Converte transacao do formato Bradesco."""
        tipo_str = lancamento.get("tipoLancamento", "C")
        tx_type = self.TRANSACTION_TYPE_MAP.get(tipo_str, TransactionType.CREDIT)

        # Bradesco usa formato DDMMYYYY para datas
        data_str = lancamento.get("dataLancamento", "")
        if len(data_str) == 8:
            tx_date = datetime.strptime(data_str, "%d%m%Y")
        else:
            tx_date = datetime.now()

        return BankTransaction(
            transaction_id=lancamento.get("numeroDocumento", ""),
            date=tx_date,
            amount=self._parse_amount(lancamento.get("valor", 0)),
            transaction_type=tx_type,
            description=lancamento.get("descricao", ""),
            balance_after=self._parse_amount(lancamento.get("saldoApos")),
            counterpart_name=lancamento.get("nomeFavorecido"),
            counterpart_document=lancamento.get("cpfCnpjFavorecido"),
            counterpart_bank=lancamento.get("bancoFavorecido"),
            counterpart_agency=lancamento.get("agenciaFavorecido"),
            counterpart_account=lancamento.get("contaFavorecido"),
            reference=lancamento.get("numeroReferencia"),
        )

    async def initiate_payment(
        self,
        payment: PaymentRequest,
    ) -> PaymentResponse:
        """Inicia pagamento TED/DOC."""
        payload = {
            "valor": float(payment.amount),
            "favorecido": {
                "nome": payment.beneficiary_name,
                "cpfCnpj": self._format_document(payment.beneficiary_document),
                "banco": payment.beneficiary_bank,
                "agencia": payment.beneficiary_agency,
                "conta": payment.beneficiary_account,
                "tipoConta": self._map_account_type(payment.beneficiary_account_type),
            },
            "descricao": payment.description or "Transferencia",
        }

        if payment.scheduled_date:
            payload["dataAgendamento"] = payment.scheduled_date.strftime("%d%m%Y")

        data = await self._make_request("POST", self.PAYMENT_ENDPOINT, data=payload)

        return PaymentResponse(
            payment_id=data.get("codigoTransacao", ""),
            status=self._parse_payment_status(data.get("situacao", "")),
            amount=payment.amount,
            scheduled_date=payment.scheduled_date,
            authentication_code=data.get("codigoAutenticacao"),
        )

    def _map_account_type(self, account_type: AccountType) -> str:
        """Mapeia tipo de conta para formato Bradesco."""
        type_map = {
            AccountType.CHECKING: "CC",
            AccountType.SAVINGS: "PP",
            AccountType.SALARY: "CS",
            AccountType.PAYMENT: "CP",
        }
        return type_map.get(account_type, "CC")

    def _parse_payment_status(self, status: str) -> PaymentStatus:
        """Converte status do Bradesco."""
        status_map = {
            "PENDENTE": PaymentStatus.PENDING,
            "EM_PROCESSAMENTO": PaymentStatus.PROCESSING,
            "PROCESSANDO": PaymentStatus.PROCESSING,
            "EFETIVADO": PaymentStatus.COMPLETED,
            "CONCLUIDO": PaymentStatus.COMPLETED,
            "AGENDADO": PaymentStatus.SCHEDULED,
            "CANCELADO": PaymentStatus.CANCELLED,
            "REJEITADO": PaymentStatus.FAILED,
            "ERRO": PaymentStatus.FAILED,
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
        if data.get("dataAgendamento"):
            scheduled = datetime.strptime(data["dataAgendamento"], "%d%m%Y").date()

        processed = None
        if data.get("dataHoraEfetivacao"):
            processed = datetime.fromisoformat(data["dataHoraEfetivacao"])

        return PaymentResponse(
            payment_id=payment_id,
            status=self._parse_payment_status(data.get("situacao", "")),
            amount=self._parse_amount(data.get("valor", 0)),
            scheduled_date=scheduled,
            processed_at=processed,
            receipt_url=data.get("urlComprovante"),
            authentication_code=data.get("codigoAutenticacao"),
            error_message=data.get("mensagemErro"),
        )

    async def cancel_payment(
        self,
        payment_id: str,
    ) -> bool:
        """Cancela pagamento agendado."""
        endpoint = f"{self.PAYMENT_ENDPOINT}/{payment_id}/cancelar"

        try:
            data = await self._make_request("POST", endpoint)
            return data.get("cancelado", False)
        except BankingAdapterError:
            return False

    async def validate_pix_key(
        self,
        key: str,
    ) -> Optional[PixKey]:
        """Valida chave PIX."""
        endpoint = f"{self.PIX_ENDPOINT}/chaves/{key}"

        try:
            data = await self._make_request("GET", endpoint)

            return PixKey(
                key_type=data.get("tipoChave", ""),
                key_value=key,
                owner_name=data.get("nomeProprietario"),
                owner_document=data.get("cpfCnpjProprietario"),
                bank_code=data.get("codigoBanco"),
                bank_name=data.get("nomeBanco"),
                agency=data.get("agencia"),
                account=data.get("conta"),
                account_type=AccountType.CHECKING,
            )

        except BankingAdapterError:
            return None

    async def initiate_pix(
        self,
        pix_key: str,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> PaymentResponse:
        """Inicia transferencia PIX."""
        # Valida a chave antes
        pix_info = await self.validate_pix_key(pix_key)
        if not pix_info:
            raise BankingAdapterError(
                "Chave PIX invalida ou nao encontrada",
                code="INVALID_PIX_KEY",
            )

        payload = {
            "chavePix": pix_key,
            "valor": float(amount),
            "descricao": description or "Transferencia PIX",
        }

        data = await self._make_request(
            "POST",
            f"{self.PIX_ENDPOINT}/transferencias",
            data=payload,
        )

        return PaymentResponse(
            payment_id=data.get("endToEndId", ""),
            status=self._parse_payment_status(data.get("situacao", "")),
            amount=amount,
            processed_at=(datetime.now() if data.get("situacao") == "EFETIVADO" else None),
            authentication_code=data.get("endToEndId"),
        )

    async def close(self) -> None:
        """Fecha cliente HTTP."""
        if self._client:
            await self._client.aclose()
            self._client = None
