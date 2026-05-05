# T_RAZAO_SOCIAL — Atualização Razão Social
**Data:** 2026-05-05
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Tipo:** DATA FIX — zero mudanças de código

---

## Objetivo

Atualizar razão social `Jordan Santos de Jesus Ltda` → `CONECTAMAIS ELETRONICA LTDA`
CNPJ: 35.710.481/0001-03 (inalterado)

---

## STEP 1 — Diagnóstico

Varredura completa em 17 tabelas/colunas. Resultado:

| Tabela | Campo | Situação |
|--------|-------|----------|
| tenants | nome | ✅ Já correto: CONECTAMAIS ELETRONICA LTDA |
| empresas | razao_social | ❌ Jordan Santos de Jesus Ltda → UPDATE necessário |
| tenants | endereco_logradouro/bairro/cep | ❌ Vazio → preencher |
| bidding_certificates | razao_social | ❌ 8 linhas com nome antigo |
| ged_clients | contact_name | ❌ Jordan Santos → Jordan Jesus |
| cashflow_entries | descricao | 📋 20 linhas históricas — mantidas |
| bank_transactions | descricao | 📋 176+ linhas históricas — mantidas |
| inter_transactions | descricao | 📋 10 linhas históricas — mantidas |
| nfses | prestador/tomador | 📋 27 linhas históricas — mantidas |

---

## STEP 2 — Backup

```
/tmp/backup_razao_social_20260505_213121.sql (16K)
Tabelas: empresas + tenants + condominios
```

---

## STEP 3 — UPDATEs Executados

```sql
BEGIN;
UPDATE empresas SET razao_social = 'CONECTAMAIS ELETRONICA LTDA', updated_at = CURRENT_DATE
  WHERE id = '619a3df1-8bce-49ce-b77a-04f80a0e8491'; -- 1 row

UPDATE tenants SET endereco_logradouro = 'Rua Adalberto Pinto Borges',
  endereco_bairro = 'Crespo', endereco_cep = '69073-488'
  WHERE cnpj = '35.710.481/0001-03'; -- 1 row

UPDATE bidding_certificates SET razao_social = 'CONECTAMAIS ELETRONICA LTDA'
  WHERE razao_social ILIKE '%jordan%' AND cnpj = '35710481000103'; -- 8 rows

UPDATE ged_clients SET contact_name = 'Jordan Jesus'
  WHERE id = '283b366c-1732-4c9f-ab7b-03b56fc97f06'; -- 1 row
COMMIT;
```

---

## STEP 4 — Verificação

| Tabela | Campo | Valor Atual |
|--------|-------|-------------|
| empresas | razao_social | CONECTAMAIS ELETRONICA LTDA ✅ |
| tenants | nome + endereço | CONECTAMAIS ELETRONICA LTDA \| Rua Adalberto Pinto Borges, Crespo, 69073-488 ✅ |
| bidding_certificates | razao_social (8 rows) | CONECTAMAIS ELETRONICA LTDA ✅ |
| ged_clients | contact_name | Jordan Jesus ✅ |

---

## STEP 5 — Contratos + Commit

- §106 appendado ao CONTRACTS_GEDEON.md
- Commit docs: `af5be3ce`

---

## Self-check

| Item | Status |
|------|--------|
| Backup criado antes de qualquer UPDATE | ✅ |
| empresas.razao_social atualizado | ✅ |
| tenants.endereco preenchido | ✅ |
| bidding_certificates (8 linhas) atualizados | ✅ |
| ged_clients.contact_name atualizado | ✅ |
| Histórico (cashflow, bank_tx, nfses) mantido intacto | ✅ |
| §106 adicionado ao CONTRACTS_GEDEON.md | ✅ |
| Zero mudanças de código | ✅ |

---

**T_RAZAO_SOCIAL OK**

[session: t5] [module: ged]
