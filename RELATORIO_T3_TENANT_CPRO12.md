# T3 CPRO12 — Seed Tenant Conecta Mais
**Data:** 2026-05-05 (executado ~00:45–01:05)
**Terminal:** T3
**Branch:** feature/people-management-reorganization

---

## Schema tenants (colunas obrigatórias sem DEFAULT)

| Coluna     | Tipo             | Constraint |
|------------|------------------|------------|
| id         | uuid             | PK, NOT NULL |
| codigo     | varchar(50)      | UNIQUE, NOT NULL |
| nome       | varchar(200)     | NOT NULL |
| documento  | varchar(20)      | UNIQUE, NOT NULL |
| email      | varchar(255)     | NOT NULL |
| status     | tenant_status    | NOT NULL, default 'trial' |
| plano      | tenant_plan      | NOT NULL, default 'free' |
| tipo       | tenant_type      | NOT NULL, default 'company' |
| ativo      | boolean          | NOT NULL, default true |

---

## Enum tenant_status (DB)

```
{active, inactive, suspended, blocked, trial, cancelled}
```

## Enum tenant_plan (DB)

```
{free, basic, professional, enterprise, custom}
```

## Enum tenant_type (DB)

```
{company, individual, government, nonprofit, educational}
```

---

## STEP 4 — Tenant inserido

```sql
INSERT INTO tenants (id, codigo, nome, nome_fantasia, documento, cnpj, email,
  responsavel_nome, responsavel_email, status, plano, tipo,
  endereco_cidade, endereco_estado, ativo)
VALUES (gen_random_uuid(), 'CPRO-001', 'CONECTAMAIS ELETRONICA LTDA',
  'Conecta Mais', '35710481000103', '35.710.481/0001-03',
  'jjesus@conectamais.pro', 'Jordan Jesus', 'jjesus@conectamais.pro',
  'active', 'free', 'company', 'Manaus', 'AM', true)
ON CONFLICT DO NOTHING
RETURNING id, nome, status, ativo;
```

**Resultado:**
```
id: 841a3906-5410-4047-a076-bc7bce95ffd2
nome: CONECTAMAIS ELETRONICA LTDA
status: active
ativo: t
INSERT 0 1
```

---

## STEP 5 — Validação SELECT

```
id                                   | nome                        | cnpj               | documento      | status | ativo | created_at
841a3906-5410-4047-a076-bc7bce95ffd2 | CONECTAMAIS ELETRONICA LTDA | 35.710.481/0001-03 | 35710481000103 | active | t     | 2026-05-05 00:49:25+00
```

```sql
SELECT COUNT(*) FROM tenants WHERE status = 'active';
-- 1
```

---

## STEP 6 — Teste vermelho (_get_active_tenants simulado)

```sql
-- Query do DB (status válido):
SELECT id, nome, status FROM tenants
WHERE status = 'active'::tenant_status AND ativo IS true;
-- Resultado: 1 linha ✅

-- Query do código Python (TenantStatus.ATIVO = "ativo"):
SELECT COUNT(*) FROM tenants WHERE status::text = 'ativo';
-- Resultado: 0 ❌  ← CENÁRIO D
```

---

## CENÁRIO D — Divergência enum Python vs DB

| | Python model | DB enum |
|---|---|---|
| Ativo | `TenantStatus.ATIVO = "ativo"` | `'active'` |
| Inativo | `TenantStatus.INATIVO = "inativo"` | `'inactive'` |
| Suspenso | `TenantStatus.SUSPENSO = "suspenso"` | `'suspended'` |

**Causa:** DB enum foi criado com valores em inglês (Alembic migration anterior).
Python enum foi posteriormente alterado para português sem atualizar o DB.

**Consequência:** `_get_active_tenants()` em `notification_triggers.py` linha 39
filtra `Tenant.status == TenantStatus.ATIVO` (= `"ativo"`), que não encontra
nenhuma linha no DB (que tem `'active'`). **Zero notificações dispararão até Jordan corrigir.**

**Decisão pendente Jordan (duas opções):**
1. Alterar Python: `TenantStatus.ATIVO = "active"` (alinha com DB — sem migration)
2. Alterar DB enum: adicionar `'ativo'` como alias (requer migration Alembic)
   **Recomendação: opção 1** — menor risco, sem migration.

---

## Hipóteses

| # | Hipótese | Resultado |
|---|---|---|
| H1 | tenants=0 antes | ✅ SIM — 0 linhas confirmado |
| H2 | enum tem 'active' | ✅ CONFIRMADO |
| H3 | campo cnpj existe | ✅ SIM — varchar(18), nullable |
| H4 | sem duplicata antes | ✅ CONFIRMADO — COUNT=0 |
| H5 | PK é UUID | ✅ SIM — sem default, uso gen_random_uuid() |
| H6 | _get_active_tenants usa 'active' | ❌ USA 'ativo' (Cenário D) |
| H7 | SELECT retorna 1 linha status='active' | ✅ SIM |
| H8 | query funcional retorna tenant | ⚠️ NÃO para query Python — SIM para query DB direta |

---

## Commits

| # | Hash | Mensagem |
|---|---|---|
| 1 | `e76e8296` | `docs(contracts): §60 — Seed Bug C3 tenant Conecta Mais (CPRO12 T3)` |
| 2 | `c8eb6da7` | `seed(tenants): Conecta Mais CNPJ 35.710.481/0001-03 status=active (§60)` |

Push: `be4f2292..c8eb6da7` ✅

---

## SELF-CHECK — 12 itens

```
[x] STEP 0 — contrato lido, §54 confirmado (última seção), §13.1 citado
[x] STEP 1.1 — \d tenants lido ANTES do INSERT (Chesterton)
[x] STEP 1.2 — enum tenant_status confirmado, 'active' existe
[x] STEP 1.3 — tabela estava vazia antes do insert (0 linhas)
[x] STEP 2 — INSERT montado com campos reais do schema
[x] STEP 3 — verificação de duplicata executada (COUNT=0)
[x] STEP 4 — INSERT executado com ON CONFLICT DO NOTHING
[x] STEP 5 — SELECT confirmou registro com status='active'
[x] STEP 6 — teste vermelho executado: query DB retorna 1 linha; Cenário D documentado
[x] STEP 7 — seed script salvo em seeds/seed_tenant_conecta_mais.sql
[x] STEP 8 — §60 no CONTRACTS_GEDEON ANTES do commit
[x] STEP 9 — 2 commits separados + push (e76e8296 + c8eb6da7)
[x] Zero código Python alterado (apenas SQL + docs)
[x] §13.4 — apenas 1 tenant inserido, nada além
```

---

## T3 CPRO12 — STATUS

**Seed executado:** tenant Conecta Mais ativo no DB (`status='active'`, `id=841a3906...`)

**⚠️ AÇÃO PENDENTE JORDAN:** corrigir `TenantStatus.ATIVO = "active"` em
`backend/modules/config/models/tenant.py` linha 20 para que
`_get_active_tenants()` encontre o tenant e as notificações operacionais disparem.
