# Relatório — Monitor Paths Fix
**Data:** 2026-04-01
**Commit:** 74f4219d
**Arquivo:** agents/skills_agent.py (linhas 156, 157, 179)

## Paths corrigidos

| Antes (404) | Depois | HTTP |
|-------------|--------|------|
| `/operacional/escalas/` | `/operacional/scales/` | ✅ 200 |
| `/operacional/turnos/` | `/operacional/shifts/` | ✅ 200 |
| `/portal/auth/me` | `/people-management/portal/auth/me` | ✅ 401 |

## Diagnóstico

Os paths usavam nomes em português (`escalas`, `turnos`) dos controllers antigos.
O backend foi refatorado para inglês (`scales`, `shifts`) durante a migração REST.
O `/portal/auth/me` estava faltando o prefixo `/people-management/` do módulo pai.

## Score esperado

| Métrica | Antes | Depois |
|---------|-------|--------|
| Bugs persistentes Telegram | 3 | 0 |
| Endpoints 404 no monitor | 3 | 0 |

## Próximo ciclo (~5 min)

Os alertas de 404 devem desaparecer do Telegram no próximo ciclo do monitor.
