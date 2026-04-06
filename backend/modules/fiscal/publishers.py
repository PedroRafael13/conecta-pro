"""
Publishers do módulo Fiscal para o ConectaEventBus.

Publica eventos de certidões, NFS-e e vencimentos fiscais.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any
from uuid import UUID

from infrastructure.event_bus import ConectaEvent, EventTypes, event_bus

logger = logging.getLogger(__name__)


async def publish_certidao_vencida(
    certidao_id: str | UUID,
    tipo: str,
    data_vencimento: date | str,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando uma certidão está vencida."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FISCAL_CERTIDAO_VENCIDA,
                payload={
                    "certidao_id": str(certidao_id),
                    "tipo": tipo,
                    "data_vencimento": str(data_vencimento),
                    **(extra or {}),
                },
                source_module="fiscal",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_certidao_vencida falhou: %s", exc)


async def publish_certidao_renovada(
    certidao_id: str | UUID,
    tipo: str,
    nova_validade: date | str,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando uma certidão é renovada com sucesso."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FISCAL_CERTIDAO_RENOVADA,
                payload={
                    "certidao_id": str(certidao_id),
                    "tipo": tipo,
                    "nova_validade": str(nova_validade),
                    **(extra or {}),
                },
                source_module="fiscal",
                cliente_id=str(cliente_id) if cliente_id else None,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_certidao_renovada falhou: %s", exc)


async def publish_nfs_emitida(
    nfs_id: str | UUID,
    numero: str | int,
    valor: float,
    tomador: str,
    competencia: str | None = None,
    cliente_id: str | UUID | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Publica evento quando uma NFS-e é emitida com sucesso."""
    try:
        await event_bus.publish(
            ConectaEvent(
                event_type=EventTypes.FISCAL_NFS_EMITIDA,
                payload={
                    "nfs_id": str(nfs_id),
                    "numero": str(numero),
                    "valor": valor,
                    "tomador": tomador,
                    **(extra or {}),
                },
                source_module="fiscal",
                cliente_id=str(cliente_id) if cliente_id else None,
                competencia=competencia,
            )
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("publish_nfs_emitida falhou: %s", exc)


async def verificar_e_publicar_vencimentos(
    certidoes: list[dict[str, Any]],
    cliente_id: str | UUID | None = None,
) -> int:
    """
    Itera lista de certidões e publica eventos de vencimento.

    Args:
        certidoes: Lista de dicts com chaves ``id``, ``tipo``, ``data_vencimento``.
        cliente_id: ID do cliente/condomínio, se aplicável.

    Returns:
        Quantidade de eventos publicados.
    """
    hoje = date.today()
    publicados = 0
    for cert in certidoes:
        try:
            venc = cert.get("data_vencimento")
            if isinstance(venc, str):
                venc = date.fromisoformat(venc.split("T")[0])
            if isinstance(venc, datetime):
                venc = venc.date()
            if venc and venc <= hoje:
                await publish_certidao_vencida(
                    certidao_id=cert.get("id", ""),
                    tipo=cert.get("tipo", "desconhecido"),
                    data_vencimento=venc,
                    cliente_id=cliente_id,
                )
                publicados += 1
        except Exception as exc:  # noqa: BLE001
            logger.warning("verificar_e_publicar_vencimentos item falhou: %s", exc)
    return publicados
