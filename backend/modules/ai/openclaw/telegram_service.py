"""
Serviço de notificação Telegram para diagnósticos do OpenClaw.

Envia mensagens formatadas em HTML para o chat configurado.
"""

import os
import time

import httpx
from loguru import logger

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
API_URL = "https://api.telegram.org"

# Throttle: máx 1 notificação por alert_name a cada 5 minutos
THROTTLE_SECONDS = 300
MAX_ALERTS_PER_HOUR = 10
_last_sent: dict[str, float] = {}
_hourly_count: list[float] = []


def _severity_emoji(severity: str) -> str:
    return {"critical": "\u2757", "warning": "\u26a0\ufe0f", "info": "\u2139\ufe0f"}.get(severity, "\u2753")


def _status_emoji(status: str) -> str:
    return {
        "resolved": "\u2705",
        "acting": "\u2699\ufe0f",
        "diagnosing": "\ud83d\udd0d",
        "failed": "\u274c",
        "escalated": "\ud83d\udea8",
    }.get(status, "\ud83d\udce1")


async def send_diagnosis(
    alert_name: str,
    severity: str,
    status: str,
    diagnosis: str,
    actions: list[dict],
    intervention_id: str,
) -> str | None:
    """
    Envia diagnóstico para o Telegram.

    Returns:
        message_id se enviado com sucesso, None caso contrário.
    """
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning("Telegram nao configurado (TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID ausentes)")
        return None

    # Throttle: suprimir duplicatas do mesmo alerta
    now = time.time()
    last = _last_sent.get(alert_name, 0)
    if now - last < THROTTLE_SECONDS:
        logger.info(f"Telegram throttled: {alert_name} (enviado {int(now - last)}s atrás, limite {THROTTLE_SECONDS}s)")
        return None

    # Throttle: limite global por hora
    _hourly_count[:] = [t for t in _hourly_count if now - t < 3600]
    if len(_hourly_count) >= MAX_ALERTS_PER_HOUR:
        logger.warning(f"Telegram throttled: limite de {MAX_ALERTS_PER_HOUR} alertas/hora atingido")
        return None

    _last_sent[alert_name] = now
    _hourly_count.append(now)

    sev_emoji = _severity_emoji(severity)
    status_emoji = _status_emoji(status)

    # Resumo das ações
    action_lines = []
    for a in actions[:10]:  # limita a 10
        step = a.get("step", "?")
        result = str(a.get("result", ""))[:100]
        action_lines.append(f"  <code>{step}</code>: {result}")
    actions_text = "\n".join(action_lines) if action_lines else "  Nenhuma acao executada"

    # Truncar diagnóstico para caber no Telegram (limite 4096 chars)
    diag_truncated = diagnosis[:1500] if diagnosis else "Sem diagnostico"

    message = (
        f"{sev_emoji} <b>OpenClaw — {alert_name}</b>\n"
        f"Status: {status_emoji} <b>{status.upper()}</b>\n"
        f"Severidade: <code>{severity}</code>\n\n"
        f"<b>Diagnostico:</b>\n<pre>{diag_truncated}</pre>\n\n"
        f"<b>Acoes:</b>\n{actions_text}\n\n"
        f"<i>ID: {intervention_id}</i>"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{API_URL}/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": CHAT_ID,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
            )
            data = response.json()
            if data.get("ok"):
                msg_id = str(data["result"]["message_id"])
                logger.info(f"Telegram enviado: message_id={msg_id}")
                return msg_id
            else:
                logger.error(f"Telegram API erro: {data}")
                return None
    except Exception as e:
        logger.error(f"Falha ao enviar Telegram: {e}")
        return None
