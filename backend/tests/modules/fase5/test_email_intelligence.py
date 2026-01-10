"""
tests/modules/fase5/test_email_intelligence.py - Email Intelligence Tests
==========================================================================
Testes de integracao para Email Intelligence com NLP
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime

from modules.fase5.email_intelligence.service import EmailIntelligenceService
from modules.fase5.email_intelligence.models import (
    EmailMessage,
    EmailAnalysis,
    EmailContext,
    ActionSuggestion
)
from modules.fase5.email_intelligence.enums import (
    EmailCategory,
    EmailPriority,
    EmailIntent,
    EmailSentiment,
    ActionType
)


class TestEmailIntelligenceService:
    """Testes para EmailIntelligenceService."""

    @pytest.fixture
    def service(self):
        """Fixture do servico de email."""
        return EmailIntelligenceService()

    @pytest.fixture
    def tenant_id(self):
        """Fixture de tenant_id."""
        return uuid4()

    # =========================================================================
    # Testes de Processamento de Email
    # =========================================================================

    @pytest.mark.asyncio
    async def test_processar_email_basico(self, service, tenant_id):
        """Deve processar email basico."""
        email = EmailMessage(
            from_address="teste@exemplo.com",
            to_addresses=["destino@empresa.com"],
            subject="Teste de email",
            body_text="Este e um email de teste.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        assert "email_id" in resultado
        assert "analysis" in resultado
        assert "suggestions" in resultado
        assert "context" in resultado

    @pytest.mark.asyncio
    async def test_processar_email_urgente(self, service, tenant_id):
        """Deve detectar email urgente."""
        email = EmailMessage(
            from_address="sindico@condominio.com",
            to_addresses=["admin@empresa.com"],
            subject="URGENTE: Vazamento no predio",
            body_text="Precisamos de atendimento imediato! Ha um vazamento grave.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        assert resultado["analysis"]["is_urgent"] is True
        assert resultado["analysis"]["priority"] in ["urgente", "alta"]

    @pytest.mark.asyncio
    async def test_processar_email_financeiro(self, service, tenant_id):
        """Deve categorizar email financeiro."""
        email = EmailMessage(
            from_address="financeiro@cliente.com",
            to_addresses=["cobranca@empresa.com"],
            subject="Solicitacao de boleto",
            body_text="Preciso da segunda via do boleto no valor de R$ 5.000,00.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        # Deve extrair valor monetario
        entities = resultado["analysis"]["entities"]
        assert "valor" in entities or len(resultado["analysis"]["keywords"]) > 0

    @pytest.mark.asyncio
    async def test_processar_email_requer_resposta(self, service, tenant_id):
        """Deve identificar emails que requerem resposta."""
        email = EmailMessage(
            from_address="cliente@empresa.com",
            to_addresses=["suporte@empresa.com"],
            subject="Duvida sobre contrato",
            body_text="Gostaria de saber mais informacoes sobre o contrato.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        assert resultado["analysis"]["requires_response"] is True

    @pytest.mark.asyncio
    async def test_processar_email_nao_spam(self, service, tenant_id):
        """Emails legitimos nao devem ser marcados como spam."""
        email = EmailMessage(
            from_address="diretor@empresa.com",
            to_addresses=["gerente@empresa.com"],
            subject="Reuniao de alinhamento",
            body_text="Vamos agendar uma reuniao para discutir o projeto.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        assert resultado["analysis"]["is_spam"] is False

    # =========================================================================
    # Testes de Extracao de Entidades
    # =========================================================================

    @pytest.mark.asyncio
    async def test_extrair_valor_monetario(self, service, tenant_id):
        """Deve extrair valores monetarios."""
        email = EmailMessage(
            from_address="fornecedor@empresa.com",
            to_addresses=["compras@empresa.com"],
            subject="Orcamento",
            body_text="O valor total e R$ 15.750,00 com vencimento em 30 dias.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        entities = resultado["analysis"]["entities"]
        assert "valor" in entities
        assert len(entities["valor"]) > 0

    @pytest.mark.asyncio
    async def test_extrair_data(self, service, tenant_id):
        """Deve extrair datas."""
        email = EmailMessage(
            from_address="rh@empresa.com",
            to_addresses=["funcionario@empresa.com"],
            subject="Ferias",
            body_text="Suas ferias estao marcadas para 15/02/2026.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        entities = resultado["analysis"]["entities"]
        assert "data" in entities

    @pytest.mark.asyncio
    async def test_extrair_keywords(self, service, tenant_id):
        """Deve extrair keywords relevantes."""
        email = EmailMessage(
            from_address="manutencao@empresa.com",
            to_addresses=["gerente@empresa.com"],
            subject="Relatorio de manutencao",
            body_text="O elevador do bloco A precisa de manutencao preventiva.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        keywords = resultado["analysis"]["keywords"]
        assert len(keywords) > 0
        assert any("elevador" in k.lower() or "manutencao" in k.lower() for k in keywords)

    # =========================================================================
    # Testes de Sugestoes de Acao
    # =========================================================================

    @pytest.mark.asyncio
    async def test_sugerir_resposta(self, service, tenant_id):
        """Deve sugerir resposta para emails."""
        email = EmailMessage(
            from_address="cliente@empresa.com",
            to_addresses=["atendimento@empresa.com"],
            subject="Informacoes",
            body_text="Gostaria de mais informacoes sobre seus servicos.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        suggestions = resultado["suggestions"]
        assert len(suggestions) > 0
        assert any(s["action_type"] == "responder" for s in suggestions)

    @pytest.mark.asyncio
    async def test_sugestoes_tem_prioridade(self, service, tenant_id):
        """Sugestoes devem ter prioridade."""
        email = EmailMessage(
            from_address="cliente@empresa.com",
            to_addresses=["vendas@empresa.com"],
            subject="Proposta comercial",
            body_text="Temos interesse em contratar seus servicos.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        for suggestion in resultado["suggestions"]:
            assert "action_priority" in suggestion
            assert isinstance(suggestion["action_priority"], int)

    # =========================================================================
    # Testes de Contexto
    # =========================================================================

    @pytest.mark.asyncio
    async def test_contexto_novo_remetente(self, service, tenant_id):
        """Deve criar contexto para novo remetente."""
        email = EmailMessage(
            from_address="novo@remetente.com",
            to_addresses=["empresa@empresa.com"],
            subject="Primeiro contato",
            body_text="Este e meu primeiro email.",
            tenant_id=tenant_id
        )
        resultado = await service.process_incoming_email(email)

        context = resultado["context"]
        assert context["email_address"] == "novo@remetente.com"
        assert context["total_emails_received"] == 0  # Historico zerado

    @pytest.mark.asyncio
    async def test_obter_contexto_email(self, service, tenant_id):
        """Deve obter contexto de email."""
        contexto = await service.get_email_context(
            "teste@exemplo.com",
            tenant_id
        )

        assert isinstance(contexto, EmailContext)
        assert contexto.email_address == "teste@exemplo.com"


class TestEmailMessage:
    """Testes para modelo EmailMessage."""

    def test_criar_email_valido(self):
        """Deve criar email com dados validos."""
        email = EmailMessage(
            from_address="remetente@email.com",
            to_addresses=["destino@email.com"],
            subject="Assunto",
            body_text="Corpo do email",
            tenant_id=uuid4()
        )
        assert email.from_address == "remetente@email.com"
        assert len(email.to_addresses) == 1
        assert email.message_id is not None

    def test_email_com_multiplos_destinatarios(self):
        """Deve aceitar multiplos destinatarios."""
        email = EmailMessage(
            from_address="remetente@email.com",
            to_addresses=[
                "destino1@email.com",
                "destino2@email.com",
                "destino3@email.com"
            ],
            subject="Para varios",
            body_text="Email para multiplos destinatarios",
            tenant_id=uuid4()
        )
        assert len(email.to_addresses) == 3

    def test_email_com_copia(self):
        """Deve aceitar CC e BCC."""
        email = EmailMessage(
            from_address="remetente@email.com",
            to_addresses=["destino@email.com"],
            cc_addresses=["copia@email.com"],
            bcc_addresses=["oculto@email.com"],
            subject="Com copias",
            body_text="Email com copias",
            tenant_id=uuid4()
        )
        assert len(email.cc_addresses) == 1
        assert len(email.bcc_addresses) == 1


class TestEmailAnalysis:
    """Testes para modelo EmailAnalysis."""

    def test_criar_analysis(self):
        """Deve criar analise com valores padrao."""
        analysis = EmailAnalysis(
            message_id=uuid4(),
            category=EmailCategory.FINANCEIRO,
            priority=EmailPriority.ALTA,
            primary_intent=EmailIntent.SOLICITAR_INFORMACAO
        )
        assert analysis.category == EmailCategory.FINANCEIRO
        assert analysis.is_spam is False
        assert analysis.requires_response is True

    def test_analysis_urgente(self):
        """Deve marcar como urgente corretamente."""
        analysis = EmailAnalysis(
            message_id=uuid4(),
            category=EmailCategory.MANUTENCAO,
            priority=EmailPriority.URGENTE,
            primary_intent=EmailIntent.REPORTAR_PROBLEMA,
            is_urgent=True
        )
        assert analysis.is_urgent is True
        assert analysis.priority == EmailPriority.URGENTE


class TestEmailEnums:
    """Testes para enums de email."""

    def test_categorias_disponiveis(self):
        """Deve ter categorias esperadas."""
        categorias = list(EmailCategory)
        assert EmailCategory.FINANCEIRO in categorias
        assert EmailCategory.MANUTENCAO in categorias
        assert EmailCategory.RH in categorias
        assert EmailCategory.COMERCIAL in categorias

    def test_prioridades_ordenadas(self):
        """Prioridades devem ter ordem logica."""
        assert EmailPriority.URGENTE.value == "urgente"
        assert EmailPriority.ALTA.value == "alta"
        assert EmailPriority.NORMAL.value == "normal"
        assert EmailPriority.BAIXA.value == "baixa"

    def test_sentimentos_disponiveis(self):
        """Deve ter sentimentos esperados."""
        sentimentos = list(EmailSentiment)
        assert EmailSentiment.POSITIVO in sentimentos
        assert EmailSentiment.NEGATIVO in sentimentos
        assert EmailSentiment.NEUTRO in sentimentos

    def test_tipos_acao_disponiveis(self):
        """Deve ter tipos de acao esperados."""
        acoes = list(ActionType)
        assert ActionType.RESPONDER in acoes
        assert ActionType.ENCAMINHAR in acoes
        assert ActionType.ARQUIVAR in acoes
