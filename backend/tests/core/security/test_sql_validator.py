"""
Testes para SQL Validator (PATCH 02)
Valida proteção contra SQL Injection via whitelist de tabelas.
"""

import pytest

from core.security.sql_validator import InvalidTableError, SQLTableValidator, validate_table_name


class TestSQLTableValidator:
    """Testes da classe SQLTableValidator."""

    def setup_method(self):
        """Setup para cada teste."""
        self.validator = SQLTableValidator()

    def test_validate_table_name_valido(self):
        """Tabela válida deve retornar True."""
        # Arrange
        table_name = "clientes"

        # Act
        result = self.validator.validate_table_name(table_name)

        # Assert
        assert result is True

    def test_validate_table_name_invalido(self):
        """Tabela inválida deve levantar exceção."""
        # Arrange
        table_name = "users; DROP TABLE"

        # Act & Assert
        with pytest.raises((InvalidTableError, ValueError)):
            self.validator.validate_table_name(table_name)

    def test_sql_injection_comentario(self):
        """Tentativa de SQL injection com comentário deve ser bloqueada."""
        # Arrange
        table_name = "clientes--"

        # Act & Assert
        with pytest.raises((InvalidTableError, ValueError)):
            self.validator.validate_table_name(table_name)

    def test_sql_injection_union(self):
        """Tentativa de SQL injection com UNION deve ser bloqueada."""
        # Arrange
        table_name = "clientes UNION SELECT * FROM users"

        # Act & Assert
        with pytest.raises((InvalidTableError, ValueError)):
            self.validator.validate_table_name(table_name)

    def test_todas_tabelas_permitidas(self):
        """Todas as tabelas da whitelist devem ser válidas."""
        # Arrange
        allowed_tables = [
            "clientes",
            "client_contracts",
            "users",
            "employees",
            "documents",
            "nfe",
            "nfse",
            "escalas",
            "postos",
            "leads",
            "oportunidades",
            "propostas",
            "contratos",
        ]

        # Act & Assert
        for table in allowed_tables:
            assert self.validator.validate_table_name(table) is True, f"Tabela {table} deveria ser válida"

    def test_case_insensitive(self):
        """Validação deve ser case insensitive."""
        # Arrange & Act & Assert
        assert self.validator.validate_table_name("CLIENTES") is True
        assert self.validator.validate_table_name("Clientes") is True
        assert self.validator.validate_table_name("clientes") is True
        assert self.validator.validate_table_name("  clientes  ") is True

    def test_string_vazia(self):
        """String vazia deve ser inválida."""
        # Arrange
        table_name = ""

        # Act
        result = self.validator.validate_table_name(table_name, raise_on_invalid=False)

        # Assert
        assert result is False

    def test_sql_injection_ponto_virgula(self):
        """Tentativa com ponto e vírgula deve ser bloqueada."""
        # Arrange
        table_name = "clientes; DELETE FROM users"

        # Act & Assert
        with pytest.raises((InvalidTableError, ValueError)):
            self.validator.validate_table_name(table_name)

    def test_sql_injection_aspas_simples(self):
        """Tentativa com aspas simples deve ser bloqueada."""
        # Arrange
        table_name = "clientes' OR '1'='1"

        # Act & Assert
        with pytest.raises((InvalidTableError, ValueError)):
            self.validator.validate_table_name(table_name)

    def test_sql_injection_parenteses(self):
        """Tentativa com parênteses deve ser bloqueada."""
        # Arrange
        table_name = "clientes()"

        # Act & Assert
        with pytest.raises((InvalidTableError, ValueError)):
            self.validator.validate_table_name(table_name)

    def test_tabela_nao_existe(self):
        """Tabela que não existe na whitelist deve ser inválida."""
        # Arrange
        table_name = "tabela_inexistente_maliciosa"

        # Act & Assert
        with pytest.raises(InvalidTableError) as exc_info:
            self.validator.validate_table_name(table_name)

        assert "não permitida" in str(exc_info.value)

    def test_adicionar_tabela_runtime(self):
        """Deve permitir adicionar tabelas em runtime."""
        # Arrange
        nova_tabela = "tabela_custom_nova"

        # Act
        self.validator.add_allowed_table(nova_tabela)
        result = self.validator.validate_table_name(nova_tabela)

        # Assert
        assert result is True

    def test_lista_tabelas_permitidas(self):
        """Método deve retornar lista ordenada de tabelas."""
        # Act
        tables = self.validator.get_allowed_tables()

        # Assert
        assert isinstance(tables, list)
        assert len(tables) >= 70  # Pelo menos 70 tabelas na whitelist
        assert tables == sorted(tables)  # Deve estar ordenada


class TestValidateTableNameFunction:
    """Testes da função standalone validate_table_name."""

    def test_funcao_global_valido(self):
        """Função global deve validar tabela corretamente."""
        # Act & Assert
        assert validate_table_name("documents") is True
        assert validate_table_name("ged_documents") is True

    def test_funcao_global_invalido(self):
        """Função global deve levantar exceção para tabela inválida."""
        # Act & Assert
        with pytest.raises(InvalidTableError):
            validate_table_name("hackers_table")


class TestSQLInjectionScenarios:
    """Testes de cenários reais de SQL Injection."""

    def test_sql_injection_boolean_based(self):
        """Ataque boolean-based deve ser bloqueado."""
        malicious_tables = [
            "users' AND '1'='1",
            "users' AND '1'='2",
            "users' OR 'x'='x",
        ]

        for table in malicious_tables:
            with pytest.raises((InvalidTableError, ValueError)):
                validate_table_name(table)

    def test_sql_injection_time_based(self):
        """Ataque time-based deve ser bloqueado."""
        malicious_tables = [
            "users; WAITFOR DELAY '00:00:05'--",
            "users; SLEEP(5)--",
        ]

        for table in malicious_tables:
            with pytest.raises((InvalidTableError, ValueError)):
                validate_table_name(table)

    def test_sql_injection_stacked_queries(self):
        """Ataque de queries empilhadas deve ser bloqueado."""
        malicious_tables = [
            "users; INSERT INTO admin VALUES ('hacker')",
            "users; UPDATE users SET admin=1",
            "users; DROP TABLE users",
        ]

        for table in malicious_tables:
            with pytest.raises((InvalidTableError, ValueError)):
                validate_table_name(table)
