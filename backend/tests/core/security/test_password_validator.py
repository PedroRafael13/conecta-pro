"""Testes para o validador de força de senha."""

import pytest

from core.security.password_validator import validate_password_strength


class TestValidatePasswordStrength:
    """Testes para validate_password_strength()."""

    def test_senha_valida(self):
        """Senha que atende todos os critérios deve ser válida."""
        is_valid, errors = validate_password_strength("MinhaSenh@123!")
        assert is_valid is True
        assert errors == []

    def test_senha_curta(self):
        """Senha com menos de 12 caracteres deve falhar."""
        is_valid, errors = validate_password_strength("Short1!a")
        assert is_valid is False
        assert any("12 caracteres" in e for e in errors)

    def test_sem_maiuscula(self):
        """Senha sem letras maiúsculas deve falhar."""
        is_valid, errors = validate_password_strength("minhasenha123!@")
        assert is_valid is False
        assert any("maiúscula" in e for e in errors)

    def test_sem_minuscula(self):
        """Senha sem letras minúsculas deve falhar."""
        is_valid, errors = validate_password_strength("MINHASENHA123!@")
        assert is_valid is False
        assert any("minúscula" in e for e in errors)

    def test_sem_numero(self):
        """Senha sem números deve falhar."""
        is_valid, errors = validate_password_strength("MinhaSenha!@#$")
        assert is_valid is False
        assert any("número" in e for e in errors)

    def test_sem_especial(self):
        """Senha sem caractere especial deve falhar."""
        is_valid, errors = validate_password_strength("MinhaSenha1234")
        assert is_valid is False
        assert any("especial" in e for e in errors)

    def test_senha_comum_en(self):
        """Senha na lista de senhas comuns (EN) deve falhar."""
        # password123 tem menos de 12 chars, mas testamos a lógica de senha comum
        is_valid, errors = validate_password_strength("password")
        assert is_valid is False
        assert any("comuns" in e for e in errors)

    def test_senha_comum_ptbr(self):
        """Senha na lista de senhas comuns (PT-BR) deve falhar."""
        is_valid, errors = validate_password_strength("corinthians")
        assert is_valid is False
        assert any("comuns" in e for e in errors)

    def test_senha_comum_case_insensitive(self):
        """Verificação de senhas comuns deve ser case-insensitive."""
        is_valid, errors = validate_password_strength("PASSWORD")
        assert is_valid is False
        assert any("comuns" in e for e in errors)

    def test_caracteres_repetidos(self):
        """4+ caracteres repetidos consecutivos deve falhar."""
        is_valid, errors = validate_password_strength("Minhaaaa1234!@")
        assert is_valid is False
        assert any("repetidos" in e for e in errors)

    def test_multiplos_erros(self):
        """Senha com múltiplos problemas deve retornar todos os erros."""
        is_valid, errors = validate_password_strength("abc")
        assert is_valid is False
        assert len(errors) >= 3  # curta, sem maiúscula, sem número, sem especial, etc.

    def test_senha_forte_com_todos_tipos(self):
        """Senha forte complexa deve ser válida."""
        is_valid, errors = validate_password_strength("C0mpl3x@Pass!2026")
        assert is_valid is True
        assert errors == []

    def test_exatamente_12_caracteres(self):
        """Senha com exatamente 12 caracteres válidos deve ser aceita."""
        is_valid, errors = validate_password_strength("Abcdef1234!@")
        assert is_valid is True
        assert errors == []

    def test_3_repetidos_ok(self):
        """3 caracteres repetidos (não 4) deve ser aceito."""
        is_valid, errors = validate_password_strength("Minhaaa12345!@")
        assert is_valid is True
        assert errors == []
