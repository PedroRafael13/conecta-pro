"""
Validador de Jornada e Adicionais — CCT 2026.
"""

import logging

from modules.cct.models.schedule import (
    ADICIONAIS,
    ESCALA_PROIBIDA_2X1,
    ESCALA_PROIBIDA_FUNDAMENTACAO,
    TipoJornadaCCT,
    get_divisor_mensal,
    get_jornada_by_tipo,
)

logger = logging.getLogger(__name__)


class ScheduleValidator:
    """Valida jornadas e calcula adicionais conforme CCT 2026."""

    @staticmethod
    def validar_jornada(jornada_tipo: str, carga_semanal: int) -> dict:
        """Valida tipo de jornada contra CCT.

        Args:
            jornada_tipo: Tipo de jornada (44h_semanais, 36h_corridas, 12x36).
            carga_semanal: Carga horaria semanal.

        Returns:
            Resultado da validacao.
        """
        alertas = []

        # Verificar escala proibida
        if ESCALA_PROIBIDA_2X1 in jornada_tipo.lower():
            alertas.append(f"Escala {ESCALA_PROIBIDA_2X1} PROIBIDA — {ESCALA_PROIBIDA_FUNDAMENTACAO}")
            return {
                "conforme": False,
                "jornada_tipo": jornada_tipo,
                "divisor_mensal": 0,
                "carga_semanal": carga_semanal,
                "alertas": alertas,
            }

        try:
            tipo = TipoJornadaCCT(jornada_tipo)
        except ValueError:
            alertas.append(f"Tipo de jornada '{jornada_tipo}' nao reconhecido pela CCT")
            return {
                "conforme": False,
                "jornada_tipo": jornada_tipo,
                "divisor_mensal": 220,
                "carga_semanal": carga_semanal,
                "alertas": alertas,
            }

        jornada = get_jornada_by_tipo(tipo)
        if not jornada:
            alertas.append(f"Jornada {jornada_tipo} nao encontrada na CCT")
            return {
                "conforme": False,
                "jornada_tipo": jornada_tipo,
                "divisor_mensal": 220,
                "carga_semanal": carga_semanal,
                "alertas": alertas,
            }

        conforme = True
        if carga_semanal > jornada.carga_semanal:
            conforme = False
            alertas.append(
                f"Carga semanal {carga_semanal}h excede limite de {jornada.carga_semanal}h para jornada {jornada_tipo}"
            )

        return {
            "conforme": conforme,
            "jornada_tipo": jornada_tipo,
            "divisor_mensal": jornada.divisor_mensal,
            "carga_semanal": carga_semanal,
            "alertas": alertas,
        }

    @staticmethod
    def calcular_hora_extra(
        salario_base: float,
        jornada_tipo: str = "12x36",
        horas_extras_normais: float = 0,
        horas_extras_feriado: float = 0,
        intrajornada_nao_concedida: bool = False,
    ) -> dict:
        """Calcula valores de hora extra conforme CCT.

        Args:
            salario_base: Salario base mensal.
            jornada_tipo: Tipo de jornada para obter divisor.
            horas_extras_normais: Horas extras em dias normais.
            horas_extras_feriado: Horas extras em feriados/folgas.
            intrajornada_nao_concedida: Se intrajornada nao foi concedida.

        Returns:
            Calculo detalhado de horas extras.
        """
        try:
            tipo = TipoJornadaCCT(jornada_tipo)
        except ValueError:
            tipo = TipoJornadaCCT.ESCALA_12X36

        divisor = get_divisor_mensal(tipo)
        hora_normal = round(salario_base / divisor, 2)
        hora_extra_50 = round(hora_normal * 1.5, 2)
        hora_extra_100 = round(hora_normal * 2.0, 2)

        total_normais = round(horas_extras_normais * hora_extra_50, 2)
        total_feriado = round(horas_extras_feriado * hora_extra_100, 2)

        valor_intrajornada = 0.0
        if intrajornada_nao_concedida:
            valor_intrajornada = round(float(ADICIONAIS.intrajornada_nao_concedida_horas) * hora_extra_50, 2)

        total = round(total_normais + total_feriado + valor_intrajornada, 2)

        return {
            "salario_base": salario_base,
            "divisor_mensal": divisor,
            "valor_hora_normal": hora_normal,
            "valor_hora_extra_50": hora_extra_50,
            "valor_hora_extra_100": hora_extra_100,
            "total_horas_extras_normais": total_normais,
            "total_horas_extras_feriado": total_feriado,
            "valor_intrajornada": valor_intrajornada,
            "total_extras": total,
        }

    @staticmethod
    def calcular_adicional_noturno(
        salario_base: float,
        jornada_tipo: str = "12x36",
        horas_noturnas: float = 0,
    ) -> dict:
        """Calcula adicional noturno com hora reduzida (52min30s).

        Args:
            salario_base: Salario base mensal.
            jornada_tipo: Tipo de jornada para obter divisor.
            horas_noturnas: Horas trabalhadas no periodo noturno (22h-05h).

        Returns:
            Calculo detalhado do adicional noturno.
        """
        try:
            tipo = TipoJornadaCCT(jornada_tipo)
        except ValueError:
            tipo = TipoJornadaCCT.ESCALA_12X36

        divisor = get_divisor_mensal(tipo)
        hora_normal = round(salario_base / divisor, 2)

        # Hora noturna reduzida: 52min30s = 52.5 minutos
        # Fator de conversao: 60 / 52.5 = 1.142857...
        fator_reducao = 60.0 / float(ADICIONAIS.hora_noturna_minutos)
        horas_reduzidas = round(horas_noturnas * fator_reducao, 4)

        # Adicional noturno: 20% sobre hora normal
        percentual = float(ADICIONAIS.adicional_noturno_percentual)
        valor_adicional = round(horas_reduzidas * hora_normal * (percentual / 100), 2)

        return {
            "salario_base": salario_base,
            "divisor_mensal": divisor,
            "valor_hora_normal": hora_normal,
            "adicional_noturno_percentual": percentual,
            "hora_noturna_minutos": float(ADICIONAIS.hora_noturna_minutos),
            "horas_noturnas_informadas": horas_noturnas,
            "horas_noturnas_reduzidas": horas_reduzidas,
            "valor_adicional_noturno": valor_adicional,
        }

    @staticmethod
    def calcular_adicionais(
        salario_base: float,
        ronda_permanente: bool = False,
        ronda_pre_2020: bool = False,
        acumulo_funcao: bool = False,
        servicos_jardinagem_piscina: bool = False,
        insalubridade: bool = False,
        periculosidade: bool = False,
    ) -> dict:
        """Calcula todos os adicionais aplicaveis conforme CCT.

        Args:
            salario_base: Salario base mensal.
            ronda_permanente: Se faz ronda permanente.
            ronda_pre_2020: Se contrato e anterior a CCT 2020.
            acumulo_funcao: Se ha acumulo de funcao comprovado.
            servicos_jardinagem_piscina: Se servicos gerais faz jardinagem/piscina.
            insalubridade: Se recebe insalubridade.
            periculosidade: Se recebe periculosidade.

        Returns:
            Calculo detalhado dos adicionais.
        """
        adicional_ronda = 0.0
        if ronda_permanente:
            percentual = (
                float(ADICIONAIS.ronda_permanente_pre_2020_percentual)
                if ronda_pre_2020
                else float(ADICIONAIS.ronda_permanente_percentual)
            )
            adicional_ronda = round(salario_base * percentual / 100, 2)

        adicional_acumulo = 0.0
        if acumulo_funcao:
            adicional_acumulo = round(salario_base * float(ADICIONAIS.acumulo_funcao_percentual) / 100, 2)

        adicional_jardinagem = 0.0
        if servicos_jardinagem_piscina:
            adicional_jardinagem = round(
                salario_base * float(ADICIONAIS.servicos_jardinagem_piscina_percentual) / 100, 2
            )

        # Insalubridade: 10% sobre salario minimo (piso CCT)
        adicional_insalubridade = 0.0
        if insalubridade:
            from modules.cct.models.salary_table import SALARIO_PISO

            adicional_insalubridade = round(
                float(SALARIO_PISO) * float(ADICIONAIS.insalubridade_minimo_percentual) / 100, 2
            )

        adicional_periculosidade = 0.0
        if periculosidade:
            adicional_periculosidade = round(salario_base * float(ADICIONAIS.periculosidade_percentual) / 100, 2)

        total = round(
            adicional_ronda
            + adicional_acumulo
            + adicional_jardinagem
            + adicional_insalubridade
            + adicional_periculosidade,
            2,
        )

        return {
            "salario_base": salario_base,
            "adicional_ronda": adicional_ronda,
            "adicional_acumulo_funcao": adicional_acumulo,
            "adicional_jardinagem_piscina": adicional_jardinagem,
            "adicional_insalubridade": adicional_insalubridade,
            "adicional_periculosidade": adicional_periculosidade,
            "total_adicionais": total,
            "salario_total": round(salario_base + total, 2),
        }
