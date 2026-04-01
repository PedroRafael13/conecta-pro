"""
Controller de NFS-e e Dashboard Financeiro.

Endpoints para consulta de notas fiscais de servico emitidas
e metricas de faturamento.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["NFS-e"])


@router.get("/nfse")
async def list_nfse(
    competencia: str | None = Query(None, description="YYYY-MM (ex: 2026-01)"),
    cliente: str | None = Query(None, description="Filtro por razao social (parcial)"),
    status: str | None = Query(None, description="autorizada, cancelada, etc."),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista NFS-e emitidas com filtros."""
    conditions = ["active = true"]
    params: dict[str, Any] = {"limit": limit}

    if competencia:
        conditions.append("to_char(data_competencia, 'YYYY-MM') = :competencia")
        params["competencia"] = competencia
    if cliente:
        conditions.append("tomador_razao_social ILIKE :cliente")
        params["cliente"] = f"%{cliente}%"
    if status:
        conditions.append("status = :status")
        params["status"] = status

    where = " AND ".join(conditions)
    result = await db.execute(
        text(f"SELECT * FROM nfses WHERE {where} ORDER BY data_competencia DESC, numero_rps LIMIT :limit"),
        params,
    )
    rows = result.mappings().all()

    return {
        "total": len(rows),
        "items": [
            {
                "id": str(r["id"]),
                "numero_nfse": r["numero_nfse"],
                "numero_rps": r["numero_rps"],
                "status": r["status"],
                "data_emissao": r["data_emissao"].isoformat() if r["data_emissao"] else None,
                "data_competencia": r["data_competencia"].isoformat() if r["data_competencia"] else None,
                "tomador_razao_social": r["tomador_razao_social"],
                "tomador_cpf_cnpj": r["tomador_cpf_cnpj"],
                "descricao_servico": r["descricao_servico"],
                "valor_servicos": float(r["valor_servicos"]),
                "iss_aliquota": float(r["iss_aliquota"]),
                "iss_valor": float(r["iss_valor"]) if r["iss_valor"] else 0,
                "iss_retido": r["iss_retido"],
                "discriminacao": r["discriminacao"],
            }
            for r in rows
        ],
    }


@router.get("/nfse/dashboard")
async def nfse_dashboard(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dashboard de faturamento com metricas consolidadas."""
    # Faturamento por competencia
    por_mes = await db.execute(
        text("""
        SELECT
            to_char(data_competencia, 'YYYY-MM') as competencia,
            count(*) as nfse_emitidas,
            sum(valor_servicos) as faturamento_bruto,
            sum(iss_valor) as iss_total,
            sum(valor_servicos) - COALESCE(sum(iss_valor), 0) as faturamento_liquido
        FROM nfses
        WHERE active = true
        GROUP BY data_competencia
        ORDER BY data_competencia DESC
        LIMIT 12
    """)
    )
    meses = por_mes.mappings().all()

    # Faturamento por cliente (acumulado)
    por_cliente = await db.execute(
        text("""
        SELECT
            tomador_razao_social as cliente,
            tomador_cpf_cnpj as cnpj,
            count(*) as nfse_emitidas,
            sum(valor_servicos) as total_bruto,
            sum(iss_valor) as total_iss
        FROM nfses
        WHERE active = true
        GROUP BY tomador_razao_social, tomador_cpf_cnpj
        ORDER BY sum(valor_servicos) DESC
    """)
    )
    clientes = por_cliente.mappings().all()

    # Faturamento por tipo de servico
    por_servico = await db.execute(
        text("""
        SELECT
            descricao_servico as servico,
            count(*) as quantidade,
            sum(valor_servicos) as total
        FROM nfses
        WHERE active = true
        GROUP BY descricao_servico
        ORDER BY sum(valor_servicos) DESC
    """)
    )
    servicos = por_servico.mappings().all()

    # Totais gerais
    totais = await db.execute(
        text("""
        SELECT
            count(*) as total_nfse,
            count(DISTINCT tomador_cpf_cnpj) as total_clientes,
            sum(valor_servicos) as faturamento_total,
            sum(iss_valor) as iss_total,
            avg(valor_servicos) as ticket_medio
        FROM nfses
        WHERE active = true
    """)
    )
    t = totais.mappings().first()

    return {
        "totais": {
            "nfse_emitidas": t["total_nfse"] if t else 0,
            "clientes_ativos": t["total_clientes"] if t else 0,
            "faturamento_bruto": round(float(t["faturamento_total"]), 2) if t and t["faturamento_total"] else 0,
            "iss_total": round(float(t["iss_total"]), 2) if t and t["iss_total"] else 0,
            "ticket_medio": round(float(t["ticket_medio"]), 2) if t and t["ticket_medio"] else 0,
        },
        "por_mes": [
            {
                "competencia": m["competencia"],
                "nfse_emitidas": m["nfse_emitidas"],
                "faturamento_bruto": round(float(m["faturamento_bruto"]), 2),
                "iss_total": round(float(m["iss_total"]), 2) if m["iss_total"] else 0,
                "faturamento_liquido": round(float(m["faturamento_liquido"]), 2) if m["faturamento_liquido"] else 0,
            }
            for m in meses
        ],
        "por_cliente": [
            {
                "cliente": c["cliente"],
                "cnpj": c["cnpj"],
                "nfse_emitidas": c["nfse_emitidas"],
                "total_bruto": round(float(c["total_bruto"]), 2),
                "total_iss": round(float(c["total_iss"]), 2) if c["total_iss"] else 0,
            }
            for c in clientes
        ],
        "por_servico": [
            {
                "servico": s["servico"],
                "quantidade": s["quantidade"],
                "total": round(float(s["total"]), 2),
            }
            for s in servicos
        ],
    }


@router.get("/contracts")
async def list_contracts(
    status_filter: str | None = Query(None, alias="status", description="ativo, cancelado, etc."),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista contratos com dados do cliente e retencoes fiscais."""
    conditions = ["ct.is_active = true"]
    params: dict[str, Any] = {}
    if status_filter:
        conditions.append("ct.status = :status")
        params["status"] = status_filter
    where = " AND ".join(conditions)
    result = await db.execute(
        text(f"""
        SELECT ct.id, ct.contract_number, ct.name as servico, ct.description,
            ct.monthly_value, ct.total_value, ct.start_date, ct.end_date,
            ct.status, ct.contract_type, ct.auto_renewal,
            ct.renewal_period_months, ct.renewal_notification_days,
            ct.adjustment_enabled, ct.adjustment_index,
            ct.sla_config,
            c.id as client_id, c.name as client_name,
            c.document_number as client_cnpj, c.email as client_email,
            c.address_city, c.address_state
        FROM contracts ct
        JOIN clients c ON ct.client_id = c.id
        WHERE {where}
        ORDER BY ct.monthly_value DESC
        """),
        params,
    )
    rows = result.mappings().all()
    total_mrr = sum(float(r["monthly_value"]) for r in rows)
    return {
        "total": len(rows),
        "mrr_total": round(total_mrr, 2),
        "items": [
            {
                "id": str(r["id"]),
                "contract_number": r["contract_number"],
                "servico": r["servico"],
                "description": r["description"],
                "monthly_value": float(r["monthly_value"]),
                "total_value": float(r["total_value"]) if r["total_value"] else 0,
                "start_date": r["start_date"].isoformat() if r["start_date"] else None,
                "end_date": r["end_date"].isoformat() if r["end_date"] else None,
                "status": r["status"],
                "contract_type": r["contract_type"],
                "auto_renewal": r["auto_renewal"],
                "renewal_period_months": r["renewal_period_months"],
                "adjustment_enabled": r["adjustment_enabled"],
                "adjustment_index": r["adjustment_index"],
                "sla_config": r["sla_config"] or {},
                "client": {
                    "id": str(r["client_id"]),
                    "name": r["client_name"],
                    "cnpj": r["client_cnpj"],
                    "email": r["client_email"],
                    "city": r["address_city"],
                    "state": r["address_state"],
                },
            }
            for r in rows
        ],
    }


@router.get("/contracts/summary")
async def contracts_summary(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Resumo dos contratos com alertas de vencimento."""
    from datetime import date as date_cls

    today = date_cls.today()
    result = await db.execute(
        text("""
        SELECT ct.id, ct.contract_number, ct.name as servico,
            ct.monthly_value, ct.end_date, ct.status, ct.auto_renewal, ct.sla_config,
            c.name as client_name, c.document_number as client_cnpj
        FROM contracts ct JOIN clients c ON ct.client_id = c.id
        WHERE ct.is_active = true ORDER BY ct.end_date ASC
        """)
    )
    rows = result.mappings().all()
    ativos = [r for r in rows if r["status"] in ("ativo", "ACTIVE")]
    total_mrr = sum(float(r["monthly_value"]) for r in ativos)
    com_inss = sum(1 for r in ativos if r["sla_config"] and r["sla_config"].get("retencao_inss"))
    com_issqn = sum(1 for r in ativos if r["sla_config"] and r["sla_config"].get("retencao_issqn"))
    com_pis = sum(1 for r in ativos if r["sla_config"] and r["sla_config"].get("retencao_pis_cofins_csll"))

    alertas = []
    for r in ativos:
        if r["end_date"]:
            dias = (r["end_date"] - today).days
            sev = (
                "critical"
                if dias <= 0
                else "high"
                if dias <= 30
                else "medium"
                if dias <= 60
                else "low"
                if dias <= 90
                else None
            )
            if sev:
                msg = f"VENCIDO há {abs(dias)} dias" if dias <= 0 else f"Vence em {dias} dias"
                alertas.append(
                    {
                        "contract_number": r["contract_number"],
                        "client": r["client_name"],
                        "end_date": r["end_date"].isoformat(),
                        "dias": dias,
                        "severity": sev,
                        "message": msg,
                    }
                )

    return {
        "total_ativos": len(ativos),
        "mrr_total": round(total_mrr, 2),
        "mrr_anual": round(total_mrr * 12, 2),
        "retencoes": {"com_inss": com_inss, "com_issqn": com_issqn, "com_pis_cofins": com_pis},
        "vencimentos": {
            "em_30_dias": sum(1 for a in alertas if a["severity"] in ("critical", "high")),
            "em_60_dias": sum(1 for a in alertas if a["severity"] == "medium"),
            "em_90_dias": sum(1 for a in alertas if a["severity"] == "low"),
        },
        "alertas": alertas,
    }


@router.post("/contracts/{contract_id}/renew", status_code=201)
async def renew_contract(
    contract_id: str,
    reajuste_percent: float = Query(0.0, description="Percentual de reajuste"),
    meses: int = Query(12, description="Meses de renovacao"),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Renova contrato criando novo periodo com reajuste opcional."""
    import uuid
    from datetime import date as date_cls
    from datetime import timedelta

    result = await db.execute(text("SELECT * FROM contracts WHERE id = :id AND is_active = true"), {"id": contract_id})
    contract = result.mappings().first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato nao encontrado")
    old_value = float(contract["monthly_value"])
    new_value = round(old_value * (1 + reajuste_percent / 100), 2)
    old_end = contract["end_date"]
    new_start = old_end + timedelta(days=1) if old_end else date_cls.today()
    new_end = date_cls(
        new_start.year + (new_start.month + meses - 1) // 12, (new_start.month + meses - 1) % 12 + 1, 1
    ) - timedelta(days=1)
    num_parts = contract["contract_number"].rsplit("-", 1)
    new_num = f"{num_parts[0]}-R{num_parts[1]}" if len(num_parts) > 1 else f"{contract['contract_number']}-R1"
    new_id = str(uuid.uuid4())
    await db.execute(
        text("""
        INSERT INTO contracts (id, contract_number, client_id, contract_type, status, name, description,
            monthly_value, total_value, setup_fee, start_date, end_date,
            grace_period_days, notice_period_days, auto_renewal, renewal_period_months,
            renewal_notification_days, adjustment_enabled, has_sla, signature_required,
            sla_config, is_active, created_at)
        VALUES (:id, :num, :cid, :type, 'ativo', :name, :desc, :mv, :tv, 0, :sd, :ed,
            0, 30, true, :months, 30, true, false, true, :sla, true, NOW())
    """),
        {
            "id": new_id,
            "num": new_num,
            "cid": str(contract["client_id"]),
            "type": contract["contract_type"],
            "name": contract["name"],
            "desc": contract["description"],
            "mv": new_value,
            "tv": round(new_value * meses, 2),
            "sd": new_start.isoformat(),
            "ed": new_end.isoformat(),
            "months": meses,
            "sla": contract["sla_config"],
        },
    )
    await db.execute(
        text("UPDATE contracts SET status='encerrado', is_active=false, updated_at=NOW() WHERE id=:id"),
        {"id": contract_id},
    )
    await db.commit()
    return {
        "message": "Contrato renovado com sucesso",
        "old_contract": {
            "id": contract_id,
            "number": contract["contract_number"],
            "value": old_value,
            "status": "encerrado",
        },
        "new_contract": {
            "id": new_id,
            "number": new_num,
            "monthly_value": new_value,
            "total_value": round(new_value * meses, 2),
            "start_date": new_start.isoformat(),
            "end_date": new_end.isoformat(),
            "reajuste_percent": reajuste_percent,
        },
    }


@router.get("/bidding/dashboard")
async def bidding_dashboard(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dashboard de licitacoes com editais, certidoes e propostas."""
    from datetime import date as date_cls

    today = date_cls.today()

    # Editais
    tenders = await db.execute(
        text("""
        SELECT id, numero, orgao_nome, objeto_resumido, valor_estimado,
            status, participando, modalidade, data_abertura, data_encerramento_propostas,
            segmento, tags
        FROM bidding_tenders WHERE ativo = true ORDER BY data_abertura DESC
    """)
    )
    all_tenders = [dict(r) for r in tenders.mappings().all()]
    for t in all_tenders:
        t["id"] = str(t["id"])
        t["valor_estimado"] = float(t["valor_estimado"]) if t["valor_estimado"] else 0
        t["data_abertura"] = t["data_abertura"].isoformat() if t["data_abertura"] else None
        t["data_encerramento_propostas"] = (
            t["data_encerramento_propostas"].isoformat() if t["data_encerramento_propostas"] else None
        )

    # Certidoes
    certs = await db.execute(
        text("""
        SELECT id, tipo, nome, situacao, status, data_validade, ativo
        FROM bidding_certificates WHERE ativo = true ORDER BY data_validade ASC
    """)
    )
    all_certs = []
    cert_alertas = []
    for c in certs.mappings().all():
        cd = dict(c)
        cd["id"] = str(cd["id"])
        dias = (cd["data_validade"].date() - today).days if cd["data_validade"] else 999
        cd["data_validade"] = cd["data_validade"].isoformat() if cd["data_validade"] else None
        cd["dias_para_vencer"] = dias
        all_certs.append(cd)
        if dias <= 0:
            cert_alertas.append(
                {
                    "tipo": cd["tipo"],
                    "nome": cd["nome"],
                    "dias": dias,
                    "severity": "critical",
                    "message": f"{cd['nome']}: VENCIDA",
                }
            )
        elif dias <= 15:
            cert_alertas.append(
                {
                    "tipo": cd["tipo"],
                    "nome": cd["nome"],
                    "dias": dias,
                    "severity": "high",
                    "message": f"{cd['nome']}: vence em {dias} dias",
                }
            )
        elif dias <= 30:
            cert_alertas.append(
                {
                    "tipo": cd["tipo"],
                    "nome": cd["nome"],
                    "dias": dias,
                    "severity": "medium",
                    "message": f"{cd['nome']}: vence em {dias} dias",
                }
            )

    # Propostas
    props = await db.execute(
        text("""
        SELECT bp.id, bp.numero, bp.valor_total, bp.status, bp.ativo,
            bt.numero as edital_numero, bt.orgao_nome, bt.objeto_resumido
        FROM bidding_proposals bp
        LEFT JOIN bidding_tenders bt ON bp.tender_id = bt.id
        WHERE bp.ativo = true ORDER BY bp.created_at DESC
    """)
    )
    all_props = []
    for p in props.mappings().all():
        pd = dict(p)
        pd["id"] = str(pd["id"])
        pd["valor_total"] = float(pd["valor_total"]) if pd["valor_total"] else 0
        all_props.append(pd)

    # Stats
    participando = [t for t in all_tenders if t["participando"]]
    won = [t for t in all_tenders if t["status"] == "won"]
    lost = [t for t in all_tenders if t["status"] == "lost"]
    pipeline = sum(t["valor_estimado"] for t in participando if t["status"] not in ("won", "lost"))
    total_won = sum(t["valor_estimado"] for t in won)
    taxa = len(won) / (len(won) + len(lost)) * 100 if (len(won) + len(lost)) > 0 else 0

    return {
        "stats": {
            "total_editais": len(all_tenders),
            "participando": len(participando),
            "pipeline_valor": round(pipeline, 2),
            "ganhas": len(won),
            "perdidas": len(lost),
            "total_ganho": round(total_won, 2),
            "taxa_conversao": round(taxa, 1),
            "certidoes_validas": sum(1 for c in all_certs if c["dias_para_vencer"] > 0),
            "certidoes_total": len(all_certs),
        },
        "tenders": all_tenders,
        "certificates": all_certs,
        "proposals": all_props,
        "alertas": cert_alertas,
    }


@router.get("/headcount")
async def headcount_by_client(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Headcount por cliente com folha bruta e valor do contrato."""
    result = await db.execute(
        text("""
        SELECT
            g.id as client_id,
            g.name as cliente,
            (SELECT n2.tomador_cpf_cnpj FROM nfses n2 WHERE n2.condominio_id = g.id LIMIT 1) as cnpj,
            count(DISTINCT a.employee_id) as headcount,
            (SELECT sum(e2.salario_base)
             FROM employees e2
             WHERE e2.id IN (
                SELECT DISTINCT a2.employee_id
                FROM allocations a2
                JOIN posts p2 ON a2.post_id = p2.id
                WHERE p2.client_id::text = g.id::text
                AND a2.status = 'active' AND p2.is_active = true
                AND e2.is_active = true
             )
            ) as folha_bruta,
            COALESCE((
                SELECT sum(valor_servicos)
                FROM nfses
                WHERE condominio_id = g.id
                AND data_competencia = (
                    SELECT MAX(data_competencia) FROM nfses
                    WHERE condominio_id = g.id AND active = true
                )
            ), 0) as contrato_mensal
        FROM ged_clients g
        JOIN posts p ON p.client_id::text = g.id::text AND p.is_active = true
        JOIN allocations a ON a.post_id = p.id AND a.status = 'active'
        JOIN employees e ON e.id = a.employee_id AND e.is_active = true
        GROUP BY g.id, g.name
        ORDER BY count(DISTINCT a.employee_id) DESC
    """)
    )
    rows = result.mappings().all()

    total_headcount = sum(r["headcount"] for r in rows)
    total_folha = sum(float(r["folha_bruta"]) for r in rows)

    return {
        "total_headcount": total_headcount,
        "total_folha_bruta": round(total_folha, 2),
        "por_cliente": [
            {
                "client_id": str(r["client_id"]),
                "cliente": r["cliente"],
                "cnpj": r["cnpj"],
                "headcount": r["headcount"],
                "folha_bruta": round(float(r["folha_bruta"]), 2),
                "contrato_mensal": round(float(r["contrato_mensal"]), 2),
            }
            for r in rows
        ],
    }


@router.get("/bi/dashboard")
async def bi_dashboard(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dashboard Business Intelligence com KPIs executivos e indicadores."""
    kpis_result = await db.execute(
        text("""
        SELECT codigo, nome, category, unit, current_value, previous_value,
               target_value, variance_percentage, trend, history
        FROM executive_kpis
        WHERE ativo = true
        ORDER BY display_order
    """)
    )
    kpis = kpis_result.mappings().all()

    obrig_result = await db.execute(
        text("""
        SELECT tipo, nome, status, competencia_mes, competencia_ano,
               data_vencimento, valor_devido
        FROM fiscal_obligations
        WHERE active = true AND status = 'pendente'
        ORDER BY data_vencimento
    """)
    )
    obrigacoes = obrig_result.mappings().all()

    cumpridas = (
        await db.execute(text("SELECT count(*) FROM fiscal_obligations WHERE active = true AND status = 'cumprida'"))
    ).scalar() or 0

    return {
        "kpis": [
            {
                "codigo": k["codigo"],
                "nome": k["nome"],
                "categoria": k["category"],
                "unidade": k["unit"],
                "valor_atual": float(k["current_value"]) if k["current_value"] else 0,
                "valor_anterior": float(k["previous_value"]) if k["previous_value"] else 0,
                "meta": float(k["target_value"]) if k["target_value"] else 0,
                "variacao_pct": float(k["variance_percentage"]) if k["variance_percentage"] else 0,
                "tendencia": k["trend"],
                "historico": k["history"],
            }
            for k in kpis
        ],
        "fiscal": {
            "obrigacoes_cumpridas": cumpridas,
            "obrigacoes_pendentes": len(obrigacoes),
            "proximas": [
                {
                    "tipo": o["tipo"],
                    "nome": o["nome"],
                    "competencia": f"{o['competencia_mes']:02d}/{o['competencia_ano']}",
                    "vencimento": o["data_vencimento"].isoformat() if o["data_vencimento"] else None,
                    "valor": float(o["valor_devido"]) if o["valor_devido"] else 0,
                }
                for o in obrigacoes
            ],
        },
    }
