"""
Adapter Banco Inter - Open Banking.

Documentação: https://developers.inter.co/
API: https://cdpj.partners.bancointer.com.br/

Autenticação: OAuth2 + mTLS (certificado digital)
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
        "saldo": "extrato.read",
        "pix": "pix.write pix.read",
        "cob": "cob.write cob.read",
        "boleto": "boleto-cobranca.write boleto-cobranca.read",
        "pagamento": "pagamento-boleto.write pagamento-boleto.read",
        "ted": "pagamento-ted.write pagamento-ted.read",
    }

    def __init__(self, credentials: BankCredentials) -> None:
        """Inicializa adapter Inter."""
        super().__init__(credentials)
        self._client: httpx.AsyncClient | None = None

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
            scopes = " ".join(
                [
                    self.SCOPES["extrato"],
                    self.SCOPES["saldo"],
                    self.SCOPES["pix"],
                    self.SCOPES.get("cob", "cob.write cob.read"),
                    self.SCOPES["boleto"],
                    self.SCOPES["pagamento"],
                    self.SCOPES.get("ted", "pagamento-ted.write pagamento-ted.read"),
                ]
            )

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

            transactions.append(
                BankTransaction(
                    transaction_id=item.get("idTransacao", ""),
                    date=datetime.fromisoformat(item.get("dataEntrada", "")),
                    amount=self._parse_amount(item.get("valor", 0)),
                    transaction_type=tx_type,
                    description=item.get("descricao", ""),
                    balance_after=self._parse_amount(item.get("saldo", 0)) if item.get("saldo") else None,
                )
            )

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
    ) -> PixKey | None:
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
        description: str | None = None,
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
        payer_address: str | None = None,
        payer_number: str | None = None,
        payer_neighborhood: str | None = None,
        payer_city: str | None = None,
        payer_state: str | None = None,
        payer_zip: str | None = None,
    ) -> dict:
        """Gera boleto de cobrança."""
        clean_doc = self._format_document(payer_document)
        tipo_pessoa = "FISICA" if len(clean_doc) == 11 else "JURIDICA"

        data = await self._request(
            "POST",
            "/cobranca/v3/cobrancas",
            json={
                "seuNumero": f"C{datetime.now().strftime('%y%m%d%H%M%S')}",
                "valorNominal": float(amount),
                "dataVencimento": due_date.strftime("%Y-%m-%d"),
                "numDiasAgenda": 30,
                "pagador": {
                    "tipoPessoa": tipo_pessoa,
                    "nome": payer_name,
                    "cpfCnpj": clean_doc,
                    "endereco": payer_address or "Endereço não informado",
                    "numero": payer_number or "S/N",
                    "bairro": payer_neighborhood or "Centro",
                    "cidade": payer_city or "Manaus",
                    "uf": payer_state or "AM",
                    "cep": (payer_zip or "69000000").replace("-", ""),
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

    async def generate_pix_charge(
        self,
        amount: Decimal,
        description: str,
        chave_pix: str = "35710481000103",
        payer_name: str | None = None,
        payer_document: str | None = None,
        expiracao_segundos: int = 86400,
    ) -> dict:
        """Gera cobrança PIX imediata (cob) via Banco Inter."""
        import random
        import string

        # txid: alfanumérico, 26-35 chars (BACEN PIX spec)
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))  # noqa: S311
        txid = f"CON{datetime.now().strftime('%Y%m%d%H%M%S')}{suffix}"

        body: dict = {
            "calendario": {"expiracao": expiracao_segundos},
            "valor": {"original": f"{float(amount):.2f}"},
            "chave": chave_pix,
            "solicitacaoPagador": description[:140] if description else "Cobrança Conecta Mais",
        }
        if payer_name:
            body["devedor"] = {"nome": payer_name}
            if payer_document:
                cpf_cnpj = payer_document.replace(".", "").replace("-", "").replace("/", "")
                if len(cpf_cnpj) == 11:
                    body["devedor"]["cpf"] = cpf_cnpj
                else:
                    body["devedor"]["cnpj"] = cpf_cnpj

        data = await self._request("PUT", f"/pix/v2/cob/{txid}", json=body)

        return {
            "charge_id": data.get("txid", txid),
            "pix_copy_paste": data.get("pixCopiaECola", ""),
            "pix_qrcode": data.get("location", ""),
            "amount": float(amount),
        }

    async def get_boleto(self, boleto_id: str) -> dict:
        """
        Consulta boleto individual — retorna barcode e PDF URL.
        GET /cobranca/v3/cobrancas/{codigoSolicitacao}
        Resposta Inter: {"cobranca": {...}, "boleto": {"codigoBarras": ...}, "pix": {...}}
        """
        try:
            data = await self._request("GET", f"/cobranca/v3/cobrancas/{boleto_id}")
            cobranca = data.get("cobranca", data)
            boleto = data.get("boleto", {})
            pix = data.get("pix", {})
            return {
                "success": True,
                "boleto_id": boleto_id,
                "barcode": boleto.get("codigoBarras", ""),
                "linha_digitavel": boleto.get("linhaDigitavel", ""),
                "nosso_numero": boleto.get("nossoNumero", ""),
                "pdf_url": cobranca.get("linkBoleto", ""),
                "status": cobranca.get("situacao", ""),
                "valor": cobranca.get("valorNominal", 0),
                "vencimento": cobranca.get("dataVencimento", ""),
                "payer": cobranca.get("pagador", {}),
                "pix_copy_paste": pix.get("pixCopiaECola", ""),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def cancel_boleto(self, boleto_id: str, motivo: str = "ACERTOS") -> dict:
        """
        Cancela boleto emitido.
        DELETE /cobranca/v3/cobrancas/{id}/cancelar
        motivo: ACERTOS | APEDIDODOCLIENTE | PAGODIRETOAOCLIENTE  # pragma: allowlist secret
        """
        try:
            await self._request(
                "DELETE",
                f"/cobranca/v3/cobrancas/{boleto_id}/cancelar",
                json={"motivoCancelamento": motivo},
            )
            return {"success": True, "boleto_id": boleto_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def initiate_ted(
        self,
        valor: float,
        banco: str,
        agencia: str,
        conta: str,
        tipo_conta: str,
        cpf_cnpj: str,
        nome: str,
        descricao: str = "",
    ) -> dict:
        """
        Realiza transferência TED.
        POST /banking/v2/transferencia
        tipo_conta: CORRENTE | POUPANCA | PAGAMENTO
        """
        try:
            clean_doc = "".join(c for c in cpf_cnpj if c.isdigit())
            payload = {
                "valor": valor,
                "descricao": descricao or f"TED para {nome}",
                "destinatario": {
                    "cpfCnpj": clean_doc,
                    "nome": nome,
                    "banco": banco,
                    "agencia": agencia,
                    "conta": conta,
                    "tipoConta": tipo_conta,
                },
            }
            data = await self._request("POST", "/banking/v2/transferencia", json=payload)
            return {
                "success": True,
                "transfer_id": data.get("codigoTransferencia", ""),
                "valor": valor,
                "destinatario": nome,
                "status": data.get("status", "processando"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_pix_received(
        self,
        data_inicio: str | None = None,
        data_fim: str | None = None,
    ) -> dict:
        """
        Consulta PIX recebidos.
        GET /pix/v2/pix?inicio=...&fim=...
        """
        from datetime import datetime, timedelta

        if not data_inicio:
            data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00.000Z")
        if not data_fim:
            data_fim = datetime.now().strftime("%Y-%m-%dT23:59:59.999Z")

        try:
            data = await self._request(
                "GET",
                "/pix/v2/pix",
                params={"inicio": data_inicio, "fim": data_fim},
            )
            pix_list = data.get("pix", [])
            return {
                "success": True,
                "total": len(pix_list),
                "pix": pix_list,
                "parametros": data.get("parametros", {}),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def request_pix_refund(
        self,
        e2e_id: str,
        refund_id: str,
        valor: float,
        motivo: str = "Devolucao solicitada",
    ) -> dict:
        """
        Solicita devolução de PIX recebido.
        PUT /pix/v2/pix/{e2eId}/devolucao/{id}
        """
        try:
            data = await self._request(
                "PUT",
                f"/pix/v2/pix/{e2e_id}/devolucao/{refund_id}",
                json={"valor": str(valor), "natureza": "ORIGINAL", "descricao": motivo},
            )
            return {
                "success": True,
                "e2e_id": e2e_id,
                "refund_id": refund_id,
                "valor": valor,
                "status": data.get("status", ""),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def pay_darf(
        self,
        cnpj_cpf: str,
        periodo_apuracao: str,
        numero_referencia: str,
        valor_principal: float,
        valor_multa: float = 0,
        valor_juros: float = 0,
        codigo_receita: str = "6015",
        data_vencimento: str | None = None,
        descricao: str = "Pagamento DARF",
    ) -> dict:
        """
        Paga DARF via API Inter.
        POST /banking/v2/darf
        codigo_receita: 6015=IRPJ, 2372=CSLL, 0561=COFINS,
                        8109=PIS, 2100=INSS, 0561=ISS
        periodo_apuracao: YYYY-MM (ex: 2026-03)
        """
        if not data_vencimento:
            data_vencimento = datetime.now().strftime("%Y-%m-%d")
        try:
            payload = {
                "cnpjCpf": "".join(c for c in cnpj_cpf if c.isdigit()),
                "codigoReceita": codigo_receita,
                "periodoApuracao": periodo_apuracao,
                "numeroReferencia": numero_referencia,
                "valorPrincipal": valor_principal,
                "valorMulta": valor_multa,
                "valorJuros": valor_juros,
                "dataVencimento": data_vencimento,
                "descricao": descricao,
            }
            data = await self._request("POST", "/banking/v2/darf", json=payload)
            return {
                "success": True,
                "payment_id": data.get("codigoPagamento", ""),
                "codigo_receita": codigo_receita,
                "valor_total": valor_principal + valor_multa + valor_juros,
                "data_vencimento": data_vencimento,
                "status": data.get("status", "processando"),
            }
        except BankingAdapterError as e:
            return {"success": False, "status_code": e.code, "detail": str(e)}
        except Exception as e:
            return {"error": str(e)}

    async def pay_barcode(
        self,
        codigo_barras: str,
        valor: float | None = None,
        data_pagamento: str | None = None,
        descricao: str = "",
    ) -> dict:
        """
        Paga boleto, convênio ou tributo por código de barras.
        POST /banking/v2/pagamento
        Suporta: boletos bancários, DARF simplificado,
                 contas de água/luz/telefone
        """
        if not data_pagamento:
            data_pagamento = datetime.now().strftime("%Y-%m-%d")
        try:
            payload: dict = {
                "codigoBarras": "".join(c for c in codigo_barras if c.isdigit()),
                "dataPagamento": data_pagamento,
                "descricao": descricao or "Pagamento via Conecta PRO",
            }
            if valor:
                payload["valor"] = valor
            data = await self._request("POST", "/banking/v2/pagamento", json=payload)
            return {
                "success": True,
                "payment_id": data.get("codigoPagamento", data.get("idPagamento", "")),
                "valor": valor,
                "data_pagamento": data_pagamento,
                "status": data.get("status", "processando"),
                "autenticacao": data.get("autenticacao", ""),
            }
        except BankingAdapterError as e:
            return {"success": False, "status_code": e.code, "detail": str(e)}
        except Exception as e:
            return {"error": str(e)}

    async def pay_batch(self, pagamentos: list) -> dict:
        """
        Realiza múltiplos pagamentos em lote.
        POST /banking/v2/pagamento/lote

        pagamentos: lista de dicts com:
          - codigo_barras: str
          - valor: float
          - data_pagamento: str (YYYY-MM-DD)
          - descricao: str
          - meu_identificador: str (ID interno)
        """
        hoje = datetime.now().strftime("%Y-%m-%d")
        lote = []
        for i, pag in enumerate(pagamentos):
            item: dict = {
                "codigoBarras": "".join(c for c in pag.get("codigo_barras", "") if c.isdigit()),
                "dataPagamento": pag.get("data_pagamento", hoje),
                "descricao": pag.get("descricao", f"Pagamento lote #{i + 1}"),
                "meuIdentificador": pag.get("meu_identificador", f"CONECTA-{i + 1:04d}"),
            }
            if pag.get("valor"):
                item["valor"] = pag["valor"]
            lote.append(item)
        try:
            data = await self._request("POST", "/banking/v2/pagamento/lote", json={"pagamentos": lote})
            return {
                "success": True,
                "lote_id": data.get("idLote", ""),
                "total_itens": len(lote),
                "status": data.get("status", "processando"),
                "detalhes": data.get("pagamentos", []),
            }
        except BankingAdapterError as e:
            return {"success": False, "status_code": e.code, "detail": str(e)}
        except Exception as e:
            return {"error": str(e)}

    async def get_payment_list(
        self,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        tipo: str | None = None,
    ) -> dict:
        """
        Consulta pagamentos realizados por período.
        GET /banking/v2/pagamento?dataInicio=...&dataFim=...
        tipo: BOLETO | PIX | TED | DARF
        """
        if not data_inicio:
            data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = datetime.now().strftime("%Y-%m-%d")
        params: dict = {"dataInicio": data_inicio, "dataFim": data_fim}
        if tipo:
            params["tipoPagamento"] = tipo
        try:
            data = await self._request("GET", "/banking/v2/pagamento", params=params)
            if isinstance(data, list):
                pagamentos = data
            else:
                pagamentos = data.get("pagamentos", [])
            return {"success": True, "total": len(pagamentos), "pagamentos": pagamentos}
        except BankingAdapterError as e:
            return {"success": False, "status_code": e.code, "detail": str(e)}
        except Exception as e:
            return {"error": str(e)}

    async def create_pix_cobv(
        self,
        txid: str,
        valor: float,
        cpf_cnpj: str,
        nome: str,
        descricao: str,
        vencimento: str,
        chave_pix: str = "35710481000103",
        juros_pct: float = 1.0,
        multa_pct: float = 2.0,
    ) -> dict:
        """
        Cria cobrança PIX com vencimento (cobv).
        PUT /pix/v2/cobv/{txid}
        vencimento: "YYYY-MM-DD"
        """
        doc = "".join(c for c in cpf_cnpj if c.isdigit())
        devedor: dict = {"nome": nome}
        if len(doc) == 11:
            devedor["cpf"] = doc
        else:
            devedor["cnpj"] = doc

        body = {
            "calendario": {
                "dataDeVencimento": vencimento,
                "validadeAposVencimento": 30,
            },
            "devedor": devedor,
            "valor": {
                "original": f"{valor:.2f}",
                "multa": {"modalidade": 2, "valorPerc": f"{multa_pct:.2f}"},
                "juros": {"modalidade": 2, "valorPerc": f"{juros_pct:.2f}"},
            },
            "chave": chave_pix,
            "solicitacaoPagador": descricao[:140],
        }

        try:
            data = await self._request("PUT", f"/pix/v2/cobv/{txid}", json=body)
            return {
                "success": True,
                "txid": data.get("txid", txid),
                "pix_copy_paste": data.get("pixCopiaECola", ""),
                "location": data.get("location", ""),
                "status": data.get("status", "ATIVA"),
                "valor": valor,
                "vencimento": vencimento,
                "devedor": nome,
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def list_cobv(
        self,
        inicio: str | None = None,
        fim: str | None = None,
        status: str | None = None,
        pagina: int = 0,
    ) -> dict:
        """
        Lista cobranças PIX com vencimento.
        GET /pix/v2/cobv
        status: ATIVA | CONCLUIDA | REMOVIDA_PELO_USUARIO_RECEBEDOR
        """
        if not inicio:
            inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00Z")
        if not fim:
            fim = datetime.now().strftime("%Y-%m-%dT23:59:59Z")

        params: dict = {"inicio": inicio, "fim": fim, "paginaAtual": pagina}
        if status:
            params["status"] = status

        try:
            data = await self._request("GET", "/pix/v2/cobv", params=params)
            cobs = data.get("cobs", [])
            return {
                "success": True,
                "total": len(cobs),
                "cobs": cobs,
                "parametros": data.get("parametros", {}),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def register_pix_webhook(self, webhook_url: str) -> dict:
        """
        Registra webhook para notificações PIX recebidos.
        PUT /pix/v2/webhook/{chave}
        """
        import os as _os

        pix_key = _os.getenv("INTER_PIX_KEY", "35710481000103")
        try:
            await self._request(
                "PUT",
                f"/pix/v2/webhook/{pix_key}",
                json={"webhookUrl": webhook_url},
            )
            return {
                "success": True,
                "chave": pix_key,
                "webhook_url": webhook_url,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_pix_webhook(self) -> dict:
        """Consulta webhook PIX configurado."""
        import os as _os

        pix_key = _os.getenv("INTER_PIX_KEY", "35710481000103")
        try:
            data = await self._request("GET", f"/pix/v2/webhook/{pix_key}")
            return {"success": True, "chave": pix_key, **data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def register_boleto_webhook(self, webhook_url: str) -> dict:
        """
        Registra webhook para notificações de boleto pago.
        POST /cobranca/v3/cobrancas/webhook
        """
        try:
            await self._request(
                "POST",
                "/cobranca/v3/cobrancas/webhook",
                json={"webhookUrl": webhook_url},
            )
            return {"success": True, "webhook_url": webhook_url}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close(self) -> None:
        """Fecha conexão."""
        if self._client:
            await self._client.aclose()
            self._client = None
