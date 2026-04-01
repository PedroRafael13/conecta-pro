---
name: testes-unitarios-conecta-pro
description: Framework para escrever e executar testes automatizados no Conecta PRO — backend FastAPI com pytest e frontend Next.js com Jest/Vitest. Usar para garantir cobertura de endpoints críticos e prevenir regressões entre sessões de desenvolvimento.
---

# Testes Automatizados — Conecta PRO

## Stack de testes
- Backend: pytest + httpx (FastAPI TestClient)
- Frontend: Jest / Vitest + React Testing Library
- Coverage: pytest-cov para backend

## Quando usar
- Após corrigir um bug — criar teste que previne regressão
- Antes de fechar um módulo como 10/10
- Quando o Claude Code rodar cobertura de testes
- Para validar que um endpoint funciona com dados reais

## Setup inicial

```bash
# Instalar dependências de teste no container
docker exec $CONTAINER pip install pytest pytest-asyncio \
  httpx pytest-cov --break-system-packages

# Criar diretório de testes se não existir
mkdir -p /opt/conecta-pro/backend/tests/{unit,integration,e2e}

# Arquivo de configuração pytest
cat > /opt/conecta-pro/backend/pytest.ini << 'EOF'
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
EOF
```

## Padrão de teste para endpoints FastAPI

```python
# tests/integration/test_ged_kits.py
import pytest
from httpx import AsyncClient
from app.main import app

# Fixture de autenticação — reutilizar em todos os testes
@pytest.fixture
async def auth_headers():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", data={
            "username": "jjesus@conectamais.pro",
            "password": "Jordan0612"  # pragma: allowlist secret
        })
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

# Testes de listagem
class TestGEDKits:
    async def test_listar_kits_retorna_200(self, auth_headers):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/ged/kits",
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or isinstance(data, list)

    async def test_listar_kits_sem_auth_retorna_401(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/ged/kits")
        assert response.status_code == 401

    async def test_kit_invalido_retorna_404(self, auth_headers):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/ged/kits/uuid-invalido-000",
                headers=auth_headers
            )
        assert response.status_code == 404

    async def test_kit_ideal_flores_tem_19_docs(self, auth_headers):
        KIT_ID = "e3ba48aa-fedc-4a43-baab-ba6b77629b0e"
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/ged/kit-real/{KIT_ID}/checklist",
                headers=auth_headers
            )
        assert response.status_code == 200
        data = response.json()
        assert data.get("total_tipos", 0) == 19
```

## Testes E2E via curl (mais rápido para o dia a dia)

```bash
TOKEN=$(curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jjesus@conectamais.pro&password=Jordan0612" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CONTAINER=$(docker ps --filter ancestor=conecta-pro-backend \
  --format '{{.Names}}' | head -1)

# Rodar bateria de testes por módulo
python3 << 'PYEOF'
import subprocess, json

TOKEN = subprocess.run(
    "curl -sf -X POST http://127.0.0.1:8080/api/v1/auth/login "
    "-H 'Content-Type: application/x-www-form-urlencoded' "
    "-d 'username=jjesus@conectamais.pro&password=Jordan0612' "
    "| python3 -c \"import sys,json; "
    "print(json.load(sys.stdin)['access_token'])\"",
    shell=True, capture_output=True, text=True
).stdout.strip()

TESTES = {
    "GED": [
        ("GET", "/api/v1/ged/kits", 200),
        ("GET", "/api/v1/ged/clients", 200),
        ("GET", "/api/v1/ged/config/drive", 200),
        ("GET", "/api/v1/ged/reports/monthly", 200),
    ],
    "Financeiro": [
        ("GET", "/api/v1/financial/receivables", 200),
        ("GET", "/api/v1/financial/payables", 200),
    ],
    "Auth": [
        ("GET", "/api/v1/ged/kits", 401),  # sem token
    ],
}

resultados = {"pass": 0, "fail": 0}

for modulo, testes in TESTES.items():
    print(f"\n=== {modulo} ===")
    for method, path, expected in testes:
        headers = f'-H "Authorization: Bearer {TOKEN}"' \
            if expected != 401 else ""
        status = subprocess.run(
            f'curl -sf -o /dev/null -w "%{{http_code}}" '
            f'-X {method} "http://127.0.0.1:8080{path}" {headers}',
            shell=True, capture_output=True, text=True
        ).stdout.strip()

        ok = status == str(expected)
        icon = "✅" if ok else "❌"
        print(f"  {icon} {method} {path} → {status} "
              f"(esperado: {expected})")
        resultados["pass" if ok else "fail"] += 1

total = resultados["pass"] + resultados["fail"]
pct = round(resultados["pass"] / total * 100)
print(f"\nRESULTADO: {resultados['pass']}/{total} ({pct}%)")
PYEOF
```

## Testes de regressão — bugs já corrigidos

```bash
# Verificar que bugs corrigidos não voltaram

echo "=== REGRESSÃO: status paga vs pago ==="
docker exec $CONTAINER psql -U postgres -d conectapro -t -c \
  "SELECT COUNT(*) FROM receivable_accounts WHERE status='paga';"
echo "↑ Deve ser > 0 (se 0, bug voltou)"

echo "=== REGRESSÃO: URL clients sem barra ==="
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/clients" \
  -H "Authorization: Bearer $TOKEN")
[ "$STATUS" = "200" ] && echo "✅ OK" || echo "❌ FALHOU"

echo "=== REGRESSÃO: documents/search não retorna 500 ==="
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8080/api/v1/ged/documents/search" \
  -H "Authorization: Bearer $TOKEN")
[ "$STATUS" = "200" ] && echo "✅ OK" || echo "❌ FALHOU ($STATUS)"

echo "=== REGRESSÃO: Bartolo greeting tem nome do usuário ==="
GREETING=$(curl -sf -X POST \
  "http://127.0.0.1:8080/api/v1/ai/bartolo/greeting" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys,json; \
    print(json.load(sys.stdin).get('message',''))" 2>/dev/null)
echo "$GREETING" | grep -q "Jordan" && \
  echo "✅ Nome correto" || echo "❌ UUID exposto"
```

## Executar pytest no container

```bash
# Rodar todos os testes
docker exec $CONTAINER bash -c \
  "cd /app && python -m pytest tests/ -v --tb=short 2>&1" \
  | tail -30

# Rodar com cobertura
docker exec $CONTAINER bash -c \
  "cd /app && python -m pytest tests/ --cov=modules \
  --cov-report=term-missing 2>&1" | tail -40

# Rodar só testes de um módulo
docker exec $CONTAINER bash -c \
  "cd /app && python -m pytest tests/integration/test_ged_kits.py \
  -v 2>&1" | tail -20
```
