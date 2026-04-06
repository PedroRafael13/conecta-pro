"""Publishers de eventos do módulo Ponto Eletrônico.

Publica no ConectaEventBus sem bloquear o fluxo principal.
Falhas são registradas como warning e nunca propagadas.
"""

import logging

from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

logger = logging.getLogger(__name__)


async def publish_batida_registrada(
    punch_id: str,
    employee_id: str,
    funcionario_nome: str,
    punch_type: str,
    punch_timestamp: str,
    cliente_id: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> None:
    """Publica evento ponto.batida.registrada no barramento de eventos."""
    try:
        payload: dict = {
            "punch_id": punch_id,
            "employee_id": employee_id,
            "funcionario_nome": funcionario_nome,
            "punch_type": punch_type,
            "punch_timestamp": punch_timestamp,
        }
        if latitude is not None:
            payload["latitude"] = latitude
        if longitude is not None:
            payload["longitude"] = longitude

        evento = ConectaEvent(
            event_type=EventTypes.PONTO_BATIDA_REGISTRADA,
            payload=payload,
            source_module="ponto",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish batida_registrada: %s", e)


async def publish_espelho_fechado(
    employee_id: str,
    funcionario_nome: str,
    competencia: str,
    total_horas: float,
    horas_extras: float,
    faltas: int,
    cliente_id: str | None = None,
) -> None:
    """Publica evento ponto.espelho.fechado no barramento de eventos."""
    try:
        payload: dict = {
            "employee_id": employee_id,
            "funcionario_nome": funcionario_nome,
            "competencia": competencia,
            "total_horas": total_horas,
            "horas_extras": horas_extras,
            "faltas": faltas,
        }

        evento = ConectaEvent(
            event_type=EventTypes.PONTO_ESPELHO_FECHADO,
            payload=payload,
            source_module="ponto",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
            competencia=competencia,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish espelho_fechado: %s", e)


async def publish_falta_confirmada(
    employee_id: str,
    funcionario_nome: str,
    data: str,
    justificada: bool,
    cliente_id: str | None = None,
) -> None:
    """Publica evento ponto.falta.confirmada no barramento de eventos."""
    try:
        payload: dict = {
            "employee_id": employee_id,
            "funcionario_nome": funcionario_nome,
            "data": data,
            "justificada": justificada,
        }

        evento = ConectaEvent(
            event_type=EventTypes.PONTO_FALTA_CONFIRMADA,
            payload=payload,
            source_module="ponto",
            funcionario_id=employee_id,
            cliente_id=cliente_id,
        )
        await event_bus.publish(evento)
    except Exception as e:
        logger.warning("Falha publish falta_confirmada: %s", e)
