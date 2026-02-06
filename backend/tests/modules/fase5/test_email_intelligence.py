"""
tests/modules/fase5/test_email_intelligence.py - Email Intelligence Tests
==========================================================================
Testes para Email Intelligence
"""

import pytest
from uuid import uuid4

from modules.fase5.email_intelligence.models import EmailMessage, EmailContext
from modules.fase5.email_intelligence.enums import (
    EmailCategory,
    EmailPriority,
    EmailIntent,
    SentimentType,
    ActionType
)


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

    def test_email_subject_obrigatorio(self):
        """Subject deve ser obrigatorio."""
        email = EmailMessage(
            from_address="remetente@email.com",
            to_addresses=["destino@email.com"],
            subject="Teste",
            body_text="Corpo",
            tenant_id=uuid4()
        )
        assert email.subject == "Teste"

    def test_email_tenant_id(self):
        """Deve ter tenant_id."""
        tid = uuid4()
        email = EmailMessage(
            from_address="remetente@email.com",
            to_addresses=["destino@email.com"],
            subject="Teste",
            body_text="Corpo",
            tenant_id=tid
        )
        assert email.tenant_id == tid


class TestEmailContext:
    """Testes para modelo EmailContext."""

    def test_criar_contexto(self):
        """Deve criar contexto valido."""
        contexto = EmailContext(
            email_address="teste@email.com"
        )
        assert contexto.email_address == "teste@email.com"
        assert contexto.total_emails_received == 0
        assert contexto.is_cliente is False

    def test_contexto_com_historico(self):
        """Deve aceitar historico."""
        contexto = EmailContext(
            email_address="cliente@empresa.com",
            total_emails_received=15,
            total_emails_sent=8,
            is_cliente=True,
            cliente_nome="Empresa ABC"
        )
        assert contexto.total_emails_received == 15
        assert contexto.total_emails_sent == 8
        assert contexto.is_cliente is True
        assert contexto.cliente_nome == "Empresa ABC"


class TestEmailEnumsBasicos:
    """Testes basicos para enums."""

    def test_email_category_existe(self):
        """EmailCategory deve existir."""
        assert EmailCategory is not None
        assert len(list(EmailCategory)) > 0

    def test_email_priority_existe(self):
        """EmailPriority deve existir."""
        assert EmailPriority is not None
        assert len(list(EmailPriority)) > 0

    def test_email_intent_existe(self):
        """EmailIntent deve existir."""
        assert EmailIntent is not None
        assert len(list(EmailIntent)) > 0

    def test_sentiment_type_existe(self):
        """SentimentType deve existir."""
        assert SentimentType is not None
        assert len(list(SentimentType)) > 0

    def test_action_type_existe(self):
        """ActionType deve existir."""
        assert ActionType is not None
        assert len(list(ActionType)) > 0
