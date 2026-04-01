"""
Validador de Estabilidade — CCT 2026.
"""

import logging
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)


class StabilityValidator:
    """Valida estabilidades previstas na CCT 2026.

    Estabilidades:
    - Pre-aposentadoria: 12 meses (minimo 5 anos na empresa)
    - Acidente de trabalho: 12 meses apos alta INSS
    - Gestante: confirmacao ate 5 meses apos parto
    """

    @staticmethod
    def verificar_estabilidade(
        employee_id: str,
        data_admissao: str,
        data_nascimento: str | None = None,
        acidente_trabalho: bool = False,
        data_alta_inss: str | None = None,
        gestante: bool = False,
        data_parto: str | None = None,
    ) -> dict:
        """Verifica todas as estabilidades aplicaveis.

        Args:
            employee_id: ID do colaborador.
            data_admissao: Data de admissao (YYYY-MM-DD).
            data_nascimento: Data de nascimento (YYYY-MM-DD).
            acidente_trabalho: Se houve acidente de trabalho.
            data_alta_inss: Data da alta INSS (YYYY-MM-DD).
            gestante: Se e gestante.
            data_parto: Data do parto (YYYY-MM-DD).

        Returns:
            Resultado da verificacao de estabilidade.
        """
        hoje = date.today()
        dt_admissao = datetime.strptime(data_admissao, "%Y-%m-%d").date()
        motivos = []
        alertas = []
        data_fim = None
        estavel = False

        tempo_empresa = (hoje - dt_admissao).days / 365.25

        # Pre-aposentadoria: 12 meses de estabilidade se >= 5 anos na empresa
        if tempo_empresa >= 5.0 and data_nascimento:
            dt_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
            idade = (hoje - dt_nascimento).days / 365.25
            # Homem: 65 anos / Mulher: 62 anos (regra geral INSS)
            # Verificar se esta a 12 meses de completar idade
            if idade >= 64.0:  # Pode estar no periodo pre-aposentadoria
                estavel = True
                motivos.append("Pre-aposentadoria (12 meses, minimo 5 anos empresa)")
                alertas.append("Colaborador pode estar em periodo pre-aposentadoria")

        # Acidente de trabalho: 12 meses apos alta INSS
        if acidente_trabalho and data_alta_inss:
            dt_alta = datetime.strptime(data_alta_inss, "%Y-%m-%d").date()
            fim_estabilidade = dt_alta + timedelta(days=365)
            if hoje <= fim_estabilidade:
                estavel = True
                motivos.append("Acidente de trabalho (12 meses apos alta INSS)")
                if data_fim is None or fim_estabilidade > datetime.strptime(data_fim, "%Y-%m-%d").date():
                    data_fim = fim_estabilidade.isoformat()
                alertas.append(f"Estabilidade por acidente ate {fim_estabilidade.isoformat()}")

        # Gestante: confirmacao ate 5 meses apos parto
        if gestante:
            if data_parto:
                dt_parto = datetime.strptime(data_parto, "%Y-%m-%d").date()
                fim_estabilidade = dt_parto + timedelta(days=150)  # 5 meses
                if hoje <= fim_estabilidade:
                    estavel = True
                    motivos.append("Gestante (ate 5 meses apos parto)")
                    if data_fim is None or fim_estabilidade > datetime.strptime(data_fim, "%Y-%m-%d").date():
                        data_fim = fim_estabilidade.isoformat()
                    alertas.append(f"Estabilidade gestante ate {fim_estabilidade.isoformat()}")
            else:
                estavel = True
                motivos.append("Gestante (em andamento — confirmar parto)")
                alertas.append("Gestante sem data de parto informada — estabilidade presumida")

        return {
            "employee_id": employee_id,
            "estavel": estavel,
            "motivos": motivos,
            "data_fim_estabilidade": data_fim,
            "alertas": alertas,
        }
