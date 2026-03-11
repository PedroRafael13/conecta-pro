"""
ProfitabilityAnalyzerAgent — Analise de Rentabilidade por Contrato
Considera regime tributario de cada empresa do grupo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from modules.financial.agents.tax_calculator import TaxCalculatorAgent


@dataclass
class RentabilidadeContrato:
    contrato_id: int
    cliente_nome: str
    tipo_servico: str
    empresa_slug: str  # conecta_eletronica | conecta_patrimonial
    regime: str

    # Financeiros
    receita_bruta_mes: Decimal
    impostos_mes: Decimal
    receita_liquida: Decimal
    custo_direto_mes: Decimal  # Mao de obra + beneficios
    custo_indireto_mes: Decimal  # Overhead rateado
    lucro_liquido_mes: Decimal
    margem_liquida_percentual: Decimal

    # Detalhes
    detalhamento_impostos: dict = field(default_factory=dict)
    alertas: list[str] = field(default_factory=list)

    @property
    def situacao(self) -> str:
        if self.margem_liquida_percentual >= Decimal("30"):
            return "excelente"
        elif self.margem_liquida_percentual >= Decimal("20"):
            return "bom"
        elif self.margem_liquida_percentual >= Decimal("10"):
            return "aceitavel"
        elif self.margem_liquida_percentual >= Decimal("0"):
            return "atencao"
        else:
            return "deficitario"


class ProfitabilityAnalyzerAgent:
    """
    Analisa rentabilidade de contratos considerando o regime
    tributario da empresa que fatura.
    """

    MARGEM_MINIMA = Decimal("10.0")
    MARGEM_IDEAL = Decimal("20.0")
    MARGEM_EXCELENTE = Decimal("30.0")

    def __init__(self):
        self.tax_calculator = TaxCalculatorAgent()

    def calcular_rentabilidade(
        self,
        receita_bruta_mes: Decimal,
        custo_direto_mes: Decimal,
        custo_indireto_mes: Decimal,
        tipo_servico: str,
        empresa_slug: str,
        regime: str,
        rbt12: Decimal | None = None,
        liminares: list[str] | None = None,
        cliente_nome: str = "",
        contrato_id: int = 0,
    ) -> RentabilidadeContrato:
        """
        Calcula rentabilidade real do contrato.

        Formula:
        RECEITA BRUTA
        (-) Impostos (conforme regime da empresa)
        (-) Custos diretos (mao de obra, beneficios, EPI, uniformes)
        (-) Custos indiretos (overhead: admin, TI, sede...)
        = LUCRO LIQUIDO
        """
        liminares = liminares or []

        # Calcular impostos conforme regime
        if regime == "simples_nacional":
            rbt12_calc = rbt12 or (receita_bruta_mes * 12)
            calc = self.tax_calculator.calcular_simples(
                receita_mes=receita_bruta_mes,
                rbt12=rbt12_calc,
                liminares=liminares,
            )
            impostos = calc.valor_das
            det_impostos = calc.distribuicao
        else:  # lucro_real
            receita_trimestre = receita_bruta_mes * 3
            calc_lr = self.tax_calculator.calcular_lucro_real(
                receita_mes=receita_bruta_mes,
                receita_trimestre=receita_trimestre,
            )
            impostos = calc_lr.total_impostos_mes
            det_impostos = {d.nome: float(d.valor) for d in calc_lr.detalhamento}

        receita_liquida = receita_bruta_mes - impostos
        lucro_liquido = receita_liquida - custo_direto_mes - custo_indireto_mes

        if receita_bruta_mes > 0:
            margem = (lucro_liquido / receita_bruta_mes * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
        else:
            margem = Decimal("0")

        alertas = []
        if margem < 0:
            alertas.append(f"Contrato DEFICITARIO! Prejuizo de R$ {abs(lucro_liquido):,.2f}/mes")
        elif margem < self.MARGEM_MINIMA:
            alertas.append(f"Margem {margem}% abaixo do minimo de {self.MARGEM_MINIMA}%")

        if custo_direto_mes > receita_liquida * Decimal("0.85"):
            alertas.append("Custo de mao de obra acima de 85% da receita liquida")

        return RentabilidadeContrato(
            contrato_id=contrato_id,
            cliente_nome=cliente_nome,
            tipo_servico=tipo_servico,
            empresa_slug=empresa_slug,
            regime=regime,
            receita_bruta_mes=receita_bruta_mes,
            impostos_mes=impostos,
            receita_liquida=receita_liquida,
            custo_direto_mes=custo_direto_mes,
            custo_indireto_mes=custo_indireto_mes,
            lucro_liquido_mes=lucro_liquido,
            margem_liquida_percentual=margem,
            detalhamento_impostos=det_impostos,
            alertas=alertas,
        )

    def comparar_empresa_para_contrato(
        self,
        receita_bruta_mes: Decimal,
        custo_direto_mes: Decimal,
        custo_indireto_mes: Decimal,
        tipo_servico: str,
        rbt12_eletronica: Decimal,
        rbt12_patrimonial: Decimal,
        liminares_patrimonial: list[str] | None = None,
    ) -> dict:
        """
        Compara rentabilidade do contrato se faturado pela Eletronica vs Patrimonial.
        """
        result_eletronica = self.calcular_rentabilidade(
            receita_bruta_mes=receita_bruta_mes,
            custo_direto_mes=custo_direto_mes,
            custo_indireto_mes=custo_indireto_mes,
            tipo_servico=tipo_servico,
            empresa_slug="conecta_eletronica",
            regime="lucro_real",
            rbt12=rbt12_eletronica,
        )

        result_patrimonial = self.calcular_rentabilidade(
            receita_bruta_mes=receita_bruta_mes,
            custo_direto_mes=custo_direto_mes,
            custo_indireto_mes=custo_indireto_mes,
            tipo_servico=tipo_servico,
            empresa_slug="conecta_patrimonial",
            regime="simples_nacional",
            rbt12=rbt12_patrimonial,
            liminares=liminares_patrimonial or [],
        )

        economia = (result_patrimonial.lucro_liquido_mes - result_eletronica.lucro_liquido_mes).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

        melhor = (
            "patrimonial"
            if result_patrimonial.margem_liquida_percentual > result_eletronica.margem_liquida_percentual
            else "eletronica"
        )

        return {
            "tipo_servico": tipo_servico,
            "receita_bruta_mes": float(receita_bruta_mes),
            "conecta_eletronica": {
                "regime": "Lucro Real",
                "impostos": float(result_eletronica.impostos_mes),
                "lucro_liquido": float(result_eletronica.lucro_liquido_mes),
                "margem": float(result_eletronica.margem_liquida_percentual),
                "situacao": result_eletronica.situacao,
            },
            "conecta_patrimonial": {
                "regime": "Simples Nacional Anexo III",
                "impostos": float(result_patrimonial.impostos_mes),
                "lucro_liquido": float(result_patrimonial.lucro_liquido_mes),
                "margem": float(result_patrimonial.margem_liquida_percentual),
                "situacao": result_patrimonial.situacao,
                "liminares": liminares_patrimonial or [],
            },
            "economia_mensal_patrimonial": float(economia),
            "economia_anual_patrimonial": float(economia * 12),
            "melhor_empresa": melhor,
            "recomendacao": (
                f"Faturar pela Conecta Patrimonial gera R$ {economia:,.2f}/mes a mais de lucro"
                if melhor == "patrimonial"
                else "Faturar pela Conecta Eletronica e mais vantajoso neste cenario"
            ),
        }
