"""
Testes para Log Masking (PATCH 04)
Valida mascaramento de PII em logs.
"""

import pytest

from core.security.log_masking import LogMasker


class TestMaskCPF:
    """Testes de mascaramento de CPF."""

    def test_mask_cpf_formatado(self):
        """CPF formatado deve ser mascarado corretamente."""
        # Arrange
        cpf = "123.456.789-00"
        expected = "***.456.789-**"

        # Act
        result = LogMasker.mask_cpf(cpf)

        # Assert
        assert result == expected

    def test_mask_cpf_numeros(self):
        """CPF apenas números deve ser mascarado."""
        # Arrange
        cpf = "12345678900"
        expected = "***.456.789-**"

        # Act
        result = LogMasker.mask_cpf(cpf)

        # Assert
        assert result == expected

    def test_mask_cpf_vazio(self):
        """CPF vazio deve retornar string vazia."""
        # Act & Assert
        assert LogMasker.mask_cpf("") == ""
        assert LogMasker.mask_cpf(None) == ""

    def test_mask_cpf_invalido(self):
        """CPF inválido deve ser mascarado completamente."""
        # Arrange
        cpf = "123"

        # Act
        result = LogMasker.mask_cpf(cpf)

        # Assert
        assert result.startswith("***")


class TestMaskEmail:
    """Testes de mascaramento de email."""

    def test_mask_email_simples(self):
        """Email simples deve ser mascarado."""
        # Arrange
        email = "joao@empresa.com"
        expected = "j***@empresa.com"

        # Act
        result = LogMasker.mask_email(email)

        # Assert
        assert result == expected

    def test_mask_email_com_ponto(self):
        """Email com ponto deve ser mascarado."""
        # Arrange
        email = "joao.silva@empresa.com.br"

        # Act
        result = LogMasker.mask_email(email)

        # Assert
        assert result.startswith("j")
        assert "@empresa.com.br" in result

    def test_mask_email_curto(self):
        """Email curto deve ser mascarado."""
        # Arrange
        email = "ab@example.com"

        # Act
        result = LogMasker.mask_email(email)

        # Assert
        assert result == "a*@example.com"

    def test_mask_email_vazio(self):
        """Email vazio deve retornar string vazia."""
        assert LogMasker.mask_email("") == ""


class TestMaskPhone:
    """Testes de mascaramento de telefone."""

    def test_mask_phone_formatado(self):
        """Telefone formatado deve ser mascarado."""
        # Arrange
        phone = "(11) 98765-4321"
        expected = "(11) 9****-****"

        # Act
        result = LogMasker.mask_phone(phone)

        # Assert
        assert result == expected

    def test_mask_phone_numeros(self):
        """Telefone apenas números deve ser mascarado."""
        # Arrange
        phone = "11987654321"
        expected = "(11) 9****-****"

        # Act
        result = LogMasker.mask_phone(phone)

        # Assert
        assert result == expected

    def test_mask_phone_fixo(self):
        """Telefone fixo deve ser mascarado."""
        # Arrange
        phone = "(11) 3456-7890"
        expected = "(11) ****-****"

        # Act
        result = LogMasker.mask_phone(phone)

        # Assert
        assert result == expected

    def test_mask_phone_vazio(self):
        """Telefone vazio deve retornar string vazia."""
        assert LogMasker.mask_phone("") == ""


class TestMaskCNPJ:
    """Testes de mascaramento de CNPJ."""

    def test_mask_cnpj_formatado(self):
        """CNPJ formatado deve ser mascarado."""
        # Arrange
        cnpj = "12.345.678/0001-90"
        expected = "**.345.678/****-**"

        # Act
        result = LogMasker.mask_cnpj(cnpj)

        # Assert
        assert result == expected

    def test_mask_cnpj_numeros(self):
        """CNPJ apenas números deve ser mascarado."""
        # Arrange
        cnpj = "12345678000190"
        expected = "**.345.678/****-**"

        # Act
        result = LogMasker.mask_cnpj(cnpj)

        # Assert
        assert result == expected

    def test_mask_cnpj_vazio(self):
        """CNPJ vazio deve retornar string vazia."""
        assert LogMasker.mask_cnpj("") == ""


class TestMaskRG:
    """Testes de mascaramento de RG."""

    def test_mask_rg_formatado(self):
        """RG formatado deve ser mascarado."""
        # Arrange
        rg = "12.345.678-9"

        # Act
        result = LogMasker.mask_rg(rg)

        # Assert
        assert "**.345" in result

    def test_mask_rg_vazio(self):
        """RG vazio deve retornar string vazia."""
        assert LogMasker.mask_rg("") == ""


class TestSanitizeSensitiveString:
    """Testes de sanitização completa de strings."""

    def test_sanitize_log_completo(self):
        """String com múltiplos PII deve ser sanitizada."""
        # Arrange
        text = "Cliente João (CPF: 123.456.789-00, email: joao@empresa.com, tel: (11) 98765-4321)"

        # Act
        result = LogMasker.mask_sensitive_string(text)

        # Assert
        assert "123.456.789-00" not in result
        assert "***.456.789-**" in result
        assert "joao@empresa.com" not in result
        assert "@empresa.com" in result
        assert "98765-4321" not in result
        assert "(11) 9****-****" in result

    def test_sanitize_multiple_emails(self):
        """String com múltiplos emails deve ser sanitizada."""
        # Arrange
        text = "Contatos: joao@empresa.com, maria@empresa.com"

        # Act
        result = LogMasker.mask_sensitive_string(text)

        # Assert
        assert "joao@empresa.com" not in result
        assert "maria@empresa.com" not in result

    def test_sanitize_cnpj(self):
        """CNPJ em string deve ser mascarado."""
        # Arrange
        text = "Empresa CNPJ: 12.345.678/0001-90 cadastrada"

        # Act
        result = LogMasker.mask_sensitive_string(text)

        # Assert
        assert "12.345.678/0001-90" not in result
        assert "**.345.678/****-**" in result

    def test_sanitize_texto_sem_pii(self):
        """Texto sem PII deve permanecer igual."""
        # Arrange
        text = "Operação realizada com sucesso no módulo financeiro"

        # Act
        result = LogMasker.mask_sensitive_string(text)

        # Assert
        assert result == text


class TestMaskDict:
    """Testes de mascaramento de dicionários."""

    def test_mask_dict_cpf_email(self):
        """Dicionário com CPF e email deve ser mascarado."""
        # Arrange
        data = {"nome": "João Silva", "cpf": "123.456.789-00", "email": "joao@empresa.com", "ativo": True}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["nome"] == "João Silva"  # Nome não é mascarado
        assert result["cpf"] == "***.456.789-**"
        assert result["email"] == "j***@empresa.com"
        assert result["ativo"] is True

    def test_mask_dict_telefone(self):
        """Dicionário com telefone deve ser mascarado."""
        # Arrange
        data = {"nome": "Maria", "telefone": "(11) 98765-4321", "celular": "11987654321"}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert "(11) 9****-****" in result["telefone"]
        assert "(11) 9****-****" in result["celular"]

    def test_mask_dict_nested(self):
        """Dicionário aninhado deve ser mascarado recursivamente."""
        # Arrange
        data = {"usuario": {"nome": "João", "cpf": "123.456.789-00"}, "contato": {"email": "joao@email.com"}}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["usuario"]["cpf"] == "***.456.789-**"
        assert "j***@email.com" in result["contato"]["email"]

    def test_mask_dict_list(self):
        """Lista em dicionário deve ser processada."""
        # Arrange
        data = {"usuarios": [{"nome": "João", "cpf": "123.456.789-00"}, {"nome": "Maria", "cpf": "987.654.321-00"}]}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["usuarios"][0]["cpf"] == "***.456.789-**"
        assert result["usuarios"][1]["cpf"] == "***.654.321-**"

    def test_mask_dict_nao_mascara(self):
        """Campos não sensíveis não devem ser alterados."""
        # Arrange
        data = {"id": "550e8400-e29b-41d4-a716-446655440000", "nome": "João Silva", "status": "ativo", "valor": 123.45}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["nome"] == "João Silva"
        assert result["status"] == "ativo"
        assert result["valor"] == 123.45


class TestMaskSenhaToken:
    """Testes de mascaramento de senhas e tokens."""

    def test_mask_senha(self):
        """Campo senha deve ser mascarado completamente."""
        # Arrange
        data = {"senha": "minha_senha_secreta123"}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["senha"] == "***"

    def test_mask_password(self):
        """Campo password deve ser mascarado completamente."""
        # Arrange
        data = {"password": "my_secret_password"}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["password"] == "***"

    def test_mask_token(self):
        """Campo token deve ser mascarado completamente."""
        # Arrange
        data = {"token": "test-token-value-for-masking"}

        # Act
        result = LogMasker.mask_dict(data)

        # Assert
        assert result["token"] == "***"
