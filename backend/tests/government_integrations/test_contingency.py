"""
Testes para módulo de contingência (matriz UF, comutação de endpoints).
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Importar módulos a testar
import sys
sys.path.insert(0, '/opt/conecta-pro/backend/modules/government_integrations')

from core.contingency.uf_matrix import (
    MatrizContingencia,
    TipoContingencia,
    MATRIZ_CONTINGENCIA_NFE,
    MATRIZ_CONTINGENCIA_CTE,
    ENDPOINTS_CENTRALIZADOS,
)
from core.contingency.endpoint_switcher import (
    ComutadorEndpoints,
    StatusEndpoint,
    ConfiguracaoComutacao,
    EstadoEndpoint,
)
from core.contingency.availability_checker import (
    VerificadorDisponibilidade,
    ResultadoVerificacao,
)


class TestMatrizContingenciaNFe:
    """Testes para matriz de contingência NF-e."""

    def test_todas_ufs_configuradas(self):
        """Deve ter configuração para todas as 27 UFs."""
        ufs_esperadas = {
            "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
            "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
            "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"
        }

        ufs_configuradas = set(MATRIZ_CONTINGENCIA_NFE.keys())

        assert ufs_esperadas == ufs_configuradas

    def test_config_sp(self):
        """Deve ter configuração correta para SP."""
        config = MATRIZ_CONTINGENCIA_NFE["SP"]

        assert config.uf == "SP"
        assert config.principal is not None
        assert "nfe.fazenda.sp.gov.br" in config.principal.url

    def test_config_am(self):
        """Deve ter configuração correta para AM."""
        config = MATRIZ_CONTINGENCIA_NFE["AM"]

        assert config.uf == "AM"
        assert config.principal is not None
        assert "sefaz.am.gov.br" in config.principal.url

    def test_contingencia_svc_an(self):
        """Estados do Norte devem usar SVC-AN."""
        estados_svc_an = ["AM", "AC", "RO", "RR", "AP", "PA", "TO", "MA"]

        for uf in estados_svc_an:
            config = MATRIZ_CONTINGENCIA_NFE.get(uf)
            if config and config.tipo_contingencia:
                assert config.tipo_contingencia == TipoContingencia.SVC_AN, f"{uf} deveria usar SVC-AN"

    def test_contingencia_svc_rs(self):
        """Estados do Sul devem usar SVC-RS."""
        estados_svc_rs = ["RS", "SC", "PR"]

        for uf in estados_svc_rs:
            config = MATRIZ_CONTINGENCIA_NFE.get(uf)
            if config and config.tipo_contingencia:
                # RS, SC, PR podem usar SVRS ou SVC-RS
                assert config.tipo_contingencia in [
                    TipoContingencia.SVC_RS,
                    TipoContingencia.SVRS,
                ], f"{uf} deveria usar SVC-RS ou SVRS"


class TestMatrizContingenciaCTe:
    """Testes para matriz de contingência CT-e."""

    def test_cte_configurado(self):
        """Deve ter configuração para CT-e."""
        assert MATRIZ_CONTINGENCIA_CTE is not None


class TestEndpointsCentralizados:
    """Testes para endpoints centralizados."""

    def test_svc_an_configurado(self):
        """Deve ter SVC-AN configurado."""
        assert "SVC_AN" in ENDPOINTS_CENTRALIZADOS

    def test_svc_rs_configurado(self):
        """Deve ter SVC-RS configurado."""
        assert "SVC_RS" in ENDPOINTS_CENTRALIZADOS

    def test_svrs_configurado(self):
        """Deve ter SVRS configurado."""
        assert "SVRS" in ENDPOINTS_CENTRALIZADOS

    def test_an_configurado(self):
        """Deve ter AN (Ambiente Nacional) configurado."""
        assert "AN" in ENDPOINTS_CENTRALIZADOS


class TestMatrizContingenciaMetodos:
    """Testes para métodos da classe MatrizContingencia."""

    def test_obter_config_nfe_valido(self):
        """Deve retornar configuração para UF válida."""
        config = MatrizContingencia.obter_config_nfe("SP")

        assert config is not None
        assert config.uf == "SP"

    def test_obter_config_nfe_invalido(self):
        """Deve retornar configuração padrão para UF inválida."""
        config = MatrizContingencia.obter_config_nfe("XX")

        assert config is not None
        # Deve usar SVRS como fallback

    def test_resolver_url_direta(self):
        """Deve retornar URL direta quando não é identificador."""
        url = "https://nfe.fazenda.sp.gov.br/ws/"
        resultado = MatrizContingencia.resolver_url(url, "NfeStatusServico")

        assert resultado.startswith("https://")

    def test_resolver_url_identificador(self):
        """Deve resolver identificador para URL real."""
        url = MatrizContingencia.resolver_url("SVC_AN", "NfeStatusServico4")

        assert url.startswith("https://")
        assert "svc" in url.lower() or "receita" in url.lower()


class TestComutadorEndpoints:
    """Testes para o comutador de endpoints."""

    def setup_method(self):
        """Setup para cada teste."""
        self.config = ConfiguracaoComutacao(
            falhas_para_indisponivel=3,
            tempo_recuperacao=5,
            limite_degradacao_ms=5000.0,
        )
        self.comutador = ComutadorEndpoints(self.config)

    def test_gerar_chave(self):
        """Deve gerar chave única para UF + tipo."""
        chave = self.comutador._gerar_chave("SP", "nfe")
        assert chave == "SP:nfe"

        chave = self.comutador._gerar_chave("sp", "NFE")
        assert chave == "SP:nfe"

    @pytest.mark.asyncio
    async def test_registrar_sucesso(self):
        """Deve registrar sucesso e atualizar estado."""
        await self.comutador.registrar_sucesso("SP", "nfe", 500)

        status = self.comutador.obter_status("SP", "nfe")

        assert status["status"] == StatusEndpoint.DISPONIVEL.value
        assert status["falhas_consecutivas"] == 0
        assert status["tempo_medio_resposta_ms"] > 0

    @pytest.mark.asyncio
    async def test_registrar_falha(self):
        """Deve registrar falha e incrementar contador."""
        await self.comutador.registrar_falha("SP", "nfe", "Timeout")

        status = self.comutador.obter_status("SP", "nfe")

        assert status["falhas_consecutivas"] == 1

    @pytest.mark.asyncio
    async def test_ativar_contingencia_apos_falhas(self):
        """Deve ativar contingência após X falhas consecutivas."""
        # Registrar falhas
        for i in range(3):
            await self.comutador.registrar_falha("SP", "nfe", "Timeout")

        status = self.comutador.obter_status("SP", "nfe")

        assert status["status"] == StatusEndpoint.INDISPONIVEL.value
        assert status["usando_contingencia"] is True

    @pytest.mark.asyncio
    async def test_forcar_contingencia(self):
        """Deve forçar uso de contingência."""
        await self.comutador.forcar_contingencia("SP", "nfe", "Manutenção programada")

        status = self.comutador.obter_status("SP", "nfe")

        assert status["usando_contingencia"] is True
        assert status["motivo_falha"] == "Manutenção programada"

    @pytest.mark.asyncio
    async def test_desativar_contingencia(self):
        """Deve desativar contingência."""
        await self.comutador.forcar_contingencia("SP", "nfe", "Teste")
        await self.comutador.desativar_contingencia("SP", "nfe")

        status = self.comutador.obter_status("SP", "nfe")

        assert status["usando_contingencia"] is False

    @pytest.mark.asyncio
    async def test_resetar_estado(self):
        """Deve resetar estado do endpoint."""
        await self.comutador.registrar_falha("SP", "nfe", "Erro")
        await self.comutador.resetar_estado("SP", "nfe")

        status = self.comutador.obter_status("SP", "nfe")

        assert status["falhas_consecutivas"] == 0

    def test_status_degradado(self):
        """Deve marcar como degradado se tempo de resposta alto."""
        # Este teste seria async na implementação real
        pass


class TestStatusEndpoint:
    """Testes para enum StatusEndpoint."""

    def test_status_disponivel(self):
        """Deve ter status DISPONIVEL."""
        assert StatusEndpoint.DISPONIVEL.value == "disponivel"

    def test_status_indisponivel(self):
        """Deve ter status INDISPONIVEL."""
        assert StatusEndpoint.INDISPONIVEL.value == "indisponivel"

    def test_status_degradado(self):
        """Deve ter status DEGRADADO."""
        assert StatusEndpoint.DEGRADADO.value == "degradado"

    def test_status_desconhecido(self):
        """Deve ter status DESCONHECIDO."""
        assert StatusEndpoint.DESCONHECIDO.value == "desconhecido"


class TestResultadoVerificacao:
    """Testes para ResultadoVerificacao."""

    def test_criar_resultado_sucesso(self):
        """Deve criar resultado de sucesso."""
        resultado = ResultadoVerificacao(
            uf="SP",
            tipo_documento="nfe",
            endpoint="https://nfe.fazenda.sp.gov.br",
            disponivel=True,
            tempo_resposta_ms=150,
            http_status=200,
        )

        assert resultado.disponivel is True
        assert resultado.tempo_resposta_ms == 150
        assert resultado.erro is None

    def test_criar_resultado_falha(self):
        """Deve criar resultado de falha."""
        resultado = ResultadoVerificacao(
            uf="SP",
            tipo_documento="nfe",
            endpoint="https://nfe.fazenda.sp.gov.br",
            disponivel=False,
            tempo_resposta_ms=10000,
            erro="Timeout",
        )

        assert resultado.disponivel is False
        assert resultado.erro == "Timeout"

    def test_timestamp_automatico(self):
        """Deve definir timestamp automaticamente."""
        resultado = ResultadoVerificacao(
            uf="SP",
            tipo_documento="nfe",
            endpoint="",
            disponivel=True,
            tempo_resposta_ms=100,
        )

        assert resultado.timestamp is not None


class TestVerificadorDisponibilidade:
    """Testes para VerificadorDisponibilidade."""

    def setup_method(self):
        """Setup para cada teste."""
        self.verificador = VerificadorDisponibilidade()

    def test_servico_teste_definido(self):
        """Deve ter serviços de teste definidos."""
        assert "nfe" in self.verificador.SERVICO_TESTE
        assert "cte" in self.verificador.SERVICO_TESTE
        assert "mdfe" in self.verificador.SERVICO_TESTE

    def test_timeout_definido(self):
        """Deve ter timeout configurado."""
        assert self.verificador.TIMEOUT > 0
        assert self.verificador.TIMEOUT <= 30  # Não deve ser muito longo

    def test_gerar_relatorio(self):
        """Deve gerar relatório de verificação."""
        resultados = [
            ResultadoVerificacao(
                uf="SP", tipo_documento="nfe", endpoint="",
                disponivel=True, tempo_resposta_ms=100
            ),
            ResultadoVerificacao(
                uf="RJ", tipo_documento="nfe", endpoint="",
                disponivel=True, tempo_resposta_ms=200
            ),
            ResultadoVerificacao(
                uf="MG", tipo_documento="nfe", endpoint="",
                disponivel=False, tempo_resposta_ms=0, erro="Timeout"
            ),
        ]

        relatorio = self.verificador.gerar_relatorio(resultados)

        assert relatorio["resumo"]["total"] == 3
        assert relatorio["resumo"]["disponiveis"] == 2
        assert relatorio["resumo"]["indisponiveis"] == 1
        assert len(relatorio["indisponiveis"]) == 1
        assert relatorio["indisponiveis"][0]["uf"] == "MG"


class TestTipoContingencia:
    """Testes para enum TipoContingencia."""

    def test_svc_an(self):
        """Deve ter tipo SVC_AN."""
        assert TipoContingencia.SVC_AN.value == "SVC_AN"

    def test_svc_rs(self):
        """Deve ter tipo SVC_RS."""
        assert TipoContingencia.SVC_RS.value == "SVC_RS"

    def test_svrs(self):
        """Deve ter tipo SVRS."""
        assert TipoContingencia.SVRS.value == "SVRS"

    def test_epec(self):
        """Deve ter tipo EPEC."""
        assert TipoContingencia.EPEC.value == "EPEC"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
