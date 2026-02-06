# INTEGRATIONS MASTERPLAN - CONECTA PRO
**Mapeamento Arquitetural Atual + Plano de Integração com Sólides/Domínio/Bling/GOV.BR**

---

## 📋 1. MAPEAMENTO ARQUITETURAL ATUAL

### 1.1. Estrutura Atual de Integrações

#### **modules/integrations/** (Existente)
```
modules/integrations/
├── banking/                    # Integrações bancárias
│   ├── adapters/              # BB, Itaú, Bradesco
│   ├── controllers/           # REST endpoints
│   ├── models/                # SQLAlchemy models  
│   ├── repositories/          # Data access layer
│   ├── schemas/               # Pydantic schemas
│   └── services/              # Business logic
├── whatsapp/                  # WhatsApp Business API
│   ├── controllers/
│   ├── models/               # Templates, Queue, Logs, Config
│   ├── repositories/
│   └── schemas/
└── email/                    # Email integrations (presumido)
```

#### **modules/government_integrations/** (Existente)
```
modules/government_integrations/
├── controllers/               # REST API endpoints
│   ├── esocial_controller.py
│   ├── fgts_inss_controller.py
│   ├── receita_federal_controller.py  
│   ├── sefaz_controller.py
│   └── status_controller.py
├── core/                     # Core engines (business logic)
│   ├── esocial_transmitter.py
│   ├── fgts_inss_manager.py
│   └── sefaz_manager.py
├── models/                   # SQLAlchemy models
├── repositories/             # Data access layer
├── schemas/                  # Pydantic schemas por órgão
│   ├── common.py
│   ├── esocial.py
│   ├── fgts_inss.py
│   ├── receita_federal.py
│   └── sefaz.py
├── services/                 # Service layer
│   ├── esocial_service.py
│   ├── fgts_inss_service.py
│   ├── receita_federal_service.py
│   └── sefaz_service.py
└── utils.py                  # Utilities (CPF/CNPJ validation)
```

### 1.2. Estrutura de Autenticação e Segurança

#### **core/auth/** (Sistema de Auth Atual)
```
core/auth/
├── jwt.py                    # JWT token handling
├── security.py              # Password hashing, validation
├── dependencies.py           # FastAPI auth dependencies
└── dependencies_fixed.py    # Auth dependencies (version 2?)
```

#### **core/security/** 
```
core/security/
├── rate_limiter.py          # Rate limiting middleware
└── __init__.py
```

#### **modules/security_lgpd/** (Compliance)
```
modules/security_lgpd/        # LGPD compliance module
```

#### **modules/audit/** (Auditoria)
```
modules/audit/                # Audit trails e compliance  
```

### 1.3. Padrões de Error Handling e Logging

#### **Logging Estruturado**
- **Path**: `core/logging/`
- **Security Logger**: `core/logging/security_logger.py`
- **JSON Logging**: Configurado para produção
- **Correlation IDs**: Implementado para tracking

#### **Error Handling Patterns**
- **FastAPI Exception Handlers**: Padronizados
- **HTTP Status Codes**: Seguindo RFC 7807
- **Error Schemas**: Pydantic schemas para responses

### 1.4. Observabilidade Stack

#### **Métricas (Prometheus)**
- **Endpoint**: http://82.25.75.74:9090
- **Exporters**: Node, Redis, Postgres
- **Custom Metrics**: Aplicação (presumido)

#### **Dashboards (Grafana)**  
- **Endpoint**: http://82.25.75.74:3000
- **Dashboards**: Sistema, aplicação, business metrics

#### **Logs Centralizados**
- **Estrutura**: JSON logging
- **Correlação**: Correlation IDs
- **Retention**: Configurado para compliance

### 1.5. Rotas e API Structure

#### **api/v1/__init__.py** (Router Principal)
```python
# Estrutura atual de routers (evidência):
- auth_router
- integrations routers (banking, whatsapp, government)
- business modules routers (CRM, operacional, financial, etc.)
```

#### **main.py** (App Principal)  
```python
# FastAPI app setup
- Include api/v1 router  
- Middleware stack (CORS, security, rate limiting)
- Lifespan management (DB, Redis connections)
```

### 1.6. Padrões de Schemas e Repositories

#### **Pydantic V2 Patterns**
- **Request/Response schemas** separados
- **Validation rules** centralizados
- **Enum classes** para constants
- **Field validation** com error messages customizados

#### **Repository Pattern**
- **SQLAlchemy Async**: Base repository class
- **CRUD operations**: Standardizados
- **Transaction management**: Async context managers
- **Multi-tenant support**: tenant_id em todas as entities

### 1.7. Rate Limiting e Headers

#### **Rate Limiting**
- **Implementation**: `core/security/rate_limiter.py`
- **Strategy**: Presumivelmente Redis-backed
- **Scopes**: Por usuário, por endpoint, global

#### **Standard Headers**
- **CORS**: Configurado no middleware
- **Security Headers**: X-Frame-Options, CSP, etc.
- **API Version**: Via URL path (/api/v1/)

---

## 📊 2. ANÁLISE DE GAPS E NECESSIDADES

### 2.1. Gaps Identificados para Nova Arquitetura

#### **❌ Faltando para Integration Framework**
1. **Connector Interface Padronizada**: Não há interface comum
2. **Sync Engine**: Sem orquestração de sincronização
3. **ID Mapping**: Sem mapeamento id_externo ↔ id_interno  
4. **Webhook Inbox**: Sem receptor padronizado
5. **Integration Accounts**: Sem gestão de credenciais multi-tenant
6. **Dead Letter Queue**: Sem tratamento de falhas persistentes
7. **State Management**: Sem cursor/state incremental
8. **Circuit Breaker**: Sem proteção contra cascading failures

#### **⚠️ Needs Enhancement**
1. **Government Integrations**: Existem mas podem estar em estado mock/placeholder
2. **Observability**: Metrics existem, mas precisam ser específicos para integrations
3. **LGPD Audit**: Módulo existe, mas precisa integrar com novo framework

### 2.2. Força Atual (A Aproveitar)

#### **✅ Infraestrutura Sólida**
- Multi-tenant architecture ✅
- Async SQLAlchemy + FastAPI ✅  
- JWT Authentication ✅
- Structured logging ✅
- Prometheus + Grafana ✅
- Rate limiting ✅
- LGPD compliance módule ✅
- Audit trails ✅

#### **✅ Patterns Estabelecidos**  
- Repository pattern ✅
- Controller/Service/Repository layers ✅
- Pydantic V2 schemas ✅
- Error handling padronizado ✅
- Migration management (Alembic) ✅

---

## 🏗️ 3. NOVA ARQUITETURA DE INTEGRAÇÃO (PROPOSTA)

### 3.1. Integration Framework Structure

```
modules/integrations/
├── base/                      # 🆕 Foundation layer
│   ├── interfaces/
│   │   ├── connector.py      # IConnector interface
│   │   ├── authenticator.py  # IAuthenticator interface
│   │   └── mapper.py         # IMapper interface
│   ├── exceptions/
│   │   ├── integration_errors.py
│   │   ├── auth_errors.py
│   │   └── sync_errors.py
│   ├── retry/
│   │   ├── circuit_breaker.py
│   │   ├── retry_manager.py  
│   │   └── backoff_strategies.py
│   └── auth_strategies/
│       ├── api_key_auth.py
│       ├── oauth2_auth.py
│       └── mtls_auth.py
│
├── connectors/               # 🆕 External system connectors  
│   ├── bling/
│   │   ├── connector.py
│   │   ├── authenticator.py
│   │   ├── client.py
│   │   └── mappers/
│   │       ├── cliente_mapper.py
│   │       ├── produto_mapper.py
│   │       └── pedido_mapper.py
│   ├── solides/
│   │   ├── connector.py
│   │   ├── authenticator.py  
│   │   ├── client.py
│   │   └── mappers/
│   │       ├── colaborador_mapper.py
│   │       └── escala_mapper.py
│   └── dominio/
│       ├── connector.py
│       ├── authenticator.py
│       ├── client.py
│       └── mappers/
│
├── sync/                     # 🆕 Synchronization engine
│   ├── engine.py            # Main sync orchestrator
│   ├── jobs/                # Sync jobs por entidade
│   │   ├── base_job.py
│   │   ├── cliente_sync_job.py
│   │   ├── produto_sync_job.py
│   │   └── colaborador_sync_job.py
│   ├── mappers/             # Transformation layer
│   ├── validators/          # Data validation
│   └── conflict_resolution/ # Conflict handling
│
├── models/                  # 🆕 Integration persistence
│   ├── integration_account.py  # Tenant credentials
│   ├── sync_run.py             # Execution tracking
│   ├── sync_state.py           # Incremental cursors
│   ├── id_map.py               # External ↔ Internal ID mapping
│   ├── webhook_inbox.py        # Webhook reception
│   └── dead_letter_queue.py    # Failed message handling
│
├── schemas/                 # 🆕 API contracts
│   ├── requests/
│   │   ├── sync_request.py
│   │   ├── account_request.py
│   │   └── webhook_request.py
│   └── responses/
│       ├── sync_response.py
│       ├── account_response.py
│       └── health_response.py
│
├── services/               # 🆕 Business services
│   ├── integration_registry_service.py
│   ├── sync_service.py
│   ├── webhook_service.py
│   ├── credentials_service.py
│   └── observability_service.py
│
└── controllers/            # 🆕 REST endpoints
    ├── integration_controller.py
    ├── sync_controller.py
    ├── webhook_controller.py
    └── health_controller.py
```

### 3.2. Government Integrations Enhancement

```
modules/government_integrations/
├── adapters/               # 🆕 Adapter pattern per gov entity
│   ├── esocial/
│   │   ├── esocial_adapter.py
│   │   ├── events/         # S-1000, S-2200, etc.
│   │   └── schemas/
│   ├── sefaz/
│   │   ├── sefaz_adapter.py
│   │   ├── nfe/
│   │   ├── cte/
│   │   └── mdfe/
│   ├── receita_federal/
│   │   ├── rf_adapter.py
│   │   └── consultas/
│   └── nfse/
│       ├── nfse_adapter.py
│       └── municipios/     # Municipal specific implementations
│
├── signing/               # 🆕 Digital signature layer
│   ├── certificate_manager.py   # A1/A3 cert handling
│   ├── xml_signer.py            # XML digital signature
│   ├── icp_brasil_validator.py  # Certificate chain validation
│   └── hsm_integration.py       # Hardware Security Module
│
├── transport/             # 🆕 Government webservice transport
│   ├── soap_client.py
│   ├── rest_client.py
│   └── mtls_client.py     # Mutual TLS
│
├── queues/               # 🆕 Async government operations
│   ├── submission_queue.py
│   ├── retry_queue.py
│   └── status_polling_queue.py
│
└── audit/                # 🆕 Government compliance audit
    ├── append_only_events.py
    ├── compliance_logger.py
    └── retention_manager.py
```

---

## 🔄 4. INTEGRATION ENDPOINTS (REST API)

### 4.1. Core Integration Management

```http
# Connector Management
GET    /api/v1/integrations/connectors                    # List available connectors
POST   /api/v1/integrations/accounts                     # Create tenant credentials
GET    /api/v1/integrations/accounts                     # List accounts
PATCH  /api/v1/integrations/accounts/{id}               # Update account
DELETE /api/v1/integrations/accounts/{id}               # Delete account

# Sync Management
POST   /api/v1/integrations/sync/run                    # Trigger manual sync
GET    /api/v1/integrations/sync/runs                   # List sync history
GET    /api/v1/integrations/sync/runs/{id}              # Get sync details
POST   /api/v1/integrations/sync/runs/{id}/retry        # Retry failed sync

# Health & Testing
GET    /api/v1/integrations/health                      # Overall integration health
GET    /api/v1/integrations/health/{connector}          # Test specific connector
POST   /api/v1/integrations/test-connection             # Test credentials

# Webhook Management  
POST   /api/v1/integrations/webhooks/{connector}        # Webhook inbox
GET    /api/v1/integrations/webhooks/history            # Webhook history
POST   /api/v1/integrations/webhooks/{id}/replay        # Replay webhook

# Observability
GET    /api/v1/integrations/metrics                     # Integration metrics
GET    /api/v1/integrations/logs                        # Integration logs
GET    /api/v1/integrations/alerts                      # Active alerts
```

### 4.2. Government Integration Endpoints

```http
# Government Webservices
POST   /api/v1/government/esocial/events                # Submit eSocial events
GET    /api/v1/government/esocial/status/{protocol}     # Check submission status
POST   /api/v1/government/sefaz/nfe                     # Submit NF-e
GET    /api/v1/government/sefaz/nfe/{chave}/status      # Check NF-e status
POST   /api/v1/government/receita/consulta              # Query Receita Federal

# Certificate Management
POST   /api/v1/government/certificates                  # Upload certificate
GET    /api/v1/government/certificates                  # List certificates
POST   /api/v1/government/certificates/{id}/validate   # Validate certificate
```

---

## 🔐 5. SEGURANÇA E COMPLIANCE

### 5.1. Credential Management

#### **Encryption at Rest**
- **Symmetric Encryption**: AES-256 for API keys/secrets
- **Key Management**: Rotate encryption keys
- **HSM Integration**: For government certificates (A3)
- **Zero-Knowledge**: Conecta PRO não pode ver credenciais em plain text

#### **Multi-Tenant Isolation**
- **Tenant Scoping**: All integration accounts scoped to tenant
- **Role-Based Access**: Admin, Integration Manager, Read-Only
- **Audit Trail**: All credential access logged

### 5.2. LGPD Compliance

#### **Data Classification**
- **PII Data**: CPF, RG, endereço, telefone, email
- **Sensitive Data**: Salário, folha de pagamento, histórico médico
- **Business Data**: CNPJ, razão social, endereço comercial
- **Government Data**: Protocolos, guias, certidões

#### **Privacy Controls**
- **Data Minimization**: Only sync required fields
- **Pseudonymization**: Hash PII when possible  
- **Right to Erasure**: Cascade deletion across integrations
- **Consent Management**: Track consent per integration

#### **Audit Requirements**
- **Access Logs**: Who accessed what data when
- **Change Logs**: All data modifications tracked
- **Integration Logs**: All external system interactions
- **Retention Policy**: 5 years for fiscal, 30 days for operational

---

## 📊 6. OBSERVABILITY ENHANCEMENT

### 6.1. New Prometheus Metrics

```python
# Sync Performance
conecta_sync_duration_seconds{connector, entity, tenant}
conecta_sync_items_processed{connector, entity, tenant}
conecta_sync_errors_total{connector, entity, error_type, tenant}
conecta_sync_lag_seconds{connector, entity, tenant}

# API Health  
conecta_connector_health_status{connector, tenant}
conecta_api_response_time{connector, endpoint, tenant}
conecta_api_rate_limit_remaining{connector, tenant}

# Data Quality
conecta_mapping_errors_total{connector, entity, field, tenant}
conecta_validation_errors_total{connector, entity, rule, tenant}
conecta_duplicate_records_total{connector, entity, tenant}

# Government Specific
conecta_gov_submission_duration{gov_entity, event_type, tenant}
conecta_gov_queue_size{gov_entity, queue_type, tenant}
conecta_gov_certificate_expiry_days{certificate_id, tenant}
```

### 6.2. Business KPIs Dashboard

#### **Integration Health Dashboard**
- **Connector Uptime**: 99.9% target
- **Sync Frequency**: Real-time lag monitoring
- **Error Rate**: <1% target
- **Data Consistency**: Validation rule compliance

#### **Government Compliance Dashboard**  
- **eSocial Events**: Submitted, accepted, rejected
- **NF-e Status**: Authorized, rejected, cancelled
- **Certificate Status**: Valid, expiring, expired
- **Queue Health**: Processing time, backlog

---

## 🎯 7. PRÓXIMOS PASSOS DE IMPLEMENTAÇÃO

### 7.1. Decisões Arquiteturais Prioritárias

#### **1. Database Schema Design**
- [ ] Design integration_account, sync_run, id_map tables
- [ ] Migration strategy (zero downtime)
- [ ] Index strategy (performance)
- [ ] Partitioning strategy (scale)

#### **2. Connector Interface Standardization**  
- [ ] Define IConnector interface contract
- [ ] Authentication strategy abstraction
- [ ] Error handling patterns
- [ ] Retry/circuit breaker policies

#### **3. Government Integration Strategy**
- [ ] Certificate management approach (A1 vs A3)
- [ ] Direct integration vs certified provider decision
- [ ] Homologation environment setup
- [ ] Compliance validation approach

### 7.2. Technology Stack Decisions

#### **Async Processing**
- **Current**: FastAPI async + SQLAlchemy async ✅
- **Enhancement**: Celery or FastAPI background tasks for long sync
- **Queue**: Redis streams or dedicated message broker

#### **HTTP Clients**
- **Choice**: httpx async ✅ (already in stack)
- **Enhancement**: Add circuit breaker, retry, rate limiting wrapper
- **Government**: Support for SOAP (zeep) and mutual TLS

#### **Encryption**
- **Symmetric**: cryptography library (Fernet)
- **Asymmetric**: Government certificates (cryptography + OpenSSL)
- **Key Storage**: Environment variables + KMS integration

---

## ✅ 8. VALIDATION CHECKLIST

### 8.1. Current System Validation

- [x] **Authentication**: JWT working, rate limiting active
- [x] **Database**: Async SQLAlchemy, Alembic migrations  
- [x] **Observability**: Prometheus metrics, Grafana dashboards
- [x] **LGPD**: Audit module exists, compliance framework present
- [x] **API Structure**: FastAPI + Pydantic V2, standardized patterns
- [x] **Multi-tenancy**: tenant_id pattern established

### 8.2. Integration Readiness Assessment  

- [ ] **API Documentation**: Review Bling, Sólides, Domínio APIs
- [ ] **Rate Limits**: Understand external system limits
- [ ] **Authentication**: API keys, OAuth2 flows mapping
- [ ] **Webhook Support**: Which systems support push notifications
- [ ] **Data Mapping**: Field-by-field mapping design
- [ ] **Government Compliance**: Homologation environments access

---

**📅 Created**: January 15, 2026  
**👤 Author**: Tech Lead + Claude Code  
**🔄 Version**: 1.0  
**📋 Status**: Foundation Mapping Complete
