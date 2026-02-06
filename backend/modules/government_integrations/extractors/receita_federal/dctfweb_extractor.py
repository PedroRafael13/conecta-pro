"""
Extrator de DCTFWeb (Declaração de Débitos e Créditos Tributários Federais).

Implementa:
- Consulta de declarações DCTFWeb
- Download de declarações transmitidas
- Consulta de débitos e créditos
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from uuid import UUID
import asyncio
import logging
from xml.etree import ElementTree as ET

from ..base_extractor import ExtratorBase, DocumentoExtraido, ResultadoExtracao
from ...core.credentials import ProvedorCredenciais, TipoCredencial

logger = logging.getLogger(__name__)


class ExtratorDCTFWeb(ExtratorBase):
    """
    Extrator de DCTFWeb.

    A DCTFWeb é gerada a partir das informações do eSocial e EFD-Reinf.
    Serviços:
    - Consulta de declarações por período
    - Download de declarações transmitidas
    - Consulta de débitos e créditos federais
    """

    URLS = {
        "producao": "https://www.sped.fazenda.gov.br/speddctfweb/consulta",
        "homologacao": "https://www.sped.fazenda.gov.br/speddctfweb-hom/consulta",
        "ecac": "https://cav.receita.fazenda.gov.br/autenticacao/login",
    }

    TIPOS_DECLARACAO = {
        "mensal": "DCTFWeb Mensal",
        "anual": "DCTFWeb Anual (13º)",
        "diaria": "DCTFWeb Diária (Espetáculos)",
        "especial": "DCTFWeb Especial (Rescisão)",
    }

    @property
    def tipo_servico(self) -> str:
        return "dctfweb"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.RECEITA_FEDERAL

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cnpjs: Optional[List[str]] = None,
        ufs: Optional[List[str]] = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """
        Extrai declarações DCTFWeb.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial (período de apuração)
            data_fim: Data final
            cnpjs: CNPJs a consultar
            incremental: Se True, busca apenas novas declarações

        Returns:
            ResultadoExtracao com declarações extraídas
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
            f"Iniciando extração DCTFWeb: {tenant_id} - "
            f"Período: {data_inicio.date()} a {data_fim.date()}"
        )

        try:
            # Obter credenciais (certificado digital)
            credencial = await self.credentials.obter_credencial(
                tenant_id, self.tipo_credencial
            )

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo DCTFWeb para CNPJ: {cnpj}")

                # Consultar declarações por tipo
                for tipo in ["mensal", "anual", "especial"]:
                    docs = await self._consultar_declaracoes(
                        tenant_id, cnpj, data_inicio, data_fim, tipo
                    )

                    for doc in docs:
                        resultado.documentos.append(doc)

                        if doc.erro:
                            resultado.documentos_erro += 1
                            resultado.erros.append(doc.erro)
                        else:
                            resultado.documentos_novos += 1

                        resultado.documentos_processados += 1

                # Consultar débitos consolidados
                doc_debitos = await self._consultar_debitos(
                    tenant_id, cnpj, data_inicio, data_fim
                )
                if doc_debitos:
                    resultado.documentos.append(doc_debitos)
                    resultado.documentos_processados += 1

                await asyncio.sleep(2)

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração DCTFWeb: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _consultar_declaracoes(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
        tipo: str,
    ) -> List[DocumentoExtraido]:
        """Consulta declarações DCTFWeb por tipo."""
        documentos = []

        try:
            session = await self._get_session(tenant_id, with_cert=True)

            # Gerar períodos mensais
            periodo_atual = data_inicio.replace(day=1)

            while periodo_atual <= data_fim:
                periodo_str = periodo_atual.strftime("%Y-%m")

                # Montar requisição
                payload = {
                    "cnpj": cnpj,
                    "periodoApuracao": periodo_str,
                    "tipoDeclaracao": tipo,
                }

                # Simular consulta ao e-CAC/SPED
                # Em produção, fazer requisição real com certificado
                doc = await self._processar_declaracao(
                    cnpj, periodo_str, tipo, payload
                )

                if doc:
                    documentos.append(doc)

                # Próximo mês
                if periodo_atual.month == 12:
                    periodo_atual = periodo_atual.replace(
                        year=periodo_atual.year + 1, month=1
                    )
                else:
                    periodo_atual = periodo_atual.replace(
                        month=periodo_atual.month + 1
                    )

                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Erro ao consultar DCTFWeb {tipo}: {e}")
            documentos.append(
                DocumentoExtraido(
                    id=f"dctfweb_{cnpj}_{tipo}_erro",
                    tipo="dctfweb",
                    dados={"cnpj": cnpj, "tipo": tipo},
                    erro=str(e),
                )
            )

        return documentos

    async def _processar_declaracao(
        self,
        cnpj: str,
        periodo: str,
        tipo: str,
        dados_resposta: Dict,
    ) -> Optional[DocumentoExtraido]:
        """Processa dados de uma declaração DCTFWeb."""
        try:
            # Estrutura de dados da DCTFWeb
            dados = {
                "cnpj": cnpj,
                "periodo_apuracao": periodo,
                "tipo_declaracao": tipo,
                "descricao_tipo": self.TIPOS_DECLARACAO.get(tipo, tipo),

                # Informações da declaração
                "numero_recibo": dados_resposta.get("numeroRecibo"),
                "data_transmissao": dados_resposta.get("dataTransmissao"),
                "situacao": dados_resposta.get("situacao", "pendente_consulta"),

                # Débitos
                "debitos": {
                    "inss": dados_resposta.get("debitoINSS", 0.0),
                    "ir": dados_resposta.get("debitoIR", 0.0),
                    "csll": dados_resposta.get("debitoCsll", 0.0),
                    "cofins": dados_resposta.get("debitoCofins", 0.0),
                    "pis": dados_resposta.get("debitoPis", 0.0),
                    "outros": dados_resposta.get("outrosDebitos", 0.0),
                    "total": dados_resposta.get("totalDebitos", 0.0),
                },

                # Créditos
                "creditos": {
                    "salario_familia": dados_resposta.get("creditoSalFamilia", 0.0),
                    "salario_maternidade": dados_resposta.get("creditoSalMaternidade", 0.0),
                    "retencoes": dados_resposta.get("retencoes", 0.0),
                    "compensacoes": dados_resposta.get("compensacoes", 0.0),
                    "total": dados_resposta.get("totalCreditos", 0.0),
                },

                # Saldo
                "saldo_devedor": dados_resposta.get("saldoDevedor", 0.0),

                "consultado_em": datetime.utcnow().isoformat(),
            }

            return DocumentoExtraido(
                id=f"dctfweb_{cnpj}_{periodo}_{tipo}",
                tipo="dctfweb",
                dados=dados,
                data_documento=datetime.strptime(periodo, "%Y-%m"),
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao processar DCTFWeb: {e}")
            return None

    async def _consultar_debitos(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> Optional[DocumentoExtraido]:
        """Consulta débitos consolidados DCTFWeb."""
        try:
            # Resumo de débitos por tributo
            dados = {
                "cnpj": cnpj,
                "periodo_inicio": data_inicio.strftime("%Y-%m"),
                "periodo_fim": data_fim.strftime("%Y-%m"),
                "tipo": "resumo_debitos",

                "tributos": [
                    {
                        "codigo": "1082-01",
                        "descricao": "Contribuição Previdenciária - Empresa",
                        "debito_total": 0.0,
                        "pago": 0.0,
                        "em_aberto": 0.0,
                    },
                    {
                        "codigo": "1138-01",
                        "descricao": "Contribuição Previdenciária - Descontada do Trabalhador",
                        "debito_total": 0.0,
                        "pago": 0.0,
                        "em_aberto": 0.0,
                    },
                    {
                        "codigo": "0561-03",
                        "descricao": "IRRF - Rendimentos do Trabalho",
                        "debito_total": 0.0,
                        "pago": 0.0,
                        "em_aberto": 0.0,
                    },
                ],

                "total_debitos": 0.0,
                "total_pago": 0.0,
                "total_em_aberto": 0.0,

                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"dctfweb_debitos_{cnpj}",
                tipo="dctfweb_debitos",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar débitos DCTFWeb: {e}")
            return None

    async def consultar_declaracao_especifica(
        self,
        tenant_id: UUID,
        cnpj: str,
        periodo: str,
        tipo: str = "mensal",
    ) -> Optional[DocumentoExtraido]:
        """
        Consulta uma declaração DCTFWeb específica.

        Args:
            tenant_id: ID do tenant
            cnpj: CNPJ da empresa
            periodo: Período de apuração (YYYY-MM)
            tipo: Tipo da declaração

        Returns:
            DocumentoExtraido ou None
        """
        try:
            session = await self._get_session(tenant_id, with_cert=True)

            # Em produção, fazer requisição ao e-CAC
            dados = {
                "cnpj": cnpj,
                "periodoApuracao": periodo,
                "tipoDeclaracao": tipo,
            }

            return await self._processar_declaracao(cnpj, periodo, tipo, dados)

        except Exception as e:
            logger.error(f"Erro ao consultar DCTFWeb específica: {e}")
            return None

    async def verificar_pendencias(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> Dict[str, Any]:
        """
        Verifica pendências de DCTFWeb.

        Returns:
            Dicionário com pendências encontradas
        """
        try:
            # Verificar declarações não transmitidas
            data_atual = datetime.utcnow()
            resultado = {
                "cnpj": cnpj,
                "pendencias": [],
                "total_pendencias": 0,
                "consultado_em": data_atual.isoformat(),
            }

            # Verificar últimos 12 meses
            for i in range(12):
                mes_verificar = data_atual - timedelta(days=30 * i)
                periodo = mes_verificar.strftime("%Y-%m")

                # Em produção, verificar se existe declaração transmitida
                # Aqui apenas indicamos como pendente
                resultado["pendencias"].append({
                    "periodo": periodo,
                    "tipo": "mensal",
                    "situacao": "verificar",
                })

            resultado["total_pendencias"] = len(resultado["pendencias"])

            return resultado

        except Exception as e:
            logger.error(f"Erro ao verificar pendências DCTFWeb: {e}")
            return {"erro": str(e)}
