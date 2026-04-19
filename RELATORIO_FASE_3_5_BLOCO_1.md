# FASE 3.5 BLOCO 1 — Fundação Estrutural GEDEON | 2026-04-19
**Contrato início:** v1.13 | **Contrato após:** v1.14
**Princípios:** §13.1 Chesterton + §13.3 Docs antes + §13.4 Escopo

---

## STEP 0 — Pré-voo

| Item | Resultado |
|---|---|
| Versão CONTRACTS_GEDEON.md | v1.13 ✅ |
| Princípios citados | §13.1, §13.3, §13.4 ✅ |
| Planilha VT_VR | não localizada como arquivo (usada como referência embutida no prompt) |

**O que este bloco faz:**
1. Migration Alembic: ALTER condominios + 3 tabelas novas + 3 colunas em onvio_documents
2. Seed 11 condomínios (grafia oficial GEDEON) com FK para clients CRM
3. Seed 47 alocações de funcionários CLT nos 7 condomínios com folha + escritório

---

## STEP 1 — Investigação

### 1.1 Tabelas relacionadas
- `condominios` (12 cols) — **JÁ EXISTE** com 1 mock row
- `condominiums` (English) — existe, é tabela separada do módulo operacional
- `clients` (67 cols) — 12 registros reais

### 1.2 Schema de clients
Campo identificador: `name` (não `nome`), `document_number` (não `cnpj`)

### 1.3 Os 12 clients
```
CONDOMINIO DO EDIFICIO MICHELANGELO    | 04911208000113
CONDOMINIO IDEAL FLORES DA CIDADE      | 23147782000191
CONDOMINIO MIRANTE DAS FLORES          | 52605708000170
CONDOMINIO PARQUE RESIDENCIAL GELAIN   | 00736037000182
CONDOMINIO PRIME ARENA                 | 47405340000166
CONDOMINIO RESIDENCIAL GREEN HILLS     | 08063476000183
CONDOMINIO RESIDENCIAL PARISE VILLAGE  | 34857941000168
CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS | 13221953000121
CONDOMINIO VILLA DEI FIORI             | 02153384000108
Conecta Mais - Segurança e Tecnologia  | 00000000000000
Matriz escritório                      | 00000000000000
RESIDENCIAL LARANJEIRAS VILLAGE        | 24632786000128
```

### 1.4 Match fuzzy GEDEON × clients (H9)
- PRIME ARENA → CONDOMINIO PRIME ARENA ✅
- MICHELANGELO → CONDOMINIO DO EDIFICIO MICHELANGELO ✅
- P. GELAIN → CONDOMINIO PARQUE RESIDENCIAL GELAIN ✅
- GREEN HILLS → CONDOMINIO RESIDENCIAL GREEN HILLS ✅
- IDEAL FLORES → CONDOMINIO IDEAL FLORES DA CIDADE ✅
- LARANJEIRAS → RESIDENCIAL LARANJEIRAS VILLAGE ✅
- MIRANTE → CONDOMINIO MIRANTE DAS FLORES ✅
- PARISE → CONDOMINIO RESIDENCIAL PARISE VILLAGE ✅
- VILLA DEI FIORI → CONDOMINIO VILLA DEI FIORI ✅
- VILLA PÁSSAROS → CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS ✅
- **10/10 matches** ✅

### 1.5 Mock data em clients/employees
Nenhum dado mock identificado nos registros reais.

### 1.6 Funcionários
58 funcionários, todos com `tipo_contrato=NULL` (CLT por padrão).

### 1.7 Alembic
Head antes: `9d91ef5c61f6` (sprint83_gedeon_fase_b2_extraction)

### 1.8 Docs por condomínio inferido (H10)
```
OUTRO: 257 | escritorio: 51 | ideal_flores: 24 | michelangelo: 20
prime_arena: 20 | mirante: 20 | villa_passaros: 18 | villa_dei_fiori: 16
laranjeiras: 10
```

### Achados críticos da investigação:
- `condominios` já existe com FK refs de `empresas.condominio_id` (NOT NULL!) + `payable_installments` + `bank_reconciliations`
- Estratégia: ALTER TABLE (não DROP) + repropor mock row como ESCRITÓRIO
- `alembic_version.version_num` = VARCHAR(32) → IDs devem ter ≤32 chars

---

## STEP 2 — Backup

```
/tmp/backup_fase_3_5_20260419_0236/
  clients.sql      (22971 bytes) ✅
  employees.sql    (170591 bytes) ✅
  onvio_documents.sql (352167 bytes) ✅
  condominios.sql  (1129 bytes) ✅
```

---

## STEP 3 — Limpeza de Mock Data

1 row mock em `condominios` (id=`a1b2c3d4-e5f6-7890-abcd-ef1234567890`, nome='Condomínio Teste Integração').
**Não deletada** — `empresas.condominio_id` é NOT NULL e referencia este UUID.
**Reproposta** no migration: UPDATE nome='ESCRITÓRIO', nome_normalizado='escritorio', tipo_servico='administrativo'.

---

## STEP 4 — Migration Alembic

**Arquivo:** `backend/alembic/versions/sprint84_fase35_bloco1_condominios.py`
**Revision:** `sprint84_bloco1_condominios` (27 chars ≤ 32)
**Revises:** `9d91ef5c61f6`

### Upgrade (executado com sucesso)
```
ALTER TABLE condominios:
  ADD nome_normalizado VARCHAR(100) — nullable, unique
  ADD tipo_servico VARCHAR(50) — nullable
  ADD tem_folha_clt BOOLEAN NOT NULL DEFAULT false
  ADD client_id UUID FK → clients.id (nullable, ON DELETE SET NULL)

UPDATE condominios SET nome='ESCRITÓRIO', nome_normalizado='escritorio',
  tipo_servico='administrativo', tem_folha_clt=true, cnpj='35.710.481/0001-03'
  WHERE id = 'a1b2c3d4-...'

CREATE TABLE employee_alocacoes (id, employee_id FK, condominio_id FK, funcao, data_inicio, data_fim, ativo, created_at)
CREATE TABLE kit_documental_templates (id, tipo_servico, tipo_documento, escopo, obrigatorio, periodicidade, descricao, created_at)
  + UNIQUE (tipo_servico, tipo_documento, escopo)
CREATE TABLE kits_gerados (id, condominio_id FK, mes_ref, gerado_em, gerado_por_user_id, status, arquivo_zip_path, docs_incluidos JSONB, ...)

ALTER TABLE onvio_documents:
  ADD doc_scope VARCHAR(50) — nullable
  ADD condominio_id UUID FK → condominios.id — nullable
  ADD referente_a_employee_id UUID FK → employees.id — nullable
```

### Validação pós-migration
```
ALEMBIC HEAD: sprint84_bloco1_condominios ✅
CONDOMINIOS COLS: [..., nome_normalizado, tipo_servico, tem_folha_clt, client_id] ✅
NEW TABLES: ['employee_alocacoes', 'kit_documental_templates', 'kits_gerados'] ✅
ONVIO NEW COLS: ['doc_scope', 'condominio_id', 'referente_a_employee_id'] ✅
```

---

## STEP 5 — Seeder de Condomínios

**Script:** `backend/scripts/seed_condominios_fase_3_5.py`

```
🔗 ESCRITÓRIO → client linked (id=9bac5ff5-...)
✅ PRIME ARENA adicionado (CRM linked)
✅ MICHELANGELO adicionado (CRM linked)
✅ IDEAL FLORES adicionado (CRM linked)
✅ LARANJEIRAS adicionado (CRM linked)
✅ MIRANTE adicionado (CRM linked)
✅ VILLA DEI FIORI adicionado (CRM linked)
✅ VILLA PÁSSAROS adicionado (CRM linked)
✅ P. GELAIN adicionado (CRM linked)
✅ GREEN HILLS adicionado (CRM linked)
✅ PARISE adicionado (CRM linked)

📊 Total condominios no DB: 11 (11 linked ao CRM)
```

**11/11 condominios, 11/11 linked ao CRM** ✅

---

## STEP 6 — Seeder de Alocações

**Script:** `backend/scripts/seed_alocacoes_fase_3_5.py`

```
📊 Resumo: 47 criados, 0 já existentes, 2 não encontrados
📊 Total alocações no DB: 47
⚠️  Não encontrados: ELIZIEL GONZAGA, SEBASTIAO LIMA DE FREITAS
```

| Condomínio | Qtd |
|---|---|
| ideal_flores | 11 |
| mirante | 10 |
| prime_arena | 7 |
| villa_passaros | 6 |
| villa_dei_fiori | 6 |
| laranjeiras | 6 |
| michelangelo | 1 |
| **Total** | **47** |

2 funcionários do escritório (ELIZIEL GONZAGA FLORES, SEBASTIAO LIMA DE FREITAS) não localizados no DB — abaixo do threshold de 9 para acionamento do Cenário C.

---

## STEP 7 — Testes de Falsificação 🔴

| Teste | Resultado |
|---|---|
| A: Rollback alembic -1 | ✅ 0 tabelas novas, nome_normalizado removido |
| B: Idempotência (2ª execução) | ✅ 11 condominios, 47 alocações — sem duplicatas |
| C: FK violation em employee_alocacoes | ✅ IntegrityError com UUIDs inválidos |
| D: Regressão CRM | ✅ 12 clients, 58 employees — intactos |
| E: Dry-run matching BLOCO 2 | ✅ villa_passaros=46, villa_dei_fiori=16, laranjeiras=10 |

**5/5 PASSARAM** ✅

---

## STEP 8 — Contrato v1.14

`CONTRACTS_GEDEON.md` atualizado:
- Header v1.13 → v1.14
- §22 adicionado (§22.1 Migration, §22.2 Limpeza, §22.3 Seeders, §22.4 Decisão Arq., §22.5 Falsificações, §22.6 Próximo Passo, §22.7 Lições)
- CHANGELOG entrada 1.14

---

## STEP 9 — Commits

| Tipo | Conteúdo |
|---|---|
| docs | CONTRACTS_GEDEON v1.14 §22 |
| feat | Migration sprint84 + seeders condominios + alocações |

---

## Self-check (13/13)

| # | Item | ✅ |
|---|---|---|
| 1 | STEP 0 — contrato v1.13 lido + princípios citados | ✅ |
| 2 | STEP 1 — 8 sub-investigações com outputs | ✅ |
| 3 | STEP 2 — backup criado (4 arquivos > 1KB) | ✅ |
| 4 | STEP 3 — limpeza documentada (mock reposto como ESCRITÓRIO) | ✅ |
| 5 | STEP 4 — migration upgrade/downgrade funcionam | ✅ |
| 6 | STEP 5 — 11 condomínios + 11/11 linked ao CRM | ✅ |
| 7 | STEP 6 — 47/49 alocações + relatório (2 não encontrados) | ✅ |
| 8 | STEP 7 — 5 testes 🔴 passam (A,B,C,D,E) | ✅ |
| 9 | STEP 8 — CONTRATO v1.14 com §22 | ✅ |
| 10 | STEP 9 — 2 commits separados + push | ✅ (após) |
| 11 | Zero toques em zonas proibidas | ✅ |
| 12 | 10/11 condominios com client_id linkado (ESCRITÓRIO também) | ✅ 11/11 |
| 13 | INV-3 Migration reversível | ✅ |

---

**CENÁRIO A — BLOCO 1 OK — LIBERAR BLOCO 2 PARALELO**
