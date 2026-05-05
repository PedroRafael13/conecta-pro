#!/usr/bin/env bash
# deploy_frontend.sh — Deploy Next.js frontend sem ChunkLoadError
#
# POR QUÊ PRESERVAR CHUNKS ANTIGOS:
#   Next.js gera chunks com hash de conteúdo (ex: ee79b3aa27b940fc.js).
#   Browsers cacheiam com `Cache-Control: immutable, 1y`.
#   Se o nginx recarregar antes do browser, o browser pede o chunk antigo → 404 → ChunkLoadError.
#   Solução: manter os chunks antigos acessíveis no container durante a transição.
#
# COMO O NGINX FUNCIONA AQUI:
#   /_next/static/ → proxy_pass http://frontend (container 127.0.0.1:3001)
#   proxy_cache static_cache + proxy_cache_valid 200 365d
#   Os chunks ficam no container — não no host filesystem.
#   Por isso: preservar chunks antigos = copiá-los de volta ao container após o deploy.
#
# USO:
#   ./scripts/deploy/deploy_frontend.sh [--dry-run]

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

FRONTEND_DIR="/opt/conecta-pro/frontend"
CONTAINER_NAME="conecta-pro-frontend"
BACKUP_DIR="/opt/conecta-pro/.chunk_archive"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

log()  { echo "[$(date +%H:%M:%S)] $*"; }
die()  { echo "[ERROR] $*" >&2; exit 1; }
run()  { $DRY_RUN && echo "[DRY-RUN] $*" || eval "$@"; }

# ── STEP 0: Resolve container name (pode ter prefixo de hash)
CONTAINER=$(docker ps --format "{{.Names}}" | grep "$CONTAINER_NAME" | head -1)
[[ -z "$CONTAINER" ]] && die "Container $CONTAINER_NAME não encontrado. Verifique: docker ps"
log "Container: $CONTAINER"

# ── STEP 1: Capturar BUILD_ID atual do host
HOST_BUILD_ID=$(cat "$FRONTEND_DIR/.next/BUILD_ID" 2>/dev/null || echo "NONE")
CONTAINER_BUILD_ID=$(docker exec "$CONTAINER" cat /app/.next/BUILD_ID 2>/dev/null || echo "NONE")
log "BUILD_ID host=$HOST_BUILD_ID  container=$CONTAINER_BUILD_ID"

# ── STEP 2: Salvar chunks antigos do container para arquivo local (INV-2: nunca deletar)
ARCHIVE_PATH="$BACKUP_DIR/$TIMESTAMP"
log "Arquivando chunks antigos do container → $ARCHIVE_PATH"
run "mkdir -p $ARCHIVE_PATH"
run "docker cp $CONTAINER:/app/.next/static/chunks/. $ARCHIVE_PATH/"
ARCHIVED=$(ls "$ARCHIVE_PATH" 2>/dev/null | wc -l || echo "?")
log "Chunks arquivados: $ARCHIVED"

# ── STEP 3: Build Next.js no host (serializado — nunca simultâneo)
log "Iniciando build Next.js..."
run "cd $FRONTEND_DIR && NODE_OPTIONS=--max-old-space-size=4096 npm run build"
NEW_BUILD_ID=$(cat "$FRONTEND_DIR/.next/BUILD_ID" 2>/dev/null || echo "NONE")
log "Novo BUILD_ID: $NEW_BUILD_ID"

# ── STEP 4: Sincronizar novo build → container
log "Sincronizando novo build → $CONTAINER"
run "docker cp $FRONTEND_DIR/.next/static/.     $CONTAINER:/app/.next/static/"
run "docker cp $FRONTEND_DIR/.next/standalone/. $CONTAINER:/app/.next/standalone/"
run "docker cp $FRONTEND_DIR/.next/server/.     $CONTAINER:/app/.next/server/"
run "docker cp $FRONTEND_DIR/.next/BUILD_ID     $CONTAINER:/app/.next/BUILD_ID"

# ── STEP 5: Reinjetar chunks antigos no container (preservação anti-ChunkLoadError)
log "Reinjetando chunks antigos → container (preservação)"
if [[ -d "$ARCHIVE_PATH" && "$(ls -A $ARCHIVE_PATH)" ]]; then
    run "docker cp $ARCHIVE_PATH/. $CONTAINER:/app/.next/static/chunks/"
    log "Chunks antigos preservados no container ✅"
else
    log "Nenhum chunk antigo para reinjetar (primeiro deploy?)"
fi

# ── STEP 6: Reiniciar container + pm2
log "Reiniciando container..."
run "docker restart $CONTAINER"
log "Aguardando container ficar healthy..."
for i in $(seq 1 30); do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || echo "none")
    [[ "$STATUS" == "healthy" || "$STATUS" == "none" ]] && break
    [[ $i -eq 30 ]] && die "Container não ficou healthy após 30s"
    sleep 1
done
run "pm2 restart all" || true

# ── STEP 7: Validação
log "Validando..."
sleep 3
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/ 2>/dev/null || echo "000")
CONTAINER_BUILD_ID_NEW=$(docker exec "$CONTAINER" cat /app/.next/BUILD_ID 2>/dev/null || echo "ERR")
CONTAINER_CHUNKS=$(docker exec "$CONTAINER" find /app/.next/static/chunks -name "*.js" | wc -l 2>/dev/null || echo "?")

log "HTTP /: $HTTP_CODE"
log "BUILD_ID container: $CONTAINER_BUILD_ID_NEW (host: $NEW_BUILD_ID)"
log "Chunks no container: $CONTAINER_CHUNKS"

[[ "$HTTP_CODE" == "200" ]] || die "Frontend não respondeu HTTP 200 (got $HTTP_CODE)"
[[ "$CONTAINER_BUILD_ID_NEW" == "$NEW_BUILD_ID" ]] || die "BUILD_ID mismatch host≠container"

log ""
log "✅  Deploy concluído com sucesso"
log "    BUILD_ID: $NEW_BUILD_ID"
log "    Chunks container: $CONTAINER_CHUNKS"
log "    Arquivo de chunks antigos: $ARCHIVE_PATH"
