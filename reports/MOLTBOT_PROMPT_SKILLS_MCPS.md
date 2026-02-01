# Prompt Avançado para Moltbot - Conecta PRO
## Skills, MCPs e Plano de Qualidade

> **Gerado em:** 01/02/2026
> **Projeto:** Conecta PRO - ERP de Gestão para Segurança Patrimonial
> **Stack:** FastAPI 0.115.6 + Next.js 16.1.3 + PostgreSQL 16 + Redis 7

---

## Diagnóstico Atual do Projeto

| Métrica | Valor | Status |
|---------|-------|--------|
| Arquivos de módulos backend | 1.710 | - |
| Arquivos de teste backend | 193 | Cobertura ~11% |
| Arquivos de teste frontend | **0** | CRÍTICO |
| CI/CD (GitHub Actions) | Existe (lint + test) | Parcial |
| Linting backend (black, isort, pylint, mypy) | Instalado | OK |
| Linting frontend (ESLint) | Apenas eslint-config-next | INSUFICIENTE |
| Jest/Vitest frontend | **Não instalado** | CRÍTICO |
| Husky/pre-commit hooks | **Não configurado** | FALTANTE |
| Prettier frontend | **Não instalado** | FALTANTE |
| Locust (testes de carga) | **Não instalado** | FALTANTE |
| Bandit (security scan) | **Não instalado** | FALTANTE |
| SonarQube | **Não configurado** | FALTANTE |
| Swagger/OpenAPI docs | Funcional via FastAPI | OK |
| Prometheus + Grafana | Configurado | OK |

---

## 1. MCPs (Model Context Protocols) - Detalhamento Técnico

### MCP 1: Testes Automatizados

#### 1.1 Backend (Python/FastAPI)

**Estado atual:** 193 testes para 1.710 arquivos de módulo (~11% de cobertura)

**Ferramentas necessárias:**
```
pytest==8.3.4          ✅ Já instalado
pytest-cov==6.0.0      ✅ Já instalado
pytest-asyncio==0.25.0 ✅ Já instalado
pytest-mock>=3.14.0    ❌ INSTALAR
pytest-timeout>=2.3.1  ❌ INSTALAR
pytest-xdist>=3.5.0    ❌ INSTALAR (paralelização)
locust>=2.29.0         ❌ INSTALAR (testes de carga)
factory-boy>=3.3.1     ❌ INSTALAR (factories de teste)
faker>=30.0.0          ❌ INSTALAR (dados fake)
httpx>=0.27.0          ❌ VERIFICAR (AsyncClient para testes)
```

**Ações concretas:**

1. **Fixtures centralizadas** - Criar `conftest.py` global com:
   ```python
   # /opt/conecta-pro/backend/tests/conftest.py
   # - Mock do banco de dados (SQLAlchemy in-memory ou TestContainers)
   # - Mock do Redis
   # - Fixture de usuário autenticado (JWT válido)
   # - Fixture de condomínio/empresa de teste
   # - AsyncClient configurado para todos os endpoints
   ```

2. **Módulos prioritários para testes** (por criticidade):
   - `modules/financial/` - Cálculos financeiros, NF-e, boletos
   - `modules/operacional/` - Escalas, postos, rondas, diaristas
   - `modules/government_integrations/` - eSocial, SEFAZ, FGTS Digital
   - `modules/hr/` - Folha de pagamento, admissão, rescisão
   - `modules/clients/` - Cadastro de clientes/condomínios
   - `modules/ai/bartolo/` - Assistente IA
   - `core/auth/` - Autenticação JWT
   - `core/security/` - Funções de segurança

3. **Testes de carga com Locust:**
   ```python
   # /opt/conecta-pro/backend/tests/load/locustfile.py
   # Endpoints críticos para teste de carga:
   # - POST /api/v1/auth/login (autenticação)
   # - GET /api/v1/operacional/escalas (listagem de escalas)
   # - GET /api/v1/financial/dashboard (dashboard financeiro)
   # - POST /api/v1/government/esocial/submit (envio eSocial)
   # - GET /api/v1/clients (listagem de clientes)
   ```

4. **Meta de cobertura por sprint:**
   - Sprint 1: 40% (módulos core + auth)
   - Sprint 2: 60% (financial + operacional)
   - Sprint 3: 80% (government + hr)
   - Sprint 4: 95% (todos os módulos restantes)

#### 1.2 Frontend (Next.js/React/TypeScript)

**Estado atual:** ZERO testes. Nenhum framework de teste instalado.

**Ferramentas a instalar:**
```bash
# Testing framework
npm install -D vitest @vitejs/plugin-react jsdom
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @vitest/coverage-v8
npm install -D msw  # Mock Service Worker para mock de API

# E2E
npm install -D playwright @playwright/test
npx playwright install
```

**Configuração Vitest:**
```typescript
// /opt/conecta-pro/frontend/vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: ['node_modules/', 'src/api/generated/'],
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
});
```

**Ações concretas:**

1. **Setup inicial do Vitest + Testing Library**
2. **Mock Service Worker (MSW)** para interceptar chamadas API Orval
3. **Componentes prioritários para teste:**
   - `src/components/layout/` - Layout principal, sidebar, header
   - `src/components/forms/` - Formulários de cadastro
   - `src/components/operacional/` - Módulo operacional
   - `src/features/` - Lógica de features com Zustand
   - `src/hooks/` - Custom hooks
   - `src/app/login/` - Fluxo de autenticação
   - `src/app/dashboard/` - Dashboard principal
4. **Playwright E2E** para fluxos críticos:
   - Login → Dashboard → Módulo Operacional
   - Cadastro de cliente/condomínio
   - Geração de escala
   - Emissão de NF-e

**Meta de cobertura frontend:**
   - Sprint 1: 30% (setup + componentes base + hooks)
   - Sprint 2: 50% (features + forms)
   - Sprint 3: 70% (páginas + E2E básico)
   - Sprint 4: 90%+ (cobertura completa)

---

### MCP 2: Linting e Qualidade de Código

#### 2.1 Backend (Python)

**Estado atual:** black, isort, pylint, mypy instalados

**Complementos a instalar:**
```
ruff>=0.8.0            ❌ INSTALAR (substitui flake8, mais rápido)
bandit>=1.8.0          ❌ INSTALAR (security linting)
safety>=3.2.0          ❌ INSTALAR (vulnerabilidades em deps)
pre-commit>=4.0.0      ❌ INSTALAR (hooks de pre-commit)
```

**Configuração pre-commit (.pre-commit-config.yaml):**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.0
    hooks:
      - id: bandit
        args: ["-r", ".", "-ll"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
      - id: detect-private-key
```

#### 2.2 Frontend (TypeScript/React)

**Estado atual:** Apenas eslint + eslint-config-next. Zero @ts-ignore auditados.

**Ferramentas a instalar:**
```bash
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install -D eslint-plugin-react-hooks eslint-plugin-jsx-a11y
npm install -D eslint-plugin-import eslint-plugin-unused-imports
npm install -D husky lint-staged
```

**Configuração Husky + lint-staged:**
```bash
npx husky init
# .husky/pre-commit:
npx lint-staged
```

```json
// package.json - lint-staged
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,css}": ["prettier --write"]
  }
}
```

**Ações concretas:**
1. Auditar e eliminar todos os `@ts-ignore` e `@ts-expect-error`
2. Configurar `tsconfig.json` com `strict: true`
3. Habilitar regras de acessibilidade (`jsx-a11y`)
4. Zero warnings de lint como meta

---

### MCP 3: Integração Contínua (CI/CD)

**Estado atual:** CI pipeline existe (`.github/workflows/ci.yml`) com lint + test básico

**Pipeline aprimorado proposto:**

```yaml
# .github/workflows/ci.yml - Pipeline Completo
name: CI/CD Pipeline Conecta PRO

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── ETAPA 1: Análise Estática ───
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff mypy bandit
      - run: ruff check backend/
      - run: mypy backend/ --ignore-missing-imports
      - run: bandit -r backend/ -ll -q

  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run type-check

  # ─── ETAPA 2: Testes ───
  test-backend:
    needs: lint-backend
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: conecta_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r backend/requirements.txt
      - run: |
          cd backend
          pytest --cov=. --cov-report=xml --cov-fail-under=80
      - uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml

  test-frontend:
    needs: lint-frontend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd frontend && npm ci
      - run: cd frontend && npx vitest run --coverage
      - uses: codecov/codecov-action@v4

  # ─── ETAPA 3: Security Scan ───
  security:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install safety bandit
      - run: safety check -r backend/requirements.txt
      - run: bandit -r backend/ -f json -o bandit-report.json -ll
      - run: cd frontend && npm audit --audit-level=high
      - uses: zaproxy/action-baseline@v0.12.0
        with:
          target: 'https://staging.erp.conectamais.pro'

  # ─── ETAPA 4: Deploy Staging ───
  deploy-staging:
    needs: security
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploy to staging..."

  # ─── ETAPA 5: Deploy Production ───
  deploy-production:
    needs: security
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploy to production..."
```

---

## 2. Skills para Integrar - Detalhamento Técnico

### Skill 1: Cobertura Avançada de Testes

**Aplicação:** Backend + Frontend
**Ferramentas:**
- `pytest-cov` (já instalado) + `coverage.py` para relatórios
- `@vitest/coverage-v8` para frontend
- **Codecov** para histórico e badges

**Configuração coverage.py:**
```ini
# /opt/conecta-pro/backend/.coveragerc
[run]
source = modules, core, api
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */alembic/*

[report]
fail_under = 80
show_missing = true
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.
    raise NotImplementedError
    pass

[html]
directory = reports/coverage_html
```

**Automação:**
```bash
# Script diário de cobertura
# /opt/conecta-pro/scripts/coverage_report.sh
#!/bin/bash
cd /opt/conecta-pro/backend
pytest --cov=modules --cov=core --cov-report=html:../reports/coverage_html \
       --cov-report=json:../reports/coverage.json \
       --cov-report=term-missing 2>&1 | tee ../reports/coverage_$(date +%Y%m%d).log

# Verificar threshold
python3 -c "
import json
data = json.load(open('../reports/coverage.json'))
total = data['totals']['percent_covered']
print(f'Cobertura total: {total:.1f}%')
if total < 80:
    print('⚠ ALERTA: Cobertura abaixo de 80%!')
    exit(1)
"
```

---

### Skill 2: Auditoria de Qualidade (SonarQube)

**Aplicação:** Backend + Frontend

**Setup Docker SonarQube:**
```yaml
# Adicionar ao docker-compose.yml
sonarqube:
  image: sonarqube:community
  container_name: conecta-pro-sonar
  ports:
    - "9000:9000"
  environment:
    - SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
  volumes:
    - sonar_data:/opt/sonarqube/data
    - sonar_logs:/opt/sonarqube/logs
    - sonar_extensions:/opt/sonarqube/extensions
```

**Configuração projeto:**
```properties
# /opt/conecta-pro/sonar-project.properties
sonar.projectKey=conecta-pro
sonar.projectName=Conecta PRO
sonar.sources=backend/modules,backend/core,frontend/src
sonar.tests=backend/tests,frontend/src
sonar.test.inclusions=**/*.test.ts,**/*.test.tsx,**/test_*.py
sonar.python.coverage.reportPaths=backend/reports/coverage.xml
sonar.typescript.lcov.reportPaths=frontend/coverage/lcov.info
sonar.exclusions=**/node_modules/**,**/__pycache__/**,**/migrations/**,**/generated/**
sonar.qualitygate.wait=true
```

**Métricas SonarQube a monitorar:**
- Code Smells: meta zero em código novo
- Bugs: meta zero
- Vulnerabilities: meta zero
- Duplications: < 3%
- Coverage: > 80%
- Maintainability Rating: A

---

### Skill 3: Análise de Desempenho

**Aplicação:** Backend + Frontend

#### Backend - Prometheus + Grafana (já configurado)

**Complementos:**
```python
# /opt/conecta-pro/backend/core/monitoring/middleware.py
# Métricas adicionais a implementar:
# - Latência por endpoint (histogram)
# - Taxa de erros por módulo (counter)
# - Queries SQL lentas > 100ms (histogram)
# - Uso de memória por worker (gauge)
# - Filas Celery pendentes (gauge)
```

**Alertas Prometheus propostos:**
```yaml
# /opt/conecta-pro/monitoring/alerts.yml
groups:
  - name: conecta-pro-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels: { severity: critical }
        annotations:
          summary: "Taxa de erro > 5% nos últimos 5 minutos"

      - alert: SlowEndpoint
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 10m
        labels: { severity: warning }
        annotations:
          summary: "P95 de latência > 2s"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 1073741824
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "Backend usando > 1GB de RAM"

      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 100
        for: 15m
        labels: { severity: warning }
        annotations:
          summary: "Fila Celery com > 100 tasks pendentes"
```

#### Frontend - Lighthouse CI + Web Vitals

```bash
# Instalar
npm install -D @lhci/cli
```

```javascript
// /opt/conecta-pro/frontend/lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/login', 'http://localhost:3000/dashboard'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['warn', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['warn', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['warn', { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: 'filesystem',
      outputDir: '../reports/lighthouse',
    },
  },
};
```

---

### Skill 4: Documentação Automatizada

**Backend - Swagger/OpenAPI (já funcional via FastAPI)**

Complementos:
```python
# Melhorias no OpenAPI existente:
# 1. Adicionar exemplos em todos os schemas Pydantic
# 2. Documentar códigos de erro por endpoint
# 3. Agrupar endpoints por módulo de negócio
# 4. Gerar changelog de API automaticamente

# Ferramenta adicional:
# mkdocs-material para documentação técnica
# pip install mkdocs-material mkdocstrings[python]
```

**Frontend - Storybook para componentes UI:**
```bash
npx storybook@latest init
# Documentar componentes visuais interativamente
```

---

### Skill 5: Segurança Avançada

**Ferramentas:**
```
bandit>=1.8.0          # Security linting Python
safety>=3.2.0          # Vulnerabilidades em dependências
pip-audit>=2.7.0       # Audit de pacotes pip
trivy                  # Scan de containers Docker
gitleaks               # Prevenção de leak de secrets
```

**GitGuardian / Gitleaks:**
```yaml
# .pre-commit-config.yaml - adicionar
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.0
    hooks:
      - id: gitleaks
```

**OWASP ZAP scan automatizado:**
```bash
# /opt/conecta-pro/scripts/security_scan.sh
#!/bin/bash
docker run --rm -t zaproxy/zap-stable zap-baseline.py \
  -t https://erp.conectamais.pro \
  -r /opt/conecta-pro/reports/zap_report.html \
  -l WARN
```

---

## 3. Skill de Monitoramento de Produção

**Stack:** Prometheus + Grafana (já configurado) + complementos

**Complementos propostos:**

1. **Sentry** para error tracking em tempo real:
   ```python
   # Backend
   pip install sentry-sdk[fastapi]
   sentry_sdk.init(dsn="...", traces_sample_rate=0.2)
   ```
   ```bash
   # Frontend
   npm install @sentry/nextjs
   ```

2. **Uptime monitoring:**
   ```yaml
   # /opt/conecta-pro/monitoring/blackbox.yml
   # Blackbox Exporter para health checks externos
   modules:
     http_2xx:
       prober: http
       timeout: 5s
       http:
         valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
         valid_status_codes: [200]
         fail_if_body_not_matches_regexp: ["healthy"]
   ```

3. **Dashboards Grafana propostos:**
   - Overview: requests/s, latência P50/P95/P99, error rate
   - Por módulo: financial, operacional, government
   - Infrastructure: CPU, RAM, disk, network
   - Celery: tasks/s, queue length, failures
   - PostgreSQL: connections, slow queries, lock waits
   - Redis: memory, hit rate, evictions

---

## 4. Plano de Implementação por Prioridade

### Prioridade CRÍTICA (Implementar Primeiro)

| # | Ação | Impacto |
|---|------|---------|
| 1 | Instalar Vitest + Testing Library no frontend | Sem testes = risco máximo |
| 2 | Configurar Husky + pre-commit hooks | Prevenir código ruim no repo |
| 3 | Instalar pytest-mock + factory-boy no backend | Acelerar criação de testes |
| 4 | Auditar e eliminar @ts-ignore no frontend | Bugs silenciosos em produção |
| 5 | Configurar strict mode no tsconfig.json | Type safety completa |

### Prioridade ALTA

| # | Ação | Impacto |
|---|------|---------|
| 6 | Testes para módulos financial + operacional | Core business protegido |
| 7 | Testes para government_integrations | Compliance fiscal |
| 8 | Pipeline CI completo (lint → test → security → deploy) | Automação total |
| 9 | Instalar Bandit + Safety para security scan | Vulnerabilidades detectadas cedo |
| 10 | Configurar Codecov com badges | Visibilidade da cobertura |

### Prioridade MÉDIA

| # | Ação | Impacto |
|---|------|---------|
| 11 | Setup SonarQube | Code smells e duplicações |
| 12 | Lighthouse CI no pipeline | Performance frontend monitorada |
| 13 | Testes E2E com Playwright | Fluxos críticos validados |
| 14 | Locust para testes de carga | Capacidade do sistema conhecida |
| 15 | Storybook para componentes UI | Documentação visual |

### Prioridade BAIXA (Refinamento)

| # | Ação | Impacto |
|---|------|---------|
| 16 | Sentry para error tracking | Erros em produção rastreados |
| 17 | Alertas Prometheus avançados | Proatividade operacional |
| 18 | GitGuardian/Gitleaks | Prevenção de leak de secrets |
| 19 | mkdocs para documentação técnica | Onboarding da equipe |
| 20 | Dashboards Grafana por módulo | Observabilidade granular |

---

## 5. Comandos de Instalação Consolidados

### Backend
```bash
cd /opt/conecta-pro/backend

# Testes
pip install pytest-mock pytest-timeout pytest-xdist factory-boy faker httpx

# Qualidade
pip install ruff bandit safety pip-audit pre-commit

# Testes de carga
pip install locust

# Documentação
pip install mkdocs-material mkdocstrings[python]

# Inicializar pre-commit
pre-commit install
```

### Frontend
```bash
cd /opt/conecta-pro/frontend

# Testes unitários
npm install -D vitest @vitejs/plugin-react jsdom @vitest/coverage-v8
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D msw

# E2E
npm install -D playwright @playwright/test
npx playwright install

# Linting + Formatação
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install -D eslint-plugin-react-hooks eslint-plugin-jsx-a11y
npm install -D eslint-plugin-import eslint-plugin-unused-imports

# Pre-commit hooks
npm install -D husky lint-staged
npx husky init

# Performance
npm install -D @lhci/cli

# Storybook
npx storybook@latest init

# Monitoring
npm install @sentry/nextjs
```

### Scripts package.json a adicionar:
```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write 'src/**/*.{ts,tsx,json,css}'",
    "lighthouse": "lhci autorun",
    "storybook": "storybook dev -p 6006",
    "prepare": "husky"
  }
}
```

---

## 6. Métricas de Sucesso

| Métrica | Atual | Meta Sprint 1 | Meta Sprint 2 | Meta Final |
|---------|-------|---------------|---------------|------------|
| Cobertura Backend | ~11% | 40% | 60% | 95% |
| Cobertura Frontend | 0% | 30% | 50% | 90% |
| @ts-ignore no código | Não auditado | 50% removidos | 90% removidos | 0 |
| Warnings ESLint | Não auditado | -50% | -90% | 0 |
| Lighthouse Performance | Não medido | > 70 | > 80 | > 90 |
| Lighthouse Accessibility | Não medido | > 80 | > 90 | > 95 |
| Security Vulnerabilities | Não escaneado | Críticas: 0 | High: 0 | Medium: 0 |
| Code Smells (SonarQube) | N/A | Baseline | -50% | Rating A |
| P95 Latência API | Não medido | < 3s | < 2s | < 1s |
| Pipeline CI | Parcial | Lint+Test | +Security | Completo |

---

## 7. Ciclo de Feedback e Melhoria Contínua

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE QUALIDADE                        │
│                                                             │
│  Developer → Pre-commit hooks → CI Pipeline → Deploy        │
│      ↑                                           │          │
│      │         ┌──────────────────┐              │          │
│      │         │ SonarQube Report │              ↓          │
│      │         │ Coverage Report  │        Monitoring        │
│      │         │ Security Scan    │     (Prometheus/Sentry)  │
│      │         └──────┬───────────┘              │          │
│      │                │                          │          │
│      └────── Backlog Técnico ◄───── Alertas ◄────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

1. **Pré-commit:** Ruff + Bandit + ESLint + Prettier (local)
2. **CI:** Testes + Coverage + Security (automático)
3. **Semanal:** Relatório SonarQube + Backlog de débito técnico
4. **Produção:** Prometheus alertas → Sentry errors → Ação imediata
5. **Mensal:** Review de métricas + ajuste de metas

---

*Relatório gerado automaticamente em 01/02/2026*
*Baseado em análise real do repositório /opt/conecta-pro/*
*193 arquivos de teste | 1.710 arquivos de módulo | 32 módulos de negócio*
