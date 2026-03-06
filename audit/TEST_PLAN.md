# 📋 PLANO DE TESTES - CONECTA PRO

**Data:** 2026-02-11
**Objetivo:** Garantir qualidade e confiabilidade para produção

---

## 1. TESTES UNITÁRIOS (EXISTENTES)

### Backend (Python/Pytest)
```bash
cd /opt/conecta-pro/backend
python3 -m pytest tests/ -v --cov=backend --cov-report=html
```

**Módulos Cobertos:**
| Módulo | Localização | Status |
|--------|-------------|--------|
| Core | tests/core/ | ✅ 85%+ |
| Domains | tests/domains/ | ✅ 80%+ |
| Modules | tests/modules/ | ✅ 75%+ |
| API | tests/api/ | ✅ 80%+ |

### Frontend (Vitest)
```bash
cd /opt/conecta-pro/frontend
npm test -- --run --coverage
```

**Módulos Cobertos:**
| Módulo | Localização | Status |
|--------|-------------|--------|
| Components UI | src/components/ui/__tests__/ | ✅ 557 testes |
| Hooks | src/hooks/__tests__/ | ✅ 100+ testes |
| Services | src/services/__tests__/ | ✅ 60+ testes |
| Lib/Utils | src/lib/__tests__/ | ✅ 200+ testes |

---

## 2. TESTES DE INTEGRAÇÃO

### API Integration (Supertest/pytest)
```bash
# Requer backend rodando
pytest tests/integration/ -v
```

**Endpoints Críticos a Testar:**
- [ ] POST /api/v1/auth/login
- [ ] POST /api/v1/auth/refresh
- [ ] GET /api/v1/users/me
- [ ] CRUD Reembolsos
- [ ] CRUD Ocorrências
- [ ] Upload/Download Documentos

### Banco de Dados
```bash
# Testar migrações
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

---

## 3. TESTES E2E (A CRIAR)

### Framework Recomendado: Playwright
```bash
cd /opt/conecta-pro/frontend
npm install -D @playwright/test
npx playwright install
```

### Estrutura de Testes E2E
```
e2e/
├── auth/
│   └── login.spec.ts
├── reembolso/
│   ├── criar-solicitacao.spec.ts
│   ├── aprovar-reembolso.spec.ts
│   └── fluxo-completo.spec.ts
├── operacional/
│   ├── registrar-ocorrencia.spec.ts
│   └── consultar-rondas.spec.ts
├── crm/
│   └── gerenciar-clientes.spec.ts
└── mobile/
    └── responsividade.spec.ts
```

### Matriz de Prioridade E2E

| Módulo | Fluxo Crítico | Prioridade | Status |
|--------|--------------|------------|--------|
| **Auth** | Login/Logout/JWT Refresh | P0 | A criar |
| **Reembolso** | Criar → Submeter → Aprovar | P0 | A criar |
| **Operacional** | Registrar Ocorrência | P0 | A criar |
| **GED** | Upload → Visualizar | P1 | A criar |
| **CRM** | Cadastrar Cliente | P1 | A criar |
| **Financeiro** | Criar Orçamento | P1 | A criar |
| **Mobile** | Navegação Responsiva | P2 | A criar |

---

## 4. TESTES DE PERFORMANCE

### Backend (k6/Locust)
```bash
# Instalar k6
docker pull grafana/k6

# Rodar teste de carga
docker run -v $(pwd)/tests/load:/tests grafana/k6 run /tests/load-test.js
```

**Cenários:**
- [ ] 100 usuários concorrentes por 5 minutos
- [ ] Pico de 500 usuários em 30 segundos
- [ ] Teste de endurance (30 minutos)

### Frontend (Lighthouse)
```bash
npm install -D @lighthouse-ci/cli
npx lhci autorun
```

**Métricas Target:**
- LCP (Largest Contentful Paint) < 2.5s
- FID (First Input Delay) < 100ms
- CLS (Cumulative Layout Shift) < 0.1

---

## 5. TESTES DE SEGURANÇA

### SAST (Semgrep)
```bash
# Instalar semgrep
pip install semgrep

# Rodar análise
semgrep --config=auto backend/ frontend/src/
```

### Dependências
```bash
# Backend
pip-audit

# Frontend
npm audit --audit-level=moderate
```

### Secrets Scan
```bash
# Gitleaks (já configurado)
gitleaks detect --source . --verbose
```

---

## 6. TESTES DE ACESSIBILIDADE

```bash
# Axe-core
npm install -D @axe-core/cli
npx axe http://localhost:3000
```

**Critérios WCAG 2.1 AA:**
- [ ] Contraste de cores
- [ ] Navegação por teclado
- [ ] Labels em formulários
- [ ] Alt text em imagens

---

## 7. COMO RODAR TODOS OS TESTES

### Script Completo
```bash
#!/bin/bash
set -e

echo "🧪 Rodando todos os testes..."

# Backend Unit
echo "📦 Backend Unit Tests..."
cd /opt/conecta-pro/backend
python3 -m pytest tests/ -q --tb=short

# Frontend Unit
echo "⚛️ Frontend Unit Tests..."
cd /opt/conecta-pro/frontend
npm test -- --run

# Type Check
echo "🔍 TypeScript Check..."
npm run type-check

# Lint
echo "📏 Lint Check..."
cd /opt/conecta-pro/backend && ruff check . --quiet
cd /opt/conecta-pro/frontend && npm run lint

# Build
echo "🏗️ Build Test..."
npm run build

echo "✅ Todos os testes passaram!"
```

---

## 8. CI/CD PIPELINE RECOMENDADA

```yaml
# .github/workflows/ci.yml
name: CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ --cov=backend

      - name: Frontend Tests
        run: |
          cd frontend
          npm ci
          npm run test:ci
          npm run build

      - name: Security Scan
        run: |
          gitleaks detect --source .
          npm audit --audit-level=moderate

      - name: E2E Tests
        run: |
          npx playwright test
```

---

## 9. CRONOGRAMA DE IMPLEMENTAÇÃO

| Semana | Foco | Entregáveis |
|--------|------|-------------|
| 1 | E2E Auth + Reembolso | 2 fluxos críticos |
| 2 | E2E Operacional + GED | 2 fluxos críticos |
| 3 | Performance + Acessibilidade | Relatórios |
| 4 | Security Hardening | Scan limpo |

---

*Documento em constante atualização*
