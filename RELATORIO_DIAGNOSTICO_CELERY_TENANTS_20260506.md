# Diagnóstico: Containers Celery + TenantStatus + health_occupational
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** DIAGNÓSTICO — estado dos workers + achados de inconsistência

---

## RESULTADO

> Todos os **7 workers Celery healthy**. Beat disparando tasks sem erros.
> Achado crítico: **`TenantStatus.INATIVO` usado em testes mas ausente no enum de produção**.

---

## #1 — Estado dos containers Celery

| Container | Status |
|-----------|--------|
| `conecta-pro-celery-beat` | Up 10 minutes (healthy) ✅ |
| `conecta-pro-celery-integrations` | Up 37 hours (healthy) ✅ |
| `conecta-pro-celery-priority` | Up 37 hours (healthy) ✅ |
| `conecta-pro-celery-sefaz` | Up 37 hours (healthy) ✅ |
| `conecta-pro-celery-nfse` | Up 37 hours (healthy) ✅ |
| `conecta-pro-celery-batch` | Up 39 hours (healthy) ✅ |
| `conecta-pro-celery-operacional` | Up 37 hours (healthy) ✅ |

Nenhum `celery-worker` genérico existe — esperado (fallback confirmado).

---

## #2 — Logs do celery-beat (últimos 40 linhas)

Beat totalmente limpo. Tasks disparando em cadência correta:

| Task | Cadência |
|------|----------|
| `solides-process-webhooks` | a cada 30s |
| `sync-work-schedules-solides` | a cada 60s |
| `gedeon-risk-monitor-5min` | a cada 5min |
| `check-endpoints-5min` | a cada 5min |
| `solides-health-check-all` | a cada 5min |
| `operacional-check-late-employees` | a cada 5min |

**Zero erros. Zero crashes.** ✅

---

## #3 — TenantStatus — achado de inconsistência

### Enum em produção (`modules/config/models/tenant.py:17`)

```python
class TenantStatus(StrEnum):
    ATIVO     = "ATIVO"
    TRIAL     = "TRIAL"
    SUSPENSO  = "SUSPENSO"
    BLOQUEADO = "BLOQUEADO"
    CANCELADO = "CANCELADO"
```

### Uso em testes (inconsistente)

| Arquivo | Linha | Uso inválido |
|---------|-------|--------------|
| `tests/test_config_service.py` | 248 | `TenantStatus.INATIVO` ← **não existe** |
| `tests/test_config_model.py` | 95 | `TenantStatus.INATIVO` ← **não existe** |

`INATIVO` não está definido no enum de produção. Os testes que usam esse valor
falharão com `AttributeError` se executados contra o modelo real.

### Impacto

- Testes unitários que instanciam `TenantStatus.INATIVO` lançam `AttributeError`
- Produção não é afetada (o enum correto está em uso no código de produção)
- Fix necessário: remover `INATIVO` dos testes ou adicionar ao enum (conforme decisão de Jordan)

---

## #4 — health_occupational / PunchService

| Item | Estado |
|------|--------|
| Router registrado em `main_production.py:658` | ✅ presente |
| `class PunchService` | ❌ não existe em nenhum arquivo |
| Serviços presentes | `SafetyAIService`, `SafetyRiskAssessment`, `RiskLevel` |
| Tasks presentes (`tasks.py`) | ✅ confirmado sessão anterior |

`PunchService` nunca foi implementado no módulo `health_occupational`.
O módulo opera exclusivamente via `SafetyAIService`.

---

## SELF-CHECK

| Item | Status |
|------|--------|
| #1 — docker ps containers celery | ✅ |
| #2 — docker logs celery-beat --tail 40 | ✅ |
| #3 — grep TenantStatus enum + usos | ✅ |
| #4 — grep PunchService + health_occupational | ✅ |
| Achado TenantStatus.INATIVO documentado | ✅ |
| Achado PunchService ausente documentado | ✅ |

---

**Beat OK (healthy, 7 workers ativos). Achado crítico: TenantStatus.INATIVO em 2 arquivos de teste não corresponde ao enum de produção — requer decisão de Jordan.**
