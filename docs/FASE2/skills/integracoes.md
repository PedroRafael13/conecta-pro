# SKILL: INTEGRACOES
## ERP CONECTA MAIS - FASE 2

**Modulo:** Integracoes
**Sprints:** 26 (Open Banking), 31-32 (WhatsApp/Email)
**Prioridade:** ALTA

---

## CONTEXTO DO MODULO

Integracoes com sistemas externos:
- Open Banking (BB, Itau, Bradesco, Santander)
- WhatsApp Business API
- Email (SMTP, Templates)
- eSocial / SPED
- DocuSign / Clicksign
- NFSe (Prefeituras)
- Gateways de Pagamento

---

## ESTRUTURA DO MODULO

```
modules/integrations/
├── __init__.py
├── banking/
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── banco_brasil.py
│   │   ├── itau.py
│   │   ├── bradesco.py
│   │   └── santander.py
│   └── services/
│       ├── __init__.py
│       └── banking_service.py
├── messaging/
│   ├── __init__.py
│   ├── whatsapp/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── templates.py
│   └── email/
│       ├── __init__.py
│       ├── client.py
│       └── templates.py
├── government/
│   ├── __init__.py
│   ├── esocial/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── events.py
│   ├── sped/
│   │   └── ...
│   └── nfse/
│       └── ...
├── signature/
│   ├── __init__.py
│   ├── docusign.py
│   └── clicksign.py
└── payment/
    ├── __init__.py
    ├── pix.py
    └── boleto.py
```

---

## OPEN BANKING

### Adapter Base

```python
# modules/integrations/banking/adapters/base.py
"""Adapter base para bancos."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


@dataclass
class BankBalance:
    """Saldo bancario."""
    available: Decimal
    blocked: Decimal
    total: Decimal
    updated_at: datetime


@dataclass
class BankTransaction:
    """Transacao bancaria."""
    id: str
    date: datetime
    description: str
    value: Decimal
    type: str  # CREDIT, DEBIT
    balance_after: Decimal
    category: Optional[str] = None
    document: Optional[str] = None


@dataclass
class PaymentResult:
    """Resultado de pagamento."""
    id: str
    status: str  # PENDING, PROCESSED, FAILED
    confirmation_code: Optional[str] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class BankAdapter(ABC):
    """Interface para adapters de banco."""

    @abstractmethod
    async def authenticate(self) -> str:
        """Autentica na API do banco."""
        pass

    @abstractmethod
    async def get_balance(self, account_id: str) -> BankBalance:
        """Obtem saldo da conta."""
        pass

    @abstractmethod
    async def get_statement(
        self,
        account_id: str,
        start_date: date,
        end_date: date
    ) -> list[BankTransaction]:
        """Obtem extrato."""
        pass

    @abstractmethod
    async def initiate_pix(
        self,
        from_account: str,
        to_key: str,
        value: Decimal,
        description: str
    ) -> PaymentResult:
        """Inicia transferencia PIX."""
        pass

    @abstractmethod
    async def initiate_ted(
        self,
        from_account: str,
        to_bank: str,
        to_agency: str,
        to_account: str,
        to_document: str,
        value: Decimal,
        description: str
    ) -> PaymentResult:
        """Inicia transferencia TED."""
        pass

    @abstractmethod
    async def pay_boleto(
        self,
        from_account: str,
        barcode: str,
        value: Decimal,
        payment_date: date
    ) -> PaymentResult:
        """Paga boleto."""
        pass

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """Consulta status de pagamento."""
        pass
```

### Adapter Banco do Brasil

```python
# modules/integrations/banking/adapters/banco_brasil.py
"""Adapter para Banco do Brasil."""

import httpx
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from core.logging import logger
from core.config import settings
from .base import BankAdapter, BankBalance, BankTransaction, PaymentResult


class BancoBrasilAdapter(BankAdapter):
    """
    Adapter para API do Banco do Brasil.

    Implementa Open Banking para consultas
    e pagamentos via API BB.
    """

    BASE_URL = "https://api.bb.com.br"
    SANDBOX_URL = "https://api.sandbox.bb.com.br"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        sandbox: bool = False
    ) -> None:
        """
        Inicializa adapter.

        Args:
            client_id: Client ID do app
            client_secret: Client Secret
            sandbox: Se True, usa ambiente sandbox
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = self.SANDBOX_URL if sandbox else self.BASE_URL
        self.token: Optional[str] = None
        self.token_expires: Optional[datetime] = None

    async def authenticate(self) -> str:
        """Autentica via OAuth2."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": "cob.read cob.write pix.read pix.write"
                },
                auth=(self.client_id, self.client_secret)
            )

            if response.status_code != 200:
                logger.error(
                    "Falha na autenticacao BB",
                    extra={"status": response.status_code}
                )
                raise Exception("Falha na autenticacao")

            data = response.json()
            self.token = data["access_token"]
            self.token_expires = datetime.now() + timedelta(
                seconds=data["expires_in"]
            )

            return self.token

    async def _ensure_authenticated(self) -> None:
        """Garante que esta autenticado."""
        if not self.token or datetime.now() >= self.token_expires:
            await self.authenticate()

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict:
        """Faz request autenticado."""
        await self._ensure_authenticated()

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.token}"},
                **kwargs
            )

            if response.status_code >= 400:
                logger.error(
                    "Erro na API BB",
                    extra={
                        "path": path,
                        "status": response.status_code,
                        "body": response.text
                    }
                )
                raise Exception(f"Erro BB: {response.status_code}")

            return response.json()

    async def get_balance(self, account_id: str) -> BankBalance:
        """Obtem saldo."""
        data = await self._request("GET", f"/contas/{account_id}/saldo")

        return BankBalance(
            available=Decimal(str(data["saldoDisponivel"])),
            blocked=Decimal(str(data.get("saldoBloqueado", 0))),
            total=Decimal(str(data["saldoTotal"])),
            updated_at=datetime.now()
        )

    async def get_statement(
        self,
        account_id: str,
        start_date: date,
        end_date: date
    ) -> list[BankTransaction]:
        """Obtem extrato."""
        data = await self._request(
            "GET",
            f"/contas/{account_id}/extrato",
            params={
                "dataInicio": start_date.isoformat(),
                "dataFim": end_date.isoformat()
            }
        )

        transactions = []
        for t in data.get("lancamentos", []):
            transactions.append(BankTransaction(
                id=t["id"],
                date=datetime.fromisoformat(t["data"]),
                description=t["descricao"],
                value=Decimal(str(t["valor"])),
                type="CREDIT" if t["valor"] > 0 else "DEBIT",
                balance_after=Decimal(str(t.get("saldoApos", 0))),
                document=t.get("documento")
            ))

        return transactions

    async def initiate_pix(
        self,
        from_account: str,
        to_key: str,
        value: Decimal,
        description: str
    ) -> PaymentResult:
        """Inicia PIX."""
        data = await self._request(
            "POST",
            "/pix/pagamentos",
            json={
                "contaOrigem": from_account,
                "chaveDestinatario": to_key,
                "valor": str(value),
                "descricao": description
            }
        )

        logger.info(
            "PIX iniciado",
            extra={
                "from": from_account,
                "to": to_key,
                "value": str(value),
                "id": data["id"]
            }
        )

        return PaymentResult(
            id=data["id"],
            status=data["status"],
            confirmation_code=data.get("endToEndId")
        )

    async def initiate_ted(
        self,
        from_account: str,
        to_bank: str,
        to_agency: str,
        to_account: str,
        to_document: str,
        value: Decimal,
        description: str
    ) -> PaymentResult:
        """Inicia TED."""
        data = await self._request(
            "POST",
            "/transferencias/ted",
            json={
                "contaDebito": from_account,
                "bancoCredito": to_bank,
                "agenciaCredito": to_agency,
                "contaCredito": to_account,
                "cpfCnpjCredito": to_document,
                "valor": str(value),
                "descricao": description
            }
        )

        return PaymentResult(
            id=data["id"],
            status=data["status"]
        )

    async def pay_boleto(
        self,
        from_account: str,
        barcode: str,
        value: Decimal,
        payment_date: date
    ) -> PaymentResult:
        """Paga boleto."""
        data = await self._request(
            "POST",
            "/boletos/pagamentos",
            json={
                "contaDebito": from_account,
                "codigoBarras": barcode,
                "valor": str(value),
                "dataPagamento": payment_date.isoformat()
            }
        )

        return PaymentResult(
            id=data["id"],
            status=data["status"]
        )

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """Consulta status."""
        data = await self._request("GET", f"/pagamentos/{payment_id}")

        return PaymentResult(
            id=data["id"],
            status=data["status"],
            confirmation_code=data.get("comprovante"),
            processed_at=datetime.fromisoformat(data["dataProcessamento"])
            if data.get("dataProcessamento") else None,
            error_message=data.get("mensagemErro")
        )
```

---

## WHATSAPP BUSINESS API

### WhatsApp Client

```python
# modules/integrations/messaging/whatsapp/client.py
"""Cliente WhatsApp Business API."""

import httpx
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.logging import logger
from core.config import settings


@dataclass
class MessageResult:
    """Resultado de envio de mensagem."""
    message_id: str
    status: str
    sent_at: datetime
    error: Optional[str] = None


@dataclass
class TemplateMessage:
    """Mensagem com template."""
    template_name: str
    language: str = "pt_BR"
    components: list = None


class WhatsAppClient:
    """
    Cliente para WhatsApp Business API.

    Envia mensagens via API oficial do WhatsApp.
    """

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(
        self,
        phone_number_id: str,
        access_token: str
    ) -> None:
        """
        Inicializa cliente.

        Args:
            phone_number_id: ID do numero no WhatsApp Business
            access_token: Token de acesso
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token

    async def send_template(
        self,
        to: str,
        template: TemplateMessage
    ) -> MessageResult:
        """
        Envia mensagem com template.

        Args:
            to: Numero de destino (com DDI)
            template: Template a enviar

        Returns:
            Resultado do envio
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template.template_name,
                "language": {"code": template.language}
            }
        }

        if template.components:
            payload["template"]["components"] = template.components

        return await self._send(payload)

    async def send_text(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> MessageResult:
        """
        Envia mensagem de texto.

        Args:
            to: Numero de destino
            text: Texto da mensagem
            preview_url: Se deve mostrar preview de URL

        Returns:
            Resultado do envio
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": text,
                "preview_url": preview_url
            }
        }

        return await self._send(payload)

    async def send_document(
        self,
        to: str,
        document_url: str,
        filename: str,
        caption: Optional[str] = None
    ) -> MessageResult:
        """
        Envia documento.

        Args:
            to: Numero de destino
            document_url: URL do documento
            filename: Nome do arquivo
            caption: Legenda opcional

        Returns:
            Resultado do envio
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": filename
            }
        }

        if caption:
            payload["document"]["caption"] = caption

        return await self._send(payload)

    async def send_interactive_buttons(
        self,
        to: str,
        body: str,
        buttons: list[dict]
    ) -> MessageResult:
        """
        Envia mensagem interativa com botoes.

        Args:
            to: Numero de destino
            body: Texto da mensagem
            buttons: Lista de botoes [{id, title}]

        Returns:
            Resultado do envio
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": b["id"], "title": b["title"]}
                        }
                        for b in buttons[:3]  # Max 3 botoes
                    ]
                }
            }
        }

        return await self._send(payload)

    async def _send(self, payload: dict) -> MessageResult:
        """Envia mensagem para API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/{self.phone_number_id}/messages",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code != 200:
                logger.error(
                    "Erro ao enviar WhatsApp",
                    extra={
                        "status": response.status_code,
                        "body": response.text
                    }
                )
                return MessageResult(
                    message_id="",
                    status="FAILED",
                    sent_at=datetime.now(),
                    error=response.text
                )

            data = response.json()
            message_id = data["messages"][0]["id"]

            logger.info(
                "WhatsApp enviado",
                extra={
                    "to": payload["to"],
                    "message_id": message_id
                }
            )

            return MessageResult(
                message_id=message_id,
                status="SENT",
                sent_at=datetime.now()
            )


# Templates pre-definidos
class WhatsAppTemplates:
    """Templates de mensagens."""

    @staticmethod
    def cobranca_lembrete(
        cliente_nome: str,
        valor: str,
        vencimento: str,
        boleto_url: str
    ) -> TemplateMessage:
        """Template de lembrete de cobranca."""
        return TemplateMessage(
            template_name="cobranca_lembrete",
            components=[
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": cliente_nome},
                        {"type": "text", "text": valor},
                        {"type": "text", "text": vencimento}
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {"type": "text", "text": boleto_url}
                    ]
                }
            ]
        )

    @staticmethod
    def confirmacao_pagamento(
        cliente_nome: str,
        valor: str,
        data: str
    ) -> TemplateMessage:
        """Template de confirmacao de pagamento."""
        return TemplateMessage(
            template_name="confirmacao_pagamento",
            components=[
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": cliente_nome},
                        {"type": "text", "text": valor},
                        {"type": "text", "text": data}
                    ]
                }
            ]
        )
```

---

## ASSINATURA DIGITAL

### DocuSign Adapter

```python
# modules/integrations/signature/docusign.py
"""Integracao DocuSign."""

import httpx
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.logging import logger


@dataclass
class SignatureRequest:
    """Solicitacao de assinatura."""
    envelope_id: str
    status: str
    signing_url: Optional[str] = None
    created_at: datetime = None


@dataclass
class Signer:
    """Assinante do documento."""
    email: str
    name: str
    role: str = "signer"
    order: int = 1


class DocuSignClient:
    """
    Cliente DocuSign.

    Gerencia envio de documentos para
    assinatura digital.
    """

    def __init__(
        self,
        integration_key: str,
        user_id: str,
        account_id: str,
        private_key: str,
        sandbox: bool = False
    ) -> None:
        """Inicializa cliente."""
        self.integration_key = integration_key
        self.user_id = user_id
        self.account_id = account_id
        self.private_key = private_key
        self.base_url = (
            "https://demo.docusign.net/restapi"
            if sandbox else
            "https://na4.docusign.net/restapi"
        )
        self.token: Optional[str] = None

    async def authenticate(self) -> str:
        """Autentica via JWT."""
        # Implementar autenticacao JWT
        pass

    async def send_for_signature(
        self,
        document: bytes,
        document_name: str,
        signers: list[Signer],
        email_subject: str,
        email_body: Optional[str] = None
    ) -> SignatureRequest:
        """
        Envia documento para assinatura.

        Args:
            document: Conteudo do documento (PDF)
            document_name: Nome do documento
            signers: Lista de assinantes
            email_subject: Assunto do email
            email_body: Corpo do email

        Returns:
            Dados do envelope criado
        """
        import base64

        # Criar envelope
        envelope = {
            "emailSubject": email_subject,
            "documents": [
                {
                    "documentBase64": base64.b64encode(document).decode(),
                    "name": document_name,
                    "fileExtension": "pdf",
                    "documentId": "1"
                }
            ],
            "recipients": {
                "signers": [
                    {
                        "email": s.email,
                        "name": s.name,
                        "recipientId": str(i + 1),
                        "routingOrder": str(s.order),
                        "tabs": {
                            "signHereTabs": [
                                {
                                    "documentId": "1",
                                    "pageNumber": "1",
                                    "xPosition": "100",
                                    "yPosition": "700"
                                }
                            ]
                        }
                    }
                    for i, s in enumerate(signers)
                ]
            },
            "status": "sent"
        }

        if email_body:
            envelope["emailBlurb"] = email_body

        # Enviar para DocuSign
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2.1/accounts/{self.account_id}/envelopes",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json=envelope
            )

            if response.status_code not in (200, 201):
                logger.error(
                    "Erro ao criar envelope DocuSign",
                    extra={"status": response.status_code}
                )
                raise Exception("Falha ao criar envelope")

            data = response.json()

        logger.info(
            "Documento enviado para assinatura",
            extra={
                "envelope_id": data["envelopeId"],
                "signers": len(signers)
            }
        )

        return SignatureRequest(
            envelope_id=data["envelopeId"],
            status=data["status"],
            created_at=datetime.now()
        )

    async def get_signing_url(
        self,
        envelope_id: str,
        signer: Signer,
        return_url: str
    ) -> str:
        """
        Obtem URL de assinatura embedded.

        Args:
            envelope_id: ID do envelope
            signer: Dados do assinante
            return_url: URL de retorno apos assinatura

        Returns:
            URL para assinatura
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2.1/accounts/{self.account_id}"
                f"/envelopes/{envelope_id}/views/recipient",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                json={
                    "email": signer.email,
                    "userName": signer.name,
                    "returnUrl": return_url,
                    "authenticationMethod": "email"
                }
            )

            data = response.json()
            return data["url"]

    async def get_envelope_status(self, envelope_id: str) -> dict:
        """Consulta status do envelope."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2.1/accounts/{self.account_id}"
                f"/envelopes/{envelope_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            return response.json()

    async def download_signed_document(
        self,
        envelope_id: str
    ) -> bytes:
        """Baixa documento assinado."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2.1/accounts/{self.account_id}"
                f"/envelopes/{envelope_id}/documents/combined",
                headers={"Authorization": f"Bearer {self.token}"}
            )

            return response.content
```

---

## NFSE

### NFSe Client

```python
# modules/integrations/government/nfse/client.py
"""Cliente para emissao de NFSe."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.logging import logger


@dataclass
class NFSeData:
    """Dados da NFSe."""
    numero: str
    codigo_verificacao: str
    data_emissao: datetime
    valor: Decimal
    pdf_url: str
    xml_url: str


@dataclass
class ServiceData:
    """Dados do servico."""
    descricao: str
    valor: Decimal
    codigo_servico: str
    aliquota_iss: Decimal
    valor_iss: Decimal


class NFSeClient:
    """
    Cliente para emissao de NFSe.

    Integra com prefeituras para emissao
    de Nota Fiscal de Servicos.
    """

    # Mapeamento de prefeituras e suas APIs
    PREFEITURAS = {
        "sao_paulo": {
            "url": "https://nfe.prefeitura.sp.gov.br",
            "adapter": "ginfes"
        },
        "rio_de_janeiro": {
            "url": "https://notacarioca.rio.gov.br",
            "adapter": "abrasf"
        },
        "belo_horizonte": {
            "url": "https://bhissdigital.pbh.gov.br",
            "adapter": "belosoft"
        }
    }

    def __init__(
        self,
        municipio: str,
        cnpj: str,
        inscricao_municipal: str,
        certificado_path: str,
        certificado_senha: str
    ) -> None:
        """Inicializa cliente."""
        self.municipio = municipio
        self.cnpj = cnpj
        self.inscricao_municipal = inscricao_municipal
        self.certificado_path = certificado_path
        self.certificado_senha = certificado_senha

        config = self.PREFEITURAS.get(municipio)
        if not config:
            raise ValueError(f"Municipio {municipio} nao suportado")

        self.base_url = config["url"]
        self.adapter = config["adapter"]

    async def emitir(
        self,
        tomador_cnpj: str,
        tomador_razao_social: str,
        tomador_endereco: dict,
        servicos: list[ServiceData],
        competencia: datetime,
        numero_rps: int
    ) -> NFSeData:
        """
        Emite NFSe.

        Args:
            tomador_cnpj: CNPJ do tomador
            tomador_razao_social: Razao social do tomador
            tomador_endereco: Endereco do tomador
            servicos: Lista de servicos
            competencia: Competencia (mes/ano)
            numero_rps: Numero do RPS

        Returns:
            Dados da NFSe emitida
        """
        # Montar RPS
        rps = self._montar_rps(
            tomador_cnpj=tomador_cnpj,
            tomador_razao_social=tomador_razao_social,
            tomador_endereco=tomador_endereco,
            servicos=servicos,
            competencia=competencia,
            numero_rps=numero_rps
        )

        # Assinar XML
        xml_assinado = self._assinar_xml(rps)

        # Enviar para prefeitura
        response = await self._enviar(xml_assinado)

        # Processar resposta
        nfse = self._processar_resposta(response)

        logger.info(
            "NFSe emitida",
            extra={
                "numero": nfse.numero,
                "valor": str(nfse.valor)
            }
        )

        return nfse

    async def consultar(self, numero: str) -> Optional[NFSeData]:
        """Consulta NFSe por numero."""
        pass

    async def cancelar(
        self,
        numero: str,
        codigo_verificacao: str,
        motivo: str
    ) -> bool:
        """Cancela NFSe."""
        pass

    def _montar_rps(self, **kwargs) -> str:
        """Monta XML do RPS."""
        # Implementar de acordo com o adapter
        pass

    def _assinar_xml(self, xml: str) -> str:
        """Assina XML com certificado A1."""
        # Usar signxml ou similar
        pass

    async def _enviar(self, xml: str) -> dict:
        """Envia para webservice da prefeitura."""
        pass

    def _processar_resposta(self, response: dict) -> NFSeData:
        """Processa resposta da prefeitura."""
        pass
```

---

## ENDPOINTS

### Banking

```
GET    /api/v1/banking/accounts              - Listar contas
GET    /api/v1/banking/accounts/{id}/balance - Saldo
GET    /api/v1/banking/accounts/{id}/statement - Extrato
POST   /api/v1/banking/pix                   - Enviar PIX
POST   /api/v1/banking/ted                   - Enviar TED
POST   /api/v1/banking/boleto                - Pagar boleto
GET    /api/v1/banking/payments/{id}         - Status pagamento
```

### Messaging

```
POST   /api/v1/whatsapp/send                 - Enviar mensagem
POST   /api/v1/whatsapp/template             - Enviar template
GET    /api/v1/whatsapp/messages             - Historico
POST   /api/v1/email/send                    - Enviar email
POST   /api/v1/email/campaign                - Enviar campanha
```

### Signature

```
POST   /api/v1/signature/send                - Enviar para assinatura
GET    /api/v1/signature/{id}/status         - Status
GET    /api/v1/signature/{id}/url            - URL de assinatura
GET    /api/v1/signature/{id}/document       - Baixar documento
```

### NFSe

```
POST   /api/v1/nfse/emit                     - Emitir NFSe
GET    /api/v1/nfse/{numero}                 - Consultar
POST   /api/v1/nfse/{numero}/cancel          - Cancelar
GET    /api/v1/nfse/{numero}/pdf             - Baixar PDF
```

---

## CHECKLIST MODULO INTEGRACOES

- [ ] Open Banking
  - [ ] Adapter BB
  - [ ] Adapter Itau
  - [ ] Adapter Bradesco
  - [ ] Adapter Santander

- [ ] Messaging
  - [ ] WhatsApp Client
  - [ ] Templates
  - [ ] Email Client

- [ ] Signature
  - [ ] DocuSign
  - [ ] Clicksign

- [ ] Government
  - [ ] eSocial
  - [ ] NFSe (SP, RJ, BH)

- [ ] Testes >= 85%
- [ ] Pylint 100/100

---

*Skill Integracoes - ERP Conecta Mais Fase 2*
