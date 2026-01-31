# 🎯 ANÁLISE COMPLETA - MÓDULO RECRUITMENT

**Data:** 28/01/2026
**Módulo:** RECRUITMENT (Recrutamento e Seleção)
**Status Atual:** ❌ 0% COBERTURA FRONTEND
**Objetivo:** IMPLEMENTAR 100% + ORVAL + REACT QUERY

---

## 📊 MAPEAMENTO DE ENDPOINTS

### Total de Endpoints: 79

#### 1️⃣ JOB POSITIONS (Vagas) - 15 endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/job-positions/` | Criar vaga |
| GET | `/api/v1/job-positions/` | Listar vagas com filtros |
| GET | `/api/v1/job-positions/open` | Listar vagas abertas |
| GET | `/api/v1/job-positions/expiring` | Vagas próximas da expiração |
| GET | `/api/v1/job-positions/stats` | Estatísticas de vagas |
| GET | `/api/v1/job-positions/{position_id}` | Buscar vaga por ID |
| GET | `/api/v1/job-positions/code/{code}` | Buscar vaga por código |
| PUT | `/api/v1/job-positions/{position_id}` | Atualizar vaga |
| DELETE | `/api/v1/job-positions/{position_id}` | Remover vaga |
| POST | `/api/v1/job-positions/{position_id}/publish` | Publicar vaga |
| POST | `/api/v1/job-positions/{position_id}/pause` | Pausar vaga |
| POST | `/api/v1/job-positions/{position_id}/reopen` | Reabrir vaga |
| POST | `/api/v1/job-positions/{position_id}/close` | Fechar vaga |
| POST | `/api/v1/job-positions/{position_id}/duplicate` | Duplicar vaga |

**Funcionalidades:**
- CRUD completo de vagas
- Workflow de status (rascunho → publicado → pausado → fechado)
- Filtros avançados (tipo, nível, departamento, modelo de trabalho)
- Estatísticas e métricas
- Sistema de código único

#### 2️⃣ CANDIDATES (Candidatos) - 23 endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/candidates/` | Criar candidato |
| POST | `/api/v1/candidates/import` | Importar de currículo (IA) |
| GET | `/api/v1/candidates/` | Listar candidatos com filtros |
| GET | `/api/v1/candidates/active` | Listar candidatos ativos |
| GET | `/api/v1/candidates/blocked` | Listar candidatos bloqueados |
| GET | `/api/v1/candidates/search-skills` | Buscar por habilidades |
| GET | `/api/v1/candidates/recently-active` | Candidatos ativos recentemente |
| GET | `/api/v1/candidates/stats` | Estatísticas de candidatos |
| GET | `/api/v1/candidates/{candidate_id}` | Buscar candidato por ID |
| GET | `/api/v1/candidates/email/{email}` | Buscar por email |
| PUT | `/api/v1/candidates/{candidate_id}` | Atualizar candidato |
| DELETE | `/api/v1/candidates/{candidate_id}` | Remover candidato |
| POST | `/api/v1/candidates/{candidate_id}/block` | Bloquear candidato |
| POST | `/api/v1/candidates/{candidate_id}/unblock` | Desbloquear candidato |
| POST | `/api/v1/candidates/{candidate_id}/archive` | Arquivar candidato |
| POST | `/api/v1/candidates/{candidate_id}/activate` | Ativar candidato |
| PUT | `/api/v1/candidates/{candidate_id}/tags` | Atualizar tags |
| POST | `/api/v1/candidates/{candidate_id}/note` | Adicionar nota |
| POST | `/api/v1/candidates/{primary_id}/merge/{secondary_id}` | Mesclar duplicados |

**Funcionalidades:**
- CRUD completo de candidatos
- Importação automática via IA (currículo)
- Busca por skills (matching)
- Sistema de bloqueio
- Tags e notas
- Merge de duplicados
- Filtros avançados (salário, localização, PCD, CNH)

#### 3️⃣ APPLICATIONS (Candidaturas) - 27 endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/applications/` | Criar candidatura |
| GET | `/api/v1/applications/` | Listar candidaturas com filtros |
| GET | `/api/v1/applications/position/{position_id}` | Candidaturas de uma vaga |
| GET | `/api/v1/applications/candidate/{candidate_id}` | Candidaturas de um candidato |
| GET | `/api/v1/applications/active` | Candidaturas ativas |
| GET | `/api/v1/applications/shortlisted/{position_id}` | Lista restrita |
| GET | `/api/v1/applications/favorites` | Candidaturas favoritas |
| GET | `/api/v1/applications/stats` | Estatísticas |
| GET | `/api/v1/applications/{application_id}` | Buscar candidatura |
| PUT | `/api/v1/applications/{application_id}` | Atualizar candidatura |
| DELETE | `/api/v1/applications/{application_id}` | Remover candidatura |
| POST | `/api/v1/applications/{application_id}/advance` | Avançar etapa |
| POST | `/api/v1/applications/{application_id}/reject` | Rejeitar candidatura |
| POST | `/api/v1/applications/{application_id}/proposal` | Enviar proposta |
| POST | `/api/v1/applications/{application_id}/accept-proposal` | Aceitar proposta |
| POST | `/api/v1/applications/{application_id}/reject-proposal` | Recusar proposta |
| POST | `/api/v1/applications/{application_id}/hire` | Contratar |
| POST | `/api/v1/applications/{application_id}/toggle-favorite` | Alternar favorito |
| POST | `/api/v1/applications/{application_id}/toggle-shortlist` | Alternar lista restrita |
| PUT | `/api/v1/applications/{application_id}/score` | Atualizar scores |
| POST | `/api/v1/applications/{application_id}/matching` | Recalcular matching |
| POST | `/api/v1/applications/position/{position_id}/update-ranking` | Atualizar ranking |
| POST | `/api/v1/applications/bulk-action` | Ação em lote |

**Funcionalidades:**
- CRUD de candidaturas
- Workflow completo (aplicação → entrevista → proposta → contratação)
- Sistema de favoritos e lista restrita
- Scores (entrevista, testes, referências)
- Matching automático (IA)
- Ranking automático
- Ações em lote

#### 4️⃣ INTERVIEWS (Entrevistas) - 24 endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/interviews/` | Agendar entrevista |
| GET | `/api/v1/interviews/` | Listar entrevistas com filtros |
| GET | `/api/v1/interviews/today` | Entrevistas de hoje |
| GET | `/api/v1/interviews/upcoming` | Próximas entrevistas |
| GET | `/api/v1/interviews/pending-confirmation` | Pendentes de confirmação |
| GET | `/api/v1/interviews/pending-result` | Pendentes de resultado |
| GET | `/api/v1/interviews/by-date-range` | Por período |
| GET | `/api/v1/interviews/available-slots` | Horários disponíveis |
| GET | `/api/v1/interviews/calendar/{interviewer_id}` | Calendário de entrevistas |
| GET | `/api/v1/interviews/stats` | Estatísticas |
| GET | `/api/v1/interviews/{interview_id}` | Buscar entrevista |
| PUT | `/api/v1/interviews/{interview_id}` | Atualizar entrevista |
| DELETE | `/api/v1/interviews/{interview_id}` | Remover entrevista |
| POST | `/api/v1/interviews/{interview_id}/confirm-candidate` | Confirmar presença candidato |
| POST | `/api/v1/interviews/{interview_id}/confirm-interviewer` | Confirmar presença entrevistador |
| POST | `/api/v1/interviews/{interview_id}/start` | Iniciar entrevista |
| POST | `/api/v1/interviews/{interview_id}/complete` | Completar entrevista |
| POST | `/api/v1/interviews/{interview_id}/cancel` | Cancelar entrevista |
| POST | `/api/v1/interviews/{interview_id}/reschedule` | Reagendar entrevista |
| POST | `/api/v1/interviews/{interview_id}/no-show` | Marcar não compareceu |
| POST | `/api/v1/interviews/{interview_id}/evaluation` | Adicionar avaliação |
| GET | `/api/v1/interviews/{interview_id}/questions` | Sugestões de perguntas (IA) |
| GET | `/api/v1/interviews/application/{application_id}` | Entrevistas de uma candidatura |

**Funcionalidades:**
- CRUD de entrevistas
- Agendamento inteligente (slots disponíveis)
- Workflow completo (agendado → confirmado → em andamento → concluído)
- Avaliações de competências
- Sistema de confirmação bidirecional
- Reagendamento
- Sugestões de perguntas via IA
- Calendário integrado

---

## 🏗️ ESTRUTURA DO BACKEND

```
backend/modules/recruitment/
├── controllers/
│   ├── job_position_controller.py      (15 endpoints)
│   ├── candidate_controller.py          (23 endpoints)
│   ├── application_controller.py        (27 endpoints)
│   └── interview_controller.py          (24 endpoints)
├── services/
│   ├── job_position_service.py
│   ├── candidate_service.py
│   ├── application_service.py
│   ├── interview_service.py
│   └── recruitment_ai_service.py        (IA para matching, parsing CV)
├── models/
│   ├── job_position.py
│   ├── candidate.py
│   ├── candidate_education.py
│   ├── candidate_experience.py
│   ├── candidate_skill.py
│   ├── application.py
│   └── interview.py
├── schemas/
│   ├── job_position.py
│   ├── candidate.py
│   ├── application.py
│   └── interview.py
└── repositories/
    ├── job_position_repository.py
    ├── candidate_repository.py
    ├── application_repository.py
    └── interview_repository.py
```

---

## 📦 SCHEMAS E TIPOS

### Job Position (Vaga)
```python
# Enums
PositionStatus: draft, published, paused, closed
PositionType: clt, pj, temporary, intern, trainee
PositionLevel: junior, mid, senior, specialist, manager, director
WorkModel: onsite, remote, hybrid
Department: admin, tech, sales, marketing, operations, hr, finance

# Schemas
JobPositionCreate
JobPositionUpdate
JobPositionResponse
JobPositionListResponse
JobPositionFilter
JobPositionStats
JobPositionPublish
```

### Candidate (Candidato)
```python
# Enums
CandidateStatus: active, archived, blocked
CandidateSource: website, linkedin, referral, internal, other

# Schemas
CandidateCreate
CandidateUpdate
CandidateResponse
CandidateListResponse
CandidateFilter
CandidateStats
CandidateBlock
CandidateImport
```

### Application (Candidatura)
```python
# Enums
ApplicationStatus: applied, screening, interview, proposal, hired, rejected

# Schemas
ApplicationCreate
ApplicationUpdate
ApplicationResponse
ApplicationListResponse
ApplicationFilter
ApplicationStats
ApplicationAdvance
ApplicationReject
ApplicationProposal
ApplicationHire
ApplicationBulkAction
```

### Interview (Entrevista)
```python
# Enums
InterviewType: phone, video, onsite, technical, hr
InterviewStatus: scheduled, confirmed, in_progress, completed, cancelled, no_show

# Schemas
InterviewCreate
InterviewUpdate
InterviewResponse
InterviewListResponse
InterviewFilter
InterviewStats
InterviewComplete
InterviewReschedule
InterviewCancel
InterviewEvaluation
InterviewSlot
InterviewCalendar
```

---

## 🎯 FUNCIONALIDADES PRINCIPAIS

### 1. Gestão de Vagas
- Publicação de vagas internas/externas
- Controle de status (rascunho → publicado → pausado → fechado)
- Código único para cada vaga
- Filtros avançados
- Estatísticas em tempo real
- Duplicação de vagas

### 2. Gestão de Candidatos
- Cadastro manual ou importação via CV (IA)
- Busca por skills (matching)
- Sistema de bloqueio/desbloqueio
- Tags e notas
- Merge de candidatos duplicados
- Histórico completo

### 3. Processo Seletivo
- Candidatura automática
- Triagem (screening)
- Entrevistas múltiplas
- Proposta de emprego
- Contratação
- Rejeição com motivo

### 4. Entrevistas
- Agendamento inteligente
- Calendário integrado
- Confirmação bidirecional
- Avaliação de competências
- Sugestões de perguntas (IA)
- Reagendamento

### 5. IA e Automação
- Parsing automático de CV
- Matching candidato x vaga
- Sugestões de perguntas
- Ranking automático
- Classificação de skills

---

## 🚨 SITUAÇÃO ATUAL

```
╔════════════════════════════════════════════════════════╗
║  MÓDULO RECRUITMENT - STATUS ATUAL                     ║
╠════════════════════════════════════════════════════════╣
║  ✅ Backend:              79 endpoints (100%)          ║
║  ❌ Frontend Service:     0% (NÃO EXISTE)              ║
║  ❌ Frontend Hooks:       0% (NÃO EXISTE)              ║
║  ❌ Frontend Componentes: 0% (NÃO EXISTE)              ║
║  ❌ Frontend Páginas:     0% (NÃO EXISTE)              ║
║  ❌ Tipos TypeScript:     0% (NÃO EXISTE)              ║
║  ❌ Testes:               0% (NÃO EXISTE)              ║
╚════════════════════════════════════════════════════════╝
```

**COBERTURA TOTAL:** ❌ **0%**

---

## 🎯 OBJETIVO

Implementar **100% de cobertura** seguindo o padrão do módulo GED:

1. ✅ Extrair OpenAPI spec do recruitment
2. ✅ Configurar Orval para geração de tipos
3. ✅ Criar service layer completo (79 métodos)
4. ✅ Criar React Query hooks
5. ✅ Criar componentes UI
6. ✅ Criar páginas do módulo
7. ✅ Documentar tudo

---

## 📋 COMPARAÇÃO COM GED

| Aspecto | GED | RECRUITMENT |
|---------|-----|-------------|
| Endpoints Backend | 138 | 79 |
| Status Frontend | ✅ 100% | ❌ 0% |
| Complexidade | Alta | Alta |
| IA Integration | Sim (classificação) | Sim (CV parsing, matching) |
| Real-time | Não | Não (mas precisa) |
| Batch Operations | Sim | Sim (bulk actions) |

**Vantagem:** Podemos usar todo o padrão do GED como referência!

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Análise completa (ESTE ARQUIVO)
2. ⏳ Criar script `extract-recruitment-spec.py`
3. ⏳ Criar `orval.config.recruitment.ts`
4. ⏳ Gerar tipos TypeScript
5. ⏳ Implementar services
6. ⏳ Implementar hooks
7. ⏳ Implementar UI
8. ⏳ Testar tudo

---

**Análise criada por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
