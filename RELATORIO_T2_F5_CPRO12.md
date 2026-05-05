# T2 F5 CPRO12 — Fix Beat Healthcheck
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Módulo:** celery-beat (healthcheck)
**Branch:** feature/people-management-reorganization

---

## Diagnóstico

**Healthcheck antes:**
```
CMD-SHELL: ps aux | grep 'celery.*beat' | grep -v grep || exit 1
Interval: 30s | Timeout: 10s | StartPeriod: 30s | Retries: 3
```
**Status antes:** unhealthy (FailingStreak: **297**)
**Causa:** `/bin/sh: ps: not found` — `ps` não existe na imagem slim do container.
Beat funciona normalmente — **falso negativo**.

---

## Hipóteses

| Hipótese | Resultado |
|----------|-----------|
| H1: `ps` ausente confirmado | ✅ `/bin/sh: 1: ps: not found` — FailingStreak 297 |
| H2: `kill -0 1` funciona | ❌ `kill` binário ausente no container |
| H3: `celery inspect ping` funciona | ✅ outros workers respondem, mas beat não é worker — não responde ao ping beat@$HOSTNAME |
| H4: `docker update --health-cmd` suportado | ❌ `unknown flag` — Docker 29.1.3 não tem esta flag |
| H5: beat healthy após update | N/A — update não aplicado (CENÁRIO B) |
| H6: beat continua schedulando | ✅ `Sending due task` a cada 30s (solides, integrations, etc.) |
| H7: batch healthcheck referência | `celery -A celery_app inspect ping -d batch@$HOSTNAME` |

---

## Alternativas disponíveis (testadas no container)

| Comando | Funciona? | Observação |
|---------|-----------|------------|
| `python3 -c "import os; os.kill(1, 0)"` | ✅ | Disponível na imagem — ideal como substituto |
| `sh -c "test -f /proc/1/status"` | ✅ | Puro filesystem, sem dependência de binário |
| `kill -0 1` (shell) | ❌ | `kill` binário ausente |
| `ps aux \| grep ...` (atual) | ❌ | `ps` ausente — causa do unhealthy |
| `celery inspect ping -d beat@$HOSTNAME` | ❌ | Beat é scheduler, não worker — não responde ao ping |

---

## CENÁRIO B — docker update não suportado

**Docker version:** 29.1.3
`docker update --health-cmd "..."` retorna `unknown flag: --health-cmd`.

O fix permanente exige recriar o container com novo healthcheck.
**Opções que requerem autorização de Jordan:**

**Opção A (preferida):** Editar `docker-compose.yml` + recriar container:
```yaml
healthcheck:
  test: ["CMD-SHELL", "python3 -c 'import os; os.kill(1,0)'"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```
Seguido de:
```bash
docker compose up --no-deps -d celery-beat
```

**Opção B:** `docker run` manual (sem tocar docker-compose):
```bash
docker run --health-cmd="python3 -c 'import os; os.kill(1,0)'" \
  --health-interval=30s --health-timeout=10s --health-retries=3 \
  ... (demais flags do container atual)
```

---

## Status Final

```
conecta-pro-celery-beat    Up 2h (unhealthy)  ⚠️  FALSO NEGATIVO
```
Beat **funcionando normalmente** — schedulando tasks a cada 30s.
Fix aguarda autorização de Jordan (Opção A ou B acima).

---

## Commit

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | 4fa144ec | §73 CONTRACTS_GEDEON.md |

---

## Cenário: B

`docker update --health-cmd` não suportado (Docker 29.1.3).
INV-9 aplicado: documentado, reportado Jordan, sem workaround invasivo.
INV-4 respeitado: docker-compose NÃO tocado.
INV-5 respeitado: beat NÃO reiniciado.

T2 F5 CPRO12 — **pendente autorização Jordan para Opção A (docker-compose) ou Opção B (docker run).**
