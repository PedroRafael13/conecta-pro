"""
Auto Reconciliation Controller — Conciliação Bancária Automática Inter × Notas.

Endpoints:
  POST /conciliar/auto              — executa conciliação em lote (até 649 txs)
  POST /conciliar/{tx_id}           — concilia transação específica
  GET  /conciliar/pendentes         — lista txs sem conciliação
  POST /conciliar/{tx_id}/justificar — registra justificativa para saída sem nota
  GET  /conciliar/relatorio         — resumo da conciliação
"""

import logging
import os

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from core.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conciliar", tags=["Conciliação Automática Inter"])

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")


def _get_conn():
    return psycopg2.connect(DATABASE_URL)


# ── MODELOS ────────────────────────────────────────────────────────────────────


class JustificativaPayload(BaseModel):
    justificativa: str
    categoria: str | None = None
    responsavel: str | None = None


# ── POST /conciliar/auto ────────────────────────────────────────────────────────


@router.post(
    "/auto",
    summary="Conciliação automática — Inter extrato × contas a pagar/receber",
    description="Matching por valor (±R$0,01 ou ±2%) + data (±3 ou ±7 dias). "
    "Saídas sem match → requires_justification = True.",
)
async def conciliacao_automatica(
    limite: int = Query(649, ge=1, le=2000),
    _user: dict = Depends(get_current_user),
):
    """Concilia até `limite` transações bancárias pendentes."""
    from modules.financial.services.reconciliation_service import conciliar_todas

    resultado = conciliar_todas(limite)
    return {"status": "ok", "resultado": resultado}


# ── POST /conciliar/{tx_id} ─────────────────────────────────────────────────────


@router.post(
    "/{tx_id}",
    summary="Conciliar transação específica",
)
async def conciliar_transacao_endpoint(
    tx_id: str,
    _user: dict = Depends(get_current_user),
):
    """Tenta conciliar uma transação bancária específica pelo ID."""
    from modules.financial.services.reconciliation_service import conciliar_transacao

    conn = _get_conn()
    try:
        resultado = conciliar_transacao(tx_id, conn)
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        conn.close()
    return resultado


# ── GET /conciliar/pendentes ────────────────────────────────────────────────────


@router.get(
    "/pendentes",
    summary="Listar transações sem conciliação ou aguardando justificativa",
)
async def listar_pendentes(
    limite: int = Query(50, ge=1, le=200),
    apenas_sem_justificativa: bool = Query(False),
    _user: dict = Depends(get_current_user),
):
    """Lista transações bancárias ainda não conciliadas."""
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cond = "reconciliation_status != 'conciliado'"
    if apenas_sem_justificativa:
        cond += " AND (requires_justification = TRUE AND justificativa IS NULL)"

    cur.execute(
        f"""
        SELECT id, transaction_date, transaction_type, amount, description,
               reconciliation_status, requires_justification,
               justificativa, justificativa_categoria
        FROM bank_transactions
        WHERE {cond}
        ORDER BY transaction_date DESC
        LIMIT %s
        """,  # noqa: S608
        (limite,),
    )
    rows = [dict(r) for r in cur.fetchall()]

    # Contagem de pendentes requerendo justificativa
    cur.execute(
        "SELECT COUNT(*) AS qtd FROM bank_transactions WHERE requires_justification = TRUE AND justificativa IS NULL"
    )
    sem_just = cur.fetchone()["qtd"]

    conn.close()
    return {
        "total": len(rows),
        "sem_justificativa_pendente": sem_just,
        "transacoes": rows,
    }


# ── POST /conciliar/{tx_id}/justificar ─────────────────────────────────────────


@router.post(
    "/{tx_id}/justificar",
    summary="Registrar justificativa para saída sem nota fiscal",
)
async def justificar_transacao(
    tx_id: str,
    payload: JustificativaPayload,
    _user: dict = Depends(get_current_user),
):
    """
    Registra justificativa para débito sem nota fiscal vinculada.
    Exemplos de categoria: 'despesa_pessoal', 'adiantamento', 'erro_operacional',
    'reembolso', 'taxa_bancaria', 'outros'.
    """
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE bank_transactions SET
            justificativa = %s,
            justificativa_categoria = %s,
            justificativa_responsavel = %s,
            justificativa_data = NOW(),
            reconciliation_status = 'justificado',
            updated_at = NOW()
        WHERE id = %s
          AND requires_justification = TRUE
        RETURNING id
        """,
        (payload.justificativa, payload.categoria, payload.responsavel, tx_id),
    )
    updated = cur.fetchone()
    conn.commit()
    conn.close()

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Transação não encontrada ou não requer justificativa",
        )
    return {
        "status": "justificado",
        "tx_id": tx_id,
        "justificativa": payload.justificativa,
        "categoria": payload.categoria,
    }


# ── GET /conciliar/relatorio ────────────────────────────────────────────────────


@router.get(
    "/relatorio",
    summary="Resumo da conciliação bancária",
)
async def relatorio_conciliacao(
    _user: dict = Depends(get_current_user),
):
    """Retorna estatísticas completas da conciliação Inter × notas."""
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(
        """
        SELECT
            COUNT(*) AS total_transacoes,
            COUNT(*) FILTER (WHERE reconciliation_status = 'conciliado') AS conciliadas,
            COUNT(*) FILTER (WHERE reconciliation_status = 'pendente') AS pendentes,
            COUNT(*) FILTER (WHERE reconciliation_status = 'justificado') AS justificadas,
            COUNT(*) FILTER (WHERE requires_justification = TRUE AND justificativa IS NULL) AS aguardando_justificativa,
            SUM(ABS(amount)) FILTER (WHERE reconciliation_status = 'conciliado') AS valor_conciliado,
            SUM(ABS(amount)) FILTER (WHERE reconciliation_status = 'pendente') AS valor_pendente,
            SUM(ABS(amount)) FILTER (WHERE transaction_type = 'debit') AS total_debitos,
            SUM(ABS(amount)) FILTER (WHERE transaction_type = 'credit') AS total_creditos
        FROM bank_transactions
        """
    )
    stats = dict(cur.fetchone())

    cur.execute(
        """
        SELECT status, COUNT(*), SUM(gross_value)
        FROM payable_accounts
        GROUP BY status ORDER BY COUNT(*) DESC
        """
    )
    payables = [dict(r) for r in cur.fetchall()]

    cur.execute(
        """
        SELECT status, COUNT(*), SUM(gross_value)
        FROM receivable_accounts
        GROUP BY status ORDER BY COUNT(*) DESC
        """
    )
    receivables = [dict(r) for r in cur.fetchall()]

    total = stats["total_transacoes"] or 1
    conn.close()

    return {
        "resumo": {
            **stats,
            "taxa_conciliacao_pct": round(float(stats.get("conciliadas") or 0) / float(total) * 100, 1),
        },
        "payable_accounts": payables,
        "receivable_accounts": receivables,
    }
