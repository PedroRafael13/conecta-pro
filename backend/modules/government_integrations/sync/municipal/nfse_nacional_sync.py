"""
Sincronizador de NFS-e Nacional (Padrao Nacional).

Extrai e sincroniza:
- NFS-e emitidas via ambiente nacional
- NFS-e recebidas
- Eventos (cancelamento, substituicao)
- DPS (Declaracao Prestacao Servicos)
"""

import logging
from collections.abc import AsyncGenerator
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class NFSeNacionalSynchronizer(BaseSynchronizer):
    """Sincronizador de NFS-e do Ambiente Nacional."""

    SERVICO_NOME = "nfse_nacional"
    INTERVALO_PADRAO = 60  # 1 hora
    DIAS_RETROATIVOS_PADRAO = 30

    # URL do ambiente nacional
    URL_PRODUCAO = "https://www.nfse.gov.br/EmissorNacional"
    URL_HOMOLOGACAO = "https://sefin.nfse.gov.br/sefinnacional"

    # Situacoes da NFS-e
    SITUACOES = {
        "1": "Normal",
        "2": "Cancelada",
        "3": "Substituida",
    }

    # Regimes tributarios
    REGIMES = {
        "1": "Microempresa Municipal",
        "2": "Estimativa",
        "3": "Sociedade de Profissionais",
        "4": "Cooperativa",
        "5": "MEI",
        "6": "ME/EPP Simples Nacional",
    }

    def __init__(self, db_session, certificate_manager=None, nfse_nacional_service=None):
        super().__init__(db_session, certificate_manager)
        self.nfse_service = nfse_nacional_service

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai NFS-e do Ambiente Nacional.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados de cada NFS-e
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)
        codigo_municipio = config.parametros_extras.get("codigo_municipio")

        logger.info(
            f"[NFS-e Nacional] Extraindo dados - CNPJ: {cnpj}, Periodo: {config.data_inicial} a {config.data_final}"
        )

        # 1. NFS-e emitidas
        async for nfse in self._consultar_nfse_emitidas(cnpj, codigo_municipio, config):
            yield nfse

        # 2. NFS-e recebidas (como tomador)
        async for nfse in self._consultar_nfse_tomadas(cnpj, config):
            yield nfse

        # 3. DPS pendentes
        async for dps in self._consultar_dps_pendentes(cnpj, codigo_municipio, config):
            yield dps

        # 4. Eventos
        async for evento in self._consultar_eventos(cnpj, codigo_municipio, config):
            yield evento

    async def _consultar_nfse_emitidas(
        self,
        cnpj: str,
        codigo_municipio: str | None,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta NFS-e emitidas pelo prestador."""
        try:
            if not self.nfse_service:
                logger.warning("[NFS-e Nacional] Service nao configurado")
                return

            notas = await self._request_com_retry(
                self.nfse_service.consultar_nfse_prestador,
                cnpj=cnpj,
                codigo_municipio=codigo_municipio,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for nota in notas or []:
                yield {
                    "tipo": "nfse_nacional",
                    "direcao": "emitida",
                    "chave_acesso": nota.get("chave"),
                    "numero": nota.get("numero"),
                    "codigo_verificacao": nota.get("codigo_verificacao"),
                    "data_emissao": self._parse_data(nota.get("data_emissao")),
                    "competencia": nota.get("competencia"),
                    "natureza_tributacao": nota.get("natureza_tributacao"),
                    "regime_especial": nota.get("regime_especial"),
                    # Prestador
                    "cnpj_prestador": nota.get("cnpj_prestador"),
                    "inscricao_municipal_prestador": nota.get("im_prestador"),
                    "razao_social_prestador": nota.get("razao_social_prestador"),
                    "municipio_prestador": nota.get("municipio_prestador"),
                    "uf_prestador": nota.get("uf_prestador"),
                    # Tomador
                    "cnpj_tomador": nota.get("cnpj_tomador"),
                    "cpf_tomador": nota.get("cpf_tomador"),
                    "razao_social_tomador": nota.get("razao_social_tomador"),
                    "municipio_tomador": nota.get("municipio_tomador"),
                    "uf_tomador": nota.get("uf_tomador"),
                    "email_tomador": nota.get("email_tomador"),
                    # Servico
                    "codigo_servico": nota.get("codigo_servico"),
                    "codigo_cnae": nota.get("codigo_cnae"),
                    "discriminacao": nota.get("discriminacao"),
                    "municipio_incidencia": nota.get("municipio_incidencia"),
                    # Valores
                    "valor_servicos": self._parse_decimal(nota.get("valor_servicos")),
                    "valor_deducoes": self._parse_decimal(nota.get("valor_deducoes")),
                    "base_calculo": self._parse_decimal(nota.get("base_calculo")),
                    "aliquota_iss": self._parse_decimal(nota.get("aliquota_iss")),
                    "valor_iss": self._parse_decimal(nota.get("valor_iss")),
                    "valor_iss_retido": self._parse_decimal(nota.get("valor_iss_retido")),
                    "valor_liquido": self._parse_decimal(nota.get("valor_liquido")),
                    "valor_pis": self._parse_decimal(nota.get("valor_pis")),
                    "valor_cofins": self._parse_decimal(nota.get("valor_cofins")),
                    "valor_inss": self._parse_decimal(nota.get("valor_inss")),
                    "valor_ir": self._parse_decimal(nota.get("valor_ir")),
                    "valor_csll": self._parse_decimal(nota.get("valor_csll")),
                    "outras_retencoes": self._parse_decimal(nota.get("outras_retencoes")),
                    # ISS
                    "iss_retido": nota.get("iss_retido", False),
                    "exigibilidade_iss": nota.get("exigibilidade_iss"),
                    # Situacao
                    "situacao": nota.get("situacao"),
                    "descricao_situacao": self.SITUACOES.get(nota.get("situacao"), "Normal"),
                    # XML
                    "xml_nfse": nota.get("xml"),
                }

        except Exception as e:
            logger.error(f"[NFS-e Nacional] Erro consultando notas emitidas: {e}")
            raise

    async def _consultar_nfse_tomadas(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta NFS-e tomadas (recebidas como tomador)."""
        try:
            if not self.nfse_service:
                return

            notas = await self._request_com_retry(
                self.nfse_service.consultar_nfse_tomador,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for nota in notas or []:
                dados = {
                    "tipo": "nfse_nacional",
                    "direcao": "tomada",
                    "chave_acesso": nota.get("chave"),
                    "numero": nota.get("numero"),
                    "codigo_verificacao": nota.get("codigo_verificacao"),
                    "data_emissao": self._parse_data(nota.get("data_emissao")),
                    "competencia": nota.get("competencia"),
                    "cnpj_prestador": nota.get("cnpj_prestador"),
                    "razao_social_prestador": nota.get("razao_social_prestador"),
                    "cnpj_tomador": nota.get("cnpj_tomador"),
                    "valor_servicos": self._parse_decimal(nota.get("valor_servicos")),
                    "valor_iss": self._parse_decimal(nota.get("valor_iss")),
                    "valor_iss_retido": self._parse_decimal(nota.get("valor_iss_retido")),
                    "iss_retido": nota.get("iss_retido", False),
                    "situacao": nota.get("situacao"),
                    "xml_nfse": nota.get("xml"),
                }

                yield dados

        except Exception as e:
            logger.error(f"[NFS-e Nacional] Erro consultando notas tomadas: {e}")

    async def _consultar_dps_pendentes(
        self,
        cnpj: str,
        codigo_municipio: str | None,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta DPS (Declaracao Prestacao Servicos) pendentes."""
        try:
            if not self.nfse_service:
                return

            dps_list = await self._request_com_retry(
                self.nfse_service.consultar_dps_pendentes,
                cnpj=cnpj,
                codigo_municipio=codigo_municipio,
            )

            for dps in dps_list or []:
                yield {
                    "tipo": "dps",
                    "id_dps": dps.get("id"),
                    "cnpj_prestador": cnpj,
                    "data_emissao": self._parse_data(dps.get("data_emissao")),
                    "competencia": dps.get("competencia"),
                    "valor_servicos": self._parse_decimal(dps.get("valor_servicos")),
                    "situacao": dps.get("situacao"),
                    "motivo_pendencia": dps.get("motivo"),
                    "xml_dps": dps.get("xml"),
                }

        except Exception as e:
            logger.error(f"[NFS-e Nacional] Erro consultando DPS pendentes: {e}")

    async def _consultar_eventos(
        self,
        cnpj: str,
        codigo_municipio: str | None,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta eventos das NFS-e."""
        try:
            if not self.nfse_service:
                return

            eventos = await self._request_com_retry(
                self.nfse_service.consultar_eventos,
                cnpj=cnpj,
                codigo_municipio=codigo_municipio,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for evento in eventos or []:
                yield {
                    "tipo": "evento_nfse_nacional",
                    "chave_nfse": evento.get("chave_nfse"),
                    "tipo_evento": evento.get("tipo"),
                    "data_evento": self._parse_data(evento.get("data")),
                    "sequencia": evento.get("sequencia"),
                    "motivo": evento.get("motivo"),
                    "chave_substituta": evento.get("chave_substituta"),
                    "codigo_cancelamento": evento.get("codigo_cancelamento"),
                    "protocolo": evento.get("protocolo"),
                    "xml_evento": evento.get("xml"),
                }

        except Exception as e:
            logger.error(f"[NFS-e Nacional] Erro consultando eventos: {e}")

    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "nfse_nacional":
            return await self._salvar_nfse(registro, config)
        elif tipo == "dps":
            return await self._salvar_dps(registro, config)
        elif tipo == "evento_nfse_nacional":
            return await self._salvar_evento(registro)

        return False

    async def _salvar_nfse(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva ou atualiza NFS-e Nacional."""
        from ..models.sync_models import DocumentoFiscal, StatusDocumentoFiscal, TipoDocumentoFiscal

        chave = registro.get("chave_acesso")
        if not chave:
            numero = registro.get("numero")
            codigo = registro.get("codigo_verificacao")
            chave = f"{config.cnpj_empresa}_{numero}_{codigo}"

        existente = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.chave_acesso == chave).first()

        # Mapear situacao
        situacao_map = {
            "1": StatusDocumentoFiscal.AUTORIZADA,
            "2": StatusDocumentoFiscal.CANCELADA,
            "3": StatusDocumentoFiscal.SUBSTITUIDA,
        }
        status = situacao_map.get(registro.get("situacao"), StatusDocumentoFiscal.AUTORIZADA)

        if existente:
            existente.status = status
            existente.xml_documento = registro.get("xml_nfse") or existente.xml_documento
            existente.updated_at = datetime.utcnow()
            return False

        # Determinar CNPJ da empresa
        if registro.get("direcao") == "emitida":
            cnpj_empresa = registro.get("cnpj_prestador") or config.cnpj_empresa
        else:
            cnpj_empresa = registro.get("cnpj_tomador") or config.cnpj_empresa

        novo = DocumentoFiscal(
            cnpj_empresa=cnpj_empresa,
            tipo_documento=TipoDocumentoFiscal.NFSE,
            chave_acesso=chave,
            numero=registro.get("numero"),
            serie="NAC",
            data_emissao=registro.get("data_emissao") or date.today(),
            cnpj_emitente=registro.get("cnpj_prestador"),
            nome_emitente=registro.get("razao_social_prestador"),
            cnpj_destinatario=registro.get("cnpj_tomador") or registro.get("cpf_tomador"),
            nome_destinatario=registro.get("razao_social_tomador"),
            valor_total=registro.get("valor_servicos") or Decimal("0"),
            valor_servicos=registro.get("valor_servicos"),
            valor_iss=registro.get("valor_iss"),
            codigo_servico=registro.get("codigo_servico"),
            status=status,
            direcao=registro.get("direcao"),
            xml_documento=registro.get("xml_nfse"),
            dados_adicionais={
                "codigo_verificacao": registro.get("codigo_verificacao"),
                "competencia": registro.get("competencia"),
                "natureza_tributacao": registro.get("natureza_tributacao"),
                "discriminacao": registro.get("discriminacao"),
                "codigo_cnae": registro.get("codigo_cnae"),
                "municipio_incidencia": registro.get("municipio_incidencia"),
                "municipio_prestador": registro.get("municipio_prestador"),
                "municipio_tomador": registro.get("municipio_tomador"),
                "aliquota_iss": str(registro.get("aliquota_iss") or 0),
                "iss_retido": registro.get("iss_retido"),
                "exigibilidade_iss": registro.get("exigibilidade_iss"),
                "valor_deducoes": str(registro.get("valor_deducoes") or 0),
                "valor_pis": str(registro.get("valor_pis") or 0),
                "valor_cofins": str(registro.get("valor_cofins") or 0),
                "valor_inss": str(registro.get("valor_inss") or 0),
                "valor_ir": str(registro.get("valor_ir") or 0),
                "valor_csll": str(registro.get("valor_csll") or 0),
                "email_tomador": registro.get("email_tomador"),
            },
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_dps(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva DPS pendente."""
        from ..models.sync_models import DPSPendente

        id_dps = registro.get("id_dps")

        existente = self.db.query(DPSPendente).filter(DPSPendente.id_dps == id_dps).first()

        if existente:
            existente.situacao = registro.get("situacao")
            existente.updated_at = datetime.utcnow()
            return False

        novo = DPSPendente(
            cnpj_empresa=config.cnpj_empresa,
            id_dps=id_dps,
            data_emissao=registro.get("data_emissao"),
            competencia=registro.get("competencia"),
            valor_servicos=Decimal(str(registro.get("valor_servicos") or 0)),
            situacao=registro.get("situacao"),
            motivo_pendencia=registro.get("motivo_pendencia"),
            xml_dps=registro.get("xml_dps"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_evento(self, registro: dict[str, Any]) -> bool:
        """Salva evento de NFS-e Nacional."""
        from ..models.sync_models import DocumentoFiscal, EventoDocumentoFiscal, StatusDocumentoFiscal

        chave = registro.get("chave_nfse")
        if not chave:
            return False

        nfse = self.db.query(DocumentoFiscal).filter(DocumentoFiscal.chave_acesso == chave).first()

        if not nfse:
            return False

        existente = (
            self.db.query(EventoDocumentoFiscal)
            .filter(
                EventoDocumentoFiscal.documento_id == nfse.id,
                EventoDocumentoFiscal.tipo_evento == registro.get("tipo_evento"),
                EventoDocumentoFiscal.sequencia == registro.get("sequencia", 1),
            )
            .first()
        )

        if existente:
            return False

        evento = EventoDocumentoFiscal(
            documento_id=nfse.id,
            tipo_evento=registro.get("tipo_evento"),
            sequencia=registro.get("sequencia", 1),
            data_evento=registro.get("data_evento") or datetime.utcnow(),
            protocolo=registro.get("protocolo"),
            descricao=registro.get("motivo"),
            xml_evento=registro.get("xml_evento"),
            dados_adicionais={
                "chave_substituta": registro.get("chave_substituta"),
                "codigo_cancelamento": registro.get("codigo_cancelamento"),
            },
        )
        self.db.add(evento)

        # Atualizar status
        tipo_evento = registro.get("tipo_evento")
        if tipo_evento == "cancelamento":
            nfse.status = StatusDocumentoFiscal.CANCELADA
            nfse.data_cancelamento = registro.get("data_evento")
        elif tipo_evento == "substituicao":
            nfse.status = StatusDocumentoFiscal.SUBSTITUIDA

        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtem ultima sincronizacao de NFS-e Nacional."""
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
        """Obtem resumo das NFS-e Nacional sincronizadas."""
        from sqlalchemy import func

        from ..models.sync_models import DocumentoFiscal, TipoDocumentoFiscal

        # Filtrar apenas NFS-e do ambiente nacional (serie NAC)
        totais = (
            self.db.query(
                func.count(DocumentoFiscal.id),
                func.sum(DocumentoFiscal.valor_total),
            )
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo_documento == TipoDocumentoFiscal.NFSE,
                DocumentoFiscal.serie == "NAC",
            )
            .first()
        )

        por_direcao = (
            self.db.query(
                DocumentoFiscal.direcao,
                func.count(DocumentoFiscal.id),
                func.sum(DocumentoFiscal.valor_total),
            )
            .filter(
                DocumentoFiscal.cnpj_empresa == cnpj,
                DocumentoFiscal.tipo_documento == TipoDocumentoFiscal.NFSE,
                DocumentoFiscal.serie == "NAC",
            )
            .group_by(DocumentoFiscal.direcao)
            .all()
        )

        return {
            "total_nfse": totais[0] or 0,
            "valor_total": float(totais[1] or 0),
            "por_direcao": {str(d): {"quantidade": q, "valor": float(v or 0)} for d, q, v in por_direcao if d},
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
