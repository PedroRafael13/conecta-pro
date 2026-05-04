# RELATÓRIO T2 — INVESTIGAÇÃO GAP NOTIFICAÇÕES 09/03/2026
**Data:** 2026-05-04
**Sessão:** tmux-t2 | **Módulo:** operacional/communication (read-only)
**Branch:** feature/people-management-reorganization

---

## 1. Confirmação do Gap

```sql
SELECT MIN(created_at), MAX(created_at), COUNT(*)
FROM communication_notifications;
→ primeiro: 2026-03-02 07:37:57 | último: 2026-03-09 07:07:57 | total: 12
```

**56 dias sem nenhuma notificação.** Confirmado.

---

## 2. Resposta às 4 Perguntas do Prompt

### 1. Houve commit em ~09/03 que mudou pipeline notif?

**SIM.** Em 07-12/03/2026 houve mega-reorganização do backend:

```
2b6ffd85  feat: add People Management module (DP + RH + Operations + Portal)
406b5a09  Reorganização backend 35→9 módulos + renomeação guardian→external
c69d8bd8  fix: corrige build TypeScript e E2E operacional
57ec3869  chore: remove OpenClaw + resolve backlog
```

O commit `406b5a09` reorganizou 35 módulos em 9 — nessa época os caminhos de import
e a lógica de `_get_active_tenants()` foram alterados.

---

### 2. Tasks Celery que disparam notif estão rodando?

**NÃO FUNCIONALMENTE.** A task `operacional.check_late_employees` é enviada pelo beat
a cada 5 minutos, mas **falha com `DataError` no worker desde 2026-03-20**:

```
DataError: invalid input value for enum tenant_status: "ATIVO"
LINE 3: WHERE tenants.status = 'ATIVO' AND tenants.ativo IS true
```

**Causa:** `_get_active_tenants()` usa `TenantStatus.ATIVO` que resolve para `"ativo"`
(PT-BR), mas o enum `tenant_status` no banco tem valores em inglês:

```sql
SELECT enum_range(NULL::tenant_status);
→ {active, inactive, suspended, blocked, trial, cancelled}
```

O código usa `"ativo"`, o banco espera `"active"` → mismatch → DataError → retry × 3 → falha definitiva.

**Evidência worker:**
```
[2026-03-20 17:49:03] ERROR: [Operacional Task] Erro ao verificar atrasos:
  DataError: invalid input value for enum tenant_status: "ATIVO"
  (todas as tentativas desde 2026-03-20 falham identicamente)
```

**Celery-beat status atual:** `Up 23 seconds (health: starting)` — reiniciando em loop com:
```
TypeError: PunchService.__init__() missing 1 required positional argument: 'db'
  File "/app/modules/people_management/ponto/controllers/punch_controller.py", line 34
```
O beat importa toda a app para carregar as tasks. O `punch_controller.py` instancia
`PunchService()` em nível de módulo (sem `db`), o que causa crash no import.

---

### 3. Eventos-fonte (rondas/ocorrências) ainda estão sendo criados?

| Tabela | Total | Último |
|--------|-------|--------|
| `occurrences` | 0 | — |
| `inspection_rounds` | 3 | 2026-03-29 |
| `solides_occurrences` | 0 | — |
| `shifts` | 180 | último shift: 2026-04-30 |
| `tenants` | **0** | — |

**`tenants` = 0 linhas** — mesmo se o DataError fosse corrigido, `_get_active_tenants()`
retornaria lista vazia → nenhum tenant para iterar → zero notificações geradas.

---

### 4. Hipótese da causa: deploy quebrou? Cron mudou? Worker morto?

**Causa real: os 12 registros existentes são SEED DATA, nunca foram notificações reais.**

Padrão de seed:
- Todos com segundos `:57` ou `:57` exatos (03:37:57, 05:37:57, 07:07:57...)
- Distribuídos em datas redondas (02/03, 04/03, 06/03, 07/03, 08/03, 09/03)
- Títulos genéricos de demonstração: "Comunicado publicado — Carnaval", "Posto Gelain sem cobertura"
- Foram inseridos durante setup inicial do banco (~sprint de março/2026)

**A pipeline de notificações NUNCA funcionou em produção** por 3 razões cumulativas:

| # | Problema | Impacto |
|---|---------|---------|
| 1 | `tenants` table vazia | `_get_active_tenants()` retorna `[]` → zero iterações |
| 2 | Enum mismatch: código usa `"ativo"`, banco tem `"active"` | `DataError` em toda execução |
| 3 | Celery-beat crashando: `PunchService()` sem `db` em nível de módulo | Beat não sobe → tasks não agendadas |

---

## 3. Bugs Identificados (Mapa para Fix)

### BUG-1 — `TenantStatus` mismatch (BLOQUEANTE)
**Arquivo:** `backend/modules/operacional/services/notification_triggers.py:39`
**Problema:** `TenantStatus.ATIVO` = `"ativo"` vs DB enum `"active"`
**Fix:** `Tenant.status == 'active'` ou alinhar enum PT-BR com DB inglês

### BUG-2 — `PunchService()` sem db em nível de módulo (BLOQUEANTE para beat)
**Arquivo:** `backend/modules/people_management/ponto/controllers/punch_controller.py:34`
**Problema:** `_service = PunchService()` instanciado sem `db` fora de endpoint
**Evidência:**
```
TypeError: PunchService.__init__() missing 1 required positional argument: 'db'
```
**Fix:** remover instanciação global; instanciar dentro de cada endpoint com `db`

### BUG-3 — `tenants` table vazia (PRÉ-REQUISITO para notificações funcionarem)
**Problema:** Sistema usa multi-tenancy mas nenhum tenant está cadastrado
**Fix:** criar tenant de produção (Conecta Mais CNPJ 35.710.481/0001-03) com `status='active'`

### BUG-4 — Celery-batch: módulo faltando
```
ModuleNotFoundError: No module named 'modules.health_occupational.tasks'
```
**Fix:** criar stub de tasks para health_occupational ou remover do celery_app.py

---

## 4. Status dos Workers

| Container | Status | Observação |
|-----------|--------|-----------|
| celery-beat | ⚠️ `health: starting` (loop) | Crasha por BUG-2 |
| celery-operacional | ✅ Up 2 weeks | Recebe tasks mas falha por BUG-1 |
| celery-batch | ⚠️ `health: starting` | Crasha por BUG-4 |
| celery-integrations | ✅ Up 2 weeks healthy | OK |
| celery-priority | ✅ Up 2 weeks healthy | OK |

---

## 5. Conclusão

O gap de 56 dias em `communication_notifications` não é uma **regressão** — é
a ausência de dados reais desde sempre. Os 12 registros existentes são seed de demonstração
inseridos no setup inicial (02-09/03/2026).

Para as notificações começarem a funcionar são necessários 3 fixes sequenciais:
1. Corrigir `PunchService()` (BUG-2) → beat sobe
2. Corrigir `TenantStatus.ATIVO` → `"active"` (BUG-1) → tasks executam
3. Criar registro em `tenants` com `status='active'` (BUG-3) → dados existem
