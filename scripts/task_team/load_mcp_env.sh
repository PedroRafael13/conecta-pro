#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-/opt/conecta-pro/.env.mcp.example}"
if [ ! -f "$ENV_FILE" ]; then
  echo "Arquivo nao encontrado: $ENV_FILE"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

echo "Variaveis MCP carregadas de: $ENV_FILE"
