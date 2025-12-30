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
