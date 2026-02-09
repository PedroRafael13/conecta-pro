"""
Sincronizador de CT-e (Conhecimento de Transporte Eletronico).

Extrai e sincroniza:
- CT-e emitidos
- CT-e recebidos
- Eventos (cancelamento, carta correcao)
- MDF-e relacionados
"""

import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from decimal import Decimal
from typing import Any

import defusedxml.ElementTree as ET  # noqa: N817

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class CTeSynchronizer(BaseSynchronizer):
    """Sincronizador de CT-e da SEFAZ."""

    SERVICO_NOME = "sefaz_cte"
    INTERVALO_PADRAO = 60  # 1 hora
    DIAS_RETROATIVOS_PADRAO = 30

    # Tipos de CT-e
    TIPOS_CTE = {
        "0": "CT-e Normal",
        "1": "CT-e de Complemento",
        "2": "CT-e de Anulacao",
        "3": "CT-e Substituto",
    }

    # Modais
    MODAIS = {
        "01": "Rodoviario",
        "02": "Aereo",
        "03": "Aquaviario",
        "04": "Ferroviario",
        "05": "Dutoviario",
        "06": "Multimodal",
    }

    # Namespace XML
    NS_CTE = {"cte": "http://www.portalfiscal.inf.br/cte"}

    def __init__(self, db_session, certificate_manager=None, sefaz_manager=None):
        super().__init__(db_session, certificate_manager)
        self.sefaz_manager = sefaz_manager

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai CT-e do webservice SEFAZ.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados de cada CT-e
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(f"[CT-e] Extraindo dados - CNPJ: {cnpj}, Periodo: {config.data_inicial} a {config.data_final}")

        # 1. CT-e emitidos
        async for cte in self._consultar_cte_emitidos(cnpj, config):
            yield cte

        # 2. CT-e recebidos (tomador)
        async for cte in self._consultar_cte_tomados(cnpj, config):
            yield cte

        # 3. Eventos
        async for evento in self._consultar_eventos(cnpj, config):
            yield evento

    async def _consultar_cte_emitidos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta CT-e emitidos pela transportadora."""
        try:
            if not self.sefaz_manager:
                logger.warning("[CT-e] SEFAZ Manager nao configurado")
                return

            ctes = await self._request_com_retry(
                self.sefaz_manager.consultar_cte_emitidos,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for cte in ctes or []:
                xml = await self._baixar_xml(cte.get("chave"))
                dados = self._parse_cte_xml(xml) if xml else {}

                dados.update(
                    {
                        "tipo": "cte_emitido",
                        "chave_acesso": cte.get("chave"),
                        "direcao": "emitido",
                        "xml_original": xml,
                    }
                )

                yield dados

        except Exception as e:
            logger.error(f"[CT-e] Erro consultando CT-e emitidos: {e}")
            raise

    async def _consultar_cte_tomados(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta CT-e onde a empresa e tomadora."""
        try:
            if not self.sefaz_manager:
                return

            ctes = await self._request_com_retry(
                self.sefaz_manager.consultar_cte_tomados,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for cte in ctes or []:
                xml = await self._baixar_xml(cte.get("chave"))
                dados = (
                    self._parse_cte_xml(xml)
                    if xml
                    else {
                        "numero": cte.get("numero"),
                        "data_emissao": self._parse_data(cte.get("data_emissao")),
                        "valor_total": self._parse_decimal(cte.get("valor")),
                        "cnpj_emitente": cte.get("cnpj_emitente"),
                    }
                )

                dados.update(
                    {
                        "tipo": "cte_tomado",
                        "chave_acesso": cte.get("chave"),
                        "direcao": "tomado",
                        "xml_original": xml,
                    }
                )

                yield dados

        except Exception as e:
            logger.error(f"[CT-e] Erro consultando CT-e tomados: {e}")

    async def _consultar_eventos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta eventos dos CT-e."""
        try:
            if not self.sefaz_manager:
                return

            ctes_locais = await self._buscar_ctes_para_atualizar(cnpj, config)

            for cte in ctes_locais:
                chave = cte.get("chave_acesso")
                if not chave:
                    continue

                eventos = await self._request_com_retry(
                    self.sefaz_manager.consultar_eventos_cte,
                    chave=chave,
                )

                for evento in eventos or []:
                    yield {
                        "tipo": "evento_cte",
                        "chave_acesso": chave,
                        "tipo_evento": evento.get("tipo"),
                        "sequencia": evento.get("sequencia"),
                        "data_evento": self._parse_data(evento.get("data")),
                        "protocolo": evento.get("protocolo"),
                        "descricao": evento.get("descricao"),
                        "xml_evento": evento.get("xml"),
                    }

        except Exception as e:
            logger.error(f"[CT-e] Erro consultando eventos: {e}")

    async def _baixar_xml(self, chave: str) -> bytes | None:
        """Baixa XML completo do CT-e."""
        try:
            if not self.sefaz_manager or not chave:
                return None

            xml = await self._request_com_retry(
                self.sefaz_manager.baixar_xml_cte,
                chave=chave,
            )
            return xml

        except Exception as e:
            logger.warning(f"[CT-e] Erro baixando XML {chave}: {e}")
            return None

    async def _buscar_ctes_para_atualizar(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> list[dict]:
        """Busca CT-e no banco para consultar eventos."""
        return []

    def _parse_cte_xml(self, xml: bytes) -> dict[str, Any]:
        """Extrai dados do XML do CT-e."""
        if not xml:
            return {}

        try:
            root = ET.fromstring(xml)

            inf_cte = root.find(".//cte:infCte", self.NS_CTE)
            if inf_cte is None:
                inf_cte = root.find(".//infCte")

            if inf_cte is None:
                return {}

            ide = inf_cte.find("cte:ide", self.NS_CTE) or inf_cte.find("ide")
            emit = inf_cte.find("cte:emit", self.NS_CTE) or inf_cte.find("emit")
            rem = inf_cte.find("cte:rem", self.NS_CTE) or inf_cte.find("rem")
            dest = inf_cte.find("cte:dest", self.NS_CTE) or inf_cte.find("dest")
            v_prest = inf_cte.find("cte:vPrest", self.NS_CTE) or inf_cte.find("vPrest")
            inf_carga = inf_cte.find("cte:infCarga", self.NS_CTE) or inf_cte.find("infCarga")

            dados = {
                "numero": self._get_text(ide, "nCT"),
                "serie": self._get_text(ide, "serie"),
                "data_emissao": self._parse_data(self._get_text(ide, "dhEmi")),
                "tipo_cte": self._get_text(ide, "tpCTe"),
                "descricao_tipo": self.TIPOS_CTE.get(self._get_text(ide, "tpCTe"), "Normal"),
                "modal": self._get_text(ide, "modal"),
                "descricao_modal": self.MODAIS.get(self._get_text(ide, "modal"), "Rodoviario"),
                "cfop": self._get_text(ide, "CFOP"),
                "uf_inicio": self._get_text(ide, "UFIni"),
                "municipio_inicio": self._get_text(ide, "xMunIni"),
                "uf_fim": self._get_text(ide, "UFFim"),
                "municipio_fim": self._get_text(ide, "xMunFim"),
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

            if rem:
                dados.update(
                    {
                        "cnpj_remetente": self._get_text(rem, "CNPJ") or self._get_text(rem, "CPF"),
                        "razao_social_remetente": self._get_text(rem, "xNome"),
                    }
                )

            if dest:
                dados.update(
                    {
                        "cnpj_destinatario": self._get_text(dest, "CNPJ") or self._get_text(dest, "CPF"),
                        "razao_social_destinatario": self._get_text(dest, "xNome"),
                    }
                )

            if v_prest:
                dados.update(
                    {
                        "valor_total": self._parse_decimal(self._get_text(v_prest, "vTPrest")),
                        "valor_receber": self._parse_decimal(self._get_text(v_prest, "vRec")),
                    }
                )

            if inf_carga:
                dados.update(
                    {
                        "valor_carga": self._parse_decimal(self._get_text(inf_carga, "vCarga")),
                        "produto_predominante": self._get_text(inf_carga, "proPred"),
                    }
                )

            # NF-e vinculadas
            nfes = []
            for inf_nfe in inf_cte.findall(".//cte:infNFe", self.NS_CTE) or inf_cte.findall(".//infNFe"):
                nfes.append(
                    {
                        "chave": self._get_text(inf_nfe, "chave"),
                    }
                )
            dados["nfes_vinculadas"] = nfes

            return dados

        except Exception as e:
            logger.error(f"[CT-e] Erro parseando XML: {e}")
            return {}

    def _get_text(self, element, path: str) -> str | None:
        """Obtem texto de elemento XML."""
        if element is None:
            return None

        el = element.find(f"cte:{path}", self.NS_CTE)
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

        if tipo in ("cte_emitido", "cte_tomado"):
            return await self._salvar_cte(registro, config)
        elif tipo == "evento_cte":
            return await self._salvar_evento(registro)

        return False

    async def _salvar_cte(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva ou atualiza CT-e no banco."""
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
            tipo=TipoDocumentoFiscal.CTE,
            chave_acesso=chave,
            numero=registro.get("numero") or 0,
            serie=registro.get("serie") or 1,
            cnpj_empresa=config.cnpj_empresa,
            direcao=registro.get("direcao"),
            cnpj_emitente=registro.get("cnpj_emitente"),
            razao_social_emitente=registro.get("razao_social_emitente"),
            uf_emitente=registro.get("uf_emitente"),
            cnpj_cpf_destinatario=registro.get("cnpj_destinatario"),
            razao_social_destinatario=registro.get("razao_social_destinatario"),
            data_emissao=registro.get("data_emissao") or datetime.utcnow(),
            valor_total=Decimal(str(registro.get("valor_total") or 0)),
            status=StatusDocumentoFiscal.AUTORIZADO,
            xml_original=registro.get("xml_original"),
            dados_adicionais={
                "tipo_cte": registro.get("tipo_cte"),
                "modal": registro.get("modal"),
                "cfop": registro.get("cfop"),
                "uf_inicio": registro.get("uf_inicio"),
                "uf_fim": registro.get("uf_fim"),
                "municipio_inicio": registro.get("municipio_inicio"),
                "municipio_fim": registro.get("municipio_fim"),
                "cnpj_remetente": registro.get("cnpj_remetente"),
                "cnpj_destinatario": registro.get("cnpj_destinatario"),
                "valor_carga": str(registro.get("valor_carga") or 0),
                "nfes_vinculadas": registro.get("nfes_vinculadas"),
            },
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_evento(self, registro: dict[str, Any]) -> bool:
        """Salva evento de CT-e."""
        from ..models.sync_models import DocumentoFiscal, EventoDocumentoFiscal, StatusDocumentoFiscal

        chave = registro.get("chave_acesso")
        if not chave:
            return False

        cte = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.chave_acesso == chave).first()

        if not cte:
            return False

        existente = (
            self.db.query(EventoDocumentoFiscal)
            .filter(
                EventoDocumentoFiscal.documento_id == cte.id,
                EventoDocumentoFiscal.tipo_evento == registro.get("tipo_evento"),
                EventoDocumentoFiscal.sequencia == registro.get("sequencia", 1),
            )
            .first()
        )

        if existente:
            return False

        evento = EventoDocumentoFiscal(
            documento_id=cte.id,
            tipo_evento=registro.get("tipo_evento"),
            sequencia=registro.get("sequencia", 1),
            data_evento=registro.get("data_evento") or datetime.utcnow(),
            protocolo=registro.get("protocolo"),
            descricao=registro.get("descricao"),
            xml_evento=registro.get("xml_evento"),
        )
        self.db.add(evento)

        if registro.get("tipo_evento") == "110111":
            cte.status = StatusDocumentoFiscal.CANCELADO
            cte.data_cancelamento = registro.get("data_evento")

        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtem ultima sincronizacao de CT-e."""
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
        """Obtem resumo dos CT-e sincronizados."""
        from sqlalchemy import func

        from ..models.sync_models import DocumentoFiscal, TipoDocumentoFiscal

        totais = (
            self.db.query(
                func.count(DocumentoFiscal.id),
                func.sum(DocumentoFiscal.valor_total),
            )
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo == TipoDocumentoFiscal.CTE,
            )
            .first()
        )

        return {
            "total_ctes": totais[0] or 0,
            "valor_total": float(totais[1] or 0),
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
