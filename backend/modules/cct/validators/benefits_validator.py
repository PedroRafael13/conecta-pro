"""
Validador de Beneficios — CCT 2026.
"""

import logging
from datetime import date

from modules.cct.models.benefits import (
    TAXA_NEGOCIAL_2026,
    TipoBeneficioCCT,
    get_beneficios_obrigatorios,
)

logger = logging.getLogger(__name__)


class BenefitsValidator:
    """Valida beneficios contra obrigatorios da CCT 2026."""

    @staticmethod
    def validar_beneficios(
        employee_id: str,
        salario_base: float,
        beneficios_ativos: list[str],
        valor_vr_dia: float | None = None,
        desconto_vt_percentual: float | None = None,
    ) -> dict:
        """Valida beneficios de um colaborador contra regras CCT.

        Args:
            employee_id: ID do colaborador.
            salario_base: Salario base do colaborador.
            beneficios_ativos: Lista de tipos de beneficio ativos.
            valor_vr_dia: Valor do VR por dia (se aplicavel).
            desconto_vt_percentual: Percentual de desconto VT (se aplicavel).

        Returns:
            Dicionario com resultado da validacao.
        """
        obrigatorios = get_beneficios_obrigatorios()
        itens = []
        faltantes = 0

        for beneficio in obrigatorios:
            presente = beneficio.tipo.value in beneficios_ativos
            conforme = presente
            alerta = None

            if not presente:
                faltantes += 1
                alerta = f"Beneficio obrigatorio {beneficio.tipo.value} nao encontrado"
            else:
                # Validacoes especificas
                if beneficio.tipo == TipoBeneficioCCT.VALE_REFEICAO and valor_vr_dia is not None:
                    if valor_vr_dia < 22.0:
                        conforme = False
                        alerta = f"VR R$ {valor_vr_dia}/dia abaixo do minimo R$ 22,00/dia"

                if beneficio.tipo == TipoBeneficioCCT.VALE_TRANSPORTE and desconto_vt_percentual is not None:
                    if desconto_vt_percentual > 4.0:
                        conforme = False
                        alerta = f"Desconto VT {desconto_vt_percentual}% acima do maximo 4%"

            itens.append(
                {
                    "tipo": beneficio.tipo.value,
                    "obrigatorio": beneficio.obrigatorio,
                    "presente": presente,
                    "conforme": conforme,
                    "alerta": alerta,
                }
            )

        presentes = len(obrigatorios) - faltantes
        conforme_geral = faltantes == 0 and all(i["conforme"] for i in itens)

        return {
            "employee_id": employee_id,
            "total_obrigatorios": len(obrigatorios),
            "presentes": presentes,
            "faltantes": faltantes,
            "conforme": conforme_geral,
            "itens": itens,
        }

    @staticmethod
    def verificar_taxa_negocial(mes: int | None = None) -> dict:
        """Verifica aplicabilidade da taxa negocial sindical.

        Args:
            mes: Mes a verificar (1-12). Se None, usa mes atual.

        Returns:
            Informacoes da taxa negocial.
        """
        if mes is None:
            mes = date.today().month

        aplicavel = mes in TAXA_NEGOCIAL_2026.meses
        proximo = None
        if not aplicavel:
            proximos = [m for m in TAXA_NEGOCIAL_2026.meses if m > mes]
            if proximos:
                proximo = f"2026-{proximos[0]:02d}"
            else:
                proximo = "2027-01 (proxima CCT)"

        return {
            "valor": float(TAXA_NEGOCIAL_2026.valor),
            "meses": list(TAXA_NEGOCIAL_2026.meses),
            "prazo_oposicao_dia": TAXA_NEGOCIAL_2026.prazo_oposicao_dia,
            "observacao": TAXA_NEGOCIAL_2026.observacao,
            "mes_atual_aplicavel": aplicavel,
            "proximo_desconto": proximo,
        }
