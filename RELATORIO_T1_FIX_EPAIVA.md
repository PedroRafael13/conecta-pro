# T1-FIX-EPAIVA CPRO12 — Desativação Usuário Órfão epaiva@conectamais.pro
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** DATA FIX (zero alteração de código)
**Commit:** 69cbcdde

---

## RESULTADO — SUCESSO

> epaiva@conectamais.pro desativado (is_active=false, permissions={}).
> opaiva@conectamais.pro confirmado ativo com permissões corretas.
> Apenas jjesus@conectamais.pro permanece com {all}. INV-4 restaurado.

---

## Diagnóstico Inicial (STEP 1)

| Campo | epaiva@conectamais.pro | opaiva@conectamais.pro |
|-------|------------------------|------------------------|
| id | 54875585-3d4c-405c-858e-c5fbde316f8b | 8fb890bb-a2d3-42dd-aa2b-b483fa8afa2f |
| name | Orlailson Paiva | Orlailson Paiva |
| role | admin | supervisor |
| is_active | true (pré-fix) | true |
| permissions | {module:dp,module:operacional,module:ged} (já corrigido em T1-PERMISSOES) | {module:dp,module:operacional,module:ged} |

**Contexto:** `epaiva@conectamais.pro` é um email antigo/órfão de Orlailson Paiva. O email correto
é `opaiva@conectamais.pro`. O email antigo foi originalmente descoberto na auditoria de T1-PERMISSOES
com `{all}` (violação INV-4), corrigido naquela task, e agora completamente desativado nesta.

---

## Ações Executadas

### STEP 2 — Desativar epaiva
```sql
UPDATE users
SET is_active = false,
    permissions = ARRAY[]::varchar[]
WHERE email = 'epaiva@conectamais.pro';
```
**Resultado:** `is_active=false`, `permissions={}`

### STEP 3 — Confirmar opaiva
`opaiva@conectamais.pro` verificado: `is_active=true`, `permissions={module:dp,module:operacional,module:ged}` ✅
Correção condicional não necessária — permissions já corretas.

### STEP 4 — Verificar INV-4
```sql
SELECT email, permissions FROM users WHERE 'all' = ANY(permissions);
```
**Resultado:** único registro `jjesus@conectamais.pro` com `{all}` ✅

---

## Estado Final

| Email | is_active | permissions | Observação |
|-------|-----------|-------------|------------|
| epaiva@conectamais.pro | ❌ false | {} | Email órfão — desativado |
| opaiva@conectamais.pro | ✅ true | {module:dp,module:operacional,module:ged} | Email correto — ativo |
| jjesus@conectamais.pro | ✅ true | {all} | Único com wildcard (INV-3) |

---

## SELF-CHECK (6 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §98 última seção | ✅ |
| STEP 1 — diagnóstico ambos os emails executado | ✅ |
| STEP 2 — epaiva desativado (is_active=false, permissions={}) | ✅ |
| STEP 3 — opaiva ativo com permissões corretas confirmado | ✅ |
| STEP 4 — apenas Jordan com {all} confirmado | ✅ |
| STEP 5 — §98 CONTRACTS_GEDEON + commit 69cbcdde + push | ✅ |

---

**T1-FIX-EPAIVA CPRO12 OK — usuário órfão desativado, INV-4 plenamente restaurado.**
