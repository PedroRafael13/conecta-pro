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


# ── Montagem Guiada (listas suspensas) ─────────────────────────────────────


@router.get("/montar/condominios")
async def listar_condominios_kit(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista 1: condominios que recebem kit mensal (7 mao de obra + 1 remota)."""
    rows = (
        (
            await db.execute(
                text(
                    "SELECT c.id, c.name, c.document_number, ct.id as contract_id, "
                    "ct.tipo_servico, ct.monthly_value, ct.retencao_iss, ct.retencao_inss, ct.retencao_csll, "
                    "(SELECT p.client_id FROM posts p WHERE p.client_id IS NOT NULL AND p.is_active = true "
                    " AND EXISTS (SELECT 1 FROM allocations a WHERE a.post_id = p.id AND a.status = 'active') "
                    " AND p.name ILIKE '%' || SPLIT_PART(c.name, ' ', 2) || '%' LIMIT 1) as ged_client_id "
                    "FROM contracts ct JOIN clients c ON ct.client_id = c.id "
                    "WHERE ct.is_active = true AND ct.kit_mensal = true "
                    "ORDER BY ct.monthly_value DESC"
                )
            )
        )
        .mappings()
        .all()
    )

    return {
        "total": len(rows),
        "condominios": [
            {
                "client_id": str(r["ged_client_id"] or r["id"]),
                "nome": r["name"],
                "cnpj": r["document_number"],
                "contract_id": str(r["contract_id"]),
                "tipo_servico": r["tipo_servico"],
                "valor_mensal": float(r["monthly_value"] or 0),
                "retencoes": {
                    "iss": r["retencao_iss"] or False,
                    "inss": r["retencao_inss"] or False,
                    "csll": r["retencao_csll"] or False,
                },
            }
            for r in rows
        ],
    }


@router.get("/montar/servicos/{client_id}")
async def listar_servicos_cliente(
    client_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista 2: servicos do condominio baseado nas NFS-e reais emitidas."""
    client = (
        (await db.execute(text("SELECT name, document_number FROM clients WHERE id = :cid"), {"cid": client_id}))
        .mappings()
        .first()
    )
    if not client:
        raise HTTPException(404, "Cliente nao encontrado")

    import re

    cnpj = re.sub(r"\D", "", client["document_number"] or "")

    nfses = (
        (
            await db.execute(
                text(
                    "SELECT DISTINCT descricao_servico, codigo_servico, valor_servicos "
                    "FROM nfses WHERE tomador_cpf_cnpj = :cnpj AND active = true "
                    "ORDER BY valor_servicos DESC"
                ),
                {"cnpj": cnpj},
            )
        )
        .mappings()
        .all()
    )

    servicos = []
    seen = set()
    for n in nfses:
        desc = n["descricao_servico"]
        if desc in seen:
            continue
        seen.add(desc)
        tem_mao = any(w in desc.lower() for w in ["portaria", "limpeza", "servicos gerais", "jardinagem", "seguranca"])
        servicos.append(
            {
                "descricao": desc,
                "codigo": n["codigo_servico"],
                "valor_ultima_nf": float(n["valor_servicos"]),
                "tem_mao_de_obra": tem_mao,
            }
        )

    if not servicos:
        servicos.append(
            {"descricao": "Servicos de portaria", "codigo": "11.02", "valor_ultima_nf": 0, "tem_mao_de_obra": True}
        )

    return {"client_id": client_id, "cliente": client["name"], "servicos": servicos}


@router.get("/montar/funcionarios/{client_id}")
async def listar_funcionarios_kit(
    client_id: str,
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista funcionarios alocados no condominio para o kit."""
    employees = await _get_employees_for_client(db, client_id)

    # Buscar ged_client correspondente
    gc = (
        (await db.execute(text("SELECT id, name FROM ged_clients WHERE id::text = :cid"), {"cid": client_id}))
        .mappings()
        .first()
    )
    # Tentar pelo client_id nos posts
    if not gc:
        gc_alt = (
            (
                await db.execute(
                    text(
                        "SELECT g.id, g.name FROM ged_clients g "
                        "JOIN posts p ON p.client_id::text = g.id::text "
                        "JOIN clients c ON c.id = :cid "
                        "WHERE p.is_active = true LIMIT 1"
                    ),
                    {"cid": client_id},
                )
            )
            .mappings()
            .first()
        )
        gc = gc_alt

    return {
        "client_id": client_id,
        "cliente": gc["name"] if gc else "-",
        "total_funcionarios": len(employees),
        "funcionarios": [
            {
                "id": e["id"],
                "nome": e["nome"],
                "cargo": e["cargo"],
                "cpf": e["cpf"],
                "salario_base": float(e["salario_base"] or 0),
                "salario_liquido": round(float(e["salario_base"] or 0) * 0.85, 2),
            }
            for e in employees
        ],
    }


@router.post("/montar/kit")
async def montar_kit_guiado(
    client_id: str = Query(...),
    competencia: str = Query("2026-03-01"),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Monta kit completo: gera PDFs + vincula NFS-e + retorna checklist."""
    from datetime import date as d

    d.fromisoformat(competencia)  # validate format

    # Verificar contrato com kit
    ct = (
        (
            await db.execute(
                text(
                    "SELECT kit_mensal, tipo_servico, retencao_iss, retencao_inss, retencao_csll FROM contracts WHERE client_id = :cid AND is_active = true AND kit_mensal = true LIMIT 1"
                ),
                {"cid": client_id},
            )
        )
        .mappings()
        .first()
    )
    if not ct:
        return {"erro": "Cliente nao recebe kit mensal", "sugestao": "Verificar contratos ativos"}

    # Buscar ou criar GED client
    gc = (
        (
            await db.execute(
                text(
                    "SELECT id FROM ged_clients WHERE id::text IN (SELECT p.client_id::text FROM posts p WHERE p.client_id IS NOT NULL) AND id::text = :cid"
                ),
                {"cid": client_id},
            )
        )
        .mappings()
        .first()
    )
    if not gc:
        # Tentar via posts linkados
        gc = (
            (
                await db.execute(
                    text(
                        "SELECT DISTINCT p.client_id as id FROM posts p WHERE p.client_id IS NOT NULL AND EXISTS (SELECT 1 FROM allocations a WHERE a.post_id = p.id AND a.status = 'active') AND p.client_id::text IN (SELECT g.id::text FROM ged_clients g) ORDER BY p.client_id LIMIT 1"
                    ),
                )
            )
            .mappings()
            .first()
        )

    ged_client_id = str(gc["id"]) if gc else client_id

    # Verificar/criar kit
    kit = (
        (
            await db.execute(
                text("SELECT id FROM ged_document_kits WHERE client_id::text = :cid AND reference_month = :rm LIMIT 1"),
                {"cid": ged_client_id, "rm": competencia},
            )
        )
        .mappings()
        .first()
    )

    if kit:
        kit_id = str(kit["id"])
    else:
        await db.execute(
            text(
                "INSERT INTO ged_document_kits (id, client_id, reference_month, status, total_employees, total_documents, completion_percentage, created_at, updated_at) "
                "VALUES (gen_random_uuid(), :cid, :rm, 'em_montagem', 0, 0, 0, NOW(), NOW()) RETURNING id"
            ),
            {"cid": ged_client_id, "rm": competencia},
        )
        await db.commit()
        new_kit = (
            (
                await db.execute(
                    text("SELECT id FROM ged_document_kits WHERE client_id::text = :cid AND reference_month = :rm"),
                    {"cid": ged_client_id, "rm": competencia},
                )
            )
            .mappings()
            .first()
        )
        kit_id = str(new_kit["id"]) if new_kit else "?"

    # Gerar PDFs reais
    result = await _gerar_kit_real(db, kit_id)

    # Adicionar info de retencoes
    result["retencoes"] = {
        "iss": ct["retencao_iss"] or False,
        "inss": ct["retencao_inss"] or False,
        "csll": ct["retencao_csll"] or False,
    }
    result["tipo_servico"] = ct["tipo_servico"]

    return result
