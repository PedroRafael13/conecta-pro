# INSTRUÇÕES OPUS — Plano de Deploy para Produção

**Papel:** Executor (infraestrutura, scripts, segurança, backup)
**Branch:** feature/openclaw-v2
**Plano completo:** `/opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md`

---

## CONTEXTO

O Plano Mestre de Produção foi concluído 100% (2026-02-10). O código está estável:
- Pytest: 6287/0 | ESLint: 0 warn | TypeScript: 0 err | Vitest: 1985/1985 | Build: OK

Agora você trabalha na infraestrutura de deploy. **NÃO toque no código da aplicação.**

---

## SUAS FASES (em ordem)

### FASE 1 — Scripts de Deploy & Rollback (1-2h)

#### 1.1 Criar `/opt/conecta-pro/scripts/deploy.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy automatizado do Conecta PRO
# Uso: ./scripts/deploy.sh [--skip-build] [--skip-migrate]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/deploy.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Funções auxiliares
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
error() { log "ERROR: $*"; exit 1; }

# Flags
SKIP_BUILD=false
SKIP_MIGRATE=false
for arg in "$@"; do
  case $arg in
    --skip-build) SKIP_BUILD=true ;;
    --skip-migrate) SKIP_MIGRATE=true ;;
  esac
done

log "=== DEPLOY INICIADO ($TIMESTAMP) ==="

# 1. Pre-flight checks
log "[1/7] Pre-flight checks..."
cd "$PROJECT_DIR"
source .env 2>/dev/null || error ".env não encontrado"
[ -n "${POSTGRES_PASSWORD:-}" ] || error "POSTGRES_PASSWORD não definido"
[ -n "${JWT_SECRET_KEY:-}" ] || error "JWT_SECRET_KEY não definido"

# 2. Git pull
log "[2/7] Atualizando código..."
git pull --ff-only || error "Git pull falhou (conflitos?)"

# 3. Backup database
log "[3/7] Backup do banco antes do deploy..."
bash "$SCRIPT_DIR/backup_database.sh" || log "WARN: Backup falhou, continuando..."

# 4. Build images
if [ "$SKIP_BUILD" = false ]; then
  log "[4/7] Building Docker images..."
  docker compose build --parallel || error "Build falhou"
else
  log "[4/7] Build pulado (--skip-build)"
fi

# 5. Run migrations
if [ "$SKIP_MIGRATE" = false ]; then
  log "[5/7] Rodando migrações Alembic..."
  docker compose run --rm backend alembic upgrade head || error "Migrações falharam"
else
  log "[5/7] Migrações puladas (--skip-migrate)"
fi

# 6. Deploy containers
log "[6/7] Iniciando containers..."
docker compose up -d || error "Docker compose up falhou"
docker compose -f docker-compose.celery.yml up -d 2>/dev/null || log "WARN: Celery compose não encontrado"

# 7. Health check com retry
log "[7/7] Verificando saúde dos serviços..."
MAX_RETRIES=30
RETRY_INTERVAL=2
for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
    log "Backend healthy (tentativa $i)"
    break
  fi
  [ "$i" -eq "$MAX_RETRIES" ] && error "Backend não respondeu após $MAX_RETRIES tentativas"
  sleep $RETRY_INTERVAL
done

for i in $(seq 1 $MAX_RETRIES); do
  if curl -sf -o /dev/null http://localhost:3001 2>&1; then
    log "Frontend healthy (tentativa $i)"
    break
  fi
  [ "$i" -eq "$MAX_RETRIES" ] && error "Frontend não respondeu após $MAX_RETRIES tentativas"
  sleep $RETRY_INTERVAL
done

# Notificar
if [ -n "${DISCORD_WEBHOOK:-}" ]; then
  curl -sf -H "Content-Type: application/json" \
    -d "{\"content\":\"Deploy Conecta PRO concluído com sucesso ($TIMESTAMP)\"}" \
    "$DISCORD_WEBHOOK" > /dev/null 2>&1 || true
fi

log "=== DEPLOY CONCLUÍDO COM SUCESSO ($TIMESTAMP) ==="
```

**Requisitos:**
- Deve ser idempotente (rodar múltiplas vezes sem problema)
- Chmod 755
- Testar com `bash -n scripts/deploy.sh` (syntax check)

#### 1.2 Criar `/opt/conecta-pro/scripts/rollback.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# rollback.sh — Rollback para versão anterior
# Uso: ./scripts/rollback.sh <commit-or-tag>
# Exemplo: ./scripts/rollback.sh v1.0.0
#          ./scripts/rollback.sh HEAD~1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TARGET="${1:-}"

[ -z "$TARGET" ] && { echo "Uso: $0 <commit-or-tag>"; exit 1; }

echo "[1/5] Backup antes do rollback..."
bash "$SCRIPT_DIR/backup_database.sh"

echo "[2/5] Parando containers..."
cd "$PROJECT_DIR"
docker compose down

echo "[3/5] Checkout para $TARGET..."
git checkout "$TARGET"

echo "[4/5] Rebuild e restart..."
docker compose build --parallel
docker compose up -d

echo "[5/5] Health check..."
sleep 10
curl -sf http://localhost:8080/health && echo " Backend OK" || echo " Backend FALHOU"
curl -sf -o /dev/null http://localhost:3001 && echo " Frontend OK" || echo " Frontend FALHOU"

echo "Rollback para $TARGET concluído."
```

#### 1.3 Criar `/opt/conecta-pro/scripts/health-check.sh`

```bash
#!/usr/bin/env bash
# health-check.sh — Verificação rápida de saúde de todos os serviços
# Exit 0 = tudo OK, Exit 1 = algo falhou

ERRORS=0

check() {
  local name="$1" cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    echo "  OK  $name"
  else
    echo "  FAIL $name"
    ERRORS=$((ERRORS + 1))
  fi
}

echo "=== Health Check Conecta PRO ==="
check "Backend API"    "curl -sf http://localhost:8080/health"
check "Frontend"       "curl -sf -o /dev/null http://localhost:3001"
check "PostgreSQL"     "docker exec conecta-pro-postgres pg_isready -U postgres"
check "Redis"          "docker exec conecta-pro-redis redis-cli ping"
check "Prometheus"     "curl -sf http://localhost:9090/-/ready"
check "Grafana"        "curl -sf -o /dev/null http://localhost:3000/api/health"

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "Todos os serviços saudáveis."
  exit 0
else
  echo "$ERRORS serviço(s) com problema."
  exit 1
fi
```

**Após criar os 3 scripts:**
```bash
chmod 755 /opt/conecta-pro/scripts/deploy.sh
chmod 755 /opt/conecta-pro/scripts/rollback.sh
chmod 755 /opt/conecta-pro/scripts/health-check.sh
bash -n /opt/conecta-pro/scripts/deploy.sh    # syntax check
bash -n /opt/conecta-pro/scripts/rollback.sh
bash -n /opt/conecta-pro/scripts/health-check.sh
```

---

### FASE 2 — Segurança & Secrets (30min)

#### 2.1 Auditar .env
```bash
# Verificar permissões
ls -la /opt/conecta-pro/.env
# Deve ser: -rw------- 1 root root

# Corrigir se necessário
chmod 600 /opt/conecta-pro/.env

# Verificar .gitignore
grep -q "^\.env$" /opt/conecta-pro/.gitignore && echo "OK: .env no .gitignore" || echo "FALTA: adicionar .env ao .gitignore"

# Verificar se foi commitado
git log --all --oneline -- .env | head -5
# Se aparecer algo, é problema
```

#### 2.2 Corrigir backup_database.sh
```
O script atual tem credenciais hardcoded:
  DB_USER="conecta_user"
  PGPASSWORD=conecta_secret_2024

Corrigir para:
  source "$(dirname "$0")/../.env"
  DB_USER="${POSTGRES_USER:?POSTGRES_USER não definido}"
  export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD não definido}"
```

#### 2.3 Verificar CORS
```bash
# No backend, verificar CORS_ORIGINS
grep -r "CORS\|cors" /opt/conecta-pro/backend/main*.py /opt/conecta-pro/backend/core/config* 2>/dev/null
# Não deve ter allow_origins=["*"] em produção
```

---

### FASE 5 — Backup & DR (1h)

#### 5.1 Executar backup
```bash
cd /opt/conecta-pro && bash scripts/backup_database.sh
```

#### 5.2 Testar restore
```bash
# Encontrar último backup
BACKUP=$(ls -t /opt/conecta-pro/backups/postgresql/*.sql.gz 2>/dev/null | head -1)
# Se dir diferente, ajustar

# Criar db temporário
docker exec conecta-pro-postgres createdb -U postgres conecta_pro_restore_test

# Restore
gunzip -c "$BACKUP" | docker exec -i conecta-pro-postgres psql -U postgres conecta_pro_restore_test

# Contar tabelas
docker exec conecta-pro-postgres psql -U postgres conecta_pro_restore_test -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"

# Limpar
docker exec conecta-pro-postgres dropdb -U postgres conecta_pro_restore_test
```

#### 5.3 Configurar cron
```bash
# Verificar cron atual
crontab -l 2>/dev/null

# Adicionar backup diário 3AM (se não existir)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/conecta-pro/scripts/backup_database.sh >> /var/log/conecta-backup.log 2>&1") | sort -u | crontab -
```

#### 5.4 Documentar RTO/RPO
Criar em `/opt/conecta-pro/docs/DISASTER-RECOVERY.md`:
```
RTO: X minutos (tempo medido do restore)
RPO: 24 horas (backup diário)
Procedimento: [passos do restore]
```

---

## COMUNICAÇÃO

Ao iniciar:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"opus","type":"status","subject":"Deploy Phase Start","content":"Iniciando Fase 1 - Scripts deploy/rollback"}' >> /opt/conecta-pro/.comms/messages/opus-exec-out.jsonl
```

Ao concluir cada fase:
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"opus","type":"done","subject":"Fase X Concluída","content":"RESULTADO AQUI"}' >> /opt/conecta-pro/.comms/messages/opus-exec-out.jsonl
```

---

## REGRAS

1. **NÃO toque no código da aplicação** (backend/frontend) — só infra/scripts
2. **NÃO rode docker compose up** até Fase 8 (staging deploy é conjunto)
3. **Teste cada script** com syntax check antes de commitar
4. **Commite após cada fase** com formato: `infra(escopo): descrição`
5. Se algo falhar, reporte no canal — NÃO tente corrigir sem aprovação
