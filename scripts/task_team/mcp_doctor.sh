#!/usr/bin/env bash
set -euo pipefail

echo "[MCP DOCTOR] Verificacao basica"

echo "- node: $(command -v node >/dev/null && echo ok || echo missing)"
echo "- npm:  $(command -v npm >/dev/null && echo ok || echo missing)"
echo "- npx:  $(command -v npx >/dev/null && echo ok || echo missing)"

check_env() {
  local v="$1"
  if [ -n "${!v:-}" ]; then
    echo "- env $v: ok"
  else
    echo "- env $v: missing"
  fi
}

for v in \
  GITHUB_PERSONAL_ACCESS_TOKEN \
  MCP_PG_USER MCP_PG_PASSWORD MCP_PG_HOST MCP_PG_PORT MCP_PG_DB \
  MCP_REDIS_HOST MCP_REDIS_PORT \
  SENTRY_AUTH_TOKEN PROMETHEUS_URL VAULT_ADDR VAULT_TOKEN; do
  check_env "$v"
done

echo "[MCP DOCTOR] Concluido"
