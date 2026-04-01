#!/usr/bin/env bash
# health-check.sh — Verificação rápida de saúde de todos os serviços
# Exit 0 = tudo OK, Exit 1 = algo falhou

ERRORS=0

check() {
  local name="$1"
  shift
  if "$@" > /dev/null 2>&1; then
    printf "  \033[0;32mOK\033[0m    %s\n" "$name"
  else
    printf "  \033[0;31mFAIL\033[0m  %s\n" "$name"
    ERRORS=$((ERRORS + 1))
  fi
}

echo "=== Health Check Conecta PRO ==="
echo ""

check "Backend API"    curl -sf http://localhost:8080/health
check "Frontend"       curl -sf -o /dev/null http://localhost:3001
check "PostgreSQL"     docker exec conecta-pro-postgres pg_isready -U postgres
check "Redis"          docker exec conecta-pro-redis redis-cli ping
check "Prometheus"     curl -sf http://localhost:9090/-/ready
check "Grafana"        curl -sf -o /dev/null http://localhost:3000/api/health
check "AlertManager"   curl -sf http://localhost:9093/-/ready
check "Loki"           curl -sf http://localhost:3100/ready

echo ""
if [ $ERRORS -eq 0 ]; then
  echo "Todos os 8 serviços saudáveis."
  exit 0
else
  echo "$ERRORS serviço(s) com problema."
  exit 1
fi
