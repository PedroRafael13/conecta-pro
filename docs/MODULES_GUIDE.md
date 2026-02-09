# Guia de Módulos - Conecta PRO

## Visão Geral

O **Conecta PRO** é um ERP completo e modular desenvolvido especificamente para empresas de segurança privada. Com 34 módulos integrados, o sistema oferece gestão total desde o relacionamento com clientes até a operação em campo, recursos humanos, financeiro e conformidade legal.

A arquitetura modular permite implementação gradual, onde cada módulo pode ser ativado conforme a necessidade da empresa, garantindo escalabilidade e adaptação ao tamanho e complexidade da operação.

---

## Módulos por Categoria

### 🎯 Comercial e Relacionamento

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **CRM** | Gestão de relacionamento com clientes | Pipeline de vendas, leads, oportunidades, histórico de interações |
| **Clientes** | Cadastro e gestão de clientes | Perfil completo, contratos, SLA, histórico de atendimento |
| **Services** | Catálogo de serviços oferecidos | Tipos de segurança, vigilância, escolta, valores customizados |
| **Recruitment** | Recrutamento de clientes | Prospecção ativa, onboarding comercial, qualificação |
| **Retention** | Retenção e fidelização | Análise de churn, satisfação, programas de fidelidade |

---

### ⚙️ Operacional

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **Operacional** | Gestão centralizada das operações | Postos de trabalho, escalas, supervisionamento, ocorrências |
| **Campo** | Operações em campo e terreno | Rondas, checkpoints, atividades externas, geolocalização |
| **Scheduler** | Agendamento e escalas automáticas | Escalas inteligentes, folgas, substituições, conflitos |
| **Mobile** | Aplicativo mobile para operacional | Ponto eletrônico, ocorrências em tempo real, fotos, assinaturas |
| **Monitoring** | Central de monitoramento 24/7 | Alertas em tempo real, painel de controle, dashboards |
| **Equipment Management** | Gestão de equipamentos | Controle de armamento, coletes, rádios, manutenção, cautela |

---

### 👥 Recursos Humanos

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **HR** | Gestão completa de RH | Cadastro, dependentes, documentos, férias, desligamento |
| **Payroll Integration** | Integração folha de pagamento | Cálculos, holerites, impostos, integração bancária |
| **Recruitment** | Recrutamento e seleção | Vagas, candidatos, processo seletivo, banco de talentos |
| **Retention** | Retenção de talentos | Pesquisa de clima, onboarding, desenvolvimento de carreira |
| **Health Occupational** | Saúde ocupacional | ASO, PGR, PCMSO, exames periódicos, absenteísmo |
| **Diaristas** | Gestão de equipes diaristas | Contratação diária, escala flexível, pagamento por dia |

---

### 💰 Financeiro

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **Financial** | Gestão financeira completa | Contas a pagar/receber, fluxo de caixa, DRE, orçamentos |
| **BI Dashboard** | Business Intelligence | KPIs, relatórios gerenciais, análise de rentabilidade |
| **Costing** | Custeio e precificação | Custo por posto, margem de lucro, simulações |
| **Reimbursement** | Reembolsos e despesas | Solicitações, aprovações, comprovantes, reembolso |
| **Bidding** | Gestão de licitações | Editais, propostas, documentação, acompanhamento |

---

### 📋 Documentação e Compliance

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **GED** | Gestão eletrônica de documentos | Armazenamento, versionamento, workflow de aprovação |
| **Documents** | Gestão documental | Emissão, controle, prazos, alertas de vencimento |
| **Document Kits** | Kits de documentos padronizados | Templates, checklists, geração automática |
| **Security LGPD** | Conformidade com LGPD | Consentimentos, dados sensíveis, anonimização, auditoria |
| **Audit** | Auditoria e compliance | Rastreabilidade, logs, relatórios de conformidade |

---

### 🤖 Inteligência Artificial e Automação

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **AI** | Inteligência Artificial | Análise preditiva, chatbots, automação inteligente |
| **Bartolo** | Agente IA especializado | Análise de contratos, assistente operacional, insights |
| **Analytics** | Análise de dados avançada | ML, predições, análise comportamental, forecasting |
| **Automation** | Automação de processos | Workflows, triggers, integrações automáticas |
| **Fase5** | Módulo de inovação contínua | Agentes autônomos, CCT compliance, inovação |

---

### 🔌 Integrações e Conectividade

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **Integrations** | Hub de integrações | APIs, webhooks, ETL, conectores genéricos |
| **Government Integrations** | Integrações governamentais | eSocial, CAGED, RAIS, conectividade social |
| **Banking** | Integração bancária | Boletos, cobrança, conciliação, pagamentos |
| **Notifications** | Sistema de notificações | SMS, email, WhatsApp, push, alertas automáticos |
| **Search** | Busca unificada | Pesquisa global, indexação, filtros avançados |

---

### 🔧 Infraestrutura e Configuração

| Módulo | Descrição | Principais Funcionalidades |
|--------|-----------|---------------------------|
| **Core** | Núcleo do sistema | Autenticação, autorização, cache, logging, base models |
| **Config** | Configurações do sistema | Parâmetros, customizações, preferências, tenants |

---

## Matriz de Integração entre Módulos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MATRIZ DE INTEGRAÇÃO                              │
├──────────────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────┤
│                  │ CRM  │Client│Operac│  HR  │ Fin  │ GED  │Mobil │   AI    │
├──────────────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────┤
│ CRM              │  ●   │  ◆◆  │  ◆   │      │  ◆   │  ◆   │      │   ◆     │
│ Clientes         │ ◆◆   │  ●   │  ◆◆  │      │  ◆◆  │  ◆◆  │      │   ◆     │
│ Operacional      │      │ ◆◆   │  ●   │ ◆◆   │  ◆   │  ◆   │ ◆◆◆  │   ◆     │
│ Campo            │      │      │ ◆◆◆  │      │      │      │ ◆◆◆  │         │
│ Scheduler        │      │      │ ◆◆◆  │ ◆◆◆  │      │      │      │   ◆     │
│ Mobile           │      │      │ ◆◆◆  │      │      │      │  ●   │         │
│ HR               │      │      │ ◆◆   │  ●   │ ◆◆◆  │  ◆   │      │   ◆     │
│ Payroll          │      │      │      │ ◆◆◆  │ ◆◆◆  │      │      │         │
│ Financial        │ ◆    │ ◆◆   │  ◆   │ ◆◆   │  ●   │      │      │   ◆     │
│ BI Dashboard     │ ◆    │  ◆   │  ◆   │  ◆   │ ◆◆◆  │      │      │  ◆◆     │
│ GED              │      │  ◆   │      │  ◆   │      │  ●   │      │   ◆     │
│ Documents        │      │  ◆   │  ◆   │  ◆   │      │ ◆◆   │      │         │
│ AI               │ ◆    │  ◆   │ ◆◆   │  ◆   │  ◆   │  ◆   │      │   ●     │
│ Analytics        │ ◆    │  ◆   │ ◆◆   │  ◆   │ ◆◆   │      │      │  ◆◆     │
│ Notifications    │  ◆   │      │ ◆◆◆  │  ◆   │  ◆   │      │      │         │
│ Audit            │  ◆   │  ◆   │  ◆   │  ◆   │  ◆   │  ◆   │      │         │
│ Government Int   │      │      │      │ ◆◆   │      │      │      │         │
│ Integrations     │      │  ◆   │      │      │  ◆   │      │      │   ◆     │
└──────────────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────────┘

Legenda:
● = Módulo Principal
◆   = Integração Leve (dados compartilhados)
◆◆  = Integração Média (processos integrados)
◆◆◆ = Integração Forte (dependência funcional)
```

---

## Fluxos Principais de Negócio

### 1. Venda e Implantação
```
CRM → Clients → Services → Documents → Scheduler → Operacional
```

### 2. Gestão de Equipe
```
Recruitment → HR → Health Occupational → Scheduler → Mobile → Payroll
```

### 3. Operação Diária
```
Scheduler → Mobile → Campo → Monitoring → Operacional → BI Dashboard
```

### 4. Ciclo Financeiro
```
Services → Financial → BI Dashboard → Reimbursement → Banking
```

### 5. Compliance e Auditoria
```
Documents → GED → Security LGPD → Audit → Government Integrations
```

---

## Dependências entre Módulos

### Módulos Core (Base para todos)
- **Core** → Todos os módulos
- **Config** → Todos os módulos
- **Audit** → Todos os módulos (logging)

### Dependências Operacionais
- **Scheduler** requer: HR, Operacional
- **Mobile** requer: Operacional, HR
- **Campo** requer: Operacional, Mobile
- **Monitoring** requer: Operacional, Campo

### Dependências Comerciais
- **CRM** requer: Core
- **Clients** requer: CRM, Services
- **Services** requer: Core

### Dependências Financeiras
- **Financial** requer: Clients, Services, HR
- **Payroll** requer: HR, Financial
- **BI Dashboard** requer: Financial, Operacional, HR

### Dependências de Compliance
- **GED** requer: Core, Security LGPD
- **Documents** requer: GED, Clients, HR
- **Security LGPD** requer: Core, Audit

---

## Estrutura de Diretórios

```
/opt/conecta-pro/backend/modules/
├── ai/                       # Inteligência Artificial
│   ├── bartolo/             # Agente IA especializado
│   └── contract_analysis/   # Análise de contratos
├── analytics/               # Análise de dados e ML
├── audit/                   # Auditoria e logs
├── automation/              # Automação de workflows
├── bidding/                 # Licitações
├── campo/                   # Operações em campo
├── clients/                 # Gestão de clientes
├── config/                  # Configurações do sistema
├── core/                    # Núcleo do sistema
├── crm/                     # CRM e vendas
├── document_kits/           # Kits de documentos
├── documents/               # Gestão documental
├── equipment_management/    # Gestão de equipamentos
├── fase5/                   # Inovação e agentes
│   ├── agents/
│   └── cct_compliance/
├── financial/               # Financeiro
│   ├── bi_dashboard/
│   └── costing/
├── ged/                     # Gestão eletrônica documentos
├── government_integrations/ # Integrações governo
├── health_occupational/     # Saúde ocupacional
├── hr/                      # Recursos Humanos
│   ├── analytics_dashboard/
│   ├── employee_portal/
│   ├── mobile_time_clock/
│   ├── payroll_integration/
│   └── rep_integration/
├── integrations/            # Hub de integrações
│   └── banking/
├── mobile/                  # Aplicativo mobile
├── monitoring/              # Central de monitoramento
├── notifications/           # Sistema de notificações
├── operacional/             # Gestão operacional
├── recruitment/             # Recrutamento
├── reimbursement/           # Reembolsos
├── reports/                 # Relatórios
├── retention/               # Retenção
├── scheduler/               # Escalas
├── search/                  # Busca unificada
├── security_lgpd/           # Segurança e LGPD
└── services/                # Catálogo de serviços
```

---

## Guia de Implementação por Fases

### Fase 1: Core e Base
1. Core
2. Config
3. Audit
4. Security LGPD

### Fase 2: Gestão Básica
5. CRM
6. Clients
7. Services
8. HR (básico)

### Fase 3: Operação
9. Operacional
10. Scheduler
11. Mobile
12. Campo

### Fase 4: Financeiro
13. Financial
14. GED
15. Documents

### Fase 5: Avançado
16. BI Dashboard
17. Analytics
18. AI / Bartolo

### Fase 6: Integrações e Otimização
19. Government Integrations
20. Automation
21. Integrations completas

---

## Considerações Finais

Este guia serve como referência completa para desenvolvedores, analistas e gestores do projeto Conecta PRO. Para mais detalhes sobre implementação específica de cada módulo, consulte a documentação técnica em `/opt/conecta-pro/docs/`.

---

*Documento gerado automaticamente em: 2026-02-05*
*Versão: 1.0*
*Total de módulos documentados: 34*
