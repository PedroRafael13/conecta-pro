"""
Sincronizador de MDF-e (Manifesto Eletronico de Documentos Fiscais).

Extrai e sincroniza:
- MDF-e emitidos
- Documentos vinculados
- Eventos (encerramento, cancelamento)
- Condutores
"""

import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from decimal import Decimal
from typing import Any

import defusedxml.ElementTree as ET  # noqa: N817

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class MDFeSynchronizer(BaseSynchronizer):
    """Sincronizador de MDF-e da SEFAZ."""

    SERVICO_NOME = "sefaz_mdfe"
    INTERVALO_PADRAO = 60  # 1 hora
    DIAS_RETROATIVOS_PADRAO = 30

    # Tipos de emitente
    TIPOS_EMITENTE = {
        "1": "Prestador de Servico de Transporte",
        "2": "Transportador de Carga Propria",
        "3": "Prestador de Servico de Transporte - CT-e Globalizado",
    }

    # Tipos de transporte
    TIPOS_TRANSPORTE = {
        "1": "ETC",
        "2": "TAC",
        "3": "CTC",
    }

    # Namespace XML
    NS_MDFE = {"mdfe": "http://www.portalfiscal.inf.br/mdfe"}

    def __init__(self, db_session, certificate_manager=None, sefaz_manager=None):
        super().__init__(db_session, certificate_manager)
        self.sefaz_manager = sefaz_manager

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai MDF-e do webservice SEFAZ.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados de cada MDF-e
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(f"[MDF-e] Extraindo dados - CNPJ: {cnpj}, Periodo: {config.data_inicial} a {config.data_final}")

        # 1. MDF-e emitidos
        async for mdfe in self._consultar_mdfe_emitidos(cnpj, config):
            yield mdfe

        # 2. Eventos
        async for evento in self._consultar_eventos(cnpj, config):
            yield evento

    async def _consultar_mdfe_emitidos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta MDF-e emitidos."""
        try:
            if not self.sefaz_manager:
                logger.warning("[MDF-e] SEFAZ Manager nao configurado")
                return

            mdfes = await self._request_com_retry(
                self.sefaz_manager.consultar_mdfe_emitidos,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for mdfe in mdfes or []:
                xml = await self._baixar_xml(mdfe.get("chave"))
                dados = self._parse_mdfe_xml(xml) if xml else {}

                dados.update(
                    {
                        "tipo": "mdfe",
                        "chave_acesso": mdfe.get("chave"),
                        "xml_original": xml,
                    }
                )

                yield dados

        except Exception as e:
            logger.error(f"[MDF-e] Erro consultando MDF-e emitidos: {e}")
            raise

    async def _consultar_eventos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta eventos dos MDF-e."""
        try:
            if not self.sefaz_manager:
                return

            mdfes_locais = await self._buscar_mdfes_para_atualizar(cnpj, config)

            for mdfe in mdfes_locais:
                chave = mdfe.get("chave_acesso")
                if not chave:
                    continue

                eventos = await self._request_com_retry(
                    self.sefaz_manager.consultar_eventos_mdfe,
                    chave=chave,
                )

                for evento in eventos or []:
                    yield {
                        "tipo": "evento_mdfe",
                        "chave_acesso": chave,
                        "tipo_evento": evento.get("tipo"),
                        "sequencia": evento.get("sequencia"),
                        "data_evento": self._parse_data(evento.get("data")),
                        "protocolo": evento.get("protocolo"),
                        "descricao": evento.get("descricao"),
                        "uf_encerramento": evento.get("uf_encerramento"),
                        "municipio_encerramento": evento.get("municipio_encerramento"),
                        "xml_evento": evento.get("xml"),
                    }

        except Exception as e:
            logger.error(f"[MDF-e] Erro consultando eventos: {e}")

    async def _baixar_xml(self, chave: str) -> bytes | None:
        """Baixa XML completo do MDF-e."""
        try:
            if not self.sefaz_manager or not chave:
                return None

            xml = await self._request_com_retry(
                self.sefaz_manager.baixar_xml_mdfe,
                chave=chave,
            )
            return xml

        except Exception as e:
            logger.warning(f"[MDF-e] Erro baixando XML {chave}: {e}")
            return None

    async def _buscar_mdfes_para_atualizar(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> list[dict]:
        """Busca MDF-e no banco para consultar eventos."""
        return []

    def _parse_mdfe_xml(self, xml: bytes) -> dict[str, Any]:
        """Extrai dados do XML do MDF-e."""
        if not xml:
            return {}

        try:
            root = ET.fromstring(xml)

            inf_mdfe = root.find(".//mdfe:infMDFe", self.NS_MDFE)
            if inf_mdfe is None:
                inf_mdfe = root.find(".//infMDFe")

            if inf_mdfe is None:
                return {}

            ide = inf_mdfe.find("mdfe:ide", self.NS_MDFE) or inf_mdfe.find("ide")
            emit = inf_mdfe.find("mdfe:emit", self.NS_MDFE) or inf_mdfe.find("emit")
            inf_doc = inf_mdfe.find("mdfe:infDoc", self.NS_MDFE) or inf_mdfe.find("infDoc")
            tot = inf_mdfe.find("mdfe:tot", self.NS_MDFE) or inf_mdfe.find("tot")

            dados = {
                "numero": self._get_text(ide, "nMDF"),
                "serie": self._get_text(ide, "serie"),
                "data_emissao": self._parse_data(self._get_text(ide, "dhEmi")),
                "tipo_emitente": self._get_text(ide, "tpEmit"),
                "descricao_tipo_emitente": self.TIPOS_EMITENTE.get(self._get_text(ide, "tpEmit"), "Transportador"),
                "modal": self._get_text(ide, "modal"),
                "uf_inicio": self._get_text(ide, "UFIni"),
                "uf_fim": self._get_text(ide, "UFFim"),
            }

            if emit:
                dados.update(
                    {
                        "cnpj_emitente": self._get_text(emit, "CNPJ"),
                        "razao_social_emitente": self._get_text(emit, "xNome"),
                        "ie_emitente": self._get_text(emit, "IE"),
                        "uf_emitente": self._get_text(emit, "enderEmit/UF"),
                    }
                )

            if tot:
                dados.update(
                    {
                        "qtd_cte": int(self._get_text(tot, "qCTe") or 0),
                        "qtd_nfe": int(self._get_text(tot, "qNFe") or 0),
                        "qtd_mdfe": int(self._get_text(tot, "qMDFe") or 0),
                        "valor_carga": self._parse_decimal(self._get_text(tot, "vCarga")),
                        "peso_bruto": self._parse_decimal(self._get_text(tot, "qCarga")),
                        "unidade": self._get_text(tot, "cUnid"),
                    }
                )

            # Documentos vinculados
            docs = []
            if inf_doc:
                for inf_mun_descarga in inf_doc.findall("mdfe:infMunDescarga", self.NS_MDFE) or inf_doc.findall(
                    "infMunDescarga"
                ):
                    municipio = self._get_text(inf_mun_descarga, "xMunDescarga")
                    self._get_text(inf_mun_descarga, "cMunDescarga")[:2] if self._get_text(
                        inf_mun_descarga, "cMunDescarga"
                    ) else None

                    for inf_cte in inf_mun_descarga.findall("mdfe:infCTe", self.NS_MDFE) or inf_mun_descarga.findall(
                        "infCTe"
                    ):
                        docs.append(
                            {
                                "tipo": "CTe",
                                "chave": self._get_text(inf_cte, "chCTe"),
                                "municipio_descarga": municipio,
                            }
                        )

                    for inf_nfe in inf_mun_descarga.findall("mdfe:infNFe", self.NS_MDFE) or inf_mun_descarga.findall(
                        "infNFe"
                    ):
                        docs.append(
                            {
                                "tipo": "NFe",
                                "chave": self._get_text(inf_nfe, "chNFe"),
                                "municipio_descarga": municipio,
                            }
                        )

            dados["documentos_vinculados"] = docs

            # Condutores
            condutores = []
            for condutor in inf_mdfe.findall(".//mdfe:condutor", self.NS_MDFE) or inf_mdfe.findall(".//condutor"):
                condutores.append(
                    {
                        "cpf": self._get_text(condutor, "CPF"),
                        "nome": self._get_text(condutor, "xNome"),
                    }
                )
            dados["condutores"] = condutores

            # Veiculos
            veiculos = []
            for veiculo in inf_mdfe.findall(".//mdfe:veicTracao", self.NS_MDFE) or inf_mdfe.findall(".//veicTracao"):
                veiculos.append(
                    {
                        "placa": self._get_text(veiculo, "placa"),
                        "renavam": self._get_text(veiculo, "RENAVAM"),
                        "uf": self._get_text(veiculo, "UF"),
                        "tipo": "tracao",
                    }
                )

            for veiculo in inf_mdfe.findall(".//mdfe:veicReboque", self.NS_MDFE) or inf_mdfe.findall(".//veicReboque"):
                veiculos.append(
                    {
                        "placa": self._get_text(veiculo, "placa"),
                        "renavam": self._get_text(veiculo, "RENAVAM"),
                        "uf": self._get_text(veiculo, "UF"),
                        "tipo": "reboque",
                    }
                )

            dados["veiculos"] = veiculos

            return dados

        except Exception as e:
            logger.error(f"[MDF-e] Erro parseando XML: {e}")
            return {}

    def _get_text(self, element, path: str) -> str | None:
        """Obtem texto de elemento XML."""
        if element is None:
            return None

        el = element.find(f"mdfe:{path}", self.NS_MDFE)
        if el is None:
            el = element.find(path)

        return el.text if el is not None else None

    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "mdfe":
            return await self._salvar_mdfe(registro, config)
        elif tipo == "evento_mdfe":
            return await self._salvar_evento(registro)

        return False

    async def _salvar_mdfe(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva ou atualiza MDF-e no banco."""
        from ..models.sync_models import DocumentoFiscal, StatusDocumentoFiscal, TipoDocumentoFiscal

        chave = registro.get("chave_acesso")
        if not chave:
            return False

        existente = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.chave_acesso == chave).first()

        if existente:
            existente.xml_original = registro.get("xml_original") or existente.xml_original
            existente.updated_at = datetime.utcnow()
            return False

        novo = DocumentoFiscal(
            tipo=TipoDocumentoFiscal.MDFE,
            chave_acesso=chave,
            numero=registro.get("numero") or 0,
            serie=registro.get("serie") or 1,
            cnpj_empresa=config.cnpj_empresa,
            direcao="emitido",
            cnpj_emitente=registro.get("cnpj_emitente"),
            razao_social_emitente=registro.get("razao_social_emitente"),
            uf_emitente=registro.get("uf_emitente"),
            data_emissao=registro.get("data_emissao") or datetime.utcnow(),
            valor_total=Decimal(str(registro.get("valor_carga") or 0)),
            status=StatusDocumentoFiscal.AUTORIZADO,
            xml_original=registro.get("xml_original"),
            dados_adicionais={
                "tipo_emitente": registro.get("tipo_emitente"),
                "modal": registro.get("modal"),
                "uf_inicio": registro.get("uf_inicio"),
                "uf_fim": registro.get("uf_fim"),
                "qtd_cte": registro.get("qtd_cte"),
                "qtd_nfe": registro.get("qtd_nfe"),
                "peso_bruto": str(registro.get("peso_bruto") or 0),
                "documentos_vinculados": registro.get("documentos_vinculados"),
                "condutores": registro.get("condutores"),
                "veiculos": registro.get("veiculos"),
            },
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_evento(self, registro: dict[str, Any]) -> bool:
        """Salva evento de MDF-e."""
        from ..models.sync_models import DocumentoFiscal, EventoDocumentoFiscal, StatusDocumentoFiscal

        chave = registro.get("chave_acesso")
        if not chave:
            return False

        mdfe = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.chave_acesso == chave).first()

        if not mdfe:
            return False

        existente = (
            self.db.query(EventoDocumentoFiscal)
            .filter(
                EventoDocumentoFiscal.documento_id == mdfe.id,
                EventoDocumentoFiscal.tipo_evento == registro.get("tipo_evento"),
                EventoDocumentoFiscal.sequencia == registro.get("sequencia", 1),
            )
            .first()
        )

        if existente:
            return False

        evento = EventoDocumentoFiscal(
            documento_id=mdfe.id,
            tipo_evento=registro.get("tipo_evento"),
            sequencia=registro.get("sequencia", 1),
            data_evento=registro.get("data_evento") or datetime.utcnow(),
            protocolo=registro.get("protocolo"),
            descricao=registro.get("descricao"),
            xml_evento=registro.get("xml_evento"),
            dados_adicionais={
                "uf_encerramento": registro.get("uf_encerramento"),
                "municipio_encerramento": registro.get("municipio_encerramento"),
            },
        )
        self.db.add(evento)

        # Atualizar status
        if registro.get("tipo_evento") == "110111":  # Cancelamento
            mdfe.status = StatusDocumentoFiscal.CANCELADO
            mdfe.data_cancelamento = registro.get("data_evento")
        elif registro.get("tipo_evento") == "110112":  # Encerramento
            mdfe.status = StatusDocumentoFiscal.ENCERRADO

        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtem ultima sincronizacao de MDF-e."""
        from ..models.sync_models import StatusSincronizacao, SyncLog

        ultimo = (
            self.db.query(SyncLog)
            .filter(
                SyncLog.cnpj_empresa == cnpj,
                SyncLog.servico == self.SERVICO_NOME,
                SyncLog.status == StatusSincronizacao.SUCESSO,
            )
            .order_by(SyncLog.fim_execucao.desc())
            .first()
        )

        return ultimo.fim_execucao if ultimo else None

    async def obter_resumo(self, cnpj: str) -> dict[str, Any]:
        """Obtem resumo dos MDF-e sincronizados."""
        from sqlalchemy import func

        from ..models.sync_models import DocumentoFiscal, StatusDocumentoFiscal, TipoDocumentoFiscal

        totais = (
            self.db.query(
                func.count(DocumentoFiscal.id),
            )
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo == TipoDocumentoFiscal.MDFE,
            )
            .first()
        )

        abertos = (
            self.db.query(
                func.count(DocumentoFiscal.id),
            )
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo == TipoDocumentoFiscal.MDFE,
                DocumentoFiscal.status == StatusDocumentoFiscal.AUTORIZADO,
            )
            .first()
        )

        return {
            "total_mdfes": totais[0] or 0,
            "mdfes_abertos": abertos[0] or 0,
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
