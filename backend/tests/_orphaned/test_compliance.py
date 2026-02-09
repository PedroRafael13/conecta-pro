"""
Testes para módulo de compliance (auditoria, mascaramento, LGPD).
"""

# Importar módulos a testar
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

sys.path.insert(0, "/opt/conecta-pro/backend/modules/government_integrations")

from core.compliance.audit_logger import (
    AuditEvent,
    AuditLogger,
    TipoEvento,
)
from core.compliance.data_masking import (
    MascaradorDados,
    TipoDadoSensivel,
    mascarar_cartao,
    mascarar_cnpj,
    mascarar_cpf,
    mascarar_email,
    mascarar_generico,
    mascarar_nome,
    mascarar_telefone,
)


class TestMascararCPF:
    """Testes para mascaramento de CPF."""

    def test_mascarar_cpf_formatado(self):
        """Deve mascarar CPF mantendo últimos 3 dígitos."""
        resultado = mascarar_cpf("123.456.789-00")
        assert "***" in resultado
        assert "789" in resultado

    def test_mascarar_cpf_sem_formatacao(self):
        """Deve mascarar CPF sem formatação."""
        resultado = mascarar_cpf("12345678900")
        assert "***" in resultado

    def test_mascarar_cpf_vazio(self):
        """Deve retornar string vazia para CPF vazio."""
        assert mascarar_cpf("") == ""
        assert mascarar_cpf(None) == ""


class TestMascararCNPJ:
    """Testes para mascaramento de CNPJ."""

    def test_mascarar_cnpj_formatado(self):
        """Deve mascarar CNPJ mantendo primeiros dígitos."""
        resultado = mascarar_cnpj("12.345.678/0001-90")
        assert "12." in resultado
        assert "***" in resultado

    def test_mascarar_cnpj_sem_formatacao(self):
        """Deve mascarar CNPJ sem formatação."""
        resultado = mascarar_cnpj("12345678000190")
        assert "12." in resultado

    def test_mascarar_cnpj_vazio(self):
        """Deve retornar string vazia para CNPJ vazio."""
        assert mascarar_cnpj("") == ""


class TestMascararEmail:
    """Testes para mascaramento de email."""

    def test_mascarar_email_valido(self):
        """Deve mascarar email mantendo domínio."""
        resultado = mascarar_email("usuario@empresa.com.br")
        assert "@empresa.com.br" in resultado
        assert "***" in resultado

    def test_mascarar_email_curto(self):
        """Deve mascarar email com usuário curto."""
        resultado = mascarar_email("ab@empresa.com")
        assert "@empresa.com" in resultado

    def test_mascarar_email_invalido(self):
        """Deve retornar placeholder para email sem @."""
        resultado = mascarar_email("nao_eh_email")
        assert "@" in resultado


class TestMascararTelefone:
    """Testes para mascaramento de telefone."""

    def test_mascarar_telefone_celular(self):
        """Deve mascarar celular mantendo DDD e últimos 2 dígitos."""
        resultado = mascarar_telefone("(11) 99999-8888")
        assert "(11)" in resultado
        assert "88" in resultado
        assert "****" in resultado

    def test_mascarar_telefone_fixo(self):
        """Deve mascarar telefone fixo."""
        resultado = mascarar_telefone("1133334444")
        assert "(11)" in resultado

    def test_mascarar_telefone_vazio(self):
        """Deve retornar string vazia para telefone vazio."""
        assert mascarar_telefone("") == ""


class TestMascararCartao:
    """Testes para mascaramento de cartão de crédito."""

    def test_mascarar_cartao_completo(self):
        """Deve mascarar cartão mantendo últimos 4 dígitos."""
        resultado = mascarar_cartao("4111111111111111")
        assert "****" in resultado
        assert "1111" in resultado

    def test_mascarar_cartao_formatado(self):
        """Deve mascarar cartão formatado."""
        resultado = mascarar_cartao("4111 1111 1111 1111")
        assert "1111" in resultado

    def test_mascarar_cartao_vazio(self):
        """Deve retornar string vazia para cartão vazio."""
        assert mascarar_cartao("") == ""


class TestMascararNome:
    """Testes para mascaramento de nome."""

    def test_mascarar_nome_completo(self):
        """Deve mascarar nome mantendo iniciais."""
        resultado = mascarar_nome("João da Silva")
        # Deve conter iniciais mascaradas
        assert "." in resultado

    def test_mascarar_nome_simples(self):
        """Deve mascarar nome simples."""
        resultado = mascarar_nome("João")
        assert "J" in resultado
        assert "***" in resultado


class TestMascararGenerico:
    """Testes para mascaramento genérico."""

    def test_mascarar_manter_inicio(self):
        """Deve manter caracteres do início."""
        resultado = mascarar_generico("123456789", manter_inicio=3)
        assert resultado.startswith("123")
        assert "***" in resultado or "*" in resultado

    def test_mascarar_manter_fim(self):
        """Deve manter caracteres do fim."""
        resultado = mascarar_generico("123456789", manter_fim=3)
        assert resultado.endswith("789")

    def test_mascarar_manter_ambos(self):
        """Deve manter início e fim."""
        resultado = mascarar_generico("123456789", manter_inicio=2, manter_fim=2)
        assert resultado.startswith("12")
        assert resultado.endswith("89")


class TestMascaradorDados:
    """Testes para a classe MascaradorDados."""

    def setup_method(self):
        """Setup para cada teste."""
        self.mascarador = MascaradorDados()

    def test_mascarar_dicionario_simples(self):
        """Deve mascarar campos sensíveis em dicionário."""
        dados = {
            "nome": "João da Silva",
            "cpf": "12345678900",
            "email": "joao@email.com",
            "idade": 30,
        }

        resultado = self.mascarador.mascarar(dados)

        assert "***" in resultado["nome"] or "." in resultado["nome"]
        assert "***" in resultado["cpf"]
        assert "@" in resultado["email"]
        assert resultado["idade"] == 30  # Não sensível

    def test_mascarar_dicionario_aninhado(self):
        """Deve mascarar campos em dicionários aninhados."""
        dados = {
            "funcionario": {
                "nome": "Maria Santos",
                "cpf": "98765432100",
            },
            "departamento": "TI",
        }

        resultado = self.mascarador.mascarar(dados)

        assert "***" in resultado["funcionario"]["cpf"]
        assert resultado["departamento"] == "TI"

    def test_mascarar_lista(self):
        """Deve mascarar campos em listas de dicionários."""
        dados = {
            "funcionarios": [
                {"nome": "João", "cpf": "11111111111"},
                {"nome": "Maria", "cpf": "22222222222"},
            ]
        }

        resultado = self.mascarador.mascarar(dados)

        for func in resultado["funcionarios"]:
            assert "***" in func["cpf"]

    def test_excluir_campos(self):
        """Deve excluir campos do mascaramento."""
        dados = {
            "cpf": "12345678900",
            "cpf_backup": "12345678900",
        }

        resultado = self.mascarador.mascarar(dados, campos_excluir=["cpf_backup"])

        assert "***" in resultado["cpf"]
        assert resultado["cpf_backup"] == "12345678900"

    def test_mascarar_senha(self):
        """Deve mascarar completamente campos de senha."""
        dados = {
            "usuario": "admin",
            "senha": "minha_senha_secreta",
            "password": "outra_senha",
        }

        resultado = self.mascarador.mascarar(dados)

        assert resultado["senha"] == "********"
        assert resultado["password"] == "********"

    def test_obter_campos_sensiveis(self):
        """Deve listar campos sensíveis encontrados."""
        dados = {
            "nome": "João",
            "cpf": "12345678900",
            "endereco": {
                "email": "joao@email.com",
            },
        }

        campos = self.mascarador.obter_campos_sensiveis(dados)

        assert "nome" in campos
        assert "cpf" in campos
        assert "endereco.email" in campos


class TestAuditLogger:
    """Testes para o logger de auditoria."""

    def setup_method(self):
        """Setup para cada teste."""
        self.logger = AuditLogger(db_session=None, mascarar_dados=True)

    def test_criar_evento_consulta(self):
        """Deve criar evento de consulta."""
        evento = AuditEvent(
            tenant_id=uuid4(),
            usuario_id=uuid4(),
            tipo=TipoEvento.CONSULTA,
            recurso="nfe",
            recurso_id="123",
            acao="Consulta de NF-e",
        )

        assert evento.tipo == TipoEvento.CONSULTA
        assert evento.recurso == "nfe"
        assert evento.sucesso is True

    def test_evento_to_dict(self):
        """Deve converter evento para dicionário."""
        tenant_id = uuid4()
        evento = AuditEvent(
            tenant_id=tenant_id,
            tipo=TipoEvento.CRIACAO,
            recurso="funcionario",
        )

        resultado = evento.to_dict()

        assert resultado["tenant_id"] == str(tenant_id)
        assert resultado["tipo"] == "criacao"
        assert resultado["recurso"] == "funcionario"
        assert "timestamp" in resultado

    def test_mascarar_evento(self):
        """Deve mascarar dados sensíveis no evento."""
        evento = AuditEvent(
            tenant_id=uuid4(),
            tipo=TipoEvento.ATUALIZACAO,
            recurso="funcionario",
            dados_antes={"cpf": "12345678900", "nome": "João"},
            dados_depois={"cpf": "12345678900", "nome": "João Silva"},
        )

        evento_mascarado = self.logger._mascarar_evento(evento)

        assert "***" in evento_mascarado.dados_antes["cpf"]
        assert "***" in evento_mascarado.dados_depois["cpf"]

    def test_calcular_hash(self):
        """Deve calcular hash de integridade."""
        evento = AuditEvent(
            tenant_id=uuid4(),
            tipo=TipoEvento.CONSULTA,
            recurso="teste",
        )

        hash1 = self.logger._calcular_hash(evento)
        hash2 = self.logger._calcular_hash(evento)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256

    def test_mascarar_campos_sensiveis(self):
        """Deve mascarar lista predefinida de campos sensíveis."""
        dados = {
            "senha": "minhasenha123",
            "token": "abc123xyz",
            "api_key": "key-12345",
            "nome_publico": "Empresa ABC",
        }

        resultado = self.logger._mascarar_dict(dados)

        assert "****" in resultado["senha"]
        assert "****" in resultado["token"]
        assert "****" in resultado["api_key"]
        assert resultado["nome_publico"] == "Empresa ABC"


class TestTiposEvento:
    """Testes para tipos de evento."""

    def test_tipo_consulta(self):
        """Deve ter tipo CONSULTA."""
        assert TipoEvento.CONSULTA.value == "consulta"

    def test_tipo_criacao(self):
        """Deve ter tipo CRIACAO."""
        assert TipoEvento.CRIACAO.value == "criacao"

    def test_tipo_envio_governo(self):
        """Deve ter tipo ENVIO_GOVERNO."""
        assert TipoEvento.ENVIO_GOVERNO.value == "envio_governo"

    def test_tipo_acesso_dados_pessoais(self):
        """Deve ter tipo ACESSO_DADOS_PESSOAIS."""
        assert TipoEvento.ACESSO_DADOS_PESSOAIS.value == "acesso_dados_pessoais"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
