"""
Testes do modelo de usuário e RBAC.
"""

import pytest
from pydantic import ValidationError

from core.models.user import ROLE_HIERARCHY, User, UserRole
from core.schemas.user import UserCreate, UserUpdate


class TestUserRole:
    """Testes dos roles de usuário."""

    def test_role_values(self):
        """Testa valores dos roles."""
        assert UserRole.SUPER_ADMIN.value == "super_admin"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.SUPERVISOR.value == "supervisor"
        assert UserRole.OPERATOR.value == "operator"
        assert UserRole.CLIENT.value == "client"
        assert UserRole.VIEWER.value == "viewer"

    def test_role_hierarchy(self):
        """Testa hierarquia de roles."""
        assert ROLE_HIERARCHY[UserRole.SUPER_ADMIN] > ROLE_HIERARCHY[UserRole.ADMIN]
        assert ROLE_HIERARCHY[UserRole.ADMIN] > ROLE_HIERARCHY[UserRole.MANAGER]
        assert ROLE_HIERARCHY[UserRole.MANAGER] > ROLE_HIERARCHY[UserRole.SUPERVISOR]
        assert ROLE_HIERARCHY[UserRole.SUPERVISOR] > ROLE_HIERARCHY[UserRole.OPERATOR]
        assert ROLE_HIERARCHY[UserRole.OPERATOR] > ROLE_HIERARCHY[UserRole.CLIENT]
        assert ROLE_HIERARCHY[UserRole.CLIENT] > ROLE_HIERARCHY[UserRole.VIEWER]


class TestUserModel:
    """Testes do modelo User."""

    def test_has_role_same_level(self):
        """Testa has_role com mesmo nível."""
        user = User(
            email="test@example.com",
            password_hash="hash",
            name="Test User",
            role=UserRole.MANAGER.value,
        )

        assert user.has_role(UserRole.MANAGER) is True

    def test_has_role_higher_level(self):
        """Testa has_role com nível superior."""
        user = User(
            email="admin@example.com",
            password_hash="hash",
            name="Admin User",
            role=UserRole.ADMIN.value,
        )

        assert user.has_role(UserRole.MANAGER) is True
        assert user.has_role(UserRole.OPERATOR) is True

    def test_has_role_lower_level(self):
        """Testa has_role com nível inferior."""
        user = User(
            email="operator@example.com",
            password_hash="hash",
            name="Operator User",
            role=UserRole.OPERATOR.value,
        )

        assert user.has_role(UserRole.MANAGER) is False
        assert user.has_role(UserRole.ADMIN) is False

    def test_has_permission_super_admin(self):
        """Testa que super_admin tem todas as permissões."""
        user = User(
            email="super@example.com",
            password_hash="hash",
            name="Super Admin",
            role=UserRole.SUPER_ADMIN.value,
            permissions=[],
        )

        assert user.has_permission("any_permission") is True
        assert user.has_permission("delete_all") is True

    def test_has_permission_specific(self):
        """Testa permissão específica."""
        user = User(
            email="user@example.com",
            password_hash="hash",
            name="User",
            role=UserRole.OPERATOR.value,
            permissions=["read_reports", "create_tickets"],
        )

        assert user.has_permission("read_reports") is True
        assert user.has_permission("create_tickets") is True
        assert user.has_permission("delete_users") is False

    def test_has_permission_empty(self):
        """Testa usuário sem permissões extras."""
        user = User(
            email="user@example.com",
            password_hash="hash",
            name="User",
            role=UserRole.OPERATOR.value,
            permissions=None,
        )

        assert user.has_permission("any_permission") is False


class TestUserSchemas:
    """Testes dos schemas de usuário."""

    def test_user_create_valid(self):
        """Testa criação de usuário válido."""
        user = UserCreate(
            email="test@example.com",
            name="Test User",
            password="StrongPass123!@#",
            role=UserRole.OPERATOR,
        )

        assert user.email == "test@example.com"
        assert user.name == "Test User"

    def test_user_create_weak_password(self):
        """Testa criação com senha fraca."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                name="Test User",
                password="weak",  # muito curta
            )

        # Verifica erro de tamanho mínimo (12 caracteres)
        error_msg = str(exc_info.value)
        assert "12" in error_msg or "at least" in error_msg.lower()

    def test_user_create_no_uppercase(self):
        """Testa senha sem maiúsculas."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                name="Test User",
                password="password123!",  # sem maiúscula, mas 13 chars
            )

        assert "maiúscula" in str(exc_info.value).lower() or "uppercase" in str(exc_info.value).lower()

    def test_user_create_no_lowercase(self):
        """Testa senha sem minúsculas."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                name="Test User",
                password="PASSWORD123!",  # sem minúscula, mas 13 chars
            )

        assert "minúscula" in str(exc_info.value).lower() or "lowercase" in str(exc_info.value).lower()

    def test_user_create_no_number(self):
        """Testa senha sem números."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                name="Test User",
                password="PasswordStrong",  # sem número
            )

        assert "número" in str(exc_info.value)

    def test_user_create_invalid_email(self):
        """Testa email inválido."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                name="Test User",
                password="StrongPass123",
            )

    def test_user_update_partial(self):
        """Testa atualização parcial."""
        update = UserUpdate(name="New Name")

        assert update.name == "New Name"
        assert update.phone is None
        assert update.role is None

    def test_user_update_role(self):
        """Testa atualização de role."""
        update = UserUpdate(role=UserRole.MANAGER)

        assert update.role == UserRole.MANAGER
