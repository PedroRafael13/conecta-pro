"""
Sincronizador do FGTS Digital.

Extrai e sincroniza:
- Guias de recolhimento FGTS
- Extratos de conta vinculada
- Eventos de movimentacao
- Debitos e parcelamentos
"""

import logging
from collections.abc import AsyncGenerator
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..base_sync import BaseSynchronizer, SyncConfig

logger = logging.getLogger(__name__)


class FGTSDigitalSynchronizer(BaseSynchronizer):
    """Sincronizador de dados do FGTS Digital."""

    SERVICO_NOME = "fgts_digital"
    INTERVALO_PADRAO = 1440  # 24 horas
    DIAS_RETROATIVOS_PADRAO = 90

    # URLs do FGTS Digital
    URL_PRODUCAO = "https://fgtsdigital.caixa.gov.br/empregador"
    URL_HOMOLOGACAO = "https://fgtsdigital-hom.caixa.gov.br/empregador"

    # Codigos de movimentacao
    CODIGOS_MOVIMENTACAO = {
        "01": "Admissao",
        "02": "Transferencia",
        "03": "Afastamento",
        "04": "Retorno Afastamento",
        "05": "Desligamento",
        "06": "Reintegracao",
    }

    def __init__(self, db_session, certificate_manager=None, fgts_service=None):
        super().__init__(db_session, certificate_manager)
        self.fgts_service = fgts_service

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Extrai dados do FGTS Digital.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados extraidos
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(
            f"[FGTS Digital] Extraindo dados - CNPJ: {cnpj}, Periodo: {config.data_inicial} a {config.data_final}"
        )

        # 1. Guias de recolhimento
        async for guia in self._consultar_guias_fgts(cnpj, config):
            yield guia

        # 2. Extratos de conta vinculada
        async for extrato in self._consultar_extratos(cnpj, config):
            yield extrato

        # 3. Debitos pendentes
        async for debito in self._consultar_debitos(cnpj):
            yield debito

        # 4. Movimentacoes de funcionarios
        async for movimentacao in self._consultar_movimentacoes(cnpj, config):
            yield movimentacao

    async def _consultar_guias_fgts(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta guias FGTS geradas."""
        try:
            if not self.fgts_service:
                logger.warning("[FGTS Digital] Service nao configurado")
                return

            guias = await self._request_com_retry(
                self.fgts_service.consultar_guias,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for guia in guias or []:
                yield {
                    "tipo": "guia_fgts",
                    "cnpj": cnpj,
                    "tipo_guia": guia.get("tipo", "mensal"),
                    "numero_guia": guia.get("numero"),
                    "competencia": guia.get("competencia"),
                    "data_vencimento": self._parse_data(guia.get("vencimento")),
                    "data_pagamento": self._parse_data(guia.get("data_pagamento")),
                    "valor_fgts": self._parse_decimal(guia.get("valor_fgts")),
                    "valor_multa_rescisoria": self._parse_decimal(guia.get("multa_rescisoria")),
                    "valor_contribuicao_social": self._parse_decimal(guia.get("contribuicao_social")),
                    "valor_juros": self._parse_decimal(guia.get("juros")),
                    "valor_multa": self._parse_decimal(guia.get("multa")),
                    "valor_total": self._parse_decimal(guia.get("valor_total")),
                    "qtd_funcionarios": guia.get("qtd_funcionarios"),
                    "status": "paga" if guia.get("data_pagamento") else "pendente",
                    "codigo_barras": guia.get("codigo_barras"),
                    "linha_digitavel": guia.get("linha_digitavel"),
                    "pix_copia_cola": guia.get("pix"),
                }

        except Exception as e:
            logger.error(f"[FGTS Digital] Erro consultando guias: {e}")
            raise

    async def _consultar_extratos(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta extratos de contas vinculadas."""
        try:
            if not self.fgts_service:
                return

            # Listar funcionarios com conta FGTS
            funcionarios = await self._request_com_retry(
                self.fgts_service.listar_contas_vinculadas,
                cnpj=cnpj,
            )

            for func in funcionarios or []:
                cpf = func.get("cpf")
                if not cpf:
                    continue

                # Consultar extrato individual
                extrato = await self._request_com_retry(
                    self.fgts_service.consultar_extrato,
                    cnpj=cnpj,
                    cpf=cpf,
                    data_inicial=config.data_inicial,
                    data_final=config.data_final,
                )

                if extrato:
                    yield {
                        "tipo": "extrato_fgts",
                        "cnpj": cnpj,
                        "cpf": cpf,
                        "nome_funcionario": func.get("nome"),
                        "pis": func.get("pis"),
                        "numero_conta": extrato.get("numero_conta"),
                        "data_abertura": self._parse_data(extrato.get("data_abertura")),
                        "saldo_anterior": self._parse_decimal(extrato.get("saldo_anterior")),
                        "depositos": self._parse_decimal(extrato.get("depositos")),
                        "saques": self._parse_decimal(extrato.get("saques")),
                        "juros_jam": self._parse_decimal(extrato.get("juros")),
                        "saldo_atual": self._parse_decimal(extrato.get("saldo_atual")),
                        "movimentacoes": extrato.get("movimentacoes", []),
                    }

        except Exception as e:
            logger.error(f"[FGTS Digital] Erro consultando extratos: {e}")

    async def _consultar_debitos(
        self,
        cnpj: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta debitos pendentes de FGTS."""
        try:
            if not self.fgts_service:
                return

            debitos = await self._request_com_retry(
                self.fgts_service.consultar_debitos,
                cnpj=cnpj,
            )

            for debito in debitos or []:
                yield {
                    "tipo": "debito_fgts",
                    "cnpj": cnpj,
                    "numero_debito": debito.get("numero"),
                    "competencia": debito.get("competencia"),
                    "origem": debito.get("origem"),
                    "valor_original": self._parse_decimal(debito.get("valor_original")),
                    "valor_atualizado": self._parse_decimal(debito.get("valor_atualizado")),
                    "data_vencimento": self._parse_data(debito.get("vencimento")),
                    "situacao": debito.get("situacao"),
                    "parcelado": debito.get("parcelado", False),
                    "numero_parcelamento": debito.get("numero_parcelamento"),
                }

        except Exception as e:
            logger.error(f"[FGTS Digital] Erro consultando debitos: {e}")

    async def _consultar_movimentacoes(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Consulta movimentacoes de funcionarios no FGTS."""
        try:
            if not self.fgts_service:
                return

            movimentacoes = await self._request_com_retry(
                self.fgts_service.consultar_movimentacoes,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for mov in movimentacoes or []:
                yield {
                    "tipo": "movimentacao_fgts",
                    "cnpj": cnpj,
                    "cpf": mov.get("cpf"),
                    "nome_funcionario": mov.get("nome"),
                    "tipo_movimentacao": mov.get("tipo"),
                    "codigo_movimentacao": mov.get("codigo"),
                    "descricao": self.CODIGOS_MOVIMENTACAO.get(mov.get("codigo"), mov.get("descricao")),
                    "data_movimentacao": self._parse_data(mov.get("data")),
                    "valor_base": self._parse_decimal(mov.get("valor_base")),
                    "valor_deposito": self._parse_decimal(mov.get("valor_deposito")),
                    "processado": mov.get("processado", False),
                }

        except Exception as e:
            logger.error(f"[FGTS Digital] Erro consultando movimentacoes: {e}")

    async def _processar_registro(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "guia_fgts":
            return await self._salvar_guia(registro, config)
        elif tipo == "extrato_fgts":
            return await self._salvar_extrato(registro, config)
        elif tipo == "debito_fgts":
            return await self._salvar_debito(registro, config)
        elif tipo == "movimentacao_fgts":
            return await self._salvar_movimentacao(registro, config)

        return False

    async def _salvar_guia(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva guia FGTS no banco."""
        from ..models.sync_models import GuiaRecolhimento, StatusGuia, TipoGuia

        numero = registro.get("numero_guia")
        cnpj = registro.get("cnpj")

        if numero:
            existente = (
                self.db.query(GuiaRecolhimento)
                .filter(
                    GuiaRecolhimento.numero_guia == numero,
                    GuiaRecolhimento.cnpj_empresa == cnpj,
                    GuiaRecolhimento.tipo_guia == TipoGuia.FGTS,
                )
                .first()
            )

            if existente:
                if registro.get("status") == "paga" and existente.status != StatusGuia.PAGA:
                    existente.status = StatusGuia.PAGA
                    existente.data_pagamento = registro.get("data_pagamento")
                return False

        nova = GuiaRecolhimento(
            cnpj_empresa=cnpj,
            tipo_guia=TipoGuia.FGTS,
            codigo_receita="FGTS",
            numero_guia=numero,
            competencia=registro.get("competencia") or date.today().strftime("%Y-%m"),
            data_vencimento=registro.get("data_vencimento") or date.today(),
            data_pagamento=registro.get("data_pagamento"),
            valor_principal=Decimal(str(registro.get("valor_fgts") or 0)),
            valor_juros=Decimal(str(registro.get("valor_juros") or 0)),
            valor_multa=Decimal(str(registro.get("valor_multa") or 0)),
            valor_total=Decimal(str(registro.get("valor_total") or 0)),
            status=StatusGuia.PAGA if registro.get("status") == "paga" else StatusGuia.GERADA,
            linha_digitavel=registro.get("linha_digitavel"),
            codigo_barras=registro.get("codigo_barras"),
            dados_adicionais={
                "valor_multa_rescisoria": str(registro.get("valor_multa_rescisoria") or 0),
                "valor_contribuicao_social": str(registro.get("valor_contribuicao_social") or 0),
                "qtd_funcionarios": registro.get("qtd_funcionarios"),
                "pix_copia_cola": registro.get("pix_copia_cola"),
            },
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_extrato(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva extrato FGTS."""
        from ..models.sync_models import ExtratoFGTS

        cpf = registro.get("cpf")
        cnpj = registro.get("cnpj")

        # Verificar se existe extrato recente
        existente = (
            self.db.query(ExtratoFGTS)
            .filter(
                ExtratoFGTS.cnpj_empresa == cnpj,
                ExtratoFGTS.cpf_funcionario == cpf,
            )
            .order_by(ExtratoFGTS.created_at.desc())
            .first()
        )

        if existente and existente.saldo_atual == registro.get("saldo_atual"):
            return False

        novo = ExtratoFGTS(
            cnpj_empresa=cnpj,
            cpf_funcionario=cpf,
            nome_funcionario=registro.get("nome_funcionario"),
            pis=registro.get("pis"),
            numero_conta=registro.get("numero_conta"),
            data_abertura=registro.get("data_abertura"),
            saldo_anterior=Decimal(str(registro.get("saldo_anterior") or 0)),
            depositos=Decimal(str(registro.get("depositos") or 0)),
            saques=Decimal(str(registro.get("saques") or 0)),
            juros_jam=Decimal(str(registro.get("juros_jam") or 0)),
            saldo_atual=Decimal(str(registro.get("saldo_atual") or 0)),
            movimentacoes=registro.get("movimentacoes"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_debito(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva debito FGTS."""
        from ..models.sync_models import DebitoFGTS

        numero = registro.get("numero_debito")
        cnpj = registro.get("cnpj")

        existente = (
            self.db.query(DebitoFGTS)
            .filter(
                DebitoFGTS.numero_debito == numero,
                DebitoFGTS.cnpj_empresa == cnpj,
            )
            .first()
        )

        if existente:
            existente.valor_atualizado = Decimal(str(registro.get("valor_atualizado") or 0))
            existente.situacao = registro.get("situacao")
            existente.updated_at = datetime.utcnow()
            return False

        novo = DebitoFGTS(
            cnpj_empresa=cnpj,
            numero_debito=numero,
            competencia=registro.get("competencia"),
            origem=registro.get("origem"),
            valor_original=Decimal(str(registro.get("valor_original") or 0)),
            valor_atualizado=Decimal(str(registro.get("valor_atualizado") or 0)),
            data_vencimento=registro.get("data_vencimento"),
            situacao=registro.get("situacao"),
            parcelado=registro.get("parcelado", False),
            numero_parcelamento=registro.get("numero_parcelamento"),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    async def _salvar_movimentacao(
        self,
        registro: dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Salva movimentacao FGTS."""
        from ..models.sync_models import MovimentacaoFGTS

        cnpj = registro.get("cnpj")
        cpf = registro.get("cpf")
        data = registro.get("data_movimentacao")
        tipo = registro.get("tipo_movimentacao")

        existente = (
            self.db.query(MovimentacaoFGTS)
            .filter(
                MovimentacaoFGTS.cnpj_empresa == cnpj,
                MovimentacaoFGTS.cpf_funcionario == cpf,
                MovimentacaoFGTS.data_movimentacao == data,
                MovimentacaoFGTS.tipo_movimentacao == tipo,
            )
            .first()
        )

        if existente:
            return False

        novo = MovimentacaoFGTS(
            cnpj_empresa=cnpj,
            cpf_funcionario=cpf,
            nome_funcionario=registro.get("nome_funcionario"),
            tipo_movimentacao=tipo,
            codigo_movimentacao=registro.get("codigo_movimentacao"),
            descricao=registro.get("descricao"),
            data_movimentacao=data,
            valor_base=Decimal(str(registro.get("valor_base") or 0)),
            valor_deposito=Decimal(str(registro.get("valor_deposito") or 0)),
            processado=registro.get("processado", False),
            sync_id=self._current_sync_id,
        )
        self.db.add(novo)
        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> datetime | None:
        """Obtem ultima sincronizacao do FGTS Digital."""
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
        """Obtem resumo dos dados FGTS."""
        from sqlalchemy import func

        from ..models.sync_models import GuiaRecolhimento, StatusGuia, TipoGuia

        guias_pendentes = (
            self.db.query(GuiaRecolhimento)
            .filter(
                GuiaRecolhimento.cnpj_empresa == cnpj,
                GuiaRecolhimento.tipo_guia == TipoGuia.FGTS,
                GuiaRecolhimento.status == StatusGuia.GERADA,
                GuiaRecolhimento.data_vencimento >= date.today(),
            )
            .count()
        )

        valor_pendente = (
            self.db.query(func.sum(GuiaRecolhimento.valor_total))
            .filter(
                GuiaRecolhimento.cnpj_empresa == cnpj,
                GuiaRecolhimento.tipo_guia == TipoGuia.FGTS,
                GuiaRecolhimento.status == StatusGuia.GERADA,
            )
            .scalar()
        )

        return {
            "guias_pendentes": guias_pendentes,
            "valor_pendente": float(valor_pendente or 0),
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
