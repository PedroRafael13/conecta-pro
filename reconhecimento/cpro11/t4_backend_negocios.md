# CPRO11 — Reconhecimento Backend: Menu Negócios
**Data:** 2026-04-20
**Analista:** Claude Code (tmux-t4)
**Escopo:** CRM · Vendas · Marketing · Licitações
**Branch:** feature/people-management-reorganization

---

## STEP 1 — Descoberta de Estrutura

Arquivos .py relevantes (find + grep):

```
modules/crm/            → 41 arquivos .py
modules/bidding/        → 78 arquivos .py
modules/comercial/      → 8 arquivos __init__.py (stubs vazios)
modules/inteligencia/   → 7 arquivos __init__.py (stubs vazios)
```

Principais subpastas encontradas:
- `crm/{models,schemas,controllers,repositories,services,publishers.py}`
- `bidding/{models,schemas,controllers,repositories,services,agents,integrations,tasks}`
- `comercial/{leads,oportunidades,propostas,contratos,clientes,comissoes,metas,atividades}` — todos vazios
- `inteligencia/{alertas,analytics,dashboards,exportacoes,kpis,relatorios}` — todos vazios

---

## 1. CRM (`modules/crm/`)

### 1.1 Models

**Tabela `leads`** — `models/lead.py`

| Campo | Tipo | Detalhes |
|-------|------|----------|
| id | UUID | PK, server_default |
| name | str | nullable=False |
| email | str | nullable=True |
| phone | str | nullable=True |
| company | str | nullable=True |
| position | str | nullable=True |
| company_size | str | nullable=True |
| industry | str | nullable=True |
| source | LeadSource (enum) | nullable=False |
| status | LeadStatus (enum) | default='novo' |
| score | int | default=0 |
| probability | float | default=0.0 |
| expected_value | float | default=0.0 |
| notes | text | nullable=True |
| assigned_to_id | FK→users | nullable=True |
| last_contact_at | datetime | nullable=True |
| next_contact_at | datetime | nullable=True |
| is_active | bool | default=True |
| created_at | datetime | server_default |
| updated_at | datetime | onupdate |

Properties: `is_hot` (score≥70), `is_qualified`, `weighted_value`

**Tabela `opportunities`** — `models/opportunity.py`

| Campo | Tipo | Detalhes |
|-------|------|----------|
| id | UUID | PK |
| title | str | nullable=False |
| description | text | nullable=True |
| lead_id | FK→leads | nullable=True |
| contact_name/email/phone | str | nullable=True |
| company_name | str | nullable=True |
| stage | OpportunityStage (enum) | qualification→needs_analysis→proposal→negotiation→closed_won→closed_lost |
| priority | enum | low/medium/high/critical |
| value | float | nullable=True |
| probability | float | default=0.0 |
| expected_close_date | date | nullable=True |
| actual_close_date | date | nullable=True |
| owner_id | FK→users | nullable=True |
| loss_reason | LossReason (enum) | nullable=True |
| competitor | str | nullable=True |
| win_notes / loss_notes | text | nullable=True |
| is_active | bool | default=True |

Properties: `weighted_value`, `is_open`, `is_won`, `is_lost`, `days_in_pipeline`, `is_overdue`

**Tabelas `proposals`, `proposal_items`, `proposal_templates`, `proposal_approvals`** — `models/proposal.py`
- Status (10 estados): draft → sent → viewed → approved → accepted / rejected / expired / cancelled / revision_requested / under_revision
- Tipo: standard / custom / renewal / amendment
- Versioning: `parent_id` FK self-referencial
- Valores: subtotal, discount_percent, discount_value, tax_rate, tax_value, total, installments
- Datas: issue_date, valid_until, sent_at, viewed_at, responded_at
- Workflow: `proposal_approvals` (approver_id, status, notes, approved_at)

**Tabelas `contracts`, `contract_items`, `contract_addendums`** — `models/contract.py`
- Tipo: RECURRING / ONE_TIME
- Status: DRAFT → PENDING_SIGNATURE → ACTIVE → SUSPENDED → CANCELLED → TERMINATED
- Índice de ajuste: IGPM / IPCA / INPC / FIXED / CUSTOM
- Serviços: SECURITY / REMOTE_GATEHOUSE / ELECTRONIC_SECURITY
- Aditivos: `contract_addendums` (tipo, valor_anterior, valor_novo, motivo, data)

**Tabelas `commissions`, `commission_rules`, `commission_summaries`** — `models/commission.py`
- Regras por vendedor, tipo de serviço, faixa de valor
- Resumos mensais: `commission_summaries` (seller_id, year, month, total_value, status)
- Status: PENDING / APPROVED / PAID / CANCELLED

### 1.2 Schemas (Pydantic v2)

| Arquivo | Schemas principais |
|---------|-------------------|
| `schemas/lead.py` | LeadCreate, LeadUpdate, LeadResponse, LeadListResponse, LeadStats |
| `schemas/opportunity.py` | OpportunityCreate, OpportunityUpdate, OpportunityResponse, PipelineStats, OpportunityClose |
| `schemas/proposal.py` | ProposalCreate, ProposalUpdate, ProposalResponse, ProposalItemCreate, ProposalTemplateResponse, ApprovalCreate, ProposalListResponse |
| `schemas/contract.py` | ContractCreate, ContractResponse, ContractDetailResponse, ContractListResponse, ContractStats, ContractAlert, ContractItem, ContractAddendum, AdjustmentResult, RenewalResult |
| `schemas/commission.py` | CommissionCreate, CommissionResponse, CommissionRuleCreate, CommissionRuleResponse, CommissionStats, SellerCommissionStats, CommissionSummaryResponse, CommissionListResponse, CommissionDetailResponse |

### 1.3 Routers / Endpoints

**Prefix base:** `/api/v1/crm` | Auth: `CurrentActiveUser` (JWT Bearer)

**Leads (`/leads`)**
| Método | Rota | Função |
|--------|------|--------|
| POST | `/` | Criar lead |
| GET | `/` | Listar leads (filtros: status, source, assigned_to, score_min) |
| GET | `/stats` | Estatísticas por status/source |
| GET | `/{id}` | Detalhe |
| PUT | `/{id}` | Atualizar |
| PATCH | `/{id}/status` | Alterar status |
| POST | `/{id}/recalculate-score` | Recalcular score |
| GET | `/{id}/recommended-action` | Ação recomendada (IA) |
| DELETE | `/{id}` | Remover |

**Opportunities (`/opportunities`)**
| Método | Rota | Função |
|--------|------|--------|
| POST | `/` | Criar oportunidade |
| POST | `/from-lead` | Criar a partir de lead |
| GET | `/` | Listar |
| GET | `/pipeline/stats` | Funil de vendas ponderado |
| GET | `/{id}` | Detalhe |
| PUT | `/{id}` | Atualizar |
| PATCH | `/{id}/stage` | Mover de estágio |
| POST | `/{id}/close` | Fechar (won/lost) |
| DELETE | `/{id}` | Remover |

**Proposals (`/proposals`)**
| Método | Rota | Função |
|--------|------|--------|
| POST | `/` | Criar proposta |
| POST | `/from-opportunity` | Criar a partir de oportunidade |
| GET | `/` | Listar |
| GET | `/{id}` | Detalhe |
| PUT | `/{id}` | Atualizar |
| PATCH | `/{id}/status` | Alterar status |
| POST | `/{id}/approve` | Aprovar |
| POST | `/{id}/send` | Enviar ao cliente |
| DELETE | `/{id}` | Remover |
| GET | `/templates` | Listar templates |
| POST | `/templates` | Criar template |

**Contracts (`/contracts`)**
| Método | Rota | Função |
|--------|------|--------|
| POST | `` | Criar contrato |
| GET | `` | Listar |
| GET | `/stats` | Estatísticas |
| GET | `/alerts` | Alertas de vencimento |
| GET | `/templates` | Templates de contrato |
| GET | `/{id}` | Detalhe |
| PUT | `/{id}` | Atualizar |
| DELETE | `/{id}` | Remover |
| POST | `/{id}/submit` | Submeter para assinatura |
| POST | `/{id}/activate` | Ativar |
| POST | `/{id}/suspend` | Suspender |
| POST | `/{id}/terminate` | Rescindir |
| POST | `/{id}/renew` | Renovar |
| POST | `/{id}/calculate-adjustment` | Calcular reajuste (IGPM/IPCA) |
| POST | `/{id}/addendums` | Adicionar aditivo |
| GET | `/{id}/addendums` | Listar aditivos |
| POST | `/{id}/items` | Adicionar item |
| PUT | `/{id}/items/{item_id}` | Atualizar item |
| DELETE | `/{id}/items/{item_id}` | Remover item |

**Commissions (`/commissions`)**
| Método | Rota | Função |
|--------|------|--------|
| POST | `/rules` | Criar regra |
| GET | `/rules` | Listar regras |
| GET | `/rules/{id}` | Detalhe regra |
| PUT | `/rules/{id}` | Atualizar regra |
| DELETE | `/rules/{id}` | Remover regra |
| POST | `/calculate` | Calcular comissão |
| GET | `` | Listar comissões |
| GET | `/stats` | Estatísticas |
| GET | `/seller/{id}/stats` | Stats por vendedor |
| GET | `/summaries` | Resumos mensais |
| POST | `/summaries/{seller_id}/{year}/{month}/close` | Fechar mês |
| GET | `/{id}` | Detalhe |
| PUT | `/{id}` | Atualizar |
| PATCH | `/{id}/status` | Alterar status |
| POST | `/{id}/approve` | Aprovar |
| DELETE | `/{id}` | Remover |

**Clients, Contacts, Dashboard, Marketing** — controllers adicionais (ver seção Marketing)

OpenAPI: `curl http://127.0.0.1:8080/openapi.json` → **API indisponível** em tempo de reconhecimento. Dados obtidos via inspeção de código-fonte.

### 1.4 Services

| Service | Método principal | Responsabilidade |
|---------|-----------------|-----------------|
| `pricing_engine.py` | `calculate()` | CCT (mão de obra + encargos), ISS por estado, margem. Inputs: base_salary, headcount, contract_months, service_type, client_state, margin_target. 14 campos no output. |
| `pipeline_service.py` | `calculate_weighted_pipeline()`, `calculate_win_rate(days=90)` | STAGE_PROBABILITIES, AVG_STAGE_DURATION, pipeline ponderado |
| `crm_360_service.py` | Customer Journey | CustomerSegment (VIP/PREMIUM/STANDARD/BRONZE/PROSPECT/CHURNING/INACTIVE), RFM |
| `signature_integration.py` | `request_signature()` | SignatureProvider: INTERNAL/DOCUSIGN/CLICKSIGN/D4SIGN/AUTENTIQUE |
| `pdf_generator.py` | `generate_proposal_pdf()` | Gera PDF de propostas/contratos |
| `dashboard_service.py` | `get_dashboard_metrics()` | KPIs do painel CRM |
| `proposal_service.py` | `create()`, `approve()`, `send()` | Versionamento, workflow de aprovação |
| `contract_service.py` | `renew()`, `calculate_adjustment()` | Renovação, reajuste por índice |
| `lead_service.py` | `recalculate_score()`, `recommend_action()` | Score e ação recomendada |
| `commission_service.py` | `calculate()`, `approve()`, `close_month()` | Cálculo e aprovação de comissões |

### 1.5 Agentes IA

**CRM não possui agentes de IA dedicados.** A lógica de "ação recomendada" em `lead_service.py` é heurística (score + status + dias sem contato) — sem chamadas a LLM. O endpoint `GET /leads/{id}/recommended-action` retorna regras estáticas.

Integrações LLM no CRM: **nenhuma**.

### 1.6 Integrações

| Integração | Status | Detalhes |
|-----------|--------|----------|
| **DocuSign** | Configurável | via `signature_integration.py`, SignatureProvider.DOCUSIGN |
| **ClickSign** | Configurável | via `signature_integration.py` |
| **D4Sign** | Configurável | via `signature_integration.py` |
| **Autentique** | Configurável | via `signature_integration.py` |
| **Assinatura Interna** | Ativo | `SignatureProvider.INTERNAL` (padrão) |
| **Banco Inter** | **Não integrado aqui** | Banco Inter está em módulo financeiro/webhooks (`main_production.py:1039`), não no CRM |
| **WhatsApp** | Campo de dado apenas | `whatsapp` é campo de contato/lead, sem envio via API |
| **SMTP** | Global (`core/mailer.py`) | Não usado diretamente pelo CRM — compartilhado via notificações |
| **Solides** | **Não integrado no CRM** | Solides é integração de RH (`sprint33_solides_integration`), sem relação com CRM |

### 1.7 Migrations Recentes

| Arquivo | Revision | Descrição | Data |
|---------|----------|-----------|------|
| `7017a3795753_create_leads_table.py` | 7017a3795753 | Tabela leads | 2025-12-30 |
| `1ab7727d6644_create_opportunities_table.py` | 1ab7727d6644 | Tabela opportunities | 2025-12-30 |
| `d32dc56bebba_create_proposal_tables.py` | d32dc56bebba | proposals + items + templates + approvals | 2025-12-30 |
| `e5f7a8b9c0d1_create_commission_tables.py` | e5f7a8b9c0d1 | commissions + rules + summaries | — |
| `f6g8h9i0j1k2_create_contract_tables.py` | f6g8h9i0j1k2 | contracts + items + addendums | — |
| `sprint14_proposals_cpq_premium.py` | sprint14 | CPQ premium — tabelas adicionais | — |
| `sprint36_fix_float_to_numeric.py` | sprint36 | Fix tipo float→numeric em valores | — |
| `sprint44_create_contract_analysis_tables.py` | sprint44 | Análise de contratos | — |
| `sprint66_add_contract_costs.py` | sprint66 | Custos adicionais de contrato | — |

### 1.8 Testes

**Localização:** `tests/modules/crm/`
**Total:** 17 arquivos · **225 funções de teste**

| Arquivo | Escopo |
|---------|--------|
| `conftest.py` + `conftest_e2e.py` | Fixtures (sync + E2E) |
| `test_controllers_lead_opp_proposal_dashboard.py` | Controllers leads/oportunidades/propostas |
| `test_controllers_commission_contract.py` | Controllers comissões/contratos |
| `test_e2e_leads_opportunities.py` | E2E: lead → qualificação → oportunidade |
| `test_e2e_proposals.py` | E2E: oportunidade → proposta → aprovação |
| `test_e2e_contracts.py` | E2E: proposta → contrato → ativação |
| `test_e2e_commissions.py` | E2E: venda → comissão → pagamento |
| `test_e2e_dashboard_clients_contacts_marketing.py` | Dashboard + clientes + contacts + marketing |
| `test_pricing_engine.py` | PricingEngine (CCT + ISS + margem) |
| `test_proposal_model.py` | Model proposal (status machine) |
| `test_proposal_service.py` | ProposalService |
| `test_repositories_lead_opp_commission.py` | Repos lead/opp/commission |
| `test_repositories_proposal_contract.py` | Repos proposal/contract |
| `test_crm_marketing_vendas.py` | Integração marketing/vendas |
| `test_coverage_gaps_controllers.py` + `test_coverage_gaps_models.py` | Coverage gaps |
| `test_coverage_final.py` + `test_services_remaining.py` | Cobertura final |

**Cobertura estimada:** Alta (17 arquivos, 225 funções, E2E completo do pipeline).

### 1.9 TODOs / Pendências

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" modules/crm --include="*.py"
```

**Resultado: NENHUM TODO/FIXME/HACK encontrado no módulo CRM.**

O CRM é o módulo mais maduro — zero pendências técnicas explícitas no código.

---

## 2. Vendas (`modules/comercial/`)

### 2.1 Models

**Nenhum model existe.** O diretório contém apenas `__init__.py` vazio.

### 2.2 Schemas

**Nenhum schema existe.**

### 2.3 Routers / Endpoints

**Nenhum endpoint existe.** Módulo não registrado em `main_production.py`.

### 2.4 Services

**Nenhum service existe.**

### 2.5 Agentes IA

**Nenhum agente existe.**

### 2.6 Integrações

**Nenhuma integração existe.**

### 2.7 Migrations Recentes

**Nenhuma migration referencia `modules/comercial/`.**

### 2.8 Testes

**Nenhum teste existe.**

### 2.9 TODOs / Pendências

```
modules/comercial/
├── __init__.py          # vazio
├── atividades/          # vazio
├── clientes/            # vazio
├── comissoes/           # vazio
├── contratos/           # vazio
├── leads/               # vazio
├── metas/               # vazio
├── oportunidades/       # vazio
└── propostas/           # vazio
```

**Status: STUB VAZIO — 8 subdiretórios com apenas `__init__.py`.**
Toda lógica de vendas está atualmente em `modules/crm/`. A intenção arquitetural é possivelmente separar "Vendas" (foco equipe comercial interna) de "CRM" (foco relacionamento cliente), mas a migração não foi iniciada.

**Pendência:** Definir se `comercial/` será o módulo de Vendas separado ou descontinuado em favor do CRM unificado.

---

## 3. Marketing (`modules/crm/controllers/marketing_controller.py`)

### 3.1 Models

Marketing **não possui ORM model dedicado**. Usa `sqlalchemy.text()` diretamente (raw SQL). As tabelas existem no banco mas sem classe SQLAlchemy.

**Tabela `marketing_campaigns`** (inferida do raw SQL):

| Campo | Tipo |
|-------|------|
| id | UUID |
| name | str |
| type | str (organic/paid/email/social/etc) |
| budget | float |
| description | text |
| start_date | date |
| end_date | date |
| utm_source | str |
| utm_medium | str |
| utm_campaign | str |
| created_at | datetime |

**Tabela `marketing_leads`** (inferida do raw SQL):

| Campo | Tipo |
|-------|------|
| id | UUID |
| campaign_id | FK→marketing_campaigns |
| name | str |
| email | str |
| phone | str |
| whatsapp | str |
| source | str |
| status | str (novo/converted/etc) |
| created_at | datetime |

### 3.2 Schemas

Schemas **inline** no controller usando `pydantic.BaseModel`:
- `CampaignCreate` — name, type, budget, description, start/end_date, UTM params
- `MktLeadCreate` — campaign_id, name, email, phone, whatsapp, source

Sem schemas em `schemas/` separado.

### 3.3 Routers / Endpoints

**Prefix:** `/api/v1/crm/marketing` | Auth: `CurrentActiveUser`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/campaigns/` | Listar campanhas (inclui total_leads e converted) |
| POST | `/campaigns/` | Criar campanha |
| PUT | `/campaigns/{id}` | Atualizar campanha |
| GET | `/leads/` | Listar leads de marketing |
| POST | `/leads/` | Criar lead de marketing |
| POST | `/leads/{id}/convert` | Converter lead → CRM Lead |
| GET | `/leads/stats` | Estatísticas de conversão |
| POST | `/licitacao/convert-to-crm` | Converter oportunidade de licitação → pipeline CRM |

### 3.4 Services

**Nenhum service layer separado.** Lógica de negócio inline no controller via raw SQL.

### 3.5 Agentes IA

**Nenhum agente de IA para Marketing.** Sem automação de campanhas ou segmentação automática.

### 3.6 Integrações

| Integração | Status | Detalhes |
|-----------|--------|----------|
| **WhatsApp** | Campo de dado | `whatsapp` armazenado nos leads, sem envio via API aqui |
| **WhatsApp Business API** | Em outro módulo | Evolution API registrada em `main_production.py:929` mas em módulo separado (`whatsapp_router`), não no marketing |
| **SMTP / E-mail marketing** | Global | `core/mailer.py` com SMTP configurável — **não usado diretamente no marketing controller** |
| **SendGrid / Mailgun** | Configurável | Enum nos tipos de canal em `sprint36_create_notification_hub_tables.py` (valores: smtp, sendgrid, mailgun) — sem implementação no marketing |
| **UTM tracking** | Implementado | Campos utm_source, utm_medium, utm_campaign no modelo de campanha |
| **Solides** | Não relacionado | Integração de RH, sem uso em marketing |
| **Banco Inter** | Não relacionado | Módulo financeiro |
| **Certificado A1** | Não aplicável | Apenas para assinatura digital e portais de licitação |

### 3.7 Migrations Recentes

Marketing usa raw SQL — **sem migrations ORM dedicadas** para as tabelas `marketing_campaigns` e `marketing_leads`. As tabelas foram criadas diretamente (sem migration rastreável no Alembic).

### 3.8 Testes

Testes inclusos nos arquivos do CRM:
- `test_crm_marketing_vendas.py` — integração marketing/vendas
- `test_e2e_dashboard_clients_contacts_marketing.py` — marketing dentro do E2E

**Sem arquivo de testes dedicado para Marketing.**

### 3.9 TODOs / Pendências

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" modules/crm/controllers/marketing_controller.py
```

**Resultado: nenhum TODO explícito.**

**Pendências identificadas por análise:**
1. Tabelas `marketing_campaigns` / `marketing_leads` sem ORM model — risco de manutenção
2. Sem E-mail marketing real (SendGrid/Mailgun não implementados no marketing)
3. WhatsApp Business API (`whatsapp_router`) não integrado com campanhas
4. Sem automação de campanhas (disparo agendado)
5. Sem A/B testing
6. Sem métricas de ROI por campanha

---

## 4. Licitações (`modules/bidding/`)

### 4.1 Models

**Tabela `bidding_tenders`** — `models/tender.py`

| Campo | Tipo | Detalhes |
|-------|------|----------|
| id | UUID | PK |
| pncp_id | str | UNIQUE — ID no PNCP |
| modalidade | enum (11) | pregao_eletronico, concorrencia, dispensa, inexigibilidade, credenciamento, leilao, dialogo_competitivo, pre_qualificacao, manifestacao_intencao, registro_preco, outros |
| criterio_julgamento | enum (6) | menor_preco, maior_desconto, melhor_tecnica, tecnica_preco, maior_lance, nao_aplicavel |
| status | enum (11) | publicado, aberto, suspenso, encerrado, homologado, revogado, anulado, fracassado, deserto, em_recurso, em_andamento |
| orgao_cnpj / orgao_uf | str | Órgão licitante |
| segmento | str | vigilancia/limpeza/etc |
| valor_estimado | Numeric | |
| participando / interesse | bool | Flags de acompanhamento |
| tags | JSONB | |
| requisitos | JSONB | |

**Índices compostos:** (orgao_cnpj, ano), (modalidade, status), (orgao_uf, segmento), (participando, status)

**Outros models:**
- `models/opportunity.py` — `bidding_opportunities` (portal, portal_id, objeto, valor_estimado, relevancia_score)
- `models/proposal.py` — `bidding_proposals` + `bidding_proposal_items` (BDI, historico_lances JSONB, encargos_sociais)
- `models/analysis.py` — AnalysisResult (resultado do agente ANALYST)
- `models/assessment.py` — Assessment (avaliação de habilitação)
- `models/certificate.py` — certidões de habilitação + validade
- `models/company_document.py` — documentos da empresa para licitações
- `models/dispute.py` — sessão de disputa em pregão eletrônico
- `models/measurement.py` — medições de contrato licitado
- `models/price_history.py` — histórico de preços do mercado
- `models/pricing.py` — resultado de precificação BDI
- `models/public_contract.py` — contratos de licitações ganhas
- `models/sync_job.py` — jobs de sincronização com portais

### 4.2 Schemas (Pydantic v2)

| Arquivo | Schemas principais |
|---------|-------------------|
| `schemas/tender.py` | TenderCreate, TenderResponse, TenderListResponse, TenderFilter |
| `schemas/proposal.py` | BiddingProposalCreate, BiddingProposalResponse, ProposalItemCreate |
| `schemas/analysis.py` | AnalysisRequest, AnalysisResult |
| `schemas/assessment.py` | AssessmentRequest, AssessmentResult, HabilitacaoScore |
| `schemas/certificate.py` | CertificateCreate, CertificateResponse, CertificateStatus |
| `schemas/contract.py` | BiddingContractCreate, BiddingContractResponse |
| `schemas/dispute.py` | DisputeSession, LanceRegistro, DisputeStatus |
| `schemas/document.py` | DocumentCreate, DocumentResponse |
| `schemas/opportunity.py` | BiddingOpportunityCreate, OpportunityResponse |
| `schemas/pipeline.py` | PipelineStatus, PipelineResult (resultado do pipeline 5 agentes) |
| `schemas/pricing.py` | BDICalculation, PricingRequest, PricingResult |

### 4.3 Routers / Endpoints

**Prefix base:** `/api/v1/licitacoes` | Inclui 10 sub-routers + WebSocket

**Tenders (`/tenders`)**
| GET | `/` | Listar (filtros avançados) |
| GET | `/dashboard` | Painel |
| GET | `/abertos` | Abertas |
| GET | `/participando` | Em participação |
| GET | `/segmento/{segmento}` | Por segmento |

**Proposals (`/proposals`)**
| GET/POST | `/` | Listar / Criar |
| GET | `/estatisticas` | Stats |
| GET | `/vencedoras` | Propostas vencedoras |
| GET | `/tender/{id}` | Por licitação |
| GET | `/{id}` | Detalhe |
| POST | `/bdi` | Calcular BDI |
| POST | `/lance` | Registrar lance |

**Agents (`/agents`)**
| GET | `/status` | Status dos agentes |
| POST | `/scout/buscar` | Busca nos portais |
| GET | `/scout/portais` | Portais disponíveis |
| POST | `/analyst/analisar` | Analisar edital (Claude AI) |
| POST | `/assessor/avaliar` | Avaliar habilitação |
| POST | `/pricer/calcular` | Calcular preço/BDI |
| POST | `/pipeline` | Pipeline completo (Scout→Compiler) |
| GET/POST | `/sentinel/tipos` + `/sentinel/verificar` + `/sentinel/alertas` | Conformidade |
| GET | `/warrior/status` | Status WARRIOR |
| POST | `/warrior/simular` | Simular disputa |
| POST | `/compiler/gerar` | Gerar proposta PDF |

**Sync (`/sync`)**
| POST | `/pncp/trigger` | Disparar sync PNCP |
| GET | `/jobs` + `/jobs/{id}` | Jobs de sync |
| POST | `/precos/trigger` | Sync histórico de preços |
| GET | `/status` | Status |

**Outros:** `/certificates`, `/documents`, `/contracts`, `/erp`, `/opportunities`, `/disputes` + WebSocket `/ws/disputes/{id}`

### 4.4 Services

| Service | Responsabilidade |
|---------|-----------------|
| `tender_service.py` | CRUD e filtros de licitações |
| `proposal_service.py` | Versionamento, submissão de propostas |
| `pncp_service.py` | Sincronização periódica com PNCP |
| `sync_service.py` | Orquestra jobs de sync multi-portal |
| `pricing_service.py` | Cálculo BDI + histórico de preços |
| `edital_parser_service.py` | Parser de PDFs de editais (regex, sem NLP, Lei 14.133/2021 + Lei 8.666) |
| `certificate_service.py` | Gestão e renovação automática de certidões |
| `document_service.py` | Upload e validação de documentos de habilitação |
| `contract_service.py` | Contratos pós-licitação, medições, faturamento |
| `opportunity_service.py` | Score de relevância de oportunidades |
| `erp_integration_service.py` | Integração com financeiro/operacional |
| `notification_service.py` | Alertas de prazos e oportunidades |

### 4.5 Agentes IA

**Pipeline:** SCOUT → ANALYST → ASSESSOR → PRICER → COMPILER (+ SENTINEL paralelo)

| Agente | LLM | Descrição |
|--------|-----|-----------|
| **ScoutAgent** | — | Busca simultânea em 6 portais. Keywords padrão: vigilancia, seguranca patrimonial, portaria, monitoramento, cftv, alarme, controle de acesso |
| **AnalystAgent** | **Claude API** (`claude-sonnet-4-20250514`) | Analisa edital com Anthropic API. `ANTHROPIC_API_KEY` via env var. Extrai objeto, requisitos, habilitação, itens, riscos |
| **AssessorAgent** | Heurístico | Avalia habilitação da Conecta vs. edital. Score de habilitação. Verifica certidões, ISO 9001/14001 |
| **PricerAgent** | Heurístico | Calcula BDI. 3 cenários: conservador/moderado/agressivo. Regimes: Simples/Lucro Presumido/**Lucro Real** (atual) |
| **CompilerAgent** | — | Monta proposta técnica completa em PDF via `pdf_renderer.py` |
| **SentinelAgent** | Heurístico | Monitora conformidade durante disputa, verifica prazos, emite alertas |
| **WarriorAgent** | — | Robô de pregão eletrônico. **STATUS: DESENVOLVIMENTO** — 7 portais suportados, modo simulação. Requer Playwright + certificado digital A1 para produção |
| **pdf_renderer** | — | Renderiza proposta em PDF |

**Prompts armazenados:** Prompt para Claude em `analyst_agent.py:107` (inline no código, não em arquivo separado .txt/.yaml).

### 4.6 Integrações Externas

**Portais de Licitação:**
| Portal | Client | Status |
|--------|--------|--------|
| PNCP | `pncp/client.py` — `https://pncp.gov.br/api/pncp` (httpx async) | ✅ Ativo |
| ComprasNet | `comprasnet/client.py` — `_PregaoHTMLParser` (HTML fallback) | ✅ Ativo |
| Licitações-e (BB) | `licitacoes_e/client.py` | ✅ Implementado |
| e-Compras AM | `ecompras_am/client.py` | ✅ Implementado |
| BLL | `bll/client.py` | ✅ Implementado |
| Portal Compras Públicas | `portal_compras_publicas/client.py` | ✅ Implementado |

**Certidões (Receita Federal):**
| Certidão | Client |
|----------|--------|
| CND (Débitos Federais) | `receita_federal/cnd_client.py` |
| CNDT (Débitos Trabalhistas) | `receita_federal/cndt_client.py` |
| CRF (Regularidade FGTS) | `receita_federal/crf_client.py` |
| ISS Manaus | `receita_federal/prefeitura_manaus_client.py` |
| SEFAZ AM | `receita_federal/sefaz_am_client.py` |

**Certificado A1:** Necessário para WarriorAgent (pregão eletrônico) via Playwright. **Ainda não integrado** — pendente para produção do WARRIOR.

**Banco Inter / WhatsApp / SMTP / Solides:** Não usados no módulo Licitações.

### 4.7 Migrations Recentes

| Arquivo | Descrição |
|---------|-----------|
| `bidding_module_tables.py` | Tabelas base (tenders, proposals, items, etc.) |
| `sprint71_bidding_ai_agents_tables.py` | Tabelas para agentes IA (análise, avaliação, pipeline) |
| `sprint72_fix_bidding_schema_alignment.py` | Correção de alinhamento de schema |

### 4.8 Testes

**Localização:** `tests/modules/bidding/`
**Total:** 4 arquivos · **66 funções de teste**

| Arquivo | Escopo |
|---------|--------|
| `test_models.py` | Tender, Proposal, PublicContract — criação e enums |
| `test_services.py` | ContractService (medições, faturamento), TenderService (search, status) |
| `test_integrations.py` | Clientes de portais externos |
| `test_agents.py` | Scout, Analyst, Pricer — lógica dos agentes |

**Cobertura estimada:** Baixa-Média (66 funções vs. ~78 arquivos e 8 agentes). WarriorAgent, SentinelAgent, CompilerAgent sem testes dedicados.

### 4.9 TODOs / Pendências

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" modules/bidding --include="*.py"
```

**Resultados:**
```
modules/bidding/agents/analyst_agent.py:167:
  "4. Identifique TODOS os documentos de habilitacao exigidos."
  (texto de prompt para Claude — falso positivo no grep)

modules/bidding/services/edital_parser_service.py:1127:
  # CNPJ padrao brasileiro: XX.XXX.XXX/XXXX-XX
  (comentário de regex — falso positivo)
```

**Pendências reais identificadas por análise:**
1. **WarriorAgent** — integração real com portais requer Playwright + certificado A1 (consta em `warrior_agent.py:6` e `:369`)
2. **Analyst** usa `claude-sonnet-4-20250514` — modelo desatualizado (disponível: `claude-sonnet-4-6`)
3. **Cobertura de testes** baixa em agentes (Warrior, Sentinel, Compiler sem testes)
4. **Prompts Claude** armazenados inline — sem versionamento em arquivo separado
5. **Certificado A1** para login nos portais não implementado

---

## 5. Sumário Executivo

### 5.1 O que Existe vs. o que Falta

| Dimensão | CRM | Vendas | Marketing | Licitações |
|----------|-----|--------|-----------|------------|
| Arquivos .py | 41 | 8 (stubs) | 1 (no CRM) | 78 |
| Models ORM | 5 | 0 | 0* | 13 |
| Endpoints | ~55 | 0 | 8 | ~65 |
| Services | 10 | 0 | 0 | 12 |
| Agentes IA | 0 | 0 | 0 | 8 (1 em dev) |
| Tasks Celery | 0 | 0 | 0 | 11 tasks |
| Integrações ext. | 1 (assinatura) | 0 | 0 | 11 portais/certidões |
| Testes (arquivos) | 17 | 0 | 0 | 4 |
| Testes (funções) | 225 | 0 | 0 | 66 |
| Migrations | 9 | 0 | 0* | 3 |

*Marketing: tabelas existem no banco mas sem ORM model / migration rastreável.

### 5.2 Módulos Maduros vs. Embrionários

**Maduros:**
- **CRM** — pipeline completo (leads → oportunidades → propostas → contratos → comissões), 225 testes, zero TODOs, event bus integrado
- **Licitações** — 8 agentes IA, 6 portais, 11 Celery tasks, Claude API integrada

**Parciais:**
- **Marketing** — funcional mas sem ORM model, sem e-mail marketing real, sem automação

**Embrionários / Stubs:**
- **Vendas** (`modules/comercial/`) — 0% implementado, apenas estrutura de pastas
- **Inteligência** (`modules/inteligencia/`) — 0% implementado, apenas estrutura de pastas

### 5.3 Riscos Técnicos Identificados

1. **WarriorAgent em simulação** — robô de pregão sem integração real; risco de perder licitações que exigem disputa automatizada
2. **Marketing sem ORM** — `marketing_campaigns` / `marketing_leads` via raw SQL = queries não rastreadas pelo ORM, sem type safety
3. **`modules/comercial/` vazio** — se o frontend espera endpoints de Vendas, há risco de 404 não tratado
4. **Analyst usa modelo antigo** — `claude-sonnet-4-20250514` vs. atual `claude-sonnet-4-6`
5. **Cobertura de testes baixa em Licitações** — 66 funções para 78 arquivos; WarriorAgent, SentinelAgent, CompilerAgent sem testes
6. **Solides não integrada ao CRM** — Solides é integração de RH; se produtos/serviços forem migrados do Solides para CRM, não há pipeline
7. **Certificado A1 para portais** — necessário para produção do WarriorAgent, não implementado

### 5.4 Score de Completude por Módulo (0–100)

| Módulo | Score | Justificativa |
|--------|-------|---------------|
| **CRM** | **92/100** | Pipeline completo, 225 testes, event bus. -8 por ausência de agentes IA nativos e automação de e-mail |
| **Licitações** | **78/100** | 8 agentes, 6 portais, Celery tasks. -22 por WarriorAgent em dev, cobertura de testes baixa, modelo Claude desatualizado |
| **Marketing** | **35/100** | Endpoints funcionais. -65 por sem ORM, sem e-mail marketing real, sem automação, sem testes dedicados |
| **Vendas** | **3/100** | Apenas estrutura de pastas. -97 por zero implementação |

### 5.5 Fluxo de Negócios Mapeado

```
Lead (UTM/campanha) ──► Lead CRM ──► Qualificação/Score ──► Oportunidade
        ▲                                                         │
   Marketing                                                  Proposta
   Campanhas                                              (PricingEngine)
        ▲                                                         │
   Licitação ──── Scout ─► Analyst(Claude) ─► Assessor ──► Aprovação
   (PNCP/portais)    └─► Pricer ─► Compiler(PDF) ─► Sentinel    │
                                                              Contrato
                                                         (assinatura digital)
                                                                  │
                                                         Ativo ──► Event Bus
                                                                  │
                                                             GEDEON ──► Operacional
```

### 5.6 Celery Tasks do Menu Negócios

**CRM:** Nenhuma task Celery dedicada.
**Marketing:** Nenhuma task Celery dedicada.
**Licitações — 11 tasks (`tasks/`):**

| Task | Nome Celery | Arquivo |
|------|-------------|---------|
| Sync PNCP oportunidades | `bidding.sync_pncp_oportunidades` | `sync_tasks.py` |
| Sync PNCP preços | `bidding.sync_pncp_precos` | `sync_tasks.py` |
| Atualizar contratos PNCP | `bidding.atualizar_contratos_pncp` | `sync_tasks.py` |
| Verificar certidões | `bidding.verificar_certidoes_vencimento` | `notification_tasks.py` |
| Notificar oportunidade nova | `bidding.notificar_oportunidade_nova` | `notification_tasks.py` |
| Notificar prazo edital | `bidding.notificar_prazo_edital` | `notification_tasks.py` |
| Notificar resultado pipeline | `bidding.notificar_resultado_pipeline` | `notification_tasks.py` |
| Processar pipeline edital | `bidding.processar_pipeline_edital` | `dispute_tasks.py` |
| Monitorar disputa sessão | `bidding.monitorar_disputa_sessao` | `dispute_tasks.py` |
| Verificar resultado licitação | `bidding.verificar_resultado_licitacao` | `dispute_tasks.py` |
| Preparar recursos/impugnação | `bidding.preparar_recursos_impugnacao` | `dispute_tasks.py` |

### 5.7 Integrações Globais Relevantes (Prompt STEP 7)

| Integração | Módulo | Status |
|-----------|--------|--------|
| **Banco Inter** | `financial/` + webhooks em `main_production.py:1039` | ✅ Pix + boleto — **não no CRM/Licitações** |
| **WhatsApp (Evolution API)** | `whatsapp_router` em `main_production.py:929` | ✅ Módulo separado — **não integrado a campanhas** |
| **SMTP** | `core/mailer.py` + `settings.SMTP_*` | ✅ Global — sem uso direto em marketing |
| **SendGrid / Mailgun** | `sprint36_notification_hub` (migration) | ⚠️ Schema criado, implementação pendente |
| **Solides** | `sprint33_solides_integration` | ✅ RH — sem relação com CRM/Licitações |
| **Certificado A1** | `core/credentials/`, `government_integrations/` | ✅ Disponível globalmente — pendente no WarriorAgent |
| **Claude API (Anthropic)** | `bidding/agents/analyst_agent.py` | ✅ `ANTHROPIC_API_KEY`, modelo `claude-sonnet-4-20250514` |

---

RECONHECIMENTO BACKEND CONCLUÍDO — arquivo em /opt/conecta-pro/reconhecimento/cpro11/t4_backend_negocios.md — 761 linhas
