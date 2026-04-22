"""
Seed do 1º kit real — LARANJEIRAS 04/2026.

Fonte de verdade: kit_documental_templates + kit_template_presenca (BLOCO A §35).
PDFs: prioriza onvio_documents (já classificado) e fallback /uploads/ (regex).

IDEMPOTÊNCIA: se kit LARANJEIRAS 04/2026 já existe, reporta e sai (não duplica).

Adaptações de schema:
  - ged_document_kits.client_id → ged_clients.id (não condominios.id)
  - ged_document_kits.reference_month → date '2026-04-01'
  - ged_kit_documents.notes → motivo_faltante (não há coluna dedicada)
  - ged_kit_documents.auto_generated = True (seeded por script)
  - ged_kit_documents.source_module = 'gedeon'
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, "/app")
from core.database.session import SyncSessionLocal  # noqa: E402

# ── Constantes ───────────────────────────────────────────────────────────────
GED_CLIENT_ID = "e55f6f4c-a641-4b08-9584-eef61dcb5575"  # RESIDENCIAL LARANJEIRAS VILLAGE
CONDOMINIO_ID = "7c2323fd-e226-4121-806d-d9b2598feeed"  # condominios.id
MES_REF = "04.2026"
REFERENCE_MONTH = "2026-04-01"
UPLOADS_ROOT = Path("/opt/conecta-pro/uploads")

# Mapeamento slug → padrões de nome de arquivo para busca em /uploads/
SLUG_FILENAME_PATTERNS: dict[str, list[str]] = {
    "nfse": ["nfse*laranjeira*", "*laranjeira*nfse*", "*nfse*04.2026*"],
    "boleto": ["boleto*laranjeira*", "*laranjeira*boleto*"],
    "folha_pagamento": ["Folha*04.2026*Laranjeira*", "Folha*Laranjeira*04.2026*"],
    "contracheque": ["Recibo*Folha*04.2026*Laranjeira*", "Contracheque*Laranjeira*04.2026*"],
    "folhas_ponto": ["Ponto*04.2026*Laranjeira*", "*Folha*Ponto*Laranjeira*04.2026*"],
    "gfd_fgts_mensal": ["GFD*FGTS*04.2026*", "*FGTS*Mensal*04.2026*"],
    "relatorio_gfd_fgts": ["RELATORIO*GFD*FGTS*04.2026*", "*Relatorio*FGTS*04.2026*"],
    "comp_pag_fgts": ["*Comp*FGTS*04.2026*", "*Comprovante*FGTS*Laranjeira*"],
    "gfd_fgts_rescisao": ["GFD*FGTS*Rescisao*Laranjeira*04.2026*"],
    "relatorio_gfd_rescisao": ["Relatorio*GFD*Rescisao*Laranjeira*04.2026*"],
    "comp_fgts_rescisao": ["Comp*FGTS*Rescisao*Laranjeira*04.2026*"],
    "dctfweb_declaracao": ["DCTFWEB*Declaracao*04.2026*", "*DCTFWEB*Decl*04*2026*"],
    "dctfweb_recibo": ["DCTFWEB*Recibo*04.2026*", "*DCTFWEB*Recibo*04*2026*"],
    "dctfweb_extrato": ["DCTFWEB*Extrato*04.2026*", "*DCTFWEB*Extrato*04*2026*"],
    "cnd_rfb": ["CND*RFB*", "*Certidao*Federal*", "*Certidao*Negativa*Federal*"],
    "cnd_caixa": ["CND*FGTS*", "*Certidao*FGTS*", "*CND*Caixa*"],
    "cnd_prefeitura": ["CND*Prefeitura*", "*Certidao*Municipal*", "*CND*Municipal*"],
    "cnd_sefaz": ["CND*Sefaz*", "*Certidao*Estadual*", "*CND*Estadual*"],
    "cnd_trabalhista": ["CND*Trabalhista*", "*Certidao*TST*", "*Trabalhista*"],
    "comp_vt_individual": ["*VT*Laranjeira*04.2026*", "*Vale*Transporte*04.2026*"],
    "comp_va_solides": ["*VA*Solides*04.2026*", "*Vale*Alimentacao*04.2026*"],
    "comp_vt_va_combinado": ["*VT*VA*04.2026*Laranjeira*"],
    "recibo_vt_va": ["Recibo*VT*04.2026*Laranjeira*", "*Recibo*Vale*04.2026*Laranjeira*"],
    "relatorio_pedido_va": ["Relatorio*VA*04.2026*", "*Pedido*VA*04.2026*"],
    "aso": ["ASO*Laranjeira*04.2026*", "*Atestado*Saude*04.2026*"],
    "contrato_trabalho": ["Contrato*Trabalho*Laranjeira*", "*Contrato*Emprego*Laranjeira*"],
    "ficha_empregado": ["Ficha*Empregado*Laranjeira*", "*Registro*Empregado*Laranjeira*"],
    "rescisao_contrato": ["Rescisao*Laranjeira*04.2026*", "*Rescisao*Contrato*04.2026*"],
    "comp_rescisao": ["Comp*Rescisao*Laranjeira*04.2026*"],
    "comp_salario_individual": ["*Comp*Salario*04.2026*Laranjeira*", "*Comprovante*Salario*04.2026*"],
}

# Nome legível para cada slug (para document_name no DB)
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
}


def find_pdf_for_template(slug: str, employee_nome: str | None, mes_ref: str, db) -> tuple[str | None, str]:
    """
    Retorna (file_path, fonte).
    fonte ∈ {'onvio_sync', 'uploads_filesystem', 'ausente'}

    1. Tenta onvio_documents (preferencial — já auditado)
    2. Fallback: glob em /uploads/ por padrões conhecidos
    3. Se não achar: retorna (None, 'ausente')
    """
    # (1) onvio_documents
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
        {"cid": CONDOMINIO_ID, "mes": mes_ref, "slug": slug},
    ).fetchone()
    if row and row[0]:
        host_path = row[0].replace("/app/", "/opt/conecta-pro/", 1)
        if Path(host_path).exists():
            return host_path, "onvio_sync"

    # (2) filesystem glob
    patterns = SLUG_FILENAME_PATTERNS.get(slug, [])
    for pattern in patterns:
        matches = list(UPLOADS_ROOT.rglob(pattern))
        if matches:
            return str(matches[0]), "uploads_filesystem"

    return None, "ausente"


def main() -> None:
    db = SyncSessionLocal()
    try:
        print("=" * 60)
        print(f"GEDEON BLOCO B — Seed LARANJEIRAS {MES_REF}")
        print("=" * 60)

        # ── Idempotência ─────────────────────────────────────────────
        existing = db.execute(
            text(
                "SELECT id FROM ged_document_kits "
                "WHERE client_id = CAST(:cid AS uuid) AND reference_month = CAST(:rm AS date)"
            ),
            {"cid": GED_CLIENT_ID, "rm": REFERENCE_MONTH},
        ).fetchone()
        if existing:
            print(f"⚠️  Kit LARANJEIRAS {MES_REF} já existe (id={existing[0]}). Abortando.")
            return

        # ── Funcionários ativos ───────────────────────────────────────
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
            {"cid": CONDOMINIO_ID},
        ).fetchall()
        n_func = len(funcs)
        print(f"📋 Funcionários ativos: {n_func}")
        for f in funcs:
            print(f"   • {f[1]} ({f[0]})")

        # ── Templates aplicáveis ──────────────────────────────────────
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
            {"cid": CONDOMINIO_ID},
        ).fetchall()
        print(f"\n📄 Templates aplicáveis: {len(templates)}")

        # ── Criar kit mestre ──────────────────────────────────────────
        kit_id = uuid.uuid4()
        total_obrig = sum(n_func if t[3] == "funcionario" else 1 for t in templates if t[5] == "obrigatorio")
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
                  'GEDEON BLOCO B — seed automático 2026-04-22', NOW()
                )
                """
            ),
            {
                "id": str(kit_id),
                "cid": GED_CLIENT_ID,
                "rm": REFERENCE_MONTH,
                "n_emp": n_func,
                "n_docs": total_obrig,
            },
        )
        print(f"\n✅ Kit criado: {kit_id}")
        print(f"   total_esperado: {total_obrig}")

        # ── Inserir documentos ────────────────────────────────────────
        inseridos_com_pdf = 0
        inseridos_placeholder = 0
        faltantes: list[str] = []

        for tpl in templates:
            tpl_id, tpl_num, slug, escopo, tipo_doc, presenca = tpl
            eh_eventual = presenca == "eventual"
            display_name = SLUG_DISPLAY_NAMES.get(slug, slug)

            if escopo == "funcionario":
                for func_id, func_nome in funcs:
                    fp, fonte = find_pdf_for_template(slug, func_nome, MES_REF, db)
                    # Eventuais só inseridos se encontrado (não viram placeholder)
                    if eh_eventual and fp is None:
                        continue
                    doc_name = f"{display_name} — {func_nome}" if fp else f"[PLACEHOLDER] {display_name} — {func_nome}"
                    notes_val = None if fp else "PDF não localizado no servidor"
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
                            "notes": notes_val,
                        },
                    )
                    if fp:
                        inseridos_com_pdf += 1
                    else:
                        inseridos_placeholder += 1
                        faltantes.append(f"func/{func_nome}/{slug}")
            else:
                # empresa_matriz ou condominio: 1 instância
                fp, fonte = find_pdf_for_template(slug, None, MES_REF, db)
                # Eventuais só inseridos se encontrado (não viram placeholder)
                if eh_eventual and fp is None:
                    continue
                doc_name = display_name if fp else f"[PLACEHOLDER] {display_name}"
                notes_val = None if fp else "PDF não localizado no servidor"
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
                        "notes": notes_val,
                    },
                )
                if fp:
                    inseridos_com_pdf += 1
                else:
                    inseridos_placeholder += 1
                    faltantes.append(f"{escopo}/{slug}")

        db.commit()

        # ── Relatório ─────────────────────────────────────────────────
        total_inserido = inseridos_com_pdf + inseridos_placeholder
        pct = (inseridos_com_pdf / total_obrig * 100) if total_obrig else 0.0
        print("\n📊 Resultado:")
        print(f"   total_esperado:      {total_obrig}")
        print(f"   docs inseridos:      {total_inserido}")
        print(f"   com PDF:             {inseridos_com_pdf}")
        print(f"   placeholder (NULL):  {inseridos_placeholder}")
        print(f"   completude:          {pct:.1f}%")
        if faltantes:
            print("\n⚠️  Primeiros 20 faltantes (file_path=NULL):")
            for item in faltantes[:20]:
                print(f"     - {item}")
        print("\n✅ BLOCO B seed concluído.")
        print(f"   Kit ID: {kit_id}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
