# ✅ GUIA DE VALIDAÇÃO - PERFORMANCE QUICK WINS

**Data:** 2026-02-05
**Versão:** 1.0
**Objetivo:** Validar que as otimizações de performance foram aplicadas corretamente

---

## 📋 Checklist de Validação

### 1. Índices do Banco de Dados

#### 1.1 Verificar se índices foram criados
```bash
# Acessar PostgreSQL
docker-compose exec postgres psql -U postgres -d conecta_pro

# Listar índices criados
SELECT
    indexname,
    tablename,
    indexdef
FROM pg_indexes
WHERE indexname LIKE 'idx_%'
  AND schemaname = 'public'
ORDER BY tablename, indexname;
```

**Resultado esperado:** Pelo menos 12 índices criados:
- `idx_ged_docs_contract`
- `idx_occ_attach_occurrence`
- `idx_shifts_employee_date`
- `idx_payables_due_status`
- `idx_receivables_client`
- `idx_audit_logs_created_at`
- ... e outros

#### 1.2 Verificar uso de índices em queries
```sql
-- Verificar se queries estão usando os índices
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM ged_documents WHERE contract_id = '123e4567-e89b-12d3-a456-426614174000';

-- Deve mostrar "Index Scan" ou "Bitmap Index Scan"
-- Não deve mostrar "Seq Scan" para tabelas grandes
```

#### 1.3 Verificar tamanho dos índices
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes
JOIN pg_stat_user_indexes USING (indexrelname)
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;
```

---

### 2. Cache Redis

#### 2.1 Verificar conexão com Redis
```bash
# Testar conexão
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Deve retornar: PONG
```

#### 2.2 Verificar chaves de cache
```bash
# Listar chaves de cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD KEYS "*"

# Contar chaves por prefixo
docker-compose exec redis redis-cli -a $REDIS_PASSWORD KEYS "api:*" | wc -l
docker-compose exec redis redis-cli -a $REDIS_PASSWORD KEYS "ref:*" | wc -l
```

#### 2.3 Verificar hit rate do cache
```bash
# Obter estatísticas
docker-compose exec redis redis-cli -a $REDIS_PASSWORD INFO stats

# Calcular hit rate manualmente:
# keyspace_hits / (keyspace_hits + keyspace_misses) * 100
# Deve ser > 70% após algum tempo de uso
```

**Resultado esperado:**
- Cache respondendo a comandos
- Chaves sendo criadas (api:*, ref:*)
- Hit rate crescente conforme uso

---

### 3. N+1 Query Corrigida

#### 3.1 Verificar logs de queries
```bash
# Habilitar log de queries no PostgreSQL (se ainda não estiver)
docker-compose exec postgres psql -U postgres -c "SET log_min_duration_statement = 100;"

# Monitorar logs
docker-compose logs -f postgres | grep "duration:"

# Ao chamar o endpoint de sugestão de diaristas, deve ver apenas 2-3 queries
# Antes da correção: N+1 queries (uma por diarista)
```

#### 3.2 Testar endpoint específico
```bash
# Testar endpoint de sugestão de diaristas
curl -s -o /dev/null -w "%{time_total}" \
  http://localhost:8080/api/v1/operacional/diaristas/sugerir?post_id=XXX&data=2026-02-05

# Tempo deve ser < 500ms (antes podia ser 2-5s com muitos diaristas)
```

---

### 4. Configurações PostgreSQL

#### 4.1 Verificar configurações aplicadas
```sql
-- Verificar configurações críticas
SHOW max_connections;           -- Deve ser: 200
SHOW shared_buffers;            -- Deve ser: 512MB
SHOW effective_cache_size;      -- Deve ser: 1536MB
SHOW work_mem;                  -- Deve ser: 4MB
SHOW random_page_cost;          -- Deve ser: 1.1
SHOW log_min_duration_statement; -- Deve ser: 1000
```

#### 4.2 Verificar cache hit ratio
```sql
-- Cache hit ratio geral (deve ser > 95%)
SELECT
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;

-- Por tabela
SELECT
    schemaname,
    relname,
    heap_blks_hit,
    heap_blks_read,
    CASE WHEN (heap_blks_hit + heap_blks_read) > 0
         THEN heap_blks_hit::float / (heap_blks_hit + heap_blks_read)
         ELSE 0
    END as ratio
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC
LIMIT 10;
```

---

### 5. Tempo de Resposta de Endpoints

#### 5.1 Testar endpoints críticos
```bash
#!/bin/bash
# performance_test.sh

BASE_URL="http://localhost:8080"
ENDPOINTS=(
    "/health"
    "/api/v1/operacional/dashboard"
    "/api/v1/operacional/kpis"
    "/api/v1/config/estados"
    "/api/v1/clients/"
)

echo "Testing endpoints..."
echo "endpoint,status,time_ms"

for endpoint in "${ENDPOINTS[@]}"; do
    time_ms=$(curl -s -o /dev/null -w "%{time_total}" "${BASE_URL}${endpoint}")
    status=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${endpoint}")
    echo "${endpoint},${status},${time_ms}"
done
```

**Resultados esperados:**
| Endpoint | Tempo Máximo Aceitável | Meta |
|----------|----------------------|------|
| /health | 100ms | < 50ms |
| /api/v1/operacional/dashboard | 500ms | < 200ms |
| /api/v1/operacional/kpis | 500ms | < 200ms |
| /api/v1/config/estados | 200ms | < 50ms (com cache) |
| /api/v1/clients/ | 500ms | < 300ms |

---

### 6. Monitoramento Contínuo

#### 6.1 Configurar log de queries lentas
```sql
-- Verificar configuração
SHOW log_min_duration_statement;  -- Deve ser 1000 (ms)

-- Ver queries lentas recentes (requer pg_stat_statements)
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### 6.2 Monitorar conexões
```sql
-- Conexões ativas
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Conexões idle
SELECT count(*) FROM pg_stat_activity WHERE state = 'idle';

-- Conexões por aplicação
SELECT application_name, count(*)
FROM pg_stat_activity
GROUP BY application_name;
```

#### 6.3 Verificar autovacuum
```sql
-- Tabelas que precisam de vacuum
SELECT
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup * 100.0 / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 10;

-- Último vacuum/analyze
SELECT
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY last_autovacuum NULLS FIRST
LIMIT 10;
```

---

## 🔧 Scripts de Validação

### Script completo de validação
```bash
#!/bin/bash
# validate_performance.sh

set -e

echo "================================"
echo "Validação de Performance"
echo "================================"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Testar PostgreSQL
echo -n "PostgreSQL: "
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FALHA${NC}"
    exit 1
fi

# Testar Redis
echo -n "Redis: "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FALHA${NC}"
    exit 1
fi

# Testar Backend
echo -n "Backend: "
if curl -sf http://localhost:8080/health > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FALHA${NC}"
    exit 1
fi

# Contar índices
INDEX_COUNT=$(docker-compose exec -T postgres psql -U postgres -t -c "
    SELECT count(*) FROM pg_indexes WHERE indexname LIKE 'idx_%';
" 2>/dev/null | xargs)
echo "Índices criados: $INDEX_COUNT"

if [ "$INDEX_COUNT" -ge 10 ]; then
    echo -e "Índices: ${GREEN}OK${NC}"
else
    echo -e "Índices: ${RED}INSUFICIENTE${NC}"
fi

echo "================================"
echo "Validação concluída!"
```

---

## 📊 Métricas de Sucesso

### Após 24h de uso

| Métrica | Antes | Depois | Sucesso |
|---------|-------|--------|---------|
| Tempo médio dashboard | > 500ms | < 200ms | ✅ |
| Queries N+1 detectadas | > 10 | 0 | ✅ |
| Cache hit ratio | N/A | > 70% | ✅ |
| PostgreSQL cache hit | ~90% | > 95% | ✅ |
| Índices criados | 0 | 12+ | ✅ |
| Conexões simultâneas | 100 | 200 | ✅ |

### Após 1 semana

- Zero queries lentas (> 1s) em operação normal
- Cache hit ratio > 80%
- Dashboard carregando em < 100ms
- Nenhum timeout em operações normais

---

## ⚠️ Problemas Comuns e Soluções

### Problema: Índices não criados
**Sintoma:** Queries ainda lentas após migração
**Diagnóstico:**
```sql
SELECT count(*) FROM pg_indexes WHERE indexname LIKE 'idx_%';
```
**Solução:**
```bash
cd backend
alembic upgrade 20260205_192551
```

### Problema: Cache não funcionando
**Sintoma:** Mesmos dados sendo consultados no banco
**Diagnóstico:**
```bash
docker-compose exec redis redis-cli INFO stats | grep keyspace
```
**Solução:** Verificar se REDIS_URL está configurada corretamente no backend

### Problema: PostgreSQL não aceita conexões
**Sintoma:** "too many connections"
**Diagnóstico:**
```sql
SELECT count(*) FROM pg_stat_activity;
```
**Solução:** Aumentar max_connections ou ajustar pool do backend

---

## 📝 Registro de Validação

Data da validação: _______________

Responsável: _______________

| Item | Status | Observações |
|------|--------|-------------|
| Índices criados | ⬜ | |
| Cache funcionando | ⬜ | |
| N+1 corrigido | ⬜ | |
| PostgreSQL config | ⬜ | |
| Tempos de resposta | ⬜ | |

Assinatura: _______________

---

**Documento criado:** 2026-02-05
**Atualizar após:** Cada deploy de performance
