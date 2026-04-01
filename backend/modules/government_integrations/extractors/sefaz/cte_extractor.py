"""
Extrator de CT-e da SEFAZ.

Implementa:
- Consulta de status de CT-e
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
NS_CTE = "http://www.portalfiscal.inf.br/cte"
NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"

NAMESPACES = {
    "cte": NS_CTE,
    "soap": NS_SOAP,
}


class ExtratorCTe(ExtratorBase):
    """
    Extrator de CT-e da SEFAZ.

    Serviços utilizados:
    - CTeStatusServico: Verificar disponibilidade
    - CTeConsultaProtocolo: Consultar CT-e por chave
    - CTeDistribuicaoDFe: Baixar documentos destinados
    """

    SERVICOS = {
        "status": "CTeStatusServico4",
        "consulta": "CTeConsultaProtocolo4",
        "distribuicao": "CTeDistribuicaoDFe",
    }

    @property
    def tipo_servico(self) -> str:
        return "sefaz_cte"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.SEFAZ_CTE

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
        Extrai CT-e da SEFAZ.

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

        # Defaults
        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=30)

        logger.info(f"Iniciando extração CT-e: {tenant_id} - Período: {data_inicio.date()} a {data_fim.date()}")

        try:
            # Obter credenciais
            credencial = await self.credentials.obter_credencial(tenant_id, self.tipo_credencial)

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            # Extrair para cada CNPJ
            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo CT-e para CNPJ: {cnpj}")

                # Usar distribuição DFe para obter documentos
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
            logger.error(f"Erro na extração CT-e: {e}")
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
        """Extrai documentos via CTeDistribuicaoDFe."""
        documentos = []
        nsu_atual = "000000000000000"

        if incremental:
            # TODO: Buscar último NSU processado do banco
            pass

        max_consultas = 100
        consultas = 0

        while consultas < max_consultas:
            consultas += 1

            try:
                envelope = self._montar_envelope_distribuicao(cnpj, nsu_atual)
                url = await self._obter_url_servico("AN", "distribuicao")

                resposta = await self._fazer_requisicao(tenant_id, url, data=envelope)

                if not resposta:
                    logger.warning("Sem resposta do serviço de distribuição CT-e")
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
                logger.error(f"Erro na consulta distribuição CT-e: {e}")
                break

        logger.info(f"Distribuição CT-e: {len(documentos)} documentos extraídos")
        return documentos

    def _montar_envelope_distribuicao(self, cnpj: str, nsu: str, tipo_consulta: str = "distNSU") -> str:
        """Monta envelope SOAP para distribuição DFe de CT-e."""
        ambiente = "1"  # Produção
        cod_uf = "13"  # AM

        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}">
    <soap12:Body>
        <cteDistDFeInteresse xmlns="{NS_CTE}">
            <cteDadosMsg>
                <distDFeInt xmlns="{NS_CTE}" versao="1.00">
                    <tpAmb>{ambiente}</tpAmb>
                    <cUFAutor>{cod_uf}</cUFAutor>
                    <CNPJ>{cnpj}</CNPJ>
                    <{tipo_consulta}>
                        <NSU>{nsu}</NSU>
                    </{tipo_consulta}>
                </distDFeInt>
            </cteDadosMsg>
        </cteDistDFeInteresse>
    </soap12:Body>
</soap12:Envelope>"""

        return envelope

    def _processar_resposta_distribuicao(self, xml_resposta: str) -> tuple[list[DocumentoExtraido], str, bool]:
        """Processa resposta da distribuição DFe de CT-e."""
        documentos = []
        ultimo_nsu = "000000000000000"
        tem_mais = False

        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(f".//{{{NS_CTE}}}retDistDFeInt")
            if ret is None:
                return documentos, ultimo_nsu, False

            c_stat = ret.findtext(f"{{{NS_CTE}}}cStat")
            if c_stat not in ["137", "138"]:
                logger.warning(f"Status distribuição CT-e: {c_stat}")
                return documentos, ultimo_nsu, False

            ultimo_nsu = ret.findtext(f"{{{NS_CTE}}}ultNSU") or ultimo_nsu
            max_nsu = ret.findtext(f"{{{NS_CTE}}}maxNSU") or ultimo_nsu

            tem_mais = ultimo_nsu < max_nsu

            lote = ret.find(f"{{{NS_CTE}}}loteDistDFeInt")
            if lote is not None:
                for doc_zip in lote.findall(f"{{{NS_CTE}}}docZip"):
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
                            logger.error(f"Erro ao decodificar CT-e NSU {nsu}: {e}")

        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML de resposta CT-e: {e}")

        return documentos, ultimo_nsu, tem_mais

    def _extrair_dados_documento(self, xml: str, schema: str, nsu: str) -> DocumentoExtraido | None:
        """Extrai dados de um documento CT-e XML."""
        try:
            root = ET.fromstring(xml.encode())

            if "procCTe" in schema or root.tag.endswith("cteProc"):
                return self._extrair_cte(root, xml, nsu)
            elif "resCTe" in schema:
                return self._extrair_resumo_cte(root, xml, nsu)
            elif "resEvento" in schema:
                return self._extrair_evento(root, xml, nsu)
            else:
                logger.debug(f"Schema CT-e não reconhecido: {schema}")
                return None

        except Exception as e:
            logger.error(f"Erro ao extrair dados do CT-e: {e}")
            return None

    def _extrair_cte(self, root: Element, xml: str, nsu: str) -> DocumentoExtraido:
        """Extrai dados de CT-e completo."""
        inf_cte = root.find(f".//{{{NS_CTE}}}infCte")

        if inf_cte is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="cte",
                dados={},
                xml_original=xml,
                erro="infCte não encontrado",
            )

        chave = inf_cte.get("Id", "").replace("CTe", "")

        ide = inf_cte.find(f"{{{NS_CTE}}}ide") or ET.Element("ide")
        emit = inf_cte.find(f"{{{NS_CTE}}}emit") or ET.Element("emit")
        rem = inf_cte.find(f"{{{NS_CTE}}}rem") or ET.Element("rem")
        dest = inf_cte.find(f"{{{NS_CTE}}}dest") or ET.Element("dest")
        v_prest = inf_cte.find(f"{{{NS_CTE}}}vPrest") or ET.Element("vPrest")

        dados = {
            "chave_acesso": chave,
            "numero": ide.findtext(f"{{{NS_CTE}}}nCT"),
            "serie": ide.findtext(f"{{{NS_CTE}}}serie"),
            "data_emissao": ide.findtext(f"{{{NS_CTE}}}dhEmi"),
            "modal": ide.findtext(f"{{{NS_CTE}}}modal"),
            "tipo_servico": ide.findtext(f"{{{NS_CTE}}}tpServ"),
            "cfop": ide.findtext(f"{{{NS_CTE}}}CFOP"),
            "emit_cnpj": emit.findtext(f"{{{NS_CTE}}}CNPJ"),
            "emit_nome": emit.findtext(f"{{{NS_CTE}}}xNome"),
            "emit_uf": self._extrair_uf_elemento(emit, "enderEmit"),
            "rem_cnpj": rem.findtext(f"{{{NS_CTE}}}CNPJ") or rem.findtext(f"{{{NS_CTE}}}CPF"),
            "rem_nome": rem.findtext(f"{{{NS_CTE}}}xNome"),
            "dest_cnpj": dest.findtext(f"{{{NS_CTE}}}CNPJ") or dest.findtext(f"{{{NS_CTE}}}CPF"),
            "dest_nome": dest.findtext(f"{{{NS_CTE}}}xNome"),
            "valor_total": v_prest.findtext(f"{{{NS_CTE}}}vTPrest"),
            "valor_receber": v_prest.findtext(f"{{{NS_CTE}}}vRec"),
            "nsu": nsu,
        }

        # Protocolo de autorização
        prot = root.find(f".//{{{NS_CTE}}}protCTe")
        if prot is not None:
            inf_prot = prot.find(f"{{{NS_CTE}}}infProt")
            if inf_prot is not None:
                dados["protocolo"] = inf_prot.findtext(f"{{{NS_CTE}}}nProt")
                dados["status_sefaz"] = inf_prot.findtext(f"{{{NS_CTE}}}cStat")
                dados["data_autorizacao"] = inf_prot.findtext(f"{{{NS_CTE}}}dhRecbto")

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="cte",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_resumo_cte(self, root: Element, xml: str, nsu: str) -> DocumentoExtraido:
        """Extrai dados de resumo de CT-e."""
        res = root if root.tag.endswith("resCTe") else root.find(f".//{{{NS_CTE}}}resCTe")

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="resumo_cte",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext(f"{{{NS_CTE}}}chCTe")

        dados = {
            "chave_acesso": chave,
            "cnpj_emitente": res.findtext(f"{{{NS_CTE}}}CNPJ"),
            "nome_emitente": res.findtext(f"{{{NS_CTE}}}xNome"),
            "ie_emitente": res.findtext(f"{{{NS_CTE}}}IE"),
            "data_emissao": res.findtext(f"{{{NS_CTE}}}dhEmi"),
            "modal": res.findtext(f"{{{NS_CTE}}}modal"),
            "valor_total": res.findtext(f"{{{NS_CTE}}}vNF"),
            "situacao": res.findtext(f"{{{NS_CTE}}}cSitCTe"),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="resumo_cte",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_evento(self, root: Element, xml: str, nsu: str) -> DocumentoExtraido:
        """Extrai dados de evento CT-e."""
        res = root if root.tag.endswith("resEvento") else root.find(f".//{{{NS_CTE}}}resEvento")

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="evento_cte",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext(f"{{{NS_CTE}}}chCTe")
        tipo_evento = res.findtext(f"{{{NS_CTE}}}tpEvento")

        dados = {
            "chave_acesso": chave,
            "tipo_evento": tipo_evento,
            "descricao_evento": res.findtext(f"{{{NS_CTE}}}xEvento"),
            "numero_sequencial": res.findtext(f"{{{NS_CTE}}}nSeqEvento"),
            "cnpj_destino": res.findtext(f"{{{NS_CTE}}}CNPJ"),
            "data_evento": res.findtext(f"{{{NS_CTE}}}dhEvento"),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=f"{chave}_{tipo_evento}_{nsu}",
            tipo="evento_cte",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_evento")),
        )

    def _extrair_uf_elemento(self, elem: Element, nome_ender: str) -> str | None:
        """Extrai UF de um elemento de endereço."""
        ender = elem.find(f"{{{NS_CTE}}}{nome_ender}")
        if ender is not None:
            return ender.findtext(f"{{{NS_CTE}}}UF")
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
        """Obtém URL do serviço CT-e para uma UF."""
        nome_servico = self.SERVICOS.get(servico, servico)

        url, usando_contingencia = await self.comutador.obter_endpoint(uf, "cte", nome_servico)

        if usando_contingencia:
            logger.warning(f"Usando contingência CT-e para {uf}")

        return url

    async def consultar_cte(self, tenant_id: UUID, chave: str) -> DocumentoExtraido | None:
        """Consulta um CT-e específico por chave de acesso."""
        cod_uf = chave[:2]
        uf = self._cod_uf_para_sigla(cod_uf)

        envelope = self._montar_envelope_consulta(chave)
        url = await self._obter_url_servico(uf, "consulta")

        resposta = await self._fazer_requisicao(tenant_id, url, data=envelope)

        if resposta:
            return self._processar_resposta_consulta(resposta, chave)

        return None

    def _montar_envelope_consulta(self, chave: str) -> str:
        """Monta envelope SOAP para consulta de CT-e."""
        ambiente = "1"

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}">
    <soap12:Body>
        <cteConsultaCT xmlns="{NS_CTE}">
            <cteDadosMsg>
                <consSitCTe xmlns="{NS_CTE}" versao="4.00">
                    <tpAmb>{ambiente}</tpAmb>
                    <xServ>CONSULTAR</xServ>
                    <chCTe>{chave}</chCTe>
                </consSitCTe>
            </cteDadosMsg>
        </cteConsultaCT>
    </soap12:Body>
</soap12:Envelope>"""

    def _processar_resposta_consulta(self, xml_resposta: str, chave: str) -> DocumentoExtraido | None:
        """Processa resposta da consulta de CT-e."""
        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(f".//{{{NS_CTE}}}retConsSitCTe")
            if ret is None:
                return None

            c_stat = ret.findtext(f"{{{NS_CTE}}}cStat")

            dados = {
                "chave_acesso": chave,
                "status_sefaz": c_stat,
                "motivo": ret.findtext(f"{{{NS_CTE}}}xMotivo"),
            }

            if c_stat in ["100", "101", "135"]:
                prot = ret.find(f"{{{NS_CTE}}}protCTe")
                if prot is not None:
                    inf_prot = prot.find(f"{{{NS_CTE}}}infProt")
                    if inf_prot is not None:
                        dados["protocolo"] = inf_prot.findtext(f"{{{NS_CTE}}}nProt")
                        dados["data_autorizacao"] = inf_prot.findtext(f"{{{NS_CTE}}}dhRecbto")

            return DocumentoExtraido(
                id=chave,
                tipo="consulta_cte",
                dados=dados,
                xml_original=xml_resposta,
            )

        except Exception as e:
            logger.error(f"Erro ao processar consulta CT-e: {e}")
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
