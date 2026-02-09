"""Controller para webhooks de dispositivos REP."""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.hr.rep_integration.repositories import REPDeviceRepository
from modules.hr.rep_integration.services import SyncService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["REP Webhooks"])


@router.post("/events/{device_serial}")
async def receive_events_webhook(
    device_serial: str,
    request: Request,
    x_signature: str | None = Header(None, alias="X-Signature"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Recebe eventos via webhook do dispositivo.

    Este endpoint não requer autenticação JWT pois é chamado
    diretamente pelo dispositivo REP.
    """
    # Ler body
    body = await request.body()

    # Validar assinatura se fornecida
    device_repo = REPDeviceRepository(db)
    device = await device_repo.get_by_serial(device_serial)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispositivo inativo",
        )

    # Validar assinatura HMAC se configurada
    if device.webhook_secret and x_signature:
        expected_signature = hmac.new(
            device.webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(x_signature, expected_signature):
            logger.warning(f"Assinatura inválida para webhook do dispositivo {device_serial}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Assinatura inválida",
            )

    # Parsear eventos
    try:
        import json  # pylint: disable=import-outside-toplevel

        data = json.loads(body)
        events = data.get("events", [])
    except Exception as e:
        logger.error(f"Erro ao parsear webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de dados inválido",
        )

    # Processar eventos
    sync_service = SyncService(db)
    success, result = await sync_service.process_webhook_events(
        device_serial=device_serial,
        events=events,
        signature=x_signature,
    )

    if not success:
        logger.error(f"Erro ao processar webhook: {result}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Erro ao processar eventos"),
        )

    return result


@router.post("/control-id/{device_serial}")
async def receive_control_id_webhook(
    device_serial: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Webhook específico para Control iD.

    Formato esperado:
    {
        "device": {"serial": "..."},
        "object": "access_logs",
        "action": "insert",
        "values": [...]
    }
    """
    body = await request.body()

    try:
        import json  # pylint: disable=import-outside-toplevel

        data = json.loads(body)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido",
        )

    # Validar dispositivo
    device_repo = REPDeviceRepository(db)
    device = await device_repo.get_by_serial(device_serial)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    # Converter formato Control iD para formato interno
    events = []
    _ = data  # Usado na conversão Control iD
    values = data.get("values", [])

    for val in values:
        events.append(
            {
                "nsr": val.get("id"),
                "datetime": val.get("time"),
                "pis": val.get("pis"),
                "user_id": val.get("user_id"),
                "user_name": val.get("user_name"),
                "event_type": "entry",  # Control iD não diferencia
                "method": _map_control_id_method(val.get("way", 1)),
                "score": val.get("score"),
            }
        )

    # Processar
    sync_service = SyncService(db)
    _success, result = await sync_service.process_webhook_events(
        device_serial=device_serial,
        events=events,
    )

    return result


@router.post("/intelbras/{device_serial}")
async def receive_intelbras_webhook(
    device_serial: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Webhook específico para Intelbras."""
    body = await request.body()

    try:
        import json  # pylint: disable=import-outside-toplevel

        _ = json.loads(body)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido",
        )

    # Validar dispositivo
    device_repo = REPDeviceRepository(db)
    device = await device_repo.get_by_serial(device_serial)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    # Converter formato Intelbras
    events = []
    # TODO: Implementar conversão do formato Intelbras  # pylint: disable=fixme

    # Processar
    sync_service = SyncService(db)
    _success, result = await sync_service.process_webhook_events(
        device_serial=device_serial,
        events=events,
    )

    return result


@router.get("/test/{device_serial}")
async def test_webhook_endpoint(device_serial: str) -> dict:
    """Endpoint para testar conectividade do webhook."""
    return {
        "status": "ok",
        "device_serial": device_serial,
        "message": "Webhook endpoint is active",
    }


def _map_control_id_method(way_code: int) -> str:
    """Mapeia código de método Control iD."""
    mapping = {
        1: "biometric",
        2: "rfid",
        3: "password",
        4: "facial",
        5: "qrcode",
    }
    return mapping.get(way_code, "biometric")
