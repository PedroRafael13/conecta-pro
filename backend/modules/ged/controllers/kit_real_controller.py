"""
Controller do Kit Real — gera documentos conforme estrutura auditada do Google Drive.

Endpoints:
- POST /kit-real/{kit_id}/gerar — gera PDFs reais para 1 kit
- POST /kit-real/gerar-todos — gera PDFs para todos os kits do mes
- GET  /kit-real/{kit_id}/checklist — o que esta pronto e o que falta
"""

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["GED - Kit Real"])


async def _get_employees_for_client(db: AsyncSession, client_id: str) -> list[dict]:
    """Busca funcionarios alocados no cliente via posts+allocations."""
    rows = (
        (
            await db.execute(
                text(
                    "SELECT DISTINCT e.id, e.nome, e.cpf, e.cargo, e.salario_base, "
                    "e.data_admissao, e.matricula "
                    "FROM employees e "
                    "JOIN allocations a ON a.employee_id = e.id AND a.status = 'active' "
                    "JOIN posts p ON a.post_id = p.id AND p.client_id::text = :cid "
                    "WHERE e.is_active = true "
                    "ORDER BY e.nome"
                ),
                {"cid": client_id},
            )
        )
        .mappings()
        .all()
    )
    return [
        {
            "id": str(r["id"]),
            "nome": r["nome"],
            "cpf": r["cpf"],
            "cargo": r["cargo"],
            "salario_base": r["salario_base"],
            "data_admissao": r["data_admissao"].strftime("%d/%m/%Y") if r["data_admissao"] else "-",
            "matricula": r["matricula"],
        }
        for r in rows
    ]


async def _gerar_kit_real(db: AsyncSession, kit_id: str) -> dict:
    """Gera os 4 PDFs consolidados + NFS-e para 1 kit."""
    from modules.ged.services.kit_real_engine import (
        gerar_contracheques_consolidado,
        gerar_folha_pagamento,
        gerar_folhas_ponto,
        gerar_recibo_vt_va,
    )

    kit = (await db.execute(text("SELECT * FROM ged_document_kits WHERE id = :id"), {"id": kit_id})).mappings().first()
    if not kit:
        return {"erro": "Kit nao encontrado"}

    client_id = str(kit["client_id"])
    comp = kit["reference_month"] or date(2026, 3, 1)

    # Nome do cliente
    gc = (
        (await db.execute(text("SELECT name FROM ged_clients WHERE id::text = :cid"), {"cid": client_id}))
        .mappings()
        .first()
    )
    cliente_nome = gc["name"] if gc else "Cliente"

    employees = await _get_employees_for_client(db, client_id)
    if not employees:
        return {"kit_id": kit_id, "cliente": cliente_nome, "gerados": 0, "motivo": "Sem funcionarios alocados"}

    gerados = 0
    docs_gerados = []

    # 1. Folha de Pagamento
    path = gerar_folha_pagamento(employees, comp, cliente_nome)
    if path:
        await _upsert_doc(db, kit_id, "folha_pagamento", "Folha de Pagamento.pdf", path)
        gerados += 1
        docs_gerados.append("folha_pagamento")

    # 2. Contracheques consolidados
    path = gerar_contracheques_consolidado(employees, comp)
    if path:
        await _upsert_doc(db, kit_id, "contracheques_consolidado", "Contracheques.pdf", path)
        gerados += 1
        docs_gerados.append("contracheques_consolidado")

    # 3. Folhas de Ponto
    path = gerar_folhas_ponto(employees, comp, cliente_nome)
    if path:
        await _upsert_doc(db, kit_id, "folhas_ponto_consolidado", "Folhas_de_Ponto.pdf", path)
        gerados += 1
        docs_gerados.append("folhas_ponto_consolidado")

    # 4. Recibo VT+VA
    path = gerar_recibo_vt_va(employees, comp, cliente_nome)
    if path:
        await _upsert_doc(db, kit_id, "recibo_vt_va", "Recibo_VT_VA.pdf", path)
        gerados += 1
        docs_gerados.append("recibo_vt_va")

    # 5. NFS-e (buscar do mes anterior — fev para kit marco)
    nfse_count = await _add_nfse_to_kit(db, kit_id, client_id, comp)
    gerados += nfse_count
    if nfse_count:
        docs_gerados.append(f"nfse x{nfse_count}")

    await db.commit()

    return {
        "kit_id": kit_id,
        "cliente": cliente_nome,
        "funcionarios": len(employees),
        "gerados": gerados,
        "documentos": docs_gerados,
    }


async def _upsert_doc(db: AsyncSession, kit_id: str, doc_type: str, doc_name: str, file_path: str) -> None:
    """Insere ou atualiza documento no kit."""
    existing = (
        await db.execute(
            text("SELECT id FROM ged_kit_documents WHERE kit_id = :kid AND document_type = :dt"),
            {"kid": kit_id, "dt": doc_type},
        )
    ).first()
    if existing:
        await db.execute(
            text(
                "UPDATE ged_kit_documents SET file_path = :fp, document_name = :dn, updated_at = NOW() WHERE kit_id = :kid AND document_type = :dt"
            ),
            {"fp": file_path, "dn": doc_name, "kid": kit_id, "dt": doc_type},
        )
    else:
        await db.execute(
            text(
                "INSERT INTO ged_kit_documents (id, kit_id, document_type, document_name, file_path, "
                "source_module, auto_generated, is_signed, created_at, updated_at) "
                "VALUES (gen_random_uuid(), :kid, :dt, :dn, :fp, 'sistema', true, false, NOW(), NOW())"
            ),
            {"kid": kit_id, "dt": doc_type, "dn": doc_name, "fp": file_path},
        )


async def _add_nfse_to_kit(db: AsyncSession, kit_id: str, client_id: str, comp: date) -> int:
    """Adiciona NFS-e do cliente (meses jan e fev) ao kit."""
    from modules.ged.controllers.kit_pdf_controller import _gerar_nfse_pdf, _save_pdf

    nfses = (
        (
            await db.execute(
                text(
                    "SELECT * FROM nfses WHERE condominio_id::text = :cid AND active = true ORDER BY data_competencia DESC"
                ),
                {"cid": client_id},
            )
        )
        .mappings()
        .all()
    )

    added = 0
    for n in nfses:
        sid = str(n["id"])
        exists = (
            await db.execute(
                text("SELECT 1 FROM ged_kit_documents WHERE kit_id = :kid AND source_record_id::text = :sid"),
                {"kid": kit_id, "sid": sid},
            )
        ).first()
        if exists:
            continue

        num = n["numero_nfse"] or str(n["numero_rps"])
        pdf_bytes = _gerar_nfse_pdf(
            numero=num,
            tomador=n["tomador_razao_social"],
            cnpj=n["tomador_cpf_cnpj"],
            valor=float(n["valor_servicos"]),
            iss=float(n["iss_valor"] or 0),
            descricao=n["descricao_servico"],
            competencia=n["data_competencia"].strftime("%m/%Y") if n["data_competencia"] else "02/2026",
        )
        path = _save_pdf(
            pdf_bytes, f"nfse_{num}_{n['data_competencia'].strftime('%Y%m') if n['data_competencia'] else '202602'}"
        )
        await db.execute(
            text(
                "INSERT INTO ged_kit_documents (id, kit_id, document_type, document_name, file_path, "
                "source_module, source_record_id, auto_generated, is_signed, created_at, updated_at) "
                "VALUES (gen_random_uuid(), :kid, 'nfse', :dn, :fp, 'fiscal', :sid, true, false, NOW(), NOW())"
            ),
            {"kid": kit_id, "dn": f"NFS-e {num}", "fp": path, "sid": sid},
        )
        added += 1
    return added


# ── Endpoints ─────────────────────────────────────────────────────────────


@router.post("/kit-real/{kit_id}/gerar")
async def gerar_kit_real(
    kit_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera todos os PDFs reais para um kit especifico."""
    return await _gerar_kit_real(db, kit_id)


@router.post("/kit-real/gerar-todos")
async def gerar_todos_kits_reais(
    mes: int = Query(3, ge=1, le=12),
    ano: int = Query(2026, ge=2020),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera PDFs reais para TODOS os kits do mes."""
    kits = (
        (
            await db.execute(
                text("SELECT id FROM ged_document_kits WHERE reference_month = :rm"),
                {"rm": f"{ano}-{mes:02d}-01"},
            )
        )
        .mappings()
        .all()
    )

    resultados = []
    total_gerados = 0
    for k in kits:
        r = await _gerar_kit_real(db, str(k["id"]))
        total_gerados += r.get("gerados", 0)
        resultados.append(r)

    return {
        "competencia": f"{mes:02d}/{ano}",
        "kits_processados": len(kits),
        "total_pdfs_gerados": total_gerados,
        "kits": resultados,
    }


@router.get("/kit-real/{kit_id}/checklist")
async def checklist_kit_real(
    kit_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Checklist do kit: prontos vs pendentes (baseado na anatomia real)."""
    kit = (await db.execute(text("SELECT * FROM ged_document_kits WHERE id = :id"), {"id": kit_id})).mappings().first()
    if not kit:
        raise HTTPException(404, "Kit nao encontrado")

    gc = (
        (await db.execute(text("SELECT name FROM ged_clients WHERE id::text = :cid"), {"cid": str(kit["client_id"])}))
        .mappings()
        .first()
    )

    docs = (
        (
            await db.execute(
                text("SELECT document_type, document_name, file_path FROM ged_kit_documents WHERE kit_id = :kid"),
                {"kid": kit_id},
            )
        )
        .mappings()
        .all()
    )
    tipos_ok = {d["document_type"] for d in docs if d["file_path"] and d["file_path"].startswith("ged/kits/")}

    TIPOS_SISTEMA = ["folha_pagamento", "contracheques_consolidado", "folhas_ponto_consolidado", "recibo_vt_va", "nfse"]
    TIPOS_UPLOAD = [
        "comprovante_fgts",
        "gfd_fgts",
        "relatorio_gfd_fgts",
        "dctf_declaracao",
        "dctf_recibo",
        "dctf_extrato",
        "boleto_nfse",
        "comprovante_salario",
        "comprovante_vt",
    ]
    TIPOS_CERTIDAO = ["cnd_caixa", "cnd_prefeitura", "cnd_receita", "cnd_sefaz", "cnd_trabalhista"]

    checklist = []
    for t in TIPOS_SISTEMA:
        checklist.append({"tipo": t, "categoria": "sistema", "status": "pronto" if t in tipos_ok else "pendente"})
    for t in TIPOS_CERTIDAO:
        checklist.append(
            {"tipo": t, "categoria": "certidao", "status": "pronto" if t in tipos_ok else "pendente_download"}
        )
    for t in TIPOS_UPLOAD:
        checklist.append(
            {"tipo": t, "categoria": "upload_manual", "status": "pronto" if t in tipos_ok else "pendente_upload"}
        )

    prontos = sum(1 for c in checklist if c["status"] == "pronto")
    return {
        "kit_id": kit_id,
        "cliente": gc["name"] if gc else "-",
        "total": len(checklist),
        "prontos": prontos,
        "pendentes": len(checklist) - prontos,
        "percentual": round(prontos / max(1, len(checklist)) * 100, 1),
        "checklist": checklist,
    }
