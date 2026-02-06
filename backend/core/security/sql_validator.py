"""
PATCH 02: Módulo de Validação SQL - Whitelist de Tabelas
Data: 2026-02-05
Severidade: CRÍTICO

Proteção contra SQL Injection em queries dinâmicas.
Usado em: deduplicator, lgpd_compliance, document_versioning
"""


class InvalidTableError(Exception):
    """Exceção lançada quando uma tabela não está na whitelist."""

    def __init__(self, table_name: str, allowed_tables: set[str] = None):
        self.table_name = table_name
        self.allowed_tables = allowed_tables
        message = f"Tabela '{table_name}' não permitida para consulta dinâmica."
        if allowed_tables:
            message += f" Tabelas permitidas: {', '.join(sorted(allowed_tables))}"
        super().__init__(message)


class SQLTableValidator:
    """
    Validador de nomes de tabelas para queries dinâmicas.

    Implementa whitelist de tabelas permitidas para prevenir SQL Injection
    via nomes de tabelas dinâmicas.

    Uso:
        validator = SQLTableValidator()
        if validator.validate_table_name("clientes"):
            query = f"SELECT * FROM {table_name} WHERE id = :id"
    """

    # Whitelist de tabelas permitidas para queries dinâmicas
    # Adicione apenas tabelas que REALMENTE precisam ser acessadas dinamicamente
    ALLOWED_TABLES: set[str] = {
        # Clientes
        "clients",
        "clientes",
        "condominiums",
        "condominios",
        "units",
        "unidades",
        "client_contracts",
        "contratos_cliente",
        # Financeiro
        "financial_accounts",
        "contas_financeiras",
        "payable_accounts",
        "contas_pagar",
        "receivable_accounts",
        "contas_receber",
        "invoices",
        "notas_fiscais",
        "nfe",
        "nfse",
        # RH/Funcionários
        "employees",
        "funcionarios",
        "payroll_records",
        "folhas_pagamento",
        "time_entries",
        "registros_ponto",
        # Operacional
        "posts",
        "postos",
        "shifts",
        "turnos",
        "scales",
        "escalas",
        "occurrences",
        "ocorrencias",
        "diarists",
        "diaristas",
        # Documentos
        "documents",
        "documentos",
        "document_versions",
        "versoes_documento",
        "document_kits",
        "kits_documento",
        "folders",
        "pastas",
        # CRM
        "leads",
        "oportunidades",
        "opportunities",
        "proposals",
        "propostas",
        "contracts",
        "contratos",
        # Configurações e Segurança
        "users",
        "usuarios",
        "user_consents",
        "consentimentos",
        "audit_logs",
        "logs_auditoria",
        "tenants",
        # Relatórios e Analytics
        "reports",
        "relatorios",
        "dashboards",
        # Licitações
        "tenders",
        "licitacoes",
        "bidding_proposals",
        "propostas_licitacao",
        # GED
        "ged_documents",
        "ged_pastas",
        "document_signatures",
        "assinaturas",
        # Integrações
        "sync_logs",
        "webhook_logs",
        "integration_settings",
        # Documentos Fiscais (ETL/Government)
        "documentos_fiscais_nfe",
        "documentos_fiscais_nfce",
        "documentos_fiscais_cte",
        "documentos_fiscais_mdfe",
        "documentos_fiscais_nfse",
        "eventos_esocial",
        "guias_fgts",
        "eventos_reinf",
        "documentos_historico",
        # LGPD Compliance
        "dependentes",
        "enderecos",
        "contatos",
        "folha_pagamento",
    }

    # Caracteres proibidos em nomes de tabelas
    FORBIDDEN_CHARS: set[str] = {
        ";",
        "--",
        "/*",
        "*/",
        "'",
        '"',
        " ",
        "\t",
        "\n",  # Whitespace
        "(",
        ")",  # Parênteses (possível função SQL)
    }

    def __init__(self, additional_tables: set[str] = None):
        """
        Inicializa o validador.

        Args:
            additional_tables: Conjunto adicional de tabelas permitidas
                              (além das padrões na ALLOWED_TABLES)
        """
        self.allowed_tables = self.ALLOWED_TABLES.copy()
        if additional_tables:
            self.allowed_tables.update(additional_tables)

    def validate_table_name(self, table_name: str, raise_on_invalid: bool = True) -> bool:
        """
        Valida se um nome de tabela está na whitelist.

        Args:
            table_name: Nome da tabela a validar
            raise_on_invalid: Se True, levanta exceção em caso inválido

        Returns:
            True se válido, False se inválido (e raise_on_invalid=False)

        Raises:
            InvalidTableError: Se tabela não permitida e raise_on_invalid=True
            ValueError: Se nome de tabela contém caracteres proibidos
        """
        if not table_name or not isinstance(table_name, str):
            if raise_on_invalid:
                raise InvalidTableError(str(table_name), self.allowed_tables)
            return False

        # Normaliza para lowercase e strip
        normalized = table_name.lower().strip()

        # Verifica caracteres proibidos
        for char in self.FORBIDDEN_CHARS:
            if char in normalized:
                if raise_on_invalid:
                    raise ValueError(f"Nome de tabela contém caracter proibido: '{char}'")
                return False

        # Verifica se está na whitelist
        if normalized not in self.allowed_tables:
            if raise_on_invalid:
                raise InvalidTableError(table_name, self.allowed_tables)
            return False

        return True

    def get_allowed_tables(self) -> list[str]:
        """Retorna lista ordenada de tabelas permitidas."""
        return sorted(self.allowed_tables)

    def add_allowed_table(self, table_name: str):
        """Adiciona uma tabela à whitelist (runtime only)."""
        self.allowed_tables.add(table_name.lower().strip())


# Função helper para uso rápido
_validator = SQLTableValidator()


def validate_table_name(table_name: str, raise_on_invalid: bool = True) -> bool:
    """
    Função standalone para validar nome de tabela.

    Uso:
        from security.sql_validator import validate_table_name

        # Em código:
        if validate_table_name(table_name):
            query = text(f"SELECT * FROM {table_name} WHERE id = :id")
    """
    return _validator.validate_table_name(table_name, raise_on_invalid)


def sanitize_table_name(table_name: str, default: str = None) -> str:
    """
    Sanitiza nome de tabela, retornando default se inválido.

    Uso seguro em templates:
        table = sanitize_table_name(user_input, default='clientes')
        query = f"SELECT * FROM {table} WHERE ..."
    """
    try:
        if validate_table_name(table_name, raise_on_invalid=True):
            return table_name.lower().strip()
    except (InvalidTableError, ValueError):
        pass

    if default is not None:
        return default

    raise InvalidTableError(table_name, _validator.allowed_tables)


# ============================================
# EXEMPLOS DE USO E TESTES
# ============================================

if __name__ == "__main__":
    # Testes do validador
    validator = SQLTableValidator()

    # Testes válidos
    assert validator.validate_table_name("clientes")
    assert validator.validate_table_name("CLIENTES")  # Case insensitive
    assert validator.validate_table_name("  clientes  ")  # Strip whitespace

    # Testes inválidos
    try:
        validator.validate_table_name("users; DROP TABLE users--")
        raise AssertionError("Deveria ter levantado exceção")
    except (InvalidTableError, ValueError):
        pass

    try:
        validator.validate_table_name("tabela_inexistente")
        raise AssertionError("Deveria ter levantado exceção")
    except InvalidTableError as e:
        print(f"✓ Exceção correta: {e}")

    # Teste da função helper
    assert validate_table_name("documents")

    # Teste de sanitização
    assert sanitize_table_name("clientes", default="users") == "clientes"
    assert sanitize_table_name("invalido", default="users") == "users"

    print("✓ Todos os testes passaram!")
    print(f"✓ Total de tabelas na whitelist: {len(validator.allowed_tables)}")
