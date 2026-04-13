"""
Auto-sync: bank_transactions → cashflow_entries
Sincroniza novas transações do Inter automaticamente.
"""

import os
import uuid

import psycopg2
from psycopg2.extras import execute_batch

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/conecta_pro").replace(
    "+asyncpg", ""
)

_INSERT_SQL = """
    INSERT INTO cashflow_entries (
        id, condominio_id, bank_account_id,
        entry_type, source_type,
        description, category,
        entry_date, expected_amount,
        realized_date, realized_amount,
        status, bank_transaction_id,
        is_transfer, counterparty_name,
        memo, notes,
        tags, created_at, updated_at, ativo
    ) VALUES (
        %(id)s, %(condominio_id)s, %(bank_account_id)s,
        %(entry_type)s, %(source_type)s,
        %(description)s, %(category)s,
        %(entry_date)s, %(expected_amount)s,
        %(realized_date)s, %(realized_amount)s,
        %(status)s, %(bank_tx_id)s,
        %(is_transfer)s, %(counterparty_name)s,
        %(memo)s, %(notes)s,
        '[]'::jsonb, NOW(), NOW(), true
    )
    ON CONFLICT (bank_transaction_id) DO NOTHING
"""

_FETCH_PENDING_SQL = """
    SELECT
        bt.id, bt.bank_account_id, bt.transaction_type,
        bt.amount, bt.description, bt.transaction_date,
        bt.status, bt.is_transfer,
        bt.payable_payment_id, bt.receivable_payment_id,
        bt.counterparty_name, bt.memo, bt.notes,
        c.id as condominio_id
    FROM bank_transactions bt
    LEFT JOIN cashflow_entries ce ON ce.bank_transaction_id = bt.id
    JOIN bank_accounts ba ON ba.id = bt.bank_account_id
    JOIN condominiums c ON c.id = ba.condominio_id
    WHERE ce.id IS NULL
      AND bt.ativo = true
    ORDER BY bt.transaction_date ASC
    LIMIT %(limit)s
"""


def _map_category(desc: str, entry_type: str) -> str:
    """Deriva categoria correta por entry_type + descrição."""
    d = (desc or "").lower()
    if entry_type == "entrada":
        return "pix_recebido" if ("pix recebido" in d or ("pix" in d and "pix enviado" not in d)) else "receita"
    # Saída — prioridade por keywords
    if "pix enviado interno" in d:
        return "transferencia_interna"
    if "saque" in d:
        return "retirada_caixa"
    if any(x in d for x in ("tarifa", "taxa", "iof")):
        return "taxa_bancaria"
    if any(x in d for x in ("salario", "folha", "solides")):
        return "folha_pagamento"
    if any(x in d for x in ("darf", "imposto", " das ", "inss", "fgts", "irrf")):
        return "impostos"
    if any(x in d for x in ("saude", "unimed", "convenio", "plano")):
        return "beneficios"
    if "cef matriz" in d or "caixa fed" in d:
        return "fgts"
    if any(x in d for x in ("energia", "aluguel", "internet", "telefon")):
        return "operacional"
    if any(x in d for x in ("fornec", "compra")):
        return "fornecedores"
    if "pix enviado" in d:
        return "pix_enviado"
    return "despesa_operacional"


def _map_row(row: tuple) -> dict | None:
    """Converte linha de bank_transactions em dict para inserção."""
    (
        tx_id,
        bank_acct_id,
        tx_type,
        amount,
        description,
        tx_date,
        tx_status,
        is_transfer,
        payable_pid,
        receivable_pid,
        counterparty,
        memo,
        notes,
        condominio_id,
    ) = row

    try:
        tt = (tx_type or "").lower()
        if tt in ("credito", "credit") or (amount is not None and float(amount) > 0):
            entry_type = "entrada"
        else:
            entry_type = "saida"

        if is_transfer:
            source_type = "transferencia"
        elif payable_pid:
            source_type = "conta_pagar"
        elif receivable_pid:
            source_type = "conta_receber"
        else:
            source_type = "manual"

        st = (tx_status or "").lower()
        if st == "confirmado":
            cf_status = "realizado"
        elif st == "pendente":
            cf_status = "previsto"
        else:
            cf_status = "confirmado"

        valor = abs(float(amount)) if amount is not None else 0.01
        if valor == 0:
            valor = 0.01
        desc = (description or memo or notes or f"Transação {tx_id}")[:500]

        return {
            "id": str(uuid.uuid4()),
            "condominio_id": str(condominio_id),
            "bank_account_id": str(bank_acct_id) if bank_acct_id else None,
            "entry_type": entry_type,
            "source_type": source_type,
            "description": desc,
            "category": _map_category(desc, entry_type),
            "entry_date": tx_date,
            "expected_amount": valor,
            "realized_date": tx_date,
            "realized_amount": valor,
            "status": cf_status,
            "bank_tx_id": str(tx_id),
            "is_transfer": bool(is_transfer),
            "counterparty_name": counterparty,
            "memo": memo,
            "notes": notes,
        }
    except Exception:
        return None


def run_full_sync(limit: int = 500) -> dict:
    """
    Sincroniza bank_transactions pendentes → cashflow_entries.
    Idempotente: ON CONFLICT (bank_transaction_id) DO NOTHING.
    Retorna: {"pending": N, "synced": N, "errors": N}
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(_FETCH_PENDING_SQL, {"limit": limit})
    rows = cur.fetchall()
    pending = len(rows)

    if not rows:
        cur.close()
        conn.close()
        return {"pending": 0, "synced": 0, "errors": 0}

    mapped = [_map_row(r) for r in rows]
    good = [m for m in mapped if m is not None]
    errors = pending - len(good)

    try:
        execute_batch(cur, _INSERT_SQL, good, page_size=100)
        conn.commit()
        synced = len(good)
    except Exception:
        conn.rollback()
        synced = 0
        for row_dict in good:
            try:
                cur.execute(_INSERT_SQL, row_dict)
                conn.commit()
                synced += 1
            except Exception:
                conn.rollback()
                errors += 1

    cur.close()
    conn.close()
    return {"pending": pending, "synced": synced, "errors": errors}


def sync_single_transaction(bank_transaction_id: str) -> bool:
    """
    Sincroniza uma transação específica (chamado após webhook/save).
    Retorna True se inserida, False se já existia ou erro.
    """
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            bt.id, bt.bank_account_id, bt.transaction_type,
            bt.amount, bt.description, bt.transaction_date,
            bt.status, bt.is_transfer,
            bt.payable_payment_id, bt.receivable_payment_id,
            bt.counterparty_name, bt.memo, bt.notes,
            c.id as condominio_id
        FROM bank_transactions bt
        JOIN bank_accounts ba ON ba.id = bt.bank_account_id
        JOIN condominiums c ON c.id = ba.condominio_id
        WHERE bt.id = %s::uuid
        """,
        (bank_transaction_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return False

    row_dict = _map_row(row)
    if not row_dict:
        cur.close()
        conn.close()
        return False

    try:
        cur.execute(_INSERT_SQL, row_dict)
        conn.commit()
        inserted = cur.rowcount > 0
    except Exception:
        conn.rollback()
        inserted = False

    cur.close()
    conn.close()
    return inserted


if __name__ == "__main__":
    result = run_full_sync()
    print(f"Sync result: {result}")
