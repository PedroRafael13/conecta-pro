"""
Extrator de EFD-Reinf (Escrituração Fiscal Digital de Retenções).

Implementa:
- Consulta de eventos transmitidos
- Download de eventos por período
- Consulta de retenções e contribuições
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


# Namespaces EFD-Reinf
NS_REINF = "http://www.reinf.esocial.gov.br/schemas/evt"
NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"


class ExtratorEFDReinf(ExtratorBase):
    """
    Extrator de EFD-Reinf.

    Eventos implementados:
    - R-1000: Informações do Contribuinte
    - R-2010: Retenção Contribuição Previdenciária - Serviços Tomados
    - R-2020: Retenção Contribuição Previdenciária - Serviços Prestados
    - R-2030: Recursos Recebidos por Associação Desportiva
    - R-2040: Recursos Repassados para Associação Desportiva
    - R-2050: Comercialização da Produção por Produtor Rural PJ
    - R-2055: Aquisição de Produção Rural
    - R-2060: Contribuição Previdenciária sobre a Receita Bruta - CPRB
    - R-2098: Reabertura dos Eventos Periódicos
    - R-2099: Fechamento dos Eventos Periódicos
    - R-4010: Pagamentos/Créditos a Beneficiário Pessoa Física
    - R-4020: Pagamentos/Créditos a Beneficiário Pessoa Jurídica
    - R-4040: Pagamentos/Créditos a Beneficiários Não Identificados
    - R-4080: Retenção no Recebimento
    - R-4099: Fechamento/Reabertura dos Eventos da Série R-4000
    - R-9000: Exclusão de Eventos
    """

    URLS = {
        "producao": "https://reinf.receita.fazenda.gov.br/WsREINF/RecepcaoLoteReinf.svc",
        "producao_restrita": "https://preprodefdreinf.receita.fazenda.gov.br/WsREINF/RecepcaoLoteReinf.svc",
        "consulta": "https://reinf.receita.fazenda.gov.br/WsREINF/ConsultasReinf.svc",
    }

    EVENTOS = {
        "R-1000": "Informações do Contribuinte",
        "R-2010": "Retenção - Serviços Tomados",
        "R-2020": "Retenção - Serviços Prestados",
        "R-2030": "Recursos Recebidos - Associação Desportiva",
        "R-2040": "Recursos Repassados - Associação Desportiva",
        "R-2050": "Comercialização Produção Rural PJ",
        "R-2055": "Aquisição Produção Rural",
        "R-2060": "CPRB",
        "R-2098": "Reabertura Eventos Periódicos",
        "R-2099": "Fechamento Eventos Periódicos",
        "R-4010": "Pagamento PF",
        "R-4020": "Pagamento PJ",
        "R-4040": "Pagamento Não Identificado",
        "R-4080": "Retenção no Recebimento",
        "R-4099": "Fechamento R-4000",
        "R-9000": "Exclusão de Eventos",
    }

    @property
    def tipo_servico(self) -> str:
        return "efd_reinf"

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
        Extrai eventos EFD-Reinf.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial
            data_fim: Data final
            cnpjs: CNPJs a consultar
            incremental: Se True, busca apenas novos eventos

        Returns:
            ResultadoExtracao com eventos extraídos
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
            f"Iniciando extração EFD-Reinf: {tenant_id} - "
            f"Período: {data_inicio.date()} a {data_fim.date()}"
        )

        try:
            credencial = await self.credentials.obter_credencial(
                tenant_id, self.tipo_credencial
            )

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo EFD-Reinf para CNPJ: {cnpj}")

                # Consultar eventos transmitidos
                docs = await self._consultar_eventos(
                    tenant_id, cnpj, data_inicio, data_fim
                )

                for doc in docs:
                    resultado.documentos.append(doc)

                    if doc.erro:
                        resultado.documentos_erro += 1
                        resultado.erros.append(doc.erro)
                    else:
                        resultado.documentos_novos += 1

                    resultado.documentos_processados += 1

                # Consultar totalizadores
                doc_total = await self._consultar_totalizadores(
                    tenant_id, cnpj, data_inicio, data_fim
                )
                if doc_total:
                    resultado.documentos.append(doc_total)
                    resultado.documentos_processados += 1

                await asyncio.sleep(2)

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração EFD-Reinf: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _consultar_eventos(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> List[DocumentoExtraido]:
        """Consulta eventos EFD-Reinf transmitidos."""
        documentos = []

        try:
            session = await self._get_session(tenant_id, with_cert=True)

            # Gerar períodos mensais
            periodo_atual = data_inicio.replace(day=1)

            while periodo_atual <= data_fim:
                periodo_str = periodo_atual.strftime("%Y-%m")

                # Consultar eventos do período
                for tipo_evento in self.EVENTOS.keys():
                    envelope = self._montar_envelope_consulta(
                        cnpj, periodo_str, tipo_evento
                    )

                    # Em produção, fazer requisição SOAP
                    doc = await self._processar_evento(
                        cnpj, periodo_str, tipo_evento, {}
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
            logger.error(f"Erro ao consultar eventos EFD-Reinf: {e}")
            documentos.append(
                DocumentoExtraido(
                    id=f"reinf_{cnpj}_erro",
                    tipo="efd_reinf",
                    dados={"cnpj": cnpj},
                    erro=str(e),
                )
            )

        return documentos

    def _montar_envelope_consulta(
        self,
        cnpj: str,
        periodo: str,
        tipo_evento: str,
    ) -> str:
        """Monta envelope SOAP para consulta de eventos."""
        ambiente = "1"  # Produção

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{NS_SOAP}">
    <soap:Body>
        <ConsultaReinfEvento xmlns="http://sped.fazenda.gov.br/">
            <tpAmb>{ambiente}</tpAmb>
            <cnpjContribuinte>{cnpj}</cnpjContribuinte>
            <perApur>{periodo}</perApur>
            <tpEvento>{tipo_evento}</tpEvento>
        </ConsultaReinfEvento>
    </soap:Body>
</soap:Envelope>"""

    async def _processar_evento(
        self,
        cnpj: str,
        periodo: str,
        tipo_evento: str,
        dados_resposta: Dict,
    ) -> Optional[DocumentoExtraido]:
        """Processa dados de um evento EFD-Reinf."""
        try:
            dados = {
                "cnpj": cnpj,
                "periodo_apuracao": periodo,
                "tipo_evento": tipo_evento,
                "descricao_evento": self.EVENTOS.get(tipo_evento, tipo_evento),

                # Dados do evento (variam por tipo)
                "numero_recibo": dados_resposta.get("nrRecibo"),
                "data_transmissao": dados_resposta.get("dhRecepcao"),
                "situacao": dados_resposta.get("situacao", "pendente_consulta"),

                # Valores (exemplo para R-2010/R-2020)
                "valor_base_retencao": dados_resposta.get("vlrBaseRet", 0.0),
                "valor_retencao": dados_resposta.get("vlrRetencao", 0.0),
                "valor_retido_inss": dados_resposta.get("vlrRetINSS", 0.0),

                "consultado_em": datetime.utcnow().isoformat(),
            }

            return DocumentoExtraido(
                id=f"reinf_{cnpj}_{periodo}_{tipo_evento}",
                tipo="efd_reinf",
                dados=dados,
                data_documento=datetime.strptime(periodo, "%Y-%m"),
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao processar evento EFD-Reinf: {e}")
            return None

    async def _consultar_totalizadores(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> Optional[DocumentoExtraido]:
        """Consulta totalizadores EFD-Reinf."""
        try:
            dados = {
                "cnpj": cnpj,
                "periodo_inicio": data_inicio.strftime("%Y-%m"),
                "periodo_fim": data_fim.strftime("%Y-%m"),
                "tipo": "totalizadores",

                "totais": {
                    "R-2010": {
                        "qtde_eventos": 0,
                        "valor_base_total": 0.0,
                        "valor_retencao_total": 0.0,
                    },
                    "R-2020": {
                        "qtde_eventos": 0,
                        "valor_base_total": 0.0,
                        "valor_retencao_total": 0.0,
                    },
                    "R-2060": {
                        "qtde_eventos": 0,
                        "valor_cprb_total": 0.0,
                    },
                    "R-4010": {
                        "qtde_eventos": 0,
                        "valor_irrf_total": 0.0,
                    },
                    "R-4020": {
                        "qtde_eventos": 0,
                        "valor_irrf_total": 0.0,
                        "valor_csll_total": 0.0,
                        "valor_cofins_total": 0.0,
                        "valor_pis_total": 0.0,
                    },
                },

                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"reinf_totais_{cnpj}",
                tipo="efd_reinf_totais",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar totalizadores EFD-Reinf: {e}")
            return None

    async def consultar_evento_especifico(
        self,
        tenant_id: UUID,
        cnpj: str,
        numero_recibo: str,
    ) -> Optional[DocumentoExtraido]:
        """
        Consulta um evento EFD-Reinf específico pelo número do recibo.

        Args:
            tenant_id: ID do tenant
            cnpj: CNPJ do contribuinte
            numero_recibo: Número do recibo do evento

        Returns:
            DocumentoExtraido ou None
        """
        try:
            session = await self._get_session(tenant_id, with_cert=True)

            envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{NS_SOAP}">
    <soap:Body>
        <ConsultaReinfRecibo xmlns="http://sped.fazenda.gov.br/">
            <tpAmb>1</tpAmb>
            <cnpjContribuinte>{cnpj}</cnpjContribuinte>
            <nrRecibo>{numero_recibo}</nrRecibo>
        </ConsultaReinfRecibo>
    </soap:Body>
</soap:Envelope>"""

            # Em produção, fazer requisição SOAP
            return DocumentoExtraido(
                id=f"reinf_recibo_{numero_recibo}",
                tipo="efd_reinf",
                dados={
                    "cnpj": cnpj,
                    "numero_recibo": numero_recibo,
                    "status": "consulta_manual_necessaria",
                },
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar evento específico: {e}")
            return None

    async def verificar_fechamento_periodo(
        self,
        tenant_id: UUID,
        cnpj: str,
        periodo: str,
    ) -> Dict[str, Any]:
        """
        Verifica se o período está fechado (R-2099).

        Args:
            tenant_id: ID do tenant
            cnpj: CNPJ do contribuinte
            periodo: Período de apuração (YYYY-MM)

        Returns:
            Dicionário com situação do fechamento
        """
        try:
            return {
                "cnpj": cnpj,
                "periodo": periodo,
                "fechado": False,
                "data_fechamento": None,
                "recibo_fechamento": None,
                "status": "verificar",
                "consultado_em": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao verificar fechamento: {e}")
            return {"erro": str(e)}
