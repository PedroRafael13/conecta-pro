# AUDITORIA ESTRUTURAL — CONECTA PRO ERP
## Data: 15/03/2026 | Executado por: Claude Code Opus

---

## 1. VISÃO GERAL DO SISTEMA

| Metrica | Valor |
|---------|-------|
| Versão | 2.0.0 |
| Backend | FastAPI / Python 3.12 / SQLAlchemy 2.x async |
| Frontend | Next.js + React 18 + TypeScript + Tailwind |
| Banco | PostgreSQL 16 |
| Cache | Redis 7 |
| Domínio | erp.conectamais.pro |
| Módulos backend | 45 diretórios (9 agregadores + 36 implementação) |
| Arquivos Python | ~2,088 |
| Tabelas no banco | 441 (28 com dados, 413 vazias) |
| Registros totais | ~268 |
| Páginas frontend | 198 page.tsx |
| Migrations Alembic | 89 |
| Routers registrados | ~100+ |

---

## 2. INFRAESTRUTURA

| Serviço | Container | Porta |
|---------|-----------|-------|
| PostgreSQL 16 | conecta-pro-postgres | interno |
| Redis 7 | conecta-pro-redis | interno |
| Backend FastAPI | conecta-pro-backend | 8080 |
| Frontend Next.js | conecta-pro-frontend | 3001 |
| Nginx (SSL) | via host | 80/443 |
| Celery Workers (6) | conecta-pro-celery-* | -- |
| Flower | conecta-pro-flower | 5555 |
| Prometheus+Grafana+Loki | erp-* | 9090/3000/3100 |

---

## 3. MÓDULOS BACKEND (45 diretórios)

### Top 10 por tamanho:
| Módulo | Arquivos .py | Função |
|--------|:---:|--------|
| ai | 329 | Bartolo IA, chatbot, ML, voice, OCR, workflows |
| people_management | 213 | DP + RH + Operações + Portal + GED + SST + Ponto |
| hr | 171 | HR legado (payroll, vacations, time-tracking) |
| government_integrations | 171 | NFS-e, eSocial, SPED, DCTFWeb, EFD-Reinf |
| financial | 167 | Contabilidade, AP/AR, bancos, cashflow, estoque |
| operacional | 167 | Postos, escalas, turnos, alocações, diaristas |
| bidding | 97 | Licitações, propostas, contratos, 7 AI agents |
| integrations | 91 | Gateway, conectores, banking, Sólides |
| notifications | 66 | Push, intelligent, hub, templates |
| retention | 47 | Onboarding, clima, turnover prediction |

### 9 Agregadores:
comercial, operacoes, tecnico, pessoas, financeiro, fiscal_contabil, inteligencia, gestao, cadastros

---

## 4. GESTÃO DE PESSOAS — MAPA COMPLETO

### 4.1 Departamento Pessoal (DP) — 100% REFERÊNCIA
- **Status:** APROVADO PARA PRODUÇÃO (25/25)
- **Controllers:** 14 (employee, admission, termination, contract, benefits, vacation, payroll, payroll-export, esocial, discipline, time-tracking, leave, document, reimbursement)
- **Endpoints:** 49 nativos + reimbursement re-exportado
- **Models:** 6 (employees, employee_dp, admission_processes, employment_contracts, employee_benefits, termination_processes)
- **Services:** 16
- **Schemas:** 5
- **Skills IA:** 4 (payroll, benefits, compliance, documenter)

### 4.2 Recursos Humanos (RH) — ~60%
- **Controllers:** 9 (career, climate, evaluation_360, onboarding, performance, recruitment, resume, training, turnover)
- **Endpoints:** ~38 nativos + re-exportados de retention/recruitment
- **Models:** 3 (career_plans, performance_reviews, training_*)
- **Services:** 9
- **Skills IA:** 5 (evaluator, onboarder, predictor, recruiter, trainer)
- **AI:** 3 (candidate_scoring, climate_analysis, turnover_prediction)
- **PROBLEMAS:** Recruitment endpoints retornam 500 (tabela faltando), route prefix duplicado em retention

### 4.3 GED — ~80%
- **Controllers:** 3 (clients 6ep, kits 11ep, documents 8ep)
- **Endpoints:** 25
- **Models:** 4 (ged_clients, ged_document_kits, ged_kit_documents, ged_kit_access_logs)
- **Services:** 7 (client, kit, collector, export, google_drive, kit_builder, signature)
- **Tasks:** 2 (auto_collect, cnd_sync)

### 4.4 Ponto Eletrônico — ~70%
- **Controllers:** 1 (punch_controller, 8 endpoints)
- **Models:** 3 (gp_clock_punches, gp_justifications, gp_monthly_closings)
- **Services:** 1
- **PENDÊNCIA:** Tabelas gp_* existem no DB mas wiring real pendente

### 4.5 SST — ~70%
- **Controllers:** 1 (sst_controller, 10 endpoints)
- **Models:** 4 (gp_asos, gp_cats, gp_epi_deliveries, gp_risks)
- **Services:** 1
- **PENDÊNCIA:** Wiring real com banco pendente

### 4.6 Portal do Funcionário — ~60%
- **Controllers:** 8 (portal, my_data, my_documents, my_notifications, my_payslips, my_schedules, my_trainings, my_vacations)
- **Endpoints:** 18
- **Models:** 4 (portal_digital_signatures, portal_notifications, portal_access_logs, portal_preferences)

### 4.7 Integração Bidirecional — ~80%
- **Endpoints:** 11
- **Fluxos:** 10 (Ops→DP shift/occurrence/availability/payroll, DP→Ops vacation/termination, RH→DP candidate, RH→Ops training, Portal→DP signature, DP→RH admission)

### 4.8 Agentes IA — 8 agentes
- Orchestrator, DP, RH, GED, OPS, SST, Ponto, Portal

### 4.9 Core — Event Bus + WebSocket + Audit
- Redis PubSub, 53 tipos de eventos, WebSocket GP, audit logger

---

## 5. FRONTEND — GESTÃO DE PESSOAS (82 páginas)

| Módulo | Diretório | Páginas |
|--------|-----------|:---:|
| DP | /modulos/dp/ | 11 |
| RH | /modulos/rh/ | 11 |
| GED | /modulos/gestao-pessoas/ged/ | 9 |
| Ponto | /modulos/gestao-pessoas/ponto/ | 7 |
| SST | /modulos/gestao-pessoas/sst/ | 6 |
| Portal | /modulos/portal/ | 7 |
| Operacional | /modulos/operacional/ | 28 |
| Saúde Ocupacional | /modulos/saude-ocupacional/ | 4 |
| **Total** | | **83** |

---

## 6. BANCO DE DADOS — TABELAS COM DADOS

| Tabela | Registros |
|--------|:---:|
| users | 52 |
| allocations | 20 |
| bidding_opportunities | 20 |
| time_bank | 18 |
| occurrences | 15 |
| reimbursement_requests | 12 |
| communication_* | 12+10+7 |
| bidding_* (14 tabelas) | 103 |
| disciplinary_actions | 7 |
| empresas | 2 |

**employees:** 44 ativos (tabela principal do sistema)

---

## 7. INTEGRAÇÕES EXISTENTES

### Sólides (32 arquivos)
- Conector completo: connector, sync_service, conflict_resolver, mappers, models, schemas, tasks, webhook_handler
- Controller: solides_controller.py
- DB: 16 tabelas solides_*
- **Status:** Standalone em modules/integrations/, NÃO conectado ao people_management

### CCT/Convenção Coletiva (38 arquivos)
- Módulo completo em modules/fase5/cct_compliance/ (models, enums, service, cct_agent)
- Usado em CRM pricing_engine e pdf_generator
- **Status:** Orphaned em fase5 (deprecated), NÃO migrado para people_management

### eSocial
- Endpoints em people_management/hr/esocial/ (S-2200, S-2299, validar, events)
- Integração government_integrations completa (171 arquivos)

### Domínio Sistemas
- Export payroll para Domínio via payroll_export_service.py

---

## 8. GAPS CRÍTICOS PARA PRODUÇÃO

| # | Gap | Impacto | Esforço |
|---|-----|---------|---------|
| 1 | Financeiro exige condominio_id | Módulo inteiro bloqueado | Alto |
| 2 | Recruitment retorna 500 | RH parcialmente inacessível | Médio |
| 3 | Config/Users retorna 500 | Admin inacessível | Médio |
| 4 | CCT orphaned em fase5 | Compliance trabalhista | Médio |
| 5 | Sólides não conectado ao GP | Sync de dados manual | Médio |
| 6 | 413 tabelas vazias | Sem dados de produção | Baixo (dados virão com uso) |
| 7 | celery-batch em restart loop | Worker de batch não funciona | Baixo |
| 8 | Ponto/SST in-memory | Dados não persistem | Médio |

---

## 9. PADRÃO DE REFERÊNCIA (DP)

### Estrutura de arquivos:
```
modules/people_management/hr/
├── __init__.py
├── aggregator.py          # Router com prefix="/hr"
├── controllers/           # 1 arquivo por domínio
│   ├── employee_controller.py
│   ├── admission_controller.py
│   └── ...
├── models/                # SQLAlchemy models
│   ├── admission.py
│   ├── benefits.py
│   └── ...
├── schemas/               # Pydantic schemas
├── services/              # Business logic
│   ├── employee_service.py
│   ├── admission_service.py
│   └── ...
└── skills/                # AI skills (optional)
```

### Padrões de código:
- **Rotas:** prefix no aggregator, sub-prefix no controller
- **Tabelas:** snake_case (admission_processes, employee_benefits)
- **Auth:** CurrentActiveUser dependency
- **DB:** AsyncSession + select() (SQLAlchemy 2.x)
- **Erros:** HTTPException com detail message
- **Serialização:** _to_dict() para converter SQLAlchemy → dict (fix profile)
- **Frontend:** 'use client' + useState + fetch + getAuthHeaders() + toast

---

## 10. RECOMENDAÇÕES PARA PRÓXIMOS MÓDULOS

1. **Seguir padrão DP** em todos os novos módulos (controller/model/service/schema)
2. **Migrar CCT** de fase5 para people_management/cct/
3. **Conectar Sólides** ao event bus do GP (flow Sólides→RH candidate sync)
4. **Remover condominio_id** dos endpoints financeiros (portado de outro sistema)
5. **Fix recruitment 500** — criar migration para tabelas faltantes
6. **Fix users 500** — coluna candidates.neighborhood faltando
7. **Wiring real Ponto/SST** — conectar controllers às tabelas gp_* existentes
8. **Dados seed** para demonstração (CRM, RH, Financeiro)
