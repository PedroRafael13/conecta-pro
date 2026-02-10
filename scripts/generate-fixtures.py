#!/usr/bin/env python3
"""
generate-fixtures.py — Gera fixtures faltantes para testes pytest

Uso:
    ./scripts/generate-fixtures.py                    # Analisa e mostra fixtures faltantes
    ./scripts/generate-fixtures.py --generate         # Gera conftest.py com fixtures
    ./scripts/generate-fixtures.py --from-output FILE # Analisa output do pytest

Detecta:
- fixture 'X' not found
- Gera código Python pronto para colar no conftest.py
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BACKEND = Path("/opt/conecta-pro/backend")
TESTS_DIR = BACKEND / "tests"

# Templates de fixtures comuns
FIXTURE_TEMPLATES = {
    "async_client": '''
@pytest.fixture
async def async_client():
    """HTTP client assíncrono para testes de API."""
    from httpx import AsyncClient
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
''',
    "client": '''
@pytest.fixture
def client():
    """HTTP client síncrono para testes de API."""
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as client:
        yield client
''',
    "db_session": '''
@pytest.fixture
async def db_session():
    """Sessão de banco de dados para testes."""
    from unittest.mock import AsyncMock, MagicMock
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    yield session
''',
    "db": '''
@pytest.fixture
async def db():
    """Alias para db_session."""
    from unittest.mock import AsyncMock, MagicMock
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    yield session
''',
    "mock_redis": '''
@pytest.fixture
def mock_redis():
    """Mock do Redis para testes."""
    from unittest.mock import AsyncMock, MagicMock
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    redis.expire = AsyncMock(return_value=True)
    yield redis
''',
    "auth_headers": '''
@pytest.fixture
def auth_headers():
    """Headers de autenticação para testes de API."""
    return {"Authorization": "Bearer test-token-12345"}
''',
    "sample_tenant": '''
@pytest.fixture
def sample_tenant():
    """Tenant de exemplo para testes."""
    from unittest.mock import MagicMock
    tenant = MagicMock()
    tenant.id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    tenant.nome = "Tenant Teste"
    tenant.codigo = "TST"
    tenant.email = "test@test.com"
    tenant.status = "ATIVO"
    return tenant
''',
    "mock_repository": '''
@pytest.fixture
def mock_repository():
    """Mock genérico de repository."""
    from unittest.mock import AsyncMock, MagicMock
    repo = MagicMock()
    repo.get = AsyncMock(return_value=None)
    repo.get_all = AsyncMock(return_value=[])
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock(return_value=True)
    repo.count = AsyncMock(return_value=0)
    return repo
''',
    "mock_service": '''
@pytest.fixture
def mock_service():
    """Mock genérico de service."""
    from unittest.mock import AsyncMock, MagicMock
    service = MagicMock()
    return service
''',
    "event_loop": '''
@pytest.fixture(scope="session")
def event_loop():
    """Event loop para testes async."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
''',
}


def find_missing_fixtures_from_tests() -> dict[str, list[str]]:
    """Escaneia testes para encontrar fixtures que provavelmente faltam."""
    fixture_usage: dict[str, list[str]] = defaultdict(list)

    if not TESTS_DIR.exists():
        return fixture_usage

    # Primeiro, encontrar fixtures definidas
    defined_fixtures = set()
    for py_file in TESTS_DIR.rglob("conftest.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        for match in re.finditer(r'@pytest\.fixture.*\ndef (\w+)', content):
            defined_fixtures.add(match.group(1))

    # Escanear testes para fixtures usadas como parâmetros
    for py_file in TESTS_DIR.rglob("test_*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        # Encontrar parâmetros de funções de teste
        for match in re.finditer(r'(?:async )?def (test_\w+)\((.*?)\)', content, re.DOTALL):
            params = match.group(2)
            # Extrair nomes de parâmetros
            for param in re.findall(r'\b(\w+)\b', params):
                if param in ("self", "request", "tmp_path", "tmpdir", "capsys",
                             "capfd", "monkeypatch", "recwarn", "pytestconfig"):
                    continue
                if param not in defined_fixtures:
                    rel_path = str(py_file.relative_to(BACKEND))
                    fixture_usage[param].append(rel_path)

    return fixture_usage


def find_missing_fixtures_from_output(output_path: str) -> dict[str, int]:
    """Parseia output do pytest para encontrar 'fixture X not found'."""
    missing = Counter()

    try:
        content = Path(output_path).read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return missing

    for match in re.finditer(r"fixture '(\w+)' not found", content):
        missing[match.group(1)] += 1

    return missing


def generate_conftest(fixtures: list[str]) -> str:
    """Gera código conftest.py com as fixtures solicitadas."""
    imports = set()
    imports.add("import pytest")

    code_blocks = []

    for fixture_name in fixtures:
        if fixture_name in FIXTURE_TEMPLATES:
            template = FIXTURE_TEMPLATES[fixture_name]
            code_blocks.append(template)

            # Detectar imports necessários
            if "AsyncMock" in template:
                imports.add("from unittest.mock import AsyncMock, MagicMock")
            elif "MagicMock" in template:
                imports.add("from unittest.mock import MagicMock")
        else:
            # Gerar fixture genérica
            code_blocks.append(f'''
@pytest.fixture
def {fixture_name}():
    """Fixture auto-gerada para '{fixture_name}'. Ajuste conforme necessário."""
    from unittest.mock import MagicMock
    return MagicMock()
''')

    header = '"""Auto-generated conftest.py fixtures."""\n\n'
    import_block = "\n".join(sorted(imports))

    return header + import_block + "\n" + "\n".join(code_blocks)


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    generate_mode = "--generate" in sys.argv
    from_output = None
    for i, arg in enumerate(sys.argv):
        if arg == "--from-output" and i + 1 < len(sys.argv):
            from_output = sys.argv[i + 1]

    print("═══════════════════════════════════════════")
    print("GENERATE FIXTURES — Fixtures Faltantes")
    print("═══════════════════════════════════════════")
    print("")

    if from_output:
        missing = find_missing_fixtures_from_output(from_output)
        if not missing:
            print("✓ Nenhuma fixture faltante no output!")
            sys.exit(0)

        print(f"Fixtures faltantes ({len(missing)}):")
        for name, count in missing.most_common(20):
            template = "✓ template" if name in FIXTURE_TEMPLATES else "⚠️ genérica"
            print(f"  {name:<30} {count:>3} testes  [{template}]")
    else:
        fixture_usage = find_missing_fixtures_from_tests()
        if not fixture_usage:
            print("✓ Nenhuma fixture potencialmente faltante!")
            sys.exit(0)

        # Filtrar para fixtures conhecidas e com muitos usos
        missing = Counter()
        for name, files in fixture_usage.items():
            if len(files) >= 2 or name in FIXTURE_TEMPLATES:
                missing[name] = len(files)

        if not missing:
            print("✓ Todas as fixtures parecem definidas!")
            sys.exit(0)

        print(f"Fixtures provavelmente faltantes ({len(missing)}):")
        for name, count in missing.most_common(20):
            template = "✓ template" if name in FIXTURE_TEMPLATES else "⚠️ genérica"
            print(f"  {name:<30} {count:>3} arquivo(s)  [{template}]")

    known_fixtures = [name for name in missing if name in FIXTURE_TEMPLATES]
    unknown_fixtures = [name for name in missing if name not in FIXTURE_TEMPLATES]

    print("")
    print(f"Com template pronto: {len(known_fixtures)}")
    print(f"Precisam definição manual: {len(unknown_fixtures)}")

    if generate_mode:
        all_fixtures = known_fixtures + unknown_fixtures
        conftest_code = generate_conftest(all_fixtures)

        output_path = BACKEND / "tests" / "conftest_generated.py"
        output_path.write_text(conftest_code, encoding="utf-8")

        print("")
        print(f"═══════════════════════════════════════════")
        print(f"✓ Gerado: {output_path}")
        print(f"")
        print(f"INSTRUÇÕES:")
        print(f"  1. Revise o arquivo gerado")
        print(f"  2. Copie as fixtures necessárias para o conftest.py adequado")
        print(f"  3. Remova o arquivo gerado: rm {output_path}")
        print(f"═══════════════════════════════════════════")
    else:
        if known_fixtures:
            print("")
            print("═══════════════════════════════════════════")
            print("Para gerar conftest.py com essas fixtures:")
            print("  ./scripts/generate-fixtures.py --generate")
            print("═══════════════════════════════════════════")

    sys.exit(0)


if __name__ == "__main__":
    main()
