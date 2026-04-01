"""
WhatsApp Service — Evolution API integration.

Envio de kits documentais, alertas de certidoes e notificacoes
para clientes via WhatsApp usando a Evolution API.
"""

import logging
import os

import aiohttp

logger = logging.getLogger(__name__)

MONTH_NAMES = [
    "Janeiro",
    "Fevereiro",
    "Marco",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


class WhatsAppService:
    """Servico de envio de mensagens via Evolution API."""

    def __init__(self) -> None:
        self.base_url = os.getenv("EVOLUTION_API_URL", "https://api.evolution.app.br")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.instance = os.getenv("WHATSAPP_INSTANCE_ID", "conecta-pro")
        self.enabled = os.getenv("WHATSAPP_API_ENABLED", "false").lower() == "true"

    def _clean_phone(self, phone: str) -> str:
        """Remove formatacao e adiciona DDI 55."""
        clean = "".join(c for c in phone if c.isdigit())
        if not clean.startswith("55"):
            clean = f"55{clean}"
        return clean

    async def _send_message(self, phone: str, message: str) -> dict:
        """Envia mensagem via Evolution API."""
        if not self.enabled:
            logger.info("WhatsApp desabilitado (WHATSAPP_API_ENABLED=false)")
            return {"status": "disabled", "message": "WhatsApp nao habilitado"}

        if not self.api_key:
            logger.warning("EVOLUTION_API_KEY nao configurada")
            return {"status": "error", "message": "API key nao configurada"}

        clean_phone = self._clean_phone(phone)
        payload = {"number": clean_phone, "text": message}
        headers = {"Content-Type": "application/json", "apikey": self.api_key}
        url = f"{self.base_url}/message/sendText/{self.instance}"

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp,
            ):
                data = await resp.json()
                if resp.status in (200, 201):
                    logger.info("WhatsApp enviado para %s", clean_phone)
                    return {"status": "sent", "phone": clean_phone, "data": data}
                logger.error("Erro WhatsApp %s: %s", resp.status, data)
                return {"status": "error", "code": resp.status, "data": data}
        except Exception as e:
            logger.error("Excecao WhatsApp: %s", e)
            return {"status": "exception", "error": str(e)}

    async def send_kit_notification(
        self,
        phone: str,
        client_name: str,
        month: int,
        year: int,
        documents_count: int,
        portal_url: str | None = None,
    ) -> dict:
        """Notifica cliente sobre kit mensal disponivel."""
        mes = MONTH_NAMES[month - 1] if 1 <= month <= 12 else str(month)
        message = (
            f"\U0001f3e2 *Conecta Mais \u2014 Seguranca e Tecnologia*\n\n"
            f"Ola! O kit documental de *{mes}/{year}* "
            f"esta disponivel para *{client_name}*.\n\n"
            f"\U0001f4c4 *{documents_count} documentos* incluidos:\n"
            f"\u2022 Contracheques\n"
            f"\u2022 Folhas de ponto\n"
            f"\u2022 Certidoes\n"
            f"\u2022 NFS-e\n\n"
        )
        if portal_url:
            message += f"\U0001f517 Acesse: {portal_url}\n\n"
        message += (
            "Em caso de duvidas, entre em contato:\n"
            "\U0001f4de (92) 9348-5518\n"
            "\U0001f4e7 contato@conectamaistech.com.br"
        )
        return await self._send_message(phone, message)

    async def send_certificate_alert(
        self,
        phone: str,
        client_name: str,
        certificate_type: str,
        expiry_date: str,
        days_remaining: int,
    ) -> dict:
        """Alerta sobre certidao vencendo."""
        emoji = "\U0001f534" if days_remaining <= 7 else "\U0001f7e1"
        urgency = "URGENTE" if days_remaining <= 7 else "ATENCAO"
        message = (
            f"{emoji} *{urgency} \u2014 Conecta Mais*\n\n"
            f"A certidao *{certificate_type}* de *{client_name}* "
            f"vence em *{days_remaining} dias* ({expiry_date}).\n\n"
            f"Por favor, providencie a renovacao.\n\n"
            f"\U0001f4de (92) 9348-5518"
        )
        return await self._send_message(phone, message)

    async def send_nfse_notification(
        self,
        phone: str,
        client_name: str,
        nfse_number: str,
        value: float,
        month: int,
        year: int,
    ) -> dict:
        """Notifica emissao de NFS-e."""
        mes = MONTH_NAMES[month - 1] if 1 <= month <= 12 else str(month)
        message = (
            f"\U0001f4cb *NFS-e Emitida \u2014 Conecta Mais*\n\n"
            f"Cliente: *{client_name}*\n"
            f"NFS-e n\u00ba: *{nfse_number}*\n"
            f"Competencia: *{mes}/{year}*\n"
            f"Valor: *R$ {value:,.2f}*\n\n"
            f"A nota fiscal esta disponivel no portal.\n"
            f"\U0001f4de (92) 9348-5518"
        )
        return await self._send_message(phone, message)

    async def send_custom(self, phone: str, message: str) -> dict:
        """Envia mensagem customizada."""
        return await self._send_message(phone, message)

    async def check_status(self) -> dict:
        """Verifica status da conexao WhatsApp."""
        if not self.enabled:
            return {"online": False, "reason": "disabled"}
        if not self.api_key:
            return {"online": False, "reason": "no_api_key"}

        headers = {"apikey": self.api_key}
        url = f"{self.base_url}/instance/fetchInstances"
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp,
            ):
                if resp.status == 200:
                    data = await resp.json()
                    return {"online": True, "instances": data}
                return {"online": False, "code": resp.status}
        except Exception as e:
            return {"online": False, "error": str(e)}


whatsapp_service = WhatsAppService()
