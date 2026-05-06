# Fechamento Alocações 7 Demitidos + Orlailson PJ
**Data:** 2026-05-06
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Autorização:** Jordan Jesus (CEO) — confirmado em 2026-05-06
**Branch:** feature/people-management-reorganization

---

## Invariantes respeitados

| INV | Descrição | Status |
|-----|-----------|--------|
| INV-1 | BACKUP antes de qualquer UPDATE | ✅ |
| INV-2 | Nunca DELETE — apenas UPDATE | ✅ |
| INV-3 | Orlailson NÃO demitido — continua PJ | ✅ |
| INV-4 | IDs confirmados antes dos UPDATEs | ✅ |
| INV-5 | Colunas reais: matricula/nome/cargo | ✅ |
| INV-6 | Status reais: 'ativo'/'inativo' | ✅ |

---

## STEP 1 — Diagnóstico + Backup

### Backups criados

| Tabela | Tamanho |
|--------|---------|
| allocations_backup_20260506 | 8 KB (51 registros) |
| employees_backup_20260506 | 64 KB (58 registros) |

### Adaptação necessária

O prompt usa `registration_number` — coluna real é `matricula`. Descoberto via `information_schema.columns`.

### Estado pré-UPDATE dos 8 funcionários

| Nome | Matrícula | status_emp | alloc_status | is_active | end_date |
|------|-----------|-----------|--------------|-----------|----------|
| ANDREW COSTA VASCONCELOS | 000161 | inativo | active | true | NULL |
| CARLOS ALBERTO ASSIS DE LIMA | 183 | inativo | active | true | NULL |
| GELSON BERNARDO LIMA | 178 | inativo | active | true | NULL |
| JEFFERSON DA SILVA BATISTA | 000182 | inativo | active | true | NULL |
| JORDANA BACRY PIRES | 179 | inativo | active | true | NULL |
| JÚLIO CÉSAR ASSIS SANTOS | 000185 | inativo | active | true | NULL |
| ROBERTO PEREIRA MENEZES | 000196 | inativo | active | true | NULL |
| ORLAILSON PAIVA PEREIRA | 000192 | inativo | active | true | NULL |

---

## STEP 2 — Fechamento das 7 alocações

### UPDATE executado

```sql
UPDATE allocations
SET
  is_active = false,
  status = 'terminated',
  end_date = CASE
    WHEN employee_id = (SELECT id FROM employees WHERE matricula = '000182')
      THEN '2026-02-19'::date
    WHEN employee_id = (SELECT id FROM employees WHERE matricula = '000185')
      THEN '2025-12-03'::date
    ELSE '2026-02-28'::date
  END,
  updated_at = NOW()
WHERE employee_id IN (
  SELECT id FROM employees
  WHERE matricula IN ('000196','183','000161','178','000182','179','000185')
)
AND is_active = true;
-- Resultado: UPDATE 7
```

### Estado pós-UPDATE

| Nome | Matrícula | alloc_status | is_active | end_date |
|------|-----------|--------------|-----------|----------|
| ANDREW COSTA VASCONCELOS | 000161 | terminated | false | 2026-02-28 |
| CARLOS ALBERTO ASSIS DE LIMA | 183 | terminated | false | 2026-02-28 |
| GELSON BERNARDO LIMA | 178 | terminated | false | 2026-02-28 |
| JEFFERSON DA SILVA BATISTA | 000182 | terminated | false | 2026-02-19 |
| JORDANA BACRY PIRES | 179 | terminated | false | 2026-02-28 |
| JÚLIO CÉSAR ASSIS SANTOS | 000185 | terminated | false | 2025-12-03 |
| ROBERTO PEREIRA MENEZES | 000196 | terminated | false | 2026-02-28 |

### Contagem alocações

| Estado | Antes | Depois | Δ |
|--------|-------|--------|---|
| Ativas (is_active=true) | 51 | **44** | −7 |
| Encerradas (terminated) | 0 | **7** | +7 |

---

## STEP 3 — Orlailson Paiva Pereira (mat. 000192)

**Cenário:** A — campo `tipo_contrato` existe na tabela `employees`

### UPDATE executado

```sql
UPDATE employees
SET tipo_contrato = 'pj',
    observacoes = '[2026-05-06] Confirmado por Jordan Jesus (CEO): colaborador PJ — mantém alocação ativa.',
    updated_at = NOW()
WHERE matricula = '000192';
-- Resultado: UPDATE 1
```

### Estado pós-UPDATE

| Campo | Valor |
|-------|-------|
| nome | ORLAILSON PAIVA PEREIRA |
| matricula | 000192 |
| tipo_contrato | **pj** |
| status | inativo |
| alloc_status | **active** |
| is_active | **true** |
| start_date | 2026-03-01 |
| end_date | NULL (alocação aberta) |

INV-3 respeitado: alocação permanece ativa.

---

## STEP 4 — Documentação

- §113 appendado ao `CONTRACTS_GEDEON.md`
- Commit: `c83eea73` — `docs(contracts): §113 — fechamento alocações 7 demitidos + Orlailson PJ`
- Push: ✅ `feature/people-management-reorganization`

---

## Self-check

| Item | Status |
|------|--------|
| Backup allocations_backup_20260506 criado | ✅ |
| Backup employees_backup_20260506 criado | ✅ |
| 8 funcionários confirmados por ID antes do UPDATE | ✅ |
| 7 alocações encerradas (terminated, is_active=false) | ✅ |
| end_dates corretos por funcionário | ✅ |
| Orlailson: tipo_contrato='pj' | ✅ |
| Orlailson: alocação is_active=true preservada | ✅ |
| §113 em CONTRACTS_GEDEON.md | ✅ |
| git commit + push | ✅ |
| Zero DELETEs executados | ✅ |

---

**MISSÃO CONCLUÍDA**

UPDATEs: 7 alocações terminated + 1 tipo_contrato PJ
Alocações ativas: 51 → 44
Novos funcionários demitidos: nenhum (apenas fechamento de alocações em aberto)
Orlailson: PJ confirmado, alocação ativa preservada

[session: t5] [module: ged]
