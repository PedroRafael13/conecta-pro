# T2 F5 Opção A CPRO12 — Fix Beat Healthcheck
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Módulo:** celery-beat
**Branch:** feature/people-management-reorganization
**Autorização:** Jordan Jesus — 2026-05-05

---

## Diagnóstico

**Arquivo:** `docker-compose.celery.yml` (serviço `celery-beat`, linha 237)

**Healthcheck antes:**
```
test: ["CMD-SHELL", "ps aux | grep 'celery.*beat' | grep -v grep || exit 1"]
start_period: 30s
```
**FailingStreak antes:** 297+ (ps ausente na imagem slim)

**Healthcheck depois:**
```
test: ["CMD-SHELL", "python3 -c 'import os; os.kill(1, 0)' || exit 1"]
start_period: 60s
```

---

## Hipóteses

| Hipótese | Resultado |
|----------|-----------|
| H1: serviço beat encontrado | ✅ docker-compose.celery.yml linha 215 |
| H2: healthcheck usava ps | ✅ `ps aux \| grep 'celery.*beat'` linha 237 |
| H3: python3 disponível no container | ✅ Python 3.12.13 |
| H4: YAML OK antes | ✅ yaml.safe_load OK |
| H5: YAML OK depois | ✅ yaml.safe_load OK — test correto confirmado |
| H6: beat healthy em 90s | ✅ healthy em ~60s após recriação |
| H7: tasks sendo enviadas | ✅ 8 tasks no primeiro segundo de startup |
| H8: outros workers intactos | ✅ 6/6 workers continuam healthy |

---

## Incidente durante recriação

**Causa:** `docker compose up --no-deps -d celery-beat` recria o container
a partir da imagem base `conecta-pro-backend:latest`. A imagem não tem
`modules/operacional/ai/` (foi adicionado após o build da imagem).
O beat antigo rodava há 3h sem restart — tinha o módulo em memória/cache.

**Erro:**
```
ModuleNotFoundError: No module named 'modules.operacional.ai'
```

**Fix aplicado (escopo mínimo):**
```bash
docker cp backend/modules/operacional/ai conecta-pro-celery-beat:/app/modules/operacional/ai
```
Módulo copiado → container subiu → import OK → beat healthy.

**INV-10:** `modules.operacional.ai` ausente da imagem é bug pré-existente.
Documentado aqui mas não corrigido na imagem (escopo §13.4).

---

## Execução

| Step | Ação | Resultado |
|------|------|-----------|
| Backup | `docker-compose.celery.yml.bak.t2f5opcaoa` | ✅ criado e removido após sucesso |
| str_replace | apenas `test:` + `start_period:` do celery-beat | ✅ cirúrgico |
| YAML válido | antes + depois | ✅ |
| docker compose up | `--no-deps -d celery-beat` (INV-6) | ✅ |
| Módulo ausente | `operacional/ai` hot-copy | ✅ |
| Beat healthy | Up 55s (healthy), FailingStreak: 0 | ✅ |
| Scheduling | 8 tasks no primeiro segundo | ✅ |
| Outros workers | 6/6 healthy, inalterados | ✅ |

---

## Status Final

```
conecta-pro-celery-beat         Up 55s   (healthy)   ✅  ← antes: unhealthy FailingStreak 297
conecta-pro-celery-batch        Up 3h    (healthy)   ✅
conecta-pro-celery-integrations Up 59min (healthy)   ✅
celery-priority                 Up 59min (healthy)   ✅
celery-sefaz                    Up 59min (healthy)   ✅
celery-nfse                     Up 59min (healthy)   ✅
celery-operacional              Up 59min (healthy)   ✅
```

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | `a52b84c4` | `docs(contracts): §74 — Fix F5-A celery-beat healthcheck ps→python3 os.kill (CPRO12)` |
| fix | `9e6ba46b` | `fix(infra): celery-beat healthcheck ps→python3 os.kill — beat healthy (§74)` |

---

## Cenário: A

Beat passou de `unhealthy` (FailingStreak 297) para `healthy`.
Tasks schedulando imediatamente após startup.
Todos os workers intactos.

T2 F5 Opção A CPRO12 — **celery-beat: healthy ✅**
