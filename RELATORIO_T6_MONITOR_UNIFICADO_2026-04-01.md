# Relatório T6 — Monitor Unificado
**Data:** 2026-04-01
**Commit:** 9fcee18a
**Branch:** feature/people-management-reorganization

---

## Antes (2 sistemas em conflito)

| Sistema | Cron | Credenciais | Score Telegram |
|---------|------|-------------|----------------|
| `skills_agent.py` | não estava no cron | `egonzaga@conectamais.pro` (usuário diferente!) | score próprio por método diferente |
| `orchestrator_geral.py` | `*/30` | `jjesus@conectamais.pro` | 13 orquestradores |
| `monitor_heartbeat.sh` | `0 */6` | bash script | CPU/RAM/Disco |
| `health_check.sh` | `*/5` | **não existia** (silent fail) | — |

**Problemas:**
- `skills_agent.py` usava usuário diferente (`egonzaga`) → scores divergentes
- `health_check.sh` não existia → cron `*/5` falhava silenciosamente há semanas
- `monitor_heartbeat.sh` era bash com 150+ linhas de shell frágil
- 2+ mensagens por ciclo de 30min → confusão no Telegram

## Depois (1 sistema unificado)

**`agents/orchestrator_unificado.py`** — 3 modos:

| Modo | Cron | O que faz | Telegram |
|------|------|-----------|---------|
| `rapido` | `*/5` | containers + endpoints críticos | Silencioso se OK; alerta em regressão ou bug persistente (3+) |
| `completo` | `*/30` | rápido + 13 orquestradores + banco | Relatório completo por módulo |
| `heartbeat` | `0 */6` | rápido + CPU/RAM/Disco/PM2/Redis | Relatório de infraestrutura |

**Crons ativos:**
```
*/5  → python3 agents/orchestrator_unificado.py rapido
*/30 → python3 agents/orchestrator_unificado.py completo
0/6  → python3 agents/orchestrator_unificado.py heartbeat
```

## O que foi absorvido

### Do `skills_agent.py`
- `check_containers()` — 4 containers críticos com weight x2 no score
- `check_endpoints()` — 6 módulos: Operacional/GED/Financeiro/DP/Portal/IA
- `check_database()` — query direta ao PostgreSQL (users count)
- `check_recent_errors()` — contagem rápida de erros 500
- `monitor_state.py` + `regression_detector.py` integração
- Score combinado: containers (peso 2) + endpoints por módulo

### Do `orchestrator_geral.py`
- `_load_pyc()` — carrega bytecode compilado se .py ausente
- `_injetar_token()` — monkey-patch em BaseAgent + BaseOrchestrator
- `_obter_token_com_retry()` — retry exponencial 65s/130s/195s
- 13 orquestradores com renovação automática de token
- Relatório JSON em `reports/modules/ciclo_geral_*.json`

### Do `monitor_heartbeat.sh`
- PM2 status check
- Redis ping via docker exec
- Backend health check (HTTP 200)
- Leitura do `monitor_state.json` (ciclos/correções/regressões/melhor_score)
- Indicadores CPU/RAM coloridos (🟢/🟡/🔴)

## Resultado dos testes

```
rapido:     Score 10.0/10 | Containers 4/4 | Erros 0 | 0.4s  ✅
heartbeat:  Enviado ao Telegram ✅
completo:   Score 9.8/10 | 13 módulos OK | 52s ✅
```

## `skills_agent.py`
**Status: DESATIVADO** → renomeado para `skills_agent.py.DESATIVADO`

## Download
```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T6_MONITOR_UNIFICADO_2026-04-01.md ~/Downloads/
```
