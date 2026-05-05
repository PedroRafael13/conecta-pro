# T1 PERMISSOES CPRO12 — Controle de Acesso por Módulo
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** BACKEND + DATA (core/permissions.py + financeiro/__init__.py + users.permissions)

---

## RESULTADO — SUCESSO

> Sistema de controle de acesso por módulo implementado e validado em produção.
> INV-4 enforced no backend: financeiro = APENAS Jordan.
> Convites Chatwoot reenviados para Ramon e Ruan.

---

## Arquivos modificados/criados

| Arquivo | Tipo | Ação |
|---------|------|------|
| `backend/core/permissions.py` | NOVO | Dependency factory `requer_modulo()` |
| `backend/modules/financeiro/__init__.py` | MODIFICADO | Injeção de deps em todas as rotas financeiras |
| `CONTRACTS_GEDEON.md` §97 | DOCS | Documentação da arquitetura de permissões |
| `users.permissions` (banco) | DATA | Permissions setadas para 6 usuários |

---

## Matriz de Permissões Implementada

| Usuário | Email | Permissões no banco |
|---------|-------|---------------------|
| Jordan Jesus | jjesus@conectamais.pro | {all} — CEO, wildcard (INV-3) |
| Pyetra Jesus | pjesus@conectamais.pro | {module:fiscal, module:dp, module:operacional, module:crm, module:ged} |
| Eliziel Gonzaga | egonzaga@conectamais.pro | {module:dp, module:operacional, module:ged} |
| Orlailson Paiva | opaiva@conectamais.pro | {module:dp, module:operacional, module:ged} |
| Ramon Araujo | romondossantosaraujo16@gmail.com | {module:dp, module:operacional, module:crm, module:ged, module:dev} |
| Pedro Neves | pedrorafaeldsn12@gmail.com | {module:dp, module:operacional, module:crm, module:ged, module:dev} |
| Ruan Souza | ruansouza538@gmail.com | {module:operacional, module:ged} |

---

## Testes de Validação (INV-3 e INV-4)

| Teste | Esperado | Resultado |
|-------|----------|-----------|
| Jordan → GET /api/v1/financial/payables | HTTP 200 | ✅ HTTP 200 |
| Ruan → GET /api/v1/financial/payables | HTTP 403 | ✅ HTTP 403 `Acesso negado ao módulo 'financeiro'` |
| Pyetra → GET /api/v1/financial/payables | HTTP 403 | ✅ HTTP 403 `Acesso negado ao módulo 'financeiro'` |
| Pyetra → GET /api/v1/financial/fiscal/stats | HTTP 2xx (fiscal permitido) | ✅ HTTP 422 (permissão passou, faltou parâmetro) |

---

## Convites Chatwoot reenviados (STEP 8)

| Email | Status |
|-------|--------|
| romondossantosaraujo16@gmail.com (Ramon) | ✅ `send_confirmation_instructions` enqueued via Sidekiq |
| ruansouza538@gmail.com (Ruan) | ✅ `send_confirmation_instructions` enqueued via Sidekiq |

---

## Nota Técnica: FastAPI 0.115.6 Limitation

**Problema descoberto:** `APIRouter.include_router()` NÃO propaga `router.dependencies` de sub-routers.
**Causa:** FastAPI cria novas `APIRoute` com `dependencies=list(route.dependencies or [])` na hora do `include_router`.
**Solução:** Modificar `route.dependencies` de cada rota ANTES do `include_router` ser chamado em `main_production.py`.
**Onde:** `modules/financeiro/__init__.py` (importado por `main_production.py` antes do `include_router`).
**Root cause da falha anterior:** Hot-copy copiou o arquivo DEPOIS do container iniciar → uvicorn carregou módulo antigo → docker restart resolveu.

---

## SELF-CHECK (12 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §97 última seção, INV-3 + INV-4 citados | ✅ |
| STEP 1 — `core/permissions.py` criado com CEO bypass + wildcard + module check | ✅ |
| STEP 2 — `financeiro/__init__.py` modificado com route.dependencies.append() | ✅ |
| STEP 3 — financeiro: Jordan {all} preservado | ✅ |
| STEP 4 — fiscal: Pyetra adicionada com module:fiscal | ✅ |
| STEP 5 — DP/RH: Pyetra, Eliziel, Orlailson, Ramon, Pedro com module:dp | ✅ |
| STEP 6 — CRM: Pyetra, Ramon, Pedro com module:crm | ✅ |
| STEP 7 — dev: Ramon, Pedro com module:dev | ✅ |
| STEP 8 — convites reenviados (Ramon + Ruan) via Chatwoot Rails | ✅ |
| STEP 9 — §97 adicionado ao CONTRACTS_GEDEON.md | ✅ |
| INV-3 — Jordan sempre tem acesso (CEO bypass no permissions.py) | ✅ |
| INV-4 — Financeiro = APENAS Jordan (validado com HTTP 403 para Ruan e Pyetra) | ✅ |

---

## Auditoria Pós-Execução (2ª passagem — linha por linha do prompt)

### Gap 1 — `epaiva@conectamais.pro` com `{all}` (violação INV-4) — CORRIGIDO

**Descoberto em:** auditoria pós-execução `SELECT ... WHERE 'all' = ANY(permissions)`
**Problema:** conta `epaiva@conectamais.pro` (Orlailson Paiva, email antigo) tinha `{all}`.
Com `{all}`, qualquer usuário com acesso a essa conta poderia acessar o módulo financeiro, violando INV-4.
**Correção:** `UPDATE users SET permissions = ARRAY['module:dp','module:operacional','module:ged'] WHERE email='epaiva@conectamais.pro'`
**Resultado:** Apenas `jjesus@conectamais.pro` permanece com `{all}`. INV-4 restabelecido.

### Gap 2 — §91 vs §97 (conflito de numeração)

**Prompt especificou:** `## §91 — Controle de acesso por módulo...`
**Conflito:** §91 já estava ocupado por "Diagnóstico profundo DP para matching GEDEON (CPRO12 T2-DIAG-DP)"
**Adaptação:** §97 utilizado (próximo disponível). Conteúdo idêntico ao especificado.

### Gap 3 — py_compile não foi executado explicitamente no STEP 7

**Prompt especificou:** `python3 -m py_compile backend/core/permissions.py`
**Estado anterior:** foi feito implicitamente (módulo carregou). **Executado na auditoria:** OK ✅

### Gap 4 — Ramon email: typo no prompt (corrigido na execução)

**Prompt especificou:** `ramondossantosaraujo16@gmail.com` (com 'a')
**Email real:** `romondossantosaraujo16@gmail.com` (com 'o', confirmado em T1-EQUIPE)
**Ação tomada:** email correto usado em todas as operações (permissions, Chatwoot, testes). ✅

---

## SELF-CHECK AUDITORIA (4 gaps — 3 corrigidos, 1 adaptação necessária)

| Gap | Tipo | Status |
|-----|------|--------|
| epaiva@conectamais.pro com {all} | CRÍTICO — viola INV-4 | ✅ Corrigido |
| §91 já ocupado → §97 | Adaptação necessária | ✅ Adaptado corretamente |
| py_compile não explícito | Menor | ✅ Executado na auditoria |
| Ramon email typo no prompt | Typo do prompt | ✅ Ignorado — email correto usado |

---

**T1 PERMISSOES CPRO12 OK — implementado, auditado e com correção de segurança aplicada.**
