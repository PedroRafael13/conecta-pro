"""Dashboard consolidado multi-empresa — dados REAIS do banco."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user, get_tenant_id
from core.database import get_db
from modules.empresas.agents.obligations_monitor import ObligationsMonitorAgent
from modules.empresas.models.empresa import Empresa, Liminar
from modules.financial.agents.profitability_analyzer import ProfitabilityAnalyzerAgent
from modules.financial.agents.tax_calculator import TaxCalculatorAgent

router = APIRouter(prefix="/dashboard", tags=["Dashboard Multi-Empresa"])
_tax = TaxCalculatorAgent()
_profit = ProfitabilityAnalyzerAgent()
_obs = ObligationsMonitorAgent()
_DEFAULT_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


async def _resolve_condominio_id(db: AsyncSession, condominio_id: UUID) -> UUID:
    """Resolve tenant padrão para o condominio real do banco."""
    if condominio_id == _DEFAULT_TENANT_ID:
        result = await db.execute(text("SELECT id FROM condominios LIMIT 1"))
        row = result.fetchone()
        if row:
            return UUID(str(row[0]))
    return condominio_id


def _inferir_empresa_por_tipo(tipo_servico: str, empresas: list[Empresa]) -> Empresa | None:
    """Infere qual empresa presta um tipo de servico baseado em tipos_servicos cadastrados."""
    for emp in empresas:
        tipos = emp.tipos_servicos or []
        if tipo_servico in tipos:
            return emp
    return None


async def _buscar_empresas(db: AsyncSession, condominio_id: UUID) -> list[dict]:
    """Busca empresas com liminares ativas."""
    stmt = select(Empresa).where(Empresa.condominio_id == condominio_id).order_by(Empresa.is_principal.desc())
    result = await db.execute(stmt)
    empresas = list(result.scalars().all())

    dados = []
    for emp in empresas:
        # Buscar liminares concedidas
        lim_stmt = select(Liminar).where(and_(Liminar.empresa_id == emp.id, Liminar.status == "concedida"))
        lim_result = await db.execute(lim_stmt)
        liminares_ativas = [lim.tipo for lim in lim_result.scalars().all()]

        dados.append(
            {
                "empresa": emp,
                "liminares_ativas": liminares_ativas,
            }
        )
    return dados


async def _receita_por_empresa(db: AsyncSession, empresas: list[Empresa], mes: int, ano: int) -> dict[str, dict]:
    """Calcula receita real por empresa, buscando de contratos e NFS-e."""
    receitas: dict[str, dict] = {}

    for emp in empresas:
        slug = emp.slug
        receitas[slug] = {
            "contratos_ativos": 0,
            "valor_mensal_contratos": Decimal("0"),
            "nfse_emitidas": 0,
            "valor_nfse": Decimal("0"),
            "postos_ativos": 0,
            "fonte": "sem_dados",
        }

        # 1. Buscar contratos ativos por tipo de servico desta empresa
        tipos = emp.tipos_servicos or []
        if tipos:
            try:
                contratos_sql = text("""
                    SELECT COUNT(*) as total, COALESCE(SUM(monthly_value), 0) as valor
                    FROM client_contracts
                    WHERE status = 'active'
                    AND service_type::text = ANY(:tipos)
                """)
                r = await db.execute(contratos_sql, {"tipos": tipos})
                row = r.fetchone()
                if row and row[0] > 0:
                    receitas[slug]["contratos_ativos"] = row[0]
                    receitas[slug]["valor_mensal_contratos"] = Decimal(str(row[1]))
                    receitas[slug]["fonte"] = "contratos"
            except Exception:
                await db.rollback()  # Reset transaction after enum error

        # 2. Buscar NFS-e emitidas por CNPJ desta empresa no mes/ano
        if emp.cnpj:
            cnpj_limpo = emp.cnpj.replace(".", "").replace("/", "").replace("-", "")
            nfse_sql = text("""
                SELECT COUNT(*) as total, COALESCE(SUM(valor_servicos), 0) as valor
                FROM nfses
                WHERE (prestador_cnpj = :cnpj OR prestador_cnpj = :cnpj_limpo)
                AND EXTRACT(MONTH FROM data_competencia) = :mes
                AND EXTRACT(YEAR FROM data_competencia) = :ano
                AND status != 'cancelada'
            """)
            r = await db.execute(
                nfse_sql,
                {
                    "cnpj": emp.cnpj,
                    "cnpj_limpo": cnpj_limpo,
                    "mes": mes,
                    "ano": ano,
                },
            )
            row = r.fetchone()
            if row and row[0] > 0:
                receitas[slug]["nfse_emitidas"] = row[0]
                receitas[slug]["valor_nfse"] = Decimal(str(row[1]))
                if receitas[slug]["fonte"] == "sem_dados":
                    receitas[slug]["fonte"] = "nfse"
                else:
                    receitas[slug]["fonte"] = "contratos+nfse"

        # 3. Contar postos ativos por tipo de servico desta empresa
        if tipos:
            try:
                postos_sql = text("""
                    SELECT COUNT(*) FROM posts
                    WHERE status = 'active' AND post_type::text = ANY(:tipos)
                """)
                r = await db.execute(postos_sql, {"tipos": tipos})
                row = r.fetchone()
                if row:
                    receitas[slug]["postos_ativos"] = row[0]
            except Exception:
                await db.rollback()

    return receitas


def _melhor_receita(dados_empresa: dict) -> Decimal:
    """Retorna a melhor estimativa de receita: contratos > nfse > 0."""
    if dados_empresa["valor_mensal_contratos"] > 0:
        return dados_empresa["valor_mensal_contratos"]
    if dados_empresa["valor_nfse"] > 0:
        return dados_empresa["valor_nfse"]
    return Decimal("0")


@router.get("/fiscal/grupo")
async def dashboard_fiscal_grupo(
    mes: int = Query(default=date.today().month),
    ano: int = Query(default=date.today().year),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dashboard fiscal consolidado do grupo — dados reais."""
    condominio_id = await _resolve_condominio_id(db, UUID(get_tenant_id(current_user)))
    empresas_dados = await _buscar_empresas(db, condominio_id)

    if not empresas_dados:
        return {
            "periodo": f"{mes:02d}/{ano}",
            "status": "sem_dados",
            "mensagem": "Nenhuma empresa cadastrada. Cadastre empresas em Multi-Empresa > Gestao.",
        }

    empresas = [e["empresa"] for e in empresas_dados]
    receitas = await _receita_por_empresa(db, empresas, mes, ano)

    resultado_empresas = {}
    total_receita = Decimal("0")
    total_impostos = Decimal("0")
    total_economia_liminares = Decimal("0")

    for ed in empresas_dados:
        emp = ed["empresa"]
        liminares = ed["liminares_ativas"]
        slug = emp.slug
        rec = receitas.get(slug, {})
        receita_mes = _melhor_receita(rec)
        total_receita += receita_mes

        empresa_result = {
            "slug": slug,
            "razao_social": emp.razao_social,
            "cnpj": emp.cnpj,
            "regime": emp.regime_tributario,
            "status": emp.status,
            "receita_mes": float(receita_mes),
            "fonte_receita": rec.get("fonte", "sem_dados"),
            "contratos_ativos": rec.get("contratos_ativos", 0),
            "nfse_emitidas": rec.get("nfse_emitidas", 0),
            "postos_ativos": rec.get("postos_ativos", 0),
        }

        # Calcular impostos apenas se houver receita
        if receita_mes > 0:
            if emp.regime_tributario == "lucro_real":
                lr = _tax.calcular_lucro_real(
                    receita_mes=receita_mes,
                    receita_trimestre=receita_mes * 3,
                )
                empresa_result["impostos_mes"] = float(lr.total_impostos_mes)
                empresa_result["carga_pct"] = float(lr.carga_tributaria_percentual)
                empresa_result["detalhamento"] = {
                    "irpj": float(lr.irpj + lr.irpj_adicional),
                    "csll": float(lr.csll),
                    "pis": float(lr.pis),
                    "cofins": float(lr.cofins),
                    "iss": float(lr.iss),
                }
                total_impostos += lr.total_impostos_mes

            elif emp.regime_tributario == "simples_nacional":
                rbt12 = receita_mes * 12
                sn = _tax.calcular_simples(
                    receita_mes=receita_mes,
                    rbt12=rbt12,
                    liminares=[],
                )
                empresa_result["impostos_sem_liminar"] = float(sn.valor_das)
                empresa_result["carga_pct_sem"] = float(sn.carga_tributaria_percentual)

                if liminares:
                    sn_lim = _tax.calcular_simples(
                        receita_mes=receita_mes,
                        rbt12=rbt12,
                        liminares=liminares,
                    )
                    empresa_result["impostos_com_liminar"] = float(sn_lim.valor_das)
                    empresa_result["carga_pct_com"] = float(sn_lim.carga_tributaria_percentual)
                    economia = sn.valor_das - sn_lim.valor_das
                    empresa_result["economia_liminar"] = float(economia)
                    total_economia_liminares += economia
                    total_impostos += sn_lim.valor_das
                else:
                    total_impostos += sn.valor_das

                empresa_result["liminares_ativas"] = liminares
                empresa_result["status_liminares"] = "ativas" if liminares else "nenhuma_concedida"
        else:
            empresa_result["impostos_mes"] = 0
            empresa_result["carga_pct"] = 0
            empresa_result["aviso"] = "Sem receita registrada. Cadastre contratos ou emita NFS-e."

        resultado_empresas[slug] = empresa_result

    # Obrigacoes do mes
    cal = _obs.gerar_calendario_grupo(mes, ano)

    return {
        "periodo": f"{mes:02d}/{ano}",
        "status": "com_dados" if total_receita > 0 else "sem_receita",
        "grupo": {
            "total_empresas": len(empresas),
            "total_receita_mes": float(total_receita),
            "total_impostos_mes": float(total_impostos),
            "economia_liminares": float(total_economia_liminares),
            "fonte": "dados_reais",
        },
        "empresas": resultado_empresas,
        "obrigacoes_mes": {
            "total": cal.total_obrigacoes,
            "criticas": cal.criticas,
            "atrasadas": cal.atrasadas,
            "pendentes": cal.pendentes,
        },
    }


@router.get("/rentabilidade/grupo")
async def dashboard_rentabilidade_grupo(
    mes: int = Query(default=date.today().month),
    ano: int = Query(default=date.today().year),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dashboard de rentabilidade consolidado — dados reais."""
    condominio_id = await _resolve_condominio_id(db, UUID(get_tenant_id(current_user)))
    empresas_dados = await _buscar_empresas(db, condominio_id)

    if not empresas_dados:
        return {
            "status": "sem_dados",
            "mensagem": "Nenhuma empresa cadastrada.",
        }

    empresas = [e["empresa"] for e in empresas_dados]
    receitas = await _receita_por_empresa(db, empresas, mes, ano)

    # Buscar custos reais de folha por tipo de servico
    custos_sql = text("""
        SELECT post_type,
               COUNT(*) as postos,
               COALESCE(SUM(monthly_cost), 0) as custo_total,
               COALESCE(SUM(current_headcount), 0) as headcount
        FROM posts
        WHERE status = 'active' AND monthly_cost > 0
        GROUP BY post_type
    """)
    custos_result = await db.execute(custos_sql)
    custos_por_tipo = {
        row[0]: {"postos": row[1], "custo": Decimal(str(row[2])), "headcount": row[3]}
        for row in custos_result.fetchall()
    }

    resultados = []
    for ed in empresas_dados:
        emp = ed["empresa"]
        liminares = ed["liminares_ativas"]
        tipos = emp.tipos_servicos or []

        for tipo in tipos:
            rec = receitas.get(emp.slug, {})
            receita_tipo = _melhor_receita(rec)

            # Se ha varios tipos, distribuir proporcionalmente
            if len(tipos) > 1 and receita_tipo > 0:
                receita_tipo = receita_tipo / len(tipos)

            custo_info = custos_por_tipo.get(tipo, {})
            custo_direto = custo_info.get("custo", Decimal("0"))

            if receita_tipo > 0 or custo_direto > 0:
                rbt12 = receita_tipo * 12 if receita_tipo > 0 else Decimal("1500000")
                r = _profit.calcular_rentabilidade(
                    receita_bruta_mes=receita_tipo,
                    custo_direto_mes=custo_direto,
                    custo_indireto_mes=custo_direto * Decimal("0.15"),
                    tipo_servico=tipo,
                    empresa_slug=emp.slug,
                    regime=emp.regime_tributario,
                    rbt12=rbt12,
                    liminares=liminares,
                )
                resultados.append(
                    {
                        "tipo_servico": tipo,
                        "empresa": emp.slug,
                        "regime": emp.regime_tributario,
                        "receita_mes": float(r.receita_bruta_mes),
                        "custo_direto": float(custo_direto),
                        "impostos_mes": float(r.impostos_mes),
                        "lucro_liquido_mes": float(r.lucro_liquido_mes),
                        "margem_pct": float(r.margem_liquida_percentual),
                        "situacao": r.situacao,
                        "alertas": r.alertas,
                        "postos_ativos": custo_info.get("postos", 0),
                        "headcount": custo_info.get("headcount", 0),
                        "fonte": "dados_reais",
                    }
                )

    if not resultados:
        return {
            "status": "sem_dados",
            "mensagem": "Sem contratos ou postos com custo cadastrado. Cadastre contratos e configure custos nos postos.",
            "resumo_grupo": {
                "total_receita_mes": 0,
                "total_lucro_liquido_mes": 0,
                "margem_media_pct": 0,
            },
            "por_contrato": [],
            "ranking": [],
            "alertas": [],
        }

    total_receita = sum(r["receita_mes"] for r in resultados)
    total_lucro = sum(r["lucro_liquido_mes"] for r in resultados)
    margem_media = (total_lucro / total_receita * 100) if total_receita else 0

    return {
        "status": "com_dados",
        "resumo_grupo": {
            "total_receita_mes": total_receita,
            "total_lucro_liquido_mes": total_lucro,
            "margem_media_pct": round(margem_media, 2),
            "total_receita_anual_estimada": total_receita * 12,
        },
        "por_contrato": resultados,
        "ranking": sorted(resultados, key=lambda x: x["margem_pct"], reverse=True),
        "alertas": [a for r in resultados for a in r["alertas"]],
    }


@router.get("/contabil/grupo")
async def dashboard_contabil_grupo(
    mes: int = Query(default=date.today().month),
    ano: int = Query(default=date.today().year),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Dashboard contabil consolidado — dados reais."""
    condominio_id = await _resolve_condominio_id(db, UUID(get_tenant_id(current_user)))
    empresas_dados = await _buscar_empresas(db, condominio_id)

    if not empresas_dados:
        return {
            "periodo": f"{mes:02d}/{ano}",
            "status": "sem_dados",
            "mensagem": "Nenhuma empresa cadastrada.",
        }

    empresas = [e["empresa"] for e in empresas_dados]
    receitas = await _receita_por_empresa(db, empresas, mes, ano)

    # Buscar lancamentos contabeis do periodo
    lancamentos_sql = text("""
        SELECT
            COALESCE(SUM(CASE WHEN ja.code LIKE '3%%' THEN jel.credit_amount ELSE 0 END), 0) as receita,
            COALESCE(SUM(CASE WHEN ja.code LIKE '4%%' THEN jel.debit_amount ELSE 0 END), 0) as despesas,
            COALESCE(SUM(CASE WHEN ja.code LIKE '5%%' THEN jel.debit_amount ELSE 0 END), 0) as impostos,
            COUNT(DISTINCT je.id) as total_lancamentos
        FROM fin_journal_entries je
        JOIN fin_journal_entry_lines jel ON jel.journal_entry_id = je.id
        JOIN fin_accounting_accounts ja ON ja.id = jel.account_id
        WHERE EXTRACT(MONTH FROM je.entry_date) = :mes
        AND EXTRACT(YEAR FROM je.entry_date) = :ano
    """)
    r = await db.execute(lancamentos_sql, {"mes": mes, "ano": ano})
    contabil = r.fetchone()

    receita_contabil = Decimal(str(contabil[0])) if contabil and contabil[0] else Decimal("0")
    despesas_contabil = Decimal(str(contabil[1])) if contabil and contabil[1] else Decimal("0")
    impostos_contabil = Decimal(str(contabil[2])) if contabil and contabil[2] else Decimal("0")
    total_lancamentos = contabil[3] if contabil else 0

    # Se nao ha lancamentos contabeis, usar receita de contratos/NFS-e
    total_receita_real = Decimal("0")
    for emp in empresas:
        rec = receitas.get(emp.slug, {})
        total_receita_real += _melhor_receita(rec)

    receita_final = receita_contabil if receita_contabil > 0 else total_receita_real
    lucro = receita_final - despesas_contabil - impostos_contabil
    margem = float(lucro / receita_final * 100) if receita_final > 0 else 0

    por_empresa = {}
    for ed in empresas_dados:
        emp = ed["empresa"]
        rec = receitas.get(emp.slug, {})
        receita_emp = _melhor_receita(rec)
        por_empresa[emp.slug] = {
            "razao_social": emp.razao_social,
            "regime": emp.regime_tributario,
            "receita_mes": float(receita_emp),
            "fonte_receita": rec.get("fonte", "sem_dados"),
            "postos_ativos": rec.get("postos_ativos", 0),
            "contratos_ativos": rec.get("contratos_ativos", 0),
            "nfse_emitidas": rec.get("nfse_emitidas", 0),
        }

    # Proxima exportacao para contador
    proximo_mes = mes + 1 if mes < 12 else 1
    proximo_ano = ano if mes < 12 else ano + 1

    tem_dados = receita_final > 0 or total_lancamentos > 0

    return {
        "periodo": f"{mes:02d}/{ano}",
        "status": "com_dados" if tem_dados else "sem_dados",
        "mensagem": None
        if tem_dados
        else "Sem lancamentos contabeis ou receita no periodo. Cadastre contratos, emita NFS-e ou registre lancamentos.",
        "grupo_consolidado": {
            "receita_bruta": float(receita_final),
            "despesas": float(despesas_contabil),
            "impostos": float(impostos_contabil),
            "lucro_liquido": float(lucro),
            "margem_liquida_pct": round(margem, 2),
            "total_lancamentos": total_lancamentos,
            "fonte": "contabilidade"
            if receita_contabil > 0
            else ("contratos" if total_receita_real > 0 else "sem_dados"),
        },
        "por_empresa": por_empresa,
        "exportacao_contador": {
            "formato": "Dominio Sistemas (TOTVS)",
            "ultima_exportacao": None,
            "proxima_exportacao": f"05/{proximo_mes:02d}/{proximo_ano}",
            "status": "pendente",
        },
    }
