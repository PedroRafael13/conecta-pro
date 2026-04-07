"""
Publishers do módulo Financeiro para o ConectaEventBus.

Publica eventos de notas emitidas, contratos inadimplentes e renovações.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

logger = logging.getLogger(__name__)


async def publish_nota_emitida(
    nota_id: str | UUID,
    numero: str | int,
    valor: float,
    cliente_id: str | UUID | None = None,
    competencia: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando uma nota fiscal/financeira é emitida."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FIN_NOTA_EMITIDA,
                payload={
                    "nota_id": str(nota_id),
                    "numero": str(numero),
                    "valor": valor,
                    **(extra or {}),
                },
                source_module="financial",
                cliente_id=str(cliente_id) if cliente_id else None,
                competencia=competencia,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_nota_emitida falhou: %s", exc)


async def publish_contrato_inadimplente(
    contrato_id: str | UUID,
    cliente_nome: str,
    valor_em_atraso: float,
    dias_atraso: int,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um contrato é identificado como inadimplente."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FIN_CONTRATO_INADIMPLENTE,
                payload={
                    "contrato_id": str(contrato_id),
                    "cliente_nome": cliente_nome,
                    "valor_em_atraso": valor_em_atraso,
                    "dias_atraso": dias_atraso,
                    **(extra or {}),
                },
                source_module="financial",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_contrato_inadimplente falhou: %s", exc)


async def publish_contrato_renovado(
    contrato_id: str | UUID,
    cliente_nome: str,
    novo_valor: float,
    nova_vigencia_fim: str,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um contrato é renovado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FIN_CONTRATO_RENOVADO,
                payload={
                    "contrato_id": str(contrato_id),
                    "cliente_nome": cliente_nome,
                    "novo_valor": novo_valor,
                    "nova_vigencia_fim": nova_vigencia_fim,
                    **(extra or {}),
                },
                source_module="financial",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_contrato_renovado falhou: %s", exc)


async def publish_pagamento_recebido(
    payment_id: str | UUID,
    installment_id: str | UUID,
    valor: float,
    cliente_id: str | UUID | None = None,
    condominio_id: str | UUID | None = None,
    competencia: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um recebimento (conta a receber) é registrado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FIN_PAGAMENTO_RECEBIDO,
                payload={
                    "payment_id": str(payment_id),
                    "installment_id": str(installment_id),
                    "valor": valor,
                    "condominio_id": str(condominio_id) if condominio_id else None,
                    **(extra or {}),
                },
                source_module="financial",
                cliente_id=str(cliente_id) if cliente_id else None,
                competencia=competencia,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_pagamento_recebido falhou: %s", exc)


async def publish_pagamento_realizado(
    payment_id: str | UUID,
    installment_id: str | UUID,
    valor: float,
    fornecedor: str | None = None,
    cliente_id: str | UUID | None = None,
    competencia: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando um pagamento (conta a pagar) é registrado."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FIN_PAGAMENTO_REALIZADO,
                payload={
                    "payment_id": str(payment_id),
                    "installment_id": str(installment_id),
                    "valor": valor,
                    "fornecedor": fornecedor,
                    **(extra or {}),
                },
                source_module="financial",
                cliente_id=str(cliente_id) if cliente_id else None,
                competencia=competencia,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_pagamento_realizado falhou: %s", exc)


async def publish_inadimplencia_detectada(
    account_id: str | UUID,
    tipo: str,
    motivo: str,
    cliente_id: str | UUID | None = None,
    valor: float = 0.0,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando inadimplência é detectada (suspend/protest/write-off/block)."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FIN_INADIMPLENCIA_DETECTADA,
                payload={
                    "account_id": str(account_id),
                    "tipo": tipo,
                    "motivo": motivo,
                    "valor": valor,
                    **(extra or {}),
                },
                source_module="financial",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_inadimplencia_detectada falhou: %s", exc)
