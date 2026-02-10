"""
Testes de Extração de Dados Governamentais.

Valida orquestrador, extratores e jobs.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# Adicionar path do módulo
sys.path.insert(0, "/opt/conecta-pro/backend")

from modules.government_integrations.extractors.base_extractor import (
    DocumentoExtraido,
    ExtratorBase,
)
from modules.government_integrations.extractors.base_extractor import (
    ResultadoExtracao as ResultadoExtracaoBase,
)
from modules.government_integrations.extractors.orchestrator import (
    ConfiguracaoExtracao,
    OrquestradorExtracao,
    ResultadoExtracao,
    ResultadoServico,
    StatusExtracao,
    TipoServico,
)


class TestConfiguracaoExtracao:
    """Testes da configuração de extração."""

    def test_configuracao_padrao(self):
        """Testa criação com valores padrão."""
        config = ConfiguracaoExtracao(
            servicos=[TipoServico.SEFAZ_NFE],
        )

        assert config.servicos == [TipoServico.SEFAZ_NFE]
        assert config.modo_incremental is True
        assert config.processar_em_paralelo is True
        assert config.max_workers == 5
        print("✓ Configuração padrão OK")

    def test_configuracao_completa(self):
        """Testa criação com todos os parâmetros."""
        config = ConfiguracaoExtracao(
            servicos=[TipoServico.SEFAZ_NFE, TipoServico.ESOCIAL],
            data_inicio=datetime(2024, 1, 1),
            data_fim=datetime(2024, 12, 31),
            cnpjs=["12345678000100"],
            ufs=["AM", "SP"],
            modo_incremental=False,
            processar_em_paralelo=True,
            max_workers=3,
        )

        assert len(config.servicos) == 2
        assert config.cnpjs == ["12345678000100"]
        assert config.ufs == ["AM", "SP"]
        assert config.processar_em_paralelo is True
        print("✓ Configuração completa OK")

    def test_tipos_servico(self):
        """Testa todos os tipos de serviço."""
        tipos = [
            TipoServico.SEFAZ_NFE,
            TipoServico.SEFAZ_CTE,
            TipoServico.SEFAZ_MDFE,
            TipoServico.ESOCIAL,
            TipoServico.FGTS_DIGITAL,
            TipoServico.NFSE_MANAUS,
            TipoServico.RECEITA_FEDERAL,
        ]

        for tipo in tipos:
            assert tipo.value is not None
            print(f"✓ TipoServico.{tipo.name} = {tipo.value}")


class TestDocumentoExtraido:
    """Testes do modelo de documento extraído."""

    def test_documento_basico(self):
        """Testa criação de documento básico."""
        doc = DocumentoExtraido(
            id="nfe_12345",
            tipo="nfe",
            dados={"chave": "12345678901234567890123456789012345678901234"},
        )

        assert doc.id == "nfe_12345"
        assert doc.tipo == "nfe"
        assert doc.processado is False
        assert doc.erro is None
        print("✓ Documento básico OK")

    def test_documento_processado(self):
        """Testa documento processado com sucesso."""
        doc = DocumentoExtraido(
            id="nfe_12345",
            tipo="nfe",
            dados={"valor": 1000.00},
            xml_original="<nfe>...</nfe>",
            processado=True,
        )

        assert doc.processado is True
        assert doc.xml_original is not None
        print("✓ Documento processado OK")

    def test_documento_com_erro(self):
        """Testa documento com erro."""
        doc = DocumentoExtraido(
            id="nfe_error",
            tipo="nfe",
            dados={},
            erro="Timeout na consulta",
        )

        assert doc.erro == "Timeout na consulta"
        assert doc.processado is False
        print("✓ Documento com erro OK")


class TestResultadoExtracao:
    """Testes do resultado de extração."""

    def test_resultado_vazio(self):
        """Testa resultado sem documentos."""
        resultado = ResultadoExtracao()

        assert resultado.total_documentos == 0
        assert resultado.total_novos == 0
        assert resultado.total_erros == 0
        assert resultado.status == StatusExtracao.INICIADA
        print("✓ Resultado vazio OK")

    def test_resultado_com_documentos(self):
        """Testa resultado com documentos."""
        resultado = ResultadoExtracao(
            status=StatusExtracao.CONCLUIDA,
            total_documentos=100,
            total_novos=50,
            total_atualizados=30,
            total_erros=5,
        )

        assert resultado.total_documentos == 100
        assert resultado.total_novos == 50
        print("✓ Resultado com documentos OK")

    def test_resultado_to_dict(self):
        """Testa conversão para dicionário."""
        tenant_id = uuid4()
        resultado = ResultadoExtracao(
            tenant_id=tenant_id,
            status=StatusExtracao.CONCLUIDA,
        )

        data = resultado.to_dict()

        assert "status" in data
        assert "tenant_id" in data
        assert "totais" in data
        assert data["status"] == "concluida"
        assert data["tenant_id"] == str(tenant_id)
        print("✓ Resultado to_dict OK")


class TestOrquestradorExtracao:
    """Testes do orquestrador de extração."""

    @pytest.fixture
    def orquestrador(self):
        """Fixture do orquestrador."""
        return OrquestradorExtracao()

    def test_instanciacao(self, orquestrador):
        """Testa criação do orquestrador."""
        assert orquestrador is not None
        assert hasattr(orquestrador, "iniciar_extracao")
        print("✓ Orquestrador instanciado OK")

    @pytest.mark.asyncio
    async def test_validar_prerequisitos(self, orquestrador):
        """Testa validação de pré-requisitos."""
        tenant_id = uuid4()

        # Mock do provedor de credenciais
        with patch.object(orquestrador, "credentials") as mock_cred:
            mock_cred.verificar_certificado = AsyncMock(
                return_value={
                    "valido": True,
                    "dias_restantes": 30,
                }
            )

            resultado = await orquestrador.validar_prerequisitos(tenant_id, [TipoServico.SEFAZ_NFE])

            # Deve retornar dict de validação
            assert resultado is not None
            print("✓ Validação de pré-requisitos OK")

    @pytest.mark.asyncio
    async def test_extracao_simples(self, orquestrador):
        """Testa extração simples."""
        tenant_id = uuid4()
        config = ConfiguracaoExtracao(
            servicos=[TipoServico.RECEITA_FEDERAL],
            cnpjs=["12345678000100"],
        )

        # Mock do método _extrair_servico
        mock_resultado_servico = ResultadoServico(
            servico=TipoServico.RECEITA_FEDERAL,
            status=StatusExtracao.CONCLUIDA,
            inicio=datetime.utcnow(),
            fim=datetime.utcnow(),
            documentos_processados=1,
            documentos_novos=1,
            erros=[],
            detalhes={},
        )

        with patch.object(orquestrador, "_extrair_servico", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_resultado_servico

            resultado = await orquestrador.iniciar_extracao(tenant_id, config)

            assert resultado is not None
            assert resultado.status in [
                StatusExtracao.CONCLUIDA,
                StatusExtracao.CONCLUIDA_PARCIAL,
                StatusExtracao.INICIADA,
                StatusExtracao.EM_ANDAMENTO,
            ]
            print("✓ Extração simples OK")


class TestExtratoresIndividuais:
    """Testes dos extratores individuais."""

    @pytest.fixture
    def mock_credentials(self):
        """Fixture para mock de credenciais."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_extrator_nfe_instancia(self, mock_credentials):
        """Testa instanciação do extrator NF-e."""
        from modules.government_integrations.extractors.sefaz.nfe_extractor import (
            ExtratorNFe,
        )

        extrator = ExtratorNFe(credentials=mock_credentials)

        assert extrator.tipo_servico == "sefaz_nfe"
        assert extrator.TIMEOUT > 0
        assert extrator.MAX_RETRIES > 0
        print("✓ Extrator NF-e instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_esocial_instancia(self, mock_credentials):
        """Testa instanciação do extrator eSocial."""
        from modules.government_integrations.extractors.esocial.esocial_extractor import (
            ExtratoreSocial,
        )

        extrator = ExtratoreSocial(credentials=mock_credentials)

        assert extrator.tipo_servico == "esocial"
        assert hasattr(extrator, "URLS")
        assert hasattr(extrator, "listar_eventos_pendentes")
        print("✓ Extrator eSocial instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_fgts_instancia(self, mock_credentials):
        """Testa instanciação do extrator FGTS."""
        from modules.government_integrations.extractors.fgts.fgts_extractor import (
            ExtratorFGTS,
        )

        extrator = ExtratorFGTS(credentials=mock_credentials)

        assert extrator.tipo_servico == "fgts_digital"
        print("✓ Extrator FGTS instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_nfse_instancia(self, mock_credentials):
        """Testa instanciação do extrator NFS-e."""
        from modules.government_integrations.extractors.nfse.manaus_extractor import (
            ExtratorNFSeManaus,
        )

        extrator = ExtratorNFSeManaus(credentials=mock_credentials)

        assert extrator.tipo_servico == "nfse_manaus"
        assert "manaus" in extrator.URL_PRODUCAO.lower()
        print("✓ Extrator NFS-e Manaus instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_rfb_instancia(self, mock_credentials):
        """Testa instanciação do extrator RFB."""
        from modules.government_integrations.extractors.receita_federal.rfb_extractor import (
            ExtratorRFB,
        )

        extrator = ExtratorRFB(credentials=mock_credentials)

        assert extrator.tipo_servico == "receita_federal"
        assert "cnpj" in extrator.URLS
        print("✓ Extrator RFB instanciado OK")


class TestJobsCelery:
    """Testes dos jobs Celery."""

    def test_import_sync_tasks(self):
        """Testa importação das tasks de sync."""
        from modules.government_integrations.jobs.sync_tasks import (
            sincronizar_esocial,
            sincronizar_fgts,
            sincronizar_nfe,
            sincronizar_nfse,
            sincronizar_rfb,
            sincronizar_todos,
        )

        assert sincronizar_nfe is not None
        assert sincronizar_esocial is not None
        assert sincronizar_fgts is not None
        assert sincronizar_nfse is not None
        assert sincronizar_rfb is not None
        assert sincronizar_todos is not None
        print("✓ Tasks de sync importadas OK")

    def test_import_monitoring_tasks(self):
        """Testa importação das tasks de monitoramento."""
        from modules.government_integrations.jobs.monitoring_tasks import (
            gerar_relatorio_diario,
            limpar_cache,
            reprocessar_falhas,
            verificar_certificados,
            verificar_disponibilidade,
        )

        assert verificar_disponibilidade is not None
        assert verificar_certificados is not None
        assert reprocessar_falhas is not None
        assert limpar_cache is not None
        assert gerar_relatorio_diario is not None
        print("✓ Tasks de monitoramento importadas OK")

    def test_task_names(self):
        """Testa nomes das tasks Celery."""
        from modules.government_integrations.jobs.sync_tasks import sincronizar_nfe

        assert sincronizar_nfe.name == "government_integrations.tasks.sync.sincronizar_nfe"
        print(f"✓ Task name: {sincronizar_nfe.name}")


class TestControllersAPI:
    """Testes dos controllers da API."""

    def test_import_dashboard_controller(self):
        """Testa importação do dashboard controller."""
        from modules.government_integrations.controllers.dashboard_controller import (
            DashboardResponse,
            DashboardService,
            router,
        )

        assert router is not None
        assert DashboardService is not None
        print("✓ Dashboard controller importado OK")

    def test_import_extraction_controller(self):
        """Testa importação do extraction controller."""
        from modules.government_integrations.controllers.extraction_controller import (
            ExtracaoResponse,
            IniciarExtracaoRequest,
            router,
        )

        assert router is not None
        assert IniciarExtracaoRequest is not None
        print("✓ Extraction controller importado OK")

    def test_dashboard_service_instancia(self):
        """Testa instanciação do DashboardService."""
        from modules.government_integrations.controllers.dashboard_controller import (
            DashboardService,
        )

        service = DashboardService()

        assert service is not None
        assert hasattr(service, "obter_dashboard")
        assert hasattr(service, "obter_metricas")
        print("✓ DashboardService instanciado OK")


def run_tests():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTES DE EXTRAÇÃO GOVERNAMENTAL")
    print("=" * 60 + "\n")

    # Testes síncronos
    print("\n--- Configuração de Extração ---")
    test_config = TestConfiguracaoExtracao()
    test_config.test_configuracao_padrao()
    test_config.test_configuracao_completa()
    test_config.test_tipos_servico()

    print("\n--- Documento Extraído ---")
    test_doc = TestDocumentoExtraido()
    test_doc.test_documento_basico()
    test_doc.test_documento_processado()
    test_doc.test_documento_com_erro()

    print("\n--- Resultado Extração ---")
    test_result = TestResultadoExtracao()
    test_result.test_resultado_vazio()
    test_result.test_resultado_com_documentos()
    test_result.test_resultado_to_dict()

    print("\n--- Extratores Individuais ---")
    mock_cred = MagicMock()
    test_ext = TestExtratoresIndividuais()
    asyncio.run(test_ext.test_extrator_nfe_instancia(mock_cred))
    asyncio.run(test_ext.test_extrator_esocial_instancia(mock_cred))
    asyncio.run(test_ext.test_extrator_fgts_instancia(mock_cred))
    asyncio.run(test_ext.test_extrator_nfse_instancia(mock_cred))
    asyncio.run(test_ext.test_extrator_rfb_instancia(mock_cred))

    print("\n--- Jobs Celery ---")
    test_jobs = TestJobsCelery()
    test_jobs.test_import_sync_tasks()
    test_jobs.test_import_monitoring_tasks()
    test_jobs.test_task_names()

    print("\n--- Controllers API ---")
    test_ctrl = TestControllersAPI()
    test_ctrl.test_import_dashboard_controller()
    test_ctrl.test_import_extraction_controller()
    test_ctrl.test_dashboard_service_instancia()

    print("\n" + "=" * 60)
    print("TODOS OS TESTES PASSARAM!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_tests()
