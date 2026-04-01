# 📊 MONITORAMENTO DE PERFORMANCE - CONECTA PRO

**Data:** 2026-02-05
**Versão:** 1.0
**Objetivo:** Monitoramento contínuo de métricas de performance

---

## 📈 Métricas Principais

### 1. Métricas da Aplicação

#### 1.1 Tempo de Resposta
```python
# Configuração do Prometheus (exemplo)
from prometheus_client import Histogram

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'status']
)

# Uso em middleware FastAPI
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).observe(duration)

    return response
```

**Alertas recomendados:**
- `http_request_duration_seconds{quantile=0.95} > 1.0` (1 segundo)
- `http_request_duration_seconds{quantile=0.99} > 2.0` (2 segundos)

#### 1.2 Throughput
```python
from prometheus_client import Counter

requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
```

---

### 2. Métricas do Banco de Dados

#### 2.1 Queries Lentas
```sql
-- View para monitorar queries lentas
CREATE OR REPLACE VIEW slow_queries AS
SELECT
    queryid,
    query,
    calls,
    round(mean_exec_time::numeric, 2) as avg_ms,
    round(total_exec_time::numeric, 2) as total_ms,
    round(stddev_exec_time::numeric, 2) as stddev_ms,
    rows
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- Queries > 100ms
ORDER BY mean_exec_time DESC;

-- Uso
SELECT * FROM slow_queries LIMIT 10;
```

#### 2.2 Cache Hit Ratio
```sql
-- Cache hit ratio geral
SELECT
    sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) as cache_hit_ratio
FROM pg_statio_user_tables;

-- Cache hit ratio por tabela
SELECT
    schemaname,
    relname,
    heap_blks_hit,
    heap_blks_read,
    CASE
        WHEN heap_blks_hit + heap_blks_read > 0
        THEN round(100.0 * heap_blks_hit / (heap_blks_hit + heap_blks_read), 2)
        ELSE 0
    END as cache_hit_pct
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC
LIMIT 20;
```

**Alertas:**
- Cache hit ratio < 95% (tabelas frequentemente acessadas)

#### 2.3 Conexões
```sql
-- Monitorar uso de conexões
SELECT
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
    count(*) as total,
    max_connections
FROM pg_stat_activity, (SELECT setting::int as max_connections FROM pg_settings WHERE name = 'max_connections');

-- Conexões por aplicação/cliente
SELECT
    application_name,
    client_addr,
    count(*) as connections,
    count(*) FILTER (WHERE state = 'active') as active
FROM pg_stat_activity
GROUP BY application_name, client_addr
ORDER BY connections DESC;
```

**Alertas:**
- Conexões ativas > 80% do max_connections
- Conexões idle in transaction > 10

---

### 3. Métricas de Cache (Redis)

#### 3.1 Cache Hit/Miss Ratio
```bash
# Obter métricas do Redis
docker-compose exec redis redis-cli INFO stats

# Métricas importantes:
# - keyspace_hits: Total de hits
# - keyspace_misses: Total de misses
# - evicted_keys: Chaves removidas por memória
# - expired_keys: Chaves expiradas

# Calcular hit rate
HITS=$(docker-compose exec redis redis-cli INFO stats | grep keyspace_hits | cut -d: -f2)
MISSES=$(docker-compose exec redis redis-cli INFO stats | grep keyspace_misses | cut -d: -f2)
TOTAL=$((HITS + MISSES))

if [ $TOTAL -gt 0 ]; then
    HIT_RATE=$(echo "scale=2; $HITS * 100 / $TOTAL" | bc)
    echo "Cache Hit Rate: $HIT_RATE%"
fi
```

**Alertas:**
- Hit rate < 70%
- Evicted keys crescendo rapidamente (indica memória insuficiente)

#### 3.2 Memória e Performance
```bash
# Uso de memória
docker-compose exec redis redis-cli INFO memory

# Métricas:
# - used_memory: Memória usada
# - used_memory_rss: Memória residente
# - maxmemory: Limite configurado
# - mem_fragmentation_ratio: Razão de fragmentação (> 1.5 indica fragmentação)

# Performance
docker-compose exec redis redis-cli INFO commandstats
```

---

### 4. Dashboard de Monitoramento

#### 4.1 Exemplo de Dashboard (Grafana)
```json
{
  "dashboard": {
    "title": "Conecta PRO - Performance",
    "panels": [
      {
        "title": "Tempo de Resposta (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Cache Hit Ratio",
        "targets": [
          {
            "expr": "rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))"
          }
        ]
      },
      {
        "title": "PostgreSQL Cache Hit Ratio",
        "targets": [
          {
            "expr": "pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)"
          }
        ]
      },
      {
        "title": "Queries Lentas",
        "targets": [
          {
            "expr": "increase(pg_stat_statements_calls_total[1m])"
          }
        ]
      }
    ]
  }
}
```

---

## 🚨 Alertas Recomendados

### Alertas Críticos (PagerDuty)

| Métrica | Condição | Ação |
|---------|----------|------|
| Tempo de resposta p99 | > 5s | Investigar imediatamente |
| Erro HTTP 5xx | > 1% | Verificar logs |
| Conexões PostgreSQL | > 90% | Verificar pool de conexões |
| Memória Redis | > 90% | Aumentar memória ou limpar cache |
| Disk usage | > 85% | Limpar logs ou expandir storage |

### Alertas de Aviso (Slack/Email)

| Métrica | Condição | Ação |
|---------|----------|------|
| Tempo de resposta p95 | > 1s | Analisar queries lentas |
| Cache hit ratio | < 70% | Revisar estratégia de cache |
| Queries lentas | > 10/min | Otimizar índices |
| Autovacuum | > 10 tabelas pendentes | Executar vacuum manual |

---

## 📋 Queries Úteis para Monitoramento

### PostgreSQL

```sql
-- 1. Tabelas mais acessadas (leitura)
SELECT
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
ORDER BY seq_scan + idx_scan DESC
LIMIT 10;

-- 2. Índices não utilizados
SELECT
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

-- 3. Locks atuais
SELECT
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.state
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted OR l.mode = 'ExclusiveLock';

-- 4. Tamanho de tabelas e índices
SELECT
    schemaname,
    relname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||relname)) as indexes_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC
LIMIT 20;

-- 5. Vacuum status
SELECT
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST
LIMIT 20;
```

### Redis

```bash
# Informações gerais
redis-cli INFO

# Estatísticas detalhadas
redis-cli INFO stats

# Memória
redis-cli INFO memory

# Clientes conectados
redis-cli INFO clients

# Keyspace (databases)
redis-cli INFO keyspace

# Comandos mais usados
redis-cli INFO commandstats

# Slow log (comandos lentos)
redis-cli SLOWLOG GET 10
```

---

## 🔧 Scripts de Monitoramento

### Script de checagem rápida
```bash
#!/bin/bash
# quick_check.sh - Verificação rápida de saúde

echo "=== Conecta PRO - Health Check ==="
echo ""

# PostgreSQL
echo "PostgreSQL:"
docker-compose exec -T postgres psql -U postgres -c "
    SELECT 'Conexões: ' || count(*) || ' / ' || (SELECT setting FROM pg_settings WHERE name = 'max_connections')
    FROM pg_stat_activity;
"

docker-compose exec -T postgres psql -U postgres -c "
    SELECT 'Cache hit ratio: ' || round(sum(heap_blks_hit)::numeric / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100, 2) || '%'
    FROM pg_statio_user_tables;
"

# Redis
echo ""
echo "Redis:"
docker-compose exec -T redis redis-cli INFO memory | grep used_memory_human
docker-compose exec -T redis redis-cli INFO stats | grep keyspace | head -2

# Backend
echo ""
echo "Backend:"
curl -s http://localhost:8080/health | jq -r '.status // "ERROR"'

echo ""
echo "=== Check concluído ==="
```

### Script de relatório diário
```bash
#!/bin/bash
# daily_report.sh - Relatório diário de performance

REPORT_FILE="/var/log/conecta-pro/performance-$(date +%Y%m%d).log"

echo "Relatório de Performance - $(date)" > "$REPORT_FILE"
echo "================================" >> "$REPORT_FILE"

# PostgreSQL
echo -e "\n--- PostgreSQL ---" >> "$REPORT_FILE"
docker-compose exec -T postgres psql -U postgres -c "
    SELECT 'Queries lentas (>100ms): ' || count(*) FROM pg_stat_statements WHERE mean_exec_time > 100;
" >> "$REPORT_FILE" 2>/dev/null

# Redis
echo -e "\n--- Redis ---" >> "$REPORT_FILE"
docker-compose exec -T redis redis-cli INFO stats >> "$REPORT_FILE" 2>/dev/null

# Compactar relatórios antigos
find /var/log/conecta-pro -name "performance-*.log" -mtime +7 -exec gzip {} \;

echo "Relatório salvo em: $REPORT_FILE"
```

---

## 📊 KPIs de Performance

### Metas Mensuráveis

| KPI | Meta | Alerta Crítico |
|-----|------|----------------|
| Tempo médio de resposta | < 200ms | > 1s |
| Tempo p95 de resposta | < 500ms | > 2s |
| Tempo p99 de resposta | < 1s | > 5s |
| Throughput | > 100 req/s | < 50 req/s |
| Erro rate | < 0.1% | > 1% |
| Cache hit ratio | > 80% | < 70% |
| PostgreSQL cache hit | > 95% | < 90% |
| Conexões disponíveis | > 20% | < 10% |
| Queries lentas/hora | < 100 | > 500 |
| Tempo de uptime | > 99.9% | < 99% |

---

## 📝 Registro de Performance

### Template de Análise

```markdown
## Análise de Performance - [Data]

### Ambiente
- Versão: [X.X.X]
- Banco: PostgreSQL X.X
- Cache: Redis X.X
- Instâncias: [N]

### Métricas Coletadas
| Métrica | Valor | Meta | Status |
|---------|-------|------|--------|
| Latência média | [X]ms | < 200ms | [OK/NOK] |
| Cache hit | [X]% | > 80% | [OK/NOK] |
| PG cache hit | [X]% | > 95% | [OK/NOK] |

### Problemas Identificados
1. [Descrição]
   - Impacto: [Alto/Médio/Baixo]
   - Ação: [Corretiva]

### Ações Realizadas
- [ ] [Ação 1]
- [ ] [Ação 2]

### Próximos Passos
1. [Passo 1]
2. [Passo 2]

Responsável: [Nome]
```

---

**Documento criado:** 2026-02-05
**Revisar a cada:** Sprint (2 semanas)
