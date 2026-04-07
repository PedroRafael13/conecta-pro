"""
Publishers SST — Saúde e Segurança do Trabalho
Publica eventos no ConectaEventBus quando ASO, EPI ou atestado são registrados.
"""

import logging

logger = logging.getLogger(__name__)


async def publish_aso_emitido(
    employee_id: str,
    funcionario_nome: str,
    tipo_aso: str,
    resultado: str,
    data_validade: str,
    cliente_id: str | None = None,
) -> None:
    """Publicar evento quando ASO é emitido (admissional, periódico, demissional)."""
    try:
        from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

        evento = ConectaEvent(
            event_type=EventTypes.SAUDE_ASO_EMITIDO,
            payload={
                "employee_id": employee_id,
                "nome": funcionario_nome,
                "tipo_aso": tipo_aso,
                "resultado": resultado,
                "data_validade": data_validade,
            },
            source_module="saude",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
        logger.info("ASO publicado no EventBus: %s [%s]", funcionario_nome, tipo_aso)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Falha ao publicar ASO: %s", exc)


async def publish_atestado_registrado(
    employee_id: str,
    funcionario_nome: str,
    data_inicio: str,
    data_fim: str,
    dias: int,
    cliente_id: str | None = None,
) -> None:
    """Publicar evento quando atestado médico é registrado."""
    try:
        from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

        evento = ConectaEvent(
            event_type=EventTypes.DP_ATESTADO_REGISTRADO,
            payload={
                "employee_id": employee_id,
                "nome": funcionario_nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "dias": dias,
            },
            source_module="dp",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
        logger.info(
            "Atestado publicado no EventBus: %s — %d dias",
            funcionario_nome,
            dias,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Falha ao publicar atestado: %s", exc)


async def publish_afastamento_iniciado(
    employee_id: str,
    funcionario_nome: str,
    tipo: str,
    data_inicio: str,
    cid: str | None = None,
    cliente_id: str | None = None,
) -> None:
    """Publicar evento quando afastamento INSS/CAT é iniciado."""
    try:
        from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

        evento = ConectaEvent(
            event_type=EventTypes.SAUDE_AFASTAMENTO_INICIADO,
            payload={
                "employee_id": employee_id,
                "nome": funcionario_nome,
                "tipo": tipo,
                "data_inicio": data_inicio,
                "cid": cid,
            },
            source_module="saude",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
        logger.info(
            "Afastamento publicado no EventBus: %s [%s]",
            funcionario_nome,
            tipo,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Falha ao publicar afastamento: %s", exc)
