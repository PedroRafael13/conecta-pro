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
        email: Optional[str] = None,
        name: Optional[str] = None,
        password: str = "Test@123456",
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
        user_id: Optional[str] = None,
        email: Optional[str] = None,
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
        name: Optional[str] = _UNSET,
        email: Optional[str] = _UNSET,
        phone: Optional[str] = _UNSET,
        company: Optional[str] = _UNSET,
        position: Optional[str] = _UNSET,
        company_size: Optional[str] = _UNSET,
        industry: Optional[str] = _UNSET,
        source: str = "website",
        status: str = "new",
        score: int = 50,
        probability: float = 25.0,
        expected_value: float = 10000.0,
        notes: Optional[str] = None,
        assigned_to_id: Optional[str] = None,
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
