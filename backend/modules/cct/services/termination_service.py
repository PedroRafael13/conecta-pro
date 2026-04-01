"""
Servico de Rescisao e Ferias — CCT 2026.
"""

import logging

from modules.cct.validators.termination_validator import TerminationValidator

logger = logging.getLogger(__name__)


class TerminationService:
    """Servico de rescisao, ferias e 13o conforme CCT 2026."""

    def __init__(self) -> None:
        self.validator = TerminationValidator()

    def validar_rescisao(
        self,
        employee_id: str,
        data_admissao: str,
        data_demissao: str,
        salario_base: float,
        motivo: str,
        aviso_previo_cumprido: bool = False,
        dias_aviso_previo: int = 30,
    ) -> dict:
        """Valida rescisao conforme regras CCT."""
        return self.validator.validar_rescisao(
            employee_id=employee_id,
            data_admissao=data_admissao,
            data_demissao=data_demissao,
            salario_base=salario_base,
            motivo=motivo,
            aviso_previo_cumprido=aviso_previo_cumprido,
            dias_aviso_previo=dias_aviso_previo,
        )

    def calcular_ferias(
        self,
        salario_base: float,
        faltas_periodo: int = 0,
        meses_trabalhados: int = 12,
        abono_pecuniario: bool = False,
    ) -> dict:
        """Calcula ferias proporcionais conforme tabela CCT."""
        return self.validator.calcular_ferias_proporcionais(
            salario_base=salario_base,
            faltas_periodo=faltas_periodo,
            meses_trabalhados=meses_trabalhados,
            abono_pecuniario=abono_pecuniario,
        )

    def calcular_decimo_terceiro(
        self,
        salario_base: float,
        meses_trabalhados: int = 12,
        adicionais_mensais: float = 0,
    ) -> dict:
        """Calcula 13o salario conforme CCT."""
        return self.validator.calcular_decimo_terceiro(
            salario_base=salario_base,
            meses_trabalhados=meses_trabalhados,
            adicionais_mensais=adicionais_mensais,
        )
