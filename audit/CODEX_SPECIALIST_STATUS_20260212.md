# CODEX SPECIALIST STATUS (2026-02-12)

## Skills permanentes criadas
- ~/.codex/skills/conecta-pro-auditor
- ~/.codex/skills/conecta-pro-security-remediator
- ~/.codex/skills/conecta-pro-release-manager
- ~/.codex/skills/conecta-pro-test-orchestrator
- ~/.codex/skills/conecta-pro-architecture-map

Todas com:
- SKILL.md
- agents/openai.yaml
- references/
- scripts/ executáveis

## MCP base permanente configurada
- Arquivo: ~/.codex/config.toml
- MCPs declarados: github, postgres, redis, docker, sentry, prometheus, playwright, vault

## Pendências para ativação total
1. Preencher credenciais no ambiente (usar /opt/conecta-pro/.env.mcp.example como base).
2. Reiniciar sessão do Codex para carregar os MCP servers.
3. Executar validação:
   - list_mcp_resources
   - scripts/task_team/mcp_doctor.sh

## Resultado atual
- Especialização de skill: CONCLUÍDA
- Infra MCP declarativa: CONCLUÍDA
- MCPs online e autenticados: PENDENTE (depende de credenciais + restart)
