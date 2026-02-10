"""Testes para os services do módulo GED."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from modules.ged.models.document import DocumentCategory, DocumentType
from modules.ged.services.document_ai_service import DocumentAIService
from modules.ged.services.document_tag_service import DocumentTagService


class TestDocumentAIService:
    """Testes para DocumentAIService."""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão do banco."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Instância do service."""
        return DocumentAIService(mock_session)

    @pytest.mark.asyncio
    async def test_classify_contract(self, service):
        """Testa classificação de contrato."""
        text = """
        CONTRATO DE PRESTAÇÃO DE SERVIÇOS

        Pelo presente instrumento particular, as partes acordam:

        CLÁUSULA PRIMEIRA - DO OBJETO
        O presente contrato tem por objeto a prestação de serviços de limpeza.

        CLÁUSULA SEGUNDA - DO PRAZO
        O prazo de vigência é de 12 meses.

        CLÁUSULA TERCEIRA - DO VALOR
        O valor mensal é de R$ 5.000,00.
        """

        result = await service.classify_document(text, "contrato_servicos.pdf")

        assert result["suggested_type"] == DocumentType.CONTRATO.value
        assert result["type_confidence"] >= 0.5
        assert "contrato" in result["keywords"]

    @pytest.mark.asyncio
    async def test_classify_ata(self, service):
        """Testa classificação de ata."""
        text = """
        ATA DA ASSEMBLEIA GERAL ORDINÁRIA

        Aos 15 dias do mês de janeiro de 2024, reuniram-se os condôminos
        do Condomínio Residencial Sol Nascente para deliberar sobre:

        1. Aprovação das contas do exercício de 2023
        2. Eleição do novo síndico
        3. Orçamento para 2024

        Deliberações:
        Foi aprovada por unanimidade a prestação de contas.
        """

        result = await service.classify_document(text, "ata_assembleia.pdf")

        assert result["suggested_type"] == DocumentType.ATA.value

    @pytest.mark.asyncio
    async def test_classify_nota_fiscal(self, service):
        """Testa classificação de nota fiscal."""
        text = """
        NOTA FISCAL DE SERVIÇOS ELETRÔNICA

        CNPJ: 12.345.678/0001-90
        Número da NFS-e: 12345

        Descrição: Serviços de manutenção
        Valor Total: R$ 1.500,00
        ISS: R$ 75,00
        """

        result = await service.classify_document(text, "nf_12345.pdf")

        assert result["suggested_type"] == DocumentType.NOTA_FISCAL.value

    @pytest.mark.asyncio
    async def test_extract_keywords(self, service):
        """Testa extração de palavras-chave."""
        text = """
        Contrato de manutenção predial com empresa terceirizada.
        Inclui limpeza, conservação e reparos gerais.
        Valor mensal de R$ 3.000,00 com vigência de 12 meses.
        """

        keywords = await service.extract_keywords(text, max_keywords=10)

        assert len(keywords) > 0
        assert len(keywords) <= 10
        assert "contrato" in keywords or "manutenção" in keywords

    @pytest.mark.asyncio
    async def test_extract_dates(self, service):
        """Testa extração de datas."""
        text = """
        Data de início: 01/01/2024
        Data de término: 31/12/2024
        Próxima revisão: 01/07/2024
        """

        result = await service.classify_document(text)

        assert len(result["dates_found"]) >= 2

    @pytest.mark.asyncio
    async def test_extract_monetary_values(self, service):
        """Testa extração de valores monetários."""
        text = """
        Valor do contrato: R$ 10.000,00
        Multa por atraso: R$ 500,00
        Total com impostos: R$ 10.850,00
        """

        result = await service.classify_document(text)

        assert len(result["values_found"]) >= 2

    @pytest.mark.asyncio
    async def test_extract_documents(self, service):
        """Testa extração de documentos (CPF/CNPJ)."""
        text = """
        Contratante: João da Silva
        CPF: 123.456.789-00

        Contratada: Empresa XYZ Ltda
        CNPJ: 12.345.678/0001-90
        """

        result = await service.classify_document(text)

        assert len(result["documents_found"]) >= 2

    @pytest.mark.asyncio
    async def test_analyze_ocr_text(self, service):
        """Testa análise de texto OCR."""
        with patch.object(service, "document_repository") as mock_repo:
            mock_doc = MagicMock()
            mock_doc.id = str(uuid4())
            mock_repo.get_by_id = AsyncMock(return_value=mock_doc)

            result = await service.analyze_ocr_text(
                mock_doc.id, "Contrato de locação residencial no valor de R$ 2.000,00"
            )

            assert "classification" in result
            assert "keywords" in result
            assert result["ocr_quality"] in ["excellent", "good", "fair", "poor"]


class TestDocumentTagServiceHelpers:
    """Testes para funções auxiliares do DocumentTagService."""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão do banco."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Instância do service."""
        return DocumentTagService(mock_session)

    def test_extract_keywords_basic(self, service):
        """Testa extração básica de keywords."""
        text = "Contrato de manutenção predial"
        keywords = service._extract_keywords(text)

        assert "contrato" in keywords
        assert "manutenção" in keywords
        assert "predial" in keywords

    def test_extract_keywords_removes_stopwords(self, service):
        """Testa remoção de stopwords."""
        text = "Este é um contrato de serviços para a empresa"
        keywords = service._extract_keywords(text)

        assert "de" not in keywords
        assert "para" not in keywords
        assert "um" not in keywords
        assert "contrato" in keywords

    def test_extract_keywords_removes_short_words(self, service):
        """Testa remoção de palavras curtas."""
        text = "O documento em PDF foi enviado"
        keywords = service._extract_keywords(text)

        assert "o" not in keywords
        assert "em" not in keywords


class TestDocumentAIServiceInsights:
    """Testes para insights do DocumentAIService."""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão do banco."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Instância do service."""
        return DocumentAIService(mock_session)

    @pytest.mark.asyncio
    async def test_calculate_health_score(self, service):
        """Testa cálculo de score de saúde."""
        with patch.object(service, "document_repository") as mock_repo:
            # Mock stats
            mock_repo.get_stats = AsyncMock(
                return_value={
                    "total_documents": 100,
                    "pending_approval": 5,
                    "pending_signature": 3,
                    "expired": 2,
                }
            )

            # Mock expiring soon
            mock_repo.get_expiring_soon = AsyncMock(return_value=[])

            insights = await service.get_insights()

            assert "health_score" in insights
            assert 0 <= insights["health_score"] <= 100
            assert "health_level" in insights
            assert insights["health_level"] in ["excellent", "good", "attention", "critical"]

    @pytest.mark.asyncio
    async def test_get_recommendations(self, service):
        """Testa geração de recomendações."""
        with patch.object(service, "document_repository") as mock_repo:
            mock_repo.get_stats = AsyncMock(
                return_value={
                    "total_documents": 100,
                    "pending_approval": 15,  # > 10
                    "pending_signature": 5,
                    "expired": 3,
                }
            )
            mock_repo.get_expiring_soon = AsyncMock(
                return_value=[
                    MagicMock(),
                    MagicMock(),
                    MagicMock(),  # 3 expirando
                ]
            )

            insights = await service.get_insights()

            assert "recommendations" in insights
            assert len(insights["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_get_trends(self, service):
        """Testa obtenção de tendências."""
        with patch.object(service, "document_repository") as mock_repo:
            mock_repo.get_stats = AsyncMock(
                return_value={
                    "total_documents": 100,
                    "by_type": {"contrato": 30, "ata": 20},
                    "by_category": {"administrativo": 50},
                    "by_status": {"publicado": 80, "rascunho": 20},
                }
            )

            trends = await service.get_trends(days=30)

            assert "summary" in trends
            assert "by_type" in trends
            assert "by_status" in trends


class TestDocumentClassificationPatterns:
    """Testes para padrões de classificação de documentos."""

    @pytest.fixture
    def mock_session(self):
        """Mock da sessão."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Service de IA."""
        return DocumentAIService(mock_session)

    @pytest.mark.asyncio
    async def test_classify_regulamento(self, service):
        """Testa classificação de regulamento."""
        text = """
        REGULAMENTO INTERNO DO CONDOMÍNIO

        Art. 1º - Este regulamento estabelece as normas de convivência.
        Art. 2º - É proibido causar perturbação após as 22h.
        Art. 3º - O uso da piscina é permitido das 8h às 22h.
        """

        result = await service.classify_document(text)
        assert result["suggested_type"] == DocumentType.REGULAMENTO.value

    @pytest.mark.asyncio
    async def test_classify_laudo(self, service):
        """Testa classificação de laudo."""
        text = """
        LAUDO TÉCNICO DE VISTORIA

        Conforme inspeção realizada no local, verificou-se:
        - Infiltração na laje do térreo
        - Trincas superficiais na fachada

        Parecer: Necessária manutenção corretiva.
        """

        result = await service.classify_document(text)
        assert result["suggested_type"] == DocumentType.LAUDO.value

    @pytest.mark.asyncio
    async def test_classify_procuracao(self, service):
        """Testa classificação de procuração."""
        text = """
        PROCURAÇÃO

        Pelo presente instrumento, outorgo poderes especiais ao
        Sr. José da Silva, CPF 123.456.789-00, para representar-me
        em assembleias condominiais e votar em meu nome.
        """

        result = await service.classify_document(text)
        assert result["suggested_type"] == DocumentType.PROCURACAO.value

    @pytest.mark.asyncio
    async def test_classify_comunicado(self, service):
        """Testa classificação de comunicado."""
        text = """
        COMUNICADO AOS MORADORES

        Informamos que haverá interrupção no fornecimento de água
        no próximo sábado, das 8h às 12h, para manutenção preventiva.

        Atenciosamente,
        A Administração
        """

        result = await service.classify_document(text)
        assert result["suggested_type"] == DocumentType.COMUNICADO.value

    @pytest.mark.asyncio
    async def test_classify_unknown(self, service):
        """Testa classificação de documento desconhecido."""
        text = "Texto genérico sem padrões específicos identificáveis."

        result = await service.classify_document(text)

        # Deve ter baixa confiança
        assert result["type_confidence"] < 0.5

    @pytest.mark.asyncio
    async def test_category_classification(self, service):
        """Testa classificação de categoria."""
        text = """
        RELATÓRIO FINANCEIRO MENSAL

        Receitas: R$ 50.000,00
        Despesas: R$ 45.000,00
        Saldo: R$ 5.000,00
        """

        result = await service.classify_document(text)
        assert result["suggested_category"] == DocumentCategory.FINANCEIRO.value
