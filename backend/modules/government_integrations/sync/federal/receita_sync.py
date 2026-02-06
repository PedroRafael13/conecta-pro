"""
Sincronizador de dados da Receita Federal / e-CAC.

Extrai e sincroniza:
- Dados cadastrais de empresas (CNPJ)
- Situacao cadastral
- Certidoes (CND, CNDT)
- Guias de impostos (DARF)
- Simples Nacional
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List, AsyncGenerator
from decimal import Decimal

from ..base_sync import BaseSynchronizer, SyncConfig, SyncResult

logger = logging.getLogger(__name__)


class ReceitaFederalSynchronizer(BaseSynchronizer):
    """Sincronizador de dados da Receita Federal."""

    SERVICO_NOME = "receita_federal"
    INTERVALO_PADRAO = 1440  # 24 horas
    DIAS_RETROATIVOS_PADRAO = 90

    def __init__(
        self,
        db_session,
        certificate_manager=None,
        receita_service=None,
        ecac_service=None,
    ):
        super().__init__(db_session, certificate_manager)
        self.receita_service = receita_service
        self.ecac_service = ecac_service

    async def _extrair_dados(
        self,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Extrai dados da Receita Federal.

        Args:
            config: Configuracao da sincronizacao

        Yields:
            Dict com dados extraidos
        """
        cnpj = self._normalizar_cnpj(config.cnpj_empresa)

        logger.info(f"[Receita] Extraindo dados - CNPJ: {cnpj}")

        # 1. Dados cadastrais da empresa
        async for dados in self._consultar_dados_cadastrais(cnpj):
            yield dados

        # 2. Situacao fiscal
        async for situacao in self._consultar_situacao_fiscal(cnpj):
            yield situacao

        # 3. Certidoes
        async for certidao in self._consultar_certidoes(cnpj):
            yield certidao

        # 4. Simples Nacional
        async for simples in self._consultar_simples_nacional(cnpj):
            yield simples

        # 5. Guias/DARFs (se disponivel)
        async for guia in self._consultar_guias(cnpj, config):
            yield guia

    async def _consultar_dados_cadastrais(
        self,
        cnpj: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta dados cadastrais do CNPJ."""
        try:
            if not self.receita_service:
                logger.warning("[Receita] Service nao configurado")
                return

            # Consultar CNPJ
            dados = await self._request_com_retry(
                self.receita_service.consultar_cnpj,
                cnpj=cnpj,
            )

            if dados:
                yield {
                    "tipo": "dados_cadastrais",
                    "cnpj": cnpj,
                    "razao_social": dados.get("razao_social"),
                    "nome_fantasia": dados.get("nome_fantasia"),
                    "situacao_cadastral": dados.get("situacao"),
                    "data_situacao_cadastral": self._parse_data(dados.get("data_situacao")),
                    "motivo_situacao": dados.get("motivo_situacao"),
                    "codigo_natureza_juridica": dados.get("natureza_juridica", {}).get("codigo"),
                    "natureza_juridica": dados.get("natureza_juridica", {}).get("descricao"),
                    "cnae_principal": dados.get("atividade_principal", [{}])[0].get("codigo") if dados.get("atividade_principal") else None,
                    "cnae_principal_descricao": dados.get("atividade_principal", [{}])[0].get("descricao") if dados.get("atividade_principal") else None,
                    "cnaes_secundarios": dados.get("atividades_secundarias", []),
                    "logradouro": dados.get("logradouro"),
                    "numero": dados.get("numero"),
                    "complemento": dados.get("complemento"),
                    "bairro": dados.get("bairro"),
                    "cep": dados.get("cep"),
                    "municipio": dados.get("municipio"),
                    "uf": dados.get("uf"),
                    "telefone": dados.get("telefone"),
                    "email": dados.get("email"),
                    "capital_social": self._parse_decimal(dados.get("capital_social")),
                    "porte": dados.get("porte"),
                    "data_abertura": self._parse_data(dados.get("abertura")),
                    "quadro_societario": dados.get("qsa", []),
                }

        except Exception as e:
            logger.error(f"[Receita] Erro consultando dados cadastrais: {e}")
            raise

    async def _consultar_situacao_fiscal(
        self,
        cnpj: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta situacao fiscal no e-CAC."""
        try:
            if not self.ecac_service:
                return

            situacao = await self._request_com_retry(
                self.ecac_service.consultar_situacao_fiscal,
                cnpj=cnpj,
            )

            if situacao:
                yield {
                    "tipo": "situacao_fiscal",
                    "cnpj": cnpj,
                    "situacao": situacao.get("situacao"),
                    "pendencias": situacao.get("pendencias", []),
                    "debitos": situacao.get("debitos", []),
                    "data_consulta": datetime.utcnow(),
                }

        except Exception as e:
            logger.error(f"[Receita] Erro consultando situacao fiscal: {e}")

    async def _consultar_certidoes(
        self,
        cnpj: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta e baixa certidoes."""
        try:
            if not self.ecac_service:
                return

            # Tipos de certidoes
            tipos_certidao = [
                ("cnd_federal", "CND Federal"),
                ("cndt", "CNDT Trabalhista"),
                ("crf_fgts", "CRF FGTS"),
            ]

            for tipo_codigo, tipo_nome in tipos_certidao:
                try:
                    certidao = await self._request_com_retry(
                        self.ecac_service.emitir_certidao,
                        cnpj=cnpj,
                        tipo=tipo_codigo,
                    )

                    if certidao:
                        yield {
                            "tipo": "certidao",
                            "cnpj": cnpj,
                            "tipo_certidao": tipo_codigo,
                            "orgao_emissor": tipo_nome,
                            "data_emissao": self._parse_data(certidao.get("data_emissao")) or datetime.utcnow(),
                            "data_validade": self._parse_data(certidao.get("data_validade")),
                            "situacao": certidao.get("situacao"),
                            "codigo_controle": certidao.get("codigo_controle"),
                            "pdf_certidao": certidao.get("pdf"),
                        }

                except Exception as e:
                    logger.warning(f"[Receita] Erro obtendo certidao {tipo_codigo}: {e}")

        except Exception as e:
            logger.error(f"[Receita] Erro consultando certidoes: {e}")

    async def _consultar_simples_nacional(
        self,
        cnpj: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta situacao no Simples Nacional."""
        try:
            if not self.receita_service:
                return

            simples = await self._request_com_retry(
                self.receita_service.consultar_simples_nacional,
                cnpj=cnpj,
            )

            if simples:
                yield {
                    "tipo": "simples_nacional",
                    "cnpj": cnpj,
                    "optante_simples": simples.get("optante"),
                    "data_opcao_simples": self._parse_data(simples.get("data_opcao")),
                    "data_exclusao_simples": self._parse_data(simples.get("data_exclusao")),
                    "optante_mei": simples.get("mei"),
                }

        except Exception as e:
            logger.error(f"[Receita] Erro consultando Simples Nacional: {e}")

    async def _consultar_guias(
        self,
        cnpj: str,
        config: SyncConfig,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Consulta guias/DARFs no e-CAC."""
        try:
            if not self.ecac_service:
                return

            guias = await self._request_com_retry(
                self.ecac_service.listar_guias,
                cnpj=cnpj,
                data_inicial=config.data_inicial,
                data_final=config.data_final,
            )

            for guia in guias or []:
                yield {
                    "tipo": "guia_darf",
                    "cnpj": cnpj,
                    "tipo_guia": "darf",
                    "codigo_receita": guia.get("codigo_receita"),
                    "numero_guia": guia.get("numero"),
                    "competencia": guia.get("periodo"),
                    "data_vencimento": self._parse_data(guia.get("vencimento")),
                    "data_pagamento": self._parse_data(guia.get("data_pagamento")),
                    "valor_principal": self._parse_decimal(guia.get("valor_principal")),
                    "valor_juros": self._parse_decimal(guia.get("juros")),
                    "valor_multa": self._parse_decimal(guia.get("multa")),
                    "valor_total": self._parse_decimal(guia.get("valor_total")),
                    "status": "paga" if guia.get("data_pagamento") else "gerada",
                    "linha_digitavel": guia.get("linha_digitavel"),
                    "codigo_barras": guia.get("codigo_barras"),
                    "pdf_guia": guia.get("pdf"),
                }

        except Exception as e:
            logger.error(f"[Receita] Erro consultando guias: {e}")

    async def _processar_registro(
        self,
        registro: Dict[str, Any],
        config: SyncConfig,
    ) -> bool:
        """Processa registro extraido."""
        tipo = registro.get("tipo")

        if tipo == "dados_cadastrais":
            return await self._salvar_dados_cadastrais(registro)
        elif tipo == "simples_nacional":
            return await self._atualizar_simples(registro)
        elif tipo == "certidao":
            return await self._salvar_certidao(registro)
        elif tipo == "guia_darf":
            return await self._salvar_guia(registro)
        elif tipo == "situacao_fiscal":
            # Apenas log, nao persiste
            logger.info(f"[Receita] Situacao fiscal: {registro.get('situacao')}")
            return False

        return False

    async def _salvar_dados_cadastrais(self, registro: Dict[str, Any]) -> bool:
        """Salva dados cadastrais da empresa."""
        from ..models.sync_models import DadosCadastraisEmpresa

        cnpj = registro.get("cnpj")
        if not cnpj:
            return False

        existente = self.db.query(DadosCadastraisEmpresa).filter(
            DadosCadastraisEmpresa.cnpj == cnpj
        ).first()

        if existente:
            # Atualizar
            for key, value in registro.items():
                if key != "tipo" and hasattr(existente, key):
                    setattr(existente, key, value)
            existente.data_ultima_atualizacao = datetime.utcnow()
            existente.updated_at = datetime.utcnow()
            return False
        else:
            # Criar novo
            novo = DadosCadastraisEmpresa(
                cnpj=cnpj,
                razao_social=registro.get("razao_social", ""),
                nome_fantasia=registro.get("nome_fantasia"),
                situacao_cadastral=registro.get("situacao_cadastral"),
                data_situacao_cadastral=registro.get("data_situacao_cadastral"),
                motivo_situacao=registro.get("motivo_situacao"),
                codigo_natureza_juridica=registro.get("codigo_natureza_juridica"),
                natureza_juridica=registro.get("natureza_juridica"),
                cnae_principal=registro.get("cnae_principal"),
                cnae_principal_descricao=registro.get("cnae_principal_descricao"),
                cnaes_secundarios=registro.get("cnaes_secundarios"),
                logradouro=registro.get("logradouro"),
                numero=registro.get("numero"),
                complemento=registro.get("complemento"),
                bairro=registro.get("bairro"),
                cep=registro.get("cep"),
                municipio=registro.get("municipio"),
                uf=registro.get("uf"),
                telefone=registro.get("telefone"),
                email=registro.get("email"),
                capital_social=Decimal(str(registro.get("capital_social") or 0)),
                porte=registro.get("porte"),
                data_abertura=registro.get("data_abertura"),
                quadro_societario=registro.get("quadro_societario"),
                data_ultima_atualizacao=datetime.utcnow(),
                sync_id=self._current_sync_id,
            )
            self.db.add(novo)
            return True

    async def _atualizar_simples(self, registro: Dict[str, Any]) -> bool:
        """Atualiza informacoes do Simples Nacional."""
        from ..models.sync_models import DadosCadastraisEmpresa

        cnpj = registro.get("cnpj")
        empresa = self.db.query(DadosCadastraisEmpresa).filter(
            DadosCadastraisEmpresa.cnpj == cnpj
        ).first()

        if empresa:
            empresa.optante_simples = registro.get("optante_simples")
            empresa.data_opcao_simples = registro.get("data_opcao_simples")
            empresa.data_exclusao_simples = registro.get("data_exclusao_simples")
            empresa.optante_mei = registro.get("optante_mei")
            empresa.updated_at = datetime.utcnow()
            return False

        return False

    async def _salvar_certidao(self, registro: Dict[str, Any]) -> bool:
        """Salva certidao."""
        from ..models.sync_models import Certidao

        cnpj = registro.get("cnpj")
        tipo = registro.get("tipo_certidao")

        # Verificar se ja existe certidao valida
        existente = self.db.query(Certidao).filter(
            Certidao.cnpj_empresa == cnpj,
            Certidao.tipo_certidao == tipo,
            Certidao.data_validade >= date.today(),
        ).first()

        if existente:
            return False

        # Criar nova certidao
        nova = Certidao(
            cnpj_empresa=cnpj,
            tipo_certidao=tipo,
            orgao_emissor=registro.get("orgao_emissor"),
            data_emissao=registro.get("data_emissao") or datetime.utcnow(),
            data_validade=registro.get("data_validade") or (date.today() + timedelta(days=180)),
            situacao=registro.get("situacao"),
            codigo_controle=registro.get("codigo_controle"),
            pdf_certidao=registro.get("pdf_certidao"),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    async def _salvar_guia(self, registro: Dict[str, Any]) -> bool:
        """Salva guia de recolhimento."""
        from ..models.sync_models import GuiaRecolhimento, TipoGuia, StatusGuia

        numero = registro.get("numero_guia")
        cnpj = registro.get("cnpj")

        if numero:
            existente = self.db.query(GuiaRecolhimento).filter(
                GuiaRecolhimento.numero_guia == numero,
                GuiaRecolhimento.cnpj_empresa == cnpj,
            ).first()

            if existente:
                # Atualizar status se foi paga
                if registro.get("status") == "paga" and existente.status != StatusGuia.PAGA:
                    existente.status = StatusGuia.PAGA
                    existente.data_pagamento = registro.get("data_pagamento")
                return False

        # Criar nova guia
        nova = GuiaRecolhimento(
            cnpj_empresa=cnpj,
            tipo_guia=TipoGuia.DARF,
            codigo_receita=registro.get("codigo_receita"),
            numero_guia=numero,
            competencia=registro.get("competencia") or date.today().strftime("%Y-%m"),
            data_vencimento=registro.get("data_vencimento") or date.today(),
            data_pagamento=registro.get("data_pagamento"),
            valor_principal=Decimal(str(registro.get("valor_principal") or 0)),
            valor_juros=Decimal(str(registro.get("valor_juros") or 0)),
            valor_multa=Decimal(str(registro.get("valor_multa") or 0)),
            valor_total=Decimal(str(registro.get("valor_total") or 0)),
            status=StatusGuia.PAGA if registro.get("status") == "paga" else StatusGuia.GERADA,
            linha_digitavel=registro.get("linha_digitavel"),
            codigo_barras=registro.get("codigo_barras"),
            pdf_guia=registro.get("pdf_guia"),
            sync_id=self._current_sync_id,
        )
        self.db.add(nova)
        return True

    def _obter_ultima_sincronizacao(self, cnpj: str) -> Optional[datetime]:
        """Obtem ultima sincronizacao."""
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

    async def consultar_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """
        Consulta dados de um CNPJ especifico.

        Args:
            cnpj: CNPJ a consultar

        Returns:
            Dict com dados cadastrais
        """
        config = SyncConfig(
            cnpj_empresa=cnpj,
            servico=self.SERVICO_NOME,
            tipo_sync="completa",
        )

        result = await self.sincronizar(config)

        if result.sucesso:
            from ..models.sync_models import DadosCadastraisEmpresa
            empresa = self.db.query(DadosCadastraisEmpresa).filter(
                DadosCadastraisEmpresa.cnpj == cnpj
            ).first()

            if empresa:
                return {
                    "cnpj": empresa.cnpj,
                    "razao_social": empresa.razao_social,
                    "nome_fantasia": empresa.nome_fantasia,
                    "situacao": empresa.situacao_cadastral,
                    "endereco": {
                        "logradouro": empresa.logradouro,
                        "numero": empresa.numero,
                        "bairro": empresa.bairro,
                        "municipio": empresa.municipio,
                        "uf": empresa.uf,
                        "cep": empresa.cep,
                    },
                    "optante_simples": empresa.optante_simples,
                }

        return {}

    async def obter_certidoes_validas(self, cnpj: str) -> List[Dict[str, Any]]:
        """Obtem certidoes validas da empresa."""
        from ..models.sync_models import Certidao

        certidoes = self.db.query(Certidao).filter(
            Certidao.cnpj_empresa == cnpj,
            Certidao.data_validade >= date.today(),
        ).all()

        return [
            {
                "tipo": c.tipo_certidao,
                "data_emissao": c.data_emissao.isoformat() if c.data_emissao else None,
                "data_validade": c.data_validade.isoformat() if c.data_validade else None,
                "situacao": c.situacao,
                "codigo_controle": c.codigo_controle,
            }
            for c in certidoes
        ]

    async def obter_resumo(self, cnpj: str) -> Dict[str, Any]:
        """Obtem resumo dos dados da Receita."""
        from ..models.sync_models import (
            DadosCadastraisEmpresa, Certidao, GuiaRecolhimento
        )

        empresa = self.db.query(DadosCadastraisEmpresa).filter(
            DadosCadastraisEmpresa.cnpj == cnpj
        ).first()

        certidoes_validas = self.db.query(Certidao).filter(
            Certidao.cnpj_empresa == cnpj,
            Certidao.data_validade >= date.today(),
        ).count()

        guias_pendentes = self.db.query(GuiaRecolhimento).filter(
            GuiaRecolhimento.cnpj_empresa == cnpj,
            GuiaRecolhimento.status == "gerada",
            GuiaRecolhimento.data_vencimento >= date.today(),
        ).count()

        return {
            "dados_cadastrais": empresa is not None,
            "situacao_cadastral": empresa.situacao_cadastral if empresa else None,
            "optante_simples": empresa.optante_simples if empresa else None,
            "certidoes_validas": certidoes_validas,
            "guias_pendentes": guias_pendentes,
            "ultima_sincronizacao": self._obter_ultima_sincronizacao(cnpj),
        }
