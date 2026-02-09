"""
Extrator do Simples Nacional.

Implementa:
- Consulta de opção pelo Simples Nacional
- Consulta de PGDAS-D (apuração mensal)
- Consulta de DAS (documento de arrecadação)
- Consulta DEFIS (declaração anual)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from ...core.credentials import TipoCredencial
from ..base_extractor import DocumentoExtraido, ExtratorBase, ResultadoExtracao

logger = logging.getLogger(__name__)


class ExtratorSimplesNacional(ExtratorBase):
    """
    Extrator do Simples Nacional.

    Serviços:
    - Consulta de opção pelo Simples/SIMEI
    - PGDAS-D: Programa Gerador do DAS Declaratório
    - DEFIS: Declaração de Informações Socioeconômicas e Fiscais
    - Consulta de débitos e pendências
    """

    URLS = {
        "portal": "https://www8.receita.fazenda.gov.br/SimplesNacional/",
        "pgdasd": "https://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgdasd.app/",
        "defis": "https://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/defis.app/",
        "consulta_opcao": "https://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATBHE/ConsultaOptantes.app/",
        "mei": "https://www8.receita.fazenda.gov.br/SimplesNacional/Aplicacoes/ATSPO/pgmei.app/",
    }

    ANEXOS_SIMPLES = {
        "I": "Comércio",
        "II": "Indústria",
        "III": "Serviços (Fator R >= 28%)",
        "IV": "Serviços (construção, advocacia, etc.)",
        "V": "Serviços (Fator R < 28%)",
    }

    @property
    def tipo_servico(self) -> str:
        return "simples_nacional"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.RECEITA_FEDERAL

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
        cnpjs: list[str] | None = None,
        ufs: list[str] | None = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """
        Extrai dados do Simples Nacional.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial
            data_fim: Data final
            cnpjs: CNPJs a consultar
            incremental: Se True, busca apenas novos dados

        Returns:
            ResultadoExtracao com dados extraídos
        """
        resultado = ResultadoExtracao(
            servico=self.tipo_servico,
            inicio=datetime.utcnow(),
        )

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=365)

        logger.info(
            f"Iniciando extração Simples Nacional: {tenant_id} - Período: {data_inicio.date()} a {data_fim.date()}"
        )

        try:
            credencial = await self.credentials.obter_credencial(tenant_id, self.tipo_credencial)

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo Simples Nacional para CNPJ: {cnpj}")

                # Consultar opção pelo Simples
                doc_opcao = await self._consultar_opcao(tenant_id, cnpj)
                if doc_opcao:
                    resultado.documentos.append(doc_opcao)
                    resultado.documentos_processados += 1
                    if not doc_opcao.erro:
                        resultado.documentos_novos += 1

                # Consultar PGDAS-D (apurações mensais)
                docs_pgdas = await self._consultar_pgdas(tenant_id, cnpj, data_inicio, data_fim)
                for doc in docs_pgdas:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1

                # Consultar DEFIS (declaração anual)
                docs_defis = await self._consultar_defis(tenant_id, cnpj, data_inicio, data_fim)
                for doc in docs_defis:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1

                # Consultar débitos
                doc_debitos = await self._consultar_debitos(tenant_id, cnpj)
                if doc_debitos:
                    resultado.documentos.append(doc_debitos)
                    resultado.documentos_processados += 1

                await asyncio.sleep(2)

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração Simples Nacional: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _consultar_opcao(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> DocumentoExtraido | None:
        """Consulta opção pelo Simples Nacional."""
        try:
            await self._get_session(tenant_id, with_cert=True)

            # Em produção, consultar portal do Simples Nacional
            dados = {
                "cnpj": cnpj,
                "tipo": "opcao_simples",
                "opcao": {
                    "optante_simples": None,  # True/False após consulta
                    "data_opcao": None,
                    "data_exclusao": None,
                    "motivo_exclusao": None,
                    "optante_mei": None,
                    "data_enquadramento_mei": None,
                },
                "situacao_atual": {
                    "regime": "verificar",  # "simples", "mei", "normal"
                    "anexo_predominante": None,
                    "sublimite_uf": None,
                },
                "historico": [],
                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"simples_opcao_{cnpj}",
                tipo="opcao_simples",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar opção Simples: {e}")
            return DocumentoExtraido(
                id=f"simples_opcao_{cnpj}",
                tipo="opcao_simples",
                dados={"cnpj": cnpj},
                erro=str(e),
            )

    async def _consultar_pgdas(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[DocumentoExtraido]:
        """Consulta apurações PGDAS-D."""
        documentos = []

        try:
            await self._get_session(tenant_id, with_cert=True)

            # Gerar períodos mensais
            periodo_atual = data_inicio.replace(day=1)

            while periodo_atual <= data_fim:
                periodo_str = periodo_atual.strftime("%Y-%m")

                dados = {
                    "cnpj": cnpj,
                    "tipo": "pgdas",
                    "periodo_apuracao": periodo_str,
                    "apuracao": {
                        "transmitida": None,
                        "data_transmissao": None,
                        "numero_recibo": None,
                        # Receitas por anexo
                        "receitas": {
                            "anexo_i": 0.0,
                            "anexo_ii": 0.0,
                            "anexo_iii": 0.0,
                            "anexo_iv": 0.0,
                            "anexo_v": 0.0,
                        },
                        "receita_bruta_total": 0.0,
                        "receita_bruta_12_meses": 0.0,
                        # Tributos
                        "aliquota_efetiva": 0.0,
                        "valor_devido": 0.0,
                        # DAS
                        "das": {
                            "numero": None,
                            "vencimento": None,
                            "valor": 0.0,
                            "situacao": "verificar",
                        },
                    },
                    "consultado_em": datetime.utcnow().isoformat(),
                    "status": "consulta_manual_necessaria",
                }

                documentos.append(
                    DocumentoExtraido(
                        id=f"simples_pgdas_{cnpj}_{periodo_str}",
                        tipo="pgdas",
                        dados=dados,
                        data_documento=periodo_atual,
                        processado=True,
                    )
                )

                # Próximo mês
                if periodo_atual.month == 12:
                    periodo_atual = periodo_atual.replace(year=periodo_atual.year + 1, month=1)
                else:
                    periodo_atual = periodo_atual.replace(month=periodo_atual.month + 1)

        except Exception as e:
            logger.error(f"Erro ao consultar PGDAS: {e}")

        return documentos

    async def _consultar_defis(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[DocumentoExtraido]:
        """Consulta declarações DEFIS (anuais)."""
        documentos = []

        try:
            await self._get_session(tenant_id, with_cert=True)

            # Anos no período
            ano_inicio = data_inicio.year
            ano_fim = data_fim.year

            for ano in range(ano_inicio, ano_fim + 1):
                dados = {
                    "cnpj": cnpj,
                    "tipo": "defis",
                    "ano_calendario": ano,
                    "declaracao": {
                        "transmitida": None,
                        "data_transmissao": None,
                        "numero_recibo": None,
                        "receita_bruta_total": 0.0,
                        "folha_salarios": 0.0,
                        "numero_empregados": 0,
                        "distribuicao_lucros": 0.0,
                        "pro_labore": 0.0,
                        "retificadora": False,
                        "numero_retificacao": 0,
                    },
                    "consultado_em": datetime.utcnow().isoformat(),
                    "status": "consulta_manual_necessaria",
                }

                documentos.append(
                    DocumentoExtraido(
                        id=f"simples_defis_{cnpj}_{ano}",
                        tipo="defis",
                        dados=dados,
                        data_documento=datetime(ano, 12, 31),
                        processado=True,
                    )
                )

        except Exception as e:
            logger.error(f"Erro ao consultar DEFIS: {e}")

        return documentos

    async def _consultar_debitos(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> DocumentoExtraido | None:
        """Consulta débitos do Simples Nacional."""
        try:
            dados = {
                "cnpj": cnpj,
                "tipo": "debitos_simples",
                "resumo": {
                    "total_das_vencidos": 0.0,
                    "quantidade_das_vencidos": 0,
                    "total_parcelado": 0.0,
                },
                "das_em_aberto": [],
                # Exemplo:
                # {
                #     "periodo": "2024-01",
                #     "vencimento": "2024-02-20",
                #     "valor_original": 500.00,
                #     "valor_atualizado": 520.00,
                #     "situacao": "vencido",
                # }
                "parcelamentos": [],
                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"simples_debitos_{cnpj}",
                tipo="debitos_simples",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar débitos Simples: {e}")
            return None

    async def calcular_das(
        self,
        tenant_id: UUID,
        cnpj: str,
        periodo: str,
        receitas: dict[str, float],
    ) -> dict[str, Any]:
        """
        Calcula DAS para um período.

        Args:
            tenant_id: ID do tenant
            cnpj: CNPJ da empresa
            periodo: Período de apuração (YYYY-MM)
            receitas: Receitas por anexo

        Returns:
            Dicionário com cálculo do DAS
        """
        try:
            # Tabelas do Simples Nacional (simplificado)
            # Em produção, usar tabelas completas com todas as faixas

            receita_total = sum(receitas.values())

            # Faixas do Anexo I (exemplo)
            if receita_total <= 180000:
                aliquota = 4.0
                deducao = 0.0
            elif receita_total <= 360000:
                aliquota = 7.3
                deducao = 5940.0
            elif receita_total <= 720000:
                aliquota = 9.5
                deducao = 13860.0
            elif receita_total <= 1800000:
                aliquota = 10.7
                deducao = 22500.0
            elif receita_total <= 3600000:
                aliquota = 14.3
                deducao = 87300.0
            else:
                aliquota = 19.0
                deducao = 378000.0

            # Cálculo simplificado
            aliquota_efetiva = ((receita_total * aliquota / 100) - deducao) / receita_total * 100
            valor_das = receita_total * aliquota_efetiva / 100

            return {
                "cnpj": cnpj,
                "periodo": periodo,
                "receita_bruta_12_meses": receita_total,
                "receita_mes": receitas,
                "aliquota_nominal": aliquota,
                "deducao": deducao,
                "aliquota_efetiva": round(aliquota_efetiva, 2),
                "valor_das": round(valor_das, 2),
                "calculado_em": datetime.utcnow().isoformat(),
                "aviso": "Cálculo simplificado - confirmar no PGDAS-D",
            }

        except Exception as e:
            logger.error(f"Erro ao calcular DAS: {e}")
            return {"erro": str(e)}
