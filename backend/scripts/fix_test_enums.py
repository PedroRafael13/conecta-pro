#!/usr/bin/env python3
"""
Script de correção em massa de enums em testes.
Parte do plano de melhoria de qualidade: Score 72 → 99+
"""

from pathlib import Path

# Mapeamento de enums errados → corretos
ENUM_MAPPINGS: dict[str, list[tuple[str, str]]] = {
    # AuditCategory
    "AuditCategory": [
        ("DATA", "DATA_ACCESS"),
        ("USER", "USER_MANAGEMENT"),
    ],
    # DataCategory
    "DataCategory": [
        ("CUSTOMER", "PERSONAL"),
        ("CLIENT", "PERSONAL"),
        ("USER_DATA", "PERSONAL"),
    ],
    # DashboardStatus
    "DashboardStatus": [
        ("PUBLISHED", "ACTIVE"),
        ("ENABLED", "ACTIVE"),
        ("DISABLED", "INACTIVE"),
    ],
    # ReportType
    "ReportType": [
        ("FINANCIAL_SUMMARY", "KPI_SUMMARY"),
        ("SUMMARY", "KPI_SUMMARY"),
        ("FINANCIAL", "INCOME_STATEMENT"),
    ],
    # ForecastStatus
    "ForecastStatus": [
        ("ATIVO", "ATIVA"),
        ("ACTIVE", "ATIVA"),
        ("DRAFT", "RASCUNHO"),
        ("COMPLETED", "CONCLUIDA"),
        ("ARCHIVED", "ARQUIVADA"),
    ],
    # ClientStatus
    "ClientStatus": [
        ("ACTIVE", "ATIVO"),
        ("INACTIVE", "INATIVO"),
        ("SUSPENDED", "SUSPENSO"),
        ("BLOCKED", "BLOQUEADO"),
        ("CANCELLED", "CANCELADO"),
    ],
    # ClientType
    "ClientType": [
        ("PJ", "EMPRESA"),
        ("PF", "RESIDENCIAL"),
        ("CORPORATE", "EMPRESA"),
        ("INDIVIDUAL", "RESIDENCIAL"),
    ],
    # ServiceCategory
    "ServiceCategory": [
        ("MANUTENCAO_PREDIAL", "MANUTENCAO"),
        ("BUILDING_MAINTENANCE", "MANUTENCAO"),
        ("SECURITY", "SEGURANCA"),
        ("CLEANING", "LIMPEZA"),
        ("GARDENING", "JARDINAGEM"),
        ("TECHNOLOGY", "TECNOLOGIA"),
        ("CONSULTING", "CONSULTORIA"),
        ("TRAINING", "TREINAMENTO"),
        ("SUPPORT", "SUPORTE"),
        ("OTHER", "OUTROS"),
    ],
    # LeadStatus
    "LeadStatus": [
        ("CONVERTED", "WON"),
        ("LOST", "LOST"),
    ],
    # ContractStatus
    "ContractStatus": [
        ("ACTIVE", "ATIVO"),
        ("INACTIVE", "INATIVO"),
        ("EXPIRED", "EXPIRADO"),
        ("CANCELLED", "CANCELADO"),
    ],
    # OccurrenceStatus
    "OccurrenceStatus": [
        ("OPEN", "ABERTA"),
        ("CLOSED", "FECHADA"),
        ("IN_PROGRESS", "EM_ANDAMENTO"),
        ("PENDING", "PENDENTE"),
    ],
    # PaymentStatus
    "PaymentStatus": [
        ("PAID", "PAGO"),
        ("PENDING", "PENDENTE"),
        ("OVERDUE", "VENCIDO"),
        ("CANCELLED", "CANCELADO"),
    ],
}

# Padrões de substituição direta (campo.VALOR)
DIRECT_PATTERNS: list[tuple[str, str]] = []

# Gerar padrões a partir do mapeamento
for enum_class, mappings in ENUM_MAPPINGS.items():
    for old_val, new_val in mappings:
        DIRECT_PATTERNS.append((f"{enum_class}.{old_val}", f"{enum_class}.{new_val}"))


def fix_file(filepath: Path) -> tuple[int, list[str]]:
    """Corrige um arquivo e retorna o número de substituições feitas."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return 0, [f"Erro ao ler {filepath}: {e}"]

    original = content
    changes = []

    for old_pattern, new_pattern in DIRECT_PATTERNS:
        if old_pattern in content:
            count = content.count(old_pattern)
            content = content.replace(old_pattern, new_pattern)
            changes.append(f"  {old_pattern} → {new_pattern} ({count}x)")

    if content != original:
        try:
            filepath.write_text(content, encoding="utf-8")
            return len(changes), changes
        except Exception as e:
            return 0, [f"Erro ao escrever {filepath}: {e}"]

    return 0, []


def main():
    """Executa a correção em todos os arquivos de teste."""
    tests_dir = Path("tests")

    if not tests_dir.exists():
        print("Diretório tests/ não encontrado!")
        return

    total_fixes = 0
    files_fixed = 0
    all_changes = []

    test_files = list(tests_dir.glob("test_*.py"))
    print(f"Analisando {len(test_files)} arquivos de teste...")
    print()

    for filepath in sorted(test_files):
        fixes, changes = fix_file(filepath)
        if fixes > 0:
            files_fixed += 1
            total_fixes += fixes
            print(f"✅ {filepath.name}: {fixes} correções")
            all_changes.extend(changes)

    print()
    print("=" * 60)
    print("RESUMO:")
    print(f"  Arquivos corrigidos: {files_fixed}")
    print(f"  Total de correções: {total_fixes}")
    print("=" * 60)

    if all_changes:
        print("\nSubstituições realizadas:")
        # Agrupar e contar
        from collections import Counter

        change_counts = Counter(all_changes)
        for change, _count in change_counts.most_common(20):
            print(f"  {change}")


if __name__ == "__main__":
    main()
