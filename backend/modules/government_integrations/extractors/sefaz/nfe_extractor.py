"""
Extrator de NF-e da SEFAZ.

Implementa:
- Consulta de status de NF-e
- Distribuição DFe (documentos destinados)
- Download de XML
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from uuid import UUID
import asyncio
import logging
import re
from xml.etree import ElementTree as ET

from ..base_extractor import ExtratorBase, DocumentoExtraido, ResultadoExtracao
from ...core.credentials import ProvedorCredenciais, TipoCredencial
from ...core.contingency import ComutadorEndpoints, MatrizContingencia

logger = logging.getLogger(__name__)


# Namespaces XML
NS_NFE = "http://www.portalfiscal.inf.br/nfe"
NS_SOAP = "http://www.w3.org/2003/05/soap-envelope"

NAMESPACES = {
    "nfe": NS_NFE,
    "soap": NS_SOAP,
}


class ExtratorNFe(ExtratorBase):
    """
    Extrator de NF-e da SEFAZ.

    Serviços utilizados:
    - NfeStatusServico: Verificar disponibilidade
    - NfeConsultaProtocolo: Consultar NF-e por chave
    - NFeDistribuicaoDFe: Baixar documentos destinados
    """

    SERVICOS = {
        "status": "NfeStatusServico4",
        "consulta": "NfeConsultaProtocolo4",
        "distribuicao": "NFeDistribuicaoDFe",
    }

    @property
    def tipo_servico(self) -> str:
        return "sefaz_nfe"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.SEFAZ_NFE

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
        Extrai NF-e da SEFAZ.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial
            data_fim: Data final
            cnpjs: CNPJs a consultar
            ufs: UFs para consulta (default: todas configuradas)
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
            f"Iniciando extração NF-e: {tenant_id} - "
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
                logger.info(f"Extraindo NF-e para CNPJ: {cnpj}")

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
                        # Verificar se é novo ou atualização
                        # (simplificado - em produção, verificar banco)
                        resultado.documentos_novos += 1

                    resultado.documentos_processados += 1

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração NF-e: {e}")
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
        """
        Extrai documentos via NFeDistribuicaoDFe.

        O serviço de distribuição retorna documentos destinados ao CNPJ.
        """
        documentos = []
        nsu_atual = "000000000000000"  # Começa do zero ou do último NSU

        # Em produção, buscar último NSU do banco
        if incremental:
            # TODO: Buscar último NSU processado
            pass

        max_consultas = 100  # Limite de consultas por execução
        consultas = 0

        while consultas < max_consultas:
            consultas += 1

            try:
                # Montar envelope SOAP
                envelope = self._montar_envelope_distribuicao(cnpj, nsu_atual)

                # Obter URL do serviço
                url = await self._obter_url_servico("AN", "distribuicao")

                # Headers SOAP 1.2 - action deve estar no Content-Type
                soap_action = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse"
                headers = {
                    "Content-Type": f'application/soap+xml; charset=utf-8; action="{soap_action}"'
                }

                # Fazer requisição
                resposta = await self._fazer_requisicao(
                    tenant_id, url, data=envelope, headers=headers
                )

                if not resposta:
                    logger.warning("Sem resposta do serviço de distribuição")
                    break

                # Processar resposta
                docs, ultimo_nsu, tem_mais = self._processar_resposta_distribuicao(
                    resposta
                )

                for doc in docs:
                    # Processar documento
                    doc = await self._processar_documento(doc)
                    documentos.append(doc)

                if not tem_mais or ultimo_nsu == nsu_atual:
                    break

                nsu_atual = ultimo_nsu

                # Rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Erro na consulta distribuição: {e}")
                break

        logger.info(f"Distribuição DFe: {len(documentos)} documentos extraídos")
        return documentos

    def _montar_envelope_distribuicao(
        self,
        cnpj: str,
        nsu: str,
        tipo_consulta: str = "distNSU"  # distNSU ou consNSU
    ) -> str:
        """Monta envelope SOAP para distribuição DFe."""

        # Ambiente: 1 = Produção, 2 = Homologação
        ambiente = "1"

        # UF do CNPJ (extrair dos 2 primeiros dígitos ou usar fixo)
        cod_uf = "13"  # AM - Manaus

        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}">
    <soap12:Body>
        <nfeDistDFeInteresse xmlns="{NS_NFE}">
            <nfeDadosMsg>
                <distDFeInt xmlns="{NS_NFE}" versao="1.01">
                    <tpAmb>{ambiente}</tpAmb>
                    <cUFAutor>{cod_uf}</cUFAutor>
                    <CNPJ>{cnpj}</CNPJ>
                    <{tipo_consulta}>
                        <NSU>{nsu}</NSU>
                    </{tipo_consulta}>
                </distDFeInt>
            </nfeDadosMsg>
        </nfeDistDFeInteresse>
    </soap12:Body>
</soap12:Envelope>"""

        return envelope

    def _processar_resposta_distribuicao(
        self,
        xml_resposta: str
    ) -> tuple[List[DocumentoExtraido], str, bool]:
        """
        Processa resposta da distribuição DFe.

        Returns:
            Tupla (documentos, ultimo_nsu, tem_mais)
        """
        documentos = []
        ultimo_nsu = "000000000000000"
        tem_mais = False

        try:
            root = ET.fromstring(xml_resposta.encode())

            # Buscar retorno
            ret = root.find(".//{%s}retDistDFeInt" % NS_NFE)
            if ret is None:
                return documentos, ultimo_nsu, False

            # Verificar status
            cStat = ret.findtext("{%s}cStat" % NS_NFE)
            if cStat not in ["137", "138"]:  # 137 = docs encontrados, 138 = fim
                logger.warning(f"Status distribuição: {cStat}")
                return documentos, ultimo_nsu, False

            # Obter último NSU
            ultimo_nsu = ret.findtext("{%s}ultNSU" % NS_NFE) or ultimo_nsu
            max_nsu = ret.findtext("{%s}maxNSU" % NS_NFE) or ultimo_nsu

            tem_mais = ultimo_nsu < max_nsu

            # Processar documentos
            lote = ret.find("{%s}loteDistDFeInt" % NS_NFE)
            if lote is not None:
                for doc_zip in lote.findall("{%s}docZip" % NS_NFE):
                    nsu = doc_zip.get("NSU")
                    schema = doc_zip.get("schema", "")

                    # Decodificar conteúdo (base64 + gzip)
                    import base64
                    import gzip

                    conteudo_b64 = doc_zip.text
                    if conteudo_b64:
                        try:
                            conteudo_gzip = base64.b64decode(conteudo_b64)
                            xml_doc = gzip.decompress(conteudo_gzip).decode("utf-8")

                            # Extrair dados do documento
                            doc = self._extrair_dados_documento(xml_doc, schema, nsu)
                            if doc:
                                documentos.append(doc)

                        except Exception as e:
                            logger.error(f"Erro ao decodificar documento NSU {nsu}: {e}")

        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML de resposta: {e}")

        return documentos, ultimo_nsu, tem_mais

    def _extrair_dados_documento(
        self,
        xml: str,
        schema: str,
        nsu: str
    ) -> Optional[DocumentoExtraido]:
        """Extrai dados de um documento XML."""
        try:
            root = ET.fromstring(xml.encode())

            # Determinar tipo de documento
            if "procNFe" in schema or root.tag.endswith("nfeProc"):
                return self._extrair_nfe(root, xml, nsu)
            elif "resNFe" in schema:
                return self._extrair_resumo_nfe(root, xml, nsu)
            elif "resEvento" in schema:
                return self._extrair_evento(root, xml, nsu)
            else:
                logger.debug(f"Schema não reconhecido: {schema}")
                return None

        except Exception as e:
            logger.error(f"Erro ao extrair dados do documento: {e}")
            return None

    def _extrair_nfe(
        self,
        root: ET.Element,
        xml: str,
        nsu: str
    ) -> DocumentoExtraido:
        """Extrai dados de NF-e completa."""
        # Buscar infNFe
        inf_nfe = root.find(".//{%s}infNFe" % NS_NFE)

        if inf_nfe is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="nfe",
                dados={},
                xml_original=xml,
                erro="infNFe não encontrado",
            )

        # Extrair chave de acesso do Id
        chave = inf_nfe.get("Id", "").replace("NFe", "")

        # Extrair campos principais
        ide = inf_nfe.find("{%s}ide" % NS_NFE) or ET.Element("ide")
        emit = inf_nfe.find("{%s}emit" % NS_NFE) or ET.Element("emit")
        dest = inf_nfe.find("{%s}dest" % NS_NFE) or ET.Element("dest")
        total = inf_nfe.find("{%s}total" % NS_NFE) or ET.Element("total")
        icms_tot = total.find("{%s}ICMSTot" % NS_NFE) or ET.Element("ICMSTot")

        dados = {
            "chave_acesso": chave,
            "numero": ide.findtext("{%s}nNF" % NS_NFE),
            "serie": ide.findtext("{%s}serie" % NS_NFE),
            "data_emissao": ide.findtext("{%s}dhEmi" % NS_NFE),
            "natureza_operacao": ide.findtext("{%s}natOp" % NS_NFE),
            "tipo_operacao": ide.findtext("{%s}tpNF" % NS_NFE),

            "emit_cnpj": emit.findtext("{%s}CNPJ" % NS_NFE),
            "emit_nome": emit.findtext("{%s}xNome" % NS_NFE),
            "emit_uf": self._extrair_uf_emitente(emit),

            "dest_cnpj": dest.findtext("{%s}CNPJ" % NS_NFE) or dest.findtext("{%s}CPF" % NS_NFE),
            "dest_nome": dest.findtext("{%s}xNome" % NS_NFE),

            "valor_produtos": icms_tot.findtext("{%s}vProd" % NS_NFE),
            "valor_total": icms_tot.findtext("{%s}vNF" % NS_NFE),
            "valor_icms": icms_tot.findtext("{%s}vICMS" % NS_NFE),

            "nsu": nsu,
        }

        # Buscar protocolo de autorização
        prot = root.find(".//{%s}protNFe" % NS_NFE)
        if prot is not None:
            inf_prot = prot.find("{%s}infProt" % NS_NFE)
            if inf_prot is not None:
                dados["protocolo"] = inf_prot.findtext("{%s}nProt" % NS_NFE)
                dados["status_sefaz"] = inf_prot.findtext("{%s}cStat" % NS_NFE)
                dados["data_autorizacao"] = inf_prot.findtext("{%s}dhRecbto" % NS_NFE)

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="nfe",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_emissao")),
        )

    def _extrair_resumo_nfe(
        self,
        root: ET.Element,
        xml: str,
        nsu: str
    ) -> DocumentoExtraido:
        """Extrai dados de resumo de NF-e."""
        res = root if root.tag.endswith("resNFe") else root.find(".//{%s}resNFe" % NS_NFE)

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="resumo_nfe",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext("{%s}chNFe" % NS_NFE)

        dados = {
            "chave_acesso": chave,
            "cnpj_emitente": res.findtext("{%s}CNPJ" % NS_NFE),
            "nome_emitente": res.findtext("{%s}xNome" % NS_NFE),
            "ie_emitente": res.findtext("{%s}IE" % NS_NFE),
            "data_emissao": res.findtext("{%s}dhEmi" % NS_NFE),
            "tipo_operacao": res.findtext("{%s}tpNF" % NS_NFE),
            "valor_total": res.findtext("{%s}vNF" % NS_NFE),
            "situacao": res.findtext("{%s}cSitNFe" % NS_NFE),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=chave or nsu,
            tipo="resumo_nfe",
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
        """Extrai dados de evento (cancelamento, carta correção, etc)."""
        res = root if root.tag.endswith("resEvento") else root.find(".//{%s}resEvento" % NS_NFE)

        if res is None:
            return DocumentoExtraido(
                id=nsu,
                tipo="evento_nfe",
                dados={},
                xml_original=xml,
            )

        chave = res.findtext("{%s}chNFe" % NS_NFE)
        tipo_evento = res.findtext("{%s}tpEvento" % NS_NFE)

        dados = {
            "chave_acesso": chave,
            "tipo_evento": tipo_evento,
            "descricao_evento": res.findtext("{%s}xEvento" % NS_NFE),
            "numero_sequencial": res.findtext("{%s}nSeqEvento" % NS_NFE),
            "cnpj_destino": res.findtext("{%s}CNPJ" % NS_NFE),
            "data_evento": res.findtext("{%s}dhEvento" % NS_NFE),
            "nsu": nsu,
        }

        return DocumentoExtraido(
            id=f"{chave}_{tipo_evento}_{nsu}",
            tipo="evento_nfe",
            dados=dados,
            xml_original=xml,
            data_documento=self._parse_data(dados.get("data_evento")),
        )

    def _extrair_uf_emitente(self, emit: ET.Element) -> Optional[str]:
        """Extrai UF do emitente."""
        ender = emit.find("{%s}enderEmit" % NS_NFE)
        if ender is not None:
            return ender.findtext("{%s}UF" % NS_NFE)
        return None

    def _parse_data(self, data_str: Optional[str]) -> Optional[datetime]:
        """Parseia string de data para datetime."""
        if not data_str:
            return None
        try:
            # Formato ISO com timezone
            return datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        except:
            try:
                # Formato sem timezone
                return datetime.strptime(data_str[:19], "%Y-%m-%dT%H:%M:%S")
            except:
                return None

    async def _obter_url_servico(self, uf: str, servico: str) -> str:
        """Obtém URL do serviço para uma UF."""
        nome_servico = self.SERVICOS.get(servico, servico)

        # Serviços do Ambiente Nacional (AN) - centralizados
        # Distribuição DFe é sempre no AN, não usa comutador por UF
        if uf.upper() == "AN":
            url = MatrizContingencia.resolver_url("AN", nome_servico)
            logger.debug(f"Usando endpoint AN para {nome_servico}: {url}")
            return url

        # Usar comutador para obter endpoint (com fallback para contingência)
        url, usando_contingencia = await self.comutador.obter_endpoint(
            uf, "nfe", nome_servico
        )

        if usando_contingencia:
            logger.warning(f"Usando contingência para {uf}")

        return url

    async def consultar_nfe(
        self,
        tenant_id: UUID,
        chave: str
    ) -> Optional[DocumentoExtraido]:
        """
        Consulta uma NF-e específica por chave de acesso.

        Args:
            tenant_id: ID do tenant
            chave: Chave de acesso (44 dígitos)

        Returns:
            Documento extraído ou None
        """
        # Extrair UF da chave (posições 0-1)
        cod_uf = chave[:2]
        uf = self._cod_uf_para_sigla(cod_uf)

        # Montar envelope
        envelope = self._montar_envelope_consulta(chave)

        # Obter URL
        url = await self._obter_url_servico(uf, "consulta")

        # Fazer requisição
        resposta = await self._fazer_requisicao(tenant_id, url, data=envelope)

        if resposta:
            return self._processar_resposta_consulta(resposta, chave)

        return None

    def _montar_envelope_consulta(self, chave: str) -> str:
        """Monta envelope SOAP para consulta de NF-e."""
        ambiente = "1"  # Produção

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:soap12="{NS_SOAP}">
    <soap12:Body>
        <nfeConsultaNF xmlns="{NS_NFE}">
            <nfeDadosMsg>
                <consSitNFe xmlns="{NS_NFE}" versao="4.00">
                    <tpAmb>{ambiente}</tpAmb>
                    <xServ>CONSULTAR</xServ>
                    <chNFe>{chave}</chNFe>
                </consSitNFe>
            </nfeDadosMsg>
        </nfeConsultaNF>
    </soap12:Body>
</soap12:Envelope>"""

    def _processar_resposta_consulta(
        self,
        xml_resposta: str,
        chave: str
    ) -> Optional[DocumentoExtraido]:
        """Processa resposta da consulta de NF-e."""
        try:
            root = ET.fromstring(xml_resposta.encode())

            ret = root.find(".//{%s}retConsSitNFe" % NS_NFE)
            if ret is None:
                return None

            cStat = ret.findtext("{%s}cStat" % NS_NFE)

            dados = {
                "chave_acesso": chave,
                "status_sefaz": cStat,
                "motivo": ret.findtext("{%s}xMotivo" % NS_NFE),
            }

            # Se autorizada (100) ou cancelada (101, 135)
            if cStat in ["100", "101", "135"]:
                prot = ret.find("{%s}protNFe" % NS_NFE)
                if prot is not None:
                    inf_prot = prot.find("{%s}infProt" % NS_NFE)
                    if inf_prot is not None:
                        dados["protocolo"] = inf_prot.findtext("{%s}nProt" % NS_NFE)
                        dados["data_autorizacao"] = inf_prot.findtext("{%s}dhRecbto" % NS_NFE)

            return DocumentoExtraido(
                id=chave,
                tipo="consulta_nfe",
                dados=dados,
                xml_original=xml_resposta,
            )

        except Exception as e:
            logger.error(f"Erro ao processar consulta: {e}")
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
