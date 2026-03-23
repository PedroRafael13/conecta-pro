#!/bin/bash
# =============================================================================
# Deploy Frontend — Conecta PRO
# Uso: bash scripts/deploy-frontend.sh
# =============================================================================
set -euo pipefail

FRONTEND_DIR="/opt/conecta-pro/frontend"
cd "$FRONTEND_DIR"

echo "=== Deploy Frontend — $(date '+%Y-%m-%d %H:%M:%S') ==="

# 1. Build
echo "[1/4] Building Next.js..."
rm -rf .next 2>/dev/null || true
NODE_OPTIONS=--max-old-space-size=4096 npx next build 2>&1 | tail -5

# 2. Verificar artefatos
if [ ! -f ".next/standalone/server.js" ]; then
  echo "ERRO: standalone/server.js não encontrado. Build falhou."
  exit 1
fi
if [ ! -f ".next/BUILD_ID" ]; then
  echo "AVISO: BUILD_ID não encontrado (Turbopack build). Continuando..."
fi

# 3. Copiar static assets para standalone
echo "[2/4] Copiando assets..."
cp -r public .next/standalone/public 2>/dev/null || true
cp -r .next/static .next/standalone/.next/static 2>/dev/null || true

# 4. Restart PM2
echo "[3/4] Restarting PM2..."
if pm2 describe conecta-pro-frontend > /dev/null 2>&1; then
  pm2 restart conecta-pro-frontend
else
  pm2 start ecosystem.config.js
fi
pm2 save

# 5. Health check
echo "[4/4] Health check..."
sleep 5
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "307" ]; then
  echo "=== Deploy OK — Frontend respondendo HTTP $HTTP_CODE ==="
else
  echo "=== AVISO — Frontend respondeu HTTP $HTTP_CODE ==="
  pm2 logs conecta-pro-frontend --err --lines 5 --nostream 2>/dev/null
fi
