"""
Controller de Integracao GED — Onboarding, SST, Portal, CCT.

Endpoints de documentos por colaborador, integrando:
- Onboarding checklist → docs admissionais
- SST → atestados, ASOs, CATs
- Portal → contracheques PDF
- CCT 2026 → convenção institucional
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ged-integration", tags=["GED - Integracao"])


# ═══════════════════════════════════════════════════
# FASE 2 — GED + ONBOARDING
# ═══════════════════════════════════════════════════


@router.get("/onboarding/{employee_id}")
async def get_onboarding_docs(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Documentos de onboarding por colaborador."""
    try:
        items = (
            (
                await db.execute(
                    text(
                        "SELECT c.id, c.etapa, c.titulo, c.responsavel, "
                        "c.prazo_data, c.concluido, c.data_conclusao, "
                        "CASE WHEN c.etapa IN (1,4,5,10,11) THEN 'requer_documento' "
                        "ELSE 'sem_documento' END as tipo_documento, "
                        "CASE WHEN c.concluido THEN 'anexado' ELSE 'pendente' END as status_doc "
                        "FROM rh_onboarding_checklist c "
                        "WHERE c.employee_id = :eid ORDER BY c.etapa"
                    ),
                    {"eid": employee_id},
                )
            )
            .mappings()
            .all()
        )

        emp = (
            (await db.execute(text("SELECT nome, cargo FROM employees WHERE id = :eid"), {"eid": employee_id}))
            .mappings()
            .first()
        )

        return {
            "employee_id": employee_id,
            "employee_name": dict(emp).get("nome", "") if emp else "",
            "cargo": dict(emp).get("cargo", "") if emp else "",
            "documentos": [dict(i) for i in items],
            "total": len(items),
            "pendentes": sum(1 for i in items if not i["concluido"]),
            "concluidos": sum(1 for i in items if i["concluido"]),
        }
    except Exception as exc:
        logger.warning("Erro docs onboarding: %s", exc)
        return {"employee_id": employee_id, "documentos": [], "total": 0}


# ═══════════════════════════════════════════════════
# FASE 3 — GED + PORTAL (Contracheques)
# ═══════════════════════════════════════════════════


@router.get("/contracheques/{employee_id}")
async def get_contracheques(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Historico de contracheques arquivados no GED."""
    try:
        emp = (
            (
                await db.execute(
                    text("SELECT nome, cargo, salario_base FROM employees WHERE id = :eid"), {"eid": employee_id}
                )
            )
            .mappings()
            .first()
        )

        if not emp:
            return {"employee_id": employee_id, "contracheques": []}

        emp_dict = dict(emp)

        docs = (
            (
                await db.execute(
                    text(
                        "SELECT id, competencia, ano, mes, path, tamanho_bytes, created_at "
                        "FROM ged_contracheques WHERE employee_id = :eid "
                        "ORDER BY ano DESC, mes DESC"
                    ),
                    {"eid": employee_id},
                )
            )
            .mappings()
            .all()
        )

        return {
            "employee_id": employee_id,
            "employee_name": emp_dict.get("nome", ""),
            "cargo": emp_dict.get("cargo", ""),
            "salario_base": str(emp_dict.get("salario_base", 0)),
            "contracheques": [dict(d) for d in docs],
            "total": len(docs),
            "pasta_ged": f"colaboradores/{employee_id}/contracheques/",
        }
    except Exception as exc:
        logger.warning("Erro contracheques GED: %s", exc)
        return {"employee_id": employee_id, "contracheques": []}


# ═══════════════════════════════════════════════════
# FASE 4 — GED + SST
# ═══════════════════════════════════════════════════


@router.get("/sst/{employee_id}")
async def get_sst_docs(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Documentos SST por colaborador (atestados, ASOs, CATs)."""
    try:
        afastamentos = (
            (
                await db.execute(
                    text(
                        "SELECT id, tipo, motivo, data_inicio, data_fim_prevista, "
                        "cid, medico, status, atestado "
                        "FROM sst_afastamentos WHERE employee_id = :eid "
                        "ORDER BY data_inicio DESC"
                    ),
                    {"eid": employee_id},
                )
            )
            .mappings()
            .all()
        )

        emp = (
            (await db.execute(text("SELECT nome, cargo FROM employees WHERE id = :eid"), {"eid": employee_id}))
            .mappings()
            .first()
        )

        return {
            "employee_id": employee_id,
            "employee_name": dict(emp).get("nome", "") if emp else "",
            "atestados": [dict(a) for a in afastamentos if a.get("atestado")],
            "asos": [],
            "cats": [],
            "total_afastamentos": len(afastamentos),
            "pasta_ged": f"colaboradores/{employee_id}/sst/",
        }
    except Exception as exc:
        logger.warning("Erro docs SST: %s", exc)
        return {"employee_id": employee_id, "atestados": [], "asos": [], "cats": []}


@router.get("/sst/asos/vencendo")
async def get_asos_vencendo(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """ASOs proximos do vencimento (sem ASO nos ultimos 12 meses)."""
    try:
        sem_aso = (
            (
                await db.execute(
                    text(
                        "SELECT e.id, e.nome, e.cargo, e.data_admissao "
                        "FROM employees e "
                        "WHERE e.status = 'ativo' "
                        "AND NOT EXISTS ( "
                        "  SELECT 1 FROM sst_afastamentos a "
                        "  WHERE a.employee_id = e.id "
                        "  AND a.tipo = 'aso_periodico' "
                        "  AND a.data_inicio >= CURRENT_DATE - INTERVAL '12 months' "
                        ") ORDER BY e.data_admissao"
                    )
                )
            )
            .mappings()
            .all()
        )

        return {
            "sem_aso_12_meses": [dict(r) for r in sem_aso],
            "total": len(sem_aso),
            "alerta": "Colaboradores sem ASO periodico nos ultimos 12 meses.",
        }
    except Exception as exc:
        logger.warning("Erro ASOs vencendo: %s", exc)
        return {"sem_aso_12_meses": [], "total": 0}


# ═══════════════════════════════════════════════════
# FASE 5 — GED + CCT 2026
# ═══════════════════════════════════════════════════


@router.get("/institucional/cct")
async def get_cct_documento(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """CCT 2026 vigente para download."""
    try:
        cargos = (
            (
                await db.execute(
                    text(
                        "SELECT nome_cargo, cbo, salario_base, divisor_horas, escala_padrao "
                        "FROM cct_cargos ORDER BY nome_cargo"
                    )
                )
            )
            .mappings()
            .all()
        )

        return {
            "cct_vigente": "CCT 2026 SINDECOMPRESTS/SINDICOND-AM",
            "vigencia": {"inicio": "2026-01-01", "fim": "2026-12-31"},
            "sindicato_empregados": "SINDECOMPRESTS",
            "sindicato_patronal": "SINDICOND-AM",
            "cargos": [dict(c) for c in cargos],
            "total_cargos": len(cargos),
            "beneficios_obrigatorios": [
                {"tipo": "VA", "valor_diario": 22.00},
                {"tipo": "Cesta Basica", "valor_mensal": 18.00},
                {"tipo": "VT", "desconto_max": "4%"},
                {"tipo": "Plano Odontologico", "desconto_max": 9.00},
                {"tipo": "Seguro de Vida", "desconto_max": 2.00},
            ],
            "pasta_ged": "institucional/cct/",
            "documento_pdf": "CCT_SINDECOMPRESTS_2026.pdf",
        }
    except Exception as exc:
        logger.warning("Erro CCT documento: %s", exc)
        return {"cct_vigente": "CCT 2026", "cargos": []}


@router.get("/institucional/comunicados")
async def get_comunicados(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Comunicados institucionais do GED."""
    _ = db  # Disponivel para queries futuras
    return {
        "comunicados": [
            {
                "id": 1,
                "titulo": "CCT 2026 — Novos pisos salariais",
                "data": "2026-01-15",
                "tipo": "cct",
                "visivel_portal": True,
            },
            {
                "id": 2,
                "titulo": "Plano Odontologico — Adesao obrigatoria",
                "data": "2026-01-20",
                "tipo": "beneficio",
                "visivel_portal": True,
            },
        ],
        "total": 2,
    }
