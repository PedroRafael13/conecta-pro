# CPRO11 — Reconhecimento Backend: Menu Negócios
**Data:** 2026-04-20
**Analista:** Claude Code (tmux-t4)
**Escopo:** CRM · Vendas · Marketing · Licitações
**Branch:** feature/people-management-reorganization

---

## STEP 1 — Descoberta de Estrutura

```bash
find /opt/conecta-pro/backend -type f \( -name "*.py" \) \
  | xargs grep -l -iE "(crm|vendas|sales|marketing|licit|bidding|lead|opportunity|pipeline|campaign|propos|pricing|precific)" 2>/dev/null
```

**Resultado — arquivos .py que referenciam os 4 módulos (seleção relevante, 300+ total):**

```
# Módulo CRM (modules/crm/)
modules/crm/__init__.py
modules/crm/publishers.py
modules/crm/controllers/client_controller.py
modules/crm/controllers/commission_controller.py
modules/crm/controllers/contact_controller.py
modules/crm/controllers/contract_controller.py
modules/crm/controllers/dashboard_controller.py
modules/crm/controllers/lead_controller.py
modules/crm/controllers/marketing_controller.py
modules/crm/controllers/opportunity_controller.py
modules/crm/controllers/proposal_controller.py
modules/crm/models/commission.py
modules/crm/models/contract.py
modules/crm/models/lead.py
modules/crm/models/opportunity.py
modules/crm/models/proposal.py
modules/crm/repositories/commission_repository.py
modules/crm/repositories/contract_repository.py
modules/crm/repositories/lead_repository.py
modules/crm/repositories/opportunity_repository.py
modules/crm/repositories/proposal_repository.py
modules/crm/schemas/commission.py
modules/crm/schemas/contract.py
modules/crm/schemas/lead.py
modules/crm/schemas/opportunity.py
modules/crm/schemas/proposal.py
modules/crm/services/commission_service.py
modules/crm/services/contract_service.py
modules/crm/services/crm_360_service.py
modules/crm/services/dashboard_service.py
modules/crm/services/lead_service.py
modules/crm/services/pdf_generator.py
modules/crm/services/pipeline_service.py
modules/crm/services/pricing_engine.py
modules/crm/services/proposal_service.py
modules/crm/services/signature_integration.py

# Módulo Licitações (modules/bidding/)
modules/bidding/__init__.py
modules/bidding/router.py
modules/bidding/agents/{orchestrator,scout,analyst,assessor,pricer,compiler,sentinel,warrior,pdf_renderer}.py
modules/bidding/controllers/{agent,certificate,contract,dispute,document,erp,opportunity,proposal,sync,tender}_controller.py
modules/bidding/integrations/{pncp,comprasnet,licitacoes_e,ecompras_am,bll,portal_compras_publicas,receita_federal}/*.py
modules/bidding/models/{analysis,assessment,certificate,company_document,dispute,measurement,opportunity,price_history,pricing,proposal,public_contract,sync_job,tender}.py
modules/bidding/repositories/{contract,document,proposal,tender}_repository.py
modules/bidding/schemas/{analysis,assessment,certificate,contract,dispute,document,opportunity,pipeline,pricing,proposal,tender}.py
modules/bidding/services/{certificate,contract,document,edital_parser,erp_integration,notification,opportunity,pncp,pricing,proposal,sync,tender}_service.py
modules/bidding/tasks/{dispute_tasks,notification_tasks,sync_tasks}.py
modules/bidding/websockets/dispute_ws.py

# Módulo Comercial (stub)
modules/comercial/__init__.py  (único arquivo não-vazio relevante)

# Outros arquivos que referenciam o domínio (analytics, AI, automation)
modules/analytics/models/scoring/lead_scorer.py
modules/analytics/models/forecasting/sales_forecaster.py
modules/ai/contract_analysis/services/{clause_extractor,compliance_checker,risk_analyzer}.py
modules/ai/conversation/services/intent_classifier.py
modules/automation/workflow/services/workflow_engine.py
celery_app.py
infrastructure/event_bus/bus.py
infrastructure/message_bus/events.py
main_production.py
alembic/versions/{7017a3795753,1ab7727d6644,d32dc56bebba,e5f7a8b9c0d1,f6g8h9i0j1k2,bidding_module_tables,sprint14,sprint44,sprint66,sprint71,sprint72}.py
```

---

## 1. CRM (`modules/crm/`)

### 1.1 Models

#### Tabela `leads` — `models/lead.py`

| Coluna | Tipo SQLAlchemy | Nullable | Default | FK |
|--------|----------------|----------|---------|-----|
| id | UUID | NO | gen_random_uuid() | — |
| name | String(255) | NO | — | — |
| email | String(255) | YES | — | — |
| phone | String(20) | YES | — | — |
| company | String(255) | YES | — | — |
| position | String(100) | YES | — | — |
| company_size | String(50) | YES | — | — |
| industry | String(100) | YES | — | — |
| source | Enum(LeadSource) | NO | 'other' | — |
| status | Enum(LeadStatus) | NO | 'novo' | — |
| score | Integer | NO | 0 | — |
| probability | Float | NO | 0.0 | — |
| expected_value | Float | NO | 0.0 | — |
| notes | Text | YES | — | — |
| assigned_to_id | UUID | YES | — | FK→users.id |
| last_contact_at | DateTime | YES | — | — |
| next_contact_at | DateTime | YES | — | — |
| is_active | Boolean | NO | True | — |
| created_at | DateTime | NO | now() | — |
| updated_at | DateTime | NO | now() | — |

**Enums:**
- `LeadSource`: website, referral, cold_call, email, social_media, event, other
- `LeadStatus`: novo, qualificado, em_contato, proposta, ganho, perdido

**Relacionamentos:**
```python
assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
```

**Properties:** `is_hot` (score≥70), `is_qualified` (status=qualificado), `weighted_value` (expected_value × probability)

---

#### Tabela `opportunities` — `models/opportunity.py`

| Coluna | Tipo | Nullable | Default | FK |
|--------|------|----------|---------|-----|
| id | UUID | NO | gen() | — |
| title | String(255) | NO | — | — |
| description | Text | YES | — | — |
| lead_id | UUID | YES | — | FK→leads.id |
| contact_name | String(255) | NO | — | — |
| contact_email | String(255) | NO | — | — |
| contact_phone | String(20) | YES | — | — |
| company_name | String(255) | YES | — | — |
| stage | Enum(OpportunityStage) | NO | QUALIFICATION | — |
| priority | Enum(OpportunityPriority) | NO | MEDIUM | — |
| value | Float | NO | 0.0 | — |
| probability | Integer | NO | 10 | — |
| expected_close_date | Date | YES | — | — |
| actual_close_date | Date | YES | — | — |
| owner_id | UUID | YES | — | FK→users.id |
| loss_reason | Enum(LossReason) | YES | — | — |
| competitor | String(255) | YES | — | — |
| win_notes / loss_notes | Text | YES | — | — |
| is_active | Boolean | NO | True | — |

**Relacionamentos:**
```python
lead: Mapped[Optional["Lead"]] = relationship("Lead", foreign_keys=[lead_id])
owner: Mapped[Optional["User"]] = relationship("User", foreign_keys=[owner_id])
```

**Properties:** `weighted_value`, `is_open`, `is_won`, `is_lost`, `days_in_pipeline`, `is_overdue`

---

#### Tabelas `proposals`, `proposal_items`, `proposal_templates`, `proposal_approvals` — `models/proposal.py`

**`proposals`:**
- Status (10): draft, sent, viewed, approved, accepted, rejected, expired, cancelled, revision_requested, under_revision
- Versioning: `parent_id` FK self-ref

**Relacionamentos:**
```python
items     = relationship("ProposalItem",    back_populates="proposal", cascade="all, delete-orphan")
versions  = relationship("Proposal",        backref="parent", remote_side=[id])
approvals = relationship("ProposalApproval",back_populates="proposal", cascade="all, delete-orphan")
# ProposalItem → proposal = relationship("Proposal", back_populates="items")
# ProposalApproval → proposal = relationship("Proposal", back_populates="approvals")
```

---

#### Tabelas `contracts`, `contract_items`, `contract_addendums`, `contract_templates`, `contract_sla_reports`

**Relacionamentos:**
```python
template  = relationship("ContractTemplate", back_populates="contracts")
items     = relationship("ContractItem",     back_populates="contract", cascade="all, delete-orphan")
addendums = relationship("ContractAddendum", back_populates="contract", cascade="all, delete-orphan")
sla_reports = relationship("ContractSLAReport", back_populates="contract", cascade="all, delete-orphan")
# ContractTemplate → contracts = relationship("Contract", back_populates="template")
# ContractItem    → contract  = relationship("Contract", back_populates="items")
# ContractAddendum→ contract  = relationship("Contract", back_populates="addendums")
```

---

#### Tabelas `commission_rules`, `seller_commission_rules`, `commissions`, `commission_payments`, `commission_summaries`

**Relacionamentos:**
```python
# CommissionRule:
commissions  = relationship("Commission",           back_populates="rule")
seller_rules = relationship("SellerCommissionRule", back_populates="rule")
# SellerCommissionRule:
rule = relationship("CommissionRule", back_populates="seller_rules")
# Commission:
rule     = relationship("CommissionRule",    back_populates="commissions")
payments = relationship("CommissionPayment", back_populates="commission", cascade="all, delete-orphan")
# CommissionPayment:
commission = relationship("Commission", back_populates="payments")
```

---

### 1.2 Schemas (Pydantic v2)

#### `schemas/lead.py`

**Validators:**
```python
@field_validator("phone")
def validate_phone(cls, v) -> str | None:
    # Remove non-digits; requer 10–15 dígitos
    digits = "".join(c for c in v if c.isdigit())
    if len(digits) < 10 or len(digits) > 15:
        raise ValueError("Telefone deve ter entre 10 e 15 dígitos")
```

**Schemas e campos:**

| Schema | Campos principais |
|--------|------------------|
| `LeadBase` | name (str, min=2, max=255), email (EmailStr), phone (max=20), company, position, company_size, industry, source (LeadSource), notes |
| `LeadCreate` | +assigned_to_id, expected_value (float, ge=0) |
| `LeadUpdate` | Todos opcionais + status, next_contact_at |
| `LeadResponse` | id, name, email, phone, company, position, company_size, industry, source, status, score, probability, expected_value, notes, assigned_to_id, last_contact_at, next_contact_at, is_active, created_at, updated_at |
| `LeadStats` | total, by_status (dict), by_source (dict), avg_score, total_value |

---

#### `schemas/opportunity.py`

| Schema | Campos principais |
|--------|------------------|
| `OpportunityBase` | title (min=1, max=255), description, contact_name, contact_email (EmailStr), contact_phone, company_name, value (float, ge=0), probability (int, ge=0, le=100), expected_close_date |
| `OpportunityCreate` | +lead_id, stage (default=QUALIFICATION), priority (default=MEDIUM), owner_id |
| `OpportunityCreateFromLead` | lead_id, title, description, value, probability (default=20), expected_close_date, priority, owner_id |
| `OpportunityUpdate` | Todos opcionais |
| `OpportunityResponse` | id + todos os campos + weighted_value, is_open, is_overdue, days_in_pipeline |
| `PipelineStats` | total_value, weighted_value, by_stage (dict), win_rate, avg_deal_size |
| `OpportunityClose` | won (bool), loss_reason, loss_notes, win_notes, actual_close_date |

---

#### `schemas/proposal.py`

| Schema | Campos principais |
|--------|------------------|
| `ProposalCreate` | opportunity_id, title, type, description, valid_until (date), payment_terms, installments (int, ge=1, le=120), notes |
| `ProposalItemCreate` | description, quantity (float, gt=0), unit_price (float, ge=0), discount_percent (float, ge=0, le=100) |
| `ProposalTemplateCreate` | name, type, content (text) |
| `ApprovalCreate` | approver_id, notes |
| `ProposalResponse` | id, status, subtotal, discount_value, tax_value, total, items[], approvals[], created_at, viewed_at, responded_at |

---

#### `schemas/contract.py`

| Schema | Campos |
|--------|--------|
| `ContractCreate` | proposal_id, type (RECURRING/ONE_TIME), start_date, end_date, value, adjustment_index, service_type, notes |
| `ContractItem` | description, quantity, unit_price |
| `ContractAddendum` | type, effective_date, value_before, value_after, description |
| `AdjustmentResult` | old_value, new_value, adjustment_percent, index_used, reference_date |
| `RenewalResult` | old_contract_id, new_contract_id, new_end_date |
| `ContractAlert` | contract_id, type (expiring/review/adjustment), days_until, message |
| `ContractStats` | total_active, total_value, by_type (dict), expiring_30d, expiring_90d |

---

#### `schemas/commission.py`

| Schema | Campos |
|--------|--------|
| `CommissionRuleCreate` | name, type, percentage (float, ge=0, le=100), base_amount, service_type, min_value, max_value |
| `CommissionCreate` | rule_id, reference_id, reference_type, base_value, notes |
| `CommissionStats` | total_pending, total_approved, total_paid, by_seller (dict) |
| `CommissionSummaryResponse` | seller_id, year, month, total_commissions, total_value, status |

---

### 1.3 Routers / Endpoints

**Prefix base:** `/api/v1/crm` | **Auth:** `CurrentActiveUser` (JWT Bearer) | **Tags:** CRM

#### `/leads`
| Método | Path | Função | Response Model |
|--------|------|--------|----------------|
| POST | `/` | create_lead | LeadResponse (201) |
| GET | `/` | list_leads | LeadListResponse |
| GET | `/stats` | get_lead_stats | LeadStats |
| GET | `/{id}` | get_lead | LeadResponse |
| PUT | `/{id}` | update_lead | LeadResponse |
| PATCH | `/{id}/status` | update_lead_status | LeadResponse |
| POST | `/{id}/recalculate-score` | recalculate_score | LeadResponse |
| GET | `/{id}/recommended-action` | get_recommended_action | dict |
| DELETE | `/{id}` | delete_lead | 204 |

#### `/opportunities`
| Método | Path | Função | Response Model |
|--------|------|--------|----------------|
| POST | `/` | create_opportunity | OpportunityResponse (201) |
| POST | `/from-lead` | create_from_lead | OpportunityResponse (201) |
| GET | `/` | list_opportunities | OpportunityListResponse |
| GET | `/pipeline/stats` | get_pipeline_stats | PipelineStats |
| GET | `/{id}` | get_opportunity | OpportunityResponse |
| PUT | `/{id}` | update_opportunity | OpportunityResponse |
| PATCH | `/{id}/stage` | update_stage | OpportunityResponse |
| POST | `/{id}/close` | close_opportunity | OpportunityResponse (201) |
| DELETE | `/{id}` | delete_opportunity | 204 |

#### `/proposals`
| Método | Path | Função | Response Model |
|--------|------|--------|----------------|
| POST | `/` | create_proposal | ProposalResponse (201) |
| POST | `/from-opportunity` | create_from_opportunity | ProposalResponse (201) |
| GET | `/` | list_proposals | ProposalListResponse |
| GET | `/templates` | list_templates | list[ProposalTemplateResponse] |
| POST | `/templates` | create_template | ProposalTemplateResponse (201) |
| GET | `/{id}` | get_proposal | ProposalResponse |
| PUT | `/{id}` | update_proposal | ProposalResponse |
| PATCH | `/{id}/status` | update_status | ProposalResponse |
| POST | `/{id}/approve` | approve_proposal | ProposalResponse (201) |
| POST | `/{id}/send` | send_proposal | ProposalResponse (201) |
| DELETE | `/{id}` | delete_proposal | 204 |

#### `/contracts`
| Método | Path | Função | Response Model |
|--------|------|--------|----------------|
| POST | `` | create_contract | ContractDetailResponse (201) |
| GET | `` | list_contracts | ContractListResponse |
| GET | `/stats` | get_stats | ContractStats |
| GET | `/alerts` | get_alerts | list[ContractAlert] |
| GET | `/templates` | list_templates | ContractTemplateListResponse |
| GET | `/{id}` | get_contract | ContractDetailResponse |
| PUT | `/{id}` | update_contract | ContractDetailResponse |
| DELETE | `/{id}` | delete_contract | 204 |
| POST | `/{id}/submit` | submit_for_signature | ContractResponse (201) |
| POST | `/{id}/activate` | activate_contract | ContractResponse (201) |
| POST | `/{id}/suspend` | suspend_contract | ContractResponse (201) |
| POST | `/{id}/terminate` | terminate_contract | ContractResponse (201) |
| POST | `/{id}/renew` | renew_contract | RenewalResult (201) |
| POST | `/{id}/calculate-adjustment` | calculate_adjustment | AdjustmentResult (201) |
| POST | `/{id}/addendums` | create_addendum | ContractAddendumResponse (201) |
| GET | `/{id}/addendums` | list_addendums | list[ContractAddendumResponse] |
| POST | `/{id}/items` | add_item | ContractItemResponse (201) |
| PUT | `/{id}/items/{item_id}` | update_item | ContractItemResponse |
| DELETE | `/{id}/items/{item_id}` | delete_item | 204 |

#### `/commissions`
| Método | Path | Função | Response Model |
|--------|------|--------|----------------|
| POST | `/rules` | create_rule | CommissionRuleResponse (201) |
| GET | `/rules` | list_rules | CommissionRuleListResponse |
| GET | `/rules/{id}` | get_rule | CommissionRuleResponse |
| PUT | `/rules/{id}` | update_rule | CommissionRuleResponse |
| DELETE | `/rules/{id}` | delete_rule | 204 |
| POST | `/calculate` | calculate | CommissionResponse (201) |
| GET | `` | list_commissions | CommissionListResponse |
| GET | `/stats` | get_stats | CommissionStats |
| GET | `/seller/{id}/stats` | seller_stats | SellerCommissionStats |
| GET | `/summaries` | list_summaries | list[CommissionSummaryResponse] |
| POST | `/summaries/{seller_id}/{year}/{month}/close` | close_month | CommissionSummaryResponse (201) |
| GET | `/{id}` | get_commission | CommissionDetailResponse |
| PUT | `/{id}` | update_commission | CommissionResponse |
| PATCH | `/{id}/status` | update_status | CommissionResponse |
| POST | `/{id}/approve` | approve | CommissionResponse (201) |
| DELETE | `/{id}` | delete_commission | 204 |

**OpenAPI curl:**
```bash
curl -s http://127.0.0.1:8080/openapi.json | jq '.paths | ...'
# → API indisponível em tempo de reconhecimento. Dados obtidos via inspeção de código-fonte.
```

---

### 1.4 Services

| Classe | Arquivo | Métodos principais |
|--------|---------|-------------------|
| `PricingEngine` | `pricing_engine.py` | `calculate(base_salary, headcount, contract_months, service_type, client_state, margin_target) → PricingResult` (14 campos: custo_mao_obra, encargos_sociais, iss_aliquota, iss_valor, margem_reais, margem_percentual, valor_total, valor_hora, valor_posto_mes, ...) |
| `PipelineService` | `pipeline_service.py` | `calculate_weighted_pipeline() → float`, `calculate_win_rate(period_days=90) → float`. STAGE_PROBABILITIES: {qualification:10%, needs_analysis:25%, proposal:50%, negotiation:75%, closed_won:100%} |
| `CRM360Service` | `crm_360_service.py` | Customer journey, RFM segmentation. CustomerSegment: VIP/PREMIUM/STANDARD/BRONZE/PROSPECT/CHURNING/INACTIVE. InteractionType: EMAIL/PHONE/WHATSAPP/PORTAL/MOBILE_APP/FACE_TO_FACE/SYSTEM/SOCIAL_MEDIA |
| `SignatureIntegration` | `signature_integration.py` | `request_signature(contract_id, provider) → SignatureRequest`. SignatureProvider: INTERNAL/DOCUSIGN/CLICKSIGN/D4SIGN/AUTENTIQUE |
| `PDFGenerator` | `pdf_generator.py` | `generate_proposal_pdf(proposal_id) → bytes`, `generate_contract_pdf(contract_id) → bytes` |
| `DashboardService` | `dashboard_service.py` | `get_metrics(period) → DashboardMetrics` |
| `ProposalService` | `proposal_service.py` | `create()`, `approve()`, `send()`, `create_version()`, `get_history()` |
| `ContractService` | `contract_service.py` | `renew()`, `calculate_adjustment(index)`, `activate()`, `terminate()` |
| `LeadService` | `lead_service.py` | `recalculate_score(lead_id)`, `get_recommended_action(lead_id) → str` |
| `CommissionService` | `commission_service.py` | `calculate(rule_id, base_value)`, `approve(commission_id)`, `close_month(seller_id, year, month)` |

---

### 1.5 Agentes IA

**CRM não possui agentes de IA dedicados.**

- `GET /leads/{id}/recommended-action` → lógica heurística em `lead_service.py` (score + status + dias sem contato) — sem LLM
- `modules/analytics/models/scoring/lead_scorer.py` — ML model para lead scoring (scikit-learn, não LLM)
- `modules/analytics/models/forecasting/sales_forecaster.py` — previsão de vendas (scikit-learn)
- `modules/ai/contract_analysis/` — análise de cláusulas contratuais (Claude/OpenAI) — módulo AI separado, não integrado diretamente no CRM

**Tasks Celery no CRM:** Nenhuma.

---

### 1.6 Integrações

| Integração | Status | Detalhes |
|-----------|--------|----------|
| DocuSign | Configurável | `signature_integration.py`, `SignatureProvider.DOCUSIGN` |
| ClickSign | Configurável | `SignatureProvider.CLICKSIGN` |
| D4Sign | Configurável | `SignatureProvider.D4SIGN` |
| Autentique | Configurável | `SignatureProvider.AUTENTIQUE` |
| Assinatura Interna | Ativo (padrão) | `SignatureProvider.INTERNAL` |
| Banco Inter | **Não no CRM** | Módulo `financial/` + webhooks em `main_production.py:1039` |
| WhatsApp | Campo apenas | `whatsapp` é campo de contato/lead; sem envio via API no CRM |
| SMTP | Global (`core/mailer.py`) | Não usado diretamente no CRM |
| Solides | **Não no CRM** | Integração de RH (`sprint33_solides_integration`) |
| Event Bus | ✅ Ativo | `publishers.py` → `CRM_LEAD_CONVERTIDO`, `CRM_PROPOSTA_APROVADA`, `CRM_CONTRATO_ATIVO` → GEDEON |

---

### 1.7 Migrations Recentes

| Arquivo | revision | down_revision | Create Date |
|---------|----------|---------------|------------|
| `7017a3795753_create_leads_table.py` | `7017a3795753` | `14f6c2c7eaa2` | 2025-12-30 03:23 |
| `1ab7727d6644_create_opportunities_table.py` | `1ab7727d6644` | `7017a3795753` | 2025-12-30 03:47 |
| `d32dc56bebba_create_proposal_tables.py` | `d32dc56bebba` | `1ab7727d6644` | 2025-12-30 04:09 |
| `e5f7a8b9c0d1_create_commission_tables.py` | `e5f7a8b9c0d1` | `d32dc56bebba` | 2025-12-30 05:00 |
| `f6g8h9i0j1k2_create_contract_tables.py` | `f6g8h9i0j1k2` | `e5f7a8b9c0d1` | 2025-12-30 08:00 |
| `sprint14_proposals_cpq_premium.py` | `sprint14_cpq` | `sprint07_workflow_engine` | 2026-01-07 |
| `sprint36_fix_float_to_numeric.py` | `sprint36_float_fix` | — | — |
| `sprint44_create_contract_analysis_tables.py` | `sprint44_contract_analysis` | `sprint43_inventory_forecast` | 2025-01-05 |
| `sprint66_add_contract_costs.py` | `sprint66_add_contract_costs` | `sprint65_fix_charts_of_accounts` | 2026-03-09 |

---

### 1.8 Testes

**Localização:** `tests/modules/crm/`
**Total:** 17 arquivos · **225 funções de teste**

| Arquivo | Funções |
|---------|---------|
| `test_controllers_lead_opp_proposal_dashboard.py` | Controllers leads/opp/propostas |
| `test_controllers_commission_contract.py` | Controllers comissões/contratos |
| `test_e2e_leads_opportunities.py` | E2E: lead → qualificação → oportunidade |
| `test_e2e_proposals.py` | E2E: oportunidade → proposta → aprovação |
| `test_e2e_contracts.py` | E2E: proposta → contrato → ativação |
| `test_e2e_commissions.py` | E2E: venda → comissão → pagamento |
| `test_e2e_dashboard_clients_contacts_marketing.py` | Dashboard + clientes + marketing E2E |
| `test_pricing_engine.py` | PricingEngine (CCT + ISS + margem) |
| `test_proposal_model.py` | Model proposal (state machine) |
| `test_proposal_service.py` | ProposalService |
| `test_repositories_lead_opp_commission.py` | Repositórios |
| `test_repositories_proposal_contract.py` | Repositórios |
| `test_crm_marketing_vendas.py` | Integração marketing/vendas |
| `test_coverage_gaps_controllers.py` | Gaps de cobertura |
| `test_coverage_gaps_models.py` | Gaps de cobertura |
| `test_coverage_final.py` | Cobertura final |
| `test_services_remaining.py` | Services restantes |

**Cobertura estimada:** Alta — E2E completo do pipeline leads→contratos. Zero TODOs no código.

---

### 1.9 TODOs / Pendências

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" modules/crm --include="*.py"
# Resultado: NENHUM
```

**Pendências identificadas por análise (não marcadas no código):**
- Sem automação de e-mail transacional (proposta enviada, contrato assinado)
- Sem agente IA nativo (recommended-action é heurística, não LLM)
- `modules/comercial/` deveria ser a camada de Vendas mas está vazia

---

## 2. Vendas (`modules/comercial/`)

### 2.1 Models
Nenhum. Apenas `__init__.py` vazio.

### 2.2 Schemas
Nenhum.

### 2.3 Routers / Endpoints
Nenhum. Módulo não registrado em `main_production.py`.

### 2.4 Services
Nenhum.

### 2.5 Agentes IA
Nenhum.

### 2.6 Integrações
Nenhuma.

### 2.7 Migrations Recentes
Nenhuma migration referencia `modules/comercial/`.

### 2.8 Testes
Nenhum teste existe.

### 2.9 TODOs / Pendências

**Status: STUB VAZIO — 100% não implementado.**

```
modules/comercial/
├── __init__.py          (vazio)
├── atividades/          (vazio)
├── clientes/            (vazio)
├── comissoes/           (vazio)
├── contratos/           (vazio)
├── leads/               (vazio)
├── metas/               (vazio)
├── oportunidades/       (vazio)
└── propostas/           (vazio)
```

Toda lógica de Vendas está atualmente em `modules/crm/`. A decisão arquitetural de separar está pendente.

---

## 3. Marketing (`modules/crm/controllers/marketing_controller.py`)

### 3.1 Models

Marketing não possui ORM model dedicado — usa `sqlalchemy.text()` (raw SQL). As tabelas existem no banco mas sem classe SQLAlchemy.

**Tabela `marketing_campaigns`** (inferida do SQL):

| Coluna | Tipo | Nullable |
|--------|------|----------|
| id | UUID | NO |
| name | str | NO |
| type | str | NO (organic/paid/email/social) |
| budget | float | NO (default=0) |
| description | text | YES |
| start_date | date | YES |
| end_date | date | YES |
| utm_source | str | YES |
| utm_medium | str | YES |
| utm_campaign | str | YES |
| created_at | datetime | NO |

**Tabela `marketing_leads`** (inferida do SQL):

| Coluna | Tipo | Nullable | FK |
|--------|------|----------|----|
| id | UUID | NO | — |
| campaign_id | UUID | YES | FK→marketing_campaigns.id |
| name | str | NO | — |
| email | str | YES | — |
| phone | str | YES | — |
| whatsapp | str | YES | — |
| source | str | YES | — |
| status | str | NO (novo/converted) | — |
| created_at | datetime | NO | — |

**Relacionamentos ORM:** Nenhum (sem ORM model).

---

### 3.2 Schemas

Inline no controller via `pydantic.BaseModel` (sem arquivo em `schemas/`):

```python
class CampaignCreate(BaseModel):
    name: str
    type: str = "organic"
    budget: float = 0
    description: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None

class MktLeadCreate(BaseModel):
    campaign_id: str | None = None
    name: str
    email: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    source: str | None = None
```

**Validators:** Nenhum — sem validação de tipos, formatos ou campos obrigatórios além do `name`.

---

### 3.3 Routers / Endpoints

**Prefix:** `/api/v1/crm/marketing` | **Auth:** `CurrentActiveUser` | **Tags:** Marketing

| Método | Path | Função | Response |
|--------|------|--------|----------|
| GET | `/campaigns/` | `listar_campanhas` | list (total_leads + converted inclusos) |
| POST | `/campaigns/` | `criar_campanha` | dict (201) |
| PUT | `/campaigns/{id}` | `atualizar_campanha` | dict |
| GET | `/leads/` | `listar_leads_mkt` | list |
| POST | `/leads/` | `criar_lead_mkt` | dict (201) |
| POST | `/leads/{id}/convert` | `converter_lead_mkt` | dict (201) — cria Lead CRM |
| GET | `/leads/stats` | `stats_leads_mkt` | dict (totais, taxa conversão) |
| POST | `/licitacao/convert-to-crm` | `converter_licitacao_crm` | dict (201) |

---

### 3.4 Services

Nenhum service layer. Lógica inline no controller via raw SQL.

---

### 3.5 Agentes IA

Nenhum agente de IA para Marketing. Sem automação de campanhas ou segmentação automática.

---

### 3.6 Integrações

| Integração | Status | Detalhes |
|-----------|--------|----------|
| WhatsApp (campo) | Armazenamento | `whatsapp` é campo de dado nos leads; sem envio via API no marketing |
| WhatsApp Business API | Módulo separado | `whatsapp_router` registrado em `main_production.py:929` (Evolution API) — sem integração com campanhas |
| SMTP | Global | `core/mailer.py` (smtplib, settings.SMTP_*) — **não usado diretamente pelo marketing controller** |
| SendGrid / Mailgun | Schema criado | Enum em `sprint36_create_notification_hub_tables` (valores: smtp, sendgrid, mailgun) — sem implementação no marketing |
| UTM tracking | Implementado | utm_source, utm_medium, utm_campaign nos campos de campanha |
| Banco Inter | Não aplicável | Módulo financeiro |
| Solides | Não aplicável | Integração de RH |
| Certificado A1 | Não aplicável | Portais de licitação |

---

### 3.7 Migrations Recentes

Marketing usa raw SQL — **sem migrations rastreáveis para `marketing_campaigns` / `marketing_leads`**.

---

### 3.8 Testes

Sem arquivo dedicado. Inclusos em:
- `tests/modules/crm/test_crm_marketing_vendas.py`
- `tests/modules/crm/test_e2e_dashboard_clients_contacts_marketing.py`

**Cobertura estimada:** Baixa — sem testes unitários para as campanhas ou conversão de leads.

---

### 3.9 TODOs / Pendências

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" modules/crm/controllers/marketing_controller.py
# Resultado: NENHUM
```

**Pendências identificadas:**
1. Sem ORM model — tabelas sem type safety
2. Sem migrations rastreáveis
3. Sem e-mail marketing real (SendGrid/Mailgun não implementados)
4. WhatsApp Business API não integrado a campanhas
5. Sem automação de disparo agendado
6. Sem A/B testing
7. Sem métricas de ROI por campanha
8. Validators ausentes nos schemas inline

---

## 4. Licitações (`modules/bidding/`)

### 4.1 Models

#### Tabela `bidding_tenders` — `models/tender.py`

| Coluna | Tipo | Nullable | Default | FK |
|--------|------|----------|---------|-----|
| id | UUID | NO | gen() | — |
| pncp_id | String(255) | NO | — | UNIQUE |
| numero_controle | String(255) | YES | — | — |
| modalidade | Enum(11) | NO | — | — |
| criterio_julgamento | Enum(6) | YES | — | — |
| status | Enum(11) | NO | publicado | — |
| orgao_cnpj | String(14) | NO | — | — |
| orgao_nome | String(500) | YES | — | — |
| orgao_uf | String(2) | NO | — | — |
| segmento | String(100) | YES | — | — |
| objeto | Text | NO | — | — |
| valor_estimado | Numeric(15,2) | YES | — | — |
| data_publicacao | DateTime | YES | — | — |
| data_abertura | DateTime | YES | — | — |
| data_encerramento | DateTime | YES | — | — |
| ano | Integer | YES | — | — |
| participando | Boolean | NO | False | — |
| interesse | Boolean | NO | False | — |
| tags | JSONB | YES | {} | — |
| requisitos | JSONB | YES | {} | — |
| is_active | Boolean | NO | True | — |

**Relacionamentos:**
```python
documentos = relationship("TenderDocument",  back_populates="tender", cascade="all, delete-orphan")
propostas  = relationship("BiddingProposal", back_populates="tender")
contratos  = relationship("PublicContract",  back_populates="tender")
# TenderDocument → tender = relationship("Tender", back_populates="documentos")
```

**Índices compostos:** (orgao_cnpj, ano), (modalidade, status), (orgao_uf, segmento), (participando, status)

**Enums:**
- `modalidade` (11): pregao_eletronico, concorrencia, dispensa, inexigibilidade, credenciamento, leilao, dialogo_competitivo, pre_qualificacao, manifestacao_intencao, registro_preco, outros
- `status` (11): publicado, aberto, suspenso, encerrado, homologado, revogado, anulado, fracassado, deserto, em_recurso, em_andamento

#### Outros models:
- `models/proposal.py` → `bidding_proposals` + `bidding_proposal_items`: BDI, historico_lances (JSONB), encargos_sociais. Rel: `tender = relationship("Tender", back_populates="propostas")`
- `models/analysis.py` → AnalysisResult (resultado Claude AI)
- `models/assessment.py` → Assessment (avaliação habilitação)
- `models/certificate.py` → certidões com validade
- `models/company_document.py` → docs da empresa
- `models/dispute.py` → sessão pregão
- `models/measurement.py` → medições de contrato
- `models/price_history.py` → histórico preços PNCP
- `models/pricing.py` → resultado BDI
- `models/public_contract.py` → contrato licitação ganha
- `models/sync_job.py` → jobs de sync

---

### 4.2 Schemas

| Arquivo | Campos / Validators |
|---------|---------------------|
| `schemas/tender.py` | TenderCreate (pncp_id, modalidade, objeto, valor_estimado, orgao_cnpj, orgao_uf), TenderResponse, TenderFilter (modalidade, status, uf, segmento, valor_min/max, apenas_abertos) |
| `schemas/proposal.py` | BiddingProposalCreate (tender_id, valor_total, bdi_percent, encargos_sociais). **Validator:** `@field_validator("valor_unitario")` — verifica valor > 0 |
| `schemas/analysis.py` | AnalysisRequest (texto_edital, tender_id), AnalysisResult (objeto, requisitos, itens[], riscos[], viabilidade_score) |
| `schemas/assessment.py` | AssessmentRequest (tender_id, company_data), AssessmentResult (habilitacao_score, docs_faltantes[], aprovado) |
| `schemas/certificate.py` | CertificateCreate (tipo, numero, validade, orgao_emissor), CertificateStatus (valid, days_until_expiry) |
| `schemas/pipeline.py` | PipelineResult (scout_result, analyst_result, assessor_result, pricer_result, compiler_result, sentinel_alerts[]) |
| `schemas/pricing.py` | BDICalculation (custos_diretos, bdi_percent, impostos, lucro, resultado), PricingRequest (valor_estimado, regime_tributario, cenario) |

---

### 4.3 Routers / Endpoints

**Prefix base:** `/api/v1/licitacoes` | 10 sub-routers + WebSocket

*(Endpoints listados em versão anterior — mantidos. Adicionando response models:)*

**Tenders:** response=TenderResponse | **Proposals:** response=BiddingProposalResponse | **Agents:** response=PipelineResult | **Sync:** response=SyncTriggerResponse

**WebSocket:** `ws://{host}/api/v1/licitacoes/ws/disputes/{dispute_id}` — streaming de lances em tempo real

---

### 4.4 Services

| Classe | Arquivo | Métodos principais |
|--------|---------|-------------------|
| `TenderService` | `tender_service.py` | `search(filters)`, `update_status(tender_id, status)`, `mark_participando(tender_id)` |
| `ProposalService` | `proposal_service.py` | `create(tender_id, data)`, `submit()`, `get_versions()` |
| `PNCPService` | `pncp_service.py` | `sync_oportunidades(uf_list)`, `sync_precos()` |
| `SyncService` | `sync_service.py` | `trigger_sync(portal)`, `get_job_status(job_id)` |
| `PricingService` | `pricing_service.py` | `calculate_bdi(custos, regime)`, `get_price_history(segmento)` |
| `EditalParserService` | `edital_parser_service.py` | `parse_pdf(path) → EditalData` — regex, Lei 14.133/2021 + Lei 8.666 |
| `CertificateService` | `certificate_service.py` | `check_expiry()`, `request_renewal(cert_id)` |
| `DocumentService` | `document_service.py` | `upload(file, tender_id)`, `validate(doc_id)` |
| `ContractService` | `contract_service.py` | `create_from_tender(tender_id)`, `add_measurement(contract_id, data)`, `gerar_fatura(measurement_id)` |
| `OpportunityService` | `opportunity_service.py` | `score_relevancia(tender_id) → float` |
| `ERPIntegrationService` | `erp_integration_service.py` | `converter_para_operacional(contract_id)` |
| `NotificationService` | `notification_service.py` | `notificar_oportunidade(tender_id)`, `notificar_prazo(tender_id)` |

---

### 4.5 Agentes IA

**Pipeline:** SCOUT → ANALYST → ASSESSOR → PRICER → COMPILER (+ SENTINEL paralelo)

| Agente | LLM | Status |
|--------|-----|--------|
| ScoutAgent | — | ✅ Produção — busca 6 portais simultaneamente |
| **AnalystAgent** | **Claude API** (`claude-sonnet-4-20250514`, `ANTHROPIC_API_KEY`) | ✅ Produção |
| AssessorAgent | Heurístico | ✅ Produção |
| PricerAgent | Heurístico | ✅ Produção |
| CompilerAgent | — | ✅ Produção |
| SentinelAgent | Heurístico | ✅ Produção |
| WarriorAgent | — | ⚠️ DESENVOLVIMENTO — simulação apenas |
| pdf_renderer | — | ✅ Produção |

**Prompts armazenados:**
- `analyst_agent.py:107` — prompt inline para Claude (sem arquivo externo .txt/.yaml)
- `templates/` — **5 arquivos JSON de templates de proposta:**
  - `carta_proposta.json`
  - `declaracao_me_epp.json`
  - `declaracao_menor.json`
  - `planilha_custos.json`
  - `proposta_comercial.json`

**Beat schedule (Celery):**
```python
# celery_app.py
"bidding-sync-pncp-2h": {
    "task": "bidding.sync_pncp_oportunidades",
    "schedule": 7200.0,          # a cada 2 horas
    "options": {"queue": "gov.batch"},
},
"bidding-check-certidoes-6h": {
    "task": "bidding.verificar_certidoes_vencimento",
    "schedule": 21600.0,         # a cada 6 horas
    "options": {"queue": "gov.batch"},
},
"bidding-sync-precos-daily": {
    "task": "bidding.sync_pncp_precos",
    "schedule": 86400.0,         # diário
    "options": {"queue": "gov.batch"},
},
```

---

### 4.6 Integrações

| Portal / Integração | Client | URL Base | Status |
|---------------------|--------|----------|--------|
| PNCP | `pncp/client.py` (httpx async) | `https://pncp.gov.br/api/pncp` | ✅ |
| ComprasNet | `comprasnet/client.py` + `_PregaoHTMLParser` | SOAP/HTML | ✅ |
| Licitações-e (BB) | `licitacoes_e/client.py` | — | ✅ |
| e-Compras AM | `ecompras_am/client.py` | — | ✅ |
| BLL | `bll/client.py` | — | ✅ |
| Portal Compras Públicas | `portal_compras_publicas/client.py` | — | ✅ |
| CND (Débitos Federais) | `receita_federal/cnd_client.py` | ReceitaFederal | ✅ |
| CNDT (Trabalhista) | `receita_federal/cndt_client.py` | TST | ✅ |
| CRF (FGTS) | `receita_federal/crf_client.py` | CEF | ✅ |
| ISS Manaus | `receita_federal/prefeitura_manaus_client.py` | SEMEF | ✅ |
| SEFAZ AM | `receita_federal/sefaz_am_client.py` | SEFAZ-AM | ✅ |
| **Certificado A1** | `core/credentials/` (global) | — | ⚠️ Disponível, pendente integração no WarriorAgent |
| Banco Inter | **Não usado** | — | — |
| WhatsApp | **Não usado** | — | — |
| SMTP | **Não usado** | — | — |
| Solides | **Não usado** | — | — |

---

### 4.7 Migrations Recentes

| Arquivo | revision | down_revision | Create Date |
|---------|----------|---------------|------------|
| `bidding_module_tables.py` | `bidding_001` | None | 2026-01-11 |
| `sprint71_bidding_ai_agents_tables.py` | `sprint71_bidding_ai_agents` | `sprint70_cost_by_type_tables` | 2026-03-12 |
| `sprint72_fix_bidding_schema_alignment.py` | `sprint72_fix_bidding_schema` | `sprint71_bidding_ai_agents` | 2026-03-12 |

---

### 4.8 Testes

**Localização:** `tests/modules/bidding/`
**Total:** 4 arquivos · **66 funções de teste**

| Arquivo | Escopo |
|---------|--------|
| `test_models.py` | Tender, Proposal, PublicContract — criação, enums, constraints |
| `test_services.py` | ContractService (add_measurement, approve_measurement, converter_para_operacional, gerar_medicao, gerar_fatura), TenderService (search, update_status, duplicate detection) |
| `test_integrations.py` | Clientes de portais — PNCP, ComprasNet |
| `test_agents.py` | Scout, Analyst, Pricer — lógica dos agentes |

**Cobertura estimada:** Baixa-Média (66 funções). WarriorAgent, SentinelAgent, CompilerAgent, WebSocket sem cobertura.

---

### 4.9 TODOs / Pendências

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" modules/bidding --include="*.py"
# Resultado real:
# modules/bidding/agents/analyst_agent.py:167 — texto de prompt para Claude (falso positivo)
# modules/bidding/services/edital_parser_service.py:1127 — comentário de regex (falso positivo)
```

**Pendências reais (consta em comentários e docstrings):**
1. `warrior_agent.py:6,369` — "Integração com portais reais pendente (requer Playwright + certificado digital A1)"
2. `analyst_agent.py` — modelo `claude-sonnet-4-20250514` desatualizado (atual: `claude-sonnet-4-6`)
3. WarriorAgent, SentinelAgent, CompilerAgent sem testes
4. Prompts Claude inline — sem versionamento em arquivo .txt/.yaml separado
5. Certificado A1 não integrado ao WarriorAgent

---

## 5. Sumário Executivo

### 5.1 O que Existe vs. o que Falta

| Dimensão | CRM | Vendas | Marketing | Licitações |
|----------|-----|--------|-----------|------------|
| Arquivos .py | 41 | 8 (stubs) | 1 (dentro CRM) | 78 |
| Models ORM | 5 | 0 | 0* | 13 |
| Relacionamentos ORM | 14 | 0 | 0 | 4 |
| Endpoints REST | ~55 | 0 | 8 | ~65 |
| Services | 10 | 0 | 0 | 12 |
| Agentes IA | 0 | 0 | 0 | 8 (1 em dev) |
| Celery Tasks | 0 | 0 | 0 | 11 |
| Beat Schedule | 0 | 0 | 0 | 3 agendamentos |
| Templates/Prompts | 0 | 0 | 0 | 5 JSON + 1 inline |
| Integrações ext. | 5 (assinatura) | 0 | 0 | 11 portais/certidões |
| Testes (arquivos) | 17 | 0 | 0 | 4 |
| Testes (funções) | 225 | 0 | 0 | 66 |
| Migrations | 9 | 0 | 0* | 3 |

*Marketing: tabelas existem no banco (sem ORM / migration rastreável)

### 5.2 Módulos Maduros vs. Embrionários

**Maduros:**
- **CRM** — pipeline completo, 225 testes, 0 TODOs, event bus, E2E coberto

**Funcionais com gaps:**
- **Licitações** — 8 agentes, 6 portais, Claude API. Gaps: WarriorAgent em dev, cobertura de testes baixa
- **Marketing** — 8 endpoints funcionais. Gaps: sem ORM, sem e-mail real, sem automação

**Embrionários / Stubs:**
- **Vendas** (`modules/comercial/`) — 0% implementado
- **Inteligência** (`modules/inteligencia/`) — 0% implementado

### 5.3 Riscos Técnicos Identificados

1. **WarriorAgent em simulação** — pregão eletrônico sem integração real; risco competitivo
2. **Marketing sem ORM** — raw SQL sem type safety, sem migrations, sem validators
3. **`modules/comercial/` vazio** — risco de 404 se frontend roteado para `/comercial`
4. **Analyst usa modelo antigo** — `claude-sonnet-4-20250514` vs. `claude-sonnet-4-6`
5. **Testes baixos em Licitações** — 66 funções para 78 arquivos
6. **Certificado A1** para portais não integrado ao WarriorAgent
7. **Prompts Claude inline** — sem versionamento; mudanças de prompt sem histórico

### 5.4 Score de Completude por Módulo (0–100)

| Módulo | Score | Justificativa |
|--------|-------|---------------|
| **CRM** | **92/100** | Pipeline completo, 225 testes, 0 TODOs, event bus, E2E. -8: sem LLM nativo, sem e-mail transacional |
| **Licitações** | **78/100** | 8 agentes IA, Claude API, 11 Celery tasks, 6 portais. -22: WarriorAgent em dev, testes baixos, modelo desatualizado |
| **Marketing** | **35/100** | 8 endpoints funcionais, UTM tracking. -65: sem ORM, sem e-mail real, sem automação, sem testes dedicados |
| **Vendas** | **3/100** | Apenas estrutura de pastas. -97: zero implementação |

### 5.5 Integrações Externas Globais (STEP 7 completo)

| Integração | Módulo | Status |
|-----------|--------|--------|
| **Banco Inter** | `financial/` + `main_production.py:1039` | ✅ Pix + boleto — NÃO no CRM/Licitações |
| **WhatsApp (Evolution API)** | `whatsapp_router` em `main_production.py:929` | ✅ Módulo separado — NÃO integrado a campanhas |
| **SMTP** | `core/mailer.py` (smtplib) + `settings.SMTP_*` | ✅ Global — NÃO usado diretamente em Marketing |
| **SendGrid / Mailgun** | Schema: `sprint36_notification_hub` | ⚠️ Schema criado, sem implementação |
| **Solides** | `sprint33_solides_integration` | ✅ RH/DP — NÃO relacionado ao menu Negócios |
| **Certificado A1** | `core/credentials/`, `government_integrations/` | ✅ Global — pendente no WarriorAgent |
| **Claude API** | `bidding/agents/analyst_agent.py` | ✅ `ANTHROPIC_API_KEY`, `claude-sonnet-4-20250514` |
| **ComprasNet/PNCP/portais** | `bidding/integrations/` | ✅ 6 portais implementados |

---

RECONHECIMENTO BACKEND CONCLUÍDO — arquivo em /opt/conecta-pro/reconhecimento/cpro11/t4_backend_negocios.md — 974 linhas
