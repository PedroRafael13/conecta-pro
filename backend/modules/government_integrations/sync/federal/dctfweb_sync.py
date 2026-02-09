"""
Sincronizador da DCTFWeb.

Extrai e sincroniza:
- Declaracoes transmitidas
- Debitos declarados
- Creditos vinculados
- Situacao fiscal
"""

import logging
from collections.abc import AsyncGenerator
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class DCTFWebSynchronizer(BaseSynchronizer):
    """Sincronizador de dados da DCTFWeb."""

    SERVICO_NOME = "dctfweb"
    INTERVALO_PADRAO = 1440  # 24 horas
    DIAS_RETROATIVOS_PADRAO = 365

    # Tipos de DCTFWeb
    TIPOS_DCTFWEB = {
        "1": "Mensal",
        "2": "Anual (13o Salario)",
        "3": "Diaria (Espetaculo Desportivo)",
    }

    # Codigos de receita principais
    CODIGOS_RECEITA = {
        "1082": "Contribuicao Previdenciaria - CP",
        "1138": "Contribuicao Terceiros",
        "1141": "RAT Ajustado",
        "5856": "CPRB",
        "5952": "Retencao Lei 9.711",
        "2985": "IRRF - Rendimentos do Trabalho",
        "2063": "IRRF - Rendimentos de Residentes no Exterior",
    }

    def __init__(self, db_session, certificate_manager=None, dctfweb_service=None):
        super().__init__(db_session, certificate_manager)
        self.dctfweb_service = dctfweb_service

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai dados da DCTFWeb.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados extraidos
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(f"[DCTFWeb] Extraindo dados - CNPJ: {cnpj}, Periodo: {config.data_inicial} a {config.data_final}")

        # 1. Declaracoes transmitidas
        async for declaracao in self._consultar_declaracoes(cnpj, config):
            yield declaracao

        # 2. Debitos apurados
        async for debito in self._consultar_debitos(cnpj, config):
            yield debito

        # 3. Creditos vinculados
        async for credito in self._consultar_creditos(cnpj, config):
            yield credito

        # 4. DARFs gerados
        async for darf in self._consultar_darfs(cnpj, config):
            yield darf

    async def _consultar_declaracoes(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta declaracoes DCTFWeb transmitidas."""
        try:
            if not self.dctfweb_service:
                logger.warning("[DCTFWeb] Service nao configurado")
                return

            declaracoes = await self._request_com_retry(
                self.dctfweb_service.consultar_declaracoes,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for decl in declaracoes or []:
                yield {
                    "tipo": "declaracao_dctfweb",
                    "numero_recibo": decl.get("recibo"),
                    "tipo_declaracao": decl.get("tipo"),
                    "descricao_tipo": self.TIPOS_DCTFWEB.get(decl.get("tipo"), "Mensal"),
                    "periodo_apuracao": decl.get("periodo"),
                    "data_transmissao": self._parse_data(decl.get("data_transmissao")),
                    "situacao": decl.get("situacao"),
                    "retificadora": decl.get("retificadora", False),
                    "numero_recibo_retificada": decl.get("recibo_retificada"),
                    "valor_total_debitos": self._parse_decimal(decl.get("total_debitos")),
                    "valor_total_creditos": self._parse_decimal(decl.get("total_creditos")),
                    "valor_total_pagar": self._parse_decimal(decl.get("total_pagar")),
                }

        except Exception as e:
            logger.error(f"[DCTFWeb] Erro consultando declaracoes: {e}")
            raise

    async def _consultar_debitos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta debitos apurados na DCTFWeb."""
        try:
            if not self.dctfweb_service:
                return

            data_atual = config.data_inicial
            while data_atual <= config.data_final:
                periodo = data_atual.strftime("%Y-%m")

                debitos = await self._request_com_retry(
                    self.dctfweb_service.consultar_debitos,
                    cnpj=cnpj,
                    periodo=periodo,
                )

                for deb in debitos or []:
                    yield {
                        "tipo": "debito_dctfweb",
                        "periodo_apuracao": periodo,
                        "codigo_receita": deb.get("codigo"),
                        "descricao_receita": self.CODIGOS_RECEITA.get(deb.get("codigo"), deb.get("descricao")),
                        "valor_principal": self._parse_decimal(deb.get("principal")),
                        "valor_multa": self._parse_decimal(deb.get("multa")),
                        "valor_juros": self._parse_decimal(deb.get("juros")),
                        "valor_total": self._parse_decimal(deb.get("total")),
                        "data_vencimento": self._parse_data(deb.get("vencimento")),
                        "situacao": deb.get("situacao"),
                        "suspenso": deb.get("suspenso", False),
                        "processo_suspensao": deb.get("processo"),
                    }

                if data_atual.month == 12:
                    data_atual = date(data_atual.year + 1, 1, 1)
                else:
                    data_atual = date(data_atual.year, data_atual.month + 1, 1)

        except Exception as e:
            logger.error(f"[DCTFWeb] Erro consultando debitos: {e}")

    async def _consultar_creditos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta creditos vinculados."""
        try:
            if not self.dctfweb_service:
                return

            creditos = await self._request_com_retry(
                self.dctfweb_service.consultar_creditos,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for cred in creditos or []:
                yield {
                    "tipo": "credito_dctfweb",
                    "tipo_credito": cred.get("tipo"),
                    "origem": cred.get("origem"),
                    "periodo_apuracao": cred.get("periodo"),
                    "valor_original": self._parse_decimal(cred.get("valor_original")),
                    "valor_utilizado": self._parse_decimal(cred.get("valor_utilizado")),
                    "valor_disponivel": self._parse_decimal(cred.get("valor_disponivel")),
                    "data_vinculacao": self._parse_data(cred.get("data_vinculacao")),
                    "debito_vinculado": cred.get("debito_vinculado"),
                }

        except Exception as e:
            logger.error(f"[DCTFWeb] Erro consultando creditos: {e}")

    async def _consultar_darfs(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta DARFs gerados pela DCTFWeb."""
        try:
            if not self.dctfweb_service:
                return

            darfs = await self._request_com_retry(
                self.dctfweb_service.consultar_darfs,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for darf in darfs or []:
                yield {
                    "tipo": "darf_dctfweb",
                    "numero_documento": darf.get("numero"),
                    "periodo_apuracao": darf.get("periodo"),
                    "codigo_receita": darf.get("codigo_receita"),
                    "data_vencimento": self._parse_data(darf.get("vencimento")),
                    "data_pagamento": self._parse_data(darf.get("data_pagamento")),
                    "valor_principal": self._parse_decimal(darf.get("principal")),
                    "valor_multa": self._parse_decimal(darf.get("multa")),
                    "valor_juros": self._parse_decimal(darf.get("juros")),
                    "valor_total": self._parse_decimal(darf.get("total")),
                    "situacao": "pago" if darf.get("data_pagamento") else "pendente",
                    "codigo_barras": darf.get("codigo_barras"),
                    "linha_digitavel": darf.get("linha_digitavel"),
                }

        except Exception as e:
            logger.error(f"[DCTFWeb] Erro consultando DARFs: {e}")

    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "declaracao_dctfweb":
            return await self._salvar_declaracao(registro, config)
        elif tipo == "debito_dctfweb":
            return await self._salvar_debito(registro, config)
        elif tipo == "credito_dctfweb":
            return await self._salvar_credito(registro, config)
        elif tipo == "darf_dctfweb":
            return await self._salvar_darf(registro, config)

        return False

    async def _salvar_declaracao(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva declaracao DCTFWeb."""
        from ..models.sync_models import DeclaracaoDCTFWeb

        recibo = registro.get("numero_recibo")

        existente = self.db.query(DeclaracaoDCTFWeb).filter(DeclaracaoDCTFWeb.numero_recibo == recibo).first()

        if existente:
            existente.situacao = registro.get("situacao")
            existente.updated_at = datetime.utcnow()
            return False

        nova = DeclaracaoDCTFWeb(
            cnpj_empresa=config.cnpj_empresa,
            numero_recibo=recibo,
            tipo_declaracao=registro.get("tipo_declaracao"),
            descricao_tipo=registro.get("descricao_tipo"),
            periodo_apuracao=registro.get("periodo_apuracao"),
            data_transmissao=registro.get("data_transmissao") or datetime.utcnow(),
            situacao=registro.get("situacao"),
            retificadora=registro.get("retificadora", False),
            numero_recibo_retificada=registro.get("numero_recibo_retificada"),
            valor_total_debitos=Decimal(str(registro.get("valor_total_debitos") or 0)),
            valor_total_creditos=Decimal(str(registro.get("valor_total_creditos") or 0)),
            valor_total_pagar=Decimal(str(registro.get("valor_total_pagar") or 0)),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_debito(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva debito DCTFWeb."""
        from ..models.sync_models import DebitoDCTFWeb

        periodo = registro.get("periodo_apuracao")
        codigo = registro.get("codigo_receita")

        existente = (
            self.db.query(DebitoDCTFWeb)
            .filter(
                DebitoDCTFWeb.cnpj_empresa == config.cnpj_empresa,
                DebitoDCTFWeb.periodo_apuracao == periodo,
                DebitoDCTFWeb.codigo_receita == codigo,
            )
            .first()
        )

        if existente:
            existente.valor_total = Decimal(str(registro.get("valor_total") or 0))
            existente.situacao = registro.get("situacao")
            existente.updated_at = datetime.utcnow()
            return False

        novo = DebitoDCTFWeb(
            cnpj_empresa=config.cnpj_empresa,
            periodo_apuracao=periodo,
            codigo_receita=codigo,
            descricao_receita=registro.get("descricao_receita"),
            valor_principal=Decimal(str(registro.get("valor_principal") or 0)),
            valor_multa=Decimal(str(registro.get("valor_multa") or 0)),
            valor_juros=Decimal(str(registro.get("valor_juros") or 0)),
            valor_total=Decimal(str(registro.get("valor_total") or 0)),
            data_vencimento=registro.get("data_vencimento"),
            situacao=registro.get("situacao"),
            suspenso=registro.get("suspenso", False),
            processo_suspensao=registro.get("processo_suspensao"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_credito(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva credito vinculado."""
        from ..models.sync_models import CreditoDCTFWeb

        tipo = registro.get("tipo_credito")
        periodo = registro.get("periodo_apuracao")

        existente = (
            self.db.query(CreditoDCTFWeb)
            .filter(
                CreditoDCTFWeb.cnpj_empresa == config.cnpj_empresa,
                CreditoDCTFWeb.tipo_credito == tipo,
                CreditoDCTFWeb.periodo_apuracao == periodo,
            )
            .first()
        )

        if existente:
            existente.valor_utilizado = Decimal(str(registro.get("valor_utilizado") or 0))
            existente.valor_disponivel = Decimal(str(registro.get("valor_disponivel") or 0))
            existente.updated_at = datetime.utcnow()
            return False

        novo = CreditoDCTFWeb(
            cnpj_empresa=config.cnpj_empresa,
            tipo_credito=tipo,
            origem=registro.get("origem"),
            periodo_apuracao=periodo,
            valor_original=Decimal(str(registro.get("valor_original") or 0)),
            valor_utilizado=Decimal(str(registro.get("valor_utilizado") or 0)),
            valor_disponivel=Decimal(str(registro.get("valor_disponivel") or 0)),
            data_vinculacao=registro.get("data_vinculacao"),
            debito_vinculado=registro.get("debito_vinculado"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_darf(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva DARF gerado pela DCTFWeb."""
        from ..models.sync_models import GuiaRecolhimento, StatusGuia, TipoGuia

        numero = registro.get("numero_documento")

        existente = (
            self.db.query(GuiaRecolhimento)
            .filter(
                GuiaRecolhimento.numero_guia == numero,
                GuiaRecolhimento.cnpj_empresa == config.cnpj_empresa,
            )
            .first()
        )

        if existente:
            if registro.get("situacao") == "pago" and existente.status != StatusGuia.PAGA:
                existente.status = StatusGuia.PAGA
                existente.data_pagamento = registro.get("data_pagamento")
            return False

        nova = GuiaRecolhimento(
            cnpj_empresa=config.cnpj_empresa,
            tipo_guia=TipoGuia.DARF,
            codigo_receita=registro.get("codigo_receita"),
            numero_guia=numero,
            competencia=registro.get("periodo_apuracao"),
            data_vencimento=registro.get("data_vencimento") or date.today(),
            data_pagamento=registro.get("data_pagamento"),
            valor_principal=Decimal(str(registro.get("valor_principal") or 0)),
            valor_juros=Decimal(str(registro.get("valor_juros") or 0)),
            valor_multa=Decimal(str(registro.get("valor_multa") or 0)),
            valor_total=Decimal(str(registro.get("valor_total") or 0)),
            status=StatusGuia.PAGA if registro.get("situacao") == "pago" else StatusGuia.GERADA,
            linha_digitavel=registro.get("linha_digitavel"),
            codigo_barras=registro.get("codigo_barras"),
            dados_adicionais={"origem": "dctfweb"},
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtem ultima sincronizacao da DCTFWeb."""
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
        """Obtem resumo dos dados DCTFWeb."""
        from sqlalchemy import func

        from ..models.sync_models import DebitoDCTFWeb, DeclaracaoDCTFWeb

        total_declaracoes = self.db.query(DeclaracaoDCTFWeb).filter(DeclaracaoDCTFWeb.cnpj_empresa == cnpj).count()

        debitos_pendentes = (
            self.db.query(func.sum(DebitoDCTFWeb.valor_total))
            .filter(
                DebitoDCTFWeb.cnpj_empresa == cnpj,
                DebitoDCTFWeb.situacao != "pago",
            )
            .scalar()
        )

        return {
            "total_declaracoes": total_declaracoes,
            "debitos_pendentes": float(debitos_pendentes or 0),
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
