"""
Sincronizador de Notas Fiscais Eletronicas (NF-e/NFC-e).

Extrai e sincroniza:
- NF-e emitidas pela empresa
- NF-e destinadas a empresa (compras)
- Eventos (cancelamento, carta correcao)
- XMLs completos
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List, AsyncGenerator
from decimal import Decimal
import xml.etree.ElementTree as ET

from ..base_sync import BaseSynchronizer, SyncConfig, SyncResult

logger = logging.getLogger(__name__)


class NFeSynchronizer(BaseSynchronizer):
    """Sincronizador de NF-e/NFC-e da SEFAZ."""

    SERVICO_NOME = "sefaz_nfe"
    INTERVALO_PADRAO = 30  # 30 minutos
    DIAS_RETROATIVOS_PADRAO = 30

    # Namespaces XML NFe
    NS_NFE = {
        "nfe": "http://www.portalfiscal.inf.br/nfe",
    }

    def __init__(self, db_session, certificate_manager=None, sefaz_manager=None):
        super().__init__(db_session, certificate_manager)
        self.sefaz_manager = sefaz_manager

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extrai NF-e do webservice SEFAZ.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados de cada NF-e
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(
            f"[NF-e] Extraindo notas - CNPJ: {cnpj}, "
            f"Periodo: {config.data_inicial} a {config.data_final}"
        )

        # 1. Notas emitidas pela empresa
        async for nota in self._consultar_notas_emitidas(cnpj, config):
            yield nota

        # 2. Notas destinadas a empresa (compras)
        async for nota in self._consultar_notas_destinadas(cnpj, config):
            yield nota

        # 3. Eventos das notas
        async for evento in self._consultar_eventos(cnpj, config):
            yield evento

    async def _consultar_notas_emitidas(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta NF-e emitidas pela empresa."""
        try:
            if not self.sefaz_manager:
                logger.warning("[NF-e] SEFAZ Manager nao configurado")
                return

            # Consultar notas emitidas
            notas = await self._request_com_retry(
                self.sefaz_manager.consultar_notas_emitidas,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for nota in notas:
                # Baixar XML completo
                xml = await self._baixar_xml(nota.get("chave"))

                dados = self._parse_nfe_xml(xml) if xml else {}
                dados.update({
                    "tipo": "nfe_emitida",
                    "chave_acesso": nota.get("chave"),
                    "tipo_participacao": "emitente",
                    "xml_original": xml,
                })

                yield dados

        except Exception as e:
            logger.error(f"[NF-e] Erro consultando notas emitidas: {e}")
            raise

    async def _consultar_notas_destinadas(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta NF-e destinadas a empresa (DF-e)."""
        try:
            if not self.sefaz_manager:
                return

            # Consultar manifestacao do destinatario (DF-e)
            notas = await self._request_com_retry(
                self.sefaz_manager.consultar_dfe,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for nota in notas:
                # Baixar XML se disponivel
                xml = None
                if nota.get("schema") == "resNFe":
                    # Resumo - tentar baixar completo
                    xml = await self._baixar_xml_destinatario(
                        nota.get("chave"),
                        cnpj,
                    )

                dados = self._parse_nfe_xml(xml) if xml else {
                    "numero": nota.get("numero"),
                    "data_emissao": self._parse_data(nota.get("data_emissao")),
                    "valor_total": self._parse_decimal(nota.get("valor")),
                    "cnpj_emitente": nota.get("cnpj_emitente"),
                    "razao_social_emitente": nota.get("razao_social"),
                }

                dados.update({
                    "tipo": "nfe_destinada",
                    "chave_acesso": nota.get("chave"),
                    "tipo_participacao": "destinatario",
                    "situacao_manifestacao": nota.get("situacao"),
                    "xml_original": xml,
                })

                yield dados

        except Exception as e:
            logger.error(f"[NF-e] Erro consultando notas destinadas: {e}")

    async def _consultar_eventos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta eventos das NF-e (cancelamento, CC-e)."""
        try:
            if not self.sefaz_manager:
                return

            # Buscar notas no banco para consultar eventos
            notas_locais = await self._buscar_notas_para_atualizar(cnpj, config)

            for nota in notas_locais:
                chave = nota.get("chave_acesso")
                if not chave:
                    continue

                # Consultar eventos da nota
                eventos = await self._request_com_retry(
                    self.sefaz_manager.consultar_eventos_nfe,
                    chave=chave,
                )

                for evento in eventos:
                    yield {
                        "tipo": "evento_nfe",
                        "chave_acesso": chave,
                        "tipo_evento": evento.get("tipo"),
                        "sequencia": evento.get("sequencia"),
                        "data_evento": self._parse_data(evento.get("data")),
                        "protocolo": evento.get("protocolo"),
                        "descricao": evento.get("descricao"),
                        "xml_evento": evento.get("xml"),
                    }

        except Exception as e:
            logger.error(f"[NF-e] Erro consultando eventos: {e}")

    async def _baixar_xml(self, chave: str) -> Optional[bytes]:
        """Baixa XML completo da NF-e."""
        try:
            if not self.sefaz_manager or not chave:
                return None

            xml = await self._request_com_retry(
                self.sefaz_manager.baixar_xml,
                chave=chave,
            )
            return xml

        except Exception as e:
            logger.warning(f"[NF-e] Erro baixando XML {chave}: {e}")
            return None

    async def _baixar_xml_destinatario(
        self,
        chave: str,
        cnpj_destinatario: str,
    ) -> Optional[bytes]:
        """Baixa XML de nota destinada via manifestacao."""
        try:
            if not self.sefaz_manager:
                return None

            xml = await self._request_com_retry(
                self.sefaz_manager.baixar_xml_destinatario,
                chave=chave,
                cnpj=cnpj_destinatario,
            )
            return xml

        except Exception as e:
            logger.warning(f"[NF-e] Erro baixando XML destinatario {chave}: {e}")
            return None

    async def _buscar_notas_para_atualizar(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> List[Dict]:
        """Busca notas no banco para consultar eventos."""
        # Implementacao depende do modelo real
        return []

    def _parse_nfe_xml(self, xml: bytes) -> Dict[str, Any]:
        """Extrai dados do XML da NF-e."""
        if not xml:
            return {}

        try:
            root = ET.fromstring(xml)

            # Encontrar elementos principais
            infNFe = root.find(".//nfe:infNFe", self.NS_NFE)
            if infNFe is None:
                # Tentar sem namespace
                infNFe = root.find(".//infNFe")

            if infNFe is None:
                return {}

            # Identificacao
            ide = infNFe.find("nfe:ide", self.NS_NFE) or infNFe.find("ide")
            emit = infNFe.find("nfe:emit", self.NS_NFE) or infNFe.find("emit")
            dest = infNFe.find("nfe:dest", self.NS_NFE) or infNFe.find("dest")
            total = infNFe.find("nfe:total/nfe:ICMSTot", self.NS_NFE) or infNFe.find("total/ICMSTot")

            dados = {
                "numero": self._get_text(ide, "nNF"),
                "serie": self._get_text(ide, "serie"),
                "data_emissao": self._parse_data(self._get_text(ide, "dhEmi")),
                "tipo_documento": "nfe" if self._get_text(ide, "mod") == "55" else "nfce",
            }

            # Emitente
            if emit is not None:
                dados.update({
                    "cnpj_emitente": self._get_text(emit, "CNPJ"),
                    "razao_social_emitente": self._get_text(emit, "xNome"),
                    "uf_emitente": self._get_text(emit, "enderEmit/UF"),
                })

            # Destinatario
            if dest is not None:
                dados.update({
                    "cnpj_cpf_destinatario": (
                        self._get_text(dest, "CNPJ") or
                        self._get_text(dest, "CPF")
                    ),
                    "razao_social_destinatario": self._get_text(dest, "xNome"),
                    "uf_destinatario": self._get_text(dest, "enderDest/UF"),
                })

            # Valores
            if total is not None:
                dados.update({
                    "valor_total": self._parse_decimal(self._get_text(total, "vNF")),
                    "valor_produtos": self._parse_decimal(self._get_text(total, "vProd")),
                    "valor_desconto": self._parse_decimal(self._get_text(total, "vDesc")),
                    "valor_frete": self._parse_decimal(self._get_text(total, "vFrete")),
                    "valor_icms": self._parse_decimal(self._get_text(total, "vICMS")),
                    "valor_icms_st": self._parse_decimal(self._get_text(total, "vST")),
                    "valor_ipi": self._parse_decimal(self._get_text(total, "vIPI")),
                    "valor_pis": self._parse_decimal(self._get_text(total, "vPIS")),
                    "valor_cofins": self._parse_decimal(self._get_text(total, "vCOFINS")),
                })

            # Itens
            itens = []
            for det in infNFe.findall("nfe:det", self.NS_NFE) or infNFe.findall("det"):
                prod = det.find("nfe:prod", self.NS_NFE) or det.find("prod")
                if prod is not None:
                    itens.append({
                        "numero_item": det.get("nItem"),
                        "codigo": self._get_text(prod, "cProd"),
                        "descricao": self._get_text(prod, "xProd"),
                        "ncm": self._get_text(prod, "NCM"),
                        "cfop": self._get_text(prod, "CFOP"),
                        "unidade": self._get_text(prod, "uCom"),
                        "quantidade": self._parse_decimal(self._get_text(prod, "qCom")),
                        "valor_unitario": self._parse_decimal(self._get_text(prod, "vUnCom")),
                        "valor_total": self._parse_decimal(self._get_text(prod, "vProd")),
                    })
            dados["itens"] = itens

            return dados

        except Exception as e:
            logger.error(f"[NF-e] Erro parseando XML: {e}")
            return {}

    def _get_text(self, element, path: str) -> Optional[str]:
        """Obtem texto de elemento XML."""
        if element is None:
            return None

        # Tentar com namespace
        el = element.find(f"nfe:{path}", self.NS_NFE)
        if el is None:
            # Tentar sem namespace
            el = element.find(path)

        return el.text if el is not None else None

    async def _processar_registro(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo in ("nfe_emitida", "nfe_destinada"):
            return await self._salvar_nota(registro, config)
        elif tipo == "evento_nfe":
            return await self._salvar_evento(registro)

        return False

    async def _salvar_nota(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva ou atualiza NF-e no banco."""
        from ..models.sync_models import (
            DocumentoFiscal, TipoDocumentoFiscal,
            StatusDocumentoFiscal, TipoParticipacao
        )

        chave = registro.get("chave_acesso")
        if not chave:
            return False

        # Verificar se existe
        existente = self.db.query(DocumentoFiscal).filter(
            DocumentoFiscal.chave_acesso == chave
        ).first()

        # Determinar tipo
        tipo_doc = TipoDocumentoFiscal.NFE
        if registro.get("tipo_documento") == "nfce":
            tipo_doc = TipoDocumentoFiscal.NFCE

        # Determinar participacao
        tipo_part = TipoParticipacao.EMITENTE
        if registro.get("tipo_participacao") == "destinatario":
            tipo_part = TipoParticipacao.DESTINATARIO

        if existente:
            # Atualizar
            existente.xml_original = registro.get("xml_original") or existente.xml_original
            existente.updated_at = datetime.utcnow()
            return False
        else:
            # Criar novo
            nova = DocumentoFiscal(
                tipo=tipo_doc,
                chave_acesso=chave,
                numero=registro.get("numero") or 0,
                serie=registro.get("serie") or 1,
                cnpj_empresa=config.cnpj_empresa,
                tipo_participacao=tipo_part,
                cnpj_emitente=registro.get("cnpj_emitente"),
                razao_social_emitente=registro.get("razao_social_emitente"),
                uf_emitente=registro.get("uf_emitente"),
                cnpj_cpf_destinatario=registro.get("cnpj_cpf_destinatario"),
                razao_social_destinatario=registro.get("razao_social_destinatario"),
                uf_destinatario=registro.get("uf_destinatario"),
                data_emissao=registro.get("data_emissao") or datetime.utcnow(),
                valor_total=Decimal(str(registro.get("valor_total") or 0)),
                valor_produtos=Decimal(str(registro.get("valor_produtos") or 0)),
                valor_desconto=Decimal(str(registro.get("valor_desconto") or 0)),
                valor_frete=Decimal(str(registro.get("valor_frete") or 0)),
                valor_icms=Decimal(str(registro.get("valor_icms") or 0)),
                valor_icms_st=Decimal(str(registro.get("valor_icms_st") or 0)),
                valor_ipi=Decimal(str(registro.get("valor_ipi") or 0)),
                valor_pis=Decimal(str(registro.get("valor_pis") or 0)),
                valor_cofins=Decimal(str(registro.get("valor_cofins") or 0)),
                status=StatusDocumentoFiscal.AUTORIZADO,
                xml_original=registro.get("xml_original"),
                itens=registro.get("itens"),
                sync_id=self._current_sync_id,
            )
            self.db.add(nova)
            return True

    async def _salvar_evento(self, registro: Dict[str, Any]) -> bool:
        """Salva evento de NF-e."""
        from ..models.sync_models import DocumentoFiscal, EventoDocumentoFiscal

        chave = registro.get("chave_acesso")
        if not chave:
            return False

        # Buscar nota
        nota = self.db.query(DocumentoFiscal).filter(
            DocumentoFiscal.chave_acesso == chave
        ).first()

        if not nota:
            return False

        # Verificar se evento ja existe
        existente = self.db.query(EventoDocumentoFiscal).filter(
            EventoDocumentoFiscal.documento_id == nota.id,
            EventoDocumentoFiscal.tipo_evento == registro.get("tipo_evento"),
            EventoDocumentoFiscal.sequencia == registro.get("sequencia", 1),
        ).first()

        if existente:
            return False

        # Criar evento
        evento = EventoDocumentoFiscal(
            documento_id=nota.id,
            tipo_evento=registro.get("tipo_evento"),
            sequencia=registro.get("sequencia", 1),
            data_evento=registro.get("data_evento") or datetime.utcnow(),
            protocolo=registro.get("protocolo"),
            descricao=registro.get("descricao"),
            xml_evento=registro.get("xml_evento"),
        )
        self.db.add(evento)

        # Atualizar status da nota se for cancelamento
        if registro.get("tipo_evento") == "110111":  # Cancelamento
            nota.status = StatusDocumentoFiscal.CANCELADO
            nota.data_cancelamento = registro.get("data_evento")

        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> Optional[datetime]:
        """Obtem ultima sincronizacao de NF-e."""
        from ..models.sync_models import SyncLog, StatusSincronizacao

        ultimo = self.db.query(SyncLog).filter(
            SyncLog.cnpj_empresa == cnpj,
            SyncLog.servico == self.SERVICO_NOME,
            SyncLog.status == StatusSincronizacao.SUCESSO,
        ).order_by(SyncLog.fim_execucao.desc()).first()

        return ultimo.fim_execucao if ultimo else None

    # =========================================================================
    # METODOS ADICIONAIS
    # =========================================================================

    async def manifestar_nota(
        self,
        cnpj: str,
        chave: str,
        tipo_manifestacao: str,
        justificativa: str = None,
    ) -> Dict[str, Any]:
        """
        Realiza manifestacao do destinatario.

        Args:
            cnpj: CNPJ da empresa
            chave: Chave de acesso da NF-e
            tipo_manifestacao: confirmacao, desconhecimento, nao_realizada, ciencia
            justificativa: Justificativa (obrigatorio para nao_realizada)

        Returns:
            Dict com resultado
        """
        if not self.sefaz_manager:
            raise ValueError("SEFAZ Manager nao configurado")

        resultado = await self.sefaz_manager.manifestar_destinatario(
            cnpj=cnpj,
            chave=chave,
            tipo=tipo_manifestacao,
            justificativa=justificativa,
        )

        return resultado

    async def obter_resumo(self, cnpj: str) -> Dict[str, Any]:
        """Obtem resumo das NF-e sincronizadas."""
        from ..models.sync_models import DocumentoFiscal, TipoDocumentoFiscal
        from sqlalchemy import func

        # Totais
        totais = self.db.query(
            func.count(DocumentoFiscal.id),
            func.sum(DocumentoFiscal.valor_total),
        ).filter(
            DocumentoFiscal.cnpj_empresa == cnpj,
            DocumentoFiscal.tipo.in_([TipoDocumentoFiscal.NFE, TipoDocumentoFiscal.NFCE]),
        ).first()

        # Por tipo de participacao
        por_participacao = self.db.query(
            DocumentoFiscal.tipo_participacao,
            func.count(DocumentoFiscal.id),
            func.sum(DocumentoFiscal.valor_total),
        ).filter(
            DocumentoFiscal.cnpj_empresa == cnpj,
        ).group_by(DocumentoFiscal.tipo_participacao).all()

        return {
            "total_notas": totais[0] or 0,
            "valor_total": float(totais[1] or 0),
            "por_participacao": {
                str(p.value): {"quantidade": q, "valor": float(v or 0)}
                for p, q, v in por_participacao
            },
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
