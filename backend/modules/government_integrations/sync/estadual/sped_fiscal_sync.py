"""
Sincronizador do SPED Fiscal (EFD ICMS/IPI).

Extrai e sincroniza:
- Escrituracoes transmitidas
- Registros de entrada/saida
- Apuracao ICMS/IPI
- Inventario
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, AsyncGenerator
from decimal import Decimal

from ..base_sync import BaseSynchronizer, SyncConfig, SyncResult

logger = logging.getLogger(__name__)


class SPEDFiscalSynchronizer(BaseSynchronizer):
    """Sincronizador de dados do SPED Fiscal (EFD ICMS/IPI)."""

    SERVICO_NOME = "sped_fiscal"
    INTERVALO_PADRAO = 1440  # 24 horas
    DIAS_RETROATIVOS_PADRAO = 365

    # Perfis de apresentacao
    PERFIS = {
        "A": "Perfil A - Apresentacao mais detalhada",
        "B": "Perfil B - Apresentacao intermediaria",
        "C": "Perfil C - Apresentacao simplificada",
    }

    def __init__(self, db_session, certificate_manager=None, sped_service=None):
        super().__init__(db_session, certificate_manager)
        self.sped_service = sped_service

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extrai dados do SPED Fiscal.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados extraidos
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(
            f"[SPED Fiscal] Extraindo dados - CNPJ: {cnpj}, "
            f"Periodo: {config.data_inicial} a {config.data_final}"
        )

        # 1. Escrituracoes transmitidas
        async for escrituracao in self._consultar_escrituracoes(cnpj, config):
            yield escrituracao

        # 2. Apuracao ICMS
        async for apuracao in self._consultar_apuracao_icms(cnpj, config):
            yield apuracao

        # 3. Apuracao IPI
        async for apuracao in self._consultar_apuracao_ipi(cnpj, config):
            yield apuracao

        # 4. Resumo de documentos
        async for resumo in self._consultar_resumo_documentos(cnpj, config):
            yield resumo

    async def _consultar_escrituracoes(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta escrituracoes SPED Fiscal transmitidas."""
        try:
            if not self.sped_service:
                logger.warning("[SPED Fiscal] Service nao configurado")
                return

            escrituracoes = await self._request_com_retry(
                self.sped_service.consultar_escrituracoes_fiscais,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for esc in escrituracoes or []:
                yield {
                    "tipo": "escrituracao_efd",
                    "numero_recibo": esc.get("recibo"),
                    "periodo_apuracao": esc.get("periodo"),
                    "data_inicial": self._parse_data(esc.get("data_inicial")),
                    "data_final": self._parse_data(esc.get("data_final")),
                    "perfil": esc.get("perfil"),
                    "descricao_perfil": self.PERFIS.get(esc.get("perfil"), "Perfil B"),
                    "data_transmissao": self._parse_data(esc.get("data_transmissao")),
                    "situacao": esc.get("situacao"),
                    "finalidade": esc.get("finalidade"),
                    "hash_arquivo": esc.get("hash"),
                    "retificadora": esc.get("retificadora", False),
                    "recibo_retificado": esc.get("recibo_retificado"),
                }

        except Exception as e:
            logger.error(f"[SPED Fiscal] Erro consultando escrituracoes: {e}")
            raise

    async def _consultar_apuracao_icms(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta apuracao do ICMS."""
        try:
            if not self.sped_service:
                return

            data_atual = config.data_inicial
            while data_atual <= config.data_final:
                periodo = data_atual.strftime("%Y-%m")

                apuracao = await self._request_com_retry(
                    self.sped_service.consultar_apuracao_icms,
                    cnpj=cnpj,
                    periodo=periodo,
                )

                if apuracao:
                    yield {
                        "tipo": "apuracao_icms",
                        "periodo_apuracao": periodo,
                        "valor_total_debitos": self._parse_decimal(apuracao.get("debitos")),
                        "valor_ajustes_debitos": self._parse_decimal(apuracao.get("ajustes_deb")),
                        "valor_total_creditos": self._parse_decimal(apuracao.get("creditos")),
                        "valor_ajustes_creditos": self._parse_decimal(apuracao.get("ajustes_cred")),
                        "saldo_credor_anterior": self._parse_decimal(apuracao.get("saldo_ant")),
                        "valor_total_deducoes": self._parse_decimal(apuracao.get("deducoes")),
                        "icms_recolher": self._parse_decimal(apuracao.get("icms_recolher")),
                        "saldo_credor_transportar": self._parse_decimal(apuracao.get("saldo_cred")),
                        "icms_st_recolher": self._parse_decimal(apuracao.get("icms_st")),
                        "difal_recolher": self._parse_decimal(apuracao.get("difal")),
                        "fcp_recolher": self._parse_decimal(apuracao.get("fcp")),
                    }

                if data_atual.month == 12:
                    data_atual = date(data_atual.year + 1, 1, 1)
                else:
                    data_atual = date(data_atual.year, data_atual.month + 1, 1)

        except Exception as e:
            logger.error(f"[SPED Fiscal] Erro consultando apuracao ICMS: {e}")

    async def _consultar_apuracao_ipi(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta apuracao do IPI."""
        try:
            if not self.sped_service:
                return

            data_atual = config.data_inicial
            while data_atual <= config.data_final:
                periodo = data_atual.strftime("%Y-%m")

                apuracao = await self._request_com_retry(
                    self.sped_service.consultar_apuracao_ipi,
                    cnpj=cnpj,
                    periodo=periodo,
                )

                if apuracao:
                    yield {
                        "tipo": "apuracao_ipi",
                        "periodo_apuracao": periodo,
                        "valor_total_debitos": self._parse_decimal(apuracao.get("debitos")),
                        "valor_total_creditos": self._parse_decimal(apuracao.get("creditos")),
                        "saldo_credor_anterior": self._parse_decimal(apuracao.get("saldo_ant")),
                        "ipi_recolher": self._parse_decimal(apuracao.get("ipi_recolher")),
                        "saldo_credor_transportar": self._parse_decimal(apuracao.get("saldo_cred")),
                    }

                if data_atual.month == 12:
                    data_atual = date(data_atual.year + 1, 1, 1)
                else:
                    data_atual = date(data_atual.year, data_atual.month + 1, 1)

        except Exception as e:
            logger.error(f"[SPED Fiscal] Erro consultando apuracao IPI: {e}")

    async def _consultar_resumo_documentos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta resumo de documentos fiscais."""
        try:
            if not self.sped_service:
                return

            resumo = await self._request_com_retry(
                self.sped_service.consultar_resumo_documentos,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            if resumo:
                yield {
                    "tipo": "resumo_documentos",
                    "periodo_inicial": config.data_inicial.isoformat() if config.data_inicial else None,
                    "periodo_final": config.data_final.isoformat() if config.data_final else None,
                    "qtd_nfe_entrada": resumo.get("nfe_entrada", 0),
                    "qtd_nfe_saida": resumo.get("nfe_saida", 0),
                    "valor_total_entradas": self._parse_decimal(resumo.get("valor_entradas")),
                    "valor_total_saidas": self._parse_decimal(resumo.get("valor_saidas")),
                    "valor_icms_entradas": self._parse_decimal(resumo.get("icms_entradas")),
                    "valor_icms_saidas": self._parse_decimal(resumo.get("icms_saidas")),
                    "valor_ipi_entradas": self._parse_decimal(resumo.get("ipi_entradas")),
                    "valor_ipi_saidas": self._parse_decimal(resumo.get("ipi_saidas")),
                }

        except Exception as e:
            logger.error(f"[SPED Fiscal] Erro consultando resumo documentos: {e}")

    async def _processar_registro(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "escrituracao_efd":
            return await self._salvar_escrituracao(registro, config)
        elif tipo == "apuracao_icms":
            return await self._salvar_apuracao_icms(registro, config)
        elif tipo == "apuracao_ipi":
            return await self._salvar_apuracao_ipi(registro, config)
        elif tipo == "resumo_documentos":
            # Apenas log, nao persiste
            logger.info(
                f"[SPED Fiscal] Resumo: {registro.get('qtd_nfe_entrada')} entradas, "
                f"{registro.get('qtd_nfe_saida')} saidas"
            )
            return False

        return False

    async def _salvar_escrituracao(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva escrituracao SPED Fiscal."""
        from ..models.sync_models import EscrituracaoSPED

        recibo = registro.get("numero_recibo")

        existente = self.db.query(EscrituracaoSPED).filter(
            EscrituracaoSPED.numero_recibo == recibo
        ).first()

        if existente:
            existente.situacao = registro.get("situacao")
            existente.updated_at = datetime.utcnow()
            return False

        nova = EscrituracaoSPED(
            cnpj_empresa=config.cnpj_empresa,
            tipo_sped="EFD",
            numero_recibo=recibo,
            periodo_apuracao=registro.get("periodo_apuracao"),
            data_inicial=registro.get("data_inicial"),
            data_final=registro.get("data_final"),
            perfil=registro.get("perfil"),
            descricao_perfil=registro.get("descricao_perfil"),
            data_transmissao=registro.get("data_transmissao"),
            situacao=registro.get("situacao"),
            finalidade=registro.get("finalidade"),
            hash_arquivo=registro.get("hash_arquivo"),
            retificadora=registro.get("retificadora", False),
            recibo_retificado=registro.get("recibo_retificado"),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_apuracao_icms(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva apuracao ICMS."""
        from ..models.sync_models import ApuracaoICMS

        periodo = registro.get("periodo_apuracao")

        existente = self.db.query(ApuracaoICMS).filter(
            ApuracaoICMS.cnpj_empresa == config.cnpj_empresa,
            ApuracaoICMS.periodo_apuracao == periodo,
        ).first()

        if existente:
            existente.icms_recolher = Decimal(str(registro.get("icms_recolher") or 0))
            existente.saldo_credor_transportar = Decimal(str(registro.get("saldo_credor_transportar") or 0))
            existente.updated_at = datetime.utcnow()
            return False

        nova = ApuracaoICMS(
            cnpj_empresa=config.cnpj_empresa,
            periodo_apuracao=periodo,
            valor_total_debitos=Decimal(str(registro.get("valor_total_debitos") or 0)),
            valor_ajustes_debitos=Decimal(str(registro.get("valor_ajustes_debitos") or 0)),
            valor_total_creditos=Decimal(str(registro.get("valor_total_creditos") or 0)),
            valor_ajustes_creditos=Decimal(str(registro.get("valor_ajustes_creditos") or 0)),
            saldo_credor_anterior=Decimal(str(registro.get("saldo_credor_anterior") or 0)),
            valor_total_deducoes=Decimal(str(registro.get("valor_total_deducoes") or 0)),
            icms_recolher=Decimal(str(registro.get("icms_recolher") or 0)),
            saldo_credor_transportar=Decimal(str(registro.get("saldo_credor_transportar") or 0)),
            icms_st_recolher=Decimal(str(registro.get("icms_st_recolher") or 0)),
            difal_recolher=Decimal(str(registro.get("difal_recolher") or 0)),
            fcp_recolher=Decimal(str(registro.get("fcp_recolher") or 0)),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_apuracao_ipi(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva apuracao IPI."""
        from ..models.sync_models import ApuracaoIPI

        periodo = registro.get("periodo_apuracao")

        existente = self.db.query(ApuracaoIPI).filter(
            ApuracaoIPI.cnpj_empresa == config.cnpj_empresa,
            ApuracaoIPI.periodo_apuracao == periodo,
        ).first()

        if existente:
            existente.ipi_recolher = Decimal(str(registro.get("ipi_recolher") or 0))
            existente.saldo_credor_transportar = Decimal(str(registro.get("saldo_credor_transportar") or 0))
            existente.updated_at = datetime.utcnow()
            return False

        nova = ApuracaoIPI(
            cnpj_empresa=config.cnpj_empresa,
            periodo_apuracao=periodo,
            valor_total_debitos=Decimal(str(registro.get("valor_total_debitos") or 0)),
            valor_total_creditos=Decimal(str(registro.get("valor_total_creditos") or 0)),
            saldo_credor_anterior=Decimal(str(registro.get("saldo_credor_anterior") or 0)),
            ipi_recolher=Decimal(str(registro.get("ipi_recolher") or 0)),
            saldo_credor_transportar=Decimal(str(registro.get("saldo_credor_transportar") or 0)),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> Optional[datetime]:
        """Obtem ultima sincronizacao do SPED Fiscal."""
        from ..models.sync_models import SyncLog, StatusSincronizacao

        ultimo = self.db.query(SyncLog).filter(
            SyncLog.cnpj_empresa == cnpj,
            SyncLog.servico == self.SERVICO_NOME,
            SyncLog.status == StatusSincronizacao.SUCESSO,
        ).order_by(SyncLog.fim_execucao.desc()).first()

        return ultimo.fim_execucao if ultimo else None

    async def obter_resumo(self, cnpj: str) -> Dict[str, Any]:
        """Obtem resumo dos dados SPED Fiscal."""
        from ..models.sync_models import EscrituracaoSPED, ApuracaoICMS
        from sqlalchemy import func

        escrituracoes = self.db.query(EscrituracaoSPED).filter(
            EscrituracaoSPED.cnpj_empresa == cnpj,
            EscrituracaoSPED.tipo_sped == "EFD",
        ).count()

        ultima_apuracao = self.db.query(ApuracaoICMS).filter(
            ApuracaoICMS.cnpj_empresa == cnpj,
        ).order_by(ApuracaoICMS.periodo_apuracao.desc()).first()

        return {
            "total_escrituracoes": escrituracoes,
            "ultimo_periodo_apurado": ultima_apuracao.periodo_apuracao if ultima_apuracao else None,
            "icms_ultimo_periodo": float(ultima_apuracao.icms_recolher) if ultima_apuracao else 0,
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
