# MCP Specialist Setup Guide - Conecta PRO

## Servidores configurados
- github
- postgres
- redis
- docker
- sentry
- prometheus
- playwright
- vault

## Credenciais/variaveis necessarias
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `MCP_PG_USER`
- `MCP_PG_PASSWORD`
- `MCP_PG_HOST`
- `MCP_PG_PORT`
- `MCP_PG_DB`
- `MCP_REDIS_HOST`
- `MCP_REDIS_PORT`
- `SENTRY_AUTH_TOKEN`
- `PROMETHEUS_URL`
- `VAULT_ADDR`
- `VAULT_TOKEN`

## Observacoes
1. Alguns servidores MCP podem exigir pacote alternativo dependendo do provedor.
2. Se um comando MCP nao existir no npm, substituir no config.toml pelo pacote correto da sua stack.
3. Validar sempre com `list_mcp_resources` apos reiniciar o Codex.

## Checklist de ativacao
1. Exportar credenciais no ambiente.
2. Reiniciar Codex.
3. Verificar se os MCPs aparecem em `list_mcp_resources`.
4. Executar um teste por MCP (query simples / health / leitura de recurso).
