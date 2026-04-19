"""Backfill doc_scope + condominio_id + referente_a_employee_id — FASE 3.5 BLOCO 2

INV-4: Idempotente — re-rodar não duplica nem perde informação.
INV-5: Commits incrementais a cada BATCH_SIZE=50 docs.
INV-8: Aborta se >10% dos docs ficarem com doc_scope NULL.
"""

import sys

sys.path.insert(0, "/app")

from collections import Counter

from sqlalchemy import text

from core.database.session import SyncSessionLocal
from modules.gedeon.services.onvio_doc_scope_classifier import OnvioDocScopeClassifier

BATCH_SIZE = 50


def backfill(dry_run: bool = False) -> None:
    db = SyncSessionLocal()
    classifier = OnvioDocScopeClassifier(db)
    stats: Counter = Counter()
    revisao_list: list[tuple[str, str]] = []

    try:
        # Usar raw SQL (doc_scope/condominio_id não estão no ORM model — adicionados via migration BLOCO 1)
        rows = db.execute(
            text("SELECT id, categoria, nome_arquivo FROM onvio_documents ORDER BY data_importado")
        ).fetchall()
        total = len(rows)
        pending: list[dict] = []

        print(f"\n{'=' * 60}")
        print(f"🔍 Backfill FASE 3.5 BLOCO 2 — {total} docs")
        print(f"   dry_run={dry_run}  BATCH_SIZE={BATCH_SIZE}")
        print(f"{'=' * 60}\n")

        for i, row in enumerate(rows):
            result = classifier.classify(row.categoria or "outros", row.nome_arquivo)
            stats[result.doc_scope] += 1
            if result.revisao_manual:
                stats["revisao_manual"] += 1
                revisao_list.append((row.nome_arquivo, result.motivo))

            if not dry_run:
                pending.append(
                    {
                        "id": str(row.id),
                        "doc_scope": result.doc_scope,
                        "condominio_id": str(result.condominio_id) if result.condominio_id else None,
                        "referente_a_employee_id": str(result.referente_a_employee_id)
                        if result.referente_a_employee_id
                        else None,
                        "revisao_manual": result.revisao_manual,
                    }
                )

            if not dry_run and len(pending) >= BATCH_SIZE:
                db.execute(
                    text("""
                        UPDATE onvio_documents SET
                            doc_scope = :doc_scope,
                            condominio_id = CAST(:condominio_id AS uuid),
                            referente_a_employee_id = CAST(:referente_a_employee_id AS uuid),
                            revisao_manual = :revisao_manual
                        WHERE id = CAST(:id AS uuid)
                    """),
                    pending,
                )
                db.commit()
                lote = (i + 1) // BATCH_SIZE
                total_lotes = (total + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"  ✓ Lote {lote}/{total_lotes} commitado ({i + 1} docs)")
                pending.clear()

        if not dry_run and pending:
            db.execute(
                text("""
                    UPDATE onvio_documents SET
                        doc_scope = :doc_scope,
                        condominio_id = CAST(:condominio_id AS uuid),
                        referente_a_employee_id = CAST(:referente_a_employee_id AS uuid),
                        revisao_manual = :revisao_manual
                    WHERE id = CAST(:id AS uuid)
                """),
                pending,
            )
            db.commit()
            print(f"  ✓ Lote final commitado ({total} docs)")

        # ── Relatório ──────────────────────────────────────────────
        print(f"\n{'=' * 60}")
        print(f"📊 RELATÓRIO BACKFILL (total {total} docs, dry_run={dry_run})")
        print(f"{'=' * 60}")
        print(f"  empresa_matriz : {stats['empresa_matriz']}")
        print(f"  condominio     : {stats['condominio']}")
        print(f"  funcionario    : {stats['funcionario']}")
        print(f"  revisao_manual : {stats['revisao_manual']}  (flag — não é um escopo)")

        total_cls = stats["empresa_matriz"] + stats["condominio"] + stats["funcionario"]
        pct_revisao = stats["revisao_manual"] / total * 100 if total else 0
        print(f"\n  Total classificados : {total_cls}/{total}")
        print(f"  Taxa revisão manual : {pct_revisao:.1f}%")

        # Verificação INV-8 (doc_scope NULL)
        if not dry_run:
            null_count = db.execute(text("SELECT COUNT(*) FROM onvio_documents WHERE doc_scope IS NULL")).scalar()
            print(f"  doc_scope NULL após : {null_count}")
            if null_count > 0:
                print(f"\n⛔ INV-8 VIOLADO: {null_count} docs com doc_scope NULL. ABORTAR.")
                sys.exit(1)
            else:
                print("  ✅ INV-8 OK — zero doc_scope NULL")

        if pct_revisao > 10:
            print(f"\n⚠️  Revisão manual: {pct_revisao:.1f}% (>10%). Verificar com Jordan.")

        if revisao_list:
            print(f"\n⚠️  {len(revisao_list)} docs em revisão manual (primeiros 15):")
            for arq, motivo in revisao_list[:15]:
                print(f"  - {arq[:70]}: {motivo[:60]}")

    finally:
        db.close()


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    backfill(dry_run=dry_run)
