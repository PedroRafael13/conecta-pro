"""
Extrator de CT-e da SEFAZ.

Implementa:
- Consulta de status de CT-e
- Distribuição DFe (documentos destinados)
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
from ...core.contingency import ComutadorEndpoints, MatrizContingencia

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
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cnpjs: Optional[List[str]] = None,
        ufs: Optional[List[str]] = None,
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

        logger.info(
            f"Iniciando extração CT-e: {tenant_id} - "
            f"Período: {data_inicio.date()} a {data_fim.date()}"
        )

        try:
            # Obter credenciais
            credencial = await self.credentials.obter_credencial(
                tenant_id, self.tipo_credencial
            )

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            # Extrair para cada CNPJ
            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo CT-e para CNPJ: {cnpj}")

                # Usar distribuição DFe para obter documentos
                docs = await self._extrair_distribuicao(
                    tenant_id, cnpj, data_inicio, data_fim, incremental
                )

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
    ) -> List[DocumentoExtraido]:
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

                resposta = await self._fazer_requisicao(
                    tenant_id, url, data=envelope
                )

                if not resposta:
                    logger.warning("Sem resposta do serviço de distribuição CT-e")
                    break

                docs, ultimo_nsu, tem_mais = self._processar_resposta_distribuicao(
                    resposta
                )

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

    def _montar_envelope_distribuicao(
        self,
        cnpj: str,
        nsu: str,
        tipo_consulta: str = "distNSU"
    ) -> str:
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

    def _processar_resposta_distribuicao(
        self,
        xml_resposta: str
    ) -> tuple[List[DocumentoExtraido], str, bool]:
        """Processa resposta da distribuição DFe de CT-e."""
        documentos = []
        ultimo_nsu = "000000000000000"
        tem_mais = False

        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(".//{%s}retDistDFeInt" % NS_CTE)
            if ret is None:
                return documentos, ultimo_nsu, False

            cStat = ret.findtext("{%s}cStat" % NS_CTE)
            if cStat not in ["137", "138"]:
                logger.warning(f"Status distribuição CT-e: {cStat}")
                return documentos, ultimo_nsu, False

            ultimo_nsu = ret.findtext("{%s}ultNSU" % NS_CTE) or ultimo_nsu
            max_nsu = ret.findtext("{%s}maxNSU" % NS_CTE) or ultimo_nsu

            tem_mais = ultimo_nsu < max_nsu

            lote = ret.find("{%s}loteDistDFeInt" % NS_CTE)
            if lote is not None:
                for doc_zip in lote.findall("{%s}docZip" % NS_CTE):
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

    def _extrair_dados_documento(
        self,
        xml: str,
        schema: str,
        nsu: str
    ) -> Optional[DocumentoExtraido]:
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

    def _extrair_cte(
        self,
        root: ET.Element,
        xml: str,
        nsu: str
    ) -> DocumentoExtraido:
        """Extrai dados de CT-e completo."""
        inf_cte = root.find(".//{%s}infCte" % NS_CTE)

        if inf_cte is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="cte",
                dados={},
                xml_original=xml,
                erro="infCte não encontrado",
            )

        chave = inf_cte.get("Id", "").replace("CTe", "")

        ide = inf_cte.find("{%s}ide" % NS_CTE) or ET.Element("ide")
        emit = inf_cte.find("{%s}emit" % NS_CTE) or ET.Element("emit")
        rem = inf_cte.find("{%s}rem" % NS_CTE) or ET.Element("rem")
        dest = inf_cte.find("{%s}dest" % NS_CTE) or ET.Element("dest")
        vPrest = inf_cte.find("{%s}vPrest" % NS_CTE) or ET.Element("vPrest")

        dados = {
            "chave_acesso": chave,
            "numero": ide.findtext("{%s}nCT" % NS_CTE),
            "serie": ide.findtext("{%s}serie" % NS_CTE),
            "data_emissao": ide.findtext("{%s}dhEmi" % NS_CTE),
            "modal": ide.findtext("{%s}modal" % NS_CTE),
            "tipo_servico": ide.findtext("{%s}tpServ" % NS_CTE),
            "cfop": ide.findtext("{%s}CFOP" % NS_CTE),

            "emit_cnpj": emit.findtext("{%s}CNPJ" % NS_CTE),
            "emit_nome": emit.findtext("{%s}xNome" % NS_CTE),
            "emit_uf": self._extrair_uf_elemento(emit, "enderEmit"),

            "rem_cnpj": rem.findtext("{%s}CNPJ" % NS_CTE) or rem.findtext("{%s}CPF" % NS_CTE),
            "rem_nome": rem.findtext("{%s}xNome" % NS_CTE),

            "dest_cnpj": dest.findtext("{%s}CNPJ" % NS_CTE) or dest.findtext("{%s}CPF" % NS_CTE),
            "dest_nome": dest.findtext("{%s}xNome" % NS_CTE),

            "valor_total": vPrest.findtext("{%s}vTPrest" % NS_CTE),
            "valor_receber": vPrest.findtext("{%s}vRec" % NS_CTE),

            "nsu": nsu,
        }

        # Protocolo de autorização
        prot = root.find(".//{%s}protCTe" % NS_CTE)
        if prot is not None:
            inf_prot = prot.find("{%s}infProt" % NS_CTE)
            if inf_prot is not None:
                dados["protocolo"] = inf_prot.findtext("{%s}nProt" % NS_CTE)
                dados["status_sefaz"] = inf_prot.findtext("{%s}cStat" % NS_CTE)
                dados["data_autorizacao"] = inf_prot.findtext("{%s}dhRecbto" % NS_CTE)

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="cte",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_resumo_cte(
        self,
        root: ET.Element,
        xml: str,
        nsu: str
    ) -> DocumentoExtraido:
        """Extrai dados de resumo de CT-e."""
        res = root if root.tag.endswith("resCTe") else root.find(".//{%s}resCTe" % NS_CTE)

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="resumo_cte",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext("{%s}chCTe" % NS_CTE)

        dados = {
            "chave_acesso": chave,
            "cnpj_emitente": res.findtext("{%s}CNPJ" % NS_CTE),
            "nome_emitente": res.findtext("{%s}xNome" % NS_CTE),
            "ie_emitente": res.findtext("{%s}IE" % NS_CTE),
            "data_emissao": res.findtext("{%s}dhEmi" % NS_CTE),
            "modal": res.findtext("{%s}modal" % NS_CTE),
            "valor_total": res.findtext("{%s}vNF" % NS_CTE),
            "situacao": res.findtext("{%s}cSitCTe" % NS_CTE),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="resumo_cte",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_evento(
        self,
        root: ET.Element,
        xml: str,
        nsu: str
    ) -> DocumentoExtraido:
        """Extrai dados de evento CT-e."""
        res = root if root.tag.endswith("resEvento") else root.find(".//{%s}resEvento" % NS_CTE)

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="evento_cte",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext("{%s}chCTe" % NS_CTE)
        tipo_evento = res.findtext("{%s}tpEvento" % NS_CTE)

        dados = {
            "chave_acesso": chave,
            "tipo_evento": tipo_evento,
            "descricao_evento": res.findtext("{%s}xEvento" % NS_CTE),
            "numero_sequencial": res.findtext("{%s}nSeqEvento" % NS_CTE),
            "cnpj_destino": res.findtext("{%s}CNPJ" % NS_CTE),
            "data_evento": res.findtext("{%s}dhEvento" % NS_CTE),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=f"{chave}_{tipo_evento}_{nsu}",
            tipo="evento_cte",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_evento")),
        )

    def _extrair_uf_elemento(self, elem: ET.Element, nome_ender: str) -> Optional[str]:
        """Extrai UF de um elemento de endereço."""
        ender = elem.find("{%s}%s" % (NS_CTE, nome_ender))
        if ender is not None:
            return ender.findtext("{%s}UF" % NS_CTE)
        return None

    def _parse_data(self, data_str: Optional[str]) -> Optional[datetime]:
        """Parseia string de data para datetime."""
        if not data_str:
            return None
        try:
            return datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        except:
            try:
                return datetime.strptime(data_str[:19], "%Y-%m-%dT%H:%M:%S")
            except:
                return None

    async def _obter_url_servico(self, uf: str, servico: str) -> str:
        """Obtém URL do serviço CT-e para uma UF."""
        nome_servico = self.SERVICOS.get(servico, servico)

        url, usando_contingencia = await self.comutador.obter_endpoint(
            uf, "cte", nome_servico
        )

        if usando_contingencia:
            logger.warning(f"Usando contingência CT-e para {uf}")

        return url

    async def consultar_cte(
        self,
        tenant_id: UUID,
        chave: str
    ) -> Optional[DocumentoExtraido]:
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

    def _processar_resposta_consulta(
        self,
        xml_resposta: str,
        chave: str
    ) -> Optional[DocumentoExtraido]:
        """Processa resposta da consulta de CT-e."""
        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(".//{%s}retConsSitCTe" % NS_CTE)
            if ret is None:
                return None

            cStat = ret.findtext("{%s}cStat" % NS_CTE)

            dados = {
                "chave_acesso": chave,
                "status_sefaz": cStat,
                "motivo": ret.findtext("{%s}xMotivo" % NS_CTE),
            }

            if cStat in ["100", "101", "135"]:
                prot = ret.find("{%s}protCTe" % NS_CTE)
                if prot is not None:
                    inf_prot = prot.find("{%s}infProt" % NS_CTE)
                    if inf_prot is not None:
                        dados["protocolo"] = inf_prot.findtext("{%s}nProt" % NS_CTE)
                        dados["data_autorizacao"] = inf_prot.findtext("{%s}dhRecbto" % NS_CTE)

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
            "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA",
            "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
            "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE",
            "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
            "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
            "52": "GO", "53": "DF",
        }
        return mapeamento.get(cod, "SP")
