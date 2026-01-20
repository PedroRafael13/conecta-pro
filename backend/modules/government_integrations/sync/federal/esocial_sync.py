"""
Sincronizador de eventos eSocial.

Extrai e sincroniza:
- Eventos enviados (S-1200, S-2200, etc)
- Status de processamento
- Recibos
- Totalizadores
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List, AsyncGenerator
from decimal import Decimal

from ..base_sync import BaseSynchronizer, SyncConfig, SyncResult

logger = logging.getLogger(__name__)


class ESocialSynchronizer(BaseSynchronizer):
    """Sincronizador de dados do eSocial."""

    SERVICO_NOME = "esocial"
    INTERVALO_PADRAO = 60  # 1 hora
    DIAS_RETROATIVOS_PADRAO = 30

    # Tipos de eventos suportados
    TIPOS_EVENTOS = [
        "S-1000",  # Empregador/Contribuinte
        "S-1005",  # Tabela Estabelecimentos
        "S-1010",  # Tabela Rubricas
        "S-1200",  # Remuneracao
        "S-1210",  # Pagamentos
        "S-1260",  # Comercializacao Producao Rural
        "S-1270",  # Contratacao Trabalhadores Avulsos
        "S-1280",  # Informacoes Complementares
        "S-1298",  # Reabertura Eventos Periodicos
        "S-1299",  # Fechamento Eventos Periodicos
        "S-2190",  # Registro Preliminar
        "S-2200",  # Cadastramento Inicial / Admissao
        "S-2205",  # Alteracao Dados Cadastrais
        "S-2206",  # Alteracao Contrato
        "S-2210",  # CAT
        "S-2220",  # Monitoramento Saude
        "S-2230",  # Afastamento
        "S-2240",  # Condicoes Ambientais
        "S-2299",  # Desligamento
        "S-2300",  # TSV Inicio
        "S-2306",  # TSV Alteracao
        "S-2399",  # TSV Termino
        "S-2400",  # CDP
        "S-3000",  # Exclusao
        "S-5001",  # Totalizador Contribuicoes
        "S-5002",  # Totalizador IRRF
        "S-5003",  # Totalizador FGTS
        "S-5011",  # Totalizador Eventos Periodicos
        "S-5012",  # Totalizador IRRF Consolidado
        "S-5013",  # Totalizador FGTS Consolidado
    ]

    def __init__(self, db_session, certificate_manager=None, esocial_transmitter=None):
        super().__init__(db_session, certificate_manager)
        self.esocial_transmitter = esocial_transmitter

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extrai eventos eSocial do webservice.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados de cada evento
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(
            f"[eSocial] Extraindo eventos - CNPJ: {cnpj}, "
            f"Periodo: {config.data_inicial} a {config.data_final}"
        )

        # 1. Consultar eventos enviados
        async for evento in self._consultar_eventos_enviados(cnpj, config):
            yield evento

        # 2. Consultar totalizadores
        async for totalizador in self._consultar_totalizadores(cnpj, config):
            yield totalizador

        # 3. Atualizar status de eventos pendentes
        async for status in self._atualizar_status_pendentes(cnpj):
            yield status

    async def _consultar_eventos_enviados(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta eventos enviados."""
        try:
            if not self.esocial_transmitter:
                logger.warning("[eSocial] Transmitter nao configurado")
                return

            # Consultar eventos por periodo
            eventos = await self._request_com_retry(
                self.esocial_transmitter.consultar_eventos,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for evento in eventos:
                yield {
                    "tipo": "evento",
                    "id": evento.get("id_evento"),
                    "tipo_evento": evento.get("tipo"),
                    "data": self._parse_data(evento.get("data_evento")),
                    "cpf_funcionario": evento.get("cpf"),
                    "matricula": evento.get("matricula"),
                    "periodo_apuracao": evento.get("periodo"),
                    "status": evento.get("status"),
                    "protocolo": evento.get("protocolo"),
                    "recibo": evento.get("recibo"),
                    "dados": evento.get("dados", {}),
                    "xml_envio": evento.get("xml"),
                }

        except Exception as e:
            logger.error(f"[eSocial] Erro consultando eventos: {e}")
            raise

    async def _consultar_totalizadores(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta totalizadores S-5001, S-5003, etc."""
        try:
            if not self.esocial_transmitter:
                return

            # Gerar periodos mensais
            data_atual = config.data_inicial
            while data_atual <= config.data_final:
                periodo = data_atual.strftime("%Y-%m")

                totalizadores = await self._request_com_retry(
                    self.esocial_transmitter.consultar_totalizadores,
                    cnpj=cnpj,
                    periodo=periodo,
                )

                for tot in totalizadores:
                    yield {
                        "tipo": "totalizador",
                        "id": f"{cnpj}_{periodo}_{tot.get('tipo')}",
                        "tipo_evento": tot.get("tipo"),
                        "periodo_apuracao": periodo,
                        "data": data_atual,
                        "dados": tot.get("valores", {}),
                    }

                # Proximo mes
                if data_atual.month == 12:
                    data_atual = date(data_atual.year + 1, 1, 1)
                else:
                    data_atual = date(data_atual.year, data_atual.month + 1, 1)

        except Exception as e:
            logger.error(f"[eSocial] Erro consultando totalizadores: {e}")

    async def _atualizar_status_pendentes(
        self,
        cnpj: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Atualiza status de eventos pendentes no banco."""
        try:
            # Buscar eventos pendentes no banco local
            eventos_pendentes = await self._buscar_eventos_pendentes(cnpj)

            for evento in eventos_pendentes:
                protocolo = evento.get("protocolo")
                if not protocolo:
                    continue

                # Consultar status no webservice
                status = await self._request_com_retry(
                    self.esocial_transmitter.consultar_protocolo,
                    protocolo=protocolo,
                )

                yield {
                    "tipo": "atualizacao_status",
                    "id": evento.get("id"),
                    "status": status.get("status"),
                    "recibo": status.get("recibo"),
                    "mensagem_erro": status.get("erro"),
                    "data": datetime.utcnow(),
                }

        except Exception as e:
            logger.error(f"[eSocial] Erro atualizando status: {e}")

    async def _buscar_eventos_pendentes(self, cnpj: str) -> List[Dict]:
        """Busca eventos pendentes no banco local."""
        # Implementacao depende do modelo real
        return []

    async def _processar_registro(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """
        Processa registro extraido.

        Args:
            registro: Dados do registro
            config: Configuracao

        Returns:
            True se registro novo, False se atualizado
        """
        tipo = registro.get("tipo")

        if tipo == "evento":
            return await self._salvar_evento(registro, config)
        elif tipo == "totalizador":
            return await self._salvar_totalizador(registro, config)
        elif tipo == "atualizacao_status":
            return await self._atualizar_evento(registro)

        return False

    async def _salvar_evento(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva ou atualiza evento no banco."""
        from ..models.sync_models import EventoESocial, TipoEventoESocial, StatusEventoESocial

        id_evento = registro.get("id")

        # Verificar se existe
        existente = self.db.query(EventoESocial).filter(
            EventoESocial.id_evento == id_evento
        ).first()

        # Mapear status
        status_map = {
            "aceito": StatusEventoESocial.ACEITO,
            "rejeitado": StatusEventoESocial.REJEITADO,
            "pendente": StatusEventoESocial.PENDENTE,
            "processando": StatusEventoESocial.PROCESSANDO,
        }

        if existente:
            # Atualizar
            existente.status = status_map.get(
                registro.get("status", "pendente"),
                StatusEventoESocial.PENDENTE
            )
            existente.recibo = registro.get("recibo")
            existente.data_processamento = datetime.utcnow()
            existente.updated_at = datetime.utcnow()
            return False
        else:
            # Criar novo
            tipo_evento = registro.get("tipo_evento", "S-2200")
            try:
                tipo_enum = TipoEventoESocial(tipo_evento)
            except ValueError:
                tipo_enum = TipoEventoESocial.S2200

            novo = EventoESocial(
                cnpj_empresa=config.cnpj_empresa,
                tipo_evento=tipo_enum,
                id_evento=id_evento,
                cpf_funcionario=registro.get("cpf_funcionario"),
                matricula=registro.get("matricula"),
                periodo_apuracao=registro.get("periodo_apuracao"),
                data_evento=registro.get("data") or date.today(),
                status=status_map.get(
                    registro.get("status", "pendente"),
                    StatusEventoESocial.PENDENTE
                ),
                protocolo_envio=registro.get("protocolo"),
                recibo=registro.get("recibo"),
                dados_evento=registro.get("dados", {}),
                xml_envio=registro.get("xml_envio"),
                sync_id=self._current_sync_id,
            )
            self.db.add(novo)
            return True

    async def _salvar_totalizador(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva totalizador no banco."""
        # Totalizadores sao armazenados como eventos especiais
        return await self._salvar_evento({
            **registro,
            "tipo": "evento",
        }, config)

    async def _atualizar_evento(self, registro: Dict[str, Any]) -> bool:
        """Atualiza status de evento existente."""
        from ..models.sync_models import EventoESocial, StatusEventoESocial

        evento = self.db.query(EventoESocial).filter(
            EventoESocial.id == registro.get("id")
        ).first()

        if evento:
            status_map = {
                "aceito": StatusEventoESocial.ACEITO,
                "rejeitado": StatusEventoESocial.REJEITADO,
            }
            evento.status = status_map.get(
                registro.get("status"),
                evento.status
            )
            evento.recibo = registro.get("recibo") or evento.recibo
            evento.mensagem_erro = registro.get("mensagem_erro")
            evento.data_processamento = datetime.utcnow()
            return False

        return False

    def _obter_ultima_sincronizacao(self, cnpj: str) -> Optional[datetime]:
        """Obtem ultima sincronizacao do eSocial."""
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

    async def sincronizar_funcionario(
        self,
        cnpj: str,
        cpf: str,
    ) -> SyncResult:
        """
        Sincroniza eventos de um funcionario especifico.

        Args:
            cnpj: CNPJ da empresa
            cpf: CPF do funcionario

        Returns:
            SyncResult
        """
        config = SyncConfig(
            cnpj_empresa=cnpj,
            servico=self.SERVICO_NOME,
            tipo_sync="completa",
            parametros_extras={"cpf_funcionario": cpf},
        )
        return await self.sincronizar(config)

    async def sincronizar_periodo(
        self,
        cnpj: str,
        periodo: str,
    ) -> SyncResult:
        """
        Sincroniza eventos de um periodo especifico (YYYY-MM).

        Args:
            cnpj: CNPJ da empresa
            periodo: Periodo no formato YYYY-MM

        Returns:
            SyncResult
        """
        ano, mes = periodo.split("-")
        data_inicial = date(int(ano), int(mes), 1)

        if int(mes) == 12:
            data_final = date(int(ano) + 1, 1, 1) - timedelta(days=1)
        else:
            data_final = date(int(ano), int(mes) + 1, 1) - timedelta(days=1)

        config = SyncConfig(
            cnpj_empresa=cnpj,
            servico=self.SERVICO_NOME,
            tipo_sync="completa",
            data_inicial=data_inicial,
            data_final=data_final,
        )
        return await self.sincronizar(config)

    async def obter_resumo(self, cnpj: str) -> Dict[str, Any]:
        """
        Obtem resumo dos eventos sincronizados.

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Dict com resumo
        """
        from ..models.sync_models import EventoESocial, StatusEventoESocial
        from sqlalchemy import func

        # Contar por status
        por_status = self.db.query(
            EventoESocial.status,
            func.count(EventoESocial.id)
        ).filter(
            EventoESocial.cnpj_empresa == cnpj
        ).group_by(EventoESocial.status).all()

        # Contar por tipo
        por_tipo = self.db.query(
            EventoESocial.tipo_evento,
            func.count(EventoESocial.id)
        ).filter(
            EventoESocial.cnpj_empresa == cnpj
        ).group_by(EventoESocial.tipo_evento).all()

        return {
            "total_eventos": sum(c for _, c in por_status),
            "por_status": {str(s.value): c for s, c in por_status},
            "por_tipo": {str(t.value): c for t, c in por_tipo},
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
