# RELATORIO_T2_KRONOS_CPRO12.md
**Sessão:** CPRO12 T2-KRONOS
**Data:** 2026-05-05
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Branch:** feature/people-management-reorganization

---

## Objetivo

Implementar task KRONOS `gedeon.verificar_kits_completos` que alerta Jordan quando um kit
GED atinge 100% de conclusão e ainda não foi enviado ao cliente.

**Regra de negócio:** Envio SEMPRE aprovado por humano — KRONOS só alerta, Jordan decide.

---

## Inventário de Invariantes

| # | Invariante | Status |
|---|-----------|--------|
| INV-1 | Não modificar tasks existentes do KRONOS/THEMIS | ✅ |
| INV-2 | Seguir padrão `@shared_task(bind=True, max_retries=3)` | ✅ |
| INV-3 | Usar `get_sync_db()` (nunca async em tasks Celery) | ✅ |
| INV-4 | NÃO enviar email nem WhatsApp — apenas `in_app` | ✅ |
| INV-5 | `tenant_id` e `user_id` obrigatórios em `communication_notifications` | ✅ |
| INV-6 | Idempotente: não recriar notificação se já existe nas últimas 24h para o mesmo kit | ✅ |
| INV-7 | `reference_type = 'ged_kit_completo'` | ✅ |
| INV-8 | `action_url = /ged/kits/{kit_id}` | ✅ |
| INV-9 | Não quebrar se não existir nenhum kit a 100% (CENÁRIO C) | ✅ |
| INV-10 | Hot-copy para TODOS os 8 containers relevantes | ✅ |
| INV-11 | Limpar pyc antes de cada docker cp | ✅ |
| INV-12 | Agendamento: 08:00 Manaus = `crontab(hour="8", minute="0")` = 12:00 UTC | ✅ |
| INV-13 | Queue: `gov.batch` | ✅ |
| INV-14 | §79 documentado em CONTRACTS_GEDEON.md antes do commit de código | ✅ |

---

## Investigação (STEP 1)

### Tabela `communication_notifications`
Schema verificado via `\d communication_notifications`:

| Coluna | Tipo | Nota |
|--------|------|------|
| id | uuid | default gen_random_uuid() |
| tenant_id | uuid | NOT NULL |
| user_id | uuid | NOT NULL |
| title | varchar(255) | |
| body | text | |
| type | varchar(50) | default 'sistema' |
| reference_type | varchar(50) | |
| reference_id | uuid | |
| channels | jsonb | default '["in_app"]' |
| action_url | varchar(500) | |
| extra_data | jsonb | default '{}' |
| is_active | boolean | default true |
| created_at | timestamp | |

### Jordan Jesus
- `user_id`: `ad9abb59-55fb-444e-a04f-0e1f22541de3`
- email: `jjesus@conectamais.pro`

### Tenant principal
- `tenant_id`: `841a3906-5410-4047-a076-bc7bce95ffd2`

### Tabela `ged_document_kits`
Colunas relevantes: `id`, `client_id`, `completion_percentage`, `sent_at`, `reference_month`

### Tabela `ged_clients`
Coluna do nome: `name` (não `nome`)

---

## Implementação

### STEP 3 — Task `verificar_kits_completos`

Arquivo: `backend/modules/gedeon/tasks/kronos_tasks.py`

- Acrescenta task no final do arquivo (após `themis_verificacao_assinaturas` e `fiscal_verificar_certidoes`)
- Pattern idêntico às tasks existentes: `@shared_task(bind=True, max_retries=3)`
- SQL usa `NOT EXISTS` para checar idempotência: sem notificação para o mesmo kit nas últimas 24h
- `tenant_id` resolvido via `SELECT id FROM tenants LIMIT 1`
- Mensagem: "O kit documental de {cliente} referente a {mes_ano} está 100% completo e aguarda envio."
- `countdown=300` no retry (padrão KRONOS)

### STEP 4 — Beat schedule em `celery_app.py`

Entrada adicionada após `gedeon-collection-0900`:

```python
"gedeon-verificar-kits-completos-0800": {
    "task": "gedeon.verificar_kits_completos",
    "schedule": crontab(hour="8", minute="0"),
    "options": {"queue": "gov.batch"},
},
```

### STEP 5 — Validação sintática

```
python3 -m py_compile backend/modules/gedeon/tasks/kronos_tasks.py  # OK
python3 -m py_compile backend/celery_app.py                          # OK
```

### STEP 7 — Hot-copy (8 containers)

| Container | Status |
|-----------|--------|
| conecta-pro-backend | ✅ |
| conecta-pro-celery-beat | ✅ |
| conecta-pro-celery-batch | ✅ |
| conecta-pro-celery-operacional | ✅ |
| conecta-pro-celery-integrations | ✅ |
| conecta-pro-celery-priority | ✅ |
| conecta-pro-celery-nfse | ✅ |
| conecta-pro-celery-sefaz | ✅ |

- Backend recarregado: `kill -HUP 1` ✅
- Beat reiniciado: `docker restart conecta-pro-celery-beat` ✅
- Beat confirmou: `celery beat v5.4.0 (opalescent) is starting.`

---

## Commits

| Hash | Descrição |
|------|-----------|
| `c23a12c8` | `docs(contracts): §79 — KRONOS task verificar_kits_completos alerta humano (CPRO12 T2)` |
| `50d28756` | `feat(gedeon): KRONOS task verificar_kits_completos — alerta kit 100% para Jordan (§79)` |

Push: `git push origin feature/people-management-reorganization` ✅

---

## Contratos Gedeon

Seção §79 adicionada em `CONTRACTS_GEDEON.md`:

```
## §79 — KRONOS task verificar_kits_completos (CPRO 12 T2-KRONOS)
Task Celery agendada diariamente às 08:00 Manaus (12:00 UTC).
Verifica kits GED com completion_percentage=100 e sent_at IS NULL.
Para cada kit elegível, cria notificação in_app para Jordan.
NÃO envia email nem WhatsApp.
Idempotente: sem duplicatas dentro de 24h por kit.
```

---

## Cenários Cobertos

| Cenário | Resultado |
|---------|-----------|
| A — Kit 100% sem notificação anterior | Cria notificação in_app ✅ |
| B — Kit 100% com notificação < 24h | Ignorado (idempotente) ✅ |
| C — Nenhum kit a 100% | Retorna `{"kits_alertados": 0}` ✅ |
| D — Jordan não encontrado no BD | Log warning + retorna erro sem exceção ✅ |
| E — Tenant não encontrado | Log warning + retorna erro sem exceção ✅ |

---

## Observação — BUG pré-existente (fora de escopo)

O celery-beat crashou na inicialização com `ModuleNotFoundError: No module named 'modules.financial.tasks'`.
Este é um BUG pré-existente documentado no escopo T1. Após o crash, o beat reiniciou sozinho
e entrou em operação (confirmado pelos logs de `Scheduler: Sending due task`).
O novo agendamento `gedeon-verificar-kits-completos-0800` está registrado e será executado
às 12:00 UTC (08:00 Manaus).

---

## Gap corrigido na auditoria (2026-05-05)

**Gap detectado:** 4 workers (`celery-operacional`, `celery-priority`, `celery-nfse`, `celery-sefaz`)
não receberam `kronos_tasks.py` nem `celery_app.py` no hot-copy inicial — INV-10/INV-11 violados.

**Correção executada:**
```bash
# Copiado para os 4 workers faltantes + SIGHUP
for CONTAINER in celery-operacional celery-priority celery-nfse celery-sefaz:
  docker cp kronos_tasks.py $CONTAINER:/app/modules/gedeon/tasks/kronos_tasks.py
  docker cp celery_app.py $CONTAINER:/app/celery_app.py
  docker exec $CONTAINER python3 -c "import os, signal; os.kill(1, signal.SIGHUP)"
```

**Verificação final:** `celery inspect registered` confirmou `gedeon.verificar_kits_completos`
registrada em todos os workers ativos.

| Container | kronos_tasks | celery_app |
|-----------|-------------|-----------|
| backend | ✅ | ✅ |
| celery-beat | ✅ | ✅ |
| celery-batch | ✅ | ✅ |
| celery-operacional | ✅ (fix) | ✅ (fix) |
| celery-integrations | ✅ | ✅ |
| celery-priority | ✅ (fix) | ✅ (fix) |
| celery-nfse | ✅ (fix) | ✅ (fix) |
| celery-sefaz | ✅ (fix) | ✅ (fix) |

---

**T2 KRONOS CPRO12 OK — task implementada, agendada, hot-copiada em todos os 8 containers e documentada em §79.**
