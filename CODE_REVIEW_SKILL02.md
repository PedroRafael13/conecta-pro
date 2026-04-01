# CODE REVIEW SKILL 02 — CONECTA PRO
> **Gerado em:** 31/03/2026
> **Metodologia:** Skill 02 (code-review-conecta-pro) — checklist 15 pontos — 5 subagentes paralelos
> **Contexto:** Complementa Skill 01 (AUDITORIA_SKILL01.md) — foca em segurança, performance, código
> **Fixes já aplicados nesta sessão:** get_db_sync corrigido · croniter instalado · requirements.txt atualizado

---

## SCORECARD CODE REVIEW

```
╔══════════════════════════════════════════════════════════════════════╗
║              CONECTA PRO — CODE REVIEW SKILL 02                     ║
║              31/03/2026 — Checklist 15 pontos por módulo            ║
╠══════════════════════╦════════════╦════════════╦════════════════════╣
║ Módulo               ║ Checklist  ║  Score     ║  Fechar 10/10?     ║
╠══════════════════════╬════════════╬════════════╬════════════════════╣
║ GED                  ║   13/15    ║  8.7/10    ║ ❌ Precisa correção ║
║ Financeiro           ║    9/15    ║  6.0/10    ║ ❌ Precisa correção ║
║ Departamento Pessoal ║    9/15    ║  6.0/10    ║ ❌ Precisa correção ║
║ Operacional          ║    8/15    ║  5.3/10    ║ ❌ Precisa correção ║
║ AI + Gov + Auth      ║   11/15    ║  7.3/10    ║ ❌ Precisa correção ║
╠══════════════════════╩════════════╩════════════╩════════════════════╣
║  Média geral: 50/75 (66.7%)  →  Score médio: 6.7/10                ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## FIXES APLICADOS AUTOMATICAMENTE (pelo próprio agente)

> Correções simples executadas direto — não precisam do T2.

| # | Fix | Arquivo | Status |
|---|-----|---------|--------|
| 1 | `get_db_sync` → `get_db` + `AsyncSession` + `await` em `gaps_funcionarios` | `esocial_controller.py:495` | ✅ Aplicado |
| 2 | `croniter>=6.0.0` adicionado ao `requirements.txt` | `backend/requirements.txt` | ✅ Aplicado |
| 3 | `croniter` instalado no container | `conecta-pro-backend` (pip) | ✅ Aplicado |
| 4 | Backend rebuildado e testado após fixes 1-3 | Docker | ✅ Validado |

---

## BUGS NOVOS DESCOBERTOS (não estavam na Skill 01)

> Ordenados por severidade.

### 🔴 CRÍTICO-1 — `ponto/dashboard` exposto SEM autenticação
**Módulo:** Departamento Pessoal
**Endpoint:** `GET /api/v1/people-management/ponto/dashboard` (e outros 8 handlers síncronos)
**Impacto:** Dados operacionais sensíveis (total de ausentes, banco de horas, inconsistências) acessíveis sem token.
**Causa:** `punch_controller.py` e `folha_controller.py` têm 10 route handlers como `def` (síncronos) sem `Depends(get_current_user)`. São: `ponto_dashboard`, `relatorio_inconsistencias`, `banco_horas`, `sincronizar_solides`, `sync_escalas`, `ajuste_ponto`, `colaboradores_sem_escala`, `folha_dashboard`, `calcular_holerite`, `calcular_batch`.
**Fix:**
```python
# Adicionar em cada handler:
from core.auth import get_current_user
async def ponto_dashboard(
    current_user = Depends(get_current_user),  # ← ADICIONAR
    db: AsyncSession = Depends(get_db),         # ← mudar para AsyncSession
```

---

### 🔴 CRÍTICO-2 — `esocial/eventos` público sem autenticação
**Módulo:** Government
**Endpoint:** `GET /api/v1/government/esocial/eventos`
**Impacto:** Lista eventos eSocial fiscais reais sem qualquer token. Dados tributários expostos publicamente.
**Fix:**
```python
# esocial_controller.py — listar_eventos
async def listar_eventos(
    current_user: User = Depends(get_current_user),  # ← ADICIONAR
    ...
```

---

### 🔴 CRÍTICO-3 — `grace_days` coluna inexistente no banco
**Módulo:** Financeiro
**Endpoint:** `GET /api/v1/financial/receivables/installments/pending`
**Causa:** `UndefinedColumnError: column receivable_installments.grace_days does not exist`. Model SQLAlchemy tem a coluna, banco não tem.
**Fix:** Migration Alembic para adicionar a coluna ou remover do model.

---

### 🔴 CRÍTICO-4 — UUID malformado derruba conexão asyncpg (GED + Operacional + DP)
**Módulos:** GED, Operacional, Departamento Pessoal
**Causa:** `document_id`, `post_id`, `employee_id` tipados como `str` nos path params. String não-UUID vai direto ao PostgreSQL → `asyncpg.DataError: invalid input syntax for type uuid` → conexão morta → 500.
**Fix universal (1 linha por controller afetado):**
```python
# Trocar: async def get_doc(document_id: str, ...)
# Por:    async def get_doc(document_id: UUID, ...)
# FastAPI valida automaticamente → 422 antes de chegar no banco
from uuid import UUID
```
**Arquivos afetados:** `document_controller.py`, `folder_controller.py`, `post_controller.py`, `scale_controller.py`, `employee_service.py`

---

### 🟡 MÉDIO-1 — `scales.total_hours` e `estimated_cost` sempre 0
**Módulo:** Operacional
**Causa:** `Scale.shifts` tem `lazy="noload"` no model (linha 172). `scale_repository.py` linhas 444-447 calcula `total_hours = sum(s.planned_hours for s in scale.shifts)` mas `scale.shifts` é sempre lista vazia.
**Fix:**
```python
# scale_repository.py — método get_by_id — carregar shifts:
from sqlalchemy.orm import selectinload
stmt = select(Scale).where(Scale.id == scale_id).options(selectinload(Scale.shifts))
```

---

### 🟡 MÉDIO-2 — `expires_at` silenciado ao criar comunicado → `data_expiracao` sempre NULL
**Módulo:** Operacional
**Causa:** Coluna real no banco é `data_expiracao`. O model tem `@property expires_at` que lê `self.data_expiracao`. O repositório ao criar passa `expires_at=data.expires_at` (kwarg ignorado pelo SQLAlchemy) em vez de `data_expiracao=data.expires_at`.
**Fix (1 linha):**
```python
# communication_repository.py linha 100
data_expiracao=data.expires_at,   # era: expires_at=data.expires_at
```

---

### 🟡 MÉDIO-3 — `condominio_id` obrigatório sem default nos endpoints financeiros
**Módulo:** Financeiro
**Causa:** Todos os endpoints de listagem financeira retornam 422 sem `condominio_id`, sem hint claro. O parâmetro deveria ser inferido do token JWT ou ter default `None`.
**Fix:** Adicionar `condominio_id: Optional[UUID] = None` com fallback para `current_user.condominio_id`.

---

### 🟡 MÉDIO-4 — N+1 em `bulk_payment` financeiro
**Módulo:** Financeiro
**Causa:** `bulk_payment` (L275-290) executa `get_by_id()` + `register_payment()` por item em loop → N+1 confirmado.
**Fix:** `SELECT ... WHERE id = ANY(:ids)` antes do loop para buscar todos os installments de uma vez.

---

### 🟡 MÉDIO-5 — Route conflict: `/installments/pending` capturada por `/{account_id}/installments`
**Módulo:** Financeiro
**Causa:** Rota estática `/installments/pending` declarada após `/{account_id}/installments` no router.
**Fix:** Mover `/installments/pending` para **antes** de `/{account_id}/installments`.

---

### 🟡 MÉDIO-6 — `time-bank/report` capturado por `/{entry_id}`
**Módulo:** Operacional
**Causa:** Mesmo padrão do bug de medidas-administrativas/templates — rota estática `/report` declarada após `/{entry_id}`.
**Fix:** Mover `/report` para antes de `/{entry_id}` no router do time-bank.

---

### 🟡 MÉDIO-7 — `scales.name` sempre string vazia (frontend exibe null)
**Módulo:** Operacional
**Causa:** 3 escalas no banco têm `name = ''` (string vazia). O schema serializa como `null`. Dados não foram populados corretamente ao criar.
**Ação:** Atualizar os 3 registros via SQL: `UPDATE scales SET name = 'Escala ' || LEFT(id::text, 8) WHERE name = '';`

---

### 🟡 MÉDIO-8 — AUTH_LIMIT (5/min) hard-coded, não configurável via env
**Módulo:** Auth
**Causa:** `core/rate_limit.py` linha 143: `AUTH_LIMIT = "5/minute"` (hardcoded). Não respeita `RATE_LIMIT_REQUESTS` do `.env`.
**Fix:**
```python
# core/rate_limit.py
auth_rate_limit: str = Field(default="5/minute")
AUTH_LIMIT = settings.auth_rate_limit
# .env:
AUTH_RATE_LIMIT=20/minute
```

---

### 🟢 BAIXO-1 — `is_active` vs `status` divergentes em 11 funcionários
**Módulo:** Departamento Pessoal
**Diagnóstico:** 11 funcionários têm `is_active=true` mas `status='inativo'` — demitidos não tiveram `is_active` atualizado.
**Recomendação:** Executar com migration rastreável:
```sql
UPDATE employees SET is_active = false WHERE status = 'inativo' AND is_active = true;
-- Afeta 11 registros. Risco: BAIXO.
```

---

### 🟢 BAIXO-2 — `Session` vs `AsyncSession` em 2 factory functions de Government
**Módulo:** Government
**Arquivos:** `sync_controller.py:170`, `meeting_assistant_controller.py:51`
**Causa:** Declaram `db: Session = Depends(get_db)` onde `get_db` retorna `AsyncSession`.
**Fix:** `Session` → `AsyncSession` nas duas factory functions.

---

### 🟢 BAIXO-3 — F-strings SQL com padrão perigoso (risco futuro)
**Módulo:** Departamento Pessoal
**Arquivos:** `auto_assemble_controller.py:76`, `time_record_service.py:581`
**Status:** Atualmente seguro (valores via bind parameters). Padrão deve ser refatorado para ORM.

---

### 🟢 BAIXO-4 — `receivables` retorna lista sem wrapper `{total, items}` (sem paginação)
**Módulo:** Financeiro
**Causa:** Endpoint de listagem retorna array bruto, sem `total` para paginação no frontend.
**Fix:** Wrapper: `{"items": [...], "total": N, "skip": 0, "limit": 50}`.

---

## DETALHAMENTO POR MÓDULO

---

### 📁 GED — 13/15 → 8.7/10 | ❌ PRECISA CORREÇÃO

| Ponto | Status | Observação |
|-------|--------|------------|
| 1 — Endpoints GET 200 | ✅ | 7/7 endpoints OK |
| 2 — UUID inválido → 404 | ❌ | Derruba asyncpg → 500 |
| 3 — Lista vazia → [] | ✅ | |
| 4 — Sem token → 401 | ✅ | Retorna 403 (aceitável) |
| 5 — Token inválido → 401 | ✅ | |
| 6 — SQL injection | ✅ | F-strings são seguras |
| 7 — Queries < 200ms | ✅ | 0.13ms / 0.18ms |
| 8 — Paginação | ✅ | `items/total/page/pages` |
| 9 — Sem N+1 | ✅ | |
| 10 — 404 português | ✅ | "Documento não encontrado" |
| 11 — 500 sem trace | ✅ | |
| 12 — Namespace antigo | ✅ | 0 ocorrências de people-management/ged |
| 13 — expire_overdue existe | ✅ | Método existe no repositório |
| 14 — GED AI ZeroDivision | ❌ | `total or 1` fix (1 linha) |
| 15 — redirect_slashes | ✅ | `False` é intencional no projeto |

**Fixes necessários (2):**
1. `document_controller.py` + `folder_controller.py`: `document_id: str` → `document_id: UUID`
2. `document_ai_service.py:482`: `stats.get("total_documents", 1)` → `stats.get("total_documents") or 1`

---

### 💰 Financeiro — 9/15 → 6.0/10 | ❌ PRECISA CORREÇÃO

| Ponto | Status | Observação |
|-------|--------|------------|
| 1 — Core endpoints | ❌ | 422 sem condominio_id |
| 2 — UUID inválido → 404 | ✅ | 404 correto |
| 3 — Lista vazia → [] | ✅ | |
| 4 — Sem token → 401 | ❌ | Retorna 403 (HTTPBearer default) |
| 5 — Token inválido → 401 | ✅ | |
| 6 — SQL injection | ✅ | Bind params corretos |
| 7 — Queries < 200ms | ✅ | 0.12ms / 0.34ms |
| 8 — Paginação | ❌ | Lista bruta sem wrapper |
| 9 — N+1 queries | ❌ | bulk_payment N+1 confirmado |
| 10 — 404 português | ✅ | "Conta nao encontrada" |
| 11 — 500 sem trace | ✅ | Erro contido nos logs |
| 12 — Frontend dados reais | ✅ | R$ 258k a receber OK |
| 13 — list_with_filters | ❌ | Método ausente → 500 prod |
| 14 — Route conflicts | ❌ | grace_days + pending conflict |
| 15 — AI endpoints OK | ✅ | 4/4 AI endpoints 200 |

**Fixes necessários (6):**
1. `condominio_id` opcional com fallback JWT
2. `list_with_filters` em `BankTransactionRepository`
3. Migration para `grace_days` em `receivable_installments`
4. Mover `/installments/pending` antes de `/{account_id}/installments`
5. `bulk_payment`: buscar todos os installments antes do loop
6. Wrapper de paginação em `/receivables` e `/payables`

---

### 👥 Departamento Pessoal — 9/15 → 6.0/10 | ❌ PRECISA CORREÇÃO

| Ponto | Status | Observação |
|-------|--------|------------|
| 1 — Funcionalidade | ✅ | 7/7 endpoints OK |
| 2 — UUID inválido → 404 | ❌ | /profile derruba asyncpg → 500 |
| 3 — Lista vazia → [] | ✅ | |
| 4 — Sem token → 401 | ❌ | **ponto/dashboard sem auth!** |
| 5 — Token inválido → 401 | ✅ | |
| 6 — SQL injection | ❌ | F-string SQL antipattern (2 arquivos) |
| 7 — Queries < 200ms | ✅ | 0.19ms / 0.17ms |
| 8 — Paginação | ✅ | items/total/page completo |
| 9 — N+1 queries | ✅ | selectinload correto |
| 10 — 404 português | ✅ | "Funcionário não encontrado" |
| 11 — 500 sem trace | ✅ | |
| 12 — is_active vs status | ⚠️ | 11 registros divergentes |
| 13 — UUID benefits | ✅ | Bug já corrigido |
| 14 — Migration sprint79 | ✅ | **Já executada — não precisa stamp** |
| 15 — Async/await | ❌ | 10 handlers síncronos sem auth |

**Fixes necessários (4, sendo 1 crítico):**
1. **URGENTE:** Adicionar `Depends(get_current_user)` nos 10 handlers síncronos
2. `employee_id: str` → `employee_id: UUID` no path param
3. Refatorar f-strings SQL para ORM em `auto_assemble_controller.py` e `time_record_service.py`
4. `UPDATE employees SET is_active = false WHERE status = 'inativo' AND is_active = true;`

---

### ⚙️ Operacional — 8/15 → 5.3/10 | ❌ PRECISA CORREÇÃO

| Ponto | Status | Observação |
|-------|--------|------------|
| 1 — Funcionalidade | ✅ | 8/8 endpoints OK |
| 2 — UUID inválido → 404 | ❌ | asyncpg DataError → 500 |
| 3 — Lista vazia → [] | ✅ | items: [] correto |
| 4 — Sem token → 401 | ⚠️ | Retorna 403 (padrão HTTPBearer) |
| 5 — Token inválido → 401 | ✅ | |
| 6 — SQL injection | ✅ | Sem f-strings SQL |
| 7 — Queries < 200ms | ✅ | 0.42ms / 0.20ms |
| 8 — Paginação | ✅ | items/total/page/pages |
| 9 — N+1 | ⚠️ | `scale.shifts` lazy=noload → totais sempre 0 |
| 10 — 404 português | ✅ | "Posto não encontrado" |
| 11 — 500 sem trace | ✅ | |
| 12 — @property expires_at | ❌ | data_expiracao sempre NULL |
| 13 — /templates antes de /{id} | ❌ | 500 confirmado |
| 14 — get_stats ausente | ❌ | AttributeError em produção |
| 15 — SQL type mismatch | ❌ | uuid = text → error |

**Fixes necessários (5):**
1. Path params: `str` → `UUID` em post/scale/shift controllers
2. `communication_repository.py:100`: `expires_at=` → `data_expiracao=`
3. `disciplinary_controller.py`: mover `/templates` e `/templates/{id}` para antes de `/{action_id}`; mover `/report` antes de `/{entry_id}` no time-bank
4. `TimeBankRepository`: implementar `get_stats()` com `func.count/sum`
5. `kpi_trends_controller.py`: remover `::text` — `WHERE t.employee_id = e.id` (ambos UUID)

---

### 🤖 AI + Gov + Auth — 11/15 → 7.3/10 | ❌ PRECISA CORREÇÃO

| Ponto | Status | Observação |
|-------|--------|------------|
| 1 — Funcionalidade | ✅ | 8/8 endpoints OK |
| 2 — UUID inválido → 404 | ✅ | 404 correto |
| 3 — Lista vazia → [] | ✅ | |
| 4 — Sem token → 401 | ❌ | **esocial/eventos público!** |
| 5 — Token inválido → 401 | ❌ | bartolo/health público |
| 6 — SQL injection | ✅ | XML namespaces, não SQL |
| 7 — Performance | ✅ | greeting 28ms, send 4.0s |
| 8 — Paginação | ✅ | |
| 9 — N+1 Bartolo | ✅ | Uma query por entity type |
| 10 — Error handling | ✅ | 422 Pydantic claro |
| 11 — 500 sem trace | ✅ | Fix aplicado nesta sessão |
| 12 — Rate limit configurável | ❌ | Hard-coded `"5/minute"` |
| 13 — get_db_sync fix | ✅ | **Aplicado nesta sessão** |
| 14 — croniter | ✅ | **Instalado + requirements.txt** |
| 15 — Async/await gov | ❌ | Session vs AsyncSession (2 arquivos) |

**Fixes necessários (4, sendo 2 críticos):**
1. **URGENTE:** `Depends(get_current_user)` em `esocial_controller.listar_eventos`
2. **URGENTE:** `Depends(get_current_user)` em `bartolo_controller.health_check`
3. `core/rate_limit.py:143`: externalizar `AUTH_LIMIT` para env var `AUTH_RATE_LIMIT=20/minute`
4. `sync_controller.py:170` + `meeting_assistant_controller.py:51`: `Session` → `AsyncSession`

---

## PLANO DE AÇÃO PRIORIZADO

### 🚨 URGENTE — Falhas de segurança (executar hoje)

```
1. ponto/dashboard + 9 handlers: adicionar Depends(get_current_user)
   → Arquivos: punch_controller.py, folha_controller.py

2. esocial/eventos: adicionar Depends(get_current_user)
   → Arquivo: esocial_controller.py

3. bartolo/health: adicionar Depends(get_current_user)
   → Arquivo: bartolo_controller.py
```

### 🔴 CRÍTICO — Corrigir 500s em produção

```
4. UUID path params: str → UUID em 5+ controllers
   → GED, Operacional, DP: document/folder/post/scale/employee

5. grace_days migration Alembic
   → receivable_installments + migration nova

6. ponto_dashboard e folha handlers: migrar para async def + AsyncSession

7. expires_at → data_expiracao no communication_repository.py:100

8. Rotas estáticas antes de /{id}: templates, report, installments/pending
```

### 🟡 MÉDIO — Qualidade de código

```
9.  BankTransactionRepository.list_with_filters implementar
10. TimeBankRepository.get_stats implementar
11. kpi_trends: remover ::text nos joins UUID
12. scale.shifts: selectinload para total_hours correto
13. GED AI ZeroDivision: or 1 fix
14. Bulk payment: ANY(:ids) antes do loop
```

### 🟢 BAIXO — Dívida técnica

```
15. UPDATE employees: sincronizar is_active com status (11 registros)
16. AUTH_LIMIT: externalizar para AUTH_RATE_LIMIT env var
17. F-strings SQL: refatorar para ORM (auto_assemble + time_record)
18. Session → AsyncSession em sync_controller e meeting_assistant
19. scales.name: popular 3 registros com nome real
20. receivables: adicionar wrapper paginação
```

---

## COMPARATIVO SKILL 01 vs SKILL 02

| Aspecto | Skill 01 (Funcionalidade) | Skill 02 (Qualidade) | Delta |
|---------|--------------------------|----------------------|-------|
| GED | 6.0/10 | 8.7/10 | +2.7 |
| Financeiro | 4.5/10 | 6.0/10 | +1.5 |
| DP/RH | 6.5/10 | 6.0/10 | -0.5 |
| Operacional | 7.0/10 | 5.3/10 | -1.7 |
| AI+Gov+Auth | 8.2/10 | 7.3/10 | -0.9 |

> **Insight:** GED e Financeiro melhoram na perspectiva de qualidade (mais simples do que pareciam). Operacional e DP pioram (a qualidade do código é inferior à funcionalidade visível — há débitos técnicos escondidos).

---

## ESTADO DOS MÓDULOS APÓS ESTA SESSÃO

```
✅ Já corrigidos (esta sessão):
   - esocial_controller: get_db_sync → get_db AsyncSession
   - requirements.txt: croniter>=6.0.0 adicionado
   - Container: croniter instalado

⏳ Pendentes (precisam do desenvolvedor):
   - 3 falhas de segurança (endpoints sem auth)
   - UUID path params em 5+ controllers
   - grace_days migration
   - 8 rotas estáticas na ordem errada
   - 3 métodos de repositório ausentes
   - 10 handlers síncronos sem auth
```

---

*Code Review executado via Skill 02 com 5 subagentes paralelos.*
*Arquivo salvo em: /opt/conecta-pro/CODE_REVIEW_SKILL02.md*
