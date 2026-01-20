# ROADMAP DE SPRINTS - FASE 2
## ERP CONECTA MAIS - CRONOGRAMA COMPLETO

**Versao:** 2.0
**Sprints Totais:** 38
**Duracao por Sprint:** 2 semanas (max)
**Prazo Total:** 18-24 meses

---

## VISAO GERAL DO ROADMAP

```
Q1 2026: Sprints 14-17 (CRM Premium + RH Base)
Q2 2026: Sprints 18-25 (RH Completo + Financeiro Base)
Q3 2026: Sprints 26-30 (Financeiro Avancado + BI)
Q4 2026: Sprints 31-35 (Automacoes + IA)
Q1 2027: Sprints 36-38 (Mobile Apps)
Q2 2027: Estabilizacao e Otimizacao
```

---

## Q1 2026 - VENDAS E RH BASE

### Sprint 14: Propostas Premium (CPQ)
**Duracao:** 2 semanas
**Prioridade:** MAXIMA
**Dependencias:** CRM Fase 1 concluido

**Entregaveis:**
```
1. Model Proposal com todos campos
2. ProposalItem para itens de proposta
3. PricingEngine - motor de precificacao
4. Calculo de CCT (Custo de Contratacao)
5. Calculo de impostos (ISS, PIS, COFINS, etc)
6. Templates de proposta (PDF)
7. Wizard de criacao em 5 etapas
8. Aprovacao em niveis (workflow)
9. Versionamento de propostas
10. Assinatura digital (integracao DocuSign)
```

**Arquivos a Criar:**
```
modules/crm/models/proposal.py
modules/crm/models/proposal_item.py
modules/crm/schemas/proposal.py
modules/crm/repositories/proposal_repository.py
modules/crm/services/pricing_engine.py
modules/crm/services/proposal_service.py
modules/crm/controllers/proposal_controller.py
tests/test_proposal_model.py
tests/test_pricing_engine.py
tests/test_proposal_api.py
```

**Criterios de Aceite:**
- [ ] Criar proposta com itens e calculos automaticos
- [ ] CCT calculado corretamente (validar com 5 casos reais)
- [ ] Impostos calculados com precisao de 2 casas
- [ ] PDF gerado com template profissional
- [ ] Workflow de aprovacao funcionando
- [ ] Pylint 100/100
- [ ] Cobertura >= 85%

---

### Sprint 15: Recrutamento IA - Parte 1
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Nenhuma

**Entregaveis:**
```
1. Model JobPosting (vaga)
2. Model Candidate (candidato)
3. Model Application (candidatura)
4. Integracao com portais (LinkedIn, Indeed)
5. Parser de curriculo (PDF -> dados)
6. Matching basico candidato-vaga
```

**Arquivos a Criar:**
```
modules/hr/
modules/hr/models/__init__.py
modules/hr/models/job_posting.py
modules/hr/models/candidate.py
modules/hr/models/application.py
modules/hr/schemas/recruitment.py
modules/hr/repositories/recruitment_repository.py
modules/hr/services/resume_parser.py
modules/hr/controllers/recruitment_controller.py
tests/test_recruitment.py
```

---

### Sprint 16: Recrutamento IA - Parte 2
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 15

**Entregaveis:**
```
1. Scoring de candidatos com IA
2. Triagem automatica
3. Agendamento de entrevistas
4. Video-entrevista integrada
5. Feedback estruturado
6. Pipeline visual (Kanban)
7. Relatorios de recrutamento
```

**Arquivos a Criar:**
```
modules/hr/services/candidate_scoring.py
modules/hr/services/interview_scheduler.py
modules/hr/models/interview.py
modules/hr/schemas/interview.py
tests/test_candidate_scoring.py
tests/test_interview.py
```

---

### Sprint 17: Ponto Eletronico
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Nenhuma

**Entregaveis:**
```
1. Model TimeEntry (registro de ponto)
2. Model TimeSheet (folha de ponto)
3. Biometria facial (integracao camera)
4. Geolocalizacao (GPS)
5. Registro via app/web/totem
6. Justificativas e abonos
7. Banco de horas
8. Relatorios MTE (Portaria 671)
9. Exportacao para folha
```

**Arquivos a Criar:**
```
modules/hr/models/time_entry.py
modules/hr/models/time_sheet.py
modules/hr/schemas/time_tracking.py
modules/hr/services/time_tracking_service.py
modules/hr/services/biometric_service.py
modules/hr/controllers/time_tracking_controller.py
tests/test_time_tracking.py
tests/test_biometric.py
```

**Criterios de Aceite:**
- [ ] Registro com foto e GPS
- [ ] Validacao de jornada (8h, 12x36, etc)
- [ ] Banco de horas calculado automaticamente
- [ ] Relatorio Portaria 671 valido
- [ ] Integracao com Control iD/Intelbras

---

## Q2 2026 - RH COMPLETO E FINANCEIRO

### Sprint 18: Admissao Digital - Parte 1
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 16

**Entregaveis:**
```
1. Model Employee (funcionario)
2. Model EmployeeDocument (documentos)
3. Onboarding digital (checklist)
4. Upload de documentos
5. Validacao automatica (CPF, RG, etc)
6. OCR para extracao de dados
```

---

### Sprint 19: Admissao Digital - Parte 2
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 18

**Entregaveis:**
```
1. Integracao eSocial (eventos S-2200)
2. Geracao de contrato
3. Assinatura digital do contrato
4. Exame admissional (ASO)
5. Cadastro de dependentes
6. Beneficios iniciais
```

---

### Sprint 20: Folha de Pagamento - Parte 1
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 19

**Entregaveis:**
```
1. Model Payroll (folha)
2. Model PayrollItem (rubricas)
3. Calculo de salario base
4. Calculo de horas extras
5. Calculo de adicional noturno
6. Descontos legais (INSS, IR)
7. Rubricas configuráveis
```

---

### Sprint 21: Folha de Pagamento - Parte 2
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 20

**Entregaveis:**
```
1. Ferias (calculo, provisao)
2. 13o salario (1a e 2a parcela)
3. Rescisao (todos os tipos)
4. FGTS (calculo e SEFIP)
5. Holerite digital
6. eSocial completo
7. DIRF, RAIS
```

---

### Sprint 22: Contas a Pagar - Parte 1
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Nenhuma

**Entregaveis:**
```
1. Model PayableAccount (conta a pagar)
2. Model Supplier (fornecedor)
3. Model PaymentCategory (categoria)
4. Cadastro de contas
5. Programacao de pagamentos
6. Aprovacao em niveis
7. Anexo de documentos
```

**Arquivos a Criar:**
```
modules/financial/
modules/financial/models/__init__.py
modules/financial/models/payable.py
modules/financial/models/supplier.py
modules/financial/schemas/payable.py
modules/financial/repositories/payable_repository.py
modules/financial/services/payable_service.py
modules/financial/controllers/payable_controller.py
tests/test_payable.py
```

---

### Sprint 23: Contas a Pagar - Parte 2
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 22

**Entregaveis:**
```
1. CNAB 240/400 (geracao de remessa)
2. Retorno bancario (leitura)
3. Conciliacao automatica
4. Pagamento via PIX
5. Boleto (leitura e pagamento)
6. DDA (Debito Direto Autorizado)
7. Relatorios de pagamentos
```

---

### Sprint 24: Contas a Receber - Parte 1
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 23

**Entregaveis:**
```
1. Model ReceivableAccount (conta a receber)
2. Model Invoice (fatura)
3. Cadastro de recebíveis
4. Geracao de boletos
5. NFSe automatica
6. Parcelamento
```

---

### Sprint 25: Contas a Receber - Parte 2
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 24

**Entregaveis:**
```
1. Cobranca automatizada (régua)
2. WhatsApp para cobranca
3. Email de cobranca
4. Negativacao (SPC/Serasa)
5. Acordo/renegociacao
6. Relatorios de inadimplencia
7. Aging report
```

---

## Q3 2026 - FINANCEIRO AVANCADO E BI

### Sprint 26: Open Banking
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 23, 25

**Entregaveis:**
```
1. Integracao Open Banking (BB, Itau, Bradesco)
2. Consulta de saldo em tempo real
3. Consulta de extrato
4. Iniciacao de pagamento
5. Conciliacao automatica
6. Multi-banco
```

**Arquivos a Criar:**
```
modules/integrations/
modules/integrations/banking/
modules/integrations/banking/adapters/base.py
modules/integrations/banking/adapters/bb.py
modules/integrations/banking/adapters/itau.py
modules/integrations/banking/adapters/bradesco.py
modules/integrations/banking/services/banking_service.py
tests/test_banking_integration.py
```

---

### Sprint 27: Fluxo de Caixa
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 26

**Entregaveis:**
```
1. Dashboard fluxo de caixa
2. Previsao com IA (30, 60, 90 dias)
3. Cenarios (otimista, pessimista, realista)
4. Alertas de saldo baixo
5. Sugestoes de investimento
6. Integracao Open Banking (saldo real)
```

---

### Sprint 28: DRE Automatico
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 27

**Entregaveis:**
```
1. Plano de contas configuravel
2. Lancamentos automaticos
3. Rateio por centro de custo
4. DRE mensal/anual
5. Comparativo periodo anterior
6. Export Excel/PDF
```

---

### Sprint 29: Balancete e Fechamento
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 28

**Entregaveis:**
```
1. Balancete de verificacao
2. Balanco patrimonial
3. Fechamento mensal automatico
4. Provisoes automaticas
5. Conciliacao contabil
6. Auditoria de lancamentos
```

---

### Sprint 30: BI e Dashboards
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprints 21, 29

**Entregaveis:**
```
1. Dashboard CEO (KPIs executivos)
2. Dashboard Financeiro
3. Dashboard RH
4. Dashboard Comercial
5. Graficos interativos
6. Drill-down em dados
7. Exportacao de relatorios
8. Agendamento de relatorios
```

**Arquivos a Criar:**
```
modules/bi/
modules/bi/models/dashboard.py
modules/bi/models/widget.py
modules/bi/models/report.py
modules/bi/services/analytics_service.py
modules/bi/services/report_generator.py
modules/bi/controllers/dashboard_controller.py
tests/test_bi.py
```

---

## Q4 2026 - AUTOMACOES E IA

### Sprint 31: Automacoes WhatsApp
**Duracao:** 2 semanas
**Prioridade:** MEDIA
**Dependencias:** Sprint 25

**Entregaveis:**
```
1. Integracao WhatsApp Business API
2. Templates de mensagem
3. Envio automatico de cobranca
4. Envio de boletos
5. Chatbot basico
6. Fila de mensagens
7. Relatorio de envios
```

---

### Sprint 32: Automacoes Email
**Duracao:** 2 semanas
**Prioridade:** MEDIA
**Dependencias:** Sprint 31

**Entregaveis:**
```
1. Templates de email (HTML)
2. Campanhas automaticas
3. Drip campaigns (nutrição)
4. Tracking (aberturas, cliques)
5. A/B testing
6. Unsubscribe automatico
```

---

### Sprint 33: Workflow Engine
**Duracao:** 2 semanas
**Prioridade:** MEDIA
**Dependencias:** Sprint 32

**Entregaveis:**
```
1. Designer visual de workflows
2. Triggers (eventos, tempo, dados)
3. Acoes (email, WhatsApp, tarefa)
4. Condicoes (if/else)
5. Loops e esperas
6. Logs de execucao
7. Workflows pre-configurados
```

---

### Sprint 34: Onboarding Automatizado
**Duracao:** 2 semanas
**Prioridade:** MEDIA
**Dependencias:** Sprint 33

**Entregaveis:**
```
1. Jornada de onboarding cliente
2. Jornada de onboarding funcionario
3. Checklists automaticos
4. Notificacoes por etapa
5. Metricas de conclusao
6. Personalizacao por tipo
```

---

### Sprint 35: IA Avancada
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprints 30, 33

**Entregaveis:**
```
1. Churn Prediction (50+ variaveis)
2. Next Best Action Engine
3. Anomaly Detection
4. Dynamic Pricing
5. Sentiment Analysis (tickets)
6. Predictive Maintenance
7. Assistente virtual inteligente
```

**Arquivos a Criar:**
```
modules/ai/
modules/ai/models/prediction.py
modules/ai/services/churn_predictor.py
modules/ai/services/next_best_action.py
modules/ai/services/anomaly_detector.py
modules/ai/services/dynamic_pricing.py
modules/ai/services/sentiment_analyzer.py
tests/test_ai_services.py
```

---

## Q1 2027 - MOBILE APPS

### Sprint 36: App Colaborador
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 17, 21

**Entregaveis:**
```
1. React Native app base
2. Login biometrico
3. Registro de ponto (foto + GPS)
4. Consulta de holerite
5. Solicitacao de ferias
6. Consulta de banco de horas
7. Push notifications
```

---

### Sprint 37: App Gestor
**Duracao:** 2 semanas
**Prioridade:** ALTA
**Dependencias:** Sprint 36

**Entregaveis:**
```
1. Dashboard mobile
2. Aprovacoes (ferias, ponto, etc)
3. Escalas da equipe
4. Comunicados
5. Relatorios simplificados
6. Alertas em tempo real
```

---

### Sprint 38: Apps Cliente e Tecnico
**Duracao:** 2 semanas
**Prioridade:** MEDIA
**Dependencias:** Sprint 37

**Entregaveis:**
```
App Cliente:
1. Portal do cliente
2. Boletos e pagamentos
3. Abertura de chamados
4. Documentos

App Tecnico:
1. Ordens de servico
2. Check-in/out
3. Fotos e assinaturas
4. Offline first
```

---

## SPRINTS EXTRAS (Se houver tempo)

### Sprint 39: App Vendedor
**Entregaveis:**
- CRM mobile
- Propostas no celular
- Agenda e visitas
- Metas e comissoes

### Sprint 40: Compliance Avancado
**Entregaveis:**
- ISO 27001 preparacao
- SOC 2 preparacao
- LGPD avancado
- Auditoria automatizada

---

## DEPENDENCIAS ENTRE SPRINTS

```
Sprint 14 (Propostas) <- CRM Fase 1
Sprint 15 (Recrutamento 1) <- Nenhuma
Sprint 16 (Recrutamento 2) <- Sprint 15
Sprint 17 (Ponto) <- Nenhuma
Sprint 18 (Admissao 1) <- Sprint 16
Sprint 19 (Admissao 2) <- Sprint 18
Sprint 20 (Folha 1) <- Sprint 19
Sprint 21 (Folha 2) <- Sprint 20
Sprint 22 (Pagar 1) <- Nenhuma
Sprint 23 (Pagar 2) <- Sprint 22
Sprint 24 (Receber 1) <- Sprint 23
Sprint 25 (Receber 2) <- Sprint 24
Sprint 26 (Banking) <- Sprint 23, 25
Sprint 27 (Fluxo) <- Sprint 26
Sprint 28 (DRE) <- Sprint 27
Sprint 29 (Balanco) <- Sprint 28
Sprint 30 (BI) <- Sprint 21, 29
Sprint 31 (WhatsApp) <- Sprint 25
Sprint 32 (Email) <- Sprint 31
Sprint 33 (Workflow) <- Sprint 32
Sprint 34 (Onboarding) <- Sprint 33
Sprint 35 (IA) <- Sprint 30, 33
Sprint 36 (App Colab) <- Sprint 17, 21
Sprint 37 (App Gestor) <- Sprint 36
Sprint 38 (Apps) <- Sprint 37
```

---

## METRICAS DE ACOMPANHAMENTO

| Metrica | Inicio | Meta Q2 | Meta Q4 | Meta Final |
|---------|--------|---------|---------|------------|
| Score Sistema | 3.9 | 6.0 | 8.0 | 9.1 |
| Sprints Concluidos | 0/38 | 12/38 | 24/38 | 38/38 |
| Arquivos Python | 675 | 1000 | 1500 | 2000+ |
| Linhas de Codigo | 214k | 350k | 500k | 700k+ |
| Cobertura Testes | 85% | 88% | 92% | 95% |
| Pylint Score | 100 | 100 | 100 | 100 |

---

## REGRAS DE TRANSICAO DE SPRINT

### Antes de Iniciar Proximo Sprint

```
1. Sprint anterior 100% concluido
2. Todos testes passando
3. Pylint >= 99/100 (meta 100)
4. Documentacao atualizada
5. Code review aprovado
6. Deploy em staging validado
```

### Se Sprint Atrasar

```
Atraso < 3 dias: Continuar e terminar
Atraso 3-5 dias: Dividir escopo, entregar parcial
Atraso > 5 dias: Parar, reuniao de crise, replanejar
```

---

*Roadmap de Sprints - ERP Conecta Mais Fase 2*
*"38 sprints para a excelencia"*
