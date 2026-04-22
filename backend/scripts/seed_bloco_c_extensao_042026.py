"""
Seed BLOCO C — extensão aos 9 condomínios restantes em 04/2026.

Reaproveita lógica do seed BLOCO B parametrizando por condomínio.

Regras:
- SKIP condomínios com 0 templates aplicáveis (ESCRITÓRIO)
- SKIP condomínios já com kit em 04/2026 (LARANJEIRAS — UUID 0107be85...)
- Idempotência via UNIQUE(client_id, reference_month)
- Eventuais sem PDF: NÃO insere (correção BLOCO B)
- Todos os docs: file_path=NULL (04/2026 ainda não sincronizado)

Mapeamento condominio_id → ged_client_id confirmado em STEP 1:
  Não há FK entre condominios e ged_clients — mapeamento hardcoded por UUID.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, "/app")
from core.database.session import SyncSessionLocal  # noqa: E402

# ── Constantes ───────────────────────────────────────────────────────────────
MES_REF = "04.2026"
REFERENCE_MONTH = "2026-04-01"
UPLOADS_ROOT = Path("/opt/conecta-pro/uploads")

# Mapping confirmado em STEP 1 (BLOCO C):
# condominio.nome_normalizado → (condominio.id, ged_clients.id)
CONDOMINIO_MAP: dict[str, tuple[str, str]] = {
    "prime_arena": (
        "21929c3d-f469-4eb4-8309-4d8201231100",
        "52958919-0a15-4e4f-806d-be3c75e5951b",
    ),
    "ideal_flores": (
        "215a124b-2dd7-4125-ab3f-6efa3aa67c99",
        "4db583b6-815a-494f-a1e3-0c62fa81eca9",
    ),
    "mirante": (
        "dfa6645a-5061-4b4d-b64a-aada36f2b732",
        "130186bf-9e37-4fba-bf19-817292df4ace",
    ),
    "villa_dei_fiori": (
        "ef2f9c03-e2d7-4a10-8458-e26c9a696f69",
        "14809ac8-f5e1-4dac-848c-4f5e0c347ecc",
    ),
    "villa_passaros": (
        "6fb88de2-4093-451f-b188-e60c318c0b2a",
        "4909237d-1003-41cd-a404-bcbe08f9c2cf",
    ),
    "michelangelo": (
        "b3ca559f-2728-4238-916e-5e303d70b4e6",
        "02d784d5-c150-479b-94fa-7f3615072e79",
    ),
    "green_hills": (
        "4900de33-c778-4792-818d-e0901b559aed",
        "b4a13504-cffc-4505-8e91-e1bebed493ed",
    ),
    "p_gelain": (
        "ab146423-859e-4e6e-aeaf-041987a18f25",
        "8199960d-42be-43ba-b0cb-ccf342bfb601",
    ),
    "parise": (
        "9be1e32b-0ff1-4668-9094-74f720c9a487",
        "d4dd6c53-222f-4c6d-a864-6d0856cd53d5",
    ),
    # LARANJEIRAS omitido — já tem kit do BLOCO B (UUID 0107be85...)
    # ESCRITÓRIO omitido — administrativo, 0 templates
}

SLUG_DISPLAY_NAMES: dict[str, str] = {
    "nfse": "NFS-e",
    "boleto": "Boleto",
    "folha_pagamento": "Folha de Pagamento",
    "contracheque": "Contracheque / Recibo de Folha",
    "folhas_ponto": "Folhas de Ponto",
    "gfd_fgts_mensal": "GFD FGTS Mensal",
    "relatorio_gfd_fgts": "Relatório GFD FGTS",
    "comp_pag_fgts": "Comprovante Pagamento FGTS",
    "gfd_fgts_rescisao": "GFD FGTS Rescisão",
    "relatorio_gfd_rescisao": "Relatório GFD Rescisão",
    "comp_fgts_rescisao": "Comprovante FGTS Rescisão",
    "dctfweb_declaracao": "DCTFWeb — Declaração Completa",
    "dctfweb_recibo": "DCTFWeb — Recibo",
    "dctfweb_extrato": "DCTFWeb — Extrato",
    "cnd_rfb": "CND Receita Federal",
    "cnd_caixa": "CND FGTS / Caixa Econômica",
    "cnd_prefeitura": "CND Prefeitura / Municipal",
    "cnd_sefaz": "CND Sefaz / Estadual",
    "cnd_trabalhista": "CND Trabalhista / TST",
    "comp_vt_individual": "Comprovante VT Individual",
    "comp_va_solides": "Comprovante VA Solides",
    "comp_vt_va_combinado": "Comprovante VT+VA Combinado",
    "recibo_vt_va": "Recibo VT/VA Geral",
    "relatorio_pedido_va": "Relatório Pedido VA",
    "aso": "ASO — Atestado de Saúde Ocupacional",
    "contrato_trabalho": "Contrato de Trabalho",
    "ficha_empregado": "Ficha de Registro do Empregado",
    "rescisao_contrato": "Rescisão de Contrato",
    "comp_rescisao": "Comprovante Pagamento Rescisão",
    "comp_salario_individual": "Comprovante Salário Individual",
    "aviso_previo_ferias": "Aviso Prévio / Férias",
    "recibo_ferias": "Recibo de Férias",
}


def find_pdf_for_template(slug: str, condominio_id: str, mes_ref: str, db) -> str | None:
    """Tenta localizar PDF via onvio_documents ou /uploads/. Retorna None se ausente."""
    row = db.execute(
        text(
            """
            SELECT od.caminho_local
            FROM onvio_documents od
            WHERE od.condominio_id = CAST(:cid AS uuid)
              AND od.mes_ref = :mes
              AND od.categoria = :slug
            LIMIT 1
            """
        ),
        {"cid": condominio_id, "mes": mes_ref, "slug": slug},
    ).fetchone()
    if row and row[0]:
        host_path = row[0].replace("/app/", "/opt/conecta-pro/", 1)
        if Path(host_path).exists():
            return host_path
    return None


def processar_condominio(db, nome_normalizado: str) -> dict:
    """
    Roda lógica do BLOCO B para 1 condomínio específico.
    Retorna dict com resultado: kit_id, docs_inseridos, skipped_reason.
    """
    condominio_id, ged_client_id = CONDOMINIO_MAP[nome_normalizado]

    # ── Idempotência ─────────────────────────────────────────────────────────
    existing = db.execute(
        text(
            "SELECT id FROM ged_document_kits "
            "WHERE client_id = CAST(:cid AS uuid) AND reference_month = CAST(:rm AS date)"
        ),
        {"cid": ged_client_id, "rm": REFERENCE_MONTH},
    ).fetchone()
    if existing:
        return {"kit_id": None, "docs_inseridos": 0, "skipped_reason": f"já existe (id={existing[0]})"}

    # ── Templates aplicáveis ──────────────────────────────────────────────────
    templates = db.execute(
        text(
            """
            SELECT t.id, t.num, t.slug, t.escopo, t.tipo_documento, p.presenca
            FROM kit_documental_templates t
            JOIN kit_template_presenca p ON p.template_id = t.id
            WHERE p.condominio_id = CAST(:cid AS uuid)
              AND p.presenca IN ('obrigatorio', 'eventual')
            ORDER BY t.num
            """
        ),
        {"cid": condominio_id},
    ).fetchall()

    if not templates:
        return {"kit_id": None, "docs_inseridos": 0, "skipped_reason": "0 templates aplicáveis"}

    # ── Funcionários ativos 04/2026 ───────────────────────────────────────────
    funcs = db.execute(
        text(
            """
            SELECT e.id, e.nome
            FROM employees e
            JOIN employee_alocacoes ea ON ea.employee_id = e.id
            WHERE ea.condominio_id = CAST(:cid AS uuid)
              AND (ea.data_fim IS NULL OR ea.data_fim >= '2026-04-01')
              AND ea.data_inicio <= '2026-04-30'
            ORDER BY e.nome
            """
        ),
        {"cid": condominio_id},
    ).fetchall()
    n_func = len(funcs)

    # ── Total esperado ────────────────────────────────────────────────────────
    total_obrig = sum(n_func if t[3] == "funcionario" else 1 for t in templates if t[5] == "obrigatorio")

    # ── Criar kit ─────────────────────────────────────────────────────────────
    kit_id = uuid.uuid4()
    db.execute(
        text(
            """
            INSERT INTO ged_document_kits
              (id, client_id, reference_month, status,
               total_employees, total_documents, documents_signed,
               completion_percentage, notes, created_at)
            VALUES (
              CAST(:id AS uuid), CAST(:cid AS uuid), CAST(:rm AS date),
              'em_montagem', :n_emp, :n_docs, 0, 0.0,
              'GEDEON BLOCO C — seed automático 2026-04-22', NOW()
            )
            """
        ),
        {
            "id": str(kit_id),
            "cid": ged_client_id,
            "rm": REFERENCE_MONTH,
            "n_emp": n_func,
            "n_docs": total_obrig,
        },
    )

    # ── Inserir documentos ────────────────────────────────────────────────────
    docs_inseridos = 0

    for tpl in templates:
        _, _, slug, escopo, _, presenca = tpl
        eh_eventual = presenca == "eventual"
        display_name = SLUG_DISPLAY_NAMES.get(slug, slug)

        if escopo == "funcionario":
            for func_id, func_nome in funcs:
                fp = find_pdf_for_template(slug, condominio_id, MES_REF, db)
                if eh_eventual and fp is None:
                    continue
                doc_name = f"{display_name} — {func_nome}" if fp else f"[PLACEHOLDER] {display_name} — {func_nome}"
                db.execute(
                    text(
                        """
                        INSERT INTO ged_kit_documents
                          (id, kit_id, employee_id, document_type, document_name,
                           file_path, is_signed, auto_generated, source_module, notes, created_at)
                        VALUES (
                          gen_random_uuid(), CAST(:kid AS uuid), CAST(:eid AS uuid),
                          :dtype, :dname, :fpath, false, true, 'gedeon', :notes, NOW()
                        )
                        """
                    ),
                    {
                        "kid": str(kit_id),
                        "eid": str(func_id),
                        "dtype": slug,
                        "dname": doc_name,
                        "fpath": fp,
                        "notes": None if fp else "PDF não localizado no servidor",
                    },
                )
                docs_inseridos += 1
        else:
            fp = find_pdf_for_template(slug, condominio_id, MES_REF, db)
            if eh_eventual and fp is None:
                continue
            doc_name = display_name if fp else f"[PLACEHOLDER] {display_name}"
            db.execute(
                text(
                    """
                    INSERT INTO ged_kit_documents
                      (id, kit_id, employee_id, document_type, document_name,
                       file_path, is_signed, auto_generated, source_module, notes, created_at)
                    VALUES (
                      gen_random_uuid(), CAST(:kid AS uuid), NULL,
                      :dtype, :dname, :fpath, false, true, 'gedeon', :notes, NOW()
                    )
                    """
                ),
                {
                    "kid": str(kit_id),
                    "dtype": slug,
                    "dname": doc_name,
                    "fpath": fp,
                    "notes": None if fp else "PDF não localizado no servidor",
                },
            )
            docs_inseridos += 1

    db.commit()
    return {"kit_id": str(kit_id), "docs_inseridos": docs_inseridos, "skipped_reason": None}


def main() -> None:
    db = SyncSessionLocal()
    try:
        print("=" * 70)
        print(f"GEDEON BLOCO C — Extensão 9 condomínios {MES_REF}")
        print("=" * 70)

        relatorio: list[dict] = []

        for nome in CONDOMINIO_MAP:
            print(f"\n▶ Processando: {nome}")
            resultado = processar_condominio(db, nome)
            resultado["condominio"] = nome
            relatorio.append(resultado)

            if resultado["skipped_reason"]:
                print(f"  ⏭  SKIP — {resultado['skipped_reason']}")
            else:
                print(f"  ✅ kit_id={resultado['kit_id']}")
                print(f"     docs inseridos: {resultado['docs_inseridos']}")

        # ── Relatório final ───────────────────────────────────────────────────
        print("\n" + "=" * 70)
        print("BLOCO C — RESUMO")
        print("=" * 70)
        kits_criados = sum(1 for r in relatorio if r["kit_id"])
        docs_total = sum(r["docs_inseridos"] for r in relatorio)
        skipped = sum(1 for r in relatorio if r["skipped_reason"])
        print(f"  Kits criados:    {kits_criados}")
        print(f"  Docs inseridos:  {docs_total}")
        print(f"  Skipped:         {skipped}")
        print(f"  Total kits 04/2026 (incluindo LARANJEIRAS): {kits_criados + 1}")
        print(f"  Total docs  04/2026 (incluindo LARANJEIRAS): {docs_total + 83}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
