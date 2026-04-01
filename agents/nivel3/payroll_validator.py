"""
PayrollValidator — Valida cálculos de folha salarial.
Verifica: INSS, IRRF, FGTS, férias, 13º, rescisão.
Baseado na legislação 2026 e CCT SINDECOMPRESTS.
"""

from decimal import Decimal, ROUND_HALF_UP


# ─── TABELAS 2026 ─────────────────────────────────────────

# Tabela INSS 2026 (progressiva — cada faixa tributa só o excedente)
TABELA_INSS_2026 = [
    (Decimal("1412.00"), Decimal("0.075")),
    (Decimal("2666.68"), Decimal("0.09")),
    (Decimal("4000.03"), Decimal("0.12")),
    (Decimal("7786.02"), Decimal("0.14")),
]

# Tabela IRRF 2026 (base de cálculo mensal)
TABELA_IRRF_2026 = [
    (Decimal("2259.20"), Decimal("0"), Decimal("0")),
    (Decimal("2826.65"), Decimal("0.075"), Decimal("169.44")),
    (Decimal("3751.05"), Decimal("0.15"), Decimal("381.44")),
    (Decimal("4664.68"), Decimal("0.225"), Decimal("662.77")),
    (Decimal("999999.99"), Decimal("0.275"), Decimal("896.00")),
]

DEDUCAO_DEPENDENTE_2026 = Decimal("189.59")
FGTS_ALIQUOTA = Decimal("0.08")
SALARIO_MINIMO_2026 = Decimal("1412.00")
TETO_INSS_2026 = Decimal("7786.02")

# Pisos CCT SINDECOMPRESTS 2026
PISOS_CCT = {
    "Agente de Portaria": Decimal("1670.00"),
    "Agente de Serviços Gerais": Decimal("1670.00"),
    "Artífice": Decimal("1742.52"),
    "Líder de Portaria": Decimal("1787.53"),
}


class PayrollValidator:
    """Valida cálculos de folha salarial brasileira."""

    @staticmethod
    def calcular_inss(salario_bruto: Decimal) -> Decimal:
        """Calcula INSS progressivo 2026 (desconto sobre cada faixa)."""
        base = min(salario_bruto, TETO_INSS_2026)
        inss = Decimal("0")
        faixa_anterior = Decimal("0")

        for teto_faixa, aliquota in TABELA_INSS_2026:
            if base <= faixa_anterior:
                break
            base_faixa = min(base, teto_faixa) - faixa_anterior
            inss += base_faixa * aliquota
            faixa_anterior = teto_faixa

        return inss.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calcular_irrf(
        salario_bruto: Decimal,
        inss: Decimal,
        dependentes: int = 0,
    ) -> Decimal:
        """Calcula IRRF 2026 (alíquota progressiva)."""
        base_irrf = salario_bruto - inss - (DEDUCAO_DEPENDENTE_2026 * dependentes)

        if base_irrf <= Decimal("0"):
            return Decimal("0.00")

        for teto, aliquota, deducao in TABELA_IRRF_2026:
            if base_irrf <= teto:
                irrf = base_irrf * aliquota - deducao
                return max(Decimal("0"), irrf).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

        return Decimal("0.00")

    @staticmethod
    def calcular_fgts(salario_bruto: Decimal) -> Decimal:
        """Calcula FGTS (8% do salário bruto)."""
        return (salario_bruto * FGTS_ALIQUOTA).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calcular_salario_liquido(
        salario_bruto: Decimal,
        inss: Decimal,
        irrf: Decimal,
        outros_descontos: Decimal = Decimal("0"),
    ) -> Decimal:
        """Calcula salário líquido."""
        return (salario_bruto - inss - irrf - outros_descontos).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calcular_ferias(salario_bruto: Decimal) -> dict:
        """
        Calcula férias completas (30 dias):
        - Base = salário bruto
        - Adicional 1/3 constitucional
        - Incidência INSS + IRRF sobre a base (sem o 1/3 para IRRF)
        """
        ferias_base = salario_bruto
        adicional_tercio = (ferias_base / 3).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_bruto = ferias_base + adicional_tercio

        inss_ferias = PayrollValidator.calcular_inss(ferias_base)
        irrf_ferias = PayrollValidator.calcular_irrf(ferias_base, inss_ferias)
        liquido = (total_bruto - inss_ferias - irrf_ferias).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "base": ferias_base,
            "adicional_tercio": adicional_tercio,
            "total_bruto": total_bruto,
            "inss": inss_ferias,
            "irrf": irrf_ferias,
            "liquido": liquido,
        }

    @staticmethod
    def calcular_decimo_terceiro(
        salario_bruto: Decimal,
        meses_trabalhados: int = 12,
    ) -> dict:
        """
        13º salário proporcional.
        Parcela 1 (novembro): 50% sem descontos.
        Parcela 2 (dezembro): 50% - INSS - IRRF (calculados sobre base total).
        """
        base = (salario_bruto * meses_trabalhados / 12).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        parcela1 = (base / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parcela2_bruta = (base - parcela1).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        inss_13 = PayrollValidator.calcular_inss(base)
        irrf_13 = PayrollValidator.calcular_irrf(base, inss_13)
        parcela2_liquida = max(
            Decimal("0"),
            (parcela2_bruta - inss_13 - irrf_13).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
        )

        return {
            "base": base,
            "meses": meses_trabalhados,
            "parcela1": parcela1,
            "parcela2_bruta": parcela2_bruta,
            "inss": inss_13,
            "irrf": irrf_13,
            "parcela2_liquida": parcela2_liquida,
        }

    @staticmethod
    def calcular_rescisao_sem_justa_causa(
        salario_bruto: Decimal,
        meses_trabalhados: int,
        saldo_fgts: Decimal,
        ferias_vencidas: bool = False,
        ferias_proporcionais_meses: int = 0,
        decimo_terceiro_meses: int = 0,
    ) -> dict:
        """
        Verbas rescisórias sem justa causa (CLT art. 477):
        - Aviso prévio: 30 dias + 3 dias/ano (máx. 90 dias — Lei 12.506/2011)
        - Férias vencidas + 1/3
        - Férias proporcionais + 1/3
        - 13º proporcional
        - Multa FGTS 40% (Decreto 99.684/1990)
        """
        anos = meses_trabalhados // 12
        dias_aviso = min(30 + (anos * 3), 90)
        aviso_previo = (salario_bruto * dias_aviso / 30).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if ferias_vencidas:
            ferias_v = (salario_bruto + (salario_bruto / 3)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            ferias_v = Decimal("0.00")

        if ferias_proporcionais_meses > 0:
            fp_base = (salario_bruto * ferias_proporcionais_meses / 12).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            ferias_prop = (fp_base + (fp_base / 3)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            ferias_prop = Decimal("0.00")

        if decimo_terceiro_meses > 0:
            decimo_prop = (salario_bruto * decimo_terceiro_meses / 12).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            decimo_prop = Decimal("0.00")

        multa_fgts = (saldo_fgts * Decimal("0.40")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        verbas = {
            "dias_aviso": dias_aviso,
            "aviso_previo": aviso_previo,
            "ferias_vencidas": ferias_v,
            "ferias_proporcionais": ferias_prop,
            "decimo_terceiro_proporcional": decimo_prop,
            "multa_fgts_40pct": multa_fgts,
        }
        verbas["total_bruto"] = sum(v for k, v in verbas.items() if k != "dias_aviso")
        return verbas

    def validar_holerite(self, holerite_api: dict) -> list:
        """
        Valida um holerite retornado pela API.
        Margem de tolerância: R$ 0,10 (arredondamento bancário).
        """
        erros = []
        TOLERANCIA = Decimal("0.10")

        salario_bruto = Decimal(str(holerite_api.get("salario_bruto", 0) or 0))
        inss_api = Decimal(str(holerite_api.get("inss", 0) or 0))
        irrf_api = Decimal(str(holerite_api.get("irrf", 0) or 0))
        fgts_api = Decimal(str(holerite_api.get("fgts", 0) or 0))
        dependentes = int(holerite_api.get("dependentes", 0) or 0)

        if salario_bruto <= 0:
            erros.append("Salário bruto inválido ou ausente")
            return erros

        inss_esp = self.calcular_inss(salario_bruto)
        irrf_esp = self.calcular_irrf(salario_bruto, inss_esp, dependentes)
        fgts_esp = self.calcular_fgts(salario_bruto)

        if inss_api > 0 and abs(inss_api - inss_esp) > TOLERANCIA:
            erros.append(
                f"INSS incorreto: API=R${inss_api}, "
                f"esperado=R${inss_esp} "
                f"(diff=R${abs(inss_api - inss_esp)})"
            )

        if irrf_api > 0 and abs(irrf_api - irrf_esp) > TOLERANCIA:
            erros.append(
                f"IRRF incorreto: API=R${irrf_api}, "
                f"esperado=R${irrf_esp} "
                f"(diff=R${abs(irrf_api - irrf_esp)})"
            )

        if fgts_api > 0 and abs(fgts_api - fgts_esp) > TOLERANCIA:
            erros.append(
                f"FGTS incorreto: API=R${fgts_api}, "
                f"esperado=R${fgts_esp} "
                f"(diff=R${abs(fgts_api - fgts_esp)})"
            )

        return erros
