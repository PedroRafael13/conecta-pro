# CONTEXTO DE ADEQUAÇÃO E INTEGRAÇÃO
## Ecossistema Conecta - North Star Architecture

**Data de Geração:** 2026-01-04
**Versão do Documento:** 1.0
**Classificação:** Interno - Estratégico

---

## 1. VISÃO DO ECOSSISTEMA CONECTA

### 1.1 Arquitetura North Star

O Ecossistema Conecta é composto por três sistemas complementares que, juntos, formam uma solução completa de gestão condominial inteligente:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ECOSSISTEMA CONECTA                                   │
│                           (North Star)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐              │
│  │   CONECTA      │   │   CONECTA      │   │   CONECTA      │              │
│  │   GUARDIAN     │   │   MAIS         │   │   PLUS         │              │
│  │   (Satélite)   │   │   (Core ERP)   │   │   (Satélite)   │              │
│  └───────┬────────┘   └───────┬────────┘   └───────┬────────┘              │
│          │                    │                    │                        │
│          │                    │                    │                        │
│          ▼                    ▼                    ▼                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         CAMADA DE DADOS UNIFICADA                    │   │
│  │                     (PostgreSQL + Redis + S3)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Propósito de Cada Sistema

| Sistema | Foco | SLA | Volume |
|---------|------|-----|--------|
| **Conecta Guardian** | Segurança e Vigilância | 99.99% | Real-time |
| **Conecta Mais** | ERP Core | 99.9% | Transacional |
| **Conecta Plus** | Alto Volume | 99.95% | High-throughput |

---

## 2. CONECTA GUARDIAN (Guardião da Integridade)

### 2.1 Propósito Estratégico

O **Conecta Guardian** é o sistema satélite especializado em **segurança condominial**, assumindo todas as responsabilidades de:

- Monitoramento de câmeras (CFTV)
- Controle de acesso (portarias)
- Gestão de alarmes
- Integração com hardware de segurança
- Análise de ocorrências em tempo real

### 2.2 Justificativa da Separação

| Aspecto | No ERP Core | No Guardian |
|---------|-------------|-------------|
| **Latência** | Aceitável (500ms) | Crítica (<100ms) |
| **Disponibilidade** | 99.9% | 99.99% |
| **Escala** | Vertical | Horizontal |
| **Deployment** | Semanal | Contínuo |
| **Especialização** | Generalista | Hardware de segurança |

**Benefícios da Separação:**
1. **Isolamento de Falhas**: Problemas no ERP não afetam a segurança
2. **Escala Independente**: Guardian pode escalar conforme demanda de câmeras
3. **Especialização Técnica**: Time focado em protocolos de segurança
4. **Compliance**: Facilita certificações de segurança (ISO 27001)

### 2.3 Funcionalidades Migradas do ERP

| Funcionalidade | Módulo ERP Origem | Status Guardian |
|----------------|-------------------|-----------------|
| Monitoramento de Câmeras | field_service | Planejado |
| Status de Equipamentos | field_service | Planejado |
| Ocorrências de Segurança | field_service | Planejado |
| Sync com Hardware | field_service | Planejado |
| Logs de Acesso | field_service | Planejado |
| Alertas Real-time | integrations | Planejado |
| Geofencing | hr.mobile_time_clock | Parcial |

### 2.4 Código Base para Guardian (field_service)

O módulo `field_service` do ERP serve como **base técnica** para o Guardian:

```
modules/field_service/                    # Base para Conecta Guardian
├── controllers/
│   ├── equipment_status_controller.py   # → Guardian Equipment API
│   ├── monitoring_controller.py         # → Guardian Monitoring API
│   ├── security_audit_controller.py     # → Guardian Audit API
│   └── ssh_gateway_controller.py        # → Guardian Device Gateway
├── models/
│   ├── equipment_status.py              # → Guardian Equipment Model
│   ├── guardian_occurrence.py           # → Guardian Incident Model
│   └── guardian_sync.py                 # → Guardian Sync Model
├── services/
│   ├── guardian_sync_service.py         # → Guardian Sync Service
│   └── occurrence_analyzer.py           # → Guardian AI Analyzer
└── guardian_logger.py                   # → Guardian Logging
```

### 2.5 Integrações de Hardware

| Fabricante | Protocolo | Funcionalidade | Status |
|------------|-----------|----------------|--------|
| **Intelbras** | API REST | DVRs, NVRs, Câmeras IP | Planejado |
| **Control iD** | API REST | Controle de Acesso | Planejado |
| **Hikvision** | ONVIF/ISAPI | Câmeras, DVRs | Planejado |

### 2.6 Arquitetura Proposta para Guardian

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONECTA GUARDIAN                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Gateway    │  │  Event Bus   │  │   AI/ML      │  │   Dashboard  │    │
│  │   Hardware   │  │   (Kafka)    │  │   Analyzer   │  │   Real-time  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         GUARDIAN CORE API                            │   │
│  │                      (FastAPI + WebSockets)                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Intelbras   │  │  Control iD  │  │   Hikvision  │  │    ONVIF     │    │
│  │   Adapter    │  │   Adapter    │  │   Adapter    │  │   Generic    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CONECTA PLUS (Serviço de Alto Volume)

### 3.1 Propósito Estratégico

O **Conecta Plus** é o sistema satélite especializado em **operações de alto volume** e **interfaces de alta disponibilidade**, assumindo:

- Portal do Morador (alto tráfego)
- Sistema de Reservas (picos de demanda)
- Notificações em Massa
- Comunicados Push
- APIs de Alta Frequência

### 3.2 Justificativa da Separação

| Aspecto | No ERP Core | No Plus |
|---------|-------------|---------|
| **Picos de Carga** | Afeta todo sistema | Isolado |
| **Cache Strategy** | Genérica | Especializada |
| **CDN** | Não otimizado | Edge caching |
| **Autoscaling** | Limitado | Horizontal agressivo |
| **UX Mobile** | Responsivo | Mobile-first |

**Benefícios da Separação:**
1. **Performance**: Otimizado para milhares de requisições/segundo
2. **Custo**: Escala apenas quando necessário (reservas de fim de semana)
3. **UX**: Interface especializada para moradores
4. **Resiliência**: Falhas no Plus não afetam operações críticas do ERP

### 3.3 Funcionalidades Migradas do ERP

| Funcionalidade | Módulo ERP Origem | Status Plus |
|----------------|-------------------|-------------|
| Portal do Morador | clients + hr.employee_portal | Planejado |
| Sistema de Reservas | facilities | Planejado |
| Comunicados Push | config.notification_template | Planejado |
| Chat de Moradores | integrations | Planejado |
| Boletos/2ª Via | financial | Planejado |
| Classificados | (novo) | Planejado |

### 3.4 Código Base para Plus

Os módulos `facilities` e `clients` servem como **base técnica** para o Plus:

```
# Funcionalidades de facilities → Conecta Plus
modules/facilities/
├── controllers/area_controller.py      # → Plus Areas API
├── models/area.py                       # → Plus Area Model
├── repositories/area_repository.py     # → Plus Area Repo
└── services/reservation_service.py     # → Plus Reservation Service

# Funcionalidades de clients → Conecta Plus
modules/clients/
├── models/unit.py                       # → Plus Unit Model
└── services/client_ai_service.py       # → Plus AI Features
```

### 3.5 Arquitetura Proposta para Plus

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONECTA PLUS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Mobile     │  │   Web PWA    │  │   Push       │  │   CDN/Edge   │    │
│  │   Apps       │  │   Portal     │  │   Service    │  │   Cache      │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          PLUS API GATEWAY                            │   │
│  │                    (Rate Limiting + Load Balancing)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                 │                 │                 │             │
│         ▼                 ▼                 ▼                 ▼             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Reservas    │  │  Comunicados │  │  Boletos     │  │  Chat        │    │
│  │  Service     │  │  Service     │  │  Service     │  │  Service     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CONECTA MAIS (Core ERP)

### 4.1 Papel no Ecossistema

Após a extração de funcionalidades para Guardian e Plus, o **Conecta Mais** permanece como o **Core ERP**, focado em:

- **Dados Mestres**: Condomínios, Unidades, Moradores
- **Backoffice**: Administração, Configurações
- **Financeiro Core**: Contabilidade, Fluxo de Caixa
- **RH**: Gestão de Funcionários, Folha
- **CRM**: Leads, Oportunidades, Contratos
- **Relatórios**: BI, Dashboards Gerenciais
- **Auditoria**: Logs, Compliance

### 4.2 Módulos que Permanecem no Core

| Módulo | Justificativa |
|--------|---------------|
| **audit** | Compliance e logs centralizados |
| **clients** | Dados mestres (source of truth) |
| **config** | Configurações do ecossistema |
| **core** | Autenticação e base |
| **crm** | Processos de venda |
| **diarists** | Gestão de terceiros |
| **document_kits** | Templates de documentos |
| **equipment_management** | Patrimônio/Comodato |
| **financial** | Contabilidade e BI |
| **ged** | Gestão de documentos |
| **hr** | RH completo |
| **integrations** | Integrações de backoffice |
| **occurrences** | Gestão de incidentes |
| **operations** | Escalas e operações |
| **recruitment** | Recrutamento |
| **reports** | Relatórios gerenciais |
| **services** | Ordens de serviço |

### 4.3 Funcionalidades Removidas/Migradas

| Funcionalidade | Destino | Motivo |
|----------------|---------|--------|
| Monitoramento CFTV | Guardian | Especialização em segurança |
| Controle de Acesso | Guardian | Real-time e hardware |
| Reservas de Áreas | Plus | Alto volume de transações |
| Portal do Morador | Plus | Alta disponibilidade |
| Push Notifications | Plus | Escala de notificações |

---

## 5. INTEGRAÇÃO ENTRE SISTEMAS

### 5.1 Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLUXO DE DADOS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐           │
│  │   GUARDIAN  │ ◀────── │  MAIS (ERP) │ ──────▶ │    PLUS     │           │
│  │   Security  │  Sync   │    Core     │  Sync   │  High Vol   │           │
│  └──────┬──────┘         └──────┬──────┘         └──────┬──────┘           │
│         │                       │                       │                   │
│         │     Events            │    Data Master        │    Events         │
│         ▼                       ▼                       ▼                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         EVENT BUS (Kafka/Redis Streams)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                       │                       │                   │
│         ▼                       ▼                       ▼                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         BANCO DE DADOS UNIFICADO                     │   │
│  │                            (PostgreSQL 16)                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Contratos de API

| Origem | Destino | Tipo | Dados |
|--------|---------|------|-------|
| ERP → Guardian | REST | Dados de condomínios, configurações |
| Guardian → ERP | Events | Ocorrências, alertas |
| ERP → Plus | REST | Dados de unidades, moradores |
| Plus → ERP | Events | Reservas, comunicados |
| Guardian → Plus | Events | Alertas para moradores |

### 5.3 Estratégia de Sincronização

1. **Dados Mestres**: Source of truth no ERP, replicação para satélites
2. **Eventos**: Publicação em Event Bus, consumo assíncrono
3. **Cache**: Redis compartilhado com namespaces isolados
4. **Consistência**: Eventual consistency com reconciliação periódica

---

## 6. ROADMAP DE MIGRAÇÃO

### 6.1 Fase 1: Preparação (Atual)
- [x] Diagnóstico do ERP Core
- [x] Melhoria de qualidade de código
- [x] Documentação de arquitetura
- [ ] Definição de contratos de API

### 6.2 Fase 2: Conecta Guardian v1.0
- [ ] Extração do módulo field_service
- [ ] Implementação de adapters de hardware
- [ ] Gateway de dispositivos
- [ ] Dashboard de monitoramento

### 6.3 Fase 3: Conecta Plus v1.0
- [ ] Extração de facilities (reservas)
- [ ] Portal do Morador
- [ ] Sistema de notificações
- [ ] CDN e caching

### 6.4 Fase 4: Integração Completa
- [ ] Event Bus (Kafka/Redis Streams)
- [ ] Sincronização de dados
- [ ] SSO unificado
- [ ] Observability centralizado

---

## 7. BENEFÍCIOS ESPERADOS

### 7.1 Técnicos

| Benefício | Métrica |
|-----------|---------|
| Disponibilidade Guardian | 99.99% (vs 99.9% atual) |
| Latência de Câmeras | <100ms (vs 500ms atual) |
| Throughput do Plus | 10k req/s (vs 1k atual) |
| Deploy Independente | Sim (vs deploy único) |

### 7.2 Negócio

| Benefício | Impacto |
|-----------|---------|
| Novos Clientes | Venda modular de soluções |
| Uptime de Segurança | Redução de incidentes |
| Satisfação Moradores | Portal mais rápido |
| Custo de Infraestrutura | Escala sob demanda |

### 7.3 Operacionais

| Benefício | Impacto |
|-----------|---------|
| Time de Segurança | Especialização |
| Atualizações | Menor risco |
| Debugging | Isolamento de problemas |
| Compliance | Certificações específicas |

---

## 8. RISCOS E MITIGAÇÕES

### 8.1 Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Inconsistência de dados | Média | Alto | Reconciliação periódica |
| Complexidade operacional | Alta | Médio | Observability unificado |
| Curva de aprendizado | Média | Médio | Documentação e treinamento |
| Custos de infraestrutura | Média | Médio | Escala sob demanda |

### 8.2 Plano de Rollback

Em caso de falha na migração:
1. Manter ERP Core funcional como fallback
2. Feature flags para habilitar/desabilitar satélites
3. Sincronização bidirecional de dados
4. Documentação de procedimentos de rollback

---

## 9. CONCLUSÃO

A arquitetura do Ecossistema Conecta representa uma evolução natural do ERP monolítico para um sistema distribuído especializado. A separação em três componentes (Guardian, Mais, Plus) permite:

1. **Especialização técnica** por domínio
2. **Escala independente** conforme demanda
3. **Resiliência** através de isolamento de falhas
4. **Agilidade** em deploys e atualizações
5. **Flexibilidade comercial** na venda de soluções

O ERP Conecta Mais permanece como o **coração do ecossistema**, mantendo os dados mestres e processos de backoffice, enquanto Guardian e Plus atendem a necessidades específicas de segurança e alto volume.

---

## 10. ANEXOS

### 10.1 Glossário

| Termo | Definição |
|-------|-----------|
| **North Star** | Visão arquitetural de longo prazo |
| **Satélite** | Sistema especializado que orbita o Core |
| **Event Bus** | Barramento de eventos para comunicação assíncrona |
| **Source of Truth** | Fonte autoritativa de dados |
| **Edge Caching** | Cache em pontos próximos ao usuário |

### 10.2 Referências

- Documentação do PostgreSQL 16
- FastAPI Best Practices
- Event-Driven Architecture Patterns
- Microservices Patterns (Chris Richardson)

---

*Documento gerado automaticamente - Claude Code*
*Data: 2026-01-04*
