"""
Validador de Rescisao e Ferias — CCT 2026.
"""

import logging
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

# Tabela de ferias por faltas (CLT art. 130 + CCT)
TABELA_FERIAS_FALTAS = {
    (0, 5): 30,
    (6, 14): 24,
    (15, 23): 18,
    (24, 32): 12,
}
FALTAS_SEM_DIREITO = 33


class TerminationValidator:
    """Valida rescisoes conforme CCT 2026."""

    @staticmethod
    def validar_rescisao(
        employee_id: str,
        data_admissao: str,
        data_demissao: str,
        salario_base: float,
        motivo: str,
        aviso_previo_cumprido: bool = False,
        dias_aviso_previo: int = 30,
    ) -> dict:
        """Valida rescisao conforme regras CCT.

        Regras:
        - +1 ano: homologacao obrigatoria no SINDECOMPRESTS
        - Prazo pagamento: 10 dias apos termino aviso previo
        - Atraso: multa = ultimo salario
        - Demissao 30 dias antes da data-base: multa = ultimo salario

        Args:
            employee_id: ID do colaborador.
            data_admissao: Data de admissao (YYYY-MM-DD).
            data_demissao: Data de demissao (YYYY-MM-DD).
            salario_base: Salario base.
            motivo: Motivo da rescisao.
            aviso_previo_cumprido: Se aviso previo foi cumprido.
            dias_aviso_previo: Dias de aviso previo.

        Returns:
            Resultado da validacao.
        """
        dt_admissao = datetime.strptime(data_admissao, "%Y-%m-%d").date()
        dt_demissao = datetime.strptime(data_demissao, "%Y-%m-%d").date()
        alertas = []

        # Tempo de servico
        delta = dt_demissao - dt_admissao
        tempo_servico_anos = round(delta.days / 365.25, 2)

        # Homologacao obrigatoria: +1 ano
        homologacao = tempo_servico_anos >= 1.0
        sindicato = "SINDECOMPRESTS — CNPJ 00.444.514/0001-36" if homologacao else None
        if homologacao:
            alertas.append("Homologacao obrigatoria no SINDECOMPRESTS (tempo >= 1 ano)")

        # Prazo de pagamento: 10 dias apos termino aviso previo
        if aviso_previo_cumprido:
            data_fim_aviso = dt_demissao + timedelta(days=dias_aviso_previo)
        else:
            data_fim_aviso = dt_demissao

        data_limite = data_fim_aviso + timedelta(days=10)
        prazo_dias = 10

        # Multa por atraso
        multa_atraso = salario_base  # Multa = ultimo salario em caso de atraso

        # Multa por demissao 30 dias antes da data-base (01/01)
        multa_pre_database = None
        data_base = date(dt_demissao.year + 1, 1, 1)
        dias_ate_database = (data_base - dt_demissao).days
        if dias_ate_database <= 30 and motivo == "sem_justa_causa":
            multa_pre_database = salario_base
            alertas.append(
                f"Demissao {dias_ate_database} dias antes da data-base (01/01): "
                f"multa adicional de R$ {salario_base:,.2f}"
            )

        return {
            "employee_id": employee_id,
            "conforme": True,
            "tempo_servico_anos": tempo_servico_anos,
            "homologacao_obrigatoria": homologacao,
            "sindicato_homologacao": sindicato,
            "prazo_pagamento_dias": prazo_dias,
            "data_limite_pagamento": data_limite.isoformat(),
            "multa_atraso": multa_atraso,
            "multa_demissao_pre_database": multa_pre_database,
            "alertas": alertas,
        }

    @staticmethod
    def calcular_ferias_proporcionais(
        salario_base: float,
        faltas_periodo: int = 0,
        meses_trabalhados: int = 12,
        abono_pecuniario: bool = False,
    ) -> dict:
        """Calcula ferias proporcionais conforme tabela CCT.

        Tabela de faltas:
        - 0 a 5 faltas: 30 dias
        - 6 a 14 faltas: 24 dias
        - 15 a 23 faltas: 18 dias
        - 24 a 32 faltas: 12 dias
        - Acima de 32: sem direito

        Args:
            salario_base: Salario base mensal.
            faltas_periodo: Faltas no periodo aquisitivo.
            meses_trabalhados: Meses trabalhados (1-12).
            abono_pecuniario: Se deseja vender 1/3 das ferias.

        Returns:
            Calculo detalhado das ferias.
        """
        # Determinar dias de direito
        dias_direito = 0
        if faltas_periodo >= FALTAS_SEM_DIREITO:
            dias_direito = 0
        else:
            for (min_faltas, max_faltas), dias in TABELA_FERIAS_FALTAS.items():
                if min_faltas <= faltas_periodo <= max_faltas:
                    dias_direito = dias
                    break

        # Proporcional
        dias_proporcionais = round(dias_direito * meses_trabalhados / 12, 2)

        # Valor
        valor_dia = salario_base / 30
        valor_ferias = round(valor_dia * dias_proporcionais, 2)
        terco = round(valor_ferias / 3, 2)

        # Abono pecuniario (venda de 1/3)
        valor_abono = 0.0
        if abono_pecuniario and dias_direito > 0:
            dias_abono = dias_direito // 3
            valor_abono = round(valor_dia * dias_abono + (valor_dia * dias_abono / 3), 2)

        total = round(valor_ferias + terco + valor_abono, 2)

        tabela = {}
        for (min_f, max_f), dias in TABELA_FERIAS_FALTAS.items():
            tabela[f"{min_f}_a_{max_f}_faltas"] = dias
        tabela["acima_32_faltas"] = 0

        return {
            "salario_base": salario_base,
            "faltas_periodo": faltas_periodo,
            "dias_direito": dias_direito,
            "meses_trabalhados": meses_trabalhados,
            "dias_proporcionais": dias_proporcionais,
            "valor_ferias": valor_ferias,
            "terco_constitucional": terco,
            "abono_pecuniario": valor_abono,
            "total": total,
            "tabela_faltas": tabela,
        }

    @staticmethod
    def calcular_decimo_terceiro(
        salario_base: float,
        meses_trabalhados: int = 12,
        adicionais_mensais: float = 0,
    ) -> dict:
        """Calcula 13o salario conforme CCT.

        2a parcela: ate 20 de dezembro.

        Args:
            salario_base: Salario base mensal.
            meses_trabalhados: Meses trabalhados no ano.
            adicionais_mensais: Total de adicionais mensais fixos.

        Returns:
            Calculo detalhado do 13o salario.
        """
        base = salario_base + adicionais_mensais
        valor_integral = base
        valor_proporcional = round(base * meses_trabalhados / 12, 2)

        primeira_parcela = round(valor_proporcional / 2, 2)
        segunda_parcela = round(valor_proporcional - primeira_parcela, 2)

        return {
            "salario_base": salario_base,
            "adicionais_mensais": adicionais_mensais,
            "meses_trabalhados": meses_trabalhados,
            "valor_integral": valor_integral,
            "valor_proporcional": valor_proporcional,
            "primeira_parcela": primeira_parcela,
            "segunda_parcela": segunda_parcela,
            "prazo_segunda_parcela": "Ate 20 de dezembro de 2026",
        }
