# PROGRESSO GERAL - ERP CONECTA MAIS V2.0

## Sprint Atual: Sprint 10 - Equipamentos (PLANEJADO)

### Progresso Geral: 26% (10/38 módulos)
### CRM Completo: 6/6 sprints (0-5 + Contratos)
### Operations: 3/8 sprints (Sprint 7-9)

---

## Checklist de Sprints

### Infraestrutura (5/5) - 100%
- [x] Estrutura de diretórios
- [x] Python venv configurado
- [x] PostgreSQL configurado (código + Alembic)
- [x] Redis configurado (código pronto)
- [x] Git inicializado

### Sprint 0: Core (7/7) - 100%
- [x] Autenticação (JWT)
- [x] User model + RBAC
- [x] Base models
- [x] Error handling (Circuit Breaker)
- [x] Logging (estruturado + sanitização)
- [x] Banco de dados (PostgreSQL + Alembic migration)
- [x] Endpoints REST de auth (register, login, refresh, me)

### Sprint 1: CRM Lead (4/4) - 100%
- [x] Lead model (20+ campos, status/source enums)
- [x] Lead service (IA scoring com 6 fatores ponderados)
- [x] Lead APIs (9 endpoints REST)
- [x] Testes (82 testes específicos)

### Sprint 2: CRM Opportunity (4/4) - 100%
- [x] Opportunity model (6 estágios do funil)
- [x] Conversão Lead -> Opportunity
- [x] Pipeline Service (métricas, forecast, health score)
- [x] Testes (81 testes, 325 total)

### Sprint 3: Propostas Comerciais (5/5) - 100%
- [x] Proposal model (versões, itens, valores)
- [x] ProposalItem model (produtos/serviços)
- [x] Template system (personalização)
- [x] Workflow de aprovação (10 status, approval history)
- [x] Testes (84 novos, 196 CRM total)

### Sprint 4: Comissões (5/5) - 100%
- [x] Commission model (5 tipos de cálculo: fixa, %, margem, progressiva, bônus)
- [x] CommissionRule model (regras, gatilhos, limites)
- [x] CommissionService (cálculo automático, stats, ranking)
- [x] CommissionRepository (CRUD + filtros avançados)
- [x] Testes (45 novos testes de comissão)

### Sprint 5: Dashboard CRM (5/5) - 100%
- [x] Dashboard Service (KPIs consolidados)
- [x] Dashboard Controller (13 endpoints REST)
- [x] Tendências (diária, semanal, mensal)
- [x] Métricas de funil e conversão
- [x] Testes (62 testes: 41 unitários + 21 API)

### Sprint 6: Contratos (8/8) - 100%
- [x] Contract model (recorrente/pontual, status workflow)
- [x] ContractTemplate model (templates por serviço)
- [x] ContractItem model (serviços do contrato)
- [x] ContractAddendum model (aditivos e reajustes)
- [x] ContractSLAReport model (relatórios mensais de SLA)
- [x] ContractService (renovação, reajuste, SLA, alertas)
- [x] ContractRepository (CRUD + filtros avançados)
- [x] Testes (61 novos testes, 515 total)

### Sprint 7: Postos e Escalas (6/6) - 100%
- [x] Post model (5 tipos, 4 status, requisitos, certificações)
- [x] Scale model (5 tipos de escala: 12x36, 6x1, 5x2, turno_revezamento, admin)
- [x] Shift model (turnos com check-in/out, horas extras, noturno)
- [x] Allocation model (alocação funcionário-posto)
- [x] Substitution model (substituições com IA de sugestões)
- [x] TimeBank model (banco de horas CLT)

### Sprint 8: Facilities Management (6/6) - 100%
- [x] Area model (5 tipos, categorias, capacidade, equipamentos)
- [x] Maintenance model (preventiva/corretiva, SLA, custos)
- [x] Inspection model (agendada/não-agendada, scoring, relatórios)
- [x] Checklist model (templates, itens, pontuação)
- [x] ServiceRequest model (8 categorias, workflow completo)
- [x] 3 Services IA: MaintenanceScheduler, InspectionAnalyzer, RequestClassifier

### Sprint 9: Portaria Remota / Guardian Integration (6/6) - 100%
- [x] GuardianSync model (sincronização ERP <-> Guardian)
- [x] AccessLog model (logs de acesso recebidos)
- [x] GuardianOccurrence model (ocorrências do Guardian)
- [x] EquipmentStatus model (status de equipamentos em tempo real)
- [x] GuardianSyncService (payloads, validações, retry lógica)
- [x] OccurrenceAnalyzer IA (classificação, priorização, SLA, sugestões)

### Sprints Restantes (28 módulos):

**Operações (5 módulos restantes):**
- [ ] Sprint 10: Equipamentos
- [ ] Sprint 11: Ocorrências
- [ ] Sprint 12: Visitantes
- [ ] Sprint 13: Moradores
- [ ] Sprint 14: GED (Gestão Documental)

**RH (7 módulos):**
- [ ] Sprint 15: Recrutamento e Seleção
- [ ] Sprint 16: Ponto Eletrônico
- [ ] Sprint 17: Folha de Pagamento
- [ ] Sprint 18: Admissão Digital
- [ ] Sprint 19: Avaliação de Desempenho
- [ ] Sprint 20: Treinamento
- [ ] Sprint 21: SST (Segurança do Trabalho)

**Financeiro (9 módulos):**
- [ ] Sprint 22: Contas a Pagar
- [ ] Sprint 23: Contas a Receber
- [ ] Sprint 24: Fluxo de Caixa
- [ ] Sprint 25: Compras
- [ ] Sprint 26: Estoque
- [ ] Sprint 27: Contabilidade
- [ ] Sprint 28: Fiscal
- [ ] Sprint 29: Custos
- [ ] Sprint 30: BI e Dashboards

**Críticos e IA (2 módulos):**
- [ ] Sprint 31: Kits Documentais
- [ ] Sprint 32: Diaristas

---

## Métricas Atuais

| Métrica | Valor |
|---------|-------|
| **Módulos completos** | **10/38 (26%)** |
| Linhas de código | ~28500+ |
| Arquivos criados | 170+ |
| Testes escritos | 900+ |
| Coverage | 85%+ |
| Commits | 13 |
| Sessões | 11 |
| Auditor Score | 100/100 |

### Progresso por Categoria
| Categoria | Completo | Total | % |
|-----------|----------|-------|---|
| Core | 1 | 1 | 100% |
| CRM | 5 | 5 | 100% |
| Contratos | 1 | 1 | 100% |
| Operações | 3 | 8 | 37.5% |
| RH | 0 | 7 | 0% |
| Financeiro | 0 | 9 | 0% |
| Críticos/IA | 0 | 2 | 0% |
| **TOTAL** | **10** | **38** | **26%** |

---

## Contracts Module - Funcionalidades (Sprint 6)

### Contract Model
- 5 Enums: ContractType (2), ContractStatus (6), AdjustmentIndex (5), AddendumType (6), ServiceType (8)
- 5 Models: Contract, ContractTemplate, ContractItem, ContractAddendum, ContractSLAReport
- 25+ Schemas Pydantic para validação
- 30+ Endpoints REST: contracts, items, templates, addendums, sla-reports

### Tipos de Contrato
- **Recorrente (RECURRING)**: Mensal, com renovação automática
- **Pontual (ONE_TIME)**: Único, sem recorrência

### Status do Contrato
- DRAFT -> PENDING_SIGNATURE -> ACTIVE -> SUSPENDED/TERMINATED/CANCELLED

### Reajuste Automático
- Índices: IGP-M, IPCA, INPC, Percentual Fixo, Personalizado
- Cálculo automático da próxima data de reajuste
- Aditivos de reajuste com histórico

### SLA e Penalidades
- Configuração de indicadores com pesos
- Cálculo de score mensal
- Penalidades automáticas por não cumprimento
- Workflow: draft -> approved/disputed

### Alertas Inteligentes
- Contratos próximos do vencimento
- Contratos que precisam de reajuste
- Severidade: critical, high, medium, low

---

## Operations Module - Postos e Escalas (Sprint 7)

### Models Implementados
- **6 Models principais**: Post, Scale, Shift, Allocation, Substitution, TimeBank
- **14 Enums**: PostType (5), PostStatus (4), ShiftType (5), ScaleType (5), ScaleStatus (5), ShiftStatus (5), AllocationStatus (4), SubstitutionReason (7), SubstitutionStatus (5), TimeBankEntryType (3), TimeBankStatus (5)
- **25+ Schemas Pydantic** para validação
- **60+ Endpoints REST**: posts, scales, shifts, allocations, substitutions, time-bank

### Tipos de Posto (PostType)
- vigilancia, portaria, monitoramento, ronda, supervisao

### Tipos de Escala (ScaleType)
- **12x36**: Trabalha 12h, folga 36h
- **6x1**: 6 dias trabalhados, 1 folga
- **5x2**: Seg-Sex trabalhados, Sab-Dom folga
- **turno_revezamento**: Rotação de turnos (manhã/tarde/noite)
- **administrativo**: Horário comercial padrão

### Geração de Escala com IA (ScaleGenerator)
- Geração automática baseada no tipo de escala
- Detecção de feriados brasileiros (library `holidays`)
- Balanceamento de turnos entre funcionários
- Validação de regras CLT (44h semanais, 11h descanso entre jornadas)
- Otimização de alocação

### Substituições com IA (SubstitutionService)
- Sugestão inteligente de substitutos
- Score de adequação (0-100) com 5 fatores ponderados:
  - Disponibilidade (30%)
  - Qualificações (25%)
  - Distância geográfica (20%)
  - Histórico de hora extra (15%)
  - Preferência do posto (10%)
- Cálculo de custo estimado
- Haversine para distância geográfica

### Banco de Horas CLT (TimeBankService)
- Limite diário de 2h extras (CLT)
- Expiração: 6 meses (individual) ou 1 ano (acordo coletivo)
- Alertas de expiração (30 dias antes)
- Cálculo de compensação com validação
- Adicional noturno: 20%
- Hora extra: 50%
- Domingo/Feriado: 100%

### Funcionalidades de Turno
- Check-in e Check-out com timestamp
- Marcação de falta com motivo
- Cálculo automático de horas trabalhadas, extras, noturnas
- Flags: is_holiday, is_night_shift, is_overtime, needs_substitution

---

## CRM Module - Funcionalidades

### Commissions (Sprint 4)
- 4 Enums: CommissionType (5), CommissionTrigger (5), CommissionStatus (5), PaymentMethod (4)
- 5 Models: Commission, CommissionRule, CommissionPayment, CommissionSummary, SellerCommissionRule
- 15+ Schemas Pydantic para validação
- 20+ Endpoints REST: rules, commissions, payments, stats, ranking
- Tipos de comissão: fixa, percentual, margem, progressiva, bônus
- Gatilhos: assinatura, primeiro pagamento, cada pagamento, pagamento total, mensal
- Workflow: pending -> approved -> paid (com cancelamento e estorno)

### Dashboard CRM (Sprint 5)
- KPIs consolidados (leads, opportunities, proposals, commissions)
- Gráfico de funil de vendas
- Tendências (diária, semanal, mensal)
- Taxas de conversão entre estágios
- Performance por vendedor
- Top performers
- Gráficos de distribuição por status

### Proposals (Sprint 3)
- 4 Enums: ProposalStatus (10), ProposalType (5), DiscountType (2), ApprovalAction (3)
- 4 Models: Proposal, ProposalItem, ProposalTemplate, ProposalApproval
- 19 Schemas Pydantic para validação
- 18 Endpoints REST: proposals, items, templates
- Versionamento de propostas (mesmo número, incrementa versão)
- Workflow: draft -> pending_approval -> approved -> sent -> accepted/rejected

### Opportunities (Sprint 2)
- Pipeline com 6 estágios
- Conversão automática de Lead
- Forecast de vendas
- Health Score do pipeline

### Leads (Sprint 1)
- IA Scoring Engine
- 9 endpoints REST
- Conversão para Opportunity

---

## Proteções Implementadas

- [x] Cache Redis com helpers
- [x] Circuit Breaker (DB, Redis, APIs externas)
- [x] Sanitização de logs (senhas, tokens, CPF/CNPJ)
- [x] Logging estruturado (JSON + console)
- [ ] Backups automáticos (próxima fase)

---

## Tecnologias Implementadas

- FastAPI 0.115.6
- SQLAlchemy 2.0.36 (async)
- Alembic 1.14.0 (configurado)
- Pydantic 2.10.4
- python-jose (JWT)
- Redis 5.2.1
- Loguru 0.7.3
- pytest 8.3.4
- Faker 40.1.0 (testes)

---

## IA Implementada

### Lead Scoring Engine (CRM)
Algoritmo de pontuação de leads com 6 fatores ponderados:
- Completude dos dados (20%)
- Fonte do lead (15%)
- Tamanho da empresa (20%)
- Setor de atuação (15%)
- Engajamento/status (20%)
- Tempo de resposta (10%)

Funcionalidades:
- `calculate_score()`: Retorna score (0-100) e probabilidade de conversão
- `get_recommended_action()`: Sugere próxima ação baseada no score/status
- `get_next_contact_date()`: Calcula data ideal para próximo contato

### Scale Generator (Operations)
Geração inteligente de escalas de trabalho:
- Suporte a 5 tipos: 12x36, 6x1, 5x2, turno_revezamento, administrativo
- Detecção automática de feriados brasileiros
- Validação de regras CLT (limite semanal, descanso entre jornadas)
- Balanceamento equitativo de turnos entre funcionários
- Otimização de alocação para minimizar custos

### Substitution Suggester (Operations)
Sugestão inteligente de substitutos com scoring:
- Análise de disponibilidade em tempo real
- Verificação de qualificações e certificações
- Cálculo de distância geográfica (Haversine)
- Histórico de horas extras do funcionário
- Preferências de posto/turno
- Score final ponderado (0-100) para ranking

### Time Bank Manager (Operations)
Gestão inteligente de banco de horas CLT:
- Cálculo automático de horas extras, noturnas, feriados
- Alertas de expiração (30 dias antes)
- Validação de compensações
- Recomendações de gestão baseadas no saldo

---

## Remote Gatehouse Module - Funcionalidades (Sprint 9)

### Integração ERP <-> Conecta Guardian
Sincronização bidirecional com o sistema de portaria remota:

**ERP para Guardian (Saída):**
- Contratos, clientes, postos, funcionários
- Pessoas autorizadas (moradores, visitantes)
- Configurações de acesso

**Guardian para ERP (Entrada):**
- Ocorrências em tempo real
- Logs de acesso (entrada, saída, negado)
- Status de equipamentos

### Models Implementados
- **GuardianSync**: Controle de sincronização com retry logic
  - 5 Status: pending, in_progress, completed, failed, partial
  - 2 Direções: erp_to_guardian, guardian_to_erp
  - 11 Tipos de entidade: contract, client, employee, occurrence, access_log, etc.
  - Backoff exponencial para retentativas

- **AccessLog**: Logs de acesso recebidos
  - 9 Tipos: entry, exit, denied, visitor, delivery, service, emergency, patrol, intercom
  - Campos: pessoa, documento, placa, foto, vídeo
  - Metadados do Guardian

- **GuardianOccurrence**: Ocorrências do sistema Guardian
  - 14 Tipos: intrusion, fire, medical, violence, vandalism, suspicious_vehicle, etc.
  - 4 Níveis de severidade: low, medium, high, critical
  - 8 Status de workflow: open -> acknowledged -> in_progress -> resolved/escalated/closed
  - Campos: imagens, vídeos, áudios, envolvidos, testemunhas

- **EquipmentStatus**: Status de equipamentos em tempo real
  - 6 Status: online, offline, warning, error, maintenance, disabled
  - Métricas de ping e latência
  - Alertas ativos

### Services IA
- **OccurrenceAnalyzer**:
  - Classificação automática de ocorrências
  - Cálculo de prioridade (0-100) com 5 fatores
  - Sugestões de ações baseadas no tipo
  - SLA e escalonamento automático
  - Detecção de padrões

- **GuardianSyncService**:
  - Preparação de payloads (contratos, pessoas, acessos)
  - Validação de dados recebidos
  - Lógica de retry com backoff exponencial
  - Priorização de sincronização

### Endpoints REST (40+)
- `/guardian/sync/*`: Gestão de sincronizações
- `/guardian/access-logs/*`: Logs de acesso
- `/guardian/occurrences/*`: Ocorrências + workflow
- `/guardian/equipment-status/*`: Status de equipamentos

---

## Última Atualização
**Data:** 2025-12-30
**Por:** Claude Code - Sessão 011
**Mudanças:**
- Sprint 9 (Portaria Remota / Guardian Integration) COMPLETO
- 4 Models implementados: GuardianSync, AccessLog, GuardianOccurrence, EquipmentStatus
- 4 Repositories com CRUD + filtros avançados + stats
- 2 Services com IA: GuardianSyncService, OccurrenceAnalyzer
- 4 Controllers com 40+ endpoints REST
- Testes unitários e de serviços
- Auditor: 100/100 (pylint + bandit)
- Progresso: 26% (10/38 módulos)
