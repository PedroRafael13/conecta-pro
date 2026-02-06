"""Testes para o sistema de logging."""

import pytest

from core.logging.logger import (
    configure_logging,
    get_logger,
    sanitize_message,
    sanitize_record,
    sanitizing_filter,
)


class TestSanitizeMessage:
    """Testes para sanitização de mensagens."""

    def test_sanitize_password_json(self):
        """Testa sanitização de password em JSON."""
        msg = '{"email": "test@test.com", "password": "secret123"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result
        assert "secret123" not in result

    def test_sanitize_senha_json(self):
        """Testa sanitização de senha em JSON."""
        msg = '{"email": "test@test.com", "senha": "minhasenha"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result
        assert "minhasenha" not in result

    def test_sanitize_token_json(self):
        """Testa sanitização de token em JSON."""
        msg = '{"token": "abc123xyz"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result
        assert "abc123xyz" not in result

    def test_sanitize_access_token(self):
        """Testa sanitização de access_token."""
        msg = '{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result

    def test_sanitize_refresh_token(self):
        """Testa sanitização de refresh_token."""
        msg = '{"refresh_token": "refresh123"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result

    def test_sanitize_api_key(self):
        """Testa sanitização de api_key."""
        msg = '{"api_key": "sk-123456789"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result

    def test_sanitize_secret(self):
        """Testa sanitização de secret."""
        msg = '{"secret": "mysecretvalue"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result

    def test_sanitize_cpf_json(self):
        """Testa sanitização de CPF em JSON."""
        msg = '{"cpf": "12345678901"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result

    def test_sanitize_cnpj_json(self):
        """Testa sanitização de CNPJ em JSON."""
        msg = '{"cnpj": "12345678901234"}'
        result = sanitize_message(msg)
        assert "[REDACTED]" in result

    def test_sanitize_password_query(self):
        """Testa sanitização de password em query string."""
        msg = "password=secret123&email=test@test.com"
        result = sanitize_message(msg)
        assert "[REDACTED]" in result
        assert "secret123" not in result

    def test_sanitize_bearer_token(self):
        """Testa sanitização de Bearer token."""
        msg = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = sanitize_message(msg)
        assert "Bearer [REDACTED]" in result

    def test_sanitize_cpf_formatted(self):
        """Testa sanitização de CPF formatado."""
        msg = "CPF do cliente: 123.456.789-01"
        result = sanitize_message(msg)
        assert "[CPF_REDACTED]" in result

    def test_sanitize_cnpj_formatted(self):
        """Testa sanitização de CNPJ formatado."""
        msg = "CNPJ da empresa: 12.345.678/0001-90"
        result = sanitize_message(msg)
        assert "[CNPJ_REDACTED]" in result

    def test_no_sanitization_needed(self):
        """Testa mensagem sem dados sensíveis."""
        msg = "Usuario logou com sucesso"
        result = sanitize_message(msg)
        assert result == msg

    def test_case_insensitive(self):
        """Testa sanitização case insensitive."""
        msg = '{"PASSWORD": "secret", "Token": "abc"}'
        result = sanitize_message(msg)
        assert "secret" not in result
        assert "abc" not in result


class TestSanitizeRecord:
    """Testes para sanitização de records."""

    def test_sanitize_record_message(self):
        """Testa sanitização do campo message."""
        record = {"message": '{"password": "secret"}'}
        result = sanitize_record(record)
        assert "[REDACTED]" in result["message"]

    def test_sanitize_record_extra(self):
        """Testa sanitização do campo extra."""
        record = {
            "message": "test",
            "extra": {"data": '{"token": "abc123"}'},
        }
        result = sanitize_record(record)
        assert "[REDACTED]" in result["extra"]["data"]

    def test_sanitize_record_no_extra(self):
        """Testa record sem extra."""
        record = {"message": "test"}
        result = sanitize_record(record)
        assert result["message"] == "test"

    def test_sanitize_record_non_string_extra(self):
        """Testa record com extra não-string."""
        record = {
            "message": "test",
            "extra": {"count": 123, "active": True},
        }
        result = sanitize_record(record)
        assert result["extra"]["count"] == 123
        assert result["extra"]["active"] is True


class TestSanitizingFilter:
    """Testes para o filtro de sanitização."""

    def test_filter_returns_true(self):
        """Testa que filtro sempre retorna True."""
        record = {"message": "test"}
        result = sanitizing_filter(record)
        assert result is True

    def test_filter_sanitizes(self):
        """Testa que filtro sanitiza."""
        record = {"message": '{"password": "secret"}'}
        sanitizing_filter(record)
        assert "[REDACTED]" in record["message"]


class TestConfigureLogging:
    """Testes para configuração de logging."""

    def test_configure_logging_runs(self):
        """Testa que configure_logging executa sem erro."""
        # Não deve lançar exceção
        configure_logging()

    def test_get_logger(self):
        """Testa obtenção de logger."""
        log = get_logger("test_module")
        assert log is not None
