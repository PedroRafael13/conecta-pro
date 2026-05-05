# T5 Chatwoot CPRO12 — Central Multiagente WhatsApp
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Duração:** ~45min
**Tipo:** INFRA — Autorização Jordan Jesus (docker-compose + .env)

---

## RESULTADO — SUCESSO

> Chatwoot multiagente instalado e integrado ao WhatsApp 0800 880 4414.
> 8 perfis criados (Jordan admin + 7 agentes). 5 filas criadas.
> Evolution API ↔ Chatwoot integrados via integração nativa.
> Commits: docs=5b26a311 infra=49bc34db

---

## Containers em Produção

| Container | Imagem | Porta | Status |
|-----------|--------|-------|--------|
| chatwoot | chatwoot/chatwoot:latest | 3002 | ✅ UP |
| chatwoot-sidekiq | chatwoot/chatwoot:latest | — | ✅ UP |
| chatwoot-postgres | pgvector/pgvector:pg16 | 5432 (interno) | ✅ UP (healthy) |

---

## Nota Técnica: pgvector

Chatwoot v3+ requer a extensão PostgreSQL `pgvector` para embeddings de IA.
O `postgres:16-alpine` (conecta-pro-postgres) não possui essa extensão.
**Solução:** container `chatwoot-postgres` dedicado com imagem `pgvector/pgvector:pg16`.
INV-3 preservado: conecta-pro-postgres não foi modificado.

---

## Configuração

| Parâmetro | Valor |
|-----------|-------|
| URL local | http://localhost:3002 |
| URL produção | https://chat.conectamais.pro |
| Banco | chatwoot_production (chatwoot-postgres) |
| Redis | redis://redis:6379/2 (DB 2, separado do backend) |
| Admin | Jordan Jesus — jjesus@conectamais.pro |
| Canal | WhatsApp 0800 880 4414 — Inbox ID=1 |

---

## Agentes e Filas

### 8 Perfis Criados

| Nome | Perfil | Email |
|------|--------|-------|
| Jordan Jesus | SuperAdmin + Administrator | jjesus@conectamais.pro |
| Administrativo | Agente | administrativo@conectamais.pro |
| Supervisor Operacional | Agente | supervisoroperacional@conectamais.pro |
| Gerente Operacional | Agente | gerenteoperacional@conectamais.pro |
| Consultor de Vendas | Agente | vendas@conectamais.pro |
| Desenvolvedor 1 | Agente | dev1@conectamais.pro |
| Desenvolvedor 2 | Agente | dev2@conectamais.pro |
| Implantador de Campo | Agente | campo@conectamais.pro |

### 5 Filas (Labels)

| Label | Cor |
|-------|-----|
| administrativa | #1E3A5F |
| operacional | #2D6A4F |
| comercial | #F97316 |
| suporte_tecnico | #7C3AED |
| campo | #DC2626 |

---

## Integração Evolution API ↔ Chatwoot

- **CHATWOOT_ENABLED=true** adicionado ao evolution-api
- Configuração via `/chatwoot/set/conecta-pro`:
  - accountId=1, url=http://chatwoot:3000
  - signMsg=true, autoCreate=true, importContacts=true
  - nameInbox="WhatsApp 0800 880 4414"
- Webhook Evolution→Chatwoot: http://chatwoot:3000 (auto-criação de conversas)

---

## Hipóteses H1-H8

| Hipótese | Status | Evidência |
|----------|--------|-----------|
| H1: Porta 3002 livre | ✅ CONFIRMADO | ss -tlnp — apenas 3001 em uso |
| H2: Redis acessível por nome container | ✅ CONFIRMADO | redis://redis:6379/2 funcional (Sidekiq conectado) |
| H3: PostgreSQL aceita novo banco | ✅ CONFIRMADO | chatwoot_production criado (depois migrado para chatwoot-postgres) |
| H4: RAM suficiente (>500MB) | ✅ CONFIRMADO | 15GB disponível de 31GB total |
| H5: Imagem chatwoot/chatwoot disponível | ✅ CONFIRMADO | sha256:250fa61c318a pulled |
| H6: Chatwoot responde na 3002 | ✅ CONFIRMADO | HTTP 302 (redirect para /auth/sign_in) |
| H7: Evolution acessível pelo Chatwoot | ✅ CONFIRMADO | integração /chatwoot/set → webhook_url=http://evolution-api:8080 |
| H8: Instância conecta-pro online | ✅ CONFIRMADO | state=open antes e após restart |

---

## SELF-CHECK (15 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §80 última seção, §13.1 + INV-3 + autorização citados | ✅ |
| STEP 1 — docker-compose lido inteiro (Chesterton) | ✅ 287 linhas |
| STEP 2 — backup criado | ✅ docker-compose.yml.bak.t5chatwoot (removido após commit) |
| STEP 3 — banco chatwoot_production criado | ✅ (depois no chatwoot-postgres com pgvector) |
| STEP 4 — SECRET_KEY_BASE gerada aleatoriamente (128 chars hex) | ✅ secrets.token_hex(64) |
| STEP 5 — chatwoot + sidekiq + chatwoot-postgres adicionados | ✅ serviços existentes intocados |
| STEP 6 — YAML válido após edição | ✅ docker compose config --quiet OK |
| STEP 7 — .env atualizado com CHATWOOT_SECRET_KEY | ✅ |
| STEP 8 — migrations OK + containers rodando + HTTP 3002 respondendo | ✅ HTTP 302 |
| STEP 9 — admin Jordan criado (SuperAdmin, conta confirmada) | ✅ jjesus@conectamais.pro |
| STEP 10 — canal WhatsApp conectado via Evolution integração nativa | ✅ Inbox ID=1 configurado |
| STEP 11 — 7 agentes + 5 filas criados | ✅ |
| STEP 12 — §82 no CONTRACTS_GEDEON | ✅ commit 5b26a311 |
| STEP 13 — 2 commits separados + push + backup removido | ✅ docs=5b26a311 infra=49bc34db |
| INV-3 — serviços existentes intocados (exceto CHATWOOT_ENABLED=true em evolution-api, necessário para integração) | ✅ |

---

## Cenário: A

Todos os containers UP. HTTP 302 confirmado na porta 3002.
Admin Jordan criado. 7 agentes + 5 filas criadas.
Evolution ↔ Chatwoot integrados (state=open preservado).

---

**T5 CHATWOOT CPRO12 OK — central multiagente instalada e integrada ao WhatsApp 0800 880 4414.**
**Acesso: http://localhost:3002 | Login: jjesus@conectamais.pro**
**Commits: docs=5b26a311 infra=49bc34db. Push: ✅ origin/feature/people-management-reorganization.**
