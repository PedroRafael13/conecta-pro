"""
Popular accounting_entries com lançamentos retroativos reais.
Fonte: nfses (27 notas) + bank_transactions Inter
Plano de contas simplificado Conecta Mais (Lucro Real).
Idempotente: usa ON CONFLICT DO NOTHING + LEFT JOIN anti-duplicata.
"""

import os
import sys

sys.path.insert(0, "/opt/conecta-pro/backend")
from datetime import datetime

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/conecta_pro")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    existing = conn.execute(text("SELECT count(*) FROM accounting_entries")).scalar()
    print(f"accounting_entries atual: {existing}")

    inserted = 0

    # ── Lançamentos por NFS-e emitida (receita de serviços) ───────────────────
    try:
        nfses = conn.execute(
            text("""
                SELECT id, numero_nfse, valor_servicos, data_emissao, tomador_razao_social
                FROM nfses
                WHERE status = 'autorizada'
                ORDER BY data_emissao
            """)
        ).fetchall()

        for nf in nfses:
            valor = float(getattr(nf, "valor_servicos", 0) or 0)
            if valor <= 0:
                continue
            conn.execute(
                text("""
                    INSERT INTO accounting_entries
                        (data_lancamento, conta_debito, conta_credito, valor,
                         historico, tipo_lancamento, documento_ref,
                         nfse_id, periodo_competencia, status)
                    VALUES
                        (:data, '1.1.3.01', '3.1.1.01', :valor,
                         :hist, 'nfse_emitida', :doc,
                         :nfse_id, :periodo, 'confirmado')
                    ON CONFLICT DO NOTHING
                """),
                {
                    "data": getattr(nf, "data_emissao", datetime.now().date()),
                    "valor": valor,
                    "hist": (
                        f"NFS-e {getattr(nf, 'numero_nfse', '')} - {str(getattr(nf, 'tomador_razao_social', ''))[:50]}"
                    ),
                    "doc": f"NFSE-{getattr(nf, 'numero_nfse', '')}",
                    "nfse_id": nf.id,
                    "periodo": str(getattr(nf, "data_emissao", datetime.now().date()))[:7],
                },
            )
            inserted += 1

        print(f"Lançamentos NFS-e: {len(nfses)} notas → {inserted} inseridos")
    except Exception as e:
        print(f"NFS-e erro: {e}")

    # ── Lançamentos por bank_transactions (créditos/débitos Inter) ────────────
    inserted_bt = 0
    try:
        txs = conn.execute(
            text("""
                SELECT bt.id, bt.transaction_date, bt.amount, bt.transaction_type,
                       bt.description
                FROM bank_transactions bt
                LEFT JOIN accounting_entries ae ON ae.bank_transaction_id = bt.id
                WHERE ae.id IS NULL
                ORDER BY bt.transaction_date
                LIMIT 200
            """)
        ).fetchall()

        for tx in txs:
            amount = float(getattr(tx, "amount", 0) or 0)
            if amount == 0:
                continue
            tipo_str = str(getattr(tx, "transaction_type", "") or "").upper()
            is_credit = amount > 0 or tipo_str in ("CREDIT", "CREDITO", "ENTRADA")
            conta_d = "1.1.1.01" if is_credit else "3.2.1.01"
            conta_c = "3.1.1.01" if is_credit else "1.1.1.01"
            desc = str(getattr(tx, "description", "") or "Transação Inter")[:200]
            data_tx = getattr(tx, "transaction_date", datetime.now().date())

            conn.execute(
                text("""
                    INSERT INTO accounting_entries
                        (data_lancamento, conta_debito, conta_credito, valor,
                         historico, tipo_lancamento, bank_transaction_id,
                         periodo_competencia, status)
                    VALUES
                        (:data, :cd, :cc, :valor,
                         :hist, 'banco_inter', :bt_id,
                         :periodo, 'confirmado')
                """),
                {
                    "data": data_tx,
                    "cd": conta_d,
                    "cc": conta_c,
                    "valor": abs(amount),
                    "hist": desc,
                    "bt_id": tx.id,
                    "periodo": str(data_tx)[:7],
                },
            )
            inserted_bt += 1

        conn.commit()
        total = conn.execute(text("SELECT count(*) FROM accounting_entries")).scalar()
        print(f"Lançamentos bank_transactions: {inserted_bt}")
        print(f"\nTotal accounting_entries: {total}")
    except Exception as e:
        print(f"bank_transactions erro: {e}")  # nosec B110
