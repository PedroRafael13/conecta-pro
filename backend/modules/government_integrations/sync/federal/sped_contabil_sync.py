"""
Sincronizador do SPED Contabil (ECD).

Extrai e sincroniza:
- Escrituracoes transmitidas
- Livros contabeis
- Plano de contas
- Balancetes
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, AsyncGenerator
from decimal import Decimal

from ..base_sync import BaseSynchronizer, SyncConfig, SyncResult

logger = logging.getLogger(__name__)


class SPEDContabilSynchronizer(BaseSynchronizer):
    """Sincronizador de dados do SPED Contabil (ECD)."""

    SERVICO_NOME = "sped_contabil"
    INTERVALO_PADRAO = 1440 * 7  # Semanal
    DIAS_RETROATIVOS_PADRAO = 365

    # Tipos de livro
    TIPOS_LIVRO = {
        "G": "Livro Diario Geral",
        "R": "Livro Diario com Escrituracao Resumida",
        "A": "Livro Diario Auxiliar",
        "Z": "Livro Razao Auxiliar",
        "B": "Livro Balancetes Diarios e Balanco",
    }

    def __init__(self, db_session, certificate_manager=None, sped_service=None):
        super().__init__(db_session, certificate_manager)
        self.sped_service = sped_service

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extrai dados do SPED Contabil.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados extraidos
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(f"[SPED Contabil] Extraindo dados - CNPJ: {cnpj}")

        # 1. Escrituracoes transmitidas
        async for escrituracao in self._consultar_escrituracoes(cnpj, config):
            yield escrituracao

        # 2. Plano de contas
        async for conta in self._consultar_plano_contas(cnpj, config):
            yield conta

        # 3. Saldos contabeis
        async for saldo in self._consultar_saldos(cnpj, config):
            yield saldo

    async def _consultar_escrituracoes(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta escrituracoes SPED Contabil transmitidas."""
        try:
            if not self.sped_service:
                logger.warning("[SPED Contabil] Service nao configurado")
                return

            escrituracoes = await self._request_com_retry(
                self.sped_service.consultar_escrituracoes_contabeis,
                cnpj=cnpj,
                ano_inicial=config.data_inicial.year if config.data_inicial else None,
                ano_final=config.data_final.year if config.data_final else None,
            )

            for esc in escrituracoes or []:
                yield {
                    "tipo": "escrituracao_ecd",
                    "numero_recibo": esc.get("recibo"),
                    "ano_calendario": esc.get("ano"),
                    "data_inicial": self._parse_data(esc.get("data_inicial")),
                    "data_final": self._parse_data(esc.get("data_final")),
                    "tipo_livro": esc.get("tipo_livro"),
                    "descricao_livro": self.TIPOS_LIVRO.get(
                        esc.get("tipo_livro"), "Livro Diario"
                    ),
                    "data_transmissao": self._parse_data(esc.get("data_transmissao")),
                    "situacao": esc.get("situacao"),
                    "hash_arquivo": esc.get("hash"),
                    "substituta": esc.get("substituta", False),
                    "recibo_substituido": esc.get("recibo_substituido"),
                }

        except Exception as e:
            logger.error(f"[SPED Contabil] Erro consultando escrituracoes: {e}")
            raise

    async def _consultar_plano_contas(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta plano de contas do SPED."""
        try:
            if not self.sped_service:
                return

            plano = await self._request_com_retry(
                self.sped_service.consultar_plano_contas,
                cnpj=cnpj,
                ano=config.data_final.year if config.data_final else date.today().year,
            )

            for conta in plano or []:
                yield {
                    "tipo": "conta_contabil",
                    "codigo_conta": conta.get("codigo"),
                    "descricao": conta.get("descricao"),
                    "tipo_conta": conta.get("tipo"),
                    "natureza": conta.get("natureza"),
                    "nivel": conta.get("nivel"),
                    "codigo_superior": conta.get("codigo_superior"),
                    "codigo_referencial": conta.get("codigo_referencial"),
                    "ano_referencia": conta.get("ano"),
                }

        except Exception as e:
            logger.error(f"[SPED Contabil] Erro consultando plano de contas: {e}")

    async def _consultar_saldos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta saldos contabeis."""
        try:
            if not self.sped_service:
                return

            saldos = await self._request_com_retry(
                self.sped_service.consultar_saldos_contabeis,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for saldo in saldos or []:
                yield {
                    "tipo": "saldo_contabil",
                    "codigo_conta": saldo.get("conta"),
                    "periodo": saldo.get("periodo"),
                    "saldo_inicial_debito": self._parse_decimal(saldo.get("sd_ini_deb")),
                    "saldo_inicial_credito": self._parse_decimal(saldo.get("sd_ini_cred")),
                    "movimento_debito": self._parse_decimal(saldo.get("mov_deb")),
                    "movimento_credito": self._parse_decimal(saldo.get("mov_cred")),
                    "saldo_final_debito": self._parse_decimal(saldo.get("sd_fin_deb")),
                    "saldo_final_credito": self._parse_decimal(saldo.get("sd_fin_cred")),
                }

        except Exception as e:
            logger.error(f"[SPED Contabil] Erro consultando saldos: {e}")

    async def _processar_registro(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "escrituracao_ecd":
            return await self._salvar_escrituracao(registro, config)
        elif tipo == "conta_contabil":
            return await self._salvar_conta(registro, config)
        elif tipo == "saldo_contabil":
            return await self._salvar_saldo(registro, config)

        return False

    async def _salvar_escrituracao(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva escrituracao SPED Contabil."""
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
            tipo_sped="ECD",
            numero_recibo=recibo,
            ano_calendario=registro.get("ano_calendario"),
            data_inicial=registro.get("data_inicial"),
            data_final=registro.get("data_final"),
            tipo_livro=registro.get("tipo_livro"),
            descricao_livro=registro.get("descricao_livro"),
            data_transmissao=registro.get("data_transmissao"),
            situacao=registro.get("situacao"),
            hash_arquivo=registro.get("hash_arquivo"),
            substituta=registro.get("substituta", False),
            recibo_substituido=registro.get("recibo_substituido"),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_conta(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva conta do plano de contas."""
        from ..models.sync_models import ContaContabil

        codigo = registro.get("codigo_conta")
        ano = registro.get("ano_referencia")

        existente = self.db.query(ContaContabil).filter(
            ContaContabil.cnpj_empresa == config.cnpj_empresa,
            ContaContabil.codigo_conta == codigo,
            ContaContabil.ano_referencia == ano,
        ).first()

        if existente:
            existente.descricao = registro.get("descricao")
            existente.updated_at = datetime.utcnow()
            return False

        nova = ContaContabil(
            cnpj_empresa=config.cnpj_empresa,
            codigo_conta=codigo,
            descricao=registro.get("descricao"),
            tipo_conta=registro.get("tipo_conta"),
            natureza=registro.get("natureza"),
            nivel=registro.get("nivel"),
            codigo_superior=registro.get("codigo_superior"),
            codigo_referencial=registro.get("codigo_referencial"),
            ano_referencia=ano,
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_saldo(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva saldo contabil."""
        from ..models.sync_models import SaldoContabil

        codigo = registro.get("codigo_conta")
        periodo = registro.get("periodo")

        existente = self.db.query(SaldoContabil).filter(
            SaldoContabil.cnpj_empresa == config.cnpj_empresa,
            SaldoContabil.codigo_conta == codigo,
            SaldoContabil.periodo == periodo,
        ).first()

        if existente:
            existente.saldo_final_debito = Decimal(str(registro.get("saldo_final_debito") or 0))
            existente.saldo_final_credito = Decimal(str(registro.get("saldo_final_credito") or 0))
            existente.updated_at = datetime.utcnow()
            return False

        novo = SaldoContabil(
            cnpj_empresa=config.cnpj_empresa,
            codigo_conta=codigo,
            periodo=periodo,
            saldo_inicial_debito=Decimal(str(registro.get("saldo_inicial_debito") or 0)),
            saldo_inicial_credito=Decimal(str(registro.get("saldo_inicial_credito") or 0)),
            movimento_debito=Decimal(str(registro.get("movimento_debito") or 0)),
            movimento_credito=Decimal(str(registro.get("movimento_credito") or 0)),
            saldo_final_debito=Decimal(str(registro.get("saldo_final_debito") or 0)),
            saldo_final_credito=Decimal(str(registro.get("saldo_final_credito") or 0)),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> Optional[datetime]:
        """Obtem ultima sincronizacao do SPED Contabil."""
        from ..models.sync_models import SyncLog, StatusSincronizacao

        ultimo = self.db.query(SyncLog).filter(
            SyncLog.cnpj_empresa == cnpj,
            SyncLog.servico == self.SERVICO_NOME,
            SyncLog.status == StatusSincronizacao.SUCESSO,
        ).order_by(SyncLog.fim_execucao.desc()).first()

        return ultimo.fim_execucao if ultimo else None

    async def obter_resumo(self, cnpj: str) -> Dict[str, Any]:
        """Obtem resumo dos dados SPED Contabil."""
        from ..models.sync_models import EscrituracaoSPED

        escrituracoes = self.db.query(EscrituracaoSPED).filter(
            EscrituracaoSPED.cnpj_empresa == cnpj,
            EscrituracaoSPED.tipo_sped == "ECD",
        ).order_by(EscrituracaoSPED.ano_calendario.desc()).all()

        return {
            "total_escrituracoes": len(escrituracoes),
            "ultima_escrituracao": escrituracoes[0].ano_calendario if escrituracoes else None,
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
