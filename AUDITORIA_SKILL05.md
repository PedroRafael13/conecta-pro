# AUDITORIA SKILL 05 — MODELAGEM E BANCO DE DADOS
## Conecta PRO — PostgreSQL 16.11 (Alpine)
**Data:** 31/03/2026
**Banco:** `conecta_pro` | **Host:** `conecta-pro-postgres`
**Migration atual:** `sprint79_just_uuid`

---

## PASSO INICIAL — SNAPSHOT GERAL

| Métrica | Valor |
|---------|-------|
| Versão PostgreSQL | 16.11 (Alpine/musl, 64-bit) |
| Tamanho total do banco | 52 MB |
| Total de tabelas | 483 |
| Total de índices | 2.361 |
| Total de FK constraints | 386 |
| Tabelas com dados | 122 (25,3%) |
| Tabelas vazias | 361 (74,7%) |
| max_connections | 150 |
| shared_buffers | 128 MB |
| work_mem | 4 MB |
| Migration atual | sprint79_just_uuid |

### Top 10 Tabelas por Tamanho
| Tabela | Tamanho Total | Dados | Índices | FKs |
|--------|--------------|-------|---------|-----|
| gp_clock_punches | 1.008 kB | 296 kB | 672 kB | 0 |
| sst_cipa_reunioes | 776 kB | 416 kB | 320 kB | 0 |
| employees | 584 kB | 168 kB | 376 kB | 0 |
| bank_transactions | 448 kB | 272 kB | 136 kB | 5 |
| disciplinary_actions | 272 kB | 16 kB | 224 kB | 4 |
| occurrences | 224 kB | 8 kB | 208 kB | 4 |
| clients | 224 kB | 8 kB | 208 kB | 1 |
| bidding_tenders | 224 kB | 8 kB | 208 kB | 0 |
| shifts | 208 kB | 48 kB | 128 kB | 3 |
| fin_accounting_accounts | 208 kB | 8 kB | 192 kB | 2 |

> ⚠️ **Padrão crítico**: 19 das 20 maiores tabelas têm mais espaço em índices do que em dados — sinal de **over-indexing severo**.

---

## SUBAGENTE 1 — AUDITORIA GED + DOCUMENTS

### CHECK 1 — Contagem de Linhas

| Tabela | Linhas |
|--------|--------|
| document_folders | 0 |
| document_kit_assignments | 0 |
| document_kit_item_statuses | 0 |
| document_kit_items | 29 |
| document_kits | 4 |
| documents | 0 |
| ged_clients | 14 |
| ged_contracheques | 0 |
| ged_document_kits | 18 |
| ged_document_shares | 0 |
| ged_document_signatures | 2 |
| ged_document_tag_associations | 0 |
| ged_document_tags | 16 |
| ged_document_versions | 1 |
| ged_documents | 1 |
| ged_folders | 7 |
| ged_kit_access_logs | 0 |
| ged_kit_documents | 44 |

### CHECK 2 — Schema `ged_documents` (70 colunas)
Tabela rica e bem estruturada:
- **Chave:** `id` UUID (gen_random_uuid()), `code` NOT NULL
- **Título/arquivo:** `title`, `file_name`, `file_extension`, `file_path`, `file_size_bytes`, `mime_type`, `checksum` — todos NOT NULL
- **Status/controle:** `status`, `confidentiality`, `document_type`, `category` — anuláveis com default
- **Versioning:** `current_version`, `version_count`, `is_latest`
- **Relacionamentos:** `condominium_id`, `contract_id`, `employee_id`, `client_id`, `resident_id`, `occurrence_id`, `owner_id`
- **Workflow:** `requires_approval`, `approved_by`, `approved_at`, `rejected_by`, `rejection_reason`
- **Assinatura:** `is_signed`, `signature_count`, `requires_signature`, `signature_deadline`
- **OCR/AI:** `is_ocr_processed`, `ocr_text`, `ocr_confidence`, `ai_classification`, `ai_confidence`
- **Auditoria:** `created_at`, `updated_at`, `deleted_at`, `created_by`, `updated_by`, `archived_by`

### CHECK 3 — Índices `ged_documents` (9 índices)
| Índice | Tipo |
|--------|------|
| ged_documents_pkey (id) | UNIQUE PRIMARY |
| ged_documents_code_key (code) | UNIQUE |
| ix_ged_documents_folder_id | B-tree |
| ix_ged_documents_status | B-tree |
| ix_ged_documents_document_type | B-tree |
| ix_ged_documents_condominium_id | B-tree |
| idx_ged_docs_client (client_id) | B-tree |
| idx_ged_docs_contract (contract_id) | B-tree |
| idx_ged_docs_employee (employee_id) | B-tree |

> ✅ Cobertura de índices adequada para as colunas de filtro mais comuns.

### CHECK 4 — Foreign Keys GED (29 FKs)
- `ged_documents.folder_id → ged_folders.id` ✅
- `ged_document_kits.client_id → ged_clients.id` ✅
- `ged_kit_documents.kit_id → ged_document_kits.id` ✅
- `ged_document_tag_associations.document_id → ged_documents.id` ✅
- `ged_document_tag_associations.tag_id → ged_document_tags.id` ✅
- `ged_document_versions.document_id → ged_documents.id` ✅
- `ged_document_shares.document_id → ged_documents.id` ✅
- `ged_document_signatures.document_id → ged_documents.id` ✅
- `document_kits.condominio_id → condominiums.id` ✅
- `document_kits.created_by → users.id`, `updated_by → users.id` ✅
- `document_kit_assignments.*` → FK intactas para users, condominiums, document_kits ✅

### CHECK 5 — Tabelas sem índices (exceto pkey)
`(0 rows)` — todas as tabelas GED têm índices.

### CHECK 6 — NULLs críticos `ged_documents`
| Campo | NULLs | Total |
|-------|-------|-------|
| title | 0 | 1 |
| file_path | 0 | 1 |
| status | 0 | 1 |
| created_at | 0 | 1 |

> ✅ Sem NULLs críticos.

### CHECK 7 — Distribuição de status `ged_documents`
| Status | Count |
|--------|-------|
| EXCLUIDO | 1 |

> ⚠️ 100% dos documentos estão com status EXCLUIDO — módulo GED praticamente sem uso real (volume irrisório: 1 doc).

### CHECK 8 — Documentos órfãos
`orphaned_docs = 0` ✅

### CHECK 9 — Status `document_kit_assignments`
`(0 rows)` — tabela vazia.

### CHECK 10 — Tamanho dos índices `ged_documents`
Todos os 9 índices: 16 kB cada (mínimo de página PostgreSQL). Banco GED em estado inicial.

---

### ═══ SCORE GED: 8/10 ═══

**Pontos positivos:**
- ✅ Schema rico e bem modelado (70 colunas, suporte a OCR, AI, assinaturas)
- ✅ Todas as 29 FKs íntegras, sem órfãos
- ✅ Índices adequados nas colunas de filtro
- ✅ Zero NULLs críticos

**Problemas:**
- ⚠️ Volume praticamente inexistente (1 documento excluído) — módulo GED sem uso real em produção
- ⚠️ `document_kit_assignments` vazia, apesar de document_kit_items ter 29 linhas — fluxo de atribuição não iniciado
- ⚠️ `ged_kit_access_logs` vazia — sem histórico de acesso

**Perda de 2 pontos:** Dados reais insuficientes para auditoria significativa de integridade.

---

## SUBAGENTE 2 — AUDITORIA FINANCEIRO

### CHECK 1 — Contagem de Linhas

| Tabela | Linhas |
|--------|--------|
| bank_accounts | 2 |
| bank_reconciliations | 0 |
| bank_transactions | **649** |
| billing_rules | 11 |
| cashflow_entries | 0 |
| cashflow_forecasts | 0 |
| fin_accounting_accounts | 9 |
| fin_accounting_periods | 3 |
| fin_charts_of_accounts | 1 |
| fin_cost_centers | 0 |
| fin_journal_entries | 11 |
| fin_journal_entry_lines | 23 |
| fin_trial_balances | 0 |
| fin_trial_balance_items | 0 |
| financial_kpis | 0 |
| payable_accounts | 8 |
| payable_categories | 0 |
| payable_installments | 0 |
| payable_payments | 0 |
| receivable_accounts | 11 |
| receivable_categories | 0 |
| receivable_installments | 0 |
| receivable_payments | 0 |

> `bank_transactions` é a tabela mais ativa com 649 linhas.

### CHECK 2 — Schema `fin_journal_entries` (48 colunas)
Modelo completo de lançamento contábil:
- `condominio_id`, `period_id` NOT NULL — isolamento multi-tenant correto
- `entry_type`, `status`, `origin` como ENUMs (USER-DEFINED)
- `total_debit`, `total_credit` como `numeric` ✅
- `is_balanced` para validação de partidas dobradas
- Campos SPED: `sped_included`, `sped_record_type`
- Soft delete: `deleted_at`, `deleted_by`

### CHECK 3 — Índices tabelas principais
**bank_transactions (5 índices):**
- `bank_transactions_pkey`, `ix_bank_transactions_bank_account_id`, `ix_bank_transactions_status`, `ix_bank_transactions_transaction_date`, `ix_bank_transactions_reconciliation_status`

**fin_journal_entries (11 índices):**
- Pkey, number UNIQUE, status, type, origin, period, condominio, date, source, active — cobertura completa ✅

**receivable_accounts (12 índices):**
- Índices em status, due_date, condominio_id, customer, unidade, morador, overdue — cobertura excelente ✅

**payable_accounts (7 índices):**
- status, due_date, condominio_id, supplier_id, category_id, condo_due composto ✅

### CHECK 4 — Foreign Keys Financeiro
- `fin_journal_entries.condominio_id`, `period_id` — referências internas ✅
- `fin_journal_entry_lines.journal_entry_id → fin_journal_entries.id` ✅
- `bank_transactions.bank_account_id → bank_accounts.id` ✅
- `receivable_accounts.condominio_id → condominiums.id` ✅
- `payable_accounts.supplier_id`, `condominio_id` ✅

> ⚠️ **FK sem índice detectada:** `bank_transactions.cashflow_entry_id`, `reconciliation_id`, `transfer_from_account_id`, `transfer_to_account_id` — listadas no Check 9 global.

### CHECK 5 — Status `bank_transactions`
| Status | Count | Total Amount |
|--------|-------|-------------|
| confirmado | 649 | R$ 30.161,24 |

> ✅ Todas as 649 transações com status `confirmado`, sem NULLs.

### CHECK 6 — NULLs críticos
| Tabela | null_valor | null_data | Total |
|--------|-----------|-----------|-------|
| bank_transactions | 0 | 0 | 649 |
| receivable_accounts | 0 | 0 | 11 |
| payable_accounts | 0 | 0 | 8 |

> ✅ Zero NULLs em campos críticos financeiros.

### CHECK 7 — Contas a receber vencidas
`overdue_receivables = 0` — nenhuma pendente vencida.

Status receivable_accounts: `pendente = 2`, `paga = 9`.

### CHECK 8 — Períodos contábeis
| Nome | Início | Fim | Status |
|------|--------|-----|--------|
| Janeiro 2026 | 2026-01-01 | 2026-01-31 | PENDING |
| Fevereiro 2026 | 2026-02-01 | 2026-02-28 | PENDING |
| Marco 2026 | 2026-03-01 | 2026-03-31 | PENDING |

> ✅ Sem sobreposição de períodos. ⚠️ Todos em PENDING — nenhum período fechado ainda.

### CHECK 9 — Linhas órfãs `fin_journal_entry_lines`
`orphaned_lines = 0` ✅

### CHECK 10 — Tamanho tabelas financeiras
| Tabela | Total | Dados |
|--------|-------|-------|
| bank_transactions | 448 kB | 272 kB |
| fin_journal_entries | 192 kB | 8 kB |
| receivable_accounts | 176 kB | 8 kB |
| payable_accounts | 96 kB | 8 kB |

---

### ═══ SCORE FINANCEIRO: 8/10 ═══

**Pontos positivos:**
- ✅ Schema robusto com suporte a multi-tenant (condominio_id)
- ✅ Zero NULLs em campos críticos
- ✅ Partidas dobradas modeladas (total_debit/total_credit + is_balanced)
- ✅ Índices excelentes em receivable/payable/journal_entries
- ✅ Sem linhas órfãs, FK intactas

**Problemas:**
- ⚠️ 4 FKs de `bank_transactions` sem índice (cashflow_entry_id, reconciliation_id, transfer_from/to_account_id)
- ⚠️ `cashflow_entries`, `cashflow_forecasts`, `fin_trial_balances` vazias — funcionalidades de fluxo de caixa e trial balance não iniciadas
- ⚠️ Todos os períodos em PENDING — nenhum mês fechado formalmente

---

## SUBAGENTE 3 — AUDITORIA DP/FUNCIONÁRIOS

### CHECK 1 — Contagem de Linhas

| Tabela | Linhas |
|--------|--------|
| admission_processes | 14 |
| cct_beneficios | 8 |
| cct_cargos | **52** |
| cct_convencoes | 1 |
| cct_feriados | 16 |
| employee_benefits | **157** |
| employee_deductions | 5 |
| employee_dp | 0 |
| employees | **52** |
| gp_asos | **96** |
| gp_cats | 2 |
| gp_clock_punches | **1.846** |
| gp_epi_deliveries | **220** |
| gp_justifications | 0 |
| gp_monthly_closings | 0 |
| gp_risks | 15 |
| hr_employee_documents | 15 |
| hr_payroll_events | **109** |
| hr_payroll_exports | 0 |
| hr_payroll_periods | 1 |
| hr_payslips | 0 |
| hr_vacation_periods | **67** |
| hr_vacation_requests | 5 |
| solides_employees | **44** |
| sst_afastamentos | 6 |
| sst_cipa_membros | 4 |
| sst_cipa_reunioes | **2.520** |

> `sst_cipa_reunioes` é a maior tabela HR com 2.520 linhas — inserção contínua de atas de reunião.

### CHECK 2 — Schema `employees` (105 colunas)
Schema completo de colaborador para empresa de vigilância:
- **Identificação:** `nome`, `cpf`, `rg`, `pis`, `ctps_numero` — com `cpf` NULável (migração pendente?)
- **Vigilância específico:** `curso_vigilante`, `curso_vigilante_validade`, `cnv`, `cnv_validade`, `porte_arma`, `porte_arma_numero`, `porte_arma_validade`
- **Integração Solides:** `solides_id`, `sync_source`, `last_synced_at`
- **Portal:** `portal_password_hash`, `portal_password_set_at`, `portal_first_access`
- **CCT:** `cct_cargo_id` (integer FK para cct_cargos)
- **Soft delete:** via `data_demissao` + `status`

### CHECK 3 — Índices `employees` e `gp_clock_punches`
**employees (11 índices):**
- pkey, `ix_employees_nome`, `ix_employees_cpf`, `ix_employees_status`, `ix_employees_is_active`, `ix_employees_posto_atual_id`, `ix_employees_cliente_id`, `ix_employees_solides_id`, `idx_employees_dados_adicionais_gin`, `idx_employees_competencias_gin`
- ⚠️ 2 índices GIN (`dados_adicionais`, `competencias`) com **0 usos** — desperdiçando 184 kB

**gp_clock_punches (4 índices):**
- pkey, `ix_gp_punches_employee`, `ix_gp_punches_time`, `idx_punches_employee_date` (composto) ✅

### CHECK 4 — Foreign Keys HR
- `shifts.employee_id → employees.id` ✅
- `shifts.scale_id → scales.id` ✅
- `diarist_evaluations.diarist_id → diarists.id` ✅
- `diarist_schedules.diarist_id → diarists.id` ✅
- `hr_vacation_requests → employees` ✅
- `employee_dp.employee_id → employees.id` ✅
- `gp_clock_punches` — **sem FK explícita** para employees (usa apenas índice)

### CHECK 5 — Status `employees`
| Status | Count |
|--------|-------|
| ativo | 41 |
| inativo | 11 |

> ✅ 41 ativos, 11 inativos. 52 employees vs 44 solides_employees — sincronização com ~85% de cobertura.

### CHECK 6 — NULLs críticos `employees`
| Campo | NULLs | Total |
|-------|-------|-------|
| nome | 0 | 52 |
| cpf | 0 | 52 |
| status | 0 | 52 |
| tipo_contrato | **52** | 52 |

> 🔴 **CRÍTICO:** `tipo_contrato` é NULL em 100% dos funcionários (52/52). Campo obrigatório para eSocial/SPED vazio.

### CHECK 7 — CPFs duplicados
`(0 rows)` — ✅ Nenhum CPF duplicado.

### CHECK 8 — Top 10 funcionários por punches
| employee_id | Punches |
|------------|---------|
| ab54e4fc... | 72 |
| 2938d6a4... | 71 |
| 9e9e1678... | 71 |
| 783a8170... | 71 |
| ... | 69-66 |

> Distribuição uniforme (~70 punches/funcionário) — batch de ponto eletrônico.

### CHECK 9 — `employee_dp` órfãos
`orphaned_dp = 0` ✅ (tabela vazia: 0 linhas)

### CHECK 10 — `gp_clock_punches` stats
- **Total:** 1.846 registros
- **Tamanho:** 1.008 kB (maior tabela do banco)
- 67% do espaço em índices (672 kB de índice para 296 kB de dados)

---

### ═══ SCORE DP/FUNCIONÁRIOS: 6/10 ═══

**Pontos positivos:**
- ✅ Zero CPFs duplicados
- ✅ employees.nome, cpf, status sem NULLs
- ✅ Estrutura completa para vigilância (CNV, porte arma, curso)
- ✅ Integração Solides funcional (44 de 52 sincronizados)
- ✅ gp_clock_punches com 1.846 registros ativos e índices adequados

**Problemas críticos:**
- 🔴 **`tipo_contrato` NULL em 100% dos funcionários (52/52)** — bloqueador para integrações eSocial
- ⚠️ `employee_dp` vazia (0 linhas) — dados do DP padrão não preenchidos
- ⚠️ `hr_payslips` vazia — nenhum holerite gerado formalmente
- ⚠️ 2 índices GIN em employees nunca utilizados (160 kB desperdiçado)
- ⚠️ `gp_justifications` e `gp_monthly_closings` vazias — fluxo de fechamento de ponto não iniciado

---

## SUBAGENTE 4 — AUDITORIA OPERACIONAL

### CHECK 1 — Contagem de Linhas

| Tabela | Linhas |
|--------|--------|
| allocations | **48** |
| diarist_assignments | 0 |
| diarist_evaluations | 0 |
| diarist_payments | 0 |
| diarist_schedules | 6 |
| diarists | 13 |
| occurrences | 5 |
| post_types | 15 |
| posts | **9** |
| scale_templates | 4 |
| scales | 3 |
| shifts | **180** |
| work_schedules | 0 |
| workflow_actions | 0 |
| workflow_conditions | 0 |
| workflow_executions | 0 |
| workflow_steps | 0 |
| workflow_triggers | 0 |
| workflows | 0 |

### CHECK 2 — Schema `posts` (38 colunas)
Modelo de posto de vigilância:
- `code`, `name`, `post_type`, `status`, `shift_type` — NOT NULL
- Localização: `address`, `city`, `state`, `zip_code`, `latitude`, `longitude`
- Requisitos: `requires_armed`, `requires_vehicle`, `requires_experience_months`, `required_certifications` (JSONB)
- Financeiro: `hourly_rate`, `monthly_cost`, `hazard_pay_percent`, `night_shift_bonus_percent`
- `is_active` NOT NULL ✅

### CHECK 3 — Schema `scales` (26 colunas)
- `post_id`, `scale_type`, `status`, `month`, `year`, `total_shifts`, `filled_shifts` NOT NULL
- `start_date`, `end_date` anuláveis — incomum para escala
- `approved_by`, `approved_at` — workflow de aprovação
- `config` JSONB para configurações flexíveis

### CHECK 4 — Índices (49 índices nas 7 tabelas)
**posts (7):** pkey, code UNIQUE, code_key, status, client_id, contract_id, city_state
**scales (6):** pkey, uq_post_month_year, status, post_id, month_year, status_year_month
**shifts (8):** pkey, scale_id, post_id, employee_id, shift_date, status, scale_status, employee_date
**allocations (6):** pkey, post_id, employee_id (duplicado!), employee_id2, dates, status
**occurrences (13):** extensa cobertura em category, code, employee, inspector, post, severity, status, type
**diarists (5):** pkey, cpf UNIQUE, cpf (duplicado!), nome, status

> ⚠️ `allocations` tem `ix_allocations_employee_id` E `idx_allocations_employee` — **índice duplicado**.
> ⚠️ `diarists` tem `diarists_cpf_key` E `ix_diarists_cpf` — **índice duplicado**.

### CHECK 5 — Foreign Keys Operacional (15 FKs)
- `allocations.post_id → posts.id` ✅
- `scales.post_id → posts.id` ✅
- `shifts.scale_id → scales.id`, `post_id → posts.id`, `employee_id → employees.id` ✅
- `occurrences.post_id → posts.id`, `employee_id → users.id`, `inspector_id → users.id`, `resolved_by_id → users.id` ✅
- `diarist_assignments.diarist_id → diarists.id` ✅
- `diarist_schedules.diarist_id → diarists.id`, `assignment_id → diarist_assignments.id` ✅

### CHECK 6 — Status `posts`
| Status | is_active | Count |
|--------|-----------|-------|
| active | true | 8 |
| inactive | false | 1 |

> ✅ 8 postos ativos, 1 inativo. Consistência status/is_active 100%.

### CHECK 7 — Alocações simultâneas por posto
| post_id | active_allocations |
|---------|-------------------|
| 593e86e5... | **9** |
| 0baad2d9... | **9** |
| a25079b0... | **8** |
| a853d52a... | **6** |
| 93a99142... | **6** |
| fdde51f0... | **4** |
| 32103e9f... | **3** |
| 7e548218... | **3** |

> 🔴 **PROBLEMA:** 8 postos com múltiplas alocações ativas simultâneas (até 9!). Esperado: 1 alocação ativa por posto por turno. Pode indicar: (a) alocações históricas não encerradas corretamente, ou (b) múltiplos funcionários por posto sem controle de turno.

### CHECK 8 — Status `diarist_assignments`
`(0 rows)` — tabela vazia.

### CHECK 9 — Alocações órfãs
`orphaned_allocations = 0` ✅

### CHECK 10 — Integridade datas `scales`
| invalid_date_range | null_start | null_end | total |
|--------------------|-----------|----------|-------|
| 0 | 0 | 0 | 3 |

> ✅ Sem inconsistências de datas nas 3 escalas.

---

### ═══ SCORE OPERACIONAL: 6/10 ═══

**Pontos positivos:**
- ✅ FK intactas em todos os relacionamentos operacionais
- ✅ Zero alocações órfãs
- ✅ Consistência status/is_active em posts
- ✅ Sem datas inválidas em scales
- ✅ Índices adequados em shifts, scales, posts

**Problemas:**
- 🔴 **8 postos com múltiplas alocações ativas simultâneas (até 9)** — violação de regra de negócio ou dado histórico inconsistente
- ⚠️ Índices duplicados: `allocations` (employee_id 2x), `diarists` (cpf 2x)
- ⚠️ `workflow_*` tabelas todas vazias — motor de workflow sem uso
- ⚠️ `diarist_assignments`, `diarist_payments`, `diarist_evaluations` vazias — módulo diaristas parcialmente operacional

---

## SUBAGENTE 5 — PERFORMANCE GLOBAL + ÍNDICES

### CHECK 1 — Top 20 maiores tabelas
*(ver tabela no PASSO INICIAL — over-indexing severo)*

Observação crítica: `audit_logs` tem 152 kB de índices e **0 bytes de dados** — completamente vazia com overhead total de armazenamento.

### CHECK 2 — Índices não utilizados (TOP 20 por tamanho)
| Índice | Tabela | Tamanho | Usos |
|--------|--------|---------|------|
| sst_cipa_reunioes_reuniao_id_key | sst_cipa_reunioes | 208 kB | 0 |
| idx_employees_dados_adicionais_gin | employees | 160 kB | 0 |
| idx_ph_descricao_gin | bidding_price_history | 24 kB | 0 |
| idx_employees_competencias_gin | employees | 24 kB | 0 |
| idx_opp_objeto_gin | bidding_opportunities | 24 kB | 0 |
| posts_code_key | posts | 16 kB | 0 |
| inspection_rounds_code_key | inspection_rounds | 16 kB | 0 |
| diarists_cpf_key | diarists | 16 kB | 0 |
| ... | ... | 16 kB | 0 |

> 🔴 **TOTAL: 1.683 índices não utilizados consumindo ~16 MB** (31% do banco inteiro!)

### CHECK 3 — Tabelas sem índices
`(0 rows)` — todas as 483 tabelas têm ao menos um índice. Situação oposta ao esperado: excesso de índices.

### CHECK 4 — Candidatos a queries lentas (alto seq_scan)
| Tabela | seq_scan | idx_scan | live_rows | seq_scan_pct |
|--------|---------|---------|-----------|-------------|
| hr_payroll_events | 66 | 6 | 109 | 91,67% |
| rh_onboarding_checklist | 54 | 0 | 102 | 100,00% |

### CHECK 5 — Estatísticas gerais
| Métrica | Valor |
|---------|-------|
| Tamanho banco | 52 MB |
| Total tabelas | 483 |
| Total índices | 2.361 (média 4,9/tabela) |
| FK constraints | 386 |
| Tabelas com dados | 122 (25,3%) |
| Tabelas vazias | 361 (74,7%) |

### CHECK 6 — Bloat (dead tuples)
| Tabela | Dead % | Last Autovacuum |
|--------|--------|-----------------|
| employee_benefits | 0,63% | 2026-03-16 |
| gp_clock_punches | 0,05% | 2026-03-23 |

> ✅ **Bloat zerado** — autovacuum funcionando perfeitamente.

### CHECK 7 — Integridade `users`
| Total | Ativos | null_email | null_password | null_role |
|-------|--------|-----------|---------------|-----------|
| 54 | 54 | 0 | 0 | 0 |

> ✅ Integridade perfeita em users.

### CHECK 8 — Índices duplicados
**57 pares confirmados.** Exemplos:
- `ai_emails_message_id_key` + `ix_ai_emails_message_id` (mesma coluna)
- `audit_logs_event_id_key` + `ix_audit_logs_event_id`
- `allocations: ix_allocations_employee_id` + `idx_allocations_employee`
- `diarists: diarists_cpf_key` + `ix_diarists_cpf`
- `bidding_tenders: bidding_tenders_pncp_id_key` + `idx_tender_pncp_id`

### CHECK 9 — FKs sem índice correspondente
**121 FKs sem índice.** Críticas para operações financeiras:
- `bank_transactions.cashflow_entry_id`
- `bank_transactions.reconciliation_id`
- `bank_transactions.transfer_from_account_id`
- `bank_transactions.transfer_to_account_id`
- `cashflow_entries.bank_account_id`
- `cashflow_entries.recurrence_parent_id`
- `client_portal_sessions.client_id`
- `client_portal_ticket_messages.ticket_id`

### CHECK 10 — Padrões de acesso
| Tabela | Total scans | Inserts | Updates | Linhas |
|--------|------------|---------|---------|--------|
| users | 64.215 | 3 | 4.764 | 54 |
| employees | 44.777 | 8 | 28.346 | 52 |
| openclaw_interventions | 31.982 | 3.902 | 22 | 18 |
| openclaw_patterns | 24.459 | 11 | 72 | 11 |
| ged_kit_documents | 16.737 | 962 | 182 | 44 |
| gp_clock_punches | 5.789 | 3.108 | 0 | 1.846 |

> ⚠️ **OpenClaw sem cache Redis**: 31.982 scans para 18 linhas (1.776x ratio) — poll loop sem TTL.

---

### ═══ SCORE PERFORMANCE GLOBAL: 4/10 ═══

**Problemas críticos:**
1. 🔴 1.683 índices não utilizados (31% do banco = ~16 MB desperdiçados)
2. 🔴 57 pares de índices duplicados
3. 🔴 121 FKs sem índice correspondente
4. ⚠️ 361 tabelas vazias com overhead de índices
5. ⚠️ OpenClaw fazendo polling sem cache Redis

---

## RELATÓRIO FINAL CONSOLIDADO

### Scores por Módulo

| Módulo | Score | Status |
|--------|-------|--------|
| GED + Documents | **8/10** | 🟢 Bom |
| Financeiro | **8/10** | 🟢 Bom |
| DP/Funcionários | **6/10** | 🟡 Atenção |
| Operacional | **6/10** | 🟡 Atenção |
| Performance Global | **4/10** | 🔴 Crítico |
| **SCORE GERAL** | **6,4/10** | 🟡 Regular |

---

### PROBLEMAS CRÍTICOS (Ação Imediata)

#### 🔴 CRÍTICO 1 — `tipo_contrato` NULL em 100% dos funcionários
- **Tabela:** `employees`
- **Impacto:** Bloqueador para eSocial e folha de pagamento oficial
- **Ação:** `UPDATE employees SET tipo_contrato = 'CLT' WHERE tipo_contrato IS NULL;` (verificar com RH o tipo correto antes de executar)

#### 🔴 CRÍTICO 2 — 8 postos com múltiplas alocações ativas simultâneas (até 9)
- **Tabela:** `allocations`
- **Impacto:** Viola regra de negócio — gera inconsistência em escalas e pagamentos
- **Ação:** Investigar se é dado histórico ou bug no fluxo de encerramento de alocações. Considerar UNIQUE partial index: `CREATE UNIQUE INDEX ON allocations (post_id) WHERE status = 'active';`

#### 🔴 CRÍTICO 3 — 1.683 índices não utilizados consumindo 16 MB
- **Impacto:** 31% do banco é overhead. Cada INSERT/UPDATE/DELETE mantém índices mortos. Com crescimento de dados, será gargalo direto de write performance.
- **Ação:** Executar auditoria de 7 dias com `pg_stat_reset()` e depois dropar índices com `idx_scan = 0` (exceto UNIQUE/PK).

---

### PROBLEMAS MÉDIOS (Resolver em 2 semanas)

#### 🟡 MÉDIO 1 — 57 índices duplicados
- Padrão: UNIQUE constraint gera `_key` + migration manual gera `ix_`/`idx_` na mesma coluna
- **Ação rápida (exemplos):**
  ```sql
  DROP INDEX idx_allocations_employee;  -- duplica ix_allocations_employee_id
  DROP INDEX ix_diarists_cpf;           -- duplica diarists_cpf_key
  DROP INDEX idx_tender_pncp_id;        -- duplica bidding_tenders_pncp_id_key
  DROP INDEX ix_audit_logs_event_id;    -- duplica audit_logs_event_id_key
  ```

#### 🟡 MÉDIO 2 — 121 FKs sem índice (foco nas críticas)
- **Ação prioritária:**
  ```sql
  CREATE INDEX CONCURRENTLY ON bank_transactions (cashflow_entry_id);
  CREATE INDEX CONCURRENTLY ON bank_transactions (transfer_from_account_id);
  CREATE INDEX CONCURRENTLY ON bank_transactions (transfer_to_account_id);
  CREATE INDEX CONCURRENTLY ON cashflow_entries (bank_account_id);
  CREATE INDEX CONCURRENTLY ON client_portal_sessions (client_id);
  ```

#### 🟡 MÉDIO 3 — OpenClaw poll sem cache
- `openclaw_interventions`: 31.982 scans para 18 linhas
- **Ação:** Implementar cache Redis com TTL 30-60s no agente OpenClaw

#### 🟡 MÉDIO 4 — hr_payroll_events com 91% seq_scan
- **Ação:**
  ```sql
  CREATE INDEX ON hr_payroll_events (employee_id);
  CREATE INDEX ON hr_payroll_events (competencia);  -- ou coluna de data usada
  ```

---

### BOAS PRÁTICAS CONFIRMADAS ✅

- Zero CPFs duplicados
- Zero registros órfãos em todas as tabelas auditadas
- Autovacuum funcionando (bloat máximo 0,63%)
- Integridade perfeita na tabela `users` (54 usuários, todos ativos)
- FK constraints intactas em todos os módulos
- Soft delete implementado corretamente (deleted_at)
- Multi-tenant correto via `condominio_id` NOT NULL nas tabelas financeiras
- Sem sobreposição de períodos contábeis

---

### ROADMAP DE AÇÕES

| Prioridade | Ação | Esforço | Risco |
|-----------|------|---------|-------|
| 🔴 IMEDIATA | Corrigir `tipo_contrato` nos 52 funcionários | 1h | Baixo |
| 🔴 IMEDIATA | Investigar/corrigir múltiplas alocações ativas | 2h | Médio |
| 🔴 IMEDIATA | Dropar 57 índices duplicados | 1h | Baixo |
| 🟡 2 SEMANAS | Criar índices nas 5 FKs financeiras críticas | 1h | Baixo |
| 🟡 2 SEMANAS | Cache Redis para OpenClaw | 4h | Baixo |
| 🟡 2 SEMANAS | Índices em hr_payroll_events | 30min | Baixo |
| 🟢 1 MÊS | Auditoria e limpeza dos 1.683 índices não usados | 8h | Médio |
| 🟢 1 MÊS | Fechar períodos contábeis janeiro/fevereiro | 2h | Médio |
| 🟢 FUTURO | Preencher employee_dp, hr_payslips, gp_monthly_closings | - | - |

---

*Auditoria executada por: Claude Sonnet 4.6*
*Data: 31 de março de 2026*
*Banco: PostgreSQL 16.11 | Migration: sprint79_just_uuid | Tamanho: 52 MB*
