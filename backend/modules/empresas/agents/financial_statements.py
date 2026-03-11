"""
FinancialStatementsAgent — DRE, Balanço Patrimonial e DFC por empresa
Gera demonstrativos financeiros consolidados e por empresa.
"""

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class FinancialStatementsAgent:
    """Gera demonstrativos financeiros DRE, BP e DFC"""

    def gerar_dre(
        self,
        empresa_slug: str,
        periodo: str,
        dados: dict,
        regime: str = "lucro_real",
    ) -> dict:
        """
        Demonstração de Resultado do Exercício completo.
        dados esperados: receita_bruta, deducoes, custos (dict), despesas (dict), outros (dict)
        """
        try:
            receita_bruta = Decimal(str(dados.get("receita_bruta", 0)))
            deducoes = Decimal(str(dados.get("deducoes", 0)))  # ISS, PIS, COFINS sobre receita
            receita_liquida = receita_bruta - deducoes

            # Custos
            custos = dados.get("custos", {})
            total_custos = sum(Decimal(str(v)) for v in custos.values())
            lucro_bruto = receita_liquida - total_custos

            # Despesas operacionais
            despesas = dados.get("despesas", {})
            total_despesas = sum(Decimal(str(v)) for v in despesas.values())
            ebit = lucro_bruto - total_despesas  # LAJIR

            # Outros (financeiros, não-operacionais)
            outros = dados.get("outros", {})
            receitas_financeiras = Decimal(str(outros.get("receitas_financeiras", 0)))
            despesas_financeiras = Decimal(str(outros.get("despesas_financeiras", 0)))
            resultado_financeiro = receitas_financeiras - despesas_financeiras
            lair = ebit + resultado_financeiro  # LAIR

            # Impostos sobre lucro
            if regime == "lucro_real":
                irpj = lair * Decimal("0.15") if lair > 0 else Decimal("0")
                adicional_irpj = max(Decimal("0"), (lair - Decimal("240000")) / 12 * Decimal("0.10"))
                csll = lair * Decimal("0.09") if lair > 0 else Decimal("0")
                total_impostos_lucro = irpj + adicional_irpj + csll
            else:
                total_impostos_lucro = Decimal(str(dados.get("das", 0)))

            lucro_liquido = lair - total_impostos_lucro

            margem_bruta = float(lucro_bruto / receita_bruta * 100) if receita_bruta > 0 else 0
            margem_ebit = float(ebit / receita_bruta * 100) if receita_bruta > 0 else 0
            margem_liquida = float(lucro_liquido / receita_bruta * 100) if receita_bruta > 0 else 0

            # Ponto de equilíbrio
            ponto_equilibrio = 0.0
            if receita_liquida > total_custos and receita_liquida > 0:
                margem_contribuicao = float(receita_liquida - total_custos) / float(receita_liquida)
                if margem_contribuicao > 0:
                    ponto_equilibrio = float(total_despesas) / margem_contribuicao

            return {
                "sucesso": True,
                "empresa": empresa_slug,
                "periodo": periodo,
                "regime": regime,
                "dre": {
                    "receita_bruta": float(receita_bruta),
                    "deducoes": float(deducoes),
                    "receita_liquida": float(receita_liquida),
                    "custos": {k: float(Decimal(str(v))) for k, v in custos.items()},
                    "total_custos": float(total_custos),
                    "lucro_bruto": float(lucro_bruto),
                    "margem_bruta_pct": round(margem_bruta, 2),
                    "despesas_operacionais": {k: float(Decimal(str(v))) for k, v in despesas.items()},
                    "total_despesas": float(total_despesas),
                    "ebit_lajir": float(ebit),
                    "margem_ebit_pct": round(margem_ebit, 2),
                    "resultado_financeiro": float(resultado_financeiro),
                    "lair": float(lair),
                    "impostos_sobre_lucro": float(total_impostos_lucro),
                    "lucro_liquido": float(lucro_liquido),
                    "margem_liquida_pct": round(margem_liquida, 2),
                },
                "indicadores": {
                    "classificacao": self._classificar(margem_liquida),
                    "ponto_equilibrio": round(ponto_equilibrio, 2),
                },
            }
        except Exception as e:
            logger.error(f"Erro ao gerar DRE: {e}")
            return {"sucesso": False, "erro": str(e)}

    def gerar_balanco_sintetico(
        self,
        empresa_slug: str,
        data_base: str,
        dados: dict,
    ) -> dict:
        """Balanço Patrimonial sintético"""
        try:
            # ATIVO
            ativo_circulante = dados.get("ativo_circulante", {})
            ativo_nao_circulante = dados.get("ativo_nao_circulante", {})
            total_ativo_circ = sum(Decimal(str(v)) for v in ativo_circulante.values())
            total_ativo_nao_circ = sum(Decimal(str(v)) for v in ativo_nao_circulante.values())
            total_ativo = total_ativo_circ + total_ativo_nao_circ

            # PASSIVO
            passivo_circulante = dados.get("passivo_circulante", {})
            passivo_nao_circulante = dados.get("passivo_nao_circulante", {})
            patrimonio_liquido = dados.get("patrimonio_liquido", {})
            total_passivo_circ = sum(Decimal(str(v)) for v in passivo_circulante.values())
            total_passivo_nao_circ = sum(Decimal(str(v)) for v in passivo_nao_circulante.values())
            total_pl = sum(Decimal(str(v)) for v in patrimonio_liquido.values())
            total_passivo = total_passivo_circ + total_passivo_nao_circ + total_pl

            balanceado = abs(total_ativo - total_passivo) < Decimal("0.01")

            liquidez_corrente = float(total_ativo_circ / total_passivo_circ) if total_passivo_circ > 0 else 0
            endividamento_pct = (
                float((total_passivo_circ + total_passivo_nao_circ) / total_ativo * 100) if total_ativo > 0 else 0
            )

            return {
                "sucesso": True,
                "empresa": empresa_slug,
                "data_base": data_base,
                "balanco": {
                    "ativo": {
                        "circulante": {k: float(Decimal(str(v))) for k, v in ativo_circulante.items()},
                        "total_circulante": float(total_ativo_circ),
                        "nao_circulante": {k: float(Decimal(str(v))) for k, v in ativo_nao_circulante.items()},
                        "total_nao_circulante": float(total_ativo_nao_circ),
                        "total_ativo": float(total_ativo),
                    },
                    "passivo": {
                        "circulante": {k: float(Decimal(str(v))) for k, v in passivo_circulante.items()},
                        "total_circulante": float(total_passivo_circ),
                        "nao_circulante": {k: float(Decimal(str(v))) for k, v in passivo_nao_circulante.items()},
                        "total_nao_circulante": float(total_passivo_nao_circ),
                        "patrimonio_liquido": {k: float(Decimal(str(v))) for k, v in patrimonio_liquido.items()},
                        "total_pl": float(total_pl),
                        "total_passivo": float(total_passivo),
                    },
                },
                "balanceado": balanceado,
                "indicadores": {
                    "liquidez_corrente": round(liquidez_corrente, 2),
                    "endividamento_pct": round(endividamento_pct, 2),
                },
            }
        except Exception as e:
            logger.error(f"Erro ao gerar Balanço: {e}")
            return {"sucesso": False, "erro": str(e)}

    def gerar_dfc_indireto(
        self,
        empresa_slug: str,
        periodo: str,
        dados: dict,
    ) -> dict:
        """Demonstração de Fluxo de Caixa — método indireto"""
        try:
            lucro_liquido = Decimal(str(dados.get("lucro_liquido", 0)))

            # Ajustes ao lucro líquido
            depreciacao = Decimal(str(dados.get("depreciacao", 0)))
            amortizacao = Decimal(str(dados.get("amortizacao", 0)))
            variacao_contas_receber = Decimal(str(dados.get("variacao_contas_receber", 0)))
            variacao_fornecedores = Decimal(str(dados.get("variacao_fornecedores", 0)))
            variacao_obrigacoes_trab = Decimal(str(dados.get("variacao_obrigacoes_trabalhistas", 0)))
            variacao_impostos = Decimal(str(dados.get("variacao_impostos", 0)))

            # Atividades operacionais
            fluxo_operacional = (
                lucro_liquido
                + depreciacao
                + amortizacao
                - variacao_contas_receber
                + variacao_fornecedores
                + variacao_obrigacoes_trab
                + variacao_impostos
            )

            # Atividades de investimento
            aquisicao_imobilizado = Decimal(str(dados.get("aquisicao_imobilizado", 0)))
            fluxo_investimento = -aquisicao_imobilizado

            # Atividades de financiamento
            emprestimos = Decimal(str(dados.get("emprestimos_obtidos", 0)))
            amortizacao_emprestimos = Decimal(str(dados.get("amortizacao_emprestimos", 0)))
            distribuicao_lucros = Decimal(str(dados.get("distribuicao_lucros", 0)))
            fluxo_financiamento = emprestimos - amortizacao_emprestimos - distribuicao_lucros

            variacao_caixa = fluxo_operacional + fluxo_investimento + fluxo_financiamento
            saldo_inicial = Decimal(str(dados.get("saldo_caixa_inicial", 0)))
            saldo_final = saldo_inicial + variacao_caixa

            return {
                "sucesso": True,
                "empresa": empresa_slug,
                "periodo": periodo,
                "dfc": {
                    "atividades_operacionais": {
                        "lucro_liquido": float(lucro_liquido),
                        "ajustes": {
                            "depreciacao_amortizacao": float(depreciacao + amortizacao),
                            "variacao_contas_receber": float(-variacao_contas_receber),
                            "variacao_fornecedores": float(variacao_fornecedores),
                            "variacao_obrigacoes": float(variacao_obrigacoes_trab + variacao_impostos),
                        },
                        "total": float(fluxo_operacional),
                    },
                    "atividades_investimento": {
                        "aquisicao_imobilizado": float(-aquisicao_imobilizado),
                        "total": float(fluxo_investimento),
                    },
                    "atividades_financiamento": {
                        "emprestimos_obtidos": float(emprestimos),
                        "amortizacao_emprestimos": float(-amortizacao_emprestimos),
                        "distribuicao_lucros": float(-distribuicao_lucros),
                        "total": float(fluxo_financiamento),
                    },
                    "variacao_caixa": float(variacao_caixa),
                    "saldo_inicial": float(saldo_inicial),
                    "saldo_final": float(saldo_final),
                },
                "saude_caixa": "POSITIVO" if variacao_caixa > 0 else "NEGATIVO",
            }
        except Exception as e:
            logger.error(f"Erro ao gerar DFC: {e}")
            return {"sucesso": False, "erro": str(e)}

    def gerar_consolidado_grupo(
        self,
        periodo: str,
        empresas: list[dict],
    ) -> dict:
        """Consolida DRE de todas as empresas do grupo"""
        try:
            total_receita = sum(e.get("receita_bruta", 0) for e in empresas)
            total_custos = sum(e.get("total_custos", 0) for e in empresas)
            total_despesas = sum(e.get("total_despesas", 0) for e in empresas)
            total_impostos = sum(e.get("impostos", 0) for e in empresas)
            total_lucro = sum(e.get("lucro_liquido", 0) for e in empresas)

            margem_grupo = (total_lucro / total_receita * 100) if total_receita > 0 else 0

            maior_contribuidor = ""
            if empresas:
                maior_contribuidor = max(empresas, key=lambda e: e.get("receita_bruta", 0)).get("empresa", "")

            return {
                "sucesso": True,
                "periodo": periodo,
                "empresas": len(empresas),
                "consolidado": {
                    "receita_total": total_receita,
                    "custos_total": total_custos,
                    "despesas_total": total_despesas,
                    "impostos_total": total_impostos,
                    "lucro_liquido_total": total_lucro,
                    "margem_liquida_grupo_pct": round(margem_grupo, 2),
                },
                "por_empresa": empresas,
                "maior_contribuidor": maior_contribuidor,
            }
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def _classificar(self, margem: float) -> str:
        if margem >= 15:
            return "EXCELENTE"
        if margem >= 8:
            return "BOM"
        if margem >= 3:
            return "REGULAR"
        if margem >= 0:
            return "CRÍTICO"
        return "PREJUÍZO"
