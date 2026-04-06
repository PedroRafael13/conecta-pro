"""
Publishers do módulo Saúde Ocupacional para o ConectaEventBus.

Publica eventos de ASO, EPI e treinamentos.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any
from uuid import UUID

from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

logger = logging.getLogger(__name__)


async def publish_aso_emitido(
    aso_id: str | UUID,
    funcionario_id: str | UUID,
    funcionario_nome: str,
    tipo_aso: str,
    resultado: str,
    data_validade: date | str | None = None,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um ASO (Atestado de Saúde Ocupacional) é emitido."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.SAUDE_ASO_EMITIDO,
                payload={
                    "aso_id": str(aso_id),
                    "funcionario_id": str(funcionario_id),
                    "funcionario_nome": funcionario_nome,
                    "tipo_aso": tipo_aso,
                    "resultado": resultado,
                    "data_validade": str(data_validade) if data_validade else None,
                    **(extra or {}),
                },
                source_module="health_occupational",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_aso_emitido falhou: %s", exc)


async def publish_aso_vencendo(
    aso_id: str | UUID,
    funcionario_id: str | UUID,
    funcionario_nome: str,
    data_vencimento: date | str,
    dias_restantes: int,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um ASO está próximo do vencimento."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.SAUDE_ASO_VENCENDO,
                payload={
                    "aso_id": str(aso_id),
                    "funcionario_id": str(funcionario_id),
                    "funcionario_nome": funcionario_nome,
                    "data_vencimento": str(data_vencimento),
                    "dias_restantes": dias_restantes,
                    **(extra or {}),
                },
                source_module="health_occupational",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_aso_vencendo falhou: %s", exc)


async def publish_epi_entregue(
    entrega_id: str | UUID,
    funcionario_id: str | UUID,
    funcionario_nome: str,
    epi_nome: str,
    quantidade: int | float,
    data_entrega: date | str | None = None,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um EPI é entregue a um funcionário."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.SAUDE_EPI_ENTREGUE,
                payload={
                    "entrega_id": str(entrega_id),
                    "funcionario_id": str(funcionario_id),
                    "funcionario_nome": funcionario_nome,
                    "epi_nome": epi_nome,
                    "quantidade": quantidade,
                    "data_entrega": str(data_entrega) if data_entrega else None,
                    **(extra or {}),
                },
                source_module="health_occupational",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_epi_entregue falhou: %s", exc)


async def publish_treinamento_concluido(
    treinamento_id: str | UUID,
    funcionario_id: str | UUID,
    funcionario_nome: str,
    titulo: str,
    carga_horaria: float,
    data_conclusao: date | str | None = None,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um treinamento de saúde/segurança é concluído."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.SAUDE_TREINAMENTO_CONCLUIDO,
                payload={
                    "treinamento_id": str(treinamento_id),
                    "funcionario_id": str(funcionario_id),
                    "funcionario_nome": funcionario_nome,
                    "titulo": titulo,
                    "carga_horaria": carga_horaria,
                    "data_conclusao": str(data_conclusao) if data_conclusao else None,
                    **(extra or {}),
                },
                source_module="health_occupational",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_treinamento_concluido falhou: %s", exc)
