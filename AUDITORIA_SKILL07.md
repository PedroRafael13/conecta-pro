# AUDITORIA SKILL 07 — DOCKERFILE & CONTAINERS (CONECTA PRO)
> **Data:** 2026-03-31
> **Auditor:** Claude Sonnet 4.6
> **Branch:** feature/people-management-reorganization
> **Ambiente:** VPS srv1134814.hstgr.cloud (82.25.75.74) — 31.34 GiB RAM
> **Escopo:** 22 containers, 5 subagentes (Backend, PostgreSQL+Redis, Celery, Frontend PM2, Monitoring)

---

## PASSO INICIAL — SNAPSHOT DO AMBIENTE

```
Total de containers:  22
Imagens principais:
  - conecta-pro-backend:latest     1.98 GB  (customizada)
  - conecta-pro-frontend:latest      434 MB  (customizada)
  - postgres:16-alpine               243 MB
  - redis:7-alpine                    41 MB

Redes:
  - conecta-pro_conecta-pro-network  (backend, celery workers)
  - monitoring_monitoring            (prometheus, grafana, exporters)
  - conecta-staging-network          (staging containers)

Política de restart: unless-stopped em todos os containers ✅
```

---

## SUBAGENTE 1 — BACKEND CONTAINER

| # | Check | Status | Evidência |
|---|-------|--------|-----------|
| 1 | Imagem customizada (não oficial) | ✅ | `conecta-pro-backend:latest` multi-stage |
| 2 | Usuário não-root | ✅ | User: `erp` |
| 3 | Healthcheck configurado | ✅ | `curl /health/detailed`, interval 60s, retries 5 |
| 4 | Memory limit | ❌ | 0 (sem limite) — pode OOM o host |
| 5 | CPU shares | ❌ | 0 (sem limite) — spike de 108% detectado |
| 6 | Secrets em variáveis de ambiente | 🔴 | **CRÍTICO** — ver detalhes abaixo |
| 7 | Docker socket montado | ⚠️ | `/var/run/docker.sock` exposto no container |
| 8 | Restart policy | ✅ | `unless-stopped` |
| 9 | Log rotation | ⚠️ | `json-file` sem max-size / max-file |
| 10 | Container saudável | ✅ | `Up` (healthy), StartedAt: 2026-03-31 |

**Score: 5/10**

### Detalhes Críticos

#### 🔴 Check 6 — Secrets em texto plano nas env vars
O container expõe os seguintes segredos diretamente via `docker inspect`:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://postgres:<SENHA>@postgres:5432/conecta_pro
JWT_SECRET_KEY=<chave>
REDIS_URL=redis://:<senha>@redis:6379/0
SMTP_PASSWORD=<senha>
CERTIFICATE_PASSWORD=<senha>
```

**Risco:** Qualquer processo no host com acesso ao Docker daemon pode extrair todas as credenciais.
**Solução recomendada:** Docker Secrets (`docker secret create`) ou arquivo `.env` com permissão 600, nunca exposto como variável de ambiente visível.

#### ⚠️ Check 7 — Docker socket montado
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```
Permite ao container criar/destruir containers no host (equivalente a root no host).
**Risco:** Se o backend for comprometido, o host inteiro é comprometido.
**Solução:** Avaliar se o socket é realmente necessário (monitor interno?). Se sim, usar socket proxy socat com permissões restritas.

#### ❌ Checks 4 e 5 — Sem limites de recurso
Spike de CPU de 108% observado durante auditoria. Sem limite de memória, um leak pode consumir todo o RAM disponível (31.34 GiB) e crashar o sistema operacional.

---

## SUBAGENTE 2 — POSTGRESQL + REDIS

| # | Check | Status | Evidência |
|---|-------|--------|-----------|
| 1 | Volume nomeado persistente | ✅ | `conecta-pro_postgres_data` |
| 2 | Backup automatizado | ✅ | Cron diário 03:00 UTC com retenção |
| 3 | Redis persistência (RDB/AOF) | ⚠️ | NOAUTH — não verificado, mas AUTH ativo |
| 4 | Redis autenticação | ✅ | `requirepass` configurado |
| 5 | PostgreSQL porta não exposta | ✅ | Porta 5432 apenas interna (null externally) |
| 6 | Redis porta não exposta | ✅ | Porta 6379 apenas interna |
| 7 | Redis maxmemory configurado | ⚠️ | NOAUTH impediu verificação |
| 8 | Conexões PostgreSQL ativas | ✅ | 15/150 (10% de uso) |
| 9 | shared_buffers otimizado | ⚠️ | 128MB — muito baixo para 31.34 GiB RAM |
| 10 | Slow query logging ativo | ⚠️ | `log_min_duration_statement = -1` (desabilitado) |

**Score: 6/10**

### Detalhes

#### ⚠️ Check 9 — shared_buffers sub-ótimo
```
Atual:     shared_buffers = 128MB
Recomendado: ~7.8 GB (25% do RAM = 25% de 31.34 GiB)
```
PostgreSQL está usando cache interno mínimo. Queries que poderiam ser servidas da memória estão indo para disco.

#### ⚠️ Check 10 — Sem monitoramento de queries lentas
```sql
log_min_duration_statement = -1   (desabilitado)
log_statement = none
```
Impossível identificar queries lentas sem este parâmetro ativo. Recomendado definir como `1000` (1 segundo) para capturar queries problemáticas.

---

## SUBAGENTE 3 — CELERY WORKERS

| # | Check | Status | Evidência |
|---|-------|--------|-----------|
| 1 | Todos os workers rodando | ✅ | 6 workers + 1 beat ativos |
| 2 | Flower dashboard acessível | ✅ | HTTP 401 (autenticado) em :5555 |
| 3 | Queues configuradas corretamente | ✅ | 11 queues com prioridade, routing correto |
| 4 | Memory/CPU limits | ❌ | Todos com mem: 0 / cpu: 0 (sem limites) |
| 5 | Beat scheduler saudável | ✅ | Schedule file atualizado 2026-03-30 |
| 6 | Retry / acks_late configurado | ✅ | `task_acks_late=True`, `task_reject_on_worker_lost=True` |
| 7 | Dead letter queue | ❌ | Não configurado (sem `x-dead-letter-exchange`) |
| 8 | Monitor task em cron | ✅ | `skills_agent.py` a cada 30min |
| 9 | celery-integrations unhealthy | 🔴 | 3281 falhas consecutivas no healthcheck |
| 10 | Task timeouts configurados | ✅ | `soft_time_limit=300s`, `time_limit=600s` |

**Score: 6/10**

### Detalhes Críticos

#### 🔴 Check 9 — celery-integrations unhealthy por 3281 ciclos
O container `conecta-pro-celery-integrations` tem healthcheck configurado para:
```bash
curl -f http://localhost:${PORT}/health
# PORT=8080
```
**Problema:** O container é um **worker Celery** (não um servidor HTTP). Não há servidor web na porta 8080 dentro do container. O healthcheck foi copiado erroneamente do container backend.

**Impacto:** O worker está funcionando corretamente (processa tasks do Sólides com sucesso), mas reporta `unhealthy` para o Docker. Isso polui alertas e impede restart automático adequado.

```
Evidência de funcionamento normal:
[2026-03-30 16:57:55] Task solides.incremental_sync succeeded in 1.767s
  Result: {processed: 47, propagated: 41, not_found: 6}
```

**Solução:** Remover o healthcheck do docker-compose.yml para `celery-integrations` ou substituir por:
```bash
celery -A celery_app inspect ping -d integrations@${HOSTNAME} --timeout=10
```

#### ❌ Check 7 — Sem Dead Letter Queue
Tasks que falham definitivamente (após retries esgotados) são descartadas silenciosamente. Não há fila de quarentena para análise posterior.

**Solução:** Configurar DLQ nas queues críticas:
```python
Queue("gov.esocial", ..., queue_arguments={
    "x-dead-letter-exchange": "dlx",
    "x-dead-letter-routing-key": "dead.esocial"
})
```

### Workers e Queues

| Worker | Queues | Concurrência |
|--------|--------|-------------|
| priority | gov.esocial, gov.fgts | 2 |
| sefaz | gov.sefaz.nfe, gov.sefaz.cte, gov.sefaz.mdfe | 3 |
| nfse | gov.nfse | 2 |
| batch | gov.batch | 2 |
| operacional | operacional | 2 |
| integrations | integrations, webhooks | 2 |
| beat | (scheduler) | — |

---

## SUBAGENTE 4 — FRONTEND PM2

| # | Check | Status | Evidência |
|---|-------|--------|-----------|
| 1 | PM2 processo rodando | 🔴 | `errored` — 663 restarts |
| 2 | PM2 dump salvo | ✅ | `/root/.pm2/dump.pm2` (2026-03-28) |
| 3 | PM2 startup no boot | ✅ | `pm2-root` habilitado (systemd) |
| 4 | NODE_OPTIONS configurado | ✅ | `--max-old-space-size=4096` |
| 5 | Memória do processo | ⚠️ | 0b (errored) — não está consumindo |
| 6 | Porta 3001 respondendo | ✅ | HTTP 200 (via Docker container) |
| 7 | Next.js standalone build existe | ✅ | `server.js` atualizado 2026-03-30 |
| 8 | PM2 log rotation | ⚠️ | Ativo, mas error.log chegou a 1.1GB |
| 9 | PORT e env vars | ✅ | PORT=3001, NODE_ENV configurado |
| 10 | Container Docker frontend | ✅ | `conecta-pro-frontend` healthy (Docker) |

**Score: 5/10**

### Detalhes Críticos

#### 🔴 Check 1 — PM2 em estado `errored` com 663 restarts
```
Status:   errored
Restarts: 663
PID:      0 (não está rodando)
```

**Causa raiz (do log de erros):**
```
⨯ Failed to start server
Error: listen EADDRINUSE: address already in use 0.0.0.0:3001
```

**Explicação:** O container Docker `conecta-pro-frontend` já ocupa a porta 3001 mapeada. O PM2 tenta iniciar o mesmo `server.js` na porta 3001 e falha com `EADDRINUSE`.

**Situação atual:** O frontend está **funcionando normalmente** via o container Docker (`Up 20 hours, healthy`). O PM2 é redundante e está em conflito.

**Análise:** Há duas estratégias de deploy para o frontend:
1. **Docker container** (atual, funciona): `conecta-pro-frontend` no `docker-compose.yml`
2. **PM2 direto no host** (configuração legada): `pm2 start /opt/conecta-pro/frontend/.next/standalone/server.js`

Ambos tentam usar a porta 3001. O Docker venceu por ser mais rápido ao iniciar.

**Solução:** Escolher UMA estratégia e desativar a outra. Recomendado: Docker (já funciona). Remover/desativar o PM2 para `conecta-pro-frontend`.

#### ⚠️ Check 8 — PM2 error.log com 1.1 GB
```
conecta-pro-frontend-error.log__2026-03-31: 1.1 GB
conecta-pro-frontend-out.log__2026-03-31:  203 MB
Total /root/.pm2/logs/:                    1.3 GB
```
O log rotation acabou de rodar (arquivos renomeados), mas o tamanho acumulado é grande. As 663 falhas EADDRINUSE geraram volume massivo de logs.

---

## SUBAGENTE 5 — MONITORAMENTO (GRAFANA / PROMETHEUS)

| # | Check | Status | Evidência |
|---|-------|--------|-----------|
| 1 | Prometheus saudável | ✅ | HTTP 200 em /-/healthy |
| 2 | Grafana acessível | ✅ | Acessível via IP de container (172.19.0.6:3000) |
| 3 | Loki saudável | ✅ | HTTP 200 em /ready |
| 4 | AlertManager saudável | ✅ | HTTP 200 em /-/healthy |
| 5 | Alert rules configuradas | ✅ | 13 regras (PostgresDown, RedisDown, DiskSpace, etc.) |
| 6 | Dashboards configurados | ✅ | "ERP Conecta Mais - Dashboard" |
| 7 | Prometheus retention | ✅ | 30 dias |
| 8 | Promtail (Loki shipper) | ✅ | `erp-promtail` Up 3 semanas |
| 9 | Scrape targets saudáveis | ⚠️ | 4/4 up, mas backend **não está** sendo scrapeado |
| 10 | AlertManager receivers | ⚠️ | 5 receivers mas SMTP local (localhost:587) |

**Score: 7/10**

### Detalhes

#### ⚠️ Check 9 — Backend não scrapeado pelo Prometheus
```yaml
# prometheus.yml — backend está COMENTADO:
# - job_name: 'erp-backend'
#   static_configs:
#     - targets: ['172.19.0.1:8080']
#   metrics_path: /metrics
```

Scrape targets ativos: `node`, `postgres`, `redis`, `prometheus` apenas.
O backend FastAPI expõe métricas Prometheus (`/metrics` via `prometheus-fastapi-instrumentator`), mas não está sendo coletado.

**Impacto:** Nenhuma métrica de aplicação (latência de endpoints, erros HTTP, taxa de requisições) está sendo monitorada.

#### ⚠️ Check 10 — SMTP configurado para localhost:587
```yaml
smtp_smarthost: localhost:587
```
Se houver um alerta crítico, o AlertManager tentará enviar email via SMTP local, que provavelmente não existe. Alertas de email não chegam.
**Solução:** Configurar SMTP externo (Gmail/SendGrid/SMTP do provedor).

#### Regras de Alerta (13 regras)
```
[inactive] PostgresDown
[inactive] PostgresConnectionLost
[inactive] RedisDown
[inactive] DiskSpaceLow
[inactive] DiskSpaceCritical
[inactive] HighMemoryUsage
[inactive] HighLoadAverage
[inactive] SSLCertExpiringSoon
[inactive] SSLCertExpiringCritical
[inactive] BackupStale
[inactive] CeleryQueueBacklog
[inactive] CeleryQueueCritical
[inactive] PM2ExcessiveRestarts     ← deveria estar FIRING (663 restarts)
```

**Anomalia:** `PM2ExcessiveRestarts` deveria estar disparando dado os 663 restarts do frontend, mas está `inactive`. Verificar se a query Prometheus está correta para a métrica `pm2_restarts_total`.

---

## SCORECARD CONSOLIDADO

| Subagente | Área | Score | Status |
|-----------|------|-------|--------|
| 1 | Backend Container | 5/10 | ⚠️ CRÍTICO (secrets em env, sem limites) |
| 2 | PostgreSQL + Redis | 6/10 | ⚠️ ATENÇÃO (shared_buffers baixo) |
| 3 | Celery Workers | 6/10 | ⚠️ ATENÇÃO (integrations unhealthy, sem DLQ) |
| 4 | Frontend PM2 | 5/10 | 🔴 CRÍTICO (PM2 errored, 663 restarts, 1.1GB log) |
| 5 | Monitoramento | 7/10 | ⚠️ ATENÇÃO (backend não scrapeado) |
| **GLOBAL** | **Containers/DevOps** | **5.8/10** | **⚠️ REQUER ATENÇÃO** |

---

## PROBLEMAS CRÍTICOS (PRIORIDADE 1)

### 🔴 P1-A — Secrets em texto plano nas env vars do backend
**Risco:** Exposição de API keys (Anthropic, OpenAI), senha do banco, JWT secret
**Ação:** Migrar para Docker Secrets ou arquivo `.env` não inspecionável

### 🔴 P1-B — PM2 frontend em conflito com Docker (663 restarts, 1.3GB logs)
**Risco:** Desperdício de 1.3GB em disco, falsos alarmes no monitoring
**Ação:** `pm2 delete conecta-pro-frontend && pm2 save` — usar apenas Docker

### 🔴 P1-C — celery-integrations unhealthy por healthcheck incorreto (3281 falhas)
**Risco:** Worker reporta unhealthy quando está funcionando; mascara falhas reais
**Ação:** Remover ou corrigir o healthcheck do worker Celery

---

## PROBLEMAS DE ATENÇÃO (PRIORIDADE 2)

### ⚠️ P2-A — Todos os containers sem memory/CPU limits
**Risco:** OOM kill do host se qualquer container vazar memória
**Ação:** Definir limites no `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.5'
```

### ⚠️ P2-B — Backend não scrapeado pelo Prometheus
**Risco:** Nenhuma métrica de aplicação (latência, erros HTTP, throughput)
**Ação:** Descomentar e corrigir o job `erp-backend` no `prometheus.yml`

### ⚠️ P2-C — shared_buffers = 128MB (25x abaixo do ideal)
**Risco:** Queries que poderiam usar cache em memória vão para disco
**Ação:** `ALTER SYSTEM SET shared_buffers = '7800MB'; SELECT pg_reload_conf();`

### ⚠️ P2-D — Sem slow query logging
**Risco:** Impossível diagnosticar queries lentas em produção
**Ação:** `ALTER SYSTEM SET log_min_duration_statement = 1000;` (1 segundo)

### ⚠️ P2-E — Docker socket montado no backend
**Risco:** Escalada de privilégios se o backend for comprometido
**Ação:** Avaliar necessidade; se necessário, usar `docker-socket-proxy`

### ⚠️ P2-F — AlertManager SMTP localhost:587
**Risco:** Alertas de email nunca chegam
**Ação:** Configurar SMTP externo válido

### ⚠️ P2-G — Sem Dead Letter Queue nas filas Celery
**Risco:** Tasks falhas são descartadas silenciosamente
**Ação:** Configurar `x-dead-letter-exchange` nas queues críticas (gov.esocial, gov.fgts)

### ⚠️ P2-H — Log rotation do backend sem max-size
**Risco:** Logs `json-file` podem crescer indefinidamente
**Ação:** Adicionar ao docker-compose.yml:
```yaml
logging:
  driver: json-file
  options:
    max-size: "100m"
    max-file: "5"
```

---

## MELHORIAS RECOMENDADAS (PRIORIDADE 3)

| Item | Descrição |
|------|-----------|
| P3-A | Grafana acessível apenas via IP interno (porta 3000 conflita com Docker routing) |
| P3-B | PM2ExcessiveRestarts alert rule não está disparando (query incorreta?) |
| P3-C | Imagens do monitoring (prometheus, grafana) com 2 anos — considerar atualização |
| P3-D | `broker_connection_retry_on_startup` deprecated warning em todos os workers Celery |
| P3-E | Celery workers sem namespace explícito no compose (nomes com hash: `34bbe0bcda76_...`) |

---

## PLANO DE CORREÇÃO SUGERIDO

### Semana 1 (Críticos)
```bash
# P1-B: Resolver conflito PM2 vs Docker
pm2 delete conecta-pro-frontend
pm2 save

# P1-C: Corrigir healthcheck do celery-integrations
# No docker-compose.yml, substituir healthcheck do celery-integrations:
# healthcheck:
#   test: ["CMD", "celery", "-A", "celery_app", "inspect", "ping",
#           "-d", "integrations@$HOSTNAME", "--timeout=10"]
#   interval: 60s
#   retries: 3

# P1-A: Secrets — iniciar migração para Docker Secrets ou .env seguro
```

### Semana 2 (Atenção)
```bash
# P2-A: Resource limits
# Adicionar no docker-compose.yml de cada serviço

# P2-C: PostgreSQL shared_buffers
docker exec conecta-pro-postgres psql -U postgres -c \
  "ALTER SYSTEM SET shared_buffers = '7800MB'; SELECT pg_reload_conf();"

# P2-D: Slow query logging
docker exec conecta-pro-postgres psql -U postgres -c \
  "ALTER SYSTEM SET log_min_duration_statement = 1000; SELECT pg_reload_conf();"

# P2-B: Descomentar job erp-backend no prometheus.yml
# Restart prometheus
```

---

*Auditoria concluída em 2026-03-31 | Score global: 5.8/10 | 3 críticos, 8 atenção, 5 melhorias*
