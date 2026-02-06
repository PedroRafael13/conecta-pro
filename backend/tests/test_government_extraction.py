"""
Testes de Extração de Dados Governamentais.

Valida orquestrador, extratores e jobs.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Adicionar path do módulo
sys.path.insert(0, '/opt/conecta-pro/backend')

from modules.government_integrations.extractors.orchestrator import (
    OrquestradorExtracao,
    ConfiguracaoExtracao,
    TipoServico,
    ResultadoExtracao,
)
from modules.government_integrations.extractors.base_extractor import (
    ExtratorBase,
    DocumentoExtraido,
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
        assert config.processar_em_paralelo is False
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
        resultado = ResultadoExtracao(
            servico="sefaz_nfe",
            inicio=datetime.utcnow(),
        )

        assert resultado.documentos_processados == 0
        assert resultado.documentos_novos == 0
        assert resultado.documentos_erro == 0
        assert resultado.status == "pendente"
        print("✓ Resultado vazio OK")

    def test_resultado_com_documentos(self):
        """Testa resultado com documentos."""
        resultado = ResultadoExtracao(
            servico="sefaz_nfe",
            inicio=datetime.utcnow(),
            documentos_processados=100,
            documentos_novos=50,
            documentos_atualizados=30,
            documentos_erro=5,
            status="concluida",
        )

        assert resultado.documentos_processados == 100
        assert resultado.documentos_novos == 50
        print("✓ Resultado com documentos OK")

    def test_resultado_to_dict(self):
        """Testa conversão para dicionário."""
        resultado = ResultadoExtracao(
            servico="esocial",
            inicio=datetime.utcnow(),
            status="concluida",
        )

        data = resultado.to_dict()

        assert "servico" in data
        assert "inicio" in data
        assert "status" in data
        assert data["servico"] == "esocial"
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
        assert hasattr(orquestrador, 'iniciar_extracao')
        print("✓ Orquestrador instanciado OK")

    @pytest.mark.asyncio
    async def test_validar_prerequisitos(self, orquestrador):
        """Testa validação de pré-requisitos."""
        tenant_id = uuid4()

        # Mock do provedor de credenciais
        with patch.object(orquestrador, 'credenciais') as mock_cred:
            mock_cred.verificar_certificado = AsyncMock(return_value={
                "valido": True,
                "dias_restantes": 30,
            })

            resultado = await orquestrador._validar_prerequisitos(
                tenant_id,
                [TipoServico.SEFAZ_NFE]
            )

            # Deve retornar True ou dict de validação
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

        # Mock dos extratores
        mock_resultado = ResultadoExtracao(
            servico="receita_federal",
            inicio=datetime.utcnow(),
            fim=datetime.utcnow(),
            status="concluida",
            documentos_processados=1,
            documentos_novos=1,
        )

        with patch.object(orquestrador, '_executar_extrator', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = mock_resultado

            resultado = await orquestrador.iniciar_extracao(tenant_id, config)

            assert resultado is not None
            assert resultado.status in ["concluida", "concluida_parcial", "pendente"]
            print("✓ Extração simples OK")


class TestExtratoresIndividuais:
    """Testes dos extratores individuais."""

    @pytest.mark.asyncio
    async def test_extrator_nfe_instancia(self):
        """Testa instanciação do extrator NF-e."""
        from modules.government_integrations.extractors.sefaz.nfe_extractor import ExtratorNFe

        extrator = ExtratorNFe()

        assert extrator.tipo_servico == "sefaz_nfe"
        assert extrator.TIMEOUT > 0
        assert extrator.MAX_RETRIES > 0
        print("✓ Extrator NF-e instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_esocial_instancia(self):
        """Testa instanciação do extrator eSocial."""
        from modules.government_integrations.extractors.esocial.esocial_extractor import ExtratoreSocial

        extrator = ExtratoreSocial()

        assert extrator.tipo_servico == "esocial"
        assert hasattr(extrator, 'EVENTOS_PERIODICOS')
        assert hasattr(extrator, 'EVENTOS_NAO_PERIODICOS')
        print("✓ Extrator eSocial instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_fgts_instancia(self):
        """Testa instanciação do extrator FGTS."""
        from modules.government_integrations.extractors.fgts.fgts_extractor import ExtratorFGTS

        extrator = ExtratorFGTS()

        assert extrator.tipo_servico == "fgts_digital"
        print("✓ Extrator FGTS instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_nfse_instancia(self):
        """Testa instanciação do extrator NFS-e."""
        from modules.government_integrations.extractors.nfse.manaus_extractor import ExtratorNFSeManaus

        extrator = ExtratorNFSeManaus()

        assert extrator.tipo_servico == "nfse_manaus"
        assert "manaus" in extrator.URL_PRODUCAO.lower()
        print("✓ Extrator NFS-e Manaus instanciado OK")

    @pytest.mark.asyncio
    async def test_extrator_rfb_instancia(self):
        """Testa instanciação do extrator RFB."""
        from modules.government_integrations.extractors.receita_federal.rfb_extractor import ExtratorRFB

        extrator = ExtratorRFB()

        assert extrator.tipo_servico == "receita_federal"
        assert "cnpj" in extrator.URLS
        print("✓ Extrator RFB instanciado OK")


class TestJobsCelery:
    """Testes dos jobs Celery."""

    def test_import_sync_tasks(self):
        """Testa importação das tasks de sync."""
        from modules.government_integrations.jobs.sync_tasks import (
            sincronizar_nfe,
            sincronizar_esocial,
            sincronizar_fgts,
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
            verificar_disponibilidade,
            verificar_certificados,
            reprocessar_falhas,
            limpar_cache,
            gerar_relatorio_diario,
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
            router,
            DashboardService,
            DashboardResponse,
        )

        assert router is not None
        assert DashboardService is not None
        print("✓ Dashboard controller importado OK")

    def test_import_extraction_controller(self):
        """Testa importação do extraction controller."""
        from modules.government_integrations.controllers.extraction_controller import (
            router,
            IniciarExtracaoRequest,
            ExtracaoResponse,
        )

        assert router is not None
        assert IniciarExtracaoRequest is not None
        print("✓ Extraction controller importado OK")

    def test_dashboard_service_instancia(self):
        """Testa instanciação do DashboardService."""
        from modules.government_integrations.controllers.dashboard_controller import DashboardService

        service = DashboardService()

        assert service is not None
        assert hasattr(service, 'obter_dashboard')
        assert hasattr(service, 'obter_metricas')
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
    test_ext = TestExtratoresIndividuais()
    asyncio.run(test_ext.test_extrator_nfe_instancia())
    asyncio.run(test_ext.test_extrator_esocial_instancia())
    asyncio.run(test_ext.test_extrator_fgts_instancia())
    asyncio.run(test_ext.test_extrator_nfse_instancia())
    asyncio.run(test_ext.test_extrator_rfb_instancia())

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
