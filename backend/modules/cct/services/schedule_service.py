"""
Servico de Jornada e Adicionais — CCT 2026.
"""

import logging

from modules.cct.models.schedule import JORNADAS_PERMITIDAS
from modules.cct.validators.schedule_validator import ScheduleValidator

logger = logging.getLogger(__name__)


class ScheduleService:
    """Servico de jornadas e adicionais CCT 2026."""

    def __init__(self) -> None:
        self.validator = ScheduleValidator()

    def get_jornadas_permitidas(self) -> list[dict]:
        """Retorna jornadas permitidas pela CCT."""
        return [
            {
                "tipo": j.tipo.value,
                "carga_semanal": j.carga_semanal,
                "divisor_mensal": j.divisor_mensal,
                "descricao": j.descricao,
            }
            for j in JORNADAS_PERMITIDAS
        ]

    def validar_jornada(self, jornada_tipo: str, carga_semanal: int) -> dict:
        """Valida jornada contra CCT."""
        return self.validator.validar_jornada(jornada_tipo, carga_semanal)

    def calcular_hora_extra(
        self,
        salario_base: float,
        jornada_tipo: str = "12x36",
        horas_extras_normais: float = 0,
        horas_extras_feriado: float = 0,
        intrajornada_nao_concedida: bool = False,
    ) -> dict:
        """Calcula horas extras conforme CCT."""
        return self.validator.calcular_hora_extra(
            salario_base=salario_base,
            jornada_tipo=jornada_tipo,
            horas_extras_normais=horas_extras_normais,
            horas_extras_feriado=horas_extras_feriado,
            intrajornada_nao_concedida=intrajornada_nao_concedida,
        )

    def calcular_adicional_noturno(
        self,
        salario_base: float,
        jornada_tipo: str = "12x36",
        horas_noturnas: float = 0,
    ) -> dict:
        """Calcula adicional noturno com hora reduzida."""
        return self.validator.calcular_adicional_noturno(
            salario_base=salario_base,
            jornada_tipo=jornada_tipo,
            horas_noturnas=horas_noturnas,
        )

    def calcular_adicionais(
        self,
        salario_base: float,
        ronda_permanente: bool = False,
        ronda_pre_2020: bool = False,
        acumulo_funcao: bool = False,
        servicos_jardinagem_piscina: bool = False,
        insalubridade: bool = False,
        periculosidade: bool = False,
    ) -> dict:
        """Calcula todos os adicionais aplicaveis."""
        return self.validator.calcular_adicionais(
            salario_base=salario_base,
            ronda_permanente=ronda_permanente,
            ronda_pre_2020=ronda_pre_2020,
            acumulo_funcao=acumulo_funcao,
            servicos_jardinagem_piscina=servicos_jardinagem_piscina,
            insalubridade=insalubridade,
            periculosidade=periculosidade,
        )
