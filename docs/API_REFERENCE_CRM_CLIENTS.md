# API Reference - CRM e Clientes (Conecta PRO)

Documentação completa dos endpoints dos módulos **CRM** (Gestão de Relacionamento) e **Clientes** (Cadastro e Gestão de Clientes/Condomínios).

---

## 📋 Índice

1. [Autenticação](#autenticação)
2. [CRM - Leads](#crm---leads)
3. [CRM - Oportunidades](#crm---oportunidades)
4. [CRM - Propostas](#crm---propostas)
5. [CRM - Contratos](#crm---contratos)
6. [CRM - Comissões](#crm---comissões)
7. [CRM - Dashboard](#crm---dashboard)
8. [Clientes - Gestão de Clientes](#clientes---gestão-de-clientes)
9. [Clientes - Condomínios](#clientes---condomínios)
10. [Clientes - Unidades](#clientes---unidades)
11. [Clientes - Contratos de Serviço](#clientes---contratos-de-serviço)
12. [Clientes - Integrações](#clientes---integrações)

---

## Autenticação

Todas as APIs requerem autenticação via **Bearer Token JWT**.

```http
Authorization: Bearer <token_jwt>
```

---

## CRM - Leads

Base URL: `/api/v1/crm/leads`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar novo lead |
| GET | `/` | Listar leads (com filtros e paginação) |
| GET | `/stats` | Estatísticas de leads |
| GET | `/{lead_id}` | Obter lead por ID |
| PUT | `/{lead_id}` | Atualizar lead |
| PATCH | `/{lead_id}/status` | Atualizar status do lead |
| POST | `/{lead_id}/recalculate-score` | Recalcular score |
| GET | `/{lead_id}/recommended-action` | Ação recomendada |
| DELETE | `/{lead_id}` | Remover lead |

### Schemas

#### LeadCreate
```json
{
  "name": "string",           // obrigatório, min 2, max 255
  "email": "string",          // obrigatório, email válido
  "phone": "string",          // opcional, max 20
  "company": "string",        // opcional, max 255
  "position": "string",       // opcional, max 100
  "company_size": "string",   // opcional, max 50
  "industry": "string",       // opcional, max 100
  "source": "WEBSITE",        // enum: WEBSITE, REFERRAL, SOCIAL_MEDIA, EVENT, COLD_CALL, PARTNER, ADVERTISING, OTHER
  "notes": "string",          // opcional
  "assigned_to_id": "uuid",   // opcional
  "expected_value": 0.0       // opcional, >= 0
}
```

#### LeadUpdate
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "company_size": "string",
  "industry": "string",
  "source": "WEBSITE",
  "status": "NEW",            // NEW, CONTACTED, QUALIFIED, LOST, CONVERTED
  "notes": "string",
  "assigned_to_id": "uuid",
  "expected_value": 0.0,
  "next_contact_at": "2024-01-01T00:00:00"
}
```

#### LeadStatusUpdate
```json
{
  "status": "CONTACTED",
  "notes": "string"
}
```

#### LeadResponse
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "company_size": "string",
  "industry": "string",
  "source": "string",
  "status": "string",
  "score": 75,                // 0-100
  "probability": 50.0,        // 0-100
  "expected_value": 10000.0,
  "notes": "string",
  "assigned_to_id": "uuid",
  "last_contact_at": "2024-01-01T00:00:00",
  "next_contact_at": "2024-01-01T00:00:00",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "is_hot": true,
  "is_qualified": true,
  "weighted_value": 5000.0
}
```

#### LeadStats
```json
{
  "total": 100,
  "by_status": {"NEW": 30, "CONTACTED": 40, "QUALIFIED": 20, "LOST": 5, "CONVERTED": 5},
  "by_source": {"WEBSITE": 50, "REFERRAL": 30, "OTHER": 20},
  "hot_leads": 15,
  "avg_score": 65.5,
  "total_expected_value": 500000.0,
  "total_weighted_value": 250000.0
}
```

---

## CRM - Oportunidades

Base URL: `/api/v1/crm/opportunities`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar oportunidade |
| POST | `/from-lead` | Criar a partir de lead |
| GET | `/` | Listar oportunidades |
| GET | `/pipeline/stats` | Estatísticas do pipeline |
| GET | `/{opportunity_id}` | Obter oportunidade |
| PUT | `/{opportunity_id}` | Atualizar oportunidade |
| PATCH | `/{opportunity_id}/stage` | Mudar estágio |
| POST | `/{opportunity_id}/close` | Fechar oportunidade |
| DELETE | `/{opportunity_id}` | Remover |

### Schemas

#### OpportunityCreate
```json
{
  "title": "string",              // obrigatório, max 255
  "description": "string",
  "contact_name": "string",       // obrigatório
  "contact_email": "string",      // obrigatório, email
  "contact_phone": "string",
  "company_name": "string",
  "value": 0.0,                   // >= 0
  "probability": 10,              // 0-100
  "expected_close_date": "2024-12-31",
  "notes": "string",
  "lead_id": "uuid",
  "stage": "QUALIFICATION",       // QUALIFICATION, PROPOSAL, NEGOTIATION, CLOSED_WON, CLOSED_LOST
  "priority": "MEDIUM",           // LOW, MEDIUM, HIGH, CRITICAL
  "owner_id": "uuid"
}
```

#### OpportunityCreateFromLead
```json
{
  "lead_id": "uuid",              // obrigatório
  "title": "string",
  "description": "string",
  "value": 0.0,
  "probability": 20,
  "expected_close_date": "2024-12-31",
  "priority": "MEDIUM",
  "owner_id": "uuid",
  "notes": "string"
}
```

#### OpportunityStageUpdate
```json
{
  "stage": "PROPOSAL",
  "notes": "string"
}
```

#### OpportunityClose
```json
{
  "won": true,
  "actual_close_date": "2024-01-01",
  "notes": "string",
  "loss_reason": "PRICE",         // PRICE, FEATURES, COMPETITOR, TIMING, BUDGET, OTHER
  "competitor": "string"
}
```

#### PipelineStats
```json
{
  "total_opportunities": 50,
  "open_opportunities": 40,
  "won_opportunities": 8,
  "lost_opportunities": 2,
  "total_value": 1000000.0,
  "weighted_value": 450000.0,
  "won_value": 200000.0,
  "lost_value": 50000.0,
  "win_rate": 80.0,
  "avg_deal_size": 25000.0,
  "avg_days_to_close": 45.5,
  "by_stage": {"QUALIFICATION": 20, "PROPOSAL": 15, "NEGOTIATION": 5},
  "by_priority": {"LOW": 10, "MEDIUM": 25, "HIGH": 10, "CRITICAL": 5},
  "overdue_count": 3
}
```

---

## CRM - Propostas

Base URL: `/api/v1/crm/proposals`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar proposta |
| POST | `/from-opportunity` | Criar de oportunidade |
| GET | `/` | Listar propostas |
| GET | `/stats` | Estatísticas |
| GET | `/templates` | Listar templates |
| GET | `/templates/{id}` | Obter template |
| PUT | `/templates/{id}` | Atualizar template |
| DELETE | `/templates/{id}` | Remover template |
| GET | `/{proposal_id}` | Obter proposta |
| PUT | `/{proposal_id}` | Atualizar |
| POST | `/{proposal_id}/submit` | Submeter |
| POST | `/{proposal_id}/approve` | Aprovar |
| POST | `/{proposal_id}/send` | Enviar ao cliente |
| POST | `/{proposal_id}/accept` | Aceitar (cliente) |
| POST | `/{proposal_id}/reject` | Rejeitar |
| POST | `/{proposal_id}/new-version` | Nova versão |
| DELETE | `/{proposal_id}` | Remover |
| POST | `/{proposal_id}/items` | Adicionar item |
| DELETE | `/{proposal_id}/items/{item_id}` | Remover item |

### Schemas

#### ProposalCreate
```json
{
  "title": "string",
  "description": "string",
  "proposal_type": "SERVICE",     // SERVICE, PRODUCT, MIXED
  "client_name": "string",
  "client_email": "string",
  "client_phone": "string",
  "client_company": "string",
  "client_document": "string",
  "client_address": "string",
  "terms_conditions": "string",
  "payment_terms": "string",
  "payment_conditions": "string",
  "installments": 1,              // 1-120
  "notes": "string",
  "valid_until": "2024-12-31",
  "opportunity_id": "uuid",
  "template_id": "uuid",
  "discount_type": "PERCENTAGE",  // PERCENTAGE, FIXED_AMOUNT
  "discount_value": 0.0,
  "discount_reason": "string",
  "taxes": 0.0,
  "items": [
    {
      "code": "string",
      "name": "string",
      "description": "string",
      "unit": "un",
      "quantity": 1.0,
      "unit_price": 0.0,
      "discount_percent": 0.0,
      "is_optional": false,
      "sort_order": 0
    }
  ]
}
```

#### ProposalSend
```json
{
  "recipient_email": "string",
  "subject": "string",
  "message": "string",
  "cc_emails": ["string"]
}
```

#### ProposalApprovalRequest
```json
{
  "action": "APPROVE",            // APPROVE, REJECT, REQUEST_CHANGES
  "comments": "string"
}
```

#### ProposalStats
```json
{
  "total_proposals": 100,
  "draft_count": 20,
  "pending_count": 15,
  "sent_count": 30,
  "accepted_count": 25,
  "rejected_count": 8,
  "expired_count": 2,
  "total_value": 500000.0,
  "accepted_value": 350000.0,
  "pending_value": 100000.0,
  "acceptance_rate": 75.8,
  "avg_proposal_value": 5000.0,
  "avg_response_time_days": 5.5,
  "by_status": {"DRAFT": 20, "SENT": 30, "ACCEPTED": 25},
  "by_type": {"SERVICE": 80, "PRODUCT": 20}
}
```

---

## CRM - Contratos

Base URL: `/api/v1/crm/contracts`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar contrato |
| POST | `/from-opportunity` | De oportunidade |
| POST | `/from-proposal` | De proposta |
| GET | `/` | Listar |
| GET | `/stats` | Estatísticas |
| GET | `/alerts` | Alertas de contratos |
| GET | `/templates` | Templates |
| GET | `/templates/{id}` | Template específico |
| PUT | `/templates/{id}` | Atualizar template |
| POST | `/templates/{id}/approve` | Aprovar template |
| DELETE | `/templates/{id}` | Remover template |
| GET | `/{contract_id}` | Obter contrato |
| PUT | `/{contract_id}` | Atualizar |
| POST | `/{contract_id}/submit` | Submeter |
| POST | `/{contract_id}/activate` | Ativar |
| POST | `/{contract_id}/suspend` | Suspender |
| POST | `/{contract_id}/terminate` | Rescindir |
| POST | `/{contract_id}/renew` | Renovar |
| POST | `/{contract_id}/calculate-adjustment` | Calcular reajuste |
| DELETE | `/{contract_id}` | Remover |
| POST | `/{contract_id}/items` | Adicionar item |
| PUT | `/{contract_id}/items/{item_id}` | Atualizar item |
| DELETE | `/{contract_id}/items/{item_id}` | Remover item |
| POST | `/{contract_id}/addendums` | Criar aditivo |
| GET | `/{contract_id}/addendums` | Listar aditivos |
| POST | `/addendums/{addendum_id}/sign` | Assinar aditivo |
| POST | `/{contract_id}/sla-reports` | Criar relatório SLA |
| GET | `/{contract_id}/sla-reports` | Listar relatórios SLA |
| POST | `/sla-reports/{report_id}/approve` | Aprovar relatório |
| POST | `/{contract_id}/calculate-sla` | Calcular SLA |

### Schemas

#### ContractCreate
```json
{
  "name": "string",               // obrigatório, min 3, max 200
  "description": "string",
  "contract_type": "RECURRING",   // RECURRING, SPOT, PROJECT
  "monthly_value": "1000.00",
  "total_value": "12000.00",
  "setup_fee": "0.00",
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "grace_period_days": 0,
  "notice_period_days": 30,
  "auto_renewal": true,
  "renewal_period_months": 12,     // 1-60
  "renewal_notification_days": 30,
  "adjustment_enabled": true,
  "adjustment_index": "IGPM",     // IGPM, IPCA, INPC, FIXE
  "adjustment_fixed_percent": null,
  "adjustment_base_date": "2024-01-01",
  "has_sla": false,
  "sla_config": {},
  "signature_required": true,
  "signature_provider": "string",
  "client_id": "uuid",
  "opportunity_id": "uuid",
  "proposal_id": "uuid",
  "template_id": "uuid",
  "content": "string",
  "clauses": [],
  "commercial_manager_id": "uuid",
  "account_manager_id": "uuid"
}
```

#### ContractRenewal
```json
{
  "new_end_date": "2026-01-01",
  "adjustment_percent": 5.0,       // 0-100
  "new_monthly_value": "1050.00"
}
```

#### ContractAddendumCreate
```json
{
  "addendum_type": "ADJUSTMENT",  // ADJUSTMENT, EXTENSION, MODIFICATION, CANCELLATION
  "effective_date": "2024-06-01",
  "description": "string",
  "reason": "string",
  "new_value": "1100.00",
  "adjustment_percent": 10.0,      // -100 a 100
  "adjustment_index": "IGPM"
}
```

#### ContractSLAReportCreate
```json
{
  "year": 2024,
  "month": 6,
  "indicators": [
    {
      "name": "string",
      "target": "95.00",
      "actual": "97.50",
      "achieved": true,
      "weight": "1.0"
    }
  ],
  "overall_score": "97.5",         // 0-150
  "penalty_applied": false,
  "penalty_percent": null,         // 0-100
  "penalty_amount": null
}
```

#### ContractStats
```json
{
  "total_contracts": 150,
  "active_contracts": 120,
  "total_monthly_revenue": "150000.00",
  "average_contract_value": "1250.00",
  "expiring_soon": 5,
  "needs_adjustment": 3,
  "by_status": {"ACTIVE": 120, "PENDING": 20, "SUSPENDED": 5, "TERMINATED": 5},
  "by_type": {"RECURRING": 130, "SPOT": 15, "PROJECT": 5}
}
```

---

## CRM - Comissões

Base URL: `/api/v1/crm/commissions`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/rules` | Criar regra de comissão |
| GET | `/rules` | Listar regras |
| GET | `/rules/{rule_id}` | Obter regra |
| PUT | `/rules/{rule_id}` | Atualizar regra |
| DELETE | `/rules/{rule_id}` | Remover regra |
| POST | `/seller-rules` | Associar regra a vendedor |
| POST | `/calculate` | Calcular comissão |
| GET | `/` | Listar comissões |
| GET | `/stats` | Estatísticas |
| GET | `/seller/{seller_id}/stats` | Stats por vendedor |
| GET | `/{commission_id}` | Obter comissão |
| PUT | `/{commission_id}` | Atualizar |
| PATCH | `/{commission_id}/status` | Atualizar status |
| POST | `/{commission_id}/approve` | Aprovar |
| DELETE | `/{commission_id}` | Remover |
| POST | `/payments` | Registrar pagamento |
| POST | `/payments/{payment_id}/confirm` | Confirmar pagamento |
| GET | `/summaries` | Resumos mensais |
| GET | `/rankings` | Ranking de vendedores |
| POST | `/summaries/{summary_id}/close` | Fechar período |

### Schemas

#### CommissionRuleCreate
```json
{
  "name": "string",
  "description": "string",
  "commission_type": "PERCENTAGE", // PERCENTAGE, FIXED_AMOUNT, PROGRESSIVE, MIXED
  "base_value": 10.0,              // percentual ou valor fixo
  "min_value": null,
  "max_value": null,
  "trigger": "ON_FIRST_PAYMENT",   // ON_SIGNATURE, ON_FIRST_PAYMENT, ON_INSTALLMENT, ON_RENEWAL
  "trigger_delay_days": 0,
  "progressive_scale": [
    {"min": 0, "max": 50000, "rate": 5.0},
    {"min": 50000, "max": 100000, "rate": 7.5}
  ],
  "applies_to_all": true,
  "product_categories": ["string"],
  "service_types": ["string"],
  "min_sale_value": null,
  "max_sale_value": null,
  "valid_from": "2024-01-01",
  "valid_until": null,
  "priority": 0
}
```

#### CommissionCalculateRequest
```json
{
  "seller_id": "uuid",
  "proposal_id": "uuid",
  "sale_value": 10000.0,
  "sale_margin": 3000.0,
  "rule_id": "uuid"                // opcional
}
```

#### CommissionCreate
```json
{
  "seller_id": "uuid",
  "proposal_id": "uuid",
  "sale_value": 10000.0,
  "sale_margin": 3000.0,
  "description": "string",
  "notes": "string",
  "rule_id": "uuid",
  "commission_type": "PERCENTAGE",
  "commission_rate": 10.0,
  "trigger": "ON_FIRST_PAYMENT",
  "trigger_date": "2024-01-01",
  "due_date": "2024-02-01",
  "period_start": "2024-01-01",
  "period_end": "2024-01-31"
}
```

#### CommissionPaymentCreate
```json
{
  "commission_id": "uuid",
  "amount": 1000.0,
  "payment_method": "PAYROLL",     // PAYROLL, BANK_TRANSFER, PIX, CHECK, CASH
  "payment_date": "2024-01-15",
  "payment_reference": "string",
  "bank_account": "string",
  "transaction_id": "string",
  "notes": "string"
}
```

#### CommissionStats
```json
{
  "total_commissions": 100,
  "pending_count": 30,
  "approved_count": 50,
  "paid_count": 18,
  "cancelled_count": 2,
  "total_value": 50000.0,
  "pending_value": 15000.0,
  "approved_value": 25000.0,
  "paid_value": 9500.0,
  "overdue_count": 5,
  "overdue_value": 2500.0,
  "avg_commission_value": 500.0,
  "avg_days_to_payment": 15.5,
  "by_status": {"PENDING": 30, "APPROVED": 50, "PAID": 18, "CANCELLED": 2},
  "by_trigger": {"ON_FIRST_PAYMENT": 70, "ON_SIGNATURE": 30},
  "by_month": {"2024-01": 5000.0, "2024-02": 7000.0}
}
```

---

## CRM - Dashboard

Base URL: `/api/v1/crm/dashboard`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/kpis` | KPIs principais |
| GET | `/funnel` | Dados do funil |
| GET | `/trends/leads` | Tendência de leads |
| GET | `/trends/sales` | Tendência de vendas |
| GET | `/trends/commissions` | Tendência de comissões |
| GET | `/conversion-rates` | Taxas de conversão |
| GET | `/seller/{seller_id}/performance` | Performance do vendedor |
| GET | `/top-performers` | Top performers |
| GET | `/charts/leads-by-status` | Gráfico leads |
| GET | `/charts/opportunities-by-stage` | Gráfico oportunidades |
| GET | `/charts/proposals-by-status` | Gráfico propostas |
| GET | `/charts/commissions-by-status` | Gráfico comissões |

---

## Clientes - Gestão de Clientes

Base URL: `/api/v1/clients`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/` | Criar cliente |
| GET | `/` | Listar clientes |
| GET | `/stats` | Estatísticas |
| GET | `/{client_id}` | Obter cliente |
| GET | `/{client_id}/full` | Cliente completo |
| PUT | `/{client_id}` | Atualizar |
| DELETE | `/{client_id}` | Remover |
| POST | `/{client_id}/activate` | Ativar |
| POST | `/{client_id}/suspend` | Suspender |
| POST | `/{client_id}/block` | Bloquear |
| POST | `/{client_id}/set-defaulter` | Marcar inadimplente |
| POST | `/{client_id}/clear-defaulter` | Limpar inadimplência |
| POST | `/{client_id}/enable-guardian` | Ativar Guardian |
| POST | `/{client_id}/enable-plus` | Ativar Plus |
| POST | `/{client_id}/condominiums` | Criar condomínio |
| GET | `/{client_id}/condominiums` | Listar condomínios |
| POST | `/{client_id}/contracts` | Criar contrato |
| GET | `/{client_id}/contracts` | Listar contratos |
| POST | `/{client_id}/integrations` | Criar integração |
| GET | `/{client_id}/integrations` | Listar integrações |

### Schemas

#### ClientCreate
```json
{
  "type": "CONDOMINIO",           // CONDOMINIO, COMPANY, PERSON, GOVERNMENT
  "segment": "RESIDENTIAL",       // RESIDENTIAL, COMMERCIAL, INDUSTRIAL, MIXED
  "legal_name": "string",
  "trade_name": "string",
  "document_type": "CNPJ",        // CPF, CNPJ
  "document_number": "string",
  "state_registration": "string",
  "municipal_registration": "string",
  "address_street": "string",
  "address_number": "string",
  "address_complement": "string",
  "address_neighborhood": "string",
  "address_city": "string",
  "address_state": "string",      // 2 caracteres
  "address_zipcode": "string",
  "latitude": null,
  "longitude": null,
  "phone": "string",
  "phone_secondary": "string",
  "whatsapp": "string",
  "email": "string",
  "email_billing": "string",
  "website": "string",
  "contact_name": "string",
  "contact_phone": "string",
  "contact_email": "string",
  "contact_role": "string",
  "payment_terms": 30,             // 0-365
  "credit_limit": "10000.00",
  "sales_rep_id": "uuid",
  "sales_rep_name": "string",
  "acquisition_source": "string",
  "settings": {},
  "tags": ["string"],
  "notes": "string",
  "is_vip": false
}
```

#### ClientResponse
```json
{
  "id": "uuid",
  "code": "CLI00001",
  "type": "CONDOMINIO",
  "status": "ACTIVE",              // ACTIVE, INACTIVE, SUSPENDED, BLOCKED
  "segment": "RESIDENTIAL",
  "legal_name": "string",
  "trade_name": "string",
  "document_type": "CNPJ",
  "document_number": "string",
  "formatted_document": "00.000.000/0000-00",
  "display_name": "string",
  "full_address": "string",
  "address_street": "string",
  "address_number": "string",
  "address_complement": "string",
  "address_neighborhood": "string",
  "address_city": "string",
  "address_state": "SP",
  "address_zipcode": "string",
  "phone": "string",
  "email": "string",
  "contact_name": "string",
  "payment_terms": 30,
  "credit_limit": "10000.00",
  "current_balance": "0.00",
  "is_defaulter": false,
  "total_debt": "0.00",
  "total_contracts": 3,
  "active_contracts": 2,
  "total_revenue": "50000.00",
  "satisfaction_score": "95.0",
  "health_score": 85,
  "guardian_enabled": true,
  "plus_enabled": false,
  "is_active": true,
  "is_vip": false,
  "tags": ["premium"],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### ClientStats
```json
{
  "total_clients": 150,
  "active_clients": 120,
  "inactive_clients": 20,
  "defaulter_clients": 5,
  "vip_clients": 10,
  "by_type": {"CONDOMINIO": 100, "COMPANY": 40, "PERSON": 10},
  "by_status": {"ACTIVE": 120, "INACTIVE": 20, "SUSPENDED": 5, "BLOCKED": 5},
  "by_segment": {"RESIDENTIAL": 80, "COMMERCIAL": 50, "INDUSTRIAL": 15, "MIXED": 5},
  "total_revenue": "500000.00",
  "average_contracts_per_client": 2.5
}
```

---

## Clientes - Condomínios

Base URL: `/api/v1/clients`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/condominiums/stats` | Estatísticas |
| GET | `/condominiums/{condominium_id}` | Obter condomínio |
| PUT | `/condominiums/{condominium_id}` | Atualizar |
| DELETE | `/condominiums/{condominium_id}` | Remover |
| POST | `/condominiums/{condominium_id}/activate` | Ativar |
| POST | `/condominiums/{condominium_id}/start-implantation` | Iniciar implantação |
| POST | `/condominiums/{condominium_id}/finish-implantation` | Finalizar implantação |
| POST | `/condominiums/{condominium_id}/units` | Criar unidade |
| GET | `/condominiums/{condominium_id}/units` | Listar unidades |
| GET | `/condominiums/{condominium_id}/units/stats` | Estatísticas de unidades |

### Schemas

#### CondominiumCreate
```json
{
  "client_id": "uuid",
  "name": "string",
  "type": "RESIDENTIAL",          // RESIDENTIAL, COMMERCIAL, INDUSTRIAL, MIXED, CORPORATE
  "administration_type": "PROFESSIONAL", // PROFESSIONAL, VOLUNTARY, SELF_MANAGED
  "cnpj": "string",
  "address_street": "string",
  "address_number": "string",
  "address_complement": "string",
  "address_neighborhood": "string",
  "address_city": "string",
  "address_state": "SP",
  "address_zipcode": "string",
  "latitude": null,
  "longitude": null,
  "phone": "string",
  "phone_portaria": "string",
  "email": "string",
  "syndic_name": "string",
  "syndic_phone": "string",
  "syndic_email": "string",
  "total_units": 100,
  "total_towers": 2,
  "total_floors": 15,
  "total_elevators": 4,
  "total_parking_spots": 120,
  "total_area_m2": "5000.00",
  "has_pool": true,
  "has_gym": true,
  "has_party_room": true,
  "has_playground": false,
  "has_24h_security": true,
  "has_cctv": true,
  "has_access_control": true,
  "settings": {},
  "tags": ["premium"],
  "notes": "string"
}
```

#### CondominiumResponse
```json
{
  "id": "uuid",
  "code": "COND00001",
  "client_id": "uuid",
  "name": "string",
  "type": "RESIDENTIAL",
  "status": "ACTIVE",              // ACTIVE, INACTIVE, IMPLANTATION, SUSPENDED
  "administration_type": "PROFESSIONAL",
  "cnpj": "string",
  "full_address": "string",
  "address_city": "string",
  "address_state": "SP",
  "syndic_name": "string",
  "syndic_phone": "string",
  "syndic_mandate_active": true,
  "total_units": 100,
  "occupied_units": 95,
  "occupancy_rate": 95.0,
  "total_towers": 2,
  "security_level": "HIGH",        // BASIC, STANDARD, HIGH, PREMIUM
  "amenities_count": 5,
  "guardian_enabled": true,
  "plus_enabled": false,
  "is_active": true,
  "is_premium": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### CondominiumStats
```json
{
  "total_condominiums": 100,
  "active_condominiums": 85,
  "total_units": 5000,
  "occupied_units": 4750,
  "average_occupancy_rate": 95.0,
  "by_type": {"RESIDENTIAL": 60, "COMMERCIAL": 25, "MIXED": 15},
  "by_status": {"ACTIVE": 85, "IMPLANTATION": 10, "INACTIVE": 5},
  "by_city": {"São Paulo": 40, "Rio de Janeiro": 20, "Belo Horizonte": 15}
}
```

---

## Clientes - Unidades

Base URL: `/api/v1/clients`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/units/{unit_id}` | Obter unidade |
| PUT | `/units/{unit_id}` | Atualizar |
| DELETE | `/units/{unit_id}` | Remover |
| POST | `/units/{unit_id}/set-owner` | Definir proprietário |
| POST | `/units/{unit_id}/set-resident` | Definir morador |
| POST | `/units/{unit_id}/clear-resident` | Limpar morador |

### Schemas

#### UnitCreate
```json
{
  "condominium_id": "uuid",
  "number": "101",
  "block": "A",
  "tower": "Torre 1",
  "floor": 1,
  "type": "APARTAMENTO",          // APARTAMENTO, SALA_COMERCIAL, LOJA, GARAGEM, DEPOSITO, OUTRO
  "area_m2": "85.50",
  "bedrooms": 3,
  "bathrooms": 2,
  "parking_spots": 2,
  "owner_name": "string",
  "owner_document": "string",
  "owner_phone": "string",
  "owner_email": "string",
  "monthly_fee": "500.00",
  "fraction": "0.01",             // 0-1
  "notes": "string",
  "tags": ["string"]
}
```

#### UnitUpdate
```json
{
  "number": "101",
  "block": "A",
  "tower": "Torre 1",
  "floor": 1,
  "type": "APARTAMENTO",
  "status": "OCCUPIED",            // VACANT, OCCUPIED, RENOVATION, RESERVED
  "area_m2": "85.50",
  "bedrooms": 3,
  "bathrooms": 2,
  "parking_spots": 2,
  "owner_name": "string",
  "owner_document": "string",
  "owner_phone": "string",
  "owner_email": "string",
  "resident_name": "string",
  "resident_phone": "string",
  "resident_email": "string",
  "is_tenant": false,
  "monthly_fee": "500.00",
  "notes": "string",
  "tags": ["string"]
}
```

#### UnitResponse
```json
{
  "id": "uuid",
  "code": "UNI00001",
  "condominium_id": "uuid",
  "number": "101",
  "block": "A",
  "tower": "Torre 1",
  "floor": 1,
  "type": "APARTAMENTO",
  "status": "OCCUPIED",
  "display_name": "A-101 - Torre 1",
  "short_name": "101-A",
  "area_m2": "85.50",
  "bedrooms": 3,
  "parking_spots": 2,
  "owner_name": "string",
  "resident_name": "string",
  "current_resident": "string",
  "is_tenant": false,
  "is_occupied": true,
  "monthly_fee": "500.00",
  "total_fee": "550.00",
  "is_defaulter": false,
  "debt_amount": "0.00",
  "has_access_credentials": true,
  "total_authorized_persons": 5,
  "total_vehicles": 2,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### UnitStats
```json
{
  "total_units": 100,
  "occupied_units": 95,
  "available_units": 5,
  "defaulter_units": 3,
  "occupancy_rate": 95.0,
  "by_type": {"APARTAMENTO": 80, "SALA_COMERCIAL": 15, "GARAGEM": 5},
  "by_status": {"OCCUPIED": 95, "VACANT": 5},
  "total_monthly_fees": "50000.00"
}
```

---

## Clientes - Contratos de Serviço

Base URL: `/api/v1/clients`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/contracts/{contract_id}` | Obter contrato |
| PUT | `/contracts/{contract_id}` | Atualizar |
| POST | `/contracts/{contract_id}/activate` | Ativar |
| POST | `/contracts/{contract_id}/suspend` | Suspender |
| POST | `/contracts/{contract_id}/cancel` | Cancelar |

### Schemas

#### ClientContractCreate
```json
{
  "client_id": "uuid",
  "contract_id": "uuid",
  "condominium_id": "uuid",
  "service_type": "GUARDIAN",      // GUARDIAN, GUARDIAN_PLUS, INTEGRATION, CONSULTING, CUSTOM
  "description": "string",
  "scope": "string",
  "monthly_value": "2500.00",
  "setup_fee": "5000.00",
  "discount_percentage": 10.0,
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "sla_response_time_minutes": 30,
  "sla_resolution_time_hours": 24,
  "is_24h": true,
  "auto_renew": true,
  "settings": {},
  "features": ["feature1", "feature2"],
  "notes": "string"
}
```

#### ClientContractResponse
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "contract_id": "uuid",
  "condominium_id": "uuid",
  "service_type": "GUARDIAN",
  "status": "ACTIVE",              // PENDING, ACTIVE, SUSPENDED, CANCELLED, EXPIRED
  "description": "string",
  "monthly_value": "2500.00",
  "final_value": "2250.00",
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "days_until_end": 180,
  "is_expiring_soon": false,
  "is_guardian_service": true,
  "is_plus_service": false,
  "is_active": true,
  "is_main_service": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

## Clientes - Integrações

Base URL: `/api/v1/clients`

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/integrations/{integration_id}` | Obter integração |
| PUT | `/integrations/{integration_id}` | Atualizar |
| DELETE | `/integrations/{integration_id}` | Remover |
| POST | `/integrations/{integration_id}/test` | Testar conexão |
| POST | `/integrations/{integration_id}/sync` | Sincronizar |
| GET | `/integrations/{integration_id}/logs` | Logs de sincronização |

### Schemas

#### IntegrationSettingsCreate
```json
{
  "client_id": "uuid",
  "integration_type": "ERP",      // ERP, ACCOUNTING, ACCESS_CONTROL, FINANCIAL, OTHER
  "name": "string",
  "description": "string",
  "sync_direction": "BIDIRECTIONAL", // TO_EXTERNAL, FROM_EXTERNAL, BIDIRECTIONAL
  "api_url": "string",
  "api_key": "string",
  "api_secret": "string",
  "webhook_url": "string",
  "webhook_secret": "string",
  "sync_interval_minutes": 60,
  "auto_sync": true,
  "sync_on_change": true,
  "settings": {},
  "notes": "string"
}
```

#### IntegrationSettingsResponse
```json
{
  "id": "uuid",
  "client_id": "uuid",
  "integration_type": "ERP",
  "name": "string",
  "description": "string",
  "sync_status": "SYNCED",        // NEVER_SYNCED, SYNCING, SYNCED, ERROR, PAUSED
  "sync_direction": "BIDIRECTIONAL",
  "api_url": "string",
  "external_client_id": "string",
  "webhook_url": "string",
  "sync_interval_minutes": 60,
  "last_sync_at": "2024-01-01T00:00:00",
  "last_sync_success_at": "2024-01-01T00:00:00",
  "last_sync_error": null,
  "success_rate": 98.5,
  "total_syncs": 100,
  "records_synced": 5000,
  "is_configured": true,
  "is_enabled": true,
  "is_active": true,
  "auto_sync": true,
  "created_at": "2024-01-01T00:00:00"
}
```

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 204 | No Content - Sucesso sem conteúdo |
| 400 | Bad Request - Requisição inválida |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 500 | Internal Server Error - Erro interno |

---

## Paginação

Listas paginadas retornam:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

Parâmetros de query:
- `page`: Número da página (default: 1)
- `page_size`: Itens por página (default: 20, max: 100)
- `search`: Busca textual

---

## Filtros Comuns

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `date_from` | Data inicial | `2024-01-01` |
| `date_to` | Data final | `2024-12-31` |
| `status` | Status | `ACTIVE`, `PENDING` |
| `search` | Busca textual | `nome empresa` |
| `min_value` | Valor mínimo | `1000.00` |
| `max_value` | Valor máximo | `10000.00` |

---

## Versionamento

A API está na versão **v1**. A versão é incluída na URL:

```
/api/v1/crm/...
/api/v1/clients/...
```

---

*Documentação gerada em: Fevereiro 2026*
*Versão da API: 2.0.0*
