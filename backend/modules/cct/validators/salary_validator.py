"""
Validador de Salarios — CCT 2026.
"""

import logging
from decimal import Decimal

from modules.cct.models.salary_table import (
    REAJUSTE_ACIMA_PISO,
    REAJUSTE_PISO,
    SALARIO_PISO,
    CargoAdditional,
    SalaryEntry,
    get_piso_by_cargo,
)

logger = logging.getLogger(__name__)


class SalaryValidator:
    """Valida salarios contra pisos da CCT 2026."""

    @staticmethod
    def validar_salario(cargo: str, salario_atual: float) -> dict:
        """Valida salario contra piso CCT do cargo.

        Args:
            cargo: Nome do cargo conforme tabela CCT.
            salario_atual: Salario atual do colaborador.

        Returns:
            Dicionario com resultado da validacao.
        """
        entry = get_piso_by_cargo(cargo)
        if not entry:
            return {
                "conforme": False,
                "cargo": cargo,
                "piso_cct": 0,
                "salario_atual": salario_atual,
                "diferenca": 0,
                "percentual_diferenca": 0,
                "adicional_tipo": None,
                "adicional_valor": None,
                "alerta": f"Cargo '{cargo}' nao encontrado na tabela CCT 2026",
            }

        piso = float(entry.piso)
        diferenca = round(salario_atual - piso, 2)
        percentual = round(((salario_atual / piso) - 1) * 100, 2) if piso > 0 else 0

        adicional_tipo = None
        adicional_valor = None
        if entry.adicional != CargoAdditional.NENHUM:
            adicional_tipo = entry.adicional.value
            adicional_valor = SalaryValidator._calcular_adicional(entry, salario_atual)

        conforme = salario_atual >= piso
        alerta = None
        if not conforme:
            alerta = f"Salario R$ {salario_atual:,.2f} esta abaixo do piso CCT R$ {piso:,.2f} para {cargo}"

        return {
            "conforme": conforme,
            "cargo": entry.cargo,
            "piso_cct": piso,
            "salario_atual": salario_atual,
            "diferenca": diferenca,
            "percentual_diferenca": percentual,
            "adicional_tipo": adicional_tipo,
            "adicional_valor": adicional_valor,
            "alerta": alerta,
        }

    @staticmethod
    def calcular_reajuste(salario_atual: float, cargo: str | None = None) -> dict:
        """Calcula reajuste salarial conforme CCT.

        Piso: 7,1% — Acima do piso: 4,5%.

        Args:
            salario_atual: Salario atual.
            cargo: Nome do cargo (opcional, para determinar se esta no piso).

        Returns:
            Dicionario com resultado do calculo.
        """
        piso_cct = None
        tipo_reajuste = "acima_do_piso"
        percentual = float(REAJUSTE_ACIMA_PISO)

        if cargo:
            entry = get_piso_by_cargo(cargo)
            if entry:
                piso_cct = float(entry.piso)
                if Decimal(str(salario_atual)) <= entry.piso:
                    tipo_reajuste = "piso"
                    percentual = float(REAJUSTE_PISO)

        salario_reajustado = round(salario_atual * (1 + percentual / 100), 2)
        diferenca = round(salario_reajustado - salario_atual, 2)

        return {
            "salario_atual": salario_atual,
            "percentual_reajuste": percentual,
            "salario_reajustado": salario_reajustado,
            "diferenca": diferenca,
            "tipo_reajuste": tipo_reajuste,
            "piso_cct": piso_cct,
        }

    @staticmethod
    def _calcular_adicional(entry: SalaryEntry, salario_base: float) -> float:
        """Calcula valor do adicional vinculado ao cargo."""
        if entry.adicional == CargoAdditional.INSALUBRIDADE_10:
            # 10% sobre salario minimo nacional (usar piso CCT como base)
            return round(float(SALARIO_PISO) * 0.10, 2)
        if entry.adicional == CargoAdditional.PERICULOSIDADE_30:
            return round(salario_base * 0.30, 2)
        if entry.adicional == CargoAdditional.ADICIONAL_10:
            return round(salario_base * 0.10, 2)
        return 0.0
