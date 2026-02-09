"""
Extrator de MDF-e da SEFAZ.

Implementa:
- Consulta de status de MDF-e
- Distribuição DFe (documentos destinados)
- Download de XML
"""

import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID
from xml.etree.ElementTree import Element  # noqa: S405

from defusedxml import ElementTree as ET  # noqa: N817

from ...core.credentials import TipoCredencial
from ..base_extractor import DocumentoExtraido, ExtratorBase, ResultadoExtracao

logger = logging.getLogger(__name__)


# Namespaces XML
NS_MDFE = "http://www.portalfiscal.inf.br/mdfe"
NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"

NAMESPACES = {
    "mdfe": NS_MDFE,
    "soap": NS_SOAP,
}


class ExtratorMDFe(ExtratorBase):
    """
    Extrator de MDF-e da SEFAZ.

    Serviços utilizados:
    - MDFeStatusServico: Verificar disponibilidade
    - MDFeConsulta: Consultar MDF-e por chave
    - MDFeDistribuicaoDFe: Baixar documentos destinados
    """

    SERVICOS = {
        "status": "MDFeStatusServico",
        "consulta": "MDFeConsulta",
        "distribuicao": "MDFeDistribuicaoDFe",
    }

    @property
    def tipo_servico(self) -> str:
        return "sefaz_mdfe"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.SEFAZ_MDFE

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
        Extrai MDF-e da SEFAZ.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial
            data_fim: Data final
            cnpjs: CNPJs a consultar
            ufs: UFs para consulta
            incremental: Se True, usa NSU para incremental

        Returns:
            ResultadoExtracao
        """
        resultado = ResultadoExtracao(
            servico=self.tipo_servico,
            inicio=datetime.utcnow(),
        )

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=30)

        logger.info(f"Iniciando extração MDF-e: {tenant_id} - Período: {data_inicio.date()} a {data_fim.date()}")

        try:
            credencial = await self.credentials.obter_credencial(tenant_id, self.tipo_credencial)

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo MDF-e para CNPJ: {cnpj}")

                docs = await self._extrair_distribuicao(tenant_id, cnpj, data_inicio, data_fim, incremental)

                for doc in docs:
                    resultado.documentos.append(doc)

                    if doc.erro:
                        resultado.documentos_erro += 1
                        resultado.erros.append(doc.erro)
                    elif doc.processado:
                        resultado.documentos_novos += 1

                    resultado.documentos_processados += 1

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração MDF-e: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _extrair_distribuicao(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
        incremental: bool,
    ) -> list[DocumentoExtraido]:
        """Extrai documentos via MDFeDistribuicaoDFe."""
        documentos = []
        nsu_atual = "000000000000000"

        max_consultas = 100
        consultas = 0

        while consultas < max_consultas:
            consultas += 1

            try:
                envelope = self._montar_envelope_distribuicao(cnpj, nsu_atual)
                url = await self._obter_url_servico("AN", "distribuicao")

                resposta = await self._fazer_requisicao(tenant_id, url, data=envelope)

                if not resposta:
                    logger.warning("Sem resposta do serviço de distribuição MDF-e")
                    break

                docs, ultimo_nsu, tem_mais = self._processar_resposta_distribuicao(resposta)

                for doc in docs:
                    doc = await self._processar_documento(doc)
                    documentos.append(doc)

                if not tem_mais or ultimo_nsu == nsu_atual:
                    break

                nsu_atual = ultimo_nsu
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Erro na consulta distribuição MDF-e: {e}")
                break

        logger.info(f"Distribuição MDF-e: {len(documentos)} documentos extraídos")
        return documentos

    def _montar_envelope_distribuicao(self, cnpj: str, nsu: str, tipo_consulta: str = "distNSU") -> str:
        """Monta envelope SOAP para distribuição DFe de MDF-e."""
        ambiente = "1"
        cod_uf = "13"

        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}">
    <soap12:Body>
        <mdfeDistDFeInteresse xmlns="{NS_MDFE}">
            <mdfeDadosMsg>
                <distDFeInt xmlns="{NS_MDFE}" versao="3.00">
                    <tpAmb>{ambiente}</tpAmb>
                    <cUFAutor>{cod_uf}</cUFAutor>
                    <CNPJ>{cnpj}</CNPJ>
                    <{tipo_consulta}>
                        <NSU>{nsu}</NSU>
                    </{tipo_consulta}>
                </distDFeInt>
            </mdfeDadosMsg>
        </mdfeDistDFeInteresse>
    </soap12:Body>
</soap12:Envelope>"""

        return envelope

    def _processar_resposta_distribuicao(self, xml_resposta: str) -> tuple[list[DocumentoExtraido], str, bool]:
        """Processa resposta da distribuição DFe de MDF-e."""
        documentos = []
        ultimo_nsu = "000000000000000"
        tem_mais = False

        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(f".//{{{NS_MDFE}}}retDistDFeInt")
            if ret is None:
                return documentos, ultimo_nsu, False

            c_stat = ret.findtext(f"{{{NS_MDFE}}}cStat")
            if c_stat not in ["137", "138"]:
                logger.warning(f"Status distribuição MDF-e: {c_stat}")
                return documentos, ultimo_nsu, False

            ultimo_nsu = ret.findtext(f"{{{NS_MDFE}}}ultNSU") or ultimo_nsu
            max_nsu = ret.findtext(f"{{{NS_MDFE}}}maxNSU") or ultimo_nsu

            tem_mais = ultimo_nsu < max_nsu

            lote = ret.find(f"{{{NS_MDFE}}}loteDistDFeInt")
            if lote is not None:
                for doc_zip in lote.findall(f"{{{NS_MDFE}}}docZip"):
                    nsu = doc_zip.get("NSU")
                    schema = doc_zip.get("schema", "")

                    import base64
                    import gzip

                    conteudo_b64 = doc_zip.text
                    if conteudo_b64:
                        try:
                            conteudo_gzip = base64.b64decode(conteudo_b64)
                            xml_doc = gzip.decompress(conteudo_gzip).decode("utf-8")

                            doc = self._extrair_dados_documento(xml_doc, schema, nsu)
                            if doc:
                                documentos.append(doc)

                        except Exception as e:
                            logger.error(f"Erro ao decodificar MDF-e NSU {nsu}: {e}")

        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML de resposta MDF-e: {e}")

        return documentos, ultimo_nsu, tem_mais

    def _extrair_dados_documento(self, xml: str, schema: str, nsu: str) -> DocumentoExtraido | None:
        """Extrai dados de um documento MDF-e XML."""
        try:
            root = ET.fromstring(xml.encode())

            if "procMDFe" in schema or root.tag.endswith("mdfeProc"):
                return self._extrair_mdfe(root, xml, nsu)
            elif "resMDFe" in schema:
                return self._extrair_resumo_mdfe(root, xml, nsu)
            elif "resEvento" in schema:
                return self._extrair_evento(root, xml, nsu)
            else:
                logger.debug(f"Schema MDF-e não reconhecido: {schema}")
                return None

        except Exception as e:
            logger.error(f"Erro ao extrair dados do MDF-e: {e}")
            return None

    def _extrair_mdfe(self, root: Element, xml: str, nsu: str) -> DocumentoExtraido:
        """Extrai dados de MDF-e completo."""
        inf_mdfe = root.find(f".//{{{NS_MDFE}}}infMDFe")

        if inf_mdfe is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="mdfe",
                dados={},
                xml_original=xml,
                erro="infMDFe não encontrado",
            )

        chave = inf_mdfe.get("Id", "").replace("MDFe", "")

        ide = inf_mdfe.find(f"{{{NS_MDFE}}}ide") or ET.Element("ide")
        emit = inf_mdfe.find(f"{{{NS_MDFE}}}emit") or ET.Element("emit")
        tot = inf_mdfe.find(f"{{{NS_MDFE}}}tot") or ET.Element("tot")

        # Informações de percurso
        inf_mun_carrega = ide.findall(f"{{{NS_MDFE}}}infMunCarrega")
        municipios_carregamento = []
        for mun in inf_mun_carrega:
            municipios_carregamento.append(
                {
                    "codigo": mun.findtext(f"{{{NS_MDFE}}}cMunCarrega"),
                    "nome": mun.findtext(f"{{{NS_MDFE}}}xMunCarrega"),
                }
            )

        # Informações de percurso UF
        inf_percurso = ide.findall(f"{{{NS_MDFE}}}infPercurso")
        ufs_percurso = [p.findtext(f"{{{NS_MDFE}}}UFPer") for p in inf_percurso]

        dados = {
            "chave_acesso": chave,
            "numero": ide.findtext(f"{{{NS_MDFE}}}nMDF"),
            "serie": ide.findtext(f"{{{NS_MDFE}}}serie"),
            "data_emissao": ide.findtext(f"{{{NS_MDFE}}}dhEmi"),
            "modal": ide.findtext(f"{{{NS_MDFE}}}modal"),
            "tipo_emitente": ide.findtext(f"{{{NS_MDFE}}}tpEmit"),
            "tipo_transportador": ide.findtext(f"{{{NS_MDFE}}}tpTransp"),
            "uf_inicio": ide.findtext(f"{{{NS_MDFE}}}UFIni"),
            "uf_fim": ide.findtext(f"{{{NS_MDFE}}}UFFim"),
            "emit_cnpj": emit.findtext(f"{{{NS_MDFE}}}CNPJ"),
            "emit_nome": emit.findtext(f"{{{NS_MDFE}}}xNome"),
            "emit_uf": self._extrair_uf_elemento(emit, "enderEmit"),
            "qtde_cte": tot.findtext(f"{{{NS_MDFE}}}qCTe"),
            "qtde_nfe": tot.findtext(f"{{{NS_MDFE}}}qNFe"),
            "valor_carga": tot.findtext(f"{{{NS_MDFE}}}vCarga"),
            "peso_bruto": tot.findtext(f"{{{NS_MDFE}}}qCarga"),
            "municipios_carregamento": municipios_carregamento,
            "ufs_percurso": ufs_percurso,
            "nsu": nsu,
        }

        # Protocolo de autorização
        prot = root.find(f".//{{{NS_MDFE}}}protMDFe")
        if prot is not None:
            inf_prot = prot.find(f"{{{NS_MDFE}}}infProt")
            if inf_prot is not None:
                dados["protocolo"] = inf_prot.findtext(f"{{{NS_MDFE}}}nProt")
                dados["status_sefaz"] = inf_prot.findtext(f"{{{NS_MDFE}}}cStat")
                dados["data_autorizacao"] = inf_prot.findtext(f"{{{NS_MDFE}}}dhRecbto")

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="mdfe",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_resumo_mdfe(self, root: Element, xml: str, nsu: str) -> DocumentoExtraido:
        """Extrai dados de resumo de MDF-e."""
        res = root if root.tag.endswith("resMDFe") else root.find(f".//{{{NS_MDFE}}}resMDFe")

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="resumo_mdfe",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext(f"{{{NS_MDFE}}}chMDFe")

        dados = {
            "chave_acesso": chave,
            "cnpj_emitente": res.findtext(f"{{{NS_MDFE}}}CNPJ"),
            "nome_emitente": res.findtext(f"{{{NS_MDFE}}}xNome"),
            "data_emissao": res.findtext(f"{{{NS_MDFE}}}dhEmi"),
            "modal": res.findtext(f"{{{NS_MDFE}}}modal"),
            "situacao": res.findtext(f"{{{NS_MDFE}}}cSitMDFe"),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="resumo_mdfe",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_evento(self, root: Element, xml: str, nsu: str) -> DocumentoExtraido:
        """Extrai dados de evento MDF-e."""
        res = root if root.tag.endswith("resEvento") else root.find(f".//{{{NS_MDFE}}}resEvento")

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="evento_mdfe",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext(f"{{{NS_MDFE}}}chMDFe")
        tipo_evento = res.findtext(f"{{{NS_MDFE}}}tpEvento")

        dados = {
            "chave_acesso": chave,
            "tipo_evento": tipo_evento,
            "descricao_evento": res.findtext(f"{{{NS_MDFE}}}xEvento"),
            "numero_sequencial": res.findtext(f"{{{NS_MDFE}}}nSeqEvento"),
            "data_evento": res.findtext(f"{{{NS_MDFE}}}dhEvento"),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=f"{chave}_{tipo_evento}_{nsu}",
            tipo="evento_mdfe",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_evento")),
        )

    def _extrair_uf_elemento(self, elem: Element, nome_ender: str) -> str | None:
        """Extrai UF de um elemento de endereço."""
        ender = elem.find(f"{{{NS_MDFE}}}{nome_ender}")
        if ender is not None:
            return ender.findtext(f"{{{NS_MDFE}}}UF")
        return None

    def _parse_data(self, data_str: str | None) -> datetime | None:
        """Parseia string de data para datetime."""
        if not data_str:
            return None
        try:
            return datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        except Exception:
            try:
                return datetime.strptime(data_str[:19], "%Y-%m-%dT%H:%M:%S")
            except Exception:
                return None

    async def _obter_url_servico(self, uf: str, servico: str) -> str:
        """Obtém URL do serviço MDF-e para uma UF."""
        nome_servico = self.SERVICOS.get(servico, servico)

        url, usando_contingencia = await self.comutador.obter_endpoint(uf, "mdfe", nome_servico)

        if usando_contingencia:
            logger.warning(f"Usando contingência MDF-e para {uf}")

        return url

    async def consultar_mdfe(self, tenant_id: UUID, chave: str) -> DocumentoExtraido | None:
        """Consulta um MDF-e específico por chave de acesso."""
        cod_uf = chave[:2]
        uf = self._cod_uf_para_sigla(cod_uf)

        envelope = self._montar_envelope_consulta(chave)
        url = await self._obter_url_servico(uf, "consulta")

        resposta = await self._fazer_requisicao(tenant_id, url, data=envelope)

        if resposta:
            return self._processar_resposta_consulta(resposta, chave)

        return None

    def _montar_envelope_consulta(self, chave: str) -> str:
        """Monta envelope SOAP para consulta de MDF-e."""
        ambiente = "1"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}">
    <soap12:Body>
        <mdfeConsultaMDF xmlns="{NS_MDFE}">
            <mdfeDadosMsg>
                <consSitMDFe xmlns="{NS_MDFE}" versao="3.00">
                    <tpAmb>{ambiente}</tpAmb>
                    <xServ>CONSULTAR</xServ>
                    <chMDFe>{chave}</chMDFe>
                </consSitMDFe>
            </mdfeDadosMsg>
        </mdfeConsultaMDF>
    </soap12:Body>
</soap12:Envelope>"""

    def _processar_resposta_consulta(self, xml_resposta: str, chave: str) -> DocumentoExtraido | None:
        """Processa resposta da consulta de MDF-e."""
        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(f".//{{{NS_MDFE}}}retConsSitMDFe")
            if ret is None:
                return None

            c_stat = ret.findtext(f"{{{NS_MDFE}}}cStat")

            dados = {
                "chave_acesso": chave,
                "status_sefaz": c_stat,
                "motivo": ret.findtext(f"{{{NS_MDFE}}}xMotivo"),
            }

            if c_stat in ["100", "101", "132"]:
                prot = ret.find(f"{{{NS_MDFE}}}protMDFe")
                if prot is not None:
                    inf_prot = prot.find(f"{{{NS_MDFE}}}infProt")
                    if inf_prot is not None:
                        dados["protocolo"] = inf_prot.findtext(f"{{{NS_MDFE}}}nProt")
                        dados["data_autorizacao"] = inf_prot.findtext(f"{{{NS_MDFE}}}dhRecbto")

            return DocumentoExtraido(
                id=chave,
                tipo="consulta_mdfe",
                dados=dados,
                xml_original=xml_resposta,
            )

        except Exception as e:
            logger.error(f"Erro ao processar consulta MDF-e: {e}")
            return None

    def _cod_uf_para_sigla(self, cod: str) -> str:
        """Converte código IBGE para sigla da UF."""
        mapeamento = {
            "11": "RO",
            "12": "AC",
            "13": "AM",
            "14": "RR",
            "15": "PA",
            "16": "AP",
            "17": "TO",
            "21": "MA",
            "22": "PI",
            "23": "CE",
            "24": "RN",
            "25": "PB",
            "26": "PE",
            "27": "AL",
            "28": "SE",
            "29": "BA",
            "31": "MG",
            "32": "ES",
            "33": "RJ",
            "35": "SP",
            "41": "PR",
            "42": "SC",
            "43": "RS",
            "50": "MS",
            "51": "MT",
            "52": "GO",
            "53": "DF",
        }
        return mapeamento.get(cod, "SP")
