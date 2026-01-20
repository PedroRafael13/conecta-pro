"""
Integracao de Assinatura Digital para Propostas.

Integra o modulo de assinatura digital (GED) com propostas comerciais
para permitir assinatura eletronica de propostas aceitas.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from core.logging import logger


class SignatureProvider(str, Enum):
    """Provedor de assinatura digital."""

    INTERNAL = "internal"  # Assinatura interna do sistema
    DOCUSIGN = "docusign"  # DocuSign
    CLICKSIGN = "clicksign"  # ClickSign
    D4SIGN = "d4sign"  # D4Sign
    AUTENTIQUE = "autentique"  # Autentique


class SignatureStatus(str, Enum):
    """Status da assinatura."""

    PENDING = "pending"  # Aguardando assinatura
    SENT = "sent"  # Link enviado
    VIEWED = "viewed"  # Documento visualizado
    SIGNED = "signed"  # Assinado
    REFUSED = "refused"  # Recusado
    EXPIRED = "expired"  # Expirado
    CANCELLED = "cancelled"  # Cancelado


@dataclass
class SignerInfo:
    """Informacoes do signatario."""

    name: str
    email: str
    cpf: Optional[str] = None
    phone: Optional[str] = None
    role: str = "cliente"
    order: int = 1


@dataclass
class SignatureRequest:
    """Requisicao de assinatura."""

    proposal_id: str
    proposal_number: str
    document_url: str
    signers: list[SignerInfo]
    provider: SignatureProvider = SignatureProvider.INTERNAL
    deadline_days: int = 7
    message: Optional[str] = None
    callback_url: Optional[str] = None


@dataclass
class SignatureResult:
    """Resultado da requisicao de assinatura."""

    success: bool
    external_id: Optional[str] = None
    signing_url: Optional[str] = None
    error: Optional[str] = None
    status: SignatureStatus = SignatureStatus.PENDING


class ProposalSignatureService:
    """
    Servico de integracao de assinatura digital para propostas.

    Funcionalidades:
    - Criar requisicao de assinatura para proposta aprovada
    - Integrar com provedores externos (DocuSign, ClickSign, etc)
    - Gerenciar status e notificacoes
    - Processar callbacks de assinatura
    """

    # URLs base dos provedores (configuravel via env)
    PROVIDER_URLS: dict[SignatureProvider, str] = {
        SignatureProvider.DOCUSIGN: "https://app.docusign.com",
        SignatureProvider.CLICKSIGN: "https://app.clicksign.com",
        SignatureProvider.D4SIGN: "https://secure.d4sign.com.br",
        SignatureProvider.AUTENTIQUE: "https://api.autentique.com.br",
    }

    def __init__(
        self,
        provider: SignatureProvider = SignatureProvider.INTERNAL,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        """
        Inicializa o servico.

        Args:
            provider: Provedor de assinatura
            api_key: Chave de API do provedor
            api_secret: Segredo de API do provedor
        """
        self.provider = provider
        self.api_key = api_key
        self.api_secret = api_secret

    async def create_signature_request(
        self, request: SignatureRequest
    ) -> SignatureResult:
        """
        Cria requisicao de assinatura para proposta.

        Args:
            request: Dados da requisicao

        Returns:
            Resultado com URL de assinatura ou erro
        """
        try:
            # Validar dados
            self._validate_request(request)

            # Chamar provedor apropriado
            if request.provider == SignatureProvider.INTERNAL:
                result = await self._create_internal_signature(request)
            elif request.provider == SignatureProvider.DOCUSIGN:
                result = await self._create_docusign_signature(request)
            elif request.provider == SignatureProvider.CLICKSIGN:
                result = await self._create_clicksign_signature(request)
            else:
                result = await self._create_generic_signature(request)

            logger.info(
                "Requisicao de assinatura criada",
                extra={
                    "proposal_id": request.proposal_id,
                    "provider": request.provider.value,
                    "success": result.success,
                },
            )

            return result

        except ValueError as e:
            logger.error(f"Erro de validacao: {e}")
            return SignatureResult(success=False, error=str(e))
        except Exception as e:
            logger.error(f"Erro ao criar requisicao: {e}")
            return SignatureResult(success=False, error="Erro interno")

    async def check_signature_status(
        self, external_id: str
    ) -> SignatureStatus:
        """
        Verifica status da assinatura no provedor.

        Args:
            external_id: ID externo da requisicao

        Returns:
            Status atual da assinatura
        """
        # Implementacao depende do provedor
        # Para interno, consulta banco local
        if self.provider == SignatureProvider.INTERNAL:
            return SignatureStatus.PENDING

        # Para provedores externos, consulta API
        # TODO: Implementar consulta real aos provedores
        return SignatureStatus.PENDING

    async def cancel_signature_request(
        self, external_id: str, reason: Optional[str] = None
    ) -> bool:
        """
        Cancela requisicao de assinatura.

        Args:
            external_id: ID externo da requisicao
            reason: Motivo do cancelamento

        Returns:
            True se cancelado com sucesso
        """
        try:
            logger.info(
                "Cancelando requisicao de assinatura",
                extra={"external_id": external_id, "reason": reason},
            )
            # TODO: Implementar cancelamento real
            return True
        except Exception as e:
            logger.error(f"Erro ao cancelar: {e}")
            return False

    async def process_webhook(
        self, provider: SignatureProvider, payload: dict
    ) -> tuple[str, SignatureStatus]:
        """
        Processa webhook de callback do provedor.

        Args:
            provider: Provedor de origem
            payload: Dados do webhook

        Returns:
            Tupla (external_id, novo_status)
        """
        if provider == SignatureProvider.DOCUSIGN:
            return self._process_docusign_webhook(payload)
        if provider == SignatureProvider.CLICKSIGN:
            return self._process_clicksign_webhook(payload)
        # Fallback
        return payload.get("external_id", ""), SignatureStatus.PENDING

    async def resend_signature_request(
        self, external_id: str, signer_email: str
    ) -> bool:
        """
        Reenvia link de assinatura.

        Args:
            external_id: ID externo
            signer_email: Email do signatario

        Returns:
            True se reenviado com sucesso
        """
        logger.info(
            "Reenviando requisicao",
            extra={"external_id": external_id, "email": signer_email},
        )
        # TODO: Implementar reenvio real
        return True

    def _validate_request(self, request: SignatureRequest) -> None:
        """Valida dados da requisicao."""
        if not request.proposal_id:
            raise ValueError("ID da proposta obrigatorio")
        if not request.signers:
            raise ValueError("Pelo menos um signatario obrigatorio")
        for signer in request.signers:
            if not signer.email:
                raise ValueError("Email do signatario obrigatorio")
            if not signer.name:
                raise ValueError("Nome do signatario obrigatorio")

    async def _create_internal_signature(
        self, request: SignatureRequest
    ) -> SignatureResult:
        """Cria assinatura usando sistema interno."""
        import uuid

        external_id = str(uuid.uuid4())
        # Gera URL de assinatura interna
        signing_url = (
            f"/proposals/{request.proposal_id}/sign?"
            f"token={external_id}"
        )

        return SignatureResult(
            success=True,
            external_id=external_id,
            signing_url=signing_url,
            status=SignatureStatus.PENDING,
        )

    async def _create_docusign_signature(
        self, request: SignatureRequest
    ) -> SignatureResult:
        """
        Cria envelope no DocuSign.

        Requer:
        - Conta DocuSign configurada
        - OAuth2 access token
        - Template ID ou documento

        Fluxo:
        1. Criar envelope com documento
        2. Adicionar signatarios
        3. Enviar e obter URL de assinatura
        """
        if not self.api_key:
            return SignatureResult(
                success=False,
                error="DocuSign API key nao configurada",
            )

        # Simula criacao de envelope
        # Em producao, chamar API real do DocuSign
        import uuid

        external_id = f"docusign_{uuid.uuid4().hex[:12]}"
        base_url = self.PROVIDER_URLS[SignatureProvider.DOCUSIGN]
        signing_url = f"{base_url}/sign/{external_id}"

        logger.info(
            "Envelope DocuSign criado",
            extra={
                "external_id": external_id,
                "signers": len(request.signers),
            },
        )

        return SignatureResult(
            success=True,
            external_id=external_id,
            signing_url=signing_url,
            status=SignatureStatus.SENT,
        )

    async def _create_clicksign_signature(
        self, request: SignatureRequest
    ) -> SignatureResult:
        """
        Cria documento no ClickSign.

        API: https://developers.clicksign.com/docs
        """
        if not self.api_key:
            return SignatureResult(
                success=False,
                error="ClickSign API key nao configurada",
            )

        import uuid

        external_id = f"clicksign_{uuid.uuid4().hex[:12]}"
        signing_url = f"{self.PROVIDER_URLS[SignatureProvider.CLICKSIGN]}/sign/{external_id}"

        return SignatureResult(
            success=True,
            external_id=external_id,
            signing_url=signing_url,
            status=SignatureStatus.SENT,
        )

    async def _create_generic_signature(
        self, request: SignatureRequest
    ) -> SignatureResult:
        """Cria assinatura em provedor generico."""
        import uuid

        external_id = f"{request.provider.value}_{uuid.uuid4().hex[:12]}"

        return SignatureResult(
            success=True,
            external_id=external_id,
            status=SignatureStatus.PENDING,
        )

    def _process_docusign_webhook(
        self, payload: dict
    ) -> tuple[str, SignatureStatus]:
        """Processa webhook do DocuSign."""
        envelope_id = payload.get("envelopeId", "")
        status_str = payload.get("status", "").lower()

        status_map = {
            "sent": SignatureStatus.SENT,
            "delivered": SignatureStatus.VIEWED,
            "completed": SignatureStatus.SIGNED,
            "declined": SignatureStatus.REFUSED,
            "voided": SignatureStatus.CANCELLED,
        }

        return envelope_id, status_map.get(status_str, SignatureStatus.PENDING)

    def _process_clicksign_webhook(
        self, payload: dict
    ) -> tuple[str, SignatureStatus]:
        """Processa webhook do ClickSign."""
        document_key = payload.get("document", {}).get("key", "")
        event = payload.get("event", {}).get("name", "")

        status_map = {
            "sign": SignatureStatus.SIGNED,
            "refuse": SignatureStatus.REFUSED,
            "auto_close": SignatureStatus.SIGNED,
            "cancel": SignatureStatus.CANCELLED,
        }

        return document_key, status_map.get(event, SignatureStatus.PENDING)


# Instancia global
proposal_signature_service = ProposalSignatureService()
