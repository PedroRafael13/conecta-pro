"""
Publishers CRM — Conecta PRO
Publica eventos no ConectaEventBus quando lead vira cliente,
contrato é assinado/ativado ou proposta aprovada.

O GEDEON escuta esses eventos para espelhar o cliente
em todos os módulos necessários automaticamente.
"""

import logging

logger = logging.getLogger(__name__)


async def publish_lead_convertido(
    lead_id: str,
    nome: str,
    empresa: str,
    score: float | None = None,
    cliente_id: str | None = None,
) -> None:
    """Publicar evento quando lead muda para status WON."""
    try:
        from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

        evento = ConectaEvent(
            event_type=EventTypes.CRM_LEAD_CONVERTIDO,
            payload={
                "lead_id": lead_id,
                "nome": nome,
                "empresa": empresa,
                "score": score,
                "cliente_id": cliente_id,
            },
            source_module="crm",
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
        logger.info("Lead convertido publicado: %s [%s]", nome, lead_id)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Falha ao publicar lead convertido: %s", exc)


async def publish_contrato_assinado(
    contrato_id: str,
    numero: str,
    cliente_id: str,
    nome_cliente: str,
    tipo_contrato: str,
    valor_mensal: float,
    vigencia_inicio: str,
    vigencia_fim: str | None = None,
) -> None:
    """Publicar evento quando contrato é ativado após assinatura."""
    try:
        from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

        evento = ConectaEvent(
            event_type=EventTypes.CRM_CONTRATO_ASSINADO,
            payload={
                "contrato_id": contrato_id,
                "numero": numero,
                "cliente_id": cliente_id,
                "nome_cliente": nome_cliente,
                "tipo_contrato": tipo_contrato,
                "valor_mensal": valor_mensal,
                "vigencia_inicio": vigencia_inicio,
                "vigencia_fim": vigencia_fim,
            },
            source_module="crm",
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
        logger.info(
            "Contrato assinado publicado: %s [%s]",
            numero,
            nome_cliente,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Falha ao publicar contrato assinado: %s", exc)


async def publish_cliente_ativo(
    cliente_id: str,
    nome: str,
    cnpj: str | None = None,
    tipo_contrato: str | None = None,
    valor_contrato: float | None = None,
) -> None:
    """
    Publicar evento quando cliente está ativo no CRM.
    O GEDEON reage criando o cliente em GED, Operacional,
    Financeiro, Fiscal e Portal automaticamente.
    """
    try:
        from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

        evento = ConectaEvent(
            event_type=EventTypes.CRM_CLIENTE_ATIVO,
            payload={
                "cliente_id": cliente_id,
                "nome": nome,
                "cnpj": cnpj,
                "tipo_contrato": tipo_contrato,
                "valor_contrato": valor_contrato,
            },
            source_module="crm",
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
        logger.info("Cliente ativo publicado: %s [%s]", nome, cliente_id)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Falha ao publicar cliente ativo: %s", exc)
