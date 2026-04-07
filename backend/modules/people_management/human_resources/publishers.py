"""
Publishers do módulo RH (Recursos Humanos) para o ConectaEventBus.

Publica eventos de carreira, avaliação de desempenho, onboarding e 360.
"""

from __future__ import annotations

import logging

from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

logger = logging.getLogger(__name__)


async def publish_plano_carreira_criado(employee_id: str, plan_id: str = "") -> None:
    """Publica evento quando um plano de carreira é criado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_PLANO_CARREIRA_CRIADO,
                payload={"employee_id": employee_id, "plan_id": plan_id},
                source_module="rh",
                funcionario_id=employee_id,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_plano_carreira_criado falhou: %s", exc)


async def publish_milestone_concluido(plan_id: str, milestone_index: int = 0, employee_id: str = "") -> None:
    """Publica evento quando um milestone de carreira é concluído."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_MILESTONE_CONCLUIDO,
                payload={"plan_id": plan_id, "milestone_index": milestone_index, "employee_id": employee_id},
                source_module="rh",
                funcionario_id=employee_id or None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_milestone_concluido falhou: %s", exc)


async def publish_avaliacao_criada(employee_id: str, review_id: str = "") -> None:
    """Publica evento quando uma avaliação de desempenho é criada."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_AVALIACAO_CRIADA,
                payload={"employee_id": employee_id, "review_id": review_id},
                source_module="rh",
                funcionario_id=employee_id,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_avaliacao_criada falhou: %s", exc)


async def publish_avaliacao_concluida(employee_id: str, review_id: str = "") -> None:
    """Publica evento quando uma avaliação de desempenho é concluída."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_AVALIACAO_CONCLUIDA,
                payload={"employee_id": employee_id, "review_id": review_id},
                source_module="rh",
                funcionario_id=employee_id,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_avaliacao_concluida falhou: %s", exc)


async def publish_onboarding_item_concluido(employee_id: str, item_id: int = 0) -> None:
    """Publica evento quando uma etapa de onboarding é concluída."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_ONBOARDING_ITEM_CONCLUIDO,
                payload={"employee_id": employee_id, "item_id": item_id},
                source_module="rh",
                funcionario_id=employee_id,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_onboarding_item_concluido falhou: %s", exc)


async def publish_avaliacao_360_criada(ciclo_id: str, employee_id: str = "") -> None:
    """Publica evento quando um ciclo de avaliação 360 é criado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_AVALIACAO_360_CRIADA,
                payload={"ciclo_id": ciclo_id, "employee_id": employee_id},
                source_module="rh",
                funcionario_id=employee_id or None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_avaliacao_360_criada falhou: %s", exc)


async def publish_avaliacao_360_iniciada(ciclo_id: str) -> None:
    """Publica evento quando a coleta de respostas do ciclo 360 é iniciada."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.RH_AVALIACAO_360_INICIADA,
                payload={"ciclo_id": ciclo_id},
                source_module="rh",
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_avaliacao_360_iniciada falhou: %s", exc)
