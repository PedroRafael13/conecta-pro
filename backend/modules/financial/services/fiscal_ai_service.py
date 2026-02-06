"""Servico de IA para modulo Fiscal - Analise, Otimizacao e Previsoes."""
# pylint: disable=too-many-locals,too-many-branches,too-many-statements
# pylint: disable=logging-fstring-interpolation,unused-argument

import logging
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.fiscal_obligation import calcular_das_anexo_iii
from modules.financial.repositories.fiscal_repository import FiscalRepository

logger = logging.getLogger(__name__)


class FiscalAIService:
    """Servico de IA para analise e otimizacao fiscal.

    Funcionalidades:
    - Analise de compliance fiscal
    - Otimizacao de carga tributaria
    - Previsao de obrigacoes
    - Deteccao de anomalias
    - Sugestoes de economia (liminar INSS, SUFRAMA)
    """

    def __init__(self, session: AsyncSession):
        """Inicializa o servico."""
        self.session = session
        self.repo = FiscalRepository(session)

    async def analisar_periodo(
        self,
        condominio_id: UUID,
        data_inicio: date,
        data_fim: date,
    ) -> Dict[str, Any]:
        """Analisa periodo fiscal e retorna insights.

        Args:
            condominio_id: ID do condominio
            data_inicio: Data inicial do periodo
            data_fim: Data final do periodo

        Returns:
            Analise completa com alertas, oportunidades e recomendacoes
        """
        logger.info(f"Analisando periodo fiscal {data_inicio} a {data_fim}")

        # Coleta dados
        nfes = await self.repo.get_nfes_periodo(condominio_id, data_inicio, data_fim)

        alertas = []
        oportunidades = []
        pendencias = []
        recomendacoes = []

        # Calcula resumo
        total_nfe = sum(nfe.valor_total_nota or Decimal("0") for nfe in nfes)

        # NFS-e por mes
        total_nfse = Decimal("0")
        total_retencoes = Decimal("0")
        economia_liminar = Decimal("0")

        mes_atual = data_inicio
        while mes_atual <= data_fim:
            nfses = await self.repo.get_nfses_competencia(
                condominio_id, mes_atual.month, mes_atual.year
            )
            for nfse in nfses:
                total_nfse += nfse.valor_servicos or Decimal("0")
                total_retencoes += (
                    (nfse.inss_valor or Decimal("0"))
                    + (nfse.ir_valor or Decimal("0"))
                    + (nfse.csll_valor or Decimal("0"))
                    + (nfse.pis_valor or Decimal("0"))
                    + (nfse.cofins_valor or Decimal("0"))
                )
                if nfse.inss_liminar_aplicada:
                    economia_liminar += nfse.valor_servicos * Decimal("0.11")

            # Proximo mes
            if mes_atual.month == 12:
                mes_atual = date(mes_atual.year + 1, 1, 1)
            else:
                mes_atual = date(mes_atual.year, mes_atual.month + 1, 1)

        # Analisa obrigacoes
        obrigacoes_pendentes = await self.repo.get_obrigacoes_pendentes(condominio_id)
        obrigacoes_atrasadas = await self.repo.get_obrigacoes_atrasadas(condominio_id)

        for obr in obrigacoes_atrasadas:
            alertas.append(
                {
                    "tipo": "obrigacao_atrasada",
                    "severidade": "alta",
                    "mensagem": (
                        f"{obr.tipo} competencia "
                        f"{obr.competencia_mes}/{obr.competencia_ano} atrasada"
                    ),
                    "dias_atraso": (date.today() - obr.data_vencimento).days,
                    "valor": float(obr.valor_devido or 0),
                }
            )

        for obr in obrigacoes_pendentes:
            dias = (obr.data_vencimento - date.today()).days
            if dias <= 5:
                alertas.append(
                    {
                        "tipo": "vencimento_proximo",
                        "severidade": "media",
                        "mensagem": f"{obr.tipo} vence em {dias} dias",
                        "vencimento": obr.data_vencimento.isoformat(),
                        "valor": float(obr.valor_devido or 0),
                    }
                )

        # Analisa uso de liminar INSS
        retencao_config = await self.repo.get_retencao_padrao_vigilancia(condominio_id)
        if retencao_config and retencao_config.inss_liminar_ativa:
            if economia_liminar > 0:
                oportunidades.append(
                    {
                        "tipo": "liminar_inss",
                        "mensagem": (
                            f"Economia com liminar INSS no periodo: "
                            f"R$ {float(economia_liminar):,.2f}"
                        ),
                        "economia": float(economia_liminar),
                        "observacao": (
                            "A liminar reconhece que retencao de 11% de INSS "
                            "caracteriza bitributacao para empresas do Simples Nacional Anexo III, "
                            "ja que o CPP esta incluso no DAS."
                        ),
                    }
                )
            else:
                recomendacoes.append(
                    "Verificar se todos os clientes estao aceitando a liminar de INSS. "
                    "A economia pode chegar a 11% do valor dos servicos."
                )

        # Analisa SUFRAMA
        suframa_config = await self.repo.get_suframa_config(condominio_id)
        if suframa_config:
            economia_zfm = await self.repo.get_economia_suframa_periodo(
                condominio_id, data_inicio, data_fim
            )
            if economia_zfm["total"] > 0:
                oportunidades.append(
                    {
                        "tipo": "suframa",
                        "mensagem": (
                            f"Economia com beneficios SUFRAMA: "
                            f"R$ {float(economia_zfm['total']):,.2f}"
                        ),
                        "detalhes": {
                            "ipi": float(economia_zfm["ipi"]),
                            "icms": float(economia_zfm["icms"]),
                            "pis_cofins": float(economia_zfm["pis_cofins"]),
                        },
                    }
                )

        # Verifica consistencia NFS-e vs DAS
        for mes in range(data_inicio.month, data_fim.month + 1):
            das = await self.repo.get_das_competencia(condominio_id, mes, data_inicio.year)
            nfses_mes = await self.repo.get_nfses_competencia(condominio_id, mes, data_inicio.year)
            receita_nfse = sum(n.valor_servicos or Decimal("0") for n in nfses_mes)

            if das and das.receita_bruta_mes != receita_nfse:
                alertas.append(
                    {
                        "tipo": "divergencia_das_nfse",
                        "severidade": "media",
                        "mensagem": (
                            f"Receita do DAS ({float(das.receita_bruta_mes)}) "
                            f"diverge das NFS-e ({float(receita_nfse)}) "
                            f"em {mes:02d}/{data_inicio.year}"
                        ),
                    }
                )

        # Pendencias
        for obr in obrigacoes_pendentes:
            pendencias.append(
                {
                    "tipo": obr.tipo,
                    "competencia": f"{obr.competencia_mes or ''}/{obr.competencia_ano}",
                    "vencimento": obr.data_vencimento.isoformat(),
                    "valor": float(obr.valor_devido or 0),
                    "status": obr.status,
                }
            )

        # Recomendacoes gerais
        if not suframa_config:
            recomendacoes.append(
                "Empresa em Manaus sem SUFRAMA configurado. "
                "Verificar se ha beneficios fiscais aplicaveis."
            )

        # Score de compliance
        score = 100
        score -= len(obrigacoes_atrasadas) * 20
        score -= len([a for a in alertas if a["severidade"] == "alta"]) * 10
        score -= len([a for a in alertas if a["severidade"] == "media"]) * 5
        score = max(0, min(100, score))

        return {
            "resumo_periodo": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "total_nfe": float(total_nfe),
                "total_nfse": float(total_nfse),
                "total_retencoes": float(total_retencoes),
                "economia_liminar": float(economia_liminar),
                "obrigacoes_pendentes": len(obrigacoes_pendentes),
                "obrigacoes_atrasadas": len(obrigacoes_atrasadas),
            },
            "alertas": alertas,
            "oportunidades": oportunidades,
            "pendencias": pendencias,
            "recomendacoes": recomendacoes,
            "score_compliance": score,
            "projecao_impostos": {
                "das_estimado": float(total_nfse * Decimal("0.06")),  # ~6% media
                "retencoes_estimadas": float(total_retencoes),
            },
        }

    async def otimizar_tributacao(
        self,
        condominio_id: UUID,
        receita_mensal_media: Decimal,
        tipo_servico: str = "vigilancia",
        uf_operacao: str = "AM",
    ) -> Dict[str, Any]:
        """Sugere otimizacoes tributarias.

        Para servicos de vigilancia em Manaus (Simples Anexo III):
        - ISS e CPP inclusos no DAS
        - Liminar INSS evita retencao de 11%
        - SUFRAMA pode trazer beneficios em compras
        """
        logger.info(f"Otimizando tributacao para receita R$ {receita_mensal_media}")

        receita_12_meses = receita_mensal_media * 12

        # Calcula DAS atual (Simples Anexo III)
        resultado_das = calcular_das_anexo_iii(
            receita_mensal_media,
            receita_12_meses,
        )

        carga_simples = resultado_das["aliquota_efetiva"]

        # Simula outros regimes
        regimes_simulados = []

        # Simples Nacional (atual)
        valor_das = resultado_das["valor_devido"]
        regimes_simulados.append(
            {
                "regime": "Simples Nacional - Anexo III",
                "aliquota_efetiva": float(carga_simples),
                "valor_mensal": float(valor_das),
                "observacoes": [
                    "ISS incluso no DAS",
                    "CPP (INSS patronal) incluso no DAS",
                    "Liminar pode eliminar retencao de 11% INSS",
                ],
                "vantagens": [
                    "Simplicidade na apuracao",
                    "Unificacao de tributos",
                    "Aliquota progressiva",
                ],
                "desvantagens": [
                    "Limite de faturamento R$ 4.8MM/ano",
                    "Nao pode creditar ICMS/IPI",
                ],
            }
        )

        # Lucro Presumido (simulacao)
        # PIS 0.65% + COFINS 3% + IRPJ 4.8% + CSLL 2.88% + ISS ~5%
        aliquota_lp = Decimal("16.33")
        valor_lp = receita_mensal_media * aliquota_lp / 100

        regimes_simulados.append(
            {
                "regime": "Lucro Presumido",
                "aliquota_efetiva": float(aliquota_lp),
                "valor_mensal": float(valor_lp),
                "observacoes": [
                    "ISS separado (~5%)",
                    "INSS patronal separado (~20%)",
                    "Retencoes na fonte",
                ],
                "vantagens": [
                    "Credito de PIS/COFINS sobre insumos",
                    "Sem limite de faturamento",
                ],
                "desvantagens": [
                    "Maior complexidade",
                    "Mais obrigacoes acessorias",
                    "INSS patronal adicional",
                ],
            }
        )

        # Melhor regime
        if carga_simples < aliquota_lp:
            melhor = "Simples Nacional - Anexo III"
            economia = (aliquota_lp - carga_simples) * receita_mensal_media / 100
        else:
            melhor = "Lucro Presumido"
            economia = (carga_simples - aliquota_lp) * receita_mensal_media / 100

        # Acoes recomendadas
        acoes = []

        # Liminar INSS
        retencao_config = await self.repo.get_retencao_padrao_vigilancia(condominio_id)
        if retencao_config and retencao_config.inss_liminar_ativa:
            economia_inss = receita_mensal_media * Decimal("0.11")
            acoes.append(
                f"Utilizar liminar de INSS com todos os clientes. "
                f"Economia potencial: R$ {float(economia_inss):,.2f}/mes"
            )
        else:
            acoes.append(
                "Avaliar obtencao de liminar para nao retencao de INSS. "
                "Economia potencial de 11% sobre servicos."
            )

        # SUFRAMA
        suframa = await self.repo.get_suframa_config(condominio_id)
        if suframa and suframa.is_vigente:
            acoes.append(
                "Aproveitar beneficios SUFRAMA em compras: "
                "isencao IPI, reducao ICMS, suspensao PIS/COFINS."
            )
        else:
            acoes.append(
                "Verificar elegibilidade para inscricao no SUFRAMA "
                "e aproveitamento de beneficios da Zona Franca."
            )

        # Fator R
        if receita_12_meses <= Decimal("4800000"):
            acoes.append(
                "Monitorar Fator R (folha/receita). "
                "Se >= 28%, pode migrar para Anexo III com ISS incluso."
            )

        return {
            "regime_atual": "Simples Nacional - Anexo III",
            "carga_tributaria_atual": float(carga_simples),
            "regimes_simulados": regimes_simulados,
            "melhor_regime": melhor,
            "economia_potencial": float(economia),
            "acoes_recomendadas": acoes,
        }

    async def prever_obrigacoes(
        self,
        condominio_id: UUID,
        meses_projecao: int = 6,
    ) -> Dict[str, Any]:
        """Preve obrigacoes fiscais futuras.

        Args:
            condominio_id: ID do condominio
            meses_projecao: Quantidade de meses para projetar

        Returns:
            Projecao de obrigacoes e valores
        """
        logger.info(f"Projetando {meses_projecao} meses de obrigacoes")

        hoje = date.today()
        projecao_mensal = []
        total_previsto = Decimal("0")
        obrigacoes_futuras = []
        alertas_vencimento = []

        # Busca media de receita dos ultimos 3 meses
        receita_media = Decimal("0")
        for i in range(1, 4):
            mes = hoje.month - i
            ano = hoje.year
            if mes <= 0:
                mes += 12
                ano -= 1

            nfses = await self.repo.get_nfses_competencia(condominio_id, mes, ano)
            for nfse in nfses:
                receita_media += nfse.valor_servicos or Decimal("0")

        receita_media = receita_media / 3

        # Busca receita 12 meses para calculo do DAS
        receita_12_meses = await self.repo.get_receita_12_meses(
            condominio_id, hoje.month, hoje.year
        )

        # Projeta cada mes
        for i in range(1, meses_projecao + 1):
            mes_proj = hoje.month + i
            ano_proj = hoje.year
            while mes_proj > 12:
                mes_proj -= 12
                ano_proj += 1

            # Calcula DAS projetado
            resultado_das = calcular_das_anexo_iii(
                receita_media,
                receita_12_meses,
            )

            # Data de vencimento do DAS: dia 20 do mes seguinte
            if mes_proj == 12:
                venc_das = date(ano_proj + 1, 1, 20)
            else:
                venc_das = date(ano_proj, mes_proj + 1, 20)

            mes_obrigacoes = []

            # DAS
            mes_obrigacoes.append(
                {
                    "tipo": "DAS",
                    "descricao": f"DAS Simples Nacional {mes_proj:02d}/{ano_proj}",
                    "vencimento": venc_das.isoformat(),
                    "valor_estimado": float(resultado_das["valor_devido"]),
                }
            )

            obrigacoes_futuras.append(
                {
                    "tipo": "DAS",
                    "competencia": f"{mes_proj:02d}/{ano_proj}",
                    "vencimento": venc_das.isoformat(),
                    "valor": float(resultado_das["valor_devido"]),
                }
            )

            total_previsto += resultado_das["valor_devido"]

            # GFIP/SEFIP (dia 7)
            venc_gfip = date(ano_proj, mes_proj, 7)
            if mes_proj == 1:
                venc_gfip = date(ano_proj, 1, 7)

            mes_obrigacoes.append(
                {
                    "tipo": "GFIP",
                    "descricao": f"GFIP {mes_proj:02d}/{ano_proj}",
                    "vencimento": venc_gfip.isoformat(),
                    "valor_estimado": 0,  # Declaratoria
                }
            )

            obrigacoes_futuras.append(
                {
                    "tipo": "GFIP",
                    "competencia": f"{mes_proj:02d}/{ano_proj}",
                    "vencimento": venc_gfip.isoformat(),
                    "valor": 0,
                }
            )

            projecao_mensal.append(
                {
                    "mes": mes_proj,
                    "ano": ano_proj,
                    "competencia": f"{mes_proj:02d}/{ano_proj}",
                    "receita_estimada": float(receita_media),
                    "das_estimado": float(resultado_das["valor_devido"]),
                    "aliquota_efetiva": float(resultado_das["aliquota_efetiva"]),
                    "obrigacoes": mes_obrigacoes,
                }
            )

        # Alertas de vencimento
        for obr in obrigacoes_futuras[:10]:
            venc = date.fromisoformat(obr["vencimento"])
            dias = (venc - hoje).days
            if dias <= 30:
                alertas_vencimento.append(
                    {
                        "tipo": obr["tipo"],
                        "competencia": obr["competencia"],
                        "vencimento": obr["vencimento"],
                        "dias_restantes": dias,
                        "valor": obr["valor"],
                    }
                )

        return {
            "projecao_mensal": projecao_mensal,
            "total_previsto": float(total_previsto),
            "obrigacoes_futuras": obrigacoes_futuras,
            "alertas_vencimento": alertas_vencimento,
        }

    async def detectar_anomalias(
        self,
        condominio_id: UUID,
        meses_analise: int = 6,
    ) -> List[Dict[str, Any]]:
        """Detecta anomalias em dados fiscais.

        Verifica:
        - Variacao brusca de receita
        - Notas com valores atipicos
        - Retencoes inconsistentes
        - CFOPs incorretos
        """
        logger.info(f"Detectando anomalias nos ultimos {meses_analise} meses")

        anomalias = []
        hoje = date.today()

        receitas_mensais = []

        for i in range(meses_analise):
            mes = hoje.month - i
            ano = hoje.year
            if mes <= 0:
                mes += 12
                ano -= 1

            nfses = await self.repo.get_nfses_competencia(condominio_id, mes, ano)
            receita_mes = sum(n.valor_servicos or Decimal("0") for n in nfses)
            receitas_mensais.append(
                {
                    "mes": mes,
                    "ano": ano,
                    "receita": receita_mes,
                }
            )

            # Verifica retencoes
            for nfse in nfses:
                # Verifica se liminar foi aplicada corretamente
                if nfse.inss_liminar_aplicada and nfse.inss_valor > 0:
                    anomalias.append(
                        {
                            "tipo": "retencao_inconsistente",
                            "severidade": "alta",
                            "descricao": (
                                f"NFS-e {nfse.numero_nfse or nfse.numero_rps} tem liminar "
                                f"marcada mas INSS retido: R$ {float(nfse.inss_valor)}"
                            ),
                            "competencia": f"{mes:02d}/{ano}",
                            "nfse_id": str(nfse.id),
                        }
                    )

                # Verifica ISS
                iss_esperado = nfse.valor_servicos * nfse.iss_aliquota / 100
                if nfse.iss_valor and abs(nfse.iss_valor - iss_esperado) > 1:
                    anomalias.append(
                        {
                            "tipo": "iss_divergente",
                            "severidade": "media",
                            "descricao": (
                                f"ISS calculado ({float(nfse.iss_valor)}) diverge do "
                                f"esperado ({float(iss_esperado)})"
                            ),
                            "competencia": f"{mes:02d}/{ano}",
                            "nfse_id": str(nfse.id),
                        }
                    )

        # Analisa variacao de receita
        if len(receitas_mensais) >= 3:
            media = sum(r["receita"] for r in receitas_mensais) / len(receitas_mensais)
            for r in receitas_mensais:
                if media > 0:
                    variacao = abs(r["receita"] - media) / media * 100
                    if variacao > 50:  # Variacao maior que 50%
                        anomalias.append(
                            {
                                "tipo": "variacao_receita",
                                "severidade": "media",
                                "descricao": (
                                    f"Receita de {r['mes']:02d}/{r['ano']} "
                                    f"(R$ {float(r['receita']):,.2f}) "
                                    f"varia {variacao:.1f}% da media"
                                ),
                                "competencia": f"{r['mes']:02d}/{r['ano']}",
                                "variacao_percentual": float(variacao),
                            }
                        )

        return anomalias

    async def sugerir_economia(
        self,
        condominio_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Sugere acoes para economia tributaria.

        Baseado no contexto:
        - Empresa de vigilancia em Manaus
        - Simples Nacional Anexo III
        - Possui liminar de INSS
        - Tem SUFRAMA
        """
        sugestoes = []

        # Verifica liminar INSS
        retencao = await self.repo.get_retencao_padrao_vigilancia(condominio_id)
        if retencao:
            if retencao.inss_liminar_ativa:
                # Calcula economia potencial
                hoje = date.today()
                receita_12 = await self.repo.get_receita_12_meses(
                    condominio_id, hoje.month, hoje.year
                )
                economia_anual = receita_12 * Decimal("0.11")

                sugestoes.append(
                    {
                        "tipo": "liminar_inss",
                        "titulo": "Ampliar uso da Liminar de INSS",
                        "descricao": (
                            "A liminar federal reconhece que empresas do Simples Nacional "
                            "Anexo III ja pagam CPP embutido no DAS, tornando a retencao "
                            "de 11% na nota uma bitributacao ilegal."
                        ),
                        "economia_potencial": float(economia_anual),
                        "acao": (
                            "Orientar comercial a informar todos os clientes sobre a liminar. "
                            f"Numero: {retencao.inss_liminar_numero}"
                        ),
                        "impacto": "alto",
                    }
                )
            else:
                sugestoes.append(
                    {
                        "tipo": "liminar_inss",
                        "titulo": "Obter Liminar de INSS",
                        "descricao": (
                            "Empresas do Simples Nacional Anexo III podem conseguir liminar "
                            "para nao ter retencao de 11% de INSS, pois caracteriza bitributacao."
                        ),
                        "economia_potencial": None,
                        "acao": "Consultar advogado tributarista para peticionamento.",
                        "impacto": "alto",
                    }
                )

        # Verifica SUFRAMA
        suframa = await self.repo.get_suframa_config(condominio_id)
        if suframa and suframa.is_vigente:
            sugestoes.append(
                {
                    "tipo": "suframa",
                    "titulo": "Maximizar Beneficios SUFRAMA",
                    "descricao": (
                        "A inscricao no SUFRAMA permite isencao de IPI, "
                        "reducao de ICMS e suspensao de PIS/COFINS em compras."
                    ),
                    "economia_potencial": None,
                    "acao": (
                        "Priorizar fornecedores que trabalham com os beneficios ZFM. "
                        "Verificar PIN (Protocolo de Internamento) em todas as compras."
                    ),
                    "impacto": "medio",
                }
            )

            # Alerta de vencimento
            dias_venc = (suframa.data_validade - date.today()).days
            if dias_venc <= 90:
                sugestoes.append(
                    {
                        "tipo": "suframa_vencimento",
                        "titulo": "Renovar Inscricao SUFRAMA",
                        "descricao": f"A inscricao SUFRAMA vence em {dias_venc} dias.",
                        "economia_potencial": None,
                        "acao": "Providenciar renovacao junto a SUFRAMA.",
                        "impacto": "alto",
                    }
                )
        else:
            sugestoes.append(
                {
                    "tipo": "suframa",
                    "titulo": "Avaliar Inscricao no SUFRAMA",
                    "descricao": (
                        "Empresas em Manaus podem se beneficiar da Zona Franca. "
                        "Verificar elegibilidade para inscricao."
                    ),
                    "economia_potencial": None,
                    "acao": "Consultar contador sobre processo de inscricao.",
                    "impacto": "medio",
                }
            )

        # Sugestao de planejamento
        sugestoes.append(
            {
                "tipo": "planejamento",
                "titulo": "Monitorar Faixa do Simples",
                "descricao": (
                    "A aliquota efetiva do Simples varia conforme a receita acumulada. "
                    "Monitorar para evitar saltos de faixa."
                ),
                "economia_potencial": None,
                "acao": (
                    "Acompanhar RBT12 mensalmente. "
                    "Considerar distribuicao de faturamento se proximo do limite."
                ),
                "impacto": "medio",
            }
        )

        return sugestoes

    async def calcular_economia_total(
        self,
        condominio_id: UUID,
        ano: int,
    ) -> Dict[str, Any]:
        """Calcula economia total obtida no ano.

        Soma:
        - Economia com liminar INSS
        - Economia com beneficios SUFRAMA
        """
        economia = {
            "ano": ano,
            "liminar_inss": Decimal("0"),
            "suframa_ipi": Decimal("0"),
            "suframa_icms": Decimal("0"),
            "suframa_pis_cofins": Decimal("0"),
            "total": Decimal("0"),
        }

        # Liminar INSS
        for mes in range(1, 13):
            nfses = await self.repo.get_nfses_competencia(condominio_id, mes, ano)
            for nfse in nfses:
                if nfse.inss_liminar_aplicada:
                    economia["liminar_inss"] += nfse.valor_servicos * Decimal("0.11")

        # SUFRAMA
        suframa_eco = await self.repo.get_economia_suframa_periodo(
            condominio_id,
            date(ano, 1, 1),
            date(ano, 12, 31),
        )
        economia["suframa_ipi"] = suframa_eco["ipi"]
        economia["suframa_icms"] = suframa_eco["icms"]
        economia["suframa_pis_cofins"] = suframa_eco["pis_cofins"]

        economia["total"] = (
            economia["liminar_inss"]
            + economia["suframa_ipi"]
            + economia["suframa_icms"]
            + economia["suframa_pis_cofins"]
        )

        return {k: float(v) if isinstance(v, Decimal) else v for k, v in economia.items()}
