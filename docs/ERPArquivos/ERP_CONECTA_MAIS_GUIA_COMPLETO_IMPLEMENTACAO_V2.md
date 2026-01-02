# 🏢 ERP CONECTA MAIS - GUIA COMPLETO DE IMPLEMENTAÇÃO
## Sistema Integrado de Gestão Empresarial com Inteligência Artificial
### Versão 2.0 - Documentação Técnica Definitiva

---

**Data:** 30 de Dezembro de 2024  
**Empresa:** Conecta Mais Tecnologia  
**CNPJ:** 35.710.481/0001-03  
**Localização:** Manaus, Amazonas, Brasil  
**Website:** www.conectamaistech.com.br

---

## 📑 ÍNDICE

1. [VISÃO GERAL E ARQUITETURA](#1-visão-geral-e-arquitetura)
2. [ANÁLISE DOS SISTEMAS DE REFERÊNCIA](#2-análise-dos-sistemas-de-referência)
3. [ARQUITETURA TÉCNICA DETALHADA](#3-arquitetura-técnica-detalhada)
4. [ESPECIFICAÇÃO DOS 38 MÓDULOS](#4-especificação-dos-38-módulos)
5. [CAMADA DE INTELIGÊNCIA ARTIFICIAL](#5-camada-de-inteligência-artificial)
6. [MCPs - MODEL CONTEXT PROTOCOLS](#6-mcps-model-context-protocols)
7. [SKILLS - HABILIDADES REUTILIZÁVEIS](#7-skills-habilidades-reutilizáveis)
8. [AGENTES DE IA ESPECIALIZADOS](#8-agentes-de-ia-especializados)
9. [INTEGRAÇÕES BANCÁRIAS](#9-integrações-bancárias)
10. [INTEGRAÇÕES GOVERNAMENTAIS](#10-integrações-governamentais)
11. [MOBILE APPS](#11-mobile-apps)
12. [SEGURANÇA E COMPLIANCE](#12-segurança-e-compliance)
13. [MODELO DE DADOS](#13-modelo-de-dados)
14. [APIs E ENDPOINTS](#14-apis-e-endpoints)
15. [INFRAESTRUTURA E DEVOPS](#15-infraestrutura-e-devops)
16. [ROADMAP DE IMPLEMENTAÇÃO](#16-roadmap-de-implementação)
17. [PLANO DE TESTES](#17-plano-de-testes)
18. [ESTRATÉGIA DE MIGRAÇÃO](#18-estratégia-de-migração)
19. [TREINAMENTO E DOCUMENTAÇÃO](#19-treinamento-e-documentação)
20. [MÉTRICAS E KPIs](#20-métricas-e-kpis)

---

# 1. VISÃO GERAL E ARQUITETURA

## 1.1 Contexto do Negócio

### 1.1.1 Perfil da Conecta Mais

**Modelo de Negócio:**
A Conecta Mais é uma empresa de segurança e tecnologia especializada em serviços para condomínios, oferecendo:

- **Segurança Patrimonial:** Vigilantes desarmados, porteiros, recepcionistas
- **Segurança Eletrônica:** CFTV, alarmes, controle de acesso, sensores
- **Portaria Remota:** Atendimento digital 24h
- **Central de Monitoramento:** Monitoramento 24h de alarmes e câmeras
- **Facilities:** Limpeza, jardinagem, manutenção predial
- **Gestão de Acesso:** Controle de moradores, visitantes, prestadores

**Segmento Principal:**
- 🏢 Condomínios residenciais e comerciais (foco principal)
- 🏭 Empresas privadas
- 🏪 Shopping centers
- 🏥 Hospitais e clínicas
- 🏫 Escolas e universidades

**Características Operacionais:**
- Contratos recorrentes mensais (principal fonte de receita)
- Contratos pontuais (instalação, manutenção)
- Múltiplos postos de trabalho simultâneos
- Equipes alocadas 24/7
- Rotatividade operacional (diaristas, treinamentos)
- Alto volume de documentação para clientes
- Dependência de compliance e CNDs

### 1.1.2 Desafios Atuais

**Processos Manuais:**
- ❌ Montagem manual de kits documentais (crítico - impacta recebimento)
- ❌ Gestão de diaristas via WhatsApp
- ❌ Planilhas Excel para controle
- ❌ Falta de integração entre sistemas
- ❌ Retrabalho e duplicação de dados
- ❌ Risco de erros humanos

**Gestão Operacional:**
- ❌ Dificuldade em alocar recursos otimamente
- ❌ Controle de escalas complexo
- ❌ Absenteísmo difícil de prever
- ❌ Ocorrências não centralizadas
- ❌ Falta de visibilidade em tempo real

**Gestão Financeira:**
- ❌ Fluxo de caixa manual
- ❌ Inadimplência não gerenciada proativamente
- ❌ Custos não rastreados por posto/contrato
- ❌ Dificuldade em análise de rentabilidade

**Gestão de Pessoas:**
- ❌ Processos de RH descentralizados
- ❌ Folha de pagamento complexa (CLT + diaristas + PJ)
- ❌ Recrutamento não otimizado
- ❌ Treinamentos não rastreados
- ❌ SST (Segurança do Trabalho) não sistematizado

**Relacionamento com Cliente:**
- ❌ Comunicação fragmentada
- ❌ Falta de portal self-service
- ❌ Documentação não automatizada
- ❌ Aprovações manuais

### 1.1.3 Objetivos do Projeto

**Objetivos de Negócio:**
1. ✅ **Automatizar 100% dos processos manuais**
2. ✅ **Reduzir tempo de montagem de kits de 4h para 5 minutos**
3. ✅ **Eliminar erros em documentação (zero rejeições de clientes)**
4. ✅ **Otimizar alocação de recursos (reduzir custos em 20-30%)**
5. ✅ **Melhorar fluxo de caixa (reduzir inadimplência em 50%)**
6. ✅ **Aumentar produtividade do time (liberar 40% do tempo)**
7. ✅ **Melhorar satisfação do cliente (NPS > 70)**
8. ✅ **Escalar operação sem aumentar headcount proporcional**

**Objetivos Técnicos:**
1. ✅ **Sistema 100% integrado (ERP + Conecta Plus + Conecta Guardian)**
2. ✅ **Backend Python (compatível com sistemas existentes)**
3. ✅ **Cloud-native e escalável**
4. ✅ **APIs RESTful completas**
5. ✅ **Mobile-first (apps nativos)**
6. ✅ **IA embarcada (agentes, predições, automações)**
7. ✅ **Integrações bancárias nativas (Cora + Inter)**
8. ✅ **Compliance total (LGPD, eSocial, SPED)**

---

## 1.2 Arquitetura do Ecossistema (CORRIGIDA)

### 1.2.1 Visão Geral Correta

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                  🏢 ERP CONECTA MAIS                          │
│                   (NÚCLEO CENTRAL)                            │
│                                                                │
│  • Gestão Comercial e Contratos                              │
│  • Recursos Humanos e Folha                                  │
│  • Financeiro e Contábil                                     │
│  • Compras e Estoque                                         │
│  • Business Intelligence                                     │
│  • Administração e Configurações                             │
│                                                                │
└────────────────┬───────────────────────┬─────────────────────┘
                 │                       │
                 │                       │
     ┌───────────┴──────────┐   ┌───────┴────────────────┐
     │                      │   │                        │
     ▼                      │   ▼                        │
┌─────────────────┐         │   ┌────────────────────┐  │
│ CONECTA PLUS    │◄────────┼──►│ CONECTA GUARDIAN   │  │
│ (Clientes)      │         │   │ (Técnico/Ops)      │  │
│                 │         │   │                    │  │
│ • Portal Web    │         │   │ • Portaria Remota  │  │
│ • App Cliente   │         │   │ • Central 24h      │  │
│ • Dashboard     │         │   │ • CFTV             │  │
│ • Solicitações  │         │   │ • Alarmes          │  │
│ • Pagamentos    │         │   │ • Controle Acesso  │  │
│ • Relatórios    │         │   │ • Sensores         │  │
│ • Agentes IA    │         │   │ • IoT              │  │
└─────────────────┘         │   └────────────────────┘  │
                            │                            │
                            │                            │
         ┌──────────────────┴────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────┐
│         🤖 CAMADA DE IA COMPARTILHADA                      │
│                                                            │
│  • Agentes de IA (Comercial, Operacional, RH, etc)       │
│  • MCPs (Model Context Protocols)                         │
│  • Skills (Habilidades Reutilizáveis)                    │
│  • ML Models (Predição, Classificação, NLP)              │
│  • Data Warehouse (histórico unificado)                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**IMPORTANTE:** O ERP é o **CENTRO** do ecossistema. Ele **SE INTEGRA** com Conecta Plus e Conecta Guardian, e não o contrário.

### 1.2.2 Fluxo de Dados e Responsabilidades

#### **ERP CONECTA MAIS (Sistema Mãe)**
**Responsabilidades:**
- ✅ Fonte da verdade para: contratos, clientes, funcionários, financeiro, estoque
- ✅ Processa: folha de pagamento, faturamento, contabilidade, compras
- ✅ Gera: relatórios gerenciais, kits documentais, análises
- ✅ Controla: permissões, usuários, configurações globais
- ✅ Distribui dados para: Conecta Plus e Conecta Guardian

**Envia para Conecta Plus:**
- Cliente cadastrado → dados básicos
- Contrato ativado → acesso ao portal
- Fatura gerada → boleto/cobrança
- OS criada → acompanhamento
- Relatório solicitado → disponibilização

**Envia para Conecta Guardian:**
- Posto alocado → configuração técnica
- Equipamento instalado → registro
- Escala definida → programação operacional
- Manutenção agendada → ordem de serviço técnica
- Alarme configurado → parâmetros

**Recebe do Conecta Plus:**
- Solicitações do cliente
- Aprovações de documentos
- Pagamentos realizados
- Feedbacks e avaliações

**Recebe do Conecta Guardian:**
- Eventos de alarme
- Ocorrências operacionais
- Status de equipamentos
- Logs de acesso
- Imagens de câmeras

#### **CONECTA PLUS (Sistema para Clientes)**
**Responsabilidades:**
- ✅ Interface com cliente final
- ✅ Portal self-service
- ✅ Solicitações e tickets
- ✅ Visualização de dados
- ✅ Aprovações digitais
- ✅ Pagamentos online

**Não faz:**
- ❌ Não gerencia contratos (só visualiza)
- ❌ Não processa folha
- ❌ Não faz contabilidade
- ❌ Não gerencia estoque

#### **CONECTA GUARDIAN (Sistema Técnico/Operacional)**
**Responsabilidades:**
- ✅ Portaria remota
- ✅ Central de monitoramento 24h
- ✅ Gestão técnica de equipamentos
- ✅ Recepção de alarmes
- ✅ Controle de acesso em tempo real
- ✅ Gravação e análise de imagens

**Não faz:**
- ❌ Não gerencia contratos (só executa)
- ❌ Não processa folha
- ❌ Não faz faturamento
- ❌ Não gerencia RH

---

## 1.3 Princípios de Arquitetura

### 1.3.1 Arquitetura de Software

**Padrão:** Microservices + Event-Driven Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    API GATEWAY                            │
│              (Kong / AWS API Gateway)                     │
└──────────────────┬────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┬─────────────┐
        │                     │              │             │
        ▼                     ▼              ▼             ▼
┌──────────────┐    ┌──────────────┐  ┌──────────┐  ┌──────────┐
│  Comercial   │    │     RH/      │  │Financeiro│  │    BI    │
│  Service     │    │   Folha      │  │ Service  │  │ Service  │
│  (Python)    │    │  Service     │  │(Python)  │  │(Python)  │
└──────┬───────┘    │  (Python)    │  └────┬─────┘  └────┬─────┘
       │            └──────┬───────┘       │             │
       │                   │               │             │
       └──────────┬────────┴───────────────┴─────────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │   MESSAGE BROKER     │
       │  (RabbitMQ / Kafka)  │
       └──────────┬───────────┘
                  │
       ┌──────────┴───────────┬──────────────┐
       │                      │              │
       ▼                      ▼              ▼
┌──────────────┐    ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │    │   MongoDB    │  │    Redis     │
│  (Relacional)│    │    (NoSQL)   │  │   (Cache)    │
└──────────────┘    └──────────────┘  └──────────────┘
```

### 1.3.2 Stack Tecnológico (Backend Python)

**Backend:**
- **Linguagem:** Python 3.11+
- **Framework:** FastAPI (APIs) + Django (Admin/ORM)
- **ORM:** SQLAlchemy + Django ORM
- **Validação:** Pydantic
- **Async:** asyncio, aiohttp
- **Task Queue:** Celery + Redis
- **Testes:** pytest, pytest-asyncio

**Frontend:**
- **Web:** React.js 18+ (TypeScript)
- **Mobile:** React Native (iOS + Android)
- **State Management:** Redux Toolkit / Zustand
- **UI:** Material-UI / Tailwind CSS
- **Charts:** Recharts, Apache ECharts

**Databases:**
- **Principal:** PostgreSQL 15+ (dados relacionais)
- **Documentos:** MongoDB 6+ (logs, ocorrências, documentos)
- **Cache:** Redis 7+ (sessões, cache, filas)
- **Busca:** Elasticsearch 8+ (logs, busca full-text)
- **Warehouse:** Snowflake / BigQuery (BI)

**Inteligência Artificial:**
- **ML Framework:** scikit-learn, XGBoost, LightGBM
- **Deep Learning:** PyTorch, TensorFlow
- **NLP:** Transformers (Hugging Face), spaCy
- **LLMs:** Claude API (Anthropic), GPT-4 (OpenAI)
- **Computer Vision:** OpenCV, YOLO, MediaPipe

**Infraestrutura:**
- **Cloud:** AWS (preferencial) ou GCP/Azure
- **Containers:** Docker + Docker Compose
- **Orquestração:** Kubernetes (EKS/GKE)
- **CI/CD:** GitHub Actions / GitLab CI
- **IaC:** Terraform + Ansible
- **Monitoring:** Datadog / New Relic / Prometheus+Grafana

**Integrações:**
- **APIs:** httpx (async HTTP client)
- **Webhooks:** FastAPI webhooks
- **Open Banking:** SDK Banco Inter, API Cora
- **Governo:** Zeep (SOAP - eSocial), requests (REST)

### 1.3.3 Padrões de Desenvolvimento

**Arquitetura em Camadas:**
```
┌─────────────────────────────────────┐
│      Presentation Layer             │  (APIs REST, GraphQL)
├─────────────────────────────────────┤
│      Application Layer              │  (Business Logic, Services)
├─────────────────────────────────────┤
│      Domain Layer                   │  (Entities, Value Objects)
├─────────────────────────────────────┤
│      Infrastructure Layer           │  (Database, External APIs)
└─────────────────────────────────────┘
```

**Design Patterns:**
- ✅ Repository Pattern (acesso a dados)
- ✅ Factory Pattern (criação de objetos)
- ✅ Strategy Pattern (algoritmos intercambiáveis)
- ✅ Observer Pattern (eventos)
- ✅ Dependency Injection (IoC)
- ✅ CQRS (Command Query Responsibility Segregation)

**Princípios SOLID:**
- ✅ Single Responsibility
- ✅ Open/Closed
- ✅ Liskov Substitution
- ✅ Interface Segregation
- ✅ Dependency Inversion

**Clean Code:**
- ✅ Nomenclatura clara e descritiva
- ✅ Funções pequenas e focadas
- ✅ Comentários apenas quando necessário
- ✅ Type hints em Python
- ✅ Docstrings em todas as funções públicas
- ✅ Testes unitários (cobertura > 80%)

---

# 2. ANÁLISE DOS SISTEMAS DE REFERÊNCIA

## 2.1 N1 Sistemas

### 2.1.1 Funcionalidades Mapeadas

**Gestão Comercial:**
- ✅ CRM básico
- ✅ Propostas comerciais
- ✅ Funil de vendas

**Gestão de Contratos:**
- ✅ Contratos recorrentes e pontuais
- ✅ Renovação automática
- ✅ Reajustes (índices econômicos)
- ✅ Aditivos
- ✅ SLA

**Gestão Operacional:**
- ✅ Cadastro de postos
- ✅ Escalas de trabalho
- ✅ Ordens de serviço
- ✅ Technology Park (equipamentos em comodato)

**Gestão Financeira:**
- ✅ Contas a pagar/receber
- ✅ Fluxo de caixa
- ✅ Faturamento automático
- ✅ Boletos e PIX
- ✅ DRE

**Gestão de Estoque:**
- ✅ Controle de equipamentos
- ✅ Movimentações
- ✅ Inventário

**Notas Fiscais:**
- ✅ NF-e
- ✅ NFS-e
- ✅ Integração SEFAZ

### 2.1.2 Gaps Identificados

**O que N1 NÃO tem mas precisamos:**
- ❌ RH completo (recrutamento, avaliação)
- ❌ Folha de pagamento
- ❌ Ponto eletrônico
- ❌ SST (Segurança do Trabalho)
- ❌ BI avançado
- ❌ Inteligência Artificial
- ❌ App mobile robusto
- ❌ Gestão de kits documentais
- ❌ Gestão de diaristas automatizada
- ❌ Conta digital integrada

---

## 2.2 HControl (Harmonit)

### 2.2.1 Funcionalidades Mapeadas

**Ordens de Serviço Mobile:**
- ✅ Agenda de OS
- ✅ Navegação GPS
- ✅ Assinatura digital
- ✅ Fotos do serviço
- ✅ CPF do recebedor

**Gestão Financeira:**
- ✅ Contas a pagar/receber
- ✅ DRE
- ✅ Comparativos mensais

**Vendas:**
- ✅ Orçamentos mobile
- ✅ Assinatura digital
- ✅ Pré-cadastro de clientes

### 2.2.2 Gaps Identificados

**O que HControl NÃO tem mas precisamos:**
- ❌ CRM completo
- ❌ RH e Folha
- ❌ Ponto eletrônico
- ❌ BI avançado
- ❌ IA
- ❌ Integrações bancárias robustas
- ❌ SST
- ❌ Gestão de kits

---

## 2.3 Bling ERP

### 2.3.1 Funcionalidades Mapeadas

**E-commerce e Vendas:**
- ✅ Integração com +250 marketplaces
- ✅ PDV (Frente de Caixa)
- ✅ Sincronização de estoque
- ✅ Checkout automatizado

**Estoque:**
- ✅ Múltiplos depósitos
- ✅ Controle de lotes e séries
- ✅ Curva ABC
- ✅ Alertas de reposição
- ✅ Custeio (médio, PEPS, UEPS)

**Financeiro:**
- ✅ Conta digital PJ gratuita (Bling Conta)
- ✅ PIX, boletos, cartões
- ✅ Conciliação automática
- ✅ Antecipação de recebíveis
- ✅ Links de pagamento

**Fiscal:**
- ✅ NF-e/NFS-e automática
- ✅ Cálculo de impostos
- ✅ SPED Fiscal
- ✅ Integração com contabilidade

**Produção:**
- ✅ Ordens de produção
- ✅ BOM (Bill of Materials)
- ✅ Controle de matéria-prima

**Relatórios:**
- ✅ +200 relatórios pré-configurados
- ✅ Construtor de relatórios customizados
- ✅ Dashboards

**Integrações:**
- ✅ +250 integrações nativas
- ✅ API REST completa
- ✅ Webhooks

**Automações:**
- ✅ +80 automações disponíveis

### 2.3.2 Gaps Identificados

**O que Bling NÃO tem mas precisamos:**
- ❌ RH e Folha
- ❌ Ponto eletrônico
- ❌ SST
- ❌ Gestão de postos/escalas
- ❌ Gestão de contratos de serviço recorrente
- ❌ Ordens de serviço operacionais
- ❌ IA avançada
- ❌ Gestão de kits documentais
- ❌ Gestão de diaristas

---

## 2.4 Sólides (RH & DP)

### 2.4.1 Funcionalidades Mapeadas

**Recrutamento e Seleção:**
- ✅ Portal de vagas
- ✅ Banco de talentos
- ✅ Triagem automática com IA
- ✅ **Profiler (Análise Comportamental DISC)** - mapeamento de +50 competências em 7 min com 97% de acurácia
- ✅ Testes técnicos online
- ✅ Videoconferência integrada
- ✅ Feedbacks automáticos

**Controle de Ponto:**
- ✅ Ponto eletrônico digital
- ✅ **Reconhecimento Facial**
- ✅ **Geolocalização**
- ✅ Modo offline
- ✅ App + Totem + Web
- ✅ Banco de horas
- ✅ Tratamento de ponto
- ✅ Horas extras
- ✅ Escalas
- ✅ Fechamento de folha ponto
- ✅ **50% de redução no tempo de fechamento**

**Folha de Pagamento:**
- ✅ Cálculo automático
- ✅ **25x mais rápida e 30% mais econômica**
- ✅ Adiantamentos
- ✅ 13º salário
- ✅ Férias
- ✅ Rescisões
- ✅ Informe de rendimentos
- ✅ Holerites digitais via app
- ✅ Integração eSocial, CAGED, SEFIP

**Admissão Digital:**
- ✅ 100% digital
- ✅ Assinatura eletrônica
- ✅ Coleta de documentos online
- ✅ Onboarding automatizado

**Férias:**
- ✅ Solicitação via app
- ✅ Aprovação por gestor
- ✅ Programação anual
- ✅ Cálculo automático

**GED:**
- ✅ Repositório digital
- ✅ Controle de vencimento
- ✅ Assinatura digital
- ✅ Histórico

**Desempenho:**
- ✅ Avaliação 360°
- ✅ PDI (Plano de Desenvolvimento Individual)
- ✅ Feedbacks contínuos
- ✅ Metas e OKRs
- ✅ One-on-One

**Clima Organizacional:**
- ✅ Pesquisas de clima
- ✅ Engajamento
- ✅ Pulse surveys
- ✅ eNPS
- ✅ Análise de sentimento

**Treinamento:**
- ✅ Trilhas de aprendizagem
- ✅ LMS integrado
- ✅ Certificações
- ✅ Matriz de competências

**Benefícios:**
- ✅ Cartão multibenefícios (8 categorias)
- ✅ Vale alimentação/refeição
- ✅ Vale transporte
- ✅ Planos de saúde
- ✅ Benefícios flexíveis
- ✅ **Clube de vantagens** (descontos e cashback)

**Inteligência Comportamental (Profiler):**
- ✅ Mapeamento de perfil
- ✅ Análise DISC
- ✅ Compatibilidade
- ✅ Fit cultural
- ✅ Recomendações para liderança

**People Analytics:**
- ✅ Dashboards interativos
- ✅ KPIs de RH
- ✅ Turnover, absenteísmo
- ✅ ROI de RH
- ✅ Análise demográfica
- ✅ Distribuição por perfil
- ✅ Employer branding

**Super App para Colaboradores:**
- ✅ Bater ponto (facial + geo)
- ✅ Solicitar férias/atestados
- ✅ Consultar holerite
- ✅ Acessar PDI
- ✅ Dar/receber feedbacks
- ✅ Assinar documentos
- ✅ Visualizar avisos
- ✅ Clube de vantagens

**App para Lideranças:**
- ✅ Gestão de equipe
- ✅ Aprovação de solicitações
- ✅ Acompanhamento de ponto
- ✅ Gestão de ajustes
- ✅ Visão consolidada

**IA (Copilot Sólides):**
- ✅ Feedbacks automáticos
- ✅ Triagem inteligente de CVs
- ✅ Sugestões de treinamento
- ✅ Alertas preditivos

### 2.4.2 Gaps Identificados

**O que Sólides NÃO tem mas precisamos:**
- ❌ Gestão comercial
- ❌ Gestão de contratos
- ❌ Financeiro completo
- ❌ Compras e estoque
- ❌ Faturamento e NF-e
- ❌ SST completo (tem básico)
- ❌ Gestão de postos/escalas operacionais
- ❌ Gestão de diaristas
- ❌ Gestão de kits documentais

---

## 2.5 Nucont (Contabilidade Consultiva)

### 2.5.1 Funcionalidades Mapeadas

**Dashboards e Indicadores:**
- ✅ Painéis visuais interativos
- ✅ Gráficos coloridos
- ✅ Linha do tempo
- ✅ Análise gerencial
- ✅ Indicadores financeiros
- ✅ Índices de liquidez, rentabilidade, endividamento

**Análise de Desempenho:**
- ✅ DRE gerencial
- ✅ Fluxo de caixa projetado
- ✅ Análise vertical e horizontal
- ✅ Comparativos mês a mês
- ✅ Análise de tendências
- ✅ Diagnóstico de problemas
- ✅ Identificação de oportunidades

**Relatórios Gerenciais:**
- ✅ +1000 relatórios consultivos
- ✅ Geração automatizada
- ✅ Baseados em dados fiscais, folha, contábil, financeiro
- ✅ Customizados por cliente
- ✅ Envio automático

**Integrações Contábeis:**
- ✅ Importação de balancete
- ✅ Integração com sistemas contábeis (Contabit, Fortes, etc)
- ✅ Atualização automática

**Contabilidade Consultiva:**
- ✅ Análise de performance
- ✅ Consultoria baseada em dados
- ✅ Tomada de decisão estratégica
- ✅ Acompanhamento recorrente
- ✅ Planos de ação

### 2.5.2 Gaps Identificados

**O que Nucont NÃO tem mas precisamos:**
- ❌ Não é um ERP (só visualização e análise)
- ❌ Não gerencia operação
- ❌ Não processa transações
- ❌ Não tem RH/Folha
- ❌ Não tem comercial
- ❌ Depende de sistemas contábeis externos

---

## 2.6 Síntese: O que o ERP Conecta Mais DEVE TER

### 2.6.1 Matriz Comparativa

| Funcionalidade | N1 | HControl | Bling | Sólides | Nucont | **ERP Conecta Mais** |
|---------------|-------|----------|-------|---------|--------|---------------------|
| **CRM Comercial** | ✅ Básico | ✅ Básico | ✅ Avançado | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Contratos** | ✅✅ Avançado | ✅ Avançado | ✅ Básico | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Postos/Escalas** | ✅ Avançado | ✅ Básico | ❌ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Facilities** | ✅ Básico | ❌ | ❌ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **RH Completo** | ❌ | ❌ | ❌ | ✅✅ | ❌ | ✅✅ **Avançado + IA** |
| **Recrutamento** | ❌ | ❌ | ❌ | ✅✅ | ❌ | ✅✅ **Avançado + IA** |
| **Ponto Eletrônico** | ❌ | ❌ | ❌ | ✅✅ | ❌ | ✅✅ **Avançado + IA** |
| **Folha Pagamento** | ❌ | ❌ | ❌ | ✅✅ | ❌ | ✅✅ **Avançado + IA** |
| **SST Completo** | ❌ | ❌ | ❌ | ✅ Básico | ❌ | ✅✅ **Avançado + IA** |
| **Financeiro** | ✅ Avançado | ✅ Básico | ✅✅ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Conta Digital** | ❌ | ❌ | ✅ | ❌ | ❌ | ✅✅ **Integrada Cora+Inter** |
| **NF-e/NFS-e** | ✅ | ✅ | ✅✅ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Fiscal** | ✅ | ✅ | ✅✅ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Contabilidade** | ❌ | ❌ | ✅ Básico | ❌ | ✅✅ | ✅✅ **Avançado + IA** |
| **Custos** | ✅ | ✅ | ✅ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Compras** | ✅ | ❌ | ✅✅ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **Estoque** | ✅✅ | ✅ | ✅✅ | ❌ | ❌ | ✅✅ **Avançado + IA** |
| **BI/Analytics** | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅✅✅ **Muito Avançado + IA** |
| **Relatórios** | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅✅✅ **+300 + IA** |
| **App Mobile** | ✅ | ✅ | ✅ | ✅✅ | ❌ | ✅✅✅ **Nativo + IA** |
| **Integrações** | ✅ | ✅ | ✅✅ +250 | ✅ | ✅ | ✅✅✅ **+300 + MCPs** |
| **Kits Documentais** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅✅✅ **Automático + IA** |
| **Diaristas** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅✅✅ **Gestão Completa + IA** |
| **Agentes IA** | ❌ | ❌ | ❌ | ✅ Básico | ❌ | ✅✅✅ **8 Agentes Especializados** |
| **MCPs** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅✅✅ **40+ MCPs** |
| **Skills** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅✅✅ **60+ Skills** |

**Conclusão:** O ERP Conecta Mais terá **TUDO** dos 5 sistemas referência **+ MUITO MAIS** com IA, automação e funcionalidades específicas.

---

# 3. ARQUITETURA TÉCNICA DETALHADA

## 3.1 Visão de Alto Nível

### 3.1.1 Diagrama de Componentes

```
┌────────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Web App    │  │  Mobile App │  │ Admin Panel │          │
│  │  (React)    │  │ (RN iOS/And)│  │  (Django)   │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                   │
└─────────┼────────────────┼────────────────┼───────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
┌──────────────────────────┼────────────────────────────────────┐
│                    API GATEWAY                                 │
│              (Kong / AWS API Gateway)                          │
│                                                                │
│  • Authentication & Authorization                              │
│  • Rate Limiting                                              │
│  • Request Routing                                            │
│  • SSL/TLS Termination                                        │
│  • API Versioning                                             │
│  • Logging & Monitoring                                       │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────┼───────────────────────────────────────┐
│                  MICROSERVICES LAYER                           │
├────────────────────────┼───────────────────────────────────────┤
│                        │                                       │
│  ┌─────────────────────┴────────────────────────────────────┐ │
│  │                                                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │  Commercial  │  │     HR &     │  │  Financial   │  │ │
│  │  │   Service    │  │    Payroll   │  │   Service    │  │ │
│  │  │  (FastAPI)   │  │   Service    │  │  (FastAPI)   │  │ │
│  │  │              │  │  (FastAPI)   │  │              │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │ │
│  │         │                  │                  │          │ │
│  │  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  │ │
│  │  │  Operations  │  │  Purchasing  │  │      BI      │  │ │
│  │  │   Service    │  │   Service    │  │   Service    │  │ │
│  │  │  (FastAPI)   │  │  (FastAPI)   │  │  (FastAPI)   │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │ │
│  │         │                  │                  │          │ │
│  └─────────┼──────────────────┼──────────────────┼──────────┘ │
│            │                  │                  │            │
│            └──────────────────┼──────────────────┘            │
│                               │                               │
│  ┌────────────────────────────┼──────────────────────────┐   │
│  │           AI SERVICES LAYER │                         │   │
│  │                             │                         │   │
│  │  ┌──────────────┐  ┌────────┴──────┐  ┌───────────┐ │   │
│  │  │  Prediction  │  │  NLP Service  │  │    CV     │ │   │
│  │  │   Service    │  │   (FastAPI)   │  │  Service  │ │   │
│  │  │  (FastAPI)   │  │               │  │ (FastAPI) │ │   │
│  │  └──────┬───────┘  └───────┬───────┘  └─────┬─────┘ │   │
│  │         │                   │                │       │   │
│  └─────────┼───────────────────┼────────────────┼───────┘   │
│            │                   │                │           │
└────────────┼───────────────────┼────────────────┼───────────┘
             │                   │                │
┌────────────┼───────────────────┼────────────────┼───────────┐
│       EVENT BUS / MESSAGE BROKER                           │
│         (RabbitMQ / Apache Kafka)                          │
│                                                            │
│  • Event Sourcing                                         │
│  • Async Communication                                    │
│  • Event Replay                                           │
│  • SAGA Pattern                                           │
└────────────┬───────────────────┬────────────────┬───────────┘
             │                   │                │
┌────────────┼───────────────────┼────────────────┼───────────┐
│                    DATA LAYER                              │
├────────────┼───────────────────┼────────────────┼───────────┤
│            │                   │                │           │
│  ┌─────────┴────────┐  ┌──────┴────────┐  ┌───┴────────┐  │
│  │   PostgreSQL     │  │    MongoDB    │  │   Redis    │  │
│  │   (Primary DB)   │  │   (Documents) │  │  (Cache)   │  │
│  │                  │  │               │  │            │  │
│  │  • Clients       │  │  • Logs       │  │  • Sessions│  │
│  │  • Contracts     │  │  • Events     │  │  • Queue   │  │
│  │  • Employees     │  │  • Docs       │  │  • PubSub  │  │
│  │  • Financials    │  │  • OCR Data   │  │            │  │
│  └──────────────────┘  └───────────────┘  └────────────┘  │
│                                                            │
│  ┌──────────────────┐  ┌───────────────┐  ┌────────────┐ │
│  │  Elasticsearch   │  │   S3 / Blob   │  │ Snowflake  │ │
│  │  (Full-text)     │  │   (Files)     │  │ (Warehouse)│ │
│  └──────────────────┘  └───────────────┘  └────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 3.1.2 Comunicação entre Serviços

**Padrões de Comunicação:**

1. **Síncrono (Request-Response):**
   - REST APIs (HTTP/HTTPS)
   - GraphQL (opcional, para queries complexas)
   - gRPC (para comunicação interna de baixa latência)

2. **Assíncrono (Event-Driven):**
   - Message Broker (RabbitMQ / Kafka)
   - Pub/Sub pattern
   - Event Sourcing
   - SAGA pattern para transações distribuídas

**Exemplo de Fluxo:**

```
Usuario cria contrato via Web App
            │
            ▼
    [API Gateway] autenticação, routing
            │
            ▼
    [Commercial Service] valida dados, cria contrato
            │
            ├─► Publica evento: "ContractCreated"
            │
            ▼
    [Message Broker] distribui evento
            │
            ├──► [Financial Service] cria faturamento recorrente
            ├──► [Operations Service] cria postos
            ├──► [Conecta Plus API] disponibiliza acesso ao cliente
            ├──► [Conecta Guardian API] configura equipamentos
            └──► [Notification Service] envia e-mail/WhatsApp
```

---

## 3.2 Segurança

### 3.2.1 Autenticação e Autorização

**OAuth 2.0 + JWT:**

```python
# Exemplo de implementação (FastAPI)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Configurações
SECRET_KEY = "sua-chave-secreta-super-segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Buscar usuário no banco
        user = await get_user_from_db(username)
        return user
    except JWTError:
        raise credentials_exception
```

**RBAC (Role-Based Access Control):**

```python
from enum import Enum
from typing import List

class Permission(str, Enum):
    # Comercial
    CONTRACTS_READ = "contracts:read"
    CONTRACTS_WRITE = "contracts:write"
    CONTRACTS_DELETE = "contracts:delete"
    
    # Financeiro
    FINANCIALS_READ = "financials:read"
    FINANCIALS_WRITE = "financials:write"
    FINANCIALS_APPROVE = "financials:approve"
    
    # RH
    EMPLOYEES_READ = "employees:read"
    EMPLOYEES_WRITE = "employees:write"
    PAYROLL_PROCESS = "payroll:process"
    
    # Admin
    USERS_MANAGE = "users:manage"
    SYSTEM_CONFIG = "system:config"

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [perm for perm in Permission],  # Todas
    Role.ADMIN: [
        Permission.CONTRACTS_READ,
        Permission.CONTRACTS_WRITE,
        Permission.FINANCIALS_READ,
        Permission.FINANCIALS_WRITE,
        Permission.EMPLOYEES_READ,
        Permission.EMPLOYEES_WRITE,
    ],
    Role.MANAGER: [
        Permission.CONTRACTS_READ,
        Permission.FINANCIALS_READ,
        Permission.EMPLOYEES_READ,
    ],
    Role.OPERATOR: [
        Permission.CONTRACTS_READ,
    ],
    Role.VIEWER: [
        Permission.CONTRACTS_READ,
        Permission.FINANCIALS_READ,
    ],
}

def has_permission(user_role: Role, required_permission: Permission) -> bool:
    return required_permission in ROLE_PERMISSIONS.get(user_role, [])

# Decorator para proteger rotas
from functools import wraps

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Uso
@app.post("/contracts")
@require_permission(Permission.CONTRACTS_WRITE)
async def create_contract(contract: ContractCreate, current_user: User = Depends(get_current_user)):
    # Lógica de criação de contrato
    pass
```

### 3.2.2 Criptografia

**Dados em Repouso:**
- AES-256 para dados sensíveis
- TDE (Transparent Data Encryption) no PostgreSQL
- Encryption at rest no S3

**Dados em Trânsito:**
- TLS 1.3
- Certificate pinning em apps mobile
- HSTS (HTTP Strict Transport Security)

**Dados Sensíveis:**
```python
from cryptography.fernet import Fernet
import base64
import os

class EncryptionService:
    def __init__(self):
        # Chave deve estar no AWS Secrets Manager / Vault
        self.key = os.getenv("ENCRYPTION_KEY").encode()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, plain_text: str) -> str:
        """Criptografa texto"""
        encrypted = self.cipher.encrypt(plain_text.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """Descriptografa texto"""
        encrypted = base64.b64decode(encrypted_text.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

# Uso para CPF, salários, etc
encryption_service = EncryptionService()

cpf_encrypted = encryption_service.encrypt("123.456.789-00")
# Salva no banco: cpf_encrypted

# Ao recuperar
cpf_decrypted = encryption_service.decrypt(cpf_encrypted)
```

### 3.2.3 Auditoria

**Modelo de Auditoria:**
```python
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, READ
    resource_type = Column(String(50), nullable=False)  # Contract, Employee, etc
    resource_id = Column(String(100), nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AuditLog {self.user_id} {self.action} {self.resource_type}:{self.resource_id}>"

# Service de Auditoria
class AuditService:
    @staticmethod
    async def log_action(
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str,
        old_value: dict = None,
        new_value: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent
        )
        # Salvar no banco
        await db.session.add(audit_log)
        await db.session.commit()
        
        # Enviar para Elasticsearch para busca
        await elasticsearch_client.index(
            index="audit_logs",
            document={
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Decorator para auto-auditoria
from functools import wraps
from fastapi import Request

def audit_action(resource_type: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args, 
            request: Request = None,
            current_user: User = Depends(get_current_user), 
            **kwargs
        ):
            # Executar função
            result = await func(*args, current_user=current_user, **kwargs)
            
            # Registrar auditoria
            await AuditService.log_action(
                user_id=current_user.id,
                action=action,
                resource_type=resource_type,
                resource_id=str(result.id) if hasattr(result, 'id') else "N/A",
                new_value=result.dict() if hasattr(result, 'dict') else None,
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
            
            return result
        return wrapper
    return decorator

# Uso
@app.post("/contracts")
@audit_action(resource_type="Contract", action="CREATE")
async def create_contract(contract: ContractCreate, current_user: User = Depends(get_current_user)):
    # Lógica
    pass
```

---

## 3.3 Escalabilidade e Performance

### 3.3.1 Cache Strategy

**Multi-Level Caching:**

```python
import redis
import json
from functools import wraps
from typing import Optional
import hashlib

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def cache(ttl: int = 300, prefix: str = "cache"):
    """
    Decorator para cache com Redis
    ttl: Time to live em segundos
    prefix: Prefixo da chave
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave baseada nos argumentos
            cache_key = f"{prefix}:{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Tentar buscar no cache
            cached_value = redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)
            
            # Se não está no cache, executar função
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

# Uso
@cache(ttl=600, prefix="contracts")
async def get_contract_by_id(contract_id: int):
    # Buscar no banco
    contract = await db.query(Contract).filter(Contract.id == contract_id).first()
    return contract

# Cache invalidation
async def invalidate_contract_cache(contract_id: int):
    pattern = f"contracts:get_contract_by_id:*{contract_id}*"
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)
```

**Cache Layers:**
1. **Application Cache (in-memory):** Dados frequentemente acessados
2. **Redis Cache:** Cache distribuído entre instâncias
3. **CDN:** Assets estáticos, imagens, CSS, JS

### 3.3.2 Database Optimization

**Índices:**
```sql
-- Índices para queries frequentes

-- Contratos por cliente
CREATE INDEX idx_contracts_client_id ON contracts(client_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_start_date ON contracts(start_date);
CREATE INDEX idx_contracts_end_date ON contracts(end_date);

-- Funcionários
CREATE INDEX idx_employees_cpf ON employees(cpf);
CREATE INDEX idx_employees_status ON employees(status);
CREATE INDEX idx_employees_admission_date ON employees(admission_date);

-- Ponto eletrônico
CREATE INDEX idx_time_entries_employee_id ON time_entries(employee_id);
CREATE INDEX idx_time_entries_date ON time_entries(date);
CREATE INDEX idx_time_entries_status ON time_entries(status);

-- Financeiro
CREATE INDEX idx_invoices_client_id ON invoices(client_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_payments_invoice_id ON payments(invoice_id);
CREATE INDEX idx_payments_date ON payments(payment_date);

-- Índices compostos
CREATE INDEX idx_contracts_client_status ON contracts(client_id, status);
CREATE INDEX idx_time_entries_employee_date ON time_entries(employee_id, date);
```

**Particionamento:**
```sql
-- Particionamento por data para tabelas grandes

-- Time entries (ponto eletrônico)
CREATE TABLE time_entries (
    id SERIAL,
    employee_id INT NOT NULL,
    date DATE NOT NULL,
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    -- outros campos
    PRIMARY KEY (id, date)
) PARTITION BY RANGE (date);

-- Criar partições mensais
CREATE TABLE time_entries_2024_01 PARTITION OF time_entries
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE time_entries_2024_02 PARTITION OF time_entries
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Script para criar partições automaticamente
-- (rodar mensalmente via cron)
```

**Read Replicas:**
- Master para writes
- Replicas para reads (relatórios, dashboards)
- Load balancer entre replicas

### 3.3.3 API Rate Limiting

```python
from fastapi import HTTPException, Request
from redis import Redis
import time

redis_client = Redis(host='localhost', port=6379, db=1)

class RateLimiter:
    def __init__(self, calls: int, period: int):
        """
        calls: número de chamadas permitidas
        period: período em segundos
        """
        self.calls = calls
        self.period = period
    
    async def __call__(self, request: Request):
        # Identificar usuário (por IP ou user_id)
        identifier = request.client.host
        
        key = f"rate_limit:{identifier}"
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, self.period, 1)
            return
        
        current = int(current)
        if current >= self.calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {redis_client.ttl(key)} seconds"
            )
        
        redis_client.incr(key)

# Uso
from fastapi import Depends

rate_limiter = RateLimiter(calls=100, period=60)  # 100 req/min

@app.get("/contracts", dependencies=[Depends(rate_limiter)])
async def list_contracts():
    pass
```

---

## 3.4 Resiliência e Fault Tolerance

### 3.4.1 Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"      # Normal
    OPEN = "open"          # Falhou, bloqueado
    HALF_OPEN = "half_open"  # Testando recuperação

class CircuitBreaker:
    def __init__(
        self, 
        failure_threshold: int = 5,
        timeout: int = 60,
        recovery_timeout: int = 30
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Uso para chamadas externas (APIs de banco, governo, etc)
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

async def call_external_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.externa.com/endpoint")
        return response.json()

# Com circuit breaker
try:
    result = await circuit_breaker.call(call_external_api)
except Exception as e:
    # Fallback
    result = get_cached_data()
```

### 3.4.2 Retry Pattern

```python
import asyncio
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator para retry com exponential backoff
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        return wrapper
    return decorator

# Uso
@retry(max_attempts=3, delay=1.0, exceptions=(httpx.HTTPError, TimeoutError))
async def fetch_cnd_from_government():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.governo.com/cnd", timeout=10)
        response.raise_for_status()
        return response.json()
```

### 3.4.3 Fallback e Degradação Graciosa

```python
async def get_contract_with_fallback(contract_id: int):
    try:
        # Tentar buscar no serviço primário
        contract = await commercial_service.get_contract(contract_id)
        return contract
    except Exception as e:
        logger.error(f"Primary service failed: {e}")
        
        try:
            # Fallback 1: Cache
            contract = await redis_cache.get(f"contract:{contract_id}")
            if contract:
                return contract
        except Exception as e2:
            logger.error(f"Cache fallback failed: {e2}")
        
        try:
            # Fallback 2: Read replica
            contract = await read_replica_db.query(Contract).get(contract_id)
            return contract
        except Exception as e3:
            logger.error(f"Read replica fallback failed: {e3}")
            
            # Fallback 3: Retornar dados parciais
            return {
                "id": contract_id,
                "status": "unavailable",
                "message": "Data temporarily unavailable"
            }
```

---

## 3.5 Observabilidade

### 3.5.1 Logging

**Structured Logging:**
```python
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['service'] = 'erp-conecta-mais'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')

# Configurar logger
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Uso
logger.info("Contract created", extra={
    "user_id": 123,
    "contract_id": 456,
    "client_id": 789,
    "amount": 5000.00
})

# Output JSON:
# {
#   "timestamp": "2024-12-30T10:00:00.000Z",
#   "level": "INFO",
#   "service": "erp-conecta-mais",
#   "environment": "production",
#   "message": "Contract created",
#   "user_id": 123,
#   "contract_id": 456,
#   "client_id": 789,
#   "amount": 5000.0
# }
```

**Níveis de Log:**
- **DEBUG:** Desenvolvimento, debugging detalhado
- **INFO:** Eventos importantes (criação, atualização, etc)
- **WARNING:** Situações anormais mas recuperáveis
- **ERROR:** Erros que precisam atenção
- **CRITICAL:** Falhas graves que impedem operação

### 3.5.2 Métricas (Prometheus + Grafana)

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Definir métricas
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_contracts_gauge = Gauge(
    'active_contracts',
    'Number of active contracts'
)

# Middleware para coletar métricas
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Atualizar gauge periodicamente
async def update_active_contracts_metric():
    while True:
        count = await db.query(Contract).filter(Contract.status == 'active').count()
        active_contracts_gauge.set(count)
        await asyncio.sleep(60)  # A cada minuto
```

### 3.5.3 Distributed Tracing (Jaeger / Zipkin)

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configurar tracer
resource = Resource(attributes={
    SERVICE_NAME: "erp-conecta-mais"
})

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Uso
@app.post("/contracts")
async def create_contract(contract: ContractCreate):
    with tracer.start_as_current_span("create_contract") as span:
        span.set_attribute("contract.client_id", contract.client_id)
        span.set_attribute("contract.amount", contract.amount)
        
        # Validação
        with tracer.start_as_current_span("validate_contract"):
            await validate_contract(contract)
        
        # Salvar no banco
        with tracer.start_as_current_span("save_to_database"):
            saved_contract = await db.save(contract)
        
        # Publicar evento
        with tracer.start_as_current_span("publish_event"):
            await event_bus.publish("ContractCreated", saved_contract)
        
        return saved_contract
```

---

Vou continuar criando o resto do documento. Está ficando MASSIVO! Aguarde...
