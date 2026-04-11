"""
Reconciliation Service — Conciliação Bancária Automática Inter × Notas
Faz matching: transação Inter ↔ conta a pagar/receber

Regras de matching (em cascata):
1. Valor exato (tolerância R$0,01) + CNPJ da contraparte + data ±3 dias
2. Valor exato + data ±3 dias (sem CNPJ)
3. Valor ±2% + data ±7 dias (flexível)

Saídas sem match → flag requires_justification = True

Colunas reais usadas:
  bank_transactions: transaction_type, amount, transaction_date,
                     reconciliation_status, reconciliation_id
  payable_accounts:  gross_value, due_date, status, payment_date, paid_at
  receivable_accounts: gross_value, due_date, status, payment_date
"""

import logging
import os
from datetime import timedelta
from decimal import Decimal

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")
TOLERANCE = Decimal("0.01")
TOLERANCE_PCT = Decimal("0.02")  # 2% para matching flexível
DATE_WINDOW = 3  # dias para matching exato
DATE_WINDOW_FLEX = 7  # dias para matching flexível


def _get_conn():
    return psycopg2.connect(DATABASE_URL)


def conciliar_transacao(tx_id: str, conn) -> dict:
    """
    Tenta conciliar uma transação bancária específica.
    Retorna dict com status, tipo_match e referência conciliada.
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(
        """
        SELECT id, transaction_date, transaction_type, amount, description,
               reconciliation_status, reconciliation_id
        FROM bank_transactions
        WHERE id = %s
        """,
        (tx_id,),
    )
    tx = cur.fetchone()
    if not tx:
        return {"erro": "Transação não encontrada"}

    if tx["reconciliation_status"] in ("conciliado", "justificado"):
        return {"status": "ja_conciliado", "reconciliation_id": str(tx["reconciliation_id"] or "")}

    valor_abs = abs(Decimal(str(tx["amount"])))
    tx_date = tx["transaction_date"]
    tx_type = tx["transaction_type"]  # 'debit' | 'credit'
    descricao = tx["description"] or ""

    data_min = tx_date - timedelta(days=DATE_WINDOW)
    data_max = tx_date + timedelta(days=DATE_WINDOW)
    data_min_flex = tx_date - timedelta(days=DATE_WINDOW_FLEX)
    data_max_flex = tx_date + timedelta(days=DATE_WINDOW_FLEX)

    # ── DÉBITO → buscar em payable_accounts ──────────────────────────────────
    if tx_type == "debit":
        # Estratégia 1+2: valor exato ±R$0,01, data ±3 dias
        cur.execute(
            """
            SELECT id, description, gross_value, net_value, due_date, status
            FROM payable_accounts
            WHERE status = 'pendente'
              AND ABS(gross_value - %s) <= %s
              AND due_date BETWEEN %s AND %s
            ORDER BY ABS(gross_value - %s)
            LIMIT 1
            """,
            (float(valor_abs), float(TOLERANCE), data_min, data_max, float(valor_abs)),
        )
        match = cur.fetchone()
        tipo_match = "valor_exato_data"

        # Estratégia 3: valor ±2%, data ±7 dias
        if not match:
            margem = float(valor_abs * TOLERANCE_PCT)
            cur.execute(
                """
                SELECT id, description, gross_value, net_value, due_date, status
                FROM payable_accounts
                WHERE status = 'pendente'
                  AND ABS(gross_value - %s) <= %s
                  AND due_date BETWEEN %s AND %s
                ORDER BY ABS(gross_value - %s)
                LIMIT 1
                """,
                (float(valor_abs), margem, data_min_flex, data_max_flex, float(valor_abs)),
            )
            match = cur.fetchone()
            tipo_match = "valor_flex_2pct"

        if match:
            pay_id = match["id"]
            # Marcar transação como conciliada
            cur.execute(
                """
                UPDATE bank_transactions SET
                    reconciliation_status = 'conciliado',
                    reconciliation_id = %s,
                    reconciled_at = %s,
                    requires_justification = FALSE,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (pay_id, tx_date, tx_id),
            )
            # Marcar payable como pago
            cur.execute(
                """
                UPDATE payable_accounts SET
                    status = 'pago',
                    payment_date = %s,
                    paid_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
                """,
                (tx_date, str(pay_id)),
            )
            conn.commit()
            return {
                "status": "conciliado",
                "tipo": "debito_payable",
                "match": tipo_match,
                "payable_id": str(pay_id),
                "payable_desc": match["description"],
                "valor_tx": float(valor_abs),
                "valor_payable": float(match["gross_value"]),
            }
        else:
            # Débito sem match → marcar para justificativa
            cur.execute(
                """
                UPDATE bank_transactions SET
                    requires_justification = TRUE,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (tx_id,),
            )
            conn.commit()
            return {
                "status": "sem_match",
                "tipo": "debito_sem_nota",
                "requires_justification": True,
                "valor": float(valor_abs),
                "descricao": descricao,
            }

    # ── CRÉDITO → buscar em receivable_accounts ───────────────────────────────
    elif tx_type == "credit":
        cur.execute(
            """
            SELECT id, description, gross_value, net_value, due_date, status
            FROM receivable_accounts
            WHERE status = 'pendente'
              AND ABS(gross_value - %s) <= %s
              AND due_date BETWEEN %s AND %s
            ORDER BY ABS(gross_value - %s)
            LIMIT 1
            """,
            (float(valor_abs), float(TOLERANCE), data_min, data_max, float(valor_abs)),
        )
        match = cur.fetchone()
        tipo_match = "valor_exato_data"

        if not match:
            margem = float(valor_abs * TOLERANCE_PCT)
            cur.execute(
                """
                SELECT id, description, gross_value, net_value, due_date, status
                FROM receivable_accounts
                WHERE status = 'pendente'
                  AND ABS(gross_value - %s) <= %s
                  AND due_date BETWEEN %s AND %s
                ORDER BY ABS(gross_value - %s)
                LIMIT 1
                """,
                (float(valor_abs), margem, data_min_flex, data_max_flex, float(valor_abs)),
            )
            match = cur.fetchone()
            tipo_match = "valor_flex_2pct"

        if match:
            rec_id = match["id"]
            cur.execute(
                """
                UPDATE bank_transactions SET
                    reconciliation_status = 'conciliado',
                    reconciliation_id = %s,
                    reconciled_at = %s,
                    requires_justification = FALSE,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (rec_id, tx_date, tx_id),
            )
            cur.execute(
                """
                UPDATE receivable_accounts SET
                    status = 'recebido',
                    payment_date = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (tx_date, str(rec_id)),
            )
            conn.commit()
            return {
                "status": "conciliado",
                "tipo": "credito_receivable",
                "match": tipo_match,
                "receivable_id": str(rec_id),
                "receivable_desc": match["description"],
                "valor_tx": float(valor_abs),
                "valor_receivable": float(match["gross_value"]),
            }

    return {"status": "tipo_nao_processado", "tipo": tx_type}


def conciliar_todas(limite: int = 649) -> dict:
    """
    Concilia todas as transações não reconciliadas.
    Inclui as marcadas como requires_justification=TRUE para dar nova chance de match.
    """
    conn = _get_conn()
    cur = conn.cursor()

    # Busca TODAS as pendentes (inclusive as com requires_justification=TRUE
    # que podem ter match com payables agora)
    cur.execute(
        """
        SELECT id FROM bank_transactions
        WHERE reconciliation_status NOT IN ('conciliado', 'justificado')
        ORDER BY transaction_date DESC
        LIMIT %s
        """,
        (limite,),
    )
    tx_ids = [str(r[0]) for r in cur.fetchall()]
    cur.close()

    total = len(tx_ids)
    conciliados = 0
    sem_match = 0
    erros = 0
    detalhes: list[dict] = []

    for tx_id in tx_ids:
        try:
            resultado = conciliar_transacao(tx_id, conn)
            st = resultado.get("status", "")
            if st == "conciliado":
                conciliados += 1
            elif st == "sem_match":
                sem_match += 1
                detalhes.append(resultado)
        except Exception as exc:
            erros += 1
            logger.error("Erro conciliação %s: %s", tx_id, exc)
            try:
                conn.rollback()
            except Exception:
                pass

    conn.close()
    return {
        "processadas": total,
        "conciliadas": conciliados,
        "sem_match_requer_justificativa": sem_match,
        "erros": erros,
        "taxa_conciliacao_pct": round(conciliados / max(1, total) * 100, 1),
        "sem_match_detalhes": detalhes[:10],
    }
