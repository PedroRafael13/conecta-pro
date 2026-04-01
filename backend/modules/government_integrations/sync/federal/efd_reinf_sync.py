"""
Sincronizador da EFD-Reinf.

Extrai e sincroniza:
- Eventos R-1000 a R-9015
- Retencoes na fonte
- Contribuicoes previdenciarias
- Producao rural
"""

import logging
from collections.abc import AsyncGenerator
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class EFDReinfSynchronizer(BaseSynchronizer):
    """Sincronizador de dados da EFD-Reinf."""

    SERVICO_NOME = "efd_reinf"
    INTERVALO_PADRAO = 60  # 1 hora
    DIAS_RETROATIVOS_PADRAO = 30

    # Tipos de eventos EFD-Reinf
    TIPOS_EVENTOS = {
        "R-1000": "Informacoes do Contribuinte",
        "R-1050": "Tabela de Entidades Ligadas",
        "R-1070": "Tabela de Processos Administrativos/Judiciais",
        "R-2010": "Retencao Contribuicao Previdenciaria - Servicos Tomados",
        "R-2020": "Retencao Contribuicao Previdenciaria - Servicos Prestados",
        "R-2030": "Recursos Recebidos por Associacao Desportiva",
        "R-2040": "Recursos Repassados para Associacao Desportiva",
        "R-2050": "Comercializacao da Producao por Produtor Rural PJ/Agroind",
        "R-2055": "Aquisicao de Producao Rural",
        "R-2060": "Contribuicao Previdenciaria sobre a Receita Bruta - CPRB",
        "R-2098": "Reabertura dos Eventos Periodicos",
        "R-2099": "Fechamento dos Eventos Periodicos",
        "R-3010": "Receita de Espetaculos Desportivos",
        "R-4010": "Pagamentos/Creditos a Beneficiario Pessoa Fisica",
        "R-4020": "Pagamentos/Creditos a Beneficiario Pessoa Juridica",
        "R-4040": "Pagamentos/Creditos a Beneficiarios Nao Identificados",
        "R-4080": "Retencao no Recebimento",
        "R-4099": "Fechamento/Reabertura dos Eventos da Serie R-4000",
        "R-9001": "Bases e Tributos - Contribuicao Previdenciaria",
        "R-9005": "Bases e Tributos - Retencoes na Fonte",
        "R-9011": "Consolidacao de Bases e Tributos - Contrib Prev",
        "R-9015": "Consolidacao de Bases e Tributos - Retencoes na Fonte",
    }

    def __init__(self, db_session, certificate_manager=None, reinf_transmitter=None):
        super().__init__(db_session, certificate_manager)
        self.reinf_transmitter = reinf_transmitter

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai dados da EFD-Reinf.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados extraidos
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(f"[EFD-Reinf] Extraindo dados - CNPJ: {cnpj}, Periodo: {config.data_inicial} a {config.data_final}")

        # 1. Eventos enviados
        async for evento in self._consultar_eventos_enviados(cnpj, config):
            yield evento

        # 2. Totalizadores
        async for totalizador in self._consultar_totalizadores(cnpj, config):
            yield totalizador

        # 3. Retencoes na fonte
        async for retencao in self._consultar_retencoes(cnpj, config):
            yield retencao

    async def _consultar_eventos_enviados(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta eventos EFD-Reinf enviados."""
        try:
            if not self.reinf_transmitter:
                logger.warning("[EFD-Reinf] Transmitter nao configurado")
                return

            eventos = await self._request_com_retry(
                self.reinf_transmitter.consultar_eventos,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for evento in eventos or []:
                yield {
                    "tipo": "evento_reinf",
                    "id_evento": evento.get("id"),
                    "tipo_evento": evento.get("tipo"),
                    "descricao_evento": self.TIPOS_EVENTOS.get(evento.get("tipo"), evento.get("descricao")),
                    "periodo_apuracao": evento.get("periodo"),
                    "data_envio": self._parse_data(evento.get("data_envio")),
                    "status": evento.get("status"),
                    "protocolo": evento.get("protocolo"),
                    "recibo": evento.get("recibo"),
                    "dados_evento": evento.get("dados", {}),
                    "xml_envio": evento.get("xml"),
                }

        except Exception as e:
            logger.error(f"[EFD-Reinf] Erro consultando eventos: {e}")
            raise

    async def _consultar_totalizadores(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta totalizadores R-9001, R-9005, etc."""
        try:
            if not self.reinf_transmitter:
                return

            data_atual = config.data_inicial
            while data_atual <= config.data_final:
                periodo = data_atual.strftime("%Y-%m")

                totalizadores = await self._request_com_retry(
                    self.reinf_transmitter.consultar_totalizadores,
                    cnpj=cnpj,
                    periodo=periodo,
                )

                for tot in totalizadores or []:
                    yield {
                        "tipo": "totalizador_reinf",
                        "tipo_evento": tot.get("tipo"),
                        "periodo_apuracao": periodo,
                        "base_calculo_cp": self._parse_decimal(tot.get("base_cp")),
                        "valor_cp_patronal": self._parse_decimal(tot.get("cp_patronal")),
                        "valor_cp_descontada": self._parse_decimal(tot.get("cp_descontada")),
                        "valor_cprb": self._parse_decimal(tot.get("cprb")),
                        "base_calculo_ir": self._parse_decimal(tot.get("base_ir")),
                        "valor_ir_retido": self._parse_decimal(tot.get("ir_retido")),
                        "valor_csll_retido": self._parse_decimal(tot.get("csll_retido")),
                        "valor_cofins_retido": self._parse_decimal(tot.get("cofins_retido")),
                        "valor_pis_retido": self._parse_decimal(tot.get("pis_retido")),
                        "dados_completos": tot.get("dados", {}),
                    }

                if data_atual.month == 12:
                    data_atual = date(data_atual.year + 1, 1, 1)
                else:
                    data_atual = date(data_atual.year, data_atual.month + 1, 1)

        except Exception as e:
            logger.error(f"[EFD-Reinf] Erro consultando totalizadores: {e}")

    async def _consultar_retencoes(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta retencoes na fonte."""
        try:
            if not self.reinf_transmitter:
                return

            retencoes = await self._request_com_retry(
                self.reinf_transmitter.consultar_retencoes,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for ret in retencoes or []:
                yield {
                    "tipo": "retencao_reinf",
                    "tipo_retencao": ret.get("tipo"),
                    "cnpj_prestador": ret.get("cnpj_prestador"),
                    "cnpj_tomador": ret.get("cnpj_tomador"),
                    "periodo_apuracao": ret.get("periodo"),
                    "data_pagamento": self._parse_data(ret.get("data_pagamento")),
                    "valor_bruto": self._parse_decimal(ret.get("valor_bruto")),
                    "base_retencao": self._parse_decimal(ret.get("base_retencao")),
                    "valor_retencao_cp": self._parse_decimal(ret.get("retencao_cp")),
                    "valor_retencao_ir": self._parse_decimal(ret.get("retencao_ir")),
                    "valor_retencao_csll": self._parse_decimal(ret.get("retencao_csll")),
                    "valor_retencao_cofins": self._parse_decimal(ret.get("retencao_cofins")),
                    "valor_retencao_pis": self._parse_decimal(ret.get("retencao_pis")),
                    "numero_nf": ret.get("numero_nf"),
                    "serie_nf": ret.get("serie_nf"),
                }

        except Exception as e:
            logger.error(f"[EFD-Reinf] Erro consultando retencoes: {e}")

    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "evento_reinf":
            return await self._salvar_evento(registro, config)
        elif tipo == "totalizador_reinf":
            return await self._salvar_totalizador(registro, config)
        elif tipo == "retencao_reinf":
            return await self._salvar_retencao(registro, config)

        return False

    async def _salvar_evento(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva evento EFD-Reinf."""
        from ..models.sync_models import EventoReinf, StatusEventoReinf

        id_evento = registro.get("id_evento")

        existente = self.db.query(EventoReinf).filter(EventoReinf.id_evento == id_evento).first()

        status_map = {
            "aceito": StatusEventoReinf.ACEITO,
            "rejeitado": StatusEventoReinf.REJEITADO,
            "pendente": StatusEventoReinf.PENDENTE,
        }

        if existente:
            existente.status = status_map.get(registro.get("status"), existente.status)
            existente.recibo = registro.get("recibo") or existente.recibo
            existente.updated_at = datetime.utcnow()
            return False

        novo = EventoReinf(
            cnpj_empresa=config.cnpj_empresa,
            id_evento=id_evento,
            tipo_evento=registro.get("tipo_evento"),
            descricao_evento=registro.get("descricao_evento"),
            periodo_apuracao=registro.get("periodo_apuracao"),
            data_envio=registro.get("data_envio") or datetime.utcnow(),
            status=status_map.get(registro.get("status"), StatusEventoReinf.PENDENTE),
            protocolo=registro.get("protocolo"),
            recibo=registro.get("recibo"),
            dados_evento=registro.get("dados_evento"),
            xml_envio=registro.get("xml_envio"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_totalizador(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva totalizador EFD-Reinf."""
        from ..models.sync_models import TotalizadorReinf

        periodo = registro.get("periodo_apuracao")
        tipo = registro.get("tipo_evento")

        existente = (
            self.db.query(TotalizadorReinf)
            .filter(
                TotalizadorReinf.cnpj_empresa == config.cnpj_empresa,
                TotalizadorReinf.periodo_apuracao == periodo,
                TotalizadorReinf.tipo_evento == tipo,
            )
            .first()
        )

        if existente:
            existente.base_calculo_cp = Decimal(str(registro.get("base_calculo_cp") or 0))
            existente.valor_cp_patronal = Decimal(str(registro.get("valor_cp_patronal") or 0))
            existente.updated_at = datetime.utcnow()
            return False

        novo = TotalizadorReinf(
            cnpj_empresa=config.cnpj_empresa,
            tipo_evento=tipo,
            periodo_apuracao=periodo,
            base_calculo_cp=Decimal(str(registro.get("base_calculo_cp") or 0)),
            valor_cp_patronal=Decimal(str(registro.get("valor_cp_patronal") or 0)),
            valor_cp_descontada=Decimal(str(registro.get("valor_cp_descontada") or 0)),
            valor_cprb=Decimal(str(registro.get("valor_cprb") or 0)),
            base_calculo_ir=Decimal(str(registro.get("base_calculo_ir") or 0)),
            valor_ir_retido=Decimal(str(registro.get("valor_ir_retido") or 0)),
            valor_csll_retido=Decimal(str(registro.get("valor_csll_retido") or 0)),
            valor_cofins_retido=Decimal(str(registro.get("valor_cofins_retido") or 0)),
            valor_pis_retido=Decimal(str(registro.get("valor_pis_retido") or 0)),
            dados_completos=registro.get("dados_completos"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_retencao(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva retencao na fonte."""
        from ..models.sync_models import RetencaoReinf

        cnpj_prestador = registro.get("cnpj_prestador")
        numero_nf = registro.get("numero_nf")
        periodo = registro.get("periodo_apuracao")

        existente = (
            self.db.query(RetencaoReinf)
            .filter(
                RetencaoReinf.cnpj_empresa == config.cnpj_empresa,
                RetencaoReinf.cnpj_prestador == cnpj_prestador,
                RetencaoReinf.numero_nf == numero_nf,
                RetencaoReinf.periodo_apuracao == periodo,
            )
            .first()
        )

        if existente:
            return False

        novo = RetencaoReinf(
            cnpj_empresa=config.cnpj_empresa,
            tipo_retencao=registro.get("tipo_retencao"),
            cnpj_prestador=cnpj_prestador,
            cnpj_tomador=registro.get("cnpj_tomador"),
            periodo_apuracao=periodo,
            data_pagamento=registro.get("data_pagamento"),
            valor_bruto=Decimal(str(registro.get("valor_bruto") or 0)),
            base_retencao=Decimal(str(registro.get("base_retencao") or 0)),
            valor_retencao_cp=Decimal(str(registro.get("valor_retencao_cp") or 0)),
            valor_retencao_ir=Decimal(str(registro.get("valor_retencao_ir") or 0)),
            valor_retencao_csll=Decimal(str(registro.get("valor_retencao_csll") or 0)),
            valor_retencao_cofins=Decimal(str(registro.get("valor_retencao_cofins") or 0)),
            valor_retencao_pis=Decimal(str(registro.get("valor_retencao_pis") or 0)),
            numero_nf=numero_nf,
            serie_nf=registro.get("serie_nf"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtem ultima sincronizacao da EFD-Reinf."""
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
        """Obtem resumo dos dados EFD-Reinf."""
        from sqlalchemy import func

        from ..models.sync_models import EventoReinf

        total_eventos = self.db.query(EventoReinf).filter(EventoReinf.cnpj_empresa == cnpj).count()

        por_tipo = (
            self.db.query(EventoReinf.tipo_evento, func.count(EventoReinf.id))
            .filter(EventoReinf.cnpj_empresa == cnpj)
            .group_by(EventoReinf.tipo_evento)
            .all()
        )

        return {
            "total_eventos": total_eventos,
            "por_tipo": dict(por_tipo),
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
