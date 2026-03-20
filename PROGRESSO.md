# PROGRESSO — Cleanup & Quality Gate do Conecta PRO

**Data de inicio:** 2026-03-19
**Data de conclusao:** 2026-03-20
**Branch:** `feature/people-management-reorganization`
**Ponto de restauracao:** tag `pre-cleanup-2026-03-19` (commit `4eed46fc`)
**Status:** ✅ TODAS AS FASES CONCLUIDAS (0-4)

---

## FASE 0 — BLINDAGEM (COMPLETA)

**Commits gerados:**
1. `f839d846` — fix: RFC6750 Bearer token + Bartolo module validation + formatting
2. `46570cd3` — fix: resolve 3 critical blockers (esocial_service, alembic chain, log perms)

**Backup:** `backups/postgresql/backup_20260319_211609.sql.gz` (384K, integridade verificada)

### O que foi feito

| Task | Detalhe | Evidencia |
|------|---------|-----------|
| **0.1 Git tag** | `pre-cleanup-2026-03-19` criada em `4eed46fc` | `git tag -l` |
| **0.2 Commit pendentes** | 4 arquivos: auth.py (RFC6750 Bearer, login retorna user object), auth schemas (Bearer default), bartolo_controller (validacao modulo whitelist), operacional/ai/controller (formatting) | commit `f839d846` |
| **0.3 Backup DB** | Script `backup_database.sh` executado, integridade OK, S3 nao configurado | `backup_20260319_211609.sql.gz` |
| **0.4 esocial_service.py** | Arquivo estava 0 bytes. Implementacao real criada: classe `ESocialEventService` com 3 metodos estaticos (`gerar_s2200`, `gerar_s2299`, `validar_xml`). Gera XMLs S-2200 (Admissao) e S-2299 (Desligamento) compativeis com layout eSocial S-1.2 | `backend/modules/people_management/hr/services/esocial_service.py` (127 linhas) |
| **0.5 Alembic chain** | `sprint75_gp_ponto_sst_tables.py` referenciava `down_revision = "sprint74_ged_client_portal_tables"` mas revision real e `sprint74_ged_client_portal` (sem `_tables`). Corrigido. | `backend/alembic/versions/sprint75_gp_ponto_sst_tables.py` linha 13 |
| **0.6 celery-batch** | Container em restart loop por `ModuleNotFoundError: edital_parser_service`. Imagem Docker estava desatualizada — faltavam `edital_parser_service.py` e `erp_integration_service.py`. Copiados via `docker cp` do host. Worker subiu: `batch@326a09b30b03 ready` | `docker logs conecta-pro-celery-batch` |
| **0.7 Frontend healthcheck** | FALSO ALARME. `ports: 3001:3000` = host:container. Healthcheck roda DENTRO do container em `127.0.0.1:3000` — correto. | Nenhuma mudanca necessaria |
| **0.8 Verificacao final** | Encontrado bug adicional: `PermissionError: /app/logs/error.log`. Owner era `root:root` com `rw-r-----`. Corrigido com `chown -R 999:999` + `chmod -R 777` em `/opt/conecta-pro/logs/`. Todos 22/22 containers healthy. | `curl http://localhost:8080/health` → OK |

### Bonus fix durante Fase 0
- **Permissoes de logs:** `/opt/conecta-pro/logs/` — arquivos `error.log`, `app.log`, `backup.log` tinham owner `root:root` com permissao `640`. Container backend roda como user `erp` (UID 999). Corrigido para `999:999` com `777`.

### Estado pos-Fase 0
- 22/22 containers Docker healthy (incluindo celery-batch que estava crashando)
- Backend `/health` retornando `{"status":"healthy","app":"Conecta PRO","version":"2.0.0"}`
- 11/11 modulos backend carregando (incluindo People Management que falhava)
- Alembic migration chain corrigida (sprint74→sprint75 link OK)
- Working tree limpa (`git status` clean)

---

## PRE-MORTEM — RISCOS IDENTIFICADOS (referencia)

### Bloqueadores criticos (RESOLVIDOS na Fase 0)
1. ~~esocial_service.py 0 bytes~~ → RESOLVIDO
2. ~~Alembic chain quebrada~~ → RESOLVIDO
3. ~~celery-batch restart loop~~ → RESOLVIDO
4. ~~4 arquivos nao commitados~~ → RESOLVIDO
5. ~~Frontend healthcheck porta errada~~ → FALSO ALARME

### Riscos de cascata (vigentes para Fases 1-4)
- Remover `ignoreBuildErrors` vai expor erros TS em massa (95% chance)
- Remover Guardian pode quebrar tipos Orval gerados (158 arquivos em `api/campo/generated/`)
- Consolidar reembolso/reimbursement afeta 3 paginas que importam de ambos
- Mudar condominio_id requer criar provider ANTES (350+ arquivos afetados)
- ESLint warn→error: pre-commit tem `--max-warnings 0` — qualquer warning bloqueia commit

---

## PLANO DE EXECUCAO — FASES 1 a 4 (TODAS COMPLETAS)

### Diagrama de dependencias

```
FASE 0 (COMPLETA)
    │
    ├── FASE 1 (paralela: T1 + T2 + T3) ─────────────────────┐
    │   ├── T1: Guardian Removal                               │
    │   ├── T2: Orval Regen + ignoreBuildErrors               │
    │   └── T3: Reembolso Consolidation                       │
    │                                                          │
    ├── FASE 2 (paralela: T4 + T5, APOS Fase 1) ────────────┐│
    │   ├── T4: Contexts (userId + condominio)                ││
    │   └── T5: Backend TODO Audit                            ││
    │                                                          ││
    ├── FASE 3 (sequencial: T6 = QA, APOS Fase 2) ──────────┘│
    │   └── T6: Build + Tests + Validation                     │
    │                                                          │
    └── FASE 4 (opcional: componentes grandes, APOS Fase 3) ──┘
```

### Ordem de execucao dos terminais

```
TEMPO     T1(Guardian)  T2(Types)  T3(Reemb.)  T4(Context)  T5(TODOs)
──────    ───────────   ─────────  ──────────  ───────────  ─────────
0 min     ████████████  █████████  ██████████
          INICIA        INICIA     INICIA
          (paralelo)    (paralelo) (paralelo)

~45 min   DONE          DONE       DONE
                                               ████████████  █████████
                                               INICIA        INICIA
                                               (paralelo)    (paralelo)

~90 min                                        DONE          DONE
          ┌──────────────────────────────────────────────────────────┐
          │ VOLTAR AO TERMINAL PRINCIPAL para Fase 3 (QA)           │
          │ Executar: build, tests, docker restart, commit final    │
          └──────────────────────────────────────────────────────────┘

~110 min  FASE 3 COMPLETA → Fase 4 (opcional, componentes grandes)
```

**IMPORTANTE:** T4 e T5 so devem ser iniciados APOS T1, T2 e T3 terminarem, porque:
- T4 precisa dos tipos Orval limpos (gerados por T2)
- T4 precisa que Guardian esteja removido (T1)
- T5 pode tocar em arquivos que T1-T3 estao editando

---

## TERMINAL 1 — Guardian Removal (Fase 1) ✅ COMPLETO

### Prompt para colar no Claude Code:

```
Voce esta trabalhando no projeto Conecta PRO em /opt/conecta-pro/.
Branch: feature/people-management-reorganization

TAREFA: Remover TODAS as referencias ao modulo Guardian do frontend.
O Guardian foi removido do backend na sessao 19 (commit e2585435) mas restos ficaram no frontend.

ESCOPO:
1. Deletar /opt/conecta-pro/frontend/src/hooks/campo/useGuardian.ts (249 linhas)
2. Deletar /opt/conecta-pro/frontend/src/services/campo/guardianService.ts
3. Editar /opt/conecta-pro/frontend/src/services/campo/index.ts — remover re-exports de Guardian
4. Deletar TODOS os arquivos Guardian* em /opt/conecta-pro/frontend/src/api/campo/generated/models/ (155+ arquivos com "guardian" ou "Guardian" no nome)
5. Editar /opt/conecta-pro/frontend/src/api/campo/generated/campo/campo.ts — remover funcoes/types Guardian
6. Verificar se alguma pagina em /opt/conecta-pro/frontend/src/app/modulos/ importa Guardian (nao deve, mas confirmar)
7. Verificar hooks/index.ts — remover export de useGuardian se existir

RESTRICOES:
- NAO rodar npm run build (Terminal 2 fara isso)
- NAO editar arquivos fora de frontend/src/
- NAO tocar em nenhum arquivo backend
- NAO commitar (commit sera feito no terminal principal)

VALIDACAO: Apos terminar, rodar:
  grep -r "guardian\|Guardian\|useGuardian\|guardianService" /opt/conecta-pro/frontend/src/ --include="*.ts" --include="*.tsx" -l
Deve retornar ZERO resultados (exceto possiveis comentarios em changelogs).

Quando terminar, liste exatamente quantos arquivos foram deletados e editados.
```

---

## TERMINAL 2 — Orval Regen + ignoreBuildErrors (Fase 1) ✅ COMPLETO

### Prompt para colar no Claude Code:

```
Voce esta trabalhando no projeto Conecta PRO em /opt/conecta-pro/.
Branch: feature/people-management-reorganization

TAREFA: Regenerar tipos Orval, remover ignoreBuildErrors, e corrigir erros TypeScript.

ESCOPO (executar nesta ordem):
1. Ler /opt/conecta-pro/frontend/next.config.ts
2. Remover a linha "ignoreBuildErrors: true" do typescript config em next.config.ts
3. Rodar: cd /opt/conecta-pro/frontend && NODE_OPTIONS=--max-old-space-size=8192 npx next build 2>&1 | tee /tmp/build-errors.log
4. Se o build falhar (vai falhar), analisar os erros TypeScript em /tmp/build-errors.log
5. Categorizar os erros por tipo (type mismatch, missing import, unused var, etc.)
6. Corrigir os erros TypeScript — prioridade:
   a. Erros de import (modules removidos, paths errados)
   b. Erros de tipo (type mismatch com API)
   c. Erros de null safety
   d. Se forem MUITOS erros (50+), focar nos criticos e para os demais pode manter ignoreBuildErrors
7. Apos correcoes, rodar build novamente para validar
8. Se build passar, ÓTIMO. Se nao, documentar erros restantes em /tmp/build-remaining-errors.log

NOTA SOBRE TERMINAL 1: O Terminal 1 esta removendo arquivos Guardian em paralelo.
Se encontrar erros relacionados a Guardian, IGNORE-OS (T1 esta cuidando).
Foque em erros NAO relacionados a Guardian.

RESTRICOES:
- NAO tocar em arquivos backend
- NAO commitar
- NAO rodar mais de 1 build simultaneo (consome 8GB RAM)
- Se precisar regenerar Orval: cd /opt/conecta-pro/frontend && npm run api:generate
  (mas so faca isso se os tipos estiverem claramente stale)

Quando terminar, reporte:
- Quantos erros TS existiam
- Quantos foram corrigidos
- Se o build passa ou nao
- Lista de erros restantes (se houver)
```

---

## TERMINAL 3 — Reembolso Consolidation (Fase 1) ✅ COMPLETO

### Prompt para colar no Claude Code:

```
Voce esta trabalhando no projeto Conecta PRO em /opt/conecta-pro/.
Branch: feature/people-management-reorganization

TAREFA: Consolidar servicos duplicados de reembolso no frontend.
Existem DOIS diretorios de servico fazendo a mesma coisa:
- /opt/conecta-pro/frontend/src/services/reembolso/ (LEGADO, 1 arquivo)
- /opt/conecta-pro/frontend/src/services/reimbursement/ (ATUAL, 6 arquivos)

ESCOPO:
1. Ler ambos os diretorios e comparar:
   - frontend/src/services/reembolso/reimbursementService.ts (legado)
   - frontend/src/services/reimbursement/index.ts + submodulos (atual)
2. Mapear TODOS os imports de reembolso/ no codebase:
   grep -r "services/reembolso" frontend/src/ --include="*.ts" --include="*.tsx" -l
3. Mapear TODOS os imports de reimbursement/:
   grep -r "services/reimbursement" frontend/src/ --include="*.ts" --include="*.tsx" -l
4. Para cada arquivo que importa de reembolso/, migrar para importar de reimbursement/
5. Verificar hooks:
   - Se existe hooks/useReimbursement.ts (singular, legado) vs hooks/reimbursement/ (diretorio, atual)
   - Migrar imports legados para hooks/reimbursement/
6. Deletar /opt/conecta-pro/frontend/src/services/reembolso/ (diretorio inteiro)
7. Atualizar frontend/src/services/index.ts se re-exporta algo de reembolso/
8. Verificar se hooks/index.ts precisa de atualizacao

RESTRICOES:
- NAO rodar npm run build (Terminal 2 fara isso)
- NAO tocar em backend
- NAO commitar
- NAO renomear rotas/URLs (as paginas continuam em /modulos/reembolso/ — so os imports mudam)

VALIDACAO:
  grep -r "services/reembolso" frontend/src/ --include="*.ts" --include="*.tsx" -l
Deve retornar ZERO resultados.

Quando terminar, liste arquivos editados e deletados.
```

---

## TERMINAL 4 — Contexts: userId + condominio (Fase 2) ✅ COMPLETO

### Prompt para colar no Claude Code:

```
Voce esta trabalhando no projeto Conecta PRO em /opt/conecta-pro/.
Branch: feature/people-management-reorganization

TAREFA: Corrigir userId hardcoded e criar infraestrutura de condominio context.

IMPORTANTE: So inicie esta tarefa APOS os Terminais 1, 2 e 3 terem finalizado.

PARTE A — userId hardcoded (2 arquivos):
1. Ler /opt/conecta-pro/frontend/src/hooks/useAuth.ts — entender como userId e obtido
2. Ler /opt/conecta-pro/frontend/src/components/ai/BartoloChat.tsx
3. Ler /opt/conecta-pro/frontend/src/components/ai/BartoloChatWidget.tsx
4. Em ambos os componentes, substituir userId hardcoded (= 1 ou similar) por:
   - Importar useAuth
   - const { user } = useAuth()
   - Usar user?.id (com fallback seguro se user for null durante loading)
5. Verificar se ha outros arquivos com userId hardcoded:
   grep -rn "userId.*=.*1\b\|userId.*:.*1\b\|user_id.*=.*1\b" frontend/src/ --include="*.ts" --include="*.tsx"

PARTE B — Condominio Context (novo):
1. Verificar se ja existe algum context de condominio:
   grep -r "CondominioContext\|useCondominio\|CondomínioProvider" frontend/src/
2. Se NAO existir, criar:
   - frontend/src/contexts/CondominioContext.tsx
   - Hook useCondominio() que retorna { condominioId, setCondominioId, condominios }
   - Pegar condominios da API (GET /api/v1/empresas ou similar)
   - Persistir selecao em localStorage
3. Integrar o provider em frontend/src/contexts/providers.tsx (ou app/layout.tsx)
4. Substituir os TOP 10 hardcoded condominio_id mais criticos:
   grep -rn "condominio_id.*=.*[\"'].*[\"']\|condominioId.*=.*[\"']" frontend/src/app/ --include="*.tsx" | head -20
5. NAO precisa trocar TODOS os 350 arquivos — foque nos 10-20 mais criticos
   (paginas financeiro, DP, GED, operacional)

RESTRICOES:
- NAO tocar em backend
- NAO commitar
- NAO rodar build (sera feito na Fase 3)
- Manter compatibilidade — se user ou condominio for null, usar fallback gracioso

Quando terminar, reporte:
- Quantos userId hardcoded corrigidos
- Se CondominioContext foi criado
- Quantos condominio_id hardcoded substituidos (de ~350 total)
```

---

## TERMINAL 5 — Backend TODO Audit (Fase 2) ✅ COMPLETO

### Prompt para colar no Claude Code:

```
Voce esta trabalhando no projeto Conecta PRO em /opt/conecta-pro/.
Branch: feature/people-management-reorganization

TAREFA: Auditar e limpar TODOs do backend (240 no modules/).

IMPORTANTE: So inicie esta tarefa APOS os Terminais 1, 2 e 3 terem finalizado.

ESCOPO:
1. Listar todos os TODOs:
   grep -rn "TODO\|FIXME\|HACK\|XXX" backend/modules/ --include="*.py" | head -300
2. Categorizar em:
   a. OBSOLETOS (refs a Guardian, search, modulos removidos) → DELETAR
   b. STUBS que nunca serao implementados ("TODO: integrar com X" onde X nao existe) → DELETAR
   c. VALIDOS mas vagos ("TODO: implementar") → Reescrever com contexto ou DELETAR
   d. VALIDOS e importantes ("TODO: migrar para Prometheus") → MANTER
3. Para cada TODO obsoleto/stub, REMOVER a linha inteira ou o bloco de comentario
4. NAO alterar logica de codigo — apenas remover/editar comentarios TODO
5. Gerar relatorio final em /tmp/todo-audit-report.txt com:
   - Total encontrados
   - Total removidos (por categoria)
   - Total mantidos (com justificativa)
   - Lista dos mantidos com arquivo:linha

ZONAS PROIBIDAS (NAO editar):
- backend/modules/financial/* (compliance fiscal)
- backend/modules/government_integrations/* (regulatorio)
- backend/modules/ai/bartolo/services/data_connector.py (core AI, 2930 linhas)
- backend/alembic/* (migrations)
- backend/main_production.py
- backend/api/v1/__init__.py

RESTRICOES:
- NAO alterar logica de codigo, apenas comentarios
- NAO commitar
- NAO reiniciar containers
- Se um TODO esta dentro de uma funcao real que funciona, so remova o comentario, nao a funcao

Quando terminar, reporte totais por categoria.
```

---

## FASE 3 — QA (COMPLETA)

**Data:** 2026-03-20
**Build:** 0 erros, 211 paginas, compilado em 31s
**Health:** backend healthy (v2.0.0)
**Commits:** `4d793684` (cleanup principal) + `727f74bb` (fix type error)
**Tag:** `post-cleanup-2026-03-19`

Comandos executados:

```bash
# 1. Verificar estado git
cd /opt/conecta-pro && git status

# 2. Build frontend (teste definitivo)
cd /opt/conecta-pro/frontend && NODE_OPTIONS=--max-old-space-size=8192 npx next build

# 3. Testes backend
cd /opt/conecta-pro/backend && python -m pytest tests/ -x --timeout=60 -q 2>&1 | tail -20

# 4. Sync para containers + restart
docker cp /opt/conecta-pro/backend/modules conecta-pro-backend:/app/modules
docker restart conecta-pro-backend
sleep 120 && curl -sf http://localhost:8080/health

# 5. ESLint — promover 5 regras criticas de warn → error
# (avaliar apos build, pode ser adiado)

# 6. Commit final
git add -A
git commit -m "refactor: cleanup phase 1+2 — Guardian removal, type fixes, reembolso consolidation, contexts, TODO audit"

# 7. Tag
git tag post-cleanup-2026-03-19
```

---

## FASE 4 — Componentes Grandes (COMPLETA)

**Data:** 2026-03-20
**Build:** passa limpo (0 erros TS, 211 paginas)

3 componentes decompostos:

| Componente | Antes | Depois | Arquivos criados |
|------------|-------|--------|------------------|
| `post-form-modal.tsx` | 872 | 340 | `post-form-steps.tsx` (477), `post-form-types.ts` (46) |
| `diarist-form-modal.tsx` | 770 | 297 | `diarist-dados-pessoais-tab.tsx` (185), `diarist-servicos-tab.tsx` (124), `diarist-pagamento-tab.tsx` (118), `diarist-form-types.ts` (105) |
| `BartoloChat.tsx` | 653 | 452 | `bartolo-chat/ChatHeader.tsx` (62), `bartolo-chat/ChatMessages.tsx` (155), `bartolo-chat/ChatInput.tsx` (62), `bartolo-chat/ChatSuggestions.tsx` (28), `bartolo-chat/DachshundIcon.tsx` (99), `bartolo-chat/types.ts` (35), `bartolo-chat/index.ts` (6) |

Nao decompostos (manter como esta):
- `reimbursement-form-modal.tsx` (546) — complexidade nao justifica
- `BartoloChatWidget.tsx` (506) — componente independente do BartoloChat

---

## ZONAS PROIBIDAS — NAO EDITAR

| Arquivo/Diretorio | Motivo |
|-------------------|--------|
| `backend/modules/financial/*` | 9,969 linhas, compliance fiscal, sem testes suficientes |
| `backend/modules/government_integrations/*` | SEFAZ/eSocial, regulatorio |
| `backend/modules/ai/bartolo/services/data_connector.py` | 2,930 linhas, core AI |
| `backend/alembic/versions/*` | Migration chain recem-corrigida |
| `backend/main_production.py` | Module loader, silent failures |
| `backend/api/v1/__init__.py` | Fallback de imports |
| `docker-compose*.yml` | Infraestrutura de producao |
| `.env*` | Segredos |
| `backend/core/` | Autenticacao, DB, config — base do sistema |

---

## COMO RESTAURAR SE ALGO DER ERRADO

```bash
# Voltar ao estado pre-cleanup
cd /opt/conecta-pro
git checkout pre-cleanup-2026-03-19
git checkout -b recovery-branch

# Restaurar banco
gunzip -k backups/postgresql/backup_20260319_211609.sql.gz
docker exec -i conecta-pro-postgres psql -U postgres -d conecta_pro < backups/postgresql/backup_20260319_211609.sql

# Restart containers
docker restart conecta-pro-backend conecta-pro-frontend
```

---

## NOTAS TECNICAS

- Backend code baked no Docker: mudancas requerem `docker cp` + `docker restart`
- Build frontend: `NODE_OPTIONS=--max-old-space-size=8192 npx next build` (8GB heap)
- Deploy frontend: `cp -r .next/static .next/standalone/.next/ && pm2 restart` OU Docker rebuild
- Auth: `admin@conectapro.com.br` / `admin123` (rate limit: 5/min, localhost:8080, form-urlencoded)
- Pre-commit: ruff + bandit + gitleaks + detect-secrets (auto-fix pode alterar staged files)
- Container user: `erp` (UID 999) — logs e uploads precisam ter permissao para esse user
