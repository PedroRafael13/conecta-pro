"""
BookkeeperAutoAgent — Escrituração contábil automatizada multi-empresa
Gera lançamentos contábeis a partir de eventos do ERP (contratos, folha, impostos).
"""

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class BookkeeperAutoAgent:
    """Escrituração automática multi-empresa"""

    def gerar_lancamentos_folha(
        self,
        empresa_slug: str,
        competencia: str,  # "YYYY-MM"
        funcionarios: list[dict],
    ) -> dict:
        """Gera lançamentos contábeis da folha de pagamento"""
        try:
            lancamentos = []
            total_salarios = Decimal("0")
            total_inss = Decimal("0")
            total_fgts = Decimal("0")
            total_ferias_provisao = Decimal("0")
            total_decimo_provisao = Decimal("0")

            for func in funcionarios:
                salario = Decimal(str(func.get("salario_bruto", 0)))
                inss_patronal = Decimal(str(func.get("inss_patronal", 0)))
                fgts = Decimal(str(func.get("fgts", 0)))

                total_salarios += salario
                total_inss += inss_patronal
                total_fgts += fgts
                total_ferias_provisao += salario * Decimal("0.1111")  # 1/9
                total_decimo_provisao += salario * Decimal("0.0833")  # 1/12

            ano, mes = competencia.split("-")
            historico_base = f"Folha {mes}/{ano}"

            # Lançamento salários
            if total_salarios > 0:
                lancamentos.append(
                    {
                        "data": f"01/{mes}/{ano}",
                        "historico": f"{historico_base} - Salários",
                        "conta_debito": "4.1.1.01",
                        "conta_credito": "2.1.2.01",
                        "valor": float(total_salarios),
                    }
                )

            # Lançamento INSS patronal
            if total_inss > 0:
                lancamentos.append(
                    {
                        "data": f"01/{mes}/{ano}",
                        "historico": f"{historico_base} - INSS Patronal",
                        "conta_debito": "4.1.2.01",
                        "conta_credito": "2.1.3.01",
                        "valor": float(total_inss),
                    }
                )

            # Lançamento FGTS
            if total_fgts > 0:
                lancamentos.append(
                    {
                        "data": f"01/{mes}/{ano}",
                        "historico": f"{historico_base} - FGTS",
                        "conta_debito": "4.1.2.02",
                        "conta_credito": "2.1.2.01",
                        "valor": float(total_fgts),
                    }
                )

            # Provisão férias
            lancamentos.append(
                {
                    "data": f"01/{mes}/{ano}",
                    "historico": f"{historico_base} - Provisão Férias",
                    "conta_debito": "4.1.2.04",
                    "conta_credito": "2.1.2.01",
                    "valor": float(total_ferias_provisao),
                }
            )

            # Provisão 13º
            lancamentos.append(
                {
                    "data": f"01/{mes}/{ano}",
                    "historico": f"{historico_base} - Provisão 13º",
                    "conta_debito": "4.1.2.03",
                    "conta_credito": "2.1.2.01",
                    "valor": float(total_decimo_provisao),
                }
            )

            return {
                "sucesso": True,
                "empresa": empresa_slug,
                "competencia": competencia,
                "total_funcionarios": len(funcionarios),
                "totais": {
                    "salarios": float(total_salarios),
                    "inss_patronal": float(total_inss),
                    "fgts": float(total_fgts),
                    "provisao_ferias": float(total_ferias_provisao),
                    "provisao_decimo": float(total_decimo_provisao),
                    "custo_total": float(
                        total_salarios + total_inss + total_fgts + total_ferias_provisao + total_decimo_provisao
                    ),
                },
                "lancamentos": lancamentos,
                "total_lancamentos": len(lancamentos),
            }
        except Exception as e:
            logger.error(f"Erro ao gerar lançamentos folha: {e}")
            return {"sucesso": False, "erro": str(e)}

    def gerar_lancamentos_impostos(
        self,
        empresa_slug: str,
        competencia: str,
        impostos: dict,
        regime: str = "lucro_real",
    ) -> dict:
        """Gera lançamentos contábeis dos impostos conforme regime tributário"""
        try:
            lancamentos = []
            ano, mes = competencia.split("-")
            historico_base = f"Impostos {mes}/{ano}"

            if regime == "simples_nacional":
                das = Decimal(str(impostos.get("das", 0)))
                if das > 0:
                    lancamentos.append(
                        {
                            "data": f"20/{mes}/{ano}",
                            "historico": f"{historico_base} - DAS Simples Nacional",
                            "conta_debito": "5.1.4.03",
                            "conta_credito": "2.1.3.01",
                            "valor": float(das),
                        }
                    )
            else:  # lucro_real
                for imposto, conta in [
                    ("irpj", "5.1.4.01"),
                    ("csll", "5.1.4.02"),
                    ("pis", "3.1.2.02"),
                    ("cofins", "3.1.2.03"),
                ]:
                    valor = Decimal(str(impostos.get(imposto, 0)))
                    if valor > 0:
                        lancamentos.append(
                            {
                                "data": f"20/{mes}/{ano}",
                                "historico": f"{historico_base} - {imposto.upper()}",
                                "conta_debito": conta,
                                "conta_credito": "2.1.3.01",
                                "valor": float(valor),
                            }
                        )

            return {
                "sucesso": True,
                "empresa": empresa_slug,
                "competencia": competencia,
                "regime": regime,
                "lancamentos": lancamentos,
                "total_lancamentos": len(lancamentos),
                "total_impostos": sum(lan["valor"] for lan in lancamentos),
            }
        except Exception as e:
            logger.error(f"Erro ao gerar lançamentos impostos: {e}")
            return {"sucesso": False, "erro": str(e)}

    def resumo_contabil_mensal(
        self,
        empresa_slug: str,
        periodo: str,
        receitas: float = 0,
        custos_folha: float = 0,
        impostos: float = 0,
        despesas_admin: float = 0,
    ) -> dict:
        """Gera resumo contábil mensal consolidado"""
        try:
            lucro_bruto = receitas - custos_folha
            lucro_operacional = lucro_bruto - despesas_admin
            lucro_liquido = lucro_operacional - impostos

            margem_bruta = (lucro_bruto / receitas * 100) if receitas > 0 else 0
            margem_operacional = (lucro_operacional / receitas * 100) if receitas > 0 else 0
            margem_liquida = (lucro_liquido / receitas * 100) if receitas > 0 else 0

            return {
                "sucesso": True,
                "empresa": empresa_slug,
                "periodo": periodo,
                "dre_resumido": {
                    "receita_bruta": receitas,
                    "custos_folha": custos_folha,
                    "lucro_bruto": lucro_bruto,
                    "margem_bruta_pct": round(margem_bruta, 2),
                    "despesas_admin": despesas_admin,
                    "lucro_operacional": lucro_operacional,
                    "margem_operacional_pct": round(margem_operacional, 2),
                    "impostos": impostos,
                    "lucro_liquido": lucro_liquido,
                    "margem_liquida_pct": round(margem_liquida, 2),
                },
                "classificacao": self._classificar_resultado(margem_liquida),
                "alertas": self._gerar_alertas(margem_liquida, margem_bruta),
            }
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def _classificar_resultado(self, margem: float) -> str:
        if margem >= 15:
            return "EXCELENTE"
        if margem >= 8:
            return "BOM"
        if margem >= 3:
            return "REGULAR"
        if margem >= 0:
            return "CRÍTICO"
        return "PREJUÍZO"

    def _gerar_alertas(self, margem_liquida: float, margem_bruta: float) -> list[str]:
        alertas = []
        if margem_liquida < 0:
            alertas.append("PREJUÍZO OPERACIONAL — revisar custos urgente")
        elif margem_liquida < 5:
            alertas.append("Margem líquida crítica — abaixo de 5%")
        if margem_bruta < 20:
            alertas.append("Custo de mão de obra elevado — acima de 80% da receita")
        return alertas
