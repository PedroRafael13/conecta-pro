"""
Extrator de NFS-e de Manaus (SEMEF).

Implementa:
- Consulta de NFS-e emitidas
- Consulta de NFS-e recebidas
- Download de XML
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


# Namespace NFS-e ABRASF
NS_NFSE = "http://www.abrasf.org.br/nfse.xsd"


class ExtratorNFSeManaus(ExtratorBase):
    """
    Extrator de NFS-e do município de Manaus.

    Utiliza o padrão ABRASF 2.04.
    """

    # URL do webservice de Manaus
    URL_PRODUCAO = "https://nfe.manaus.am.gov.br/ws/NfseWSService"
    URL_HOMOLOGACAO = "https://nfe.manaus.am.gov.br/ws-homologacao/NfseWSService"

    @property
    def tipo_servico(self) -> str:
        return "nfse_manaus"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.NFSE_MUNICIPAL

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cnpjs: Optional[List[str]] = None,
        ufs: Optional[List[str]] = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """Extrai NFS-e de Manaus."""
        resultado = ResultadoExtracao(
            servico=self.tipo_servico,
            inicio=datetime.utcnow(),
        )

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=30)

        logger.info(f"Iniciando extração NFS-e Manaus: {tenant_id}")

        try:
            credencial = await self.credentials.obter_credencial(
                tenant_id, self.tipo_credencial, codigo_municipio="1302603"
            )

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                # Consultar NFS-e emitidas
                docs_emitidas = await self._consultar_emitidas(
                    tenant_id, cnpj, credencial.inscricao_municipal,
                    data_inicio, data_fim
                )

                for doc in docs_emitidas:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1
                    if doc.erro:
                        resultado.documentos_erro += 1
                    else:
                        resultado.documentos_novos += 1

                # Consultar NFS-e recebidas (tomadas)
                docs_tomadas = await self._consultar_tomadas(
                    tenant_id, cnpj, credencial.inscricao_municipal,
                    data_inicio, data_fim
                )

                for doc in docs_tomadas:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração NFS-e Manaus: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()

        return resultado

    async def _consultar_emitidas(
        self,
        tenant_id: UUID,
        cnpj: str,
        inscricao_municipal: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> List[DocumentoExtraido]:
        """Consulta NFS-e emitidas pelo prestador."""
        documentos = []

        envelope = self._montar_envelope_consulta(
            cnpj, inscricao_municipal, data_inicio, data_fim, "prestador"
        )

        resposta = await self._fazer_requisicao(
            tenant_id, self.URL_PRODUCAO, data=envelope
        )

        if resposta:
            documentos = self._processar_resposta_consulta(resposta)

        return documentos

    async def _consultar_tomadas(
        self,
        tenant_id: UUID,
        cnpj: str,
        inscricao_municipal: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> List[DocumentoExtraido]:
        """Consulta NFS-e tomadas (recebidas)."""
        documentos = []

        envelope = self._montar_envelope_consulta(
            cnpj, inscricao_municipal, data_inicio, data_fim, "tomador"
        )

        resposta = await self._fazer_requisicao(
            tenant_id, self.URL_PRODUCAO, data=envelope
        )

        if resposta:
            documentos = self._processar_resposta_consulta(resposta)

        return documentos

    def _montar_envelope_consulta(
        self,
        cnpj: str,
        inscricao_municipal: str,
        data_inicio: datetime,
        data_fim: datetime,
        tipo: str  # prestador ou tomador
    ) -> str:
        """Monta envelope SOAP para consulta de NFS-e."""
        data_ini = data_inicio.strftime("%Y-%m-%d")
        data_fin = data_fim.strftime("%Y-%m-%d")

        if tipo == "prestador":
            filtro = f"""
                <Prestador>
                    <CpfCnpj>
                        <Cnpj>{cnpj}</Cnpj>
                    </CpfCnpj>
                    <InscricaoMunicipal>{inscricao_municipal}</InscricaoMunicipal>
                </Prestador>"""
        else:
            filtro = f"""
                <Tomador>
                    <CpfCnpj>
                        <Cnpj>{cnpj}</Cnpj>
                    </CpfCnpj>
                </Tomador>"""

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <ConsultarNfseServicoPrestadoRequest xmlns="{NS_NFSE}">
            <ConsultarNfseServicoPrestadoEnvio>
                {filtro}
                <PeriodoEmissao>
                    <DataInicial>{data_ini}</DataInicial>
                    <DataFinal>{data_fin}</DataFinal>
                </PeriodoEmissao>
                <Pagina>1</Pagina>
            </ConsultarNfseServicoPrestadoEnvio>
        </ConsultarNfseServicoPrestadoRequest>
    </soap:Body>
</soap:Envelope>"""

    def _processar_resposta_consulta(
        self,
        xml_resposta: str
    ) -> List[DocumentoExtraido]:
        """Processa resposta da consulta de NFS-e."""
        documentos = []

        try:
            root = ET.fromstring(xml_resposta.encode())

            # Buscar NFS-e no retorno
            nfses = root.findall(".//{%s}CompNfse" % NS_NFSE)

            for comp in nfses:
                doc = self._extrair_nfse(comp)
                if doc:
                    documentos.append(doc)

        except ET.ParseError as e:
            logger.error(f"Erro ao parsear resposta NFS-e: {e}")

        return documentos

    def _extrair_nfse(self, elemento: ET.Element) -> Optional[DocumentoExtraido]:
        """Extrai dados de uma NFS-e."""
        try:
            nfse = elemento.find("{%s}Nfse" % NS_NFSE)
            if nfse is None:
                return None

            inf_nfse = nfse.find("{%s}InfNfse" % NS_NFSE)
            if inf_nfse is None:
                return None

            numero = inf_nfse.findtext("{%s}Numero" % NS_NFSE)
            codigo_verificacao = inf_nfse.findtext("{%s}CodigoVerificacao" % NS_NFSE)

            # Valores
            valores = inf_nfse.find("{%s}ValoresNfse" % NS_NFSE) or ET.Element("v")

            # Prestador
            prestador = inf_nfse.find("{%s}PrestadorServico" % NS_NFSE) or ET.Element("p")
            ident_prest = prestador.find("{%s}IdentificacaoPrestador" % NS_NFSE) or ET.Element("i")

            # Tomador
            tomador = inf_nfse.find("{%s}TomadorServico" % NS_NFSE) or ET.Element("t")
            ident_tom = tomador.find("{%s}IdentificacaoTomador" % NS_NFSE) or ET.Element("i")
            cpf_cnpj_tom = ident_tom.find("{%s}CpfCnpj" % NS_NFSE) or ET.Element("c")

            dados = {
                "numero": numero,
                "codigo_verificacao": codigo_verificacao,
                "data_emissao": inf_nfse.findtext("{%s}DataEmissao" % NS_NFSE),
                "competencia": inf_nfse.findtext("{%s}Competencia" % NS_NFSE),

                # Prestador
                "prestador_cnpj": ident_prest.findtext(".//{%s}Cnpj" % NS_NFSE),
                "prestador_nome": prestador.findtext("{%s}RazaoSocial" % NS_NFSE),

                # Tomador
                "tomador_cnpj": cpf_cnpj_tom.findtext("{%s}Cnpj" % NS_NFSE),
                "tomador_cpf": cpf_cnpj_tom.findtext("{%s}Cpf" % NS_NFSE),
                "tomador_nome": tomador.findtext("{%s}RazaoSocial" % NS_NFSE),

                # Valores
                "valor_servico": valores.findtext("{%s}ValorServicos" % NS_NFSE),
                "valor_iss": valores.findtext("{%s}ValorIss" % NS_NFSE),
                "aliquota_iss": valores.findtext("{%s}Aliquota" % NS_NFSE),

                # Serviço
                "discriminacao": inf_nfse.findtext(".//{%s}Discriminacao" % NS_NFSE),
                "codigo_servico": inf_nfse.findtext(".//{%s}ItemListaServico" % NS_NFSE),
            }

            return DocumentoExtraido(
                id=f"{numero}_{codigo_verificacao}",
                tipo="nfse",
                dados=dados,
                xml_original=ET.tostring(elemento, encoding="unicode"),
                data_documento=self._parse_data(dados.get("data_emissao")),
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao extrair NFS-e: {e}")
            return None

    def _parse_data(self, data_str: Optional[str]) -> Optional[datetime]:
        """Parseia string de data."""
        if not data_str:
            return None
        try:
            return datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        except:
            return None
