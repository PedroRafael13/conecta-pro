"""Testes para ClassificationAIService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from modules.occurrences.services.classification_ai_service import ClassificationAIService
from modules.occurrences.models.occurrence import OccurrenceType, OccurrencePriority


class TestClassificationAIService:
    """Testes para ClassificationAIService."""

    @pytest.fixture
    def mock_session(self):
        """Cria sessao mock."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Cria instancia do service."""
        return ClassificationAIService(mock_session)

    @pytest.mark.asyncio
    async def test_classify_reclamacao(self, service):
        """Testa classificacao de reclamacao."""
        result = await service.classify_occurrence(
            title="Barulho excessivo do vizinho",
            description="O vizinho do apartamento 302 esta fazendo muito barulho toda noite",
        )

        assert result["suggested_type"] == OccurrenceType.RECLAMACAO.value
        assert "barulho" in [k.lower() for k in result["keywords"]]
        assert result["confidence"] > 0

    @pytest.mark.asyncio
    async def test_classify_emergencia(self, service):
        """Testa classificacao de emergencia."""
        result = await service.classify_occurrence(
            title="Incendio no estacionamento",
            description="Fogo visivel no estacionamento, precisa de socorro urgente",
        )

        assert result["suggested_type"] == OccurrenceType.EMERGENCIA.value
        assert result["suggested_priority"] in [
            OccurrencePriority.URGENTE.value,
            OccurrencePriority.CRITICA.value,
        ]

    @pytest.mark.asyncio
    async def test_classify_sugestao(self, service):
        """Testa classificacao de sugestao."""
        result = await service.classify_occurrence(
            title="Sugestao de melhoria na area de lazer",
            description="Seria otimo se pudessemos ter mais bancos no jardim",
        )

        assert result["suggested_type"] == OccurrenceType.SUGESTAO.value

    @pytest.mark.asyncio
    async def test_classify_elogio(self, service):
        """Testa classificacao de elogio."""
        result = await service.classify_occurrence(
            title="Parabens pela excelente manutencao",
            description="Agradeco o otimo trabalho realizado na piscina",
        )

        assert result["suggested_type"] == OccurrenceType.ELOGIO.value
        assert result["sentiment"] == "positivo"

    @pytest.mark.asyncio
    async def test_classify_solicitacao(self, service):
        """Testa classificacao de solicitacao."""
        result = await service.classify_occurrence(
            title="Solicito troca de lampada",
            description="Preciso que troquem a lampada do corredor do 3o andar",
        )

        assert result["suggested_type"] == OccurrenceType.SOLICITACAO.value

    @pytest.mark.asyncio
    async def test_classify_denuncia(self, service):
        """Testa classificacao de denuncia."""
        result = await service.classify_occurrence(
            title="Denuncia de uso irregular de vaga",
            description="Estao usando a vaga de forma ilegal para comercio",
        )

        assert result["suggested_type"] == OccurrenceType.DENUNCIA.value

    @pytest.mark.asyncio
    async def test_classify_incidente(self, service):
        """Testa classificacao de incidente."""
        result = await service.classify_occurrence(
            title="Vazamento de agua no teto",
            description="Agua esta escorrendo do teto do banheiro, danificando o forro",
        )

        assert result["suggested_type"] == OccurrenceType.INCIDENTE.value

    @pytest.mark.asyncio
    async def test_priority_keywords_critica(self, service):
        """Testa prioridade critica por palavras-chave."""
        result = await service.classify_occurrence(
            title="Situacao critica urgente",
            description="Emergencia imediata, precisa de atencao urgente agora",
        )

        assert result["suggested_priority"] in [
            OccurrencePriority.CRITICA.value,
            OccurrencePriority.URGENTE.value,
        ]

    @pytest.mark.asyncio
    async def test_priority_keywords_baixa(self, service):
        """Testa prioridade baixa por palavras-chave."""
        result = await service.classify_occurrence(
            title="Pequeno ajuste quando possivel",
            description="Nao e urgente, pode ser feito quando tiver tempo",
        )

        # Pode ser baixa ou media dependendo do contexto
        assert result["suggested_priority"] in [
            OccurrencePriority.BAIXA.value,
            OccurrencePriority.MEDIA.value,
        ]

    @pytest.mark.asyncio
    async def test_sentiment_negative(self, service):
        """Testa deteccao de sentimento negativo."""
        result = await service.classify_occurrence(
            title="Problema grave nao resolvido",
            description="Estou muito insatisfeito com a situacao horrivel",
        )

        assert result["sentiment"] == "negativo"

    @pytest.mark.asyncio
    async def test_sentiment_positive(self, service):
        """Testa deteccao de sentimento positivo."""
        result = await service.classify_occurrence(
            title="Excelente servico prestado",
            description="Muito satisfeito com o otimo trabalho realizado, obrigado",
        )

        assert result["sentiment"] == "positivo"

    @pytest.mark.asyncio
    async def test_keyword_extraction(self, service):
        """Testa extracao de palavras-chave."""
        result = await service.classify_occurrence(
            title="Problema com elevador social",
            description="O elevador do bloco A esta com defeito e precisa de manutencao",
        )

        keywords = [k.lower() for k in result["keywords"]]
        assert any(kw in keywords for kw in ["elevador", "manutencao", "defeito"])

    @pytest.mark.asyncio
    async def test_confidence_score(self, service):
        """Testa score de confianca."""
        result = await service.classify_occurrence(
            title="Reclamacao sobre barulho",
            description="Reclamacao formal sobre excesso de barulho do vizinho",
        )

        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_empty_input(self, service):
        """Testa entrada vazia."""
        result = await service.classify_occurrence(
            title="",
            description="",
        )

        # Deve retornar tipo padrao
        assert result["suggested_type"] is not None
        assert result["suggested_priority"] is not None

    @pytest.mark.asyncio
    async def test_calculate_priority_score_not_found(self, service, mock_session):
        """Testa calculo de score para ocorrencia inexistente."""
        with patch.object(service, "occurrence_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)

            result = await service.calculate_priority_score(uuid4())

            assert "error" in result

    @pytest.mark.asyncio
    async def test_calculate_priority_score_success(self, service, mock_session):
        """Testa calculo de score com sucesso."""
        occurrence_id = uuid4()

        mock_occurrence = MagicMock()
        mock_occurrence.id = occurrence_id
        mock_occurrence.priority = OccurrencePriority.ALTA
        mock_occurrence.type = OccurrenceType.EMERGENCIA
        mock_occurrence.created_at = datetime.utcnow() - timedelta(days=3)
        mock_occurrence.sla_response_deadline = datetime.utcnow() - timedelta(hours=1)
        mock_occurrence.is_escalated = True
        mock_occurrence.reopen_count = 1
        mock_occurrence.condominium_id = str(uuid4())

        with patch.object(service, "occurrence_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=mock_occurrence)

            result = await service.calculate_priority_score(occurrence_id)

            assert "total_score" in result
            assert "factors" in result
            assert result["total_score"] > 0

    @pytest.mark.asyncio
    async def test_suggest_assignee_not_found(self, service):
        """Testa sugestao de responsavel para ocorrencia inexistente."""
        with patch.object(service, "occurrence_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)

            result = await service.suggest_assignee(uuid4())

            assert "error" in result

    @pytest.mark.asyncio
    async def test_suggest_assignee_by_category(self, service):
        """Testa sugestao de responsavel por categoria."""
        occurrence_id = uuid4()
        category_id = uuid4()

        mock_occurrence = MagicMock()
        mock_occurrence.id = occurrence_id
        mock_occurrence.category_id = category_id
        mock_occurrence.type = OccurrenceType.SOLICITACAO

        mock_category = MagicMock()
        mock_category.default_assignee_id = str(uuid4())
        mock_category.default_assignee_name = "Tecnico Padrao"

        with patch.object(service, "occurrence_repository") as mock_occ_repo:
            with patch.object(service, "category_repository") as mock_cat_repo:
                mock_occ_repo.get_by_id = AsyncMock(return_value=mock_occurrence)
                mock_cat_repo.get_by_id = AsyncMock(return_value=mock_category)

                result = await service.suggest_assignee(occurrence_id)

                assert result["suggested_assignee_id"] == mock_category.default_assignee_id

    @pytest.mark.asyncio
    async def test_analyze_trends(self, service):
        """Testa analise de tendencias."""
        condominium_id = str(uuid4())

        mock_stats = {
            "total": 100,
            "by_status": {"aberta": 30, "resolvida": 60},
            "by_type": {"reclamacao": 40, "solicitacao": 35},
            "by_priority": {"alta": 20, "media": 50},
        }

        with patch.object(service, "occurrence_repository") as mock_repo:
            mock_repo.get_stats = AsyncMock(return_value=mock_stats)
            mock_repo.list_with_filters = AsyncMock(return_value=([], 0))

            result = await service.analyze_trends(condominium_id, days=30)

            assert "period_days" in result
            assert result["period_days"] == 30
            assert "total_occurrences" in result
            assert "insights" in result


class TestClassificationKeywords:
    """Testes para palavras-chave de classificacao."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service."""
        mock_session = AsyncMock()
        return ClassificationAIService(mock_session)

    @pytest.mark.asyncio
    async def test_multiple_type_keywords(self, service):
        """Testa texto com multiplas palavras-chave de tipos diferentes."""
        # Texto com palavras de reclamacao E solicitacao
        result = await service.classify_occurrence(
            title="Reclamacao e solicitacao de reparo",
            description="Reclamo do barulho e solicito conserto da porta",
        )

        # Deve escolher o tipo mais relevante
        assert result["suggested_type"] in [
            OccurrenceType.RECLAMACAO.value,
            OccurrenceType.SOLICITACAO.value,
        ]

    @pytest.mark.asyncio
    async def test_portuguese_accents(self, service):
        """Testa tratamento de acentos em portugues."""
        result = await service.classify_occurrence(
            title="Manutencao emergencial",
            description="Situacao urgentissima na area de lazer",
        )

        # Deve detectar corretamente mesmo sem acentos
        assert result["suggested_type"] is not None

    @pytest.mark.asyncio
    async def test_mixed_case(self, service):
        """Testa texto com caixa mista."""
        result = await service.classify_occurrence(
            title="EMERGENCIA URGENTE",
            description="Preciso de AJUDA IMEDIATA com vazamento",
        )

        assert result["suggested_priority"] in [
            OccurrencePriority.URGENTE.value,
            OccurrencePriority.CRITICA.value,
        ]
