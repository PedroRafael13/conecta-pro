# AUDITORIA SKILL 01 — DEBUGGER SISTEMÁTICO CONECTA PRO
> **Gerada em:** 31/03/2026
> **Metodologia:** Skill 01 (debugger-sistematico-conecta-pro) — 5 subagentes paralelos
> **Cobertura:** GED · Financeiro · Departamento Pessoal · Operacional · AI + Gov + Auth
> **Backend:** http://127.0.0.1:8080 · Container: conecta-pro-backend

---

## SCORECARD EXECUTIVO

```
╔══════════════════════════════════════════════════════════════════════╗
║              CONECTA PRO — SCORECARD COMPLETO                       ║
║              Auditoria: 31/03/2026 — Skill 01 Paralela              ║
╠══════════════════════╦════════════╦════════════╦════════════════════╣
║ Módulo               ║ Endpoints  ║  Passando  ║  Score             ║
╠══════════════════════╬════════════╬════════════╬════════════════════╣
║ GED                  ║   120/133  ║   92/120   ║   6.0 / 10         ║
║ Financeiro + BI      ║    40/472  ║   22/40    ║   4.5 / 10 ⚠️       ║
║ Departamento Pessoal ║    61/213  ║   51/61    ║   6.5 / 10         ║
║ Operacional          ║    91/243  ║   63/91    ║   7.0 / 10         ║
║ AI + Gov + Auth      ║    64/~80  ║   56/64    ║   8.2 / 10 ✅       ║
╠══════════════════════╬════════════╬════════════╬════════════════════╣
║ TOTAL                ║   376/~1141║  284/376   ║   6.4 / 10         ║
╠══════════════════════╩════════════╩════════════╩════════════════════╣
║                                                                      ║
║  Taxa de sucesso geral: 75.5% (284/376 endpoints testados)          ║
║  Bugs 500 confirmados: 31 endpoints                                  ║
║  Score médio ponderado: 6.4/10                                       ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## BUGS CRÍTICOS ENCONTRADOS (por prioridade de correção)

### 🔴 PRIORIDADE 1 — Financeiro: BI Dashboard 0% funcional
**Módulo:** `/api/v1/financial/bi/*`
**Impacto:** 11/11 endpoints retornam 500 — módulo completamente inoperante
**Causa:** `bi_controller.py` declara `db: Session = Depends(get_db)` (sync), mas `get_db` retorna `AsyncSession`. Incompatibilidade total.
**Arquivo:** `/opt/conecta-pro/backend/modules/financial/bi_dashboard/controllers/bi_controller.py`
**Fix:** Trocar `Session` por `AsyncSession` em todos os métodos do controller.

---

### 🔴 PRIORIDADE 2 — Financeiro: `User` não é subscriptable (Contabilidade)
**Módulo:** `/api/v1/financial/accounting/*`
**Impacto:** 4 endpoints (cost-centers, journal-entries, periods, trial-balances) retornam 500
**Causa:** `accounting_controller.py` usa `current_user["condominio_id"]` (dict-style), mas `get_current_user` retorna objeto `User` SQLAlchemy. Correto: `current_user.condominio_id`.
**Arquivo:** `/opt/conecta-pro/backend/modules/financial/controllers/accounting_controller.py` (72 ocorrências)
**Fix:** Substituir `current_user["key"]` → `current_user.key` em todo o arquivo.

---

### 🔴 PRIORIDADE 3 — GED: `DocumentTagRepository` sem `is_associated`
**Módulo:** `/api/v1/ged/document-tags/*`
**Impacto:** 4 endpoints (DELETE tag, add/set/get tags de documento) retornam 500
**Causa:** `AttributeError: 'DocumentTagRepository' object has no attribute 'is_associated'`
**Fix:** Implementar o método `is_associated(tag_id, document_id)` no repositório de tags.

---

### 🔴 PRIORIDADE 4 — DP/RH: CCT Controller com nomes de colunas SQL errados
**Módulo:** `/api/v1/people-management/hr/cct/*`
**Impacto:** 5 endpoints retornam 500 (resumo, cargos, conformidade, funcionários)
**Causa:** `cct_controller.py` usa raw SQL com colunas que não existem na tabela:

| Usado no SQL     | Coluna Real no Banco            |
|------------------|---------------------------------|
| `nome_cargo`     | `cargo_nome`                    |
| `salario_base`   | `piso_salarial`                 |
| `ativo`          | `is_active`                     |
| `adicional_insalubridade` | `adicional_insalubridade_percentual` |
| `cbo`            | (não existe)                    |

**Arquivo:** `/opt/conecta-pro/backend/modules/people_management/hr/controllers/cct_controller.py`

---

### 🔴 PRIORIDADE 5 — Operacional: Tenant ID mismatch (dados invisíveis)
**Módulo:** `/api/v1/operacional/comunicados` e `/medidas-administrativas`
**Impacto:** 11 medidas disciplinares e 10 comunicados existem no banco, mas a API retorna listas vazias
**Causa:** Dados foram inseridos com `tenant_id = "a1b2c3d4-..."` mas a lógica usa `str(user.id)` como tenant. O usuário admin tem UUID diferente do tenant dos dados.
**Fix:** Unificar o conceito de tenant_id — definir um DEFAULT_TENANT_ID fixo no settings ou usar o `condominio_id` do usuário.

---

### 🔴 PRIORIDADE 6 — Operacional: `@property expires_at` usada como coluna SQLAlchemy
**Módulo:** `/api/v1/operacional/comunicados/nao-lidos`
**Causa:** `Announcement.expires_at` é um `@property` Python (não coluna SQLAlchemy), sendo usado em `.is_(None)`. Erro: `AttributeError: 'property' object has no attribute 'is_'`
**Arquivo:** `/opt/conecta-pro/backend/modules/operacional/communication/repositories/communication_repository.py` linha 372

---

### 🟡 PRIORIDADE 7 — Government: `ImportError: cannot import name 'get_db_sync'`
**Módulo:** `/api/v1/government/esocial/gaps-funcionarios`
**Causa:** `esocial_controller.py:495` importa `get_db_sync` que não existe mais
**Fix:** Substituir por `get_db` assíncrono.

---

### 🟡 PRIORIDADE 8 — Government: `No module named 'croniter'`
**Módulo:** `/api/v1/government/jobs/status`
**Causa:** Dependência `croniter` não instalada no container
**Fix:** Adicionar `croniter` ao `requirements.txt` e rebuildar.

---

### 🟡 PRIORIDADE 9 — GED: AI endpoints completamente quebrados (5/5)
**Módulo:** `/api/v1/ged/documents/ai/*`
**Impacto:** dashboard, insights, extract-keywords, check-duplicates, analyze-ocr retornam 500
**Causa provável:** Dependência LLM/OpenAI não configurada ou método não implementado no service AI.

---

### 🟡 PRIORIDADE 10 — Operacional: Rota conflito em `/medidas-administrativas/templates`
**Causa:** FastAPI captura "templates" como `{action_id}` UUID → `ValueError: invalid UUID 'templates'`
**Fix:** Declarar a rota `/templates` ANTES de `/{action_id}` no router.

---

### 🟡 PRIORIDADE 11 — Operacional: `TimeBankRepository` sem método `get_stats`
**Módulo:** `GET /api/v1/operacional/time-bank/stats`
**Causa:** Controller chama `repo.get_stats()` mas método não existe na classe.

---

### 🟡 PRIORIDADE 12 — Financeiro: `BankTransactionRepository` sem `list_with_filters`
**Módulo:** `GET /api/v1/financial/bank-transactions`
**Causa:** Controller chama `repo.list_with_filters(filters, ...)` mas método não existe.

---

### 🟢 PRIORIDADE 13 — GED: Trailing Slash 404 em 4 rotas principais
**Módulo:** `/api/v1/ged/folders/`, `/documents/`, `/document-tags/`, `/document-shares/`
**Causa:** FastAPI registrou rotas sem trailing slash, mas clientes chamam com `/`.
**Fix:** Adicionar `redirect_slashes=True` no `APIRouter` ou registrar ambas as variantes.

---

### 🟢 PRIORIDADE 14 — Migration `sprint79` não rastreada pelo Alembic
**Causa:** `alembic current` reporta "Can't locate revision" para `sprint79_justification_employee_uuid.py`.
**Status:** Banco já tem a coluna correta (`character varying`), mas o Alembic perdeu o tracking.
**Fix:** Executar `alembic stamp sprint79_justification_employee_uuid` para sincronizar.

---

## ANÁLISE POR MÓDULO

### 📁 GED — Score 6/10

**Pontos positivos:**
- CRUD core de documentos, pastas e assinaturas funcionam (77% de sucesso)
- Workflow de assinaturas digitais completo (sign, verify, notify, remind, cancel)
- Sistema de permissões de pastas operacional
- Auth JWT protegendo todos os endpoints corretamente

**Problemas:**
- 4 bugs de trailing slash 404 nas rotas de listagem principal
- `DocumentTagRepository.is_associated` ausente — 4 endpoints quebrados
- `DocumentShareRepository.expire_overdue` ausente — 2 endpoints quebrados
- AI features (5/5) completamente inoperantes
- Document Versions com 3 endpoints retornando 500
- Banco praticamente vazio (1 documento, 0 shares) — dados de teste ausentes

---

### 💰 Financeiro + BI — Score 4.5/10

**Pontos positivos:**
- Núcleo financeiro básico (receber/pagar/fornecedores) funciona
- AI Financeiro 100% funcional: command-center, risks, cashflow-prediction, advisor
- Dados reais no banco: R$ 258.482 a receber, R$ 128.514 a pagar
- Status 'paga' vs 'pago' — é design intencional, não bug

**Problemas:**
- BI Dashboard: 0/11 endpoints (incompatibilidade AsyncSession)
- Contabilidade: 4 endpoints quebrados (User subscriptable bug)
- Bank Transactions: quebrado (método ausente no repo)
- 3 endpoints retornam 404 (fiscal/inventory sem registro)
- Route conflicts em `/upcoming` e `/stats`

---

### 👥 Departamento Pessoal — Score 6.5/10

**Pontos positivos:**
- 52 funcionários todos com CCT vinculada (0 sem vínculo)
- Ponto eletrônico funcionando (batidas, espelho, dashboard, banco-horas)
- SST completo (ASO, CAT, EPI, CIPA, PCMSO, PPRA, LTCAT, NR-1)
- RH avançado (clima, onboarding, avaliação 360, turnover) funcional
- 1.846 batidas de ponto registradas no banco

**Problemas:**
- CCT Controller: 5 endpoints com 500 (nomes de colunas SQL errados)
- Benefits/employee: UUID não serializado como string (1 endpoint)
- Migration sprint79 não rastreada pelo Alembic
- `is_active` e `status` divergem (52 ativos vs 41 com status='ativo')

---

### ⚙️ Operacional — Score 7/10

**Pontos positivos:**
- Base sólida: postos, escalas, turnos, alocações, funcionários, ocorrências, rondas funcionais
- Diaristas com ecossistema completo (CRUD, pagamentos, fiscal, IA)
- Módulo de comunicados e notificações registrado e respondendo
- 9 postos, 180 turnos, 48 alocações, 13 diaristas no banco

**Problemas:**
- Tenant ID mismatch: 11 medidas + 10 comunicados invisíveis via API
- `@property expires_at` usado como coluna SQLAlchemy
- Rota conflito em `/medidas-administrativas/templates`
- `TimeBankRepository` sem `get_stats`
- SQL type mismatch em `kpi-trends/performance-scores`

---

### 🤖 AI + Governo + Auth — Score 8.2/10

**Pontos positivos:**
- Auth JWT: login, logout, /me, refresh, Google OAuth — tudo funcional
- **Bartolo retorna dados REAIS:** 8 postos, 52 funcionários, 3 escalas confirmados
- Greeting personalizado ("Olá, Jordan!")
- Wizards interativos: proposta comercial com 9 passos funcionando
- Government: 25+ endpoints operacionais (SEFAZ-AM respondendo em 379ms, CNPJ real)
- OpenClaw: 88.9% taxa de resolução, 18 intervenções, dados reais
- Briefing executivo com Telegram configurado

**Problemas:**
- `ImportError: get_db_sync` em esocial/gaps-funcionarios
- `No module named 'croniter'` em jobs/status
- Rate limit de 5/min no login é restritivo para integrações
- Escalas retornam `nome: null` (campo vazio no banco)

---

## DADOS REAIS DO BANCO (snapshot auditoria)

| Tabela | Registros |
|--------|-----------|
| employees (ativos) | 52 |
| cct_cargos | 52 |
| gp_clock_punches (batidas) | 1.846 |
| posts (postos) | 9 |
| shifts (turnos) | 180 |
| allocations | 48 |
| diarists | 13 |
| inspection_rounds | 3 |
| receivable_accounts | 11 (R$ 258.482,62) |
| payable_accounts | 8 (R$ 128.514,43) |
| bank_transactions | 649 |
| ged_document_tags | 16 |
| communication_announcements | 10 |
| disciplinary_actions | 11 |
| vacation_requests | 8 |
| ged_documents | 1 |

---

## PRÓXIMAS AÇÕES (plano de correção priorizado)

### Sprint imediata (bugs bloqueantes):

1. **Financeiro BI** — trocar `Session` → `AsyncSession` em `bi_controller.py` → desbloqueia 11 endpoints
2. **Financeiro Contabilidade** — `current_user["key"]` → `current_user.key` (72 ocorrências) → desbloqueia 4 endpoints
3. **DP/RH CCT** — corrigir nomes de colunas SQL em `cct_controller.py` → desbloqueia 5 endpoints
4. **GED Tags** — implementar `is_associated()` no `DocumentTagRepository` → desbloqueia 4 endpoints
5. **Operacional Tenant** — unificar `tenant_id` com `DEFAULT_TENANT_ID` fixo → torna 21 registros visíveis

### Sprint seguinte (bugs funcionais):

6. **Government** — instalar `croniter` no `requirements.txt` e corrigir import `get_db_sync`
7. **Operacional** — corrigir rota `/templates` antes de `/{action_id}` e implementar `get_stats()` no `TimeBankRepository`
8. **GED** — adicionar `redirect_slashes=True` nos routers para resolver trailing slash 404
9. **DP/RH** — serializar UUID como string no benefits service
10. **Alembic** — executar `alembic stamp sprint79_justification_employee_uuid`

### Médio prazo:

11. **GED AI** — configurar LLM provider corretamente para endpoints de AI
12. **Operacional** — corrigir `@property expires_at` no model `Announcement`
13. **Financeiro** — implementar `list_with_filters` no `BankTransactionRepository`

---

## RESUMO EXECUTIVO

O Conecta PRO está **funcionalmente operacional para o core do negócio** (vigilância, ponto eletrônico, financeiro básico, documentos), mas apresenta **falhas técnicas importantes** em módulos secundários que reduzem a experiência.

**Destaques positivos:**
- Bartolo com dados reais do banco ✅
- Auth e segurança JWT sólidos ✅
- Ponto eletrônico e SST funcionais ✅
- Integrações governamentais estáveis ✅

**Destaques negativos:**
- BI Dashboard financeiro 100% quebrado ❌
- CCT Controller com SQL desatualizado ❌
- 31 endpoints retornando 500 em produção ❌
- Tenant ID mismatch tornando dados invisíveis ❌

**Impacto no usuário:** Funcionalidades críticas (ponto, financeiro básico, docs) funcionam. Relatórios de BI, CCT e comunicados internos estão inacessíveis.

---

*Auditoria executada via Skill 01 (debugger-sistematico-conecta-pro) com 5 subagentes paralelos.*
*Arquivo salvo em: /opt/conecta-pro/AUDITORIA_SKILL01.md*
