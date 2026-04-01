"""
Factories para criacao de dados de teste.
Usa factory_boy + Faker para gerar dados realistas.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from faker import Faker

from core.auth.security import get_password_hash
from core.models.user import User, UserRole

fake = Faker("pt_BR")


class UserFactory:
    """Factory para criar usuarios de teste."""

    @staticmethod
    def build(
        email: str | None = None,
        name: str | None = None,
        password: str = "Test@123456",  # noqa: S107
        role: UserRole = UserRole.OPERATOR,
        is_active: bool = True,
        **kwargs,
    ) -> User:
        """
        Cria um objeto User sem salvar no banco.

        Args:
            email: Email do usuario (gerado se nao fornecido)
            name: Nome do usuario (gerado se nao fornecido)
            password: Senha em texto plano
            role: Role do usuario
            is_active: Se usuario esta ativo
            **kwargs: Campos adicionais

        Returns:
            Objeto User
        """
        return User(
            id=kwargs.get("id", uuid.uuid4()),
            email=email or fake.email(),
            name=name or fake.name(),
            password_hash=get_password_hash(password),
            phone=kwargs.get("phone", fake.phone_number()),
            role=role.value if isinstance(role, UserRole) else role,
            is_active=is_active,
            created_at=kwargs.get("created_at", datetime.utcnow()),
            updated_at=kwargs.get("updated_at", datetime.utcnow()),
            last_login=kwargs.get("last_login"),
            notes=kwargs.get("notes"),
        )

    @staticmethod
    def build_admin(**kwargs) -> User:
        """Cria usuario admin."""
        return UserFactory.build(role=UserRole.ADMIN, **kwargs)

    @staticmethod
    def build_super_admin(**kwargs) -> User:
        """Cria super admin."""
        return UserFactory.build(role=UserRole.SUPER_ADMIN, **kwargs)

    @staticmethod
    def build_inactive(**kwargs) -> User:
        """Cria usuario inativo."""
        return UserFactory.build(is_active=False, **kwargs)

    @staticmethod
    def build_batch(count: int, **kwargs) -> list[User]:
        """Cria multiplos usuarios."""
        return [UserFactory.build(**kwargs) for _ in range(count)]


class TokenFactory:
    """Factory para criar tokens de teste."""

    @staticmethod
    def build_valid_payload(
        user_id: str | None = None,
        email: str | None = None,
        role: str = "operator",
    ) -> dict:
        """Cria payload de token valido."""
        return {
            "sub": user_id or str(uuid.uuid4()),
            "email": email or fake.email(),
            "role": role,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

    @staticmethod
    def build_expired_payload(**kwargs) -> dict:
        """Cria payload de token expirado."""
        payload = TokenFactory.build_valid_payload(**kwargs)
        payload["exp"] = datetime.utcnow() - timedelta(hours=1)
        return payload


# Dados de teste padrao
TEST_USER_DATA = {
    "email": "test@erp.local",
    "name": "Usuario Teste",
    "password": "Test@123456",
}

TEST_ADMIN_DATA = {
    "email": "admin@erp.local",
    "name": "Admin Teste",
    "password": "Admin@123456",
}


# Sentinel para diferenciar None explícito de parâmetro não fornecido
_UNSET = object()


class LeadFactory:
    """Factory para criar leads de teste."""

    @staticmethod
    def build(
        name: str | None = _UNSET,
        email: str | None = _UNSET,
        phone: str | None = _UNSET,
        company: str | None = _UNSET,
        position: str | None = _UNSET,
        company_size: str | None = _UNSET,
        industry: str | None = _UNSET,
        source: str = "website",
        status: str = "new",
        score: int = 50,
        probability: float = 25.0,
        expected_value: float = 10000.0,
        notes: str | None = None,
        assigned_to_id: str | None = None,
        **kwargs,
    ):
        """
        Cria dados de Lead para testes.

        Returns:
            Dicionário com dados do lead
        """
        from modules.crm.models.lead import Lead

        return Lead(
            id=kwargs.get("id", str(uuid.uuid4())),
            name=fake.name() if name is _UNSET else name,
            email=fake.email() if email is _UNSET else email,
            phone=fake.phone_number() if phone is _UNSET else phone,
            company=fake.company() if company is _UNSET else company,
            position=fake.job() if position is _UNSET else position,
            company_size="medium" if company_size is _UNSET else company_size,
            industry="condominios" if industry is _UNSET else industry,
            source=source,
            status=status,
            score=score,
            probability=probability,
            expected_value=expected_value,
            notes=notes,
            assigned_to_id=assigned_to_id,
            created_at=kwargs.get("created_at", datetime.utcnow()),
            updated_at=kwargs.get("updated_at", datetime.utcnow()),
            last_contact_at=kwargs.get("last_contact_at"),
            next_contact_at=kwargs.get("next_contact_at"),
            is_active=kwargs.get("is_active", True),
        )

    @staticmethod
    def build_hot_lead(**kwargs):
        """Cria lead quente (score alto)."""
        return LeadFactory.build(
            score=85,
            probability=70.0,
            status="qualified",
            company_size="enterprise",
            industry="condominios",
            **kwargs,
        )

    @staticmethod
    def build_cold_lead(**kwargs):
        """Cria lead frio (score baixo)."""
        return LeadFactory.build(
            score=25,
            probability=10.0,
            status="new",
            company_size="micro",
            company=None,
            **kwargs,
        )

    @staticmethod
    def build_batch(count: int, **kwargs) -> list:
        """Cria múltiplos leads."""
        return [LeadFactory.build(**kwargs) for _ in range(count)]


TEST_LEAD_DATA = {
    "name": "Lead Teste",
    "email": "lead@empresa.com",
    "phone": "(11) 99999-9999",
    "company": "Empresa Teste",
    "position": "Gerente",
    "company_size": "medium",
    "industry": "condominios",
    "source": "website",
    "expected_value": 15000.0,
    "notes": "Lead interessado no produto",
}


class OpportunityFactory:
    """Factory para criar opportunities de teste."""

    @staticmethod
    def build(
        title: str | None = _UNSET,
        contact_name: str | None = _UNSET,
        contact_email: str | None = _UNSET,
        contact_phone: str | None = _UNSET,
        company_name: str | None = _UNSET,
        description: str | None = None,
        lead_id: str | None = None,
        stage: str = "qualification",
        priority: str = "medium",
        value: float = 10000.0,
        probability: int = 25,
        expected_close_date=None,
        actual_close_date=None,
        owner_id: str | None = None,
        loss_reason: str | None = None,
        competitor: str | None = None,
        win_notes: str | None = None,
        loss_notes: str | None = None,
        notes: str | None = None,
        **kwargs,
    ):
        """
        Cria dados de Opportunity para testes.

        Returns:
            Objeto Opportunity
        """
        from modules.crm.models.opportunity import Opportunity

        return Opportunity(
            id=kwargs.get("id", str(uuid.uuid4())),
            title=f"Oportunidade {fake.company()}" if title is _UNSET else title,
            description=description,
            lead_id=lead_id,
            contact_name=fake.name() if contact_name is _UNSET else contact_name,
            contact_email=fake.email() if contact_email is _UNSET else contact_email,
            contact_phone=fake.phone_number() if contact_phone is _UNSET else contact_phone,
            company_name=fake.company() if company_name is _UNSET else company_name,
            stage=stage,
            priority=priority,
            value=value,
            probability=probability,
            expected_close_date=expected_close_date,
            actual_close_date=actual_close_date,
            owner_id=owner_id,
            loss_reason=loss_reason,
            competitor=competitor,
            win_notes=win_notes,
            loss_notes=loss_notes,
            notes=notes,
            created_at=kwargs.get("created_at", datetime.utcnow()),
            updated_at=kwargs.get("updated_at", datetime.utcnow()),
            is_active=kwargs.get("is_active", True),
        )

    @staticmethod
    def build_won(**kwargs):
        """Cria opportunity ganha."""
        from datetime import date

        defaults = {
            "stage": "closed_won",
            "probability": 100,
            "actual_close_date": date.today(),
            "win_notes": "Fechamos o negocio!",
        }
        defaults.update(kwargs)
        return OpportunityFactory.build(**defaults)

    @staticmethod
    def build_lost(**kwargs):
        """Cria opportunity perdida."""
        from datetime import date

        defaults = {
            "stage": "closed_lost",
            "probability": 0,
            "actual_close_date": date.today(),
            "loss_reason": "price",
            "loss_notes": "Perdemos por preco",
        }
        defaults.update(kwargs)
        return OpportunityFactory.build(**defaults)

    @staticmethod
    def build_high_value(**kwargs):
        """Cria opportunity de alto valor."""
        return OpportunityFactory.build(
            value=100000.0,
            probability=50,
            priority="high",
            stage="proposal",
            **kwargs,
        )

    @staticmethod
    def build_batch(count: int, **kwargs) -> list:
        """Cria multiplas opportunities."""
        return [OpportunityFactory.build(**kwargs) for _ in range(count)]


TEST_OPPORTUNITY_DATA = {
    "title": "Oportunidade Teste",
    "contact_name": "Contato Teste",
    "contact_email": "contato@empresa.com",
    "contact_phone": "(11) 99999-9999",
    "company_name": "Empresa Teste",
    "value": 25000.0,
    "probability": 50,
    "notes": "Oportunidade promissora",
}


class ProposalFactory:
    """Factory para criar proposals de teste."""

    _counter = 0

    @staticmethod
    def _next_number() -> str:
        """Gera numero de proposta unico."""
        ProposalFactory._counter += 1
        return f"PROP-{datetime.utcnow().strftime('%Y%m%d')}-{ProposalFactory._counter:06d}"

    @staticmethod
    def build(
        title: str | None = _UNSET,
        description: str | None = None,
        client_name: str | None = _UNSET,
        client_email: str | None = _UNSET,
        client_phone: str | None = _UNSET,
        client_company: str | None = _UNSET,
        client_document: str | None = None,
        client_address: str | None = None,
        proposal_type: str = "service",
        status: str = "draft",
        subtotal: float = 10000.0,
        discount_type: str | None = None,
        discount_value: float = 0.0,
        taxes: float = 0.0,
        total: float = 10000.0,
        terms_conditions: str | None = None,
        payment_terms: str | None = None,
        payment_conditions: str | None = None,
        installments: int = 1,
        valid_until=_UNSET,
        opportunity_id: str | None = None,
        template_id: str | None = None,
        created_by_id: str | None = None,
        **kwargs,
    ):
        """
        Cria dados de Proposal para testes.

        Returns:
            Objeto Proposal
        """
        from datetime import date

        from modules.crm.models.proposal import Proposal

        return Proposal(
            id=kwargs.get("id", str(uuid.uuid4())),
            number=kwargs.get("number", ProposalFactory._next_number()),
            version=kwargs.get("version", 1),
            parent_id=kwargs.get("parent_id"),
            opportunity_id=opportunity_id,
            template_id=template_id,
            title=f"Proposta {fake.company()}" if title is _UNSET else title,
            description=description,
            proposal_type=proposal_type,
            client_name=fake.name() if client_name is _UNSET else client_name,
            client_email=fake.email() if client_email is _UNSET else client_email,
            client_phone=fake.phone_number() if client_phone is _UNSET else client_phone,
            client_company=fake.company() if client_company is _UNSET else client_company,
            client_document=client_document,
            client_address=client_address,
            subtotal=subtotal,
            discount_type=discount_type,
            discount_value=discount_value,
            taxes=taxes,
            total=total,
            terms_conditions=terms_conditions,
            payment_terms=payment_terms,
            payment_conditions=payment_conditions,
            installments=installments,
            issue_date=kwargs.get("issue_date", date.today()),
            valid_until=date.today() + timedelta(days=30) if valid_until is _UNSET else valid_until,
            sent_at=kwargs.get("sent_at"),
            viewed_at=kwargs.get("viewed_at"),
            responded_at=kwargs.get("responded_at"),
            status=status,
            rejection_reason=kwargs.get("rejection_reason"),
            notes=kwargs.get("notes"),
            created_by_id=created_by_id,
            approved_by_id=kwargs.get("approved_by_id"),
            approved_at=kwargs.get("approved_at"),
            created_at=kwargs.get("created_at", datetime.utcnow()),
            updated_at=kwargs.get("updated_at", datetime.utcnow()),
            is_active=kwargs.get("is_active", True),
        )

    @staticmethod
    def build_approved(**kwargs):
        """Cria proposal aprovada."""
        defaults = {
            "status": "approved",
            "approved_at": datetime.utcnow(),
            "approved_by_id": str(uuid.uuid4()),
        }
        defaults.update(kwargs)
        return ProposalFactory.build(**defaults)

    @staticmethod
    def build_sent(**kwargs):
        """Cria proposal enviada."""
        defaults = {
            "status": "sent",
            "sent_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return ProposalFactory.build_approved(**defaults)

    @staticmethod
    def build_accepted(**kwargs):
        """Cria proposal aceita."""
        defaults = {
            "status": "accepted",
            "responded_at": datetime.utcnow(),
        }
        defaults.update(kwargs)
        return ProposalFactory.build_sent(**defaults)

    @staticmethod
    def build_rejected(**kwargs):
        """Cria proposal rejeitada."""
        defaults = {
            "status": "rejected",
            "responded_at": datetime.utcnow(),
            "rejection_reason": "Preco muito alto",
        }
        defaults.update(kwargs)
        return ProposalFactory.build_sent(**defaults)

    @staticmethod
    def build_expired(**kwargs):
        """Cria proposal expirada."""
        from datetime import date

        defaults = {
            "status": "expired",
            "valid_until": date.today() - timedelta(days=5),
        }
        defaults.update(kwargs)
        return ProposalFactory.build(**defaults)

    @staticmethod
    def build_high_value(**kwargs):
        """Cria proposal de alto valor."""
        return ProposalFactory.build(
            subtotal=100000.0,
            total=100000.0,
            proposal_type="project",
            **kwargs,
        )

    @staticmethod
    def build_batch(count: int, **kwargs) -> list:
        """Cria multiplas proposals."""
        return [ProposalFactory.build(**kwargs) for _ in range(count)]


class ProposalItemFactory:
    """Factory para criar proposal items de teste."""

    @staticmethod
    def build(
        proposal_id: str | None = None,
        code: str | None = None,
        name: str | None = _UNSET,
        description: str | None = None,
        unit: str = "un",
        quantity: float = 1.0,
        unit_price: float = 1000.0,
        discount_percent: float = 0.0,
        sort_order: int = 0,
        is_optional: bool = False,
        **kwargs,
    ):
        """Cria dados de ProposalItem para testes."""
        from modules.crm.models.proposal import ProposalItem

        # subtotal e discount_amount são properties, não colunas
        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount_percent / 100)
        total = subtotal - discount_amount

        return ProposalItem(
            id=kwargs.get("id", str(uuid.uuid4())),
            proposal_id=proposal_id or str(uuid.uuid4()),
            code=code or f"PROD-{uuid.uuid4().hex[:6].upper()}",
            name=fake.word().capitalize() if name is _UNSET else name,
            description=description,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            discount_percent=discount_percent,
            total=total,  # calculado
            sort_order=sort_order,
            is_optional=is_optional,
            created_at=kwargs.get("created_at", datetime.utcnow()),
            updated_at=kwargs.get("updated_at", datetime.utcnow()),
            is_active=kwargs.get("is_active", True),
        )

    @staticmethod
    def build_batch(count: int, proposal_id: str | None = None, **kwargs) -> list:
        """Cria multiplos items."""
        return [ProposalItemFactory.build(proposal_id=proposal_id, sort_order=i, **kwargs) for i in range(count)]


class ProposalTemplateFactory:
    """Factory para criar proposal templates de teste."""

    @staticmethod
    def build(
        name: str | None = _UNSET,
        description: str | None = None,
        default_title: str | None = None,
        default_description: str | None = None,
        terms_conditions: str | None = None,
        payment_terms: str | None = None,
        validity_days: int = 30,
        proposal_type: str = "service",
        header_html: str | None = None,
        footer_html: str | None = None,
        css_styles: str | None = None,
        is_default: bool = False,
        **kwargs,
    ):
        """Cria dados de ProposalTemplate para testes."""
        from modules.crm.models.proposal import ProposalTemplate

        return ProposalTemplate(
            id=kwargs.get("id", str(uuid.uuid4())),
            name=f"Template {fake.word().capitalize()}" if name is _UNSET else name,
            description=description,
            default_title=default_title,
            default_description=default_description,
            terms_conditions=terms_conditions or "Termos e condicoes padrao",
            payment_terms=payment_terms or "Pagamento em 30 dias",
            validity_days=validity_days,
            proposal_type=proposal_type,
            header_html=header_html,
            footer_html=footer_html,
            css_styles=css_styles,
            is_default=is_default,
            created_at=kwargs.get("created_at", datetime.utcnow()),
            updated_at=kwargs.get("updated_at", datetime.utcnow()),
            is_active=kwargs.get("is_active", True),
        )

    @staticmethod
    def build_default(**kwargs):
        """Cria template padrao."""
        return ProposalTemplateFactory.build(is_default=True, **kwargs)

    @staticmethod
    def build_batch(count: int, **kwargs) -> list:
        """Cria multiplos templates."""
        return [ProposalTemplateFactory.build(**kwargs) for _ in range(count)]


TEST_PROPOSAL_DATA = {
    "title": "Proposta Comercial Teste",
    "client_name": "Cliente Teste",
    "client_email": "cliente@empresa.com",
    "client_phone": "(11) 99999-9999",
    "client_company": "Empresa Teste",
    "proposal_type": "service",
    "terms_conditions": "Termos e condicoes de teste",
    "payment_terms": "30 dias",
    "installments": 1,
}

TEST_PROPOSAL_ITEM_DATA = {
    "code": "SERV-001",
    "name": "Servico de Teste",
    "description": "Descricao do servico",
    "unit": "un",
    "quantity": 1.0,
    "unit_price": 5000.0,
    "discount_percent": 0.0,
}
