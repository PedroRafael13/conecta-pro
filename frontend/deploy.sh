#!/bin/bash
# Deploy frontend — inclui copia de static para standalone
set -e

echo "=== BUILD ==="
export NODE_OPTIONS=--max-old-space-size=4096
rm -f .next/lock
npx next build

echo "=== COPY STATIC TO STANDALONE ==="
cp -r .next/static .next/standalone/.next/static
cp -r public .next/standalone/public 2>/dev/null || true

echo "=== RESTART PM2 ==="
PORT=3001 pm2 restart conecta-pro-frontend --update-env
pm2 save

echo "=== VERIFICACAO ==="
sleep 5
CHUNK=$(ls .next/standalone/.next/static/chunks/ | head -1)
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "http://127.0.0.1:3001/_next/static/chunks/$CHUNK")
echo "Chunk test: HTTP $STATUS"
[ "$STATUS" = "200" ] && echo "DEPLOY OK" || echo "DEPLOY FALHOU"
