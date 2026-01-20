"""
Testes do Validation Engine.

Testes para validacao de CPF, CNPJ, email, telefone,
datas e regras customizadas.
"""

import pytest
from modules.documents.models.validation_result import (
    BUILTIN_VALIDATORS,
    ValidationRule,
    ValidationSeverity,
    ValidationType,
    validate_cep,
    validate_cnpj,
    validate_cpf,
    validate_email,
    validate_phone_br,
)


class TestCPFValidation:
    """Testes de validacao de CPF."""

    def test_cpf_valido(self):
        """Testa CPF valido."""
        # CPFs validos
        assert validate_cpf("529.982.247-25") is True
        assert validate_cpf("52998224725") is True
        assert validate_cpf("111.444.777-35") is True

    def test_cpf_invalido(self):
        """Testa CPF invalido."""
        # CPFs invalidos
        assert validate_cpf("529.982.247-26") is False  # Digito errado
        assert validate_cpf("111.111.111-11") is False  # Todos iguais
        assert validate_cpf("000.000.000-00") is False  # Zeros
        assert validate_cpf("123.456.789") is False  # Incompleto
        assert validate_cpf("abc.def.ghi-jk") is False  # Letras

    def test_cpf_formatos_diversos(self):
        """Testa CPF em diversos formatos."""
        cpf = "52998224725"
        assert validate_cpf(cpf) is True
        assert validate_cpf("529.982.247-25") is True
        assert validate_cpf("529 982 247 25") is True


class TestCNPJValidation:
    """Testes de validacao de CNPJ."""

    def test_cnpj_valido(self):
        """Testa CNPJ valido."""
        assert validate_cnpj("11.222.333/0001-81") is True
        assert validate_cnpj("11222333000181") is True

    def test_cnpj_invalido(self):
        """Testa CNPJ invalido."""
        assert validate_cnpj("11.222.333/0001-82") is False
        assert validate_cnpj("11.111.111/1111-11") is False
        assert validate_cnpj("00.000.000/0000-00") is False
        assert validate_cnpj("12.345.678/0001") is False


class TestEmailValidation:
    """Testes de validacao de email."""

    def test_email_valido(self):
        """Testa emails validos."""
        assert validate_email("teste@email.com") is True
        assert validate_email("usuario.nome@empresa.com.br") is True
        assert validate_email("user+tag@domain.io") is True

    def test_email_invalido(self):
        """Testa emails invalidos."""
        assert validate_email("sem-arroba.com") is False
        assert validate_email("@semdominio.com") is False
        assert validate_email("teste@") is False
        assert validate_email("teste") is False


class TestPhoneValidation:
    """Testes de validacao de telefone."""

    def test_telefone_celular(self):
        """Testa telefone celular (11 digitos)."""
        assert validate_phone_br("11999887766") is True
        assert validate_phone_br("(11) 99988-7766") is True
        assert validate_phone_br("+55 11 99988-7766") is True

    def test_telefone_fixo(self):
        """Testa telefone fixo (10 digitos)."""
        assert validate_phone_br("1133445566") is True
        assert validate_phone_br("(11) 3344-5566") is True

    def test_telefone_invalido(self):
        """Testa telefones invalidos."""
        assert validate_phone_br("123456") is False  # Muito curto
        assert validate_phone_br("12345678901234") is False  # Muito longo


class TestCEPValidation:
    """Testes de validacao de CEP."""

    def test_cep_valido(self):
        """Testa CEP valido."""
        assert validate_cep("01310-100") is True
        assert validate_cep("01310100") is True
        assert validate_cep("12345-678") is True

    def test_cep_invalido(self):
        """Testa CEP invalido."""
        assert validate_cep("1234-567") is False  # Incompleto
        assert validate_cep("123456789") is False  # Muito longo
        assert validate_cep("abcde-fgh") is False  # Letras


class TestValidationRule:
    """Testes de regras de validacao."""

    def test_criar_regra(self):
        """Testa criacao de regra."""
        rule = ValidationRule(
            name="cpf_rule",
            field_name="cpf",
            validation_type=ValidationType.CPF,
            error_message="CPF invalido",
        )

        assert rule.name == "cpf_rule"
        assert rule.validation_type == ValidationType.CPF
        assert rule.is_active is True

    def test_format_error_message(self):
        """Testa formatacao de mensagem de erro."""
        rule = ValidationRule(
            name="length_rule",
            field_name="nome",
            validation_type=ValidationType.LENGTH,
            error_message="Tamanho invalido",
            error_message_template="Campo {field} deve ter entre {min_length} e {max_length} caracteres",
            min_length=3,
            max_length=100,
            params={"min_length": 3, "max_length": 100},
        )

        msg = rule.format_error_message("Jo")
        assert "3" in msg
        assert "100" in msg

    def test_regra_to_dict(self):
        """Testa conversao para dicionario."""
        rule = ValidationRule(
            name="test",
            field_name="campo",
            validation_type=ValidationType.REQUIRED,
            error_message="Campo obrigatorio",
        )

        data = rule.to_dict()
        assert data["name"] == "test"
        assert data["validation_type"] == "required"


class TestBuiltinValidators:
    """Testa dicionario de validadores."""

    def test_validators_disponiveis(self):
        """Testa validadores disponiveis."""
        assert ValidationType.CPF in BUILTIN_VALIDATORS
        assert ValidationType.CNPJ in BUILTIN_VALIDATORS
        assert ValidationType.EMAIL in BUILTIN_VALIDATORS
        assert ValidationType.PHONE in BUILTIN_VALIDATORS
        assert ValidationType.CEP in BUILTIN_VALIDATORS

    def test_usar_validator_dict(self):
        """Testa uso do dicionario de validadores."""
        cpf_validator = BUILTIN_VALIDATORS[ValidationType.CPF]
        assert cpf_validator("52998224725") is True
        assert cpf_validator("11111111111") is False
