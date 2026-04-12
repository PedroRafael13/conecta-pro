"""
Sync retroativo: bank_transactions → cashflow_entries
Mapeamento baseado na estrutura real da tabela.
"""

import os
import sys
import uuid

sys.path.insert(0, "/opt/conecta-pro/backend")

import psycopg2
from psycopg2.extras import execute_batch

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/conecta_pro").replace(
    "+asyncpg", ""
)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Condominio padrão (único)
cur.execute("SELECT id FROM condominiums LIMIT 1")
row = cur.fetchone()
CONDOMINIO_ID = str(row[0]) if row else "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
print(f"condominio_id: {CONDOMINIO_ID}")

# Contagem antes
cur.execute("SELECT count(*) FROM cashflow_entries")
antes = cur.fetchone()[0]
print(f"cashflow_entries antes: {antes}")

# Buscar bank_transactions sem cashflow vinculado
cur.execute("""
    SELECT
        bt.id, bt.bank_account_id, bt.transaction_type,
        bt.amount, bt.description, bt.transaction_date,
        bt.category, bt.status, bt.is_transfer,
        bt.payable_payment_id, bt.receivable_payment_id,
        bt.counterparty_name, bt.memo, bt.notes
    FROM bank_transactions bt
    LEFT JOIN cashflow_entries ce ON ce.bank_transaction_id = bt.id
    WHERE ce.id IS NULL
      AND bt.ativo = true
    ORDER BY bt.transaction_date ASC
""")
txs = cur.fetchall()
print(f"bank_transactions sem sync: {len(txs)}")

if not txs:
    print("Nada para sincronizar.")
    sys.exit(0)

INSERT_SQL = """
    INSERT INTO cashflow_entries (
        id, condominio_id, bank_account_id,
        entry_type, source_type,
        description, category,
        entry_date, expected_amount,
        realized_date, realized_amount,
        status, bank_transaction_id,
        is_transfer, counterparty_name,
        memo, notes,
        created_at, updated_at, ativo
    ) VALUES (
        %(id)s, %(condominio_id)s, %(bank_account_id)s,
        %(entry_type)s, %(source_type)s,
        %(description)s, %(category)s,
        %(entry_date)s, %(expected_amount)s,
        %(realized_date)s, %(realized_amount)s,
        %(status)s, %(bank_tx_id)s,
        %(is_transfer)s, %(counterparty_name)s,
        %(memo)s, %(notes)s,
        NOW(), NOW(), true
    )
    ON CONFLICT DO NOTHING
"""

rows = []
errors = 0

for tx in txs:
    (
        tx_id,
        bank_acct_id,
        tx_type,
        amount,
        description,
        tx_date,
        category,
        tx_status,
        is_transfer,
        payable_pid,
        receivable_pid,
        counterparty,
        memo,
        notes,
    ) = tx

    try:
        # entry_type
        tt = (tx_type or "").lower()
        if tt in ("credito", "credit") or (amount is not None and float(amount) > 0):
            entry_type = "entrada"
        else:
            entry_type = "saida"

        # source_type
        if is_transfer:
            source_type = "transferencia"
        elif payable_pid:
            source_type = "conta_pagar"
        elif receivable_pid:
            source_type = "conta_receber"
        else:
            source_type = "manual"

        # status mapping
        if (tx_status or "").lower() == "confirmado":
            cf_status = "realizado"
        elif (tx_status or "").lower() == "pendente":
            cf_status = "previsto"
        else:
            cf_status = "confirmado"

        valor = abs(float(amount)) if amount is not None else 0.0
        desc = (description or memo or notes or f"Transação {tx_id}")[:500]

        # Derivar categoria correta por entry_type — nunca usar bt.category diretamente
        # (o Inter classifica tudo como 'receita', independente de ser entrada ou saída)
        desc_lower = desc.lower()
        if entry_type == "entrada":
            mapped_category = (
                "pix_recebido"
                if "pix recebido" in desc_lower or "pix enviado" not in desc_lower and "pix" in desc_lower
                else "receita"
            )
        elif "pix enviado interno" in desc_lower:
            mapped_category = "transferencia_interna"
        elif "saque" in desc_lower:
            mapped_category = "retirada_caixa"
        elif "tarifa" in desc_lower or "taxa" in desc_lower or "iof" in desc_lower:
            mapped_category = "taxa_bancaria"
        elif any(x in desc_lower for x in ("salario", "folha", "solides")):
            mapped_category = "folha_pagamento"
        elif any(x in desc_lower for x in ("darf", "imposto", " das ", "inss", "fgts", "irrf")):
            mapped_category = "impostos"
        elif any(x in desc_lower for x in ("saude", "unimed", "convenio", "plano")):
            mapped_category = "beneficios"
        elif "cef matriz" in desc_lower or "caixa fed" in desc_lower:
            mapped_category = "fgts"
        elif "pix enviado" in desc_lower:
            mapped_category = "pix_enviado"
        else:
            mapped_category = "despesa_operacional"

        rows.append(
            {
                "id": str(uuid.uuid4()),
                "condominio_id": CONDOMINIO_ID,
                "bank_account_id": str(bank_acct_id) if bank_acct_id else None,
                "entry_type": entry_type,
                "source_type": source_type,
                "description": desc,
                "category": mapped_category,
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
        )
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"  Mapeamento erro {tx_id}: {e}")

# Inserção em batch
try:
    execute_batch(cur, INSERT_SQL, rows, page_size=100)
    conn.commit()
except Exception as e:
    conn.rollback()
    print(f"Erro no batch: {e}")
    # Tentar um por um
    inserted_ok = 0
    for row in rows:
        try:
            cur.execute(INSERT_SQL, row)
            conn.commit()
            inserted_ok += 1
        except Exception as e2:
            conn.rollback()
            errors += 1
            if errors <= 5:
                print(f"  Erro individual: {e2}")
    print(f"Fallback individual: {inserted_ok} OK")

cur.execute("SELECT count(*) FROM cashflow_entries")
depois = cur.fetchone()[0]

print("\n=== RESULTADO ===")
print(f"Antes:     {antes}")
print(f"Mapeados:  {len(rows)}")
print(f"Erros:     {errors}")
print(f"Depois:    {depois}")
print(f"Inseridos: {depois - antes}")

cur.close()
conn.close()
