"""Briefing Executivo — Endpoint REST + envio Telegram."""

import logging
import os

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/briefing", tags=["Briefing Executivo"])

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


async def _coletar(db: AsyncSession) -> dict:
    """Coleta dados reais do banco."""
    from datetime import date

    hoje = date.today()
    d: dict = {}

    def _scalar(result, field: str, default=0):
        row = result.fetchone()
        return float(getattr(row, field, default) or default) if row else default

    try:
        r = await db.execute(text("SELECT SUM(current_balance) as v FROM bank_accounts WHERE ativo=true"))
        d["saldo"] = _scalar(r, "v")
    except Exception:
        d["saldo"] = 0

    try:
        r = await db.execute(
            text(
                "SELECT COUNT(*) as q, COALESCE(SUM(valor_servicos),0) as v FROM nfses "
                "WHERE data_emissao >= date_trunc('month', CURRENT_DATE)"
            )
        )
        row = r.fetchone()
        d["nfse_qtd"] = int(row.q) if row else 0
        d["nfse_val"] = float(row.v) if row else 0
    except Exception:
        d["nfse_qtd"] = 0
        d["nfse_val"] = 0

    try:
        r = await db.execute(
            text(
                "SELECT COUNT(*) as q, COALESCE(SUM(gross_value),0) as v "
                "FROM receivable_accounts WHERE due_date < :h AND status='pendente'"
            ),
            {"h": hoje},
        )
        row = r.fetchone()
        d["vencidos"] = int(row.q) if row else 0
        d["vencido_val"] = float(row.v) if row else 0
    except Exception:
        d["vencidos"] = 0
        d["vencido_val"] = 0

    try:
        r = await db.execute(
            text(
                "SELECT COUNT(*) as q, COALESCE(SUM(monthly_value),0) as v "
                "FROM contracts WHERE status IN ('ativo','ACTIVE','active')"
            )
        )
        row = r.fetchone()
        d["contratos"] = int(row.q) if row else 0
        d["mrr"] = float(row.v) if row else 0
    except Exception:
        d["contratos"] = 0
        d["mrr"] = 0

    try:
        r = await db.execute(text("SELECT COUNT(*) as q FROM employees WHERE status='ativo'"))
        d["func"] = int(r.fetchone().q)
    except Exception:
        d["func"] = 0

    try:
        r = await db.execute(
            text(
                "SELECT COUNT(*) FILTER (WHERE reconciliation_status='conciliado') as ok, "
                "COUNT(*) FILTER (WHERE reconciliation_status='pendente') as pend "
                "FROM bank_transactions"
            )
        )
        row = r.fetchone()
        d["conc_ok"] = int(row.ok) if row else 0
        d["conc_pend"] = int(row.pend) if row else 0
    except Exception:
        d["conc_ok"] = 0
        d["conc_pend"] = 0

    try:
        r = await db.execute(
            text(
                "SELECT COUNT(*) as q, COALESCE(SUM(gross_value),0) as v "
                "FROM payable_accounts WHERE due_date <= CURRENT_DATE + 7 AND status='pendente'"
            )
        )
        row = r.fetchone()
        d["pagar_qtd"] = int(row.q) if row else 0
        d["pagar_val"] = float(row.v) if row else 0
    except Exception:
        d["pagar_qtd"] = 0
        d["pagar_val"] = 0

    return d


def _fmt(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _montar_texto(d: dict) -> str:
    from datetime import datetime

    h = datetime.now()
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]

    linhas = [
        f"📊 BRIEFING {dias[h.weekday()]} {h.strftime('%d/%m/%Y %H:%M')}",
        "",
        f"💰 Saldo: {_fmt(d['saldo'])}",
        f"📋 MRR: {_fmt(d['mrr'])} ({d['contratos']} contratos)",
        f"📄 NFS-e mes: {d['nfse_qtd']} ({_fmt(d['nfse_val'])})",
    ]

    if d.get("vencidos", 0) > 0:
        linhas.append(f"🔴 VENCIDOS: {d['vencidos']} ({_fmt(d['vencido_val'])})")
    if d.get("pagar_qtd", 0) > 0:
        linhas.append(f"📤 A pagar 7d: {d['pagar_qtd']} ({_fmt(d['pagar_val'])})")

    linhas.extend(
        [
            f"👷 Equipe: {d['func']} ativos",
            f"🔄 Conciliacao: {d['conc_ok']} OK | {d['conc_pend']} pendentes",
            "",
            "Bom dia, Jordan. O que priorizo?",
        ]
    )

    return "\n".join(linhas)


async def _enviar_telegram(texto: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": texto},
                timeout=15,
            )
        return r.status_code == 200
    except Exception as e:
        logger.error("Telegram falhou: %s", e)
        return False


@router.get("/diario")
async def briefing_diario(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
) -> dict:
    """Retorna briefing executivo do dia com dados reais."""
    dados = await _coletar(db)
    texto = _montar_texto(dados)
    return {"texto": texto, "dados": dados}


@router.post("/enviar")
async def enviar_briefing(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
) -> dict:
    """Gera e envia briefing via Telegram."""
    dados = await _coletar(db)
    texto = _montar_texto(dados)
    enviado = await _enviar_telegram(texto)
    return {
        "texto": texto,
        "dados": dados,
        "enviado": enviado,
        "canal": "telegram" if TELEGRAM_TOKEN else "nenhum",
    }


@router.get("/status")
async def briefing_status() -> dict:
    """Health check do briefing."""
    from datetime import datetime

    return {
        "status": "ok",
        "telegram_configurado": bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID),
        "hora": datetime.now().isoformat(),
        "proximo": "07:30 seg-sex",
    }
