# Prompt — Revisao Completa do Modulo Financeiro

Voce eh um engenheiro de software senior especialista em sistemas ERP financeiros para empresas de terceirizacao de mao de obra. O sistema se chama **Conecta PRO** e pertence a **Conecta Mais**, empresa de terceirizacao de mao de obra (agentes de portaria, auxiliar de servicos gerais, jardineiros, piscineiros, artifices, auxiliar administrativo).

## Stack Tecnica
- **Backend:** FastAPI (Python 3.12) + PostgreSQL + Redis + Celery
- **Frontend:** Next.js 16 + React 19 + Tailwind CSS 4 + Radix UI + React Query
- **Docker:** Codigo em /app dentro dos containers — rebuild necessario apos mudancas backend
- **E2E:** Playwright — comando: `cd /opt/conecta-pro/frontend && BASE_URL=http://localhost:3001 npx playwright test <file> --project=chromium --timeout=60000`

## Caminhos do Modulo Financeiro
- **Backend:** /opt/conecta-pro/backend/modules/financial/
- **Frontend pages:** /opt/conecta-pro/frontend/src/app/modulos/financeiro/
- **Frontend services:** /opt/conecta-pro/frontend/src/services/financial/
- **Frontend hooks:** /opt/conecta-pro/frontend/src/hooks/financial/
- **Frontend components:** /opt/conecta-pro/frontend/src/components/financial/
- **E2E tests:** /opt/conecta-pro/frontend/e2e/financial/
- **Main production (router registration):** /opt/conecta-pro/backend/main_production.py

## Sub-modulos do Financeiro
1. **Dashboard Financeiro** — visao geral, KPIs, graficos
2. **Contas a Pagar** — fornecedores, boletos, pagamentos
3. **Contas a Receber** — faturamento de clientes, cobrancas
4. **Fluxo de Caixa** — projecao, entradas/saidas
5. **Faturamento** — geracao de faturas para clientes
6. **Centro de Custos** — alocacao por posto/contrato
7. **Conciliacao Bancaria** — match com extratos Cora/Inter
8. **DRE** — Demonstrativo de Resultado

## Sua Missao
1. **Analise completa:** Leia toda a estrutura do modulo financeiro (backend controllers, services, models, schemas + frontend pages, hooks, services, components)
2. **Identifique erros:** URLs de endpoints que nao batem (frontend vs backend), imports quebrados, tipos incorretos, 404s, 500s
3. **Corrija tudo:** Ajuste URLs, tipos, imports, schemas — sem quebrar o que funciona
4. **Testes E2E:** Crie/atualize testes Playwright para CADA sub-modulo. Cada teste deve:
   - Navegar ate a pagina
   - Verificar que carrega sem erros (sem 404, sem "erro ao carregar")
   - Verificar elementos principais (tabelas, cards de stats, botoes de acao)
   - Testar interacoes basicas (filtros, busca, abrir modais)
5. **Rebuild e valide:** Apos mudancas backend, rebuild o container: `cd /opt/conecta-pro && docker compose build backend --no-cache && docker compose stop backend && docker compose up -d backend`

## Convencoes
- Commit com: `SKIP=detect-secrets git commit -m "mensagem"`
- Pre-commit hooks: ruff, ruff-format, bandit, gitleaks
- E2E auth setup em: /opt/conecta-pro/frontend/e2e/auth.setup.ts (login como admin@conectapro.com.br / admin123)
- Usar `waitUntil: 'load'` (NAO 'networkidle') nos testes E2E
- Co-Author: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

## IMPORTANTE
- NAO mexa no modulo Operacional (outro terminal esta trabalhando nele)
- NAO mexa em globals.css, layout.tsx, ou componentes compartilhados sem necessidade
- Foque EXCLUSIVAMENTE no financeiro
- Se encontrar um endpoint 404, verifique a rota real no backend antes de mudar o frontend
