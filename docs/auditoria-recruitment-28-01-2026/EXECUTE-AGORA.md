# ⚡ EXECUTE AGORA - RECRUITMENT

Comandos prontos para copiar e executar.

---

## 🔴 PRÉ-REQUISITO: BACKEND ONLINE

```bash
# Iniciar backend se não estiver rodando
cd /opt/conecta-pro
docker compose up -d backend

# Aguardar backend ficar pronto (até 30s)
for i in {1..10}; do
  curl -s http://localhost:8080/health && echo "✅ Backend online!" && break
  echo "⏳ Aguardando... ($i/10)"
  sleep 3
done
```

---

## ETAPA 1: EXTRAIR OPENAPI SPEC (5min)

```bash
cd /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026

# Baixar spec completo
curl -s http://localhost:8080/openapi.json -o openapi-conecta-pro.json

# Verificar tamanho
ls -lh openapi-conecta-pro.json

# Extrair apenas recruitment
python3 extract-recruitment-spec.py

# Verificar resultado
ls -lh openapi-recruitment.json
```

**Resultado esperado:**
```
✅ Endpoints do módulo RECRUITMENT: 79
   - Job Positions: 15
   - Candidates: 23
   - Applications: 27
   - Interviews: 24
```

---

## ETAPA 2: CONFIGURAR ORVAL NO FRONTEND (10min)

```bash
cd /opt/conecta-pro/frontend

# Copiar arquivos necessários
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/openapi-recruitment.json ./
cp /opt/conecta-pro/docs/auditoria-recruitment-28-01-2026/orval.config.recruitment.ts ./

# Instalar Orval (se ainda não estiver instalado)
npm install -D orval

# Adicionar script no package.json
# ADICIONAR MANUALMENTE esta linha em "scripts":
#   "orval:recruitment": "orval --config orval.config.recruitment.ts",

# Ou via sed (Linux):
sed -i '/"scripts": {/a\    "orval:recruitment": "orval --config orval.config.recruitment.ts",' package.json
```

---

## ETAPA 3: GERAR TIPOS TYPESCRIPT (5min)

```bash
cd /opt/conecta-pro/frontend

# Gerar tipos
npm run orval:recruitment

# Verificar tipos gerados
ls -la src/types/generated/recruitment/

# Verificar se não há erros TypeScript
npm run types:check
```

**Arquivos gerados esperados:**
```
src/types/generated/recruitment/
├── recruitment-vagas.ts
├── recruitment-candidatos.ts
├── recruitment-candidaturas.ts
├── recruitment-entrevistas.ts
└── common.ts
```

---

## ETAPA 4: CRIAR SERVICE LAYER (8h)

```bash
cd /opt/conecta-pro/frontend

# Criar diretório se não existir
mkdir -p src/lib/services

# Criar arquivo do service
# (Código completo está em 02-SERVICE-RECRUITMENT.md)
```

**Estrutura do arquivo `src/lib/services/recruitment.ts`:**

```typescript
import type {
  // Job Positions
  JobPositionCreate,
  JobPositionUpdate,
  JobPositionResponse,
  JobPositionListResponse,
  JobPositionFilter,
  JobPositionStats,
  JobPositionPublish,
  // Candidates
  CandidateCreate,
  CandidateUpdate,
  CandidateResponse,
  CandidateListResponse,
  CandidateFilter,
  CandidateStats,
  CandidateBlock,
  CandidateImport,
  // Applications
  ApplicationCreate,
  ApplicationUpdate,
  ApplicationResponse,
  ApplicationListResponse,
  ApplicationFilter,
  ApplicationStats,
  ApplicationAdvance,
  ApplicationReject,
  ApplicationProposal,
  ApplicationHire,
  ApplicationBulkAction,
  // Interviews
  InterviewCreate,
  InterviewUpdate,
  InterviewResponse,
  InterviewListResponse,
  InterviewFilter,
  InterviewStats,
  InterviewComplete,
  InterviewReschedule,
  InterviewCancel,
  InterviewEvaluation,
  InterviewSlot,
  InterviewCalendar,
} from '@/types/generated/recruitment';

import { api } from '@/lib/api';

// ===================================================================
// JOB POSITIONS SERVICE (15 métodos)
// ===================================================================
export const jobPositionService = {
  // CRUD básico
  create: async (data: JobPositionCreate): Promise<JobPositionResponse> => {
    const response = await api.post('/api/v1/recruitment/job-positions/', data);
    return response.data;
  },

  list: async (filters?: JobPositionFilter): Promise<JobPositionListResponse> => {
    const response = await api.get('/api/v1/recruitment/job-positions/', { params: filters });
    return response.data;
  },

  getById: async (positionId: string): Promise<JobPositionResponse> => {
    const response = await api.get(`/api/v1/recruitment/job-positions/${positionId}`);
    return response.data;
  },

  getByCode: async (code: string): Promise<JobPositionResponse> => {
    const response = await api.get(`/api/v1/recruitment/job-positions/code/${code}`);
    return response.data;
  },

  update: async (positionId: string, data: JobPositionUpdate): Promise<JobPositionResponse> => {
    const response = await api.put(`/api/v1/recruitment/job-positions/${positionId}`, data);
    return response.data;
  },

  delete: async (positionId: string): Promise<void> => {
    await api.delete(`/api/v1/recruitment/job-positions/${positionId}`);
  },

  // Listas especiais
  listOpen: async (condominiumId?: string): Promise<JobPositionListResponse> => {
    const response = await api.get('/api/v1/recruitment/job-positions/open', {
      params: { condominium_id: condominiumId },
    });
    return response.data;
  },

  listExpiring: async (days: number = 7): Promise<JobPositionListResponse> => {
    const response = await api.get('/api/v1/recruitment/job-positions/expiring', {
      params: { days },
    });
    return response.data;
  },

  // Estatísticas
  getStats: async (condominiumId?: string): Promise<JobPositionStats> => {
    const response = await api.get('/api/v1/recruitment/job-positions/stats', {
      params: { condominium_id: condominiumId },
    });
    return response.data;
  },

  // Ações de workflow
  publish: async (positionId: string, data: JobPositionPublish): Promise<JobPositionResponse> => {
    const response = await api.post(`/api/v1/recruitment/job-positions/${positionId}/publish`, data);
    return response.data;
  },

  pause: async (positionId: string, reason?: string): Promise<JobPositionResponse> => {
    const response = await api.post(`/api/v1/recruitment/job-positions/${positionId}/pause`, { reason });
    return response.data;
  },

  reopen: async (positionId: string): Promise<JobPositionResponse> => {
    const response = await api.post(`/api/v1/recruitment/job-positions/${positionId}/reopen`);
    return response.data;
  },

  close: async (positionId: string, reason?: string): Promise<JobPositionResponse> => {
    const response = await api.post(`/api/v1/recruitment/job-positions/${positionId}/close`, { reason });
    return response.data;
  },

  duplicate: async (positionId: string): Promise<JobPositionResponse> => {
    const response = await api.post(`/api/v1/recruitment/job-positions/${positionId}/duplicate`);
    return response.data;
  },
};

// ===================================================================
// CANDIDATES SERVICE (23 métodos)
// ===================================================================
export const candidateService = {
  // CRUD básico
  create: async (data: CandidateCreate): Promise<CandidateResponse> => {
    const response = await api.post('/api/v1/recruitment/candidates/', data);
    return response.data;
  },

  importFromResume: async (data: CandidateImport): Promise<CandidateResponse> => {
    const response = await api.post('/api/v1/recruitment/candidates/import', data);
    return response.data;
  },

  list: async (filters?: CandidateFilter): Promise<CandidateListResponse> => {
    const response = await api.get('/api/v1/recruitment/candidates/', { params: filters });
    return response.data;
  },

  getById: async (candidateId: string): Promise<CandidateResponse> => {
    const response = await api.get(`/api/v1/recruitment/candidates/${candidateId}`);
    return response.data;
  },

  getByEmail: async (email: string): Promise<CandidateResponse> => {
    const response = await api.get(`/api/v1/recruitment/candidates/email/${email}`);
    return response.data;
  },

  update: async (candidateId: string, data: CandidateUpdate): Promise<CandidateResponse> => {
    const response = await api.put(`/api/v1/recruitment/candidates/${candidateId}`, data);
    return response.data;
  },

  delete: async (candidateId: string): Promise<void> => {
    await api.delete(`/api/v1/recruitment/candidates/${candidateId}`);
  },

  // Listas especiais
  listActive: async (condominiumId?: string, skip: number = 0, limit: number = 50): Promise<CandidateListResponse> => {
    const response = await api.get('/api/v1/recruitment/candidates/active', {
      params: { condominium_id: condominiumId, skip, limit },
    });
    return response.data;
  },

  listBlocked: async (skip: number = 0, limit: number = 50): Promise<CandidateListResponse> => {
    const response = await api.get('/api/v1/recruitment/candidates/blocked', {
      params: { skip, limit },
    });
    return response.data;
  },

  searchBySkills: async (skills: string[], limit: number = 50): Promise<CandidateListResponse> => {
    const response = await api.get('/api/v1/recruitment/candidates/search-skills', {
      params: { skills, limit },
    });
    return response.data;
  },

  listRecentlyActive: async (days: number = 30, limit: number = 50): Promise<CandidateListResponse> => {
    const response = await api.get('/api/v1/recruitment/candidates/recently-active', {
      params: { days, limit },
    });
    return response.data;
  },

  // Estatísticas
  getStats: async (condominiumId?: string): Promise<CandidateStats> => {
    const response = await api.get('/api/v1/recruitment/candidates/stats', {
      params: { condominium_id: condominiumId },
    });
    return response.data;
  },

  // Ações
  block: async (candidateId: string, data: CandidateBlock): Promise<CandidateResponse> => {
    const response = await api.post(`/api/v1/recruitment/candidates/${candidateId}/block`, data);
    return response.data;
  },

  unblock: async (candidateId: string): Promise<CandidateResponse> => {
    const response = await api.post(`/api/v1/recruitment/candidates/${candidateId}/unblock`);
    return response.data;
  },

  archive: async (candidateId: string): Promise<CandidateResponse> => {
    const response = await api.post(`/api/v1/recruitment/candidates/${candidateId}/archive`);
    return response.data;
  },

  activate: async (candidateId: string): Promise<CandidateResponse> => {
    const response = await api.post(`/api/v1/recruitment/candidates/${candidateId}/activate`);
    return response.data;
  },

  updateTags: async (candidateId: string, tags: string[]): Promise<CandidateResponse> => {
    const response = await api.put(`/api/v1/recruitment/candidates/${candidateId}/tags`, { tags });
    return response.data;
  },

  addNote: async (candidateId: string, note: string): Promise<CandidateResponse> => {
    const response = await api.post(`/api/v1/recruitment/candidates/${candidateId}/note`, { note });
    return response.data;
  },

  mergeDuplicates: async (primaryId: string, secondaryId: string): Promise<CandidateResponse> => {
    const response = await api.post(`/api/v1/recruitment/candidates/${primaryId}/merge/${secondaryId}`);
    return response.data;
  },
};

// ===================================================================
// APPLICATIONS SERVICE (27 métodos)
// ===================================================================
export const applicationService = {
  // CRUD básico
  create: async (data: ApplicationCreate): Promise<ApplicationResponse> => {
    const response = await api.post('/api/v1/recruitment/applications/', data);
    return response.data;
  },

  list: async (filters?: ApplicationFilter): Promise<ApplicationListResponse> => {
    const response = await api.get('/api/v1/recruitment/applications/', { params: filters });
    return response.data;
  },

  getById: async (applicationId: string): Promise<ApplicationResponse> => {
    const response = await api.get(`/api/v1/recruitment/applications/${applicationId}`);
    return response.data;
  },

  update: async (applicationId: string, data: ApplicationUpdate): Promise<ApplicationResponse> => {
    const response = await api.put(`/api/v1/recruitment/applications/${applicationId}`, data);
    return response.data;
  },

  delete: async (applicationId: string): Promise<void> => {
    await api.delete(`/api/v1/recruitment/applications/${applicationId}`);
  },

  // Listas especiais
  listByPosition: async (positionId: string, status?: string, skip: number = 0, limit: number = 50): Promise<ApplicationListResponse> => {
    const response = await api.get(`/api/v1/recruitment/applications/position/${positionId}`, {
      params: { status, skip, limit },
    });
    return response.data;
  },

  listByCandidate: async (candidateId: string, skip: number = 0, limit: number = 50): Promise<ApplicationListResponse> => {
    const response = await api.get(`/api/v1/recruitment/applications/candidate/${candidateId}`, {
      params: { skip, limit },
    });
    return response.data;
  },

  listActive: async (positionId?: string, skip: number = 0, limit: number = 50): Promise<ApplicationListResponse> => {
    const response = await api.get('/api/v1/recruitment/applications/active', {
      params: { position_id: positionId, skip, limit },
    });
    return response.data;
  },

  listShortlisted: async (positionId: string, skip: number = 0, limit: number = 50): Promise<ApplicationListResponse> => {
    const response = await api.get(`/api/v1/recruitment/applications/shortlisted/${positionId}`, {
      params: { skip, limit },
    });
    return response.data;
  },

  listFavorites: async (positionId?: string, skip: number = 0, limit: number = 50): Promise<ApplicationListResponse> => {
    const response = await api.get('/api/v1/recruitment/applications/favorites', {
      params: { position_id: positionId, skip, limit },
    });
    return response.data;
  },

  // Estatísticas
  getStats: async (positionId?: string): Promise<ApplicationStats> => {
    const response = await api.get('/api/v1/recruitment/applications/stats', {
      params: { position_id: positionId },
    });
    return response.data;
  },

  // Workflow
  advance: async (applicationId: string, data: ApplicationAdvance): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/advance`, data);
    return response.data;
  },

  reject: async (applicationId: string, data: ApplicationReject): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/reject`, data);
    return response.data;
  },

  sendProposal: async (applicationId: string, data: ApplicationProposal): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/proposal`, data);
    return response.data;
  },

  acceptProposal: async (applicationId: string, startDate?: string): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/accept-proposal`, { start_date: startDate });
    return response.data;
  },

  rejectProposal: async (applicationId: string, reason?: string): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/reject-proposal`, { reason });
    return response.data;
  },

  hire: async (applicationId: string, data: ApplicationHire): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/hire`, data);
    return response.data;
  },

  // Ações
  toggleFavorite: async (applicationId: string): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/toggle-favorite`);
    return response.data;
  },

  toggleShortlist: async (applicationId: string): Promise<ApplicationResponse> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/toggle-shortlist`);
    return response.data;
  },

  updateScore: async (applicationId: string, scores: { interview_score?: number; test_score?: number; reference_score?: number }): Promise<ApplicationResponse> => {
    const response = await api.put(`/api/v1/recruitment/applications/${applicationId}/score`, scores);
    return response.data;
  },

  recalculateMatching: async (applicationId: string): Promise<any> => {
    const response = await api.post(`/api/v1/recruitment/applications/${applicationId}/matching`);
    return response.data;
  },

  updateRanking: async (positionId: string): Promise<void> => {
    await api.post(`/api/v1/recruitment/applications/position/${positionId}/update-ranking`);
  },

  bulkAction: async (data: ApplicationBulkAction): Promise<any> => {
    const response = await api.post('/api/v1/recruitment/applications/bulk-action', data);
    return response.data;
  },
};

// ===================================================================
// INTERVIEWS SERVICE (24 métodos)
// ===================================================================
export const interviewService = {
  // CRUD básico
  create: async (data: InterviewCreate): Promise<InterviewResponse> => {
    const response = await api.post('/api/v1/recruitment/interviews/', data);
    return response.data;
  },

  list: async (filters?: InterviewFilter): Promise<InterviewListResponse> => {
    const response = await api.get('/api/v1/recruitment/interviews/', { params: filters });
    return response.data;
  },

  getById: async (interviewId: string): Promise<InterviewResponse> => {
    const response = await api.get(`/api/v1/recruitment/interviews/${interviewId}`);
    return response.data;
  },

  update: async (interviewId: string, data: InterviewUpdate): Promise<InterviewResponse> => {
    const response = await api.put(`/api/v1/recruitment/interviews/${interviewId}`, data);
    return response.data;
  },

  delete: async (interviewId: string): Promise<void> => {
    await api.delete(`/api/v1/recruitment/interviews/${interviewId}`);
  },

  // Listas especiais
  listToday: async (interviewerId?: string): Promise<InterviewListResponse> => {
    const response = await api.get('/api/v1/recruitment/interviews/today', {
      params: { interviewer_id: interviewerId },
    });
    return response.data;
  },

  listUpcoming: async (days: number = 7, interviewerId?: string): Promise<InterviewListResponse> => {
    const response = await api.get('/api/v1/recruitment/interviews/upcoming', {
      params: { days, interviewer_id: interviewerId },
    });
    return response.data;
  },

  listPendingConfirmation: async (): Promise<InterviewListResponse> => {
    const response = await api.get('/api/v1/recruitment/interviews/pending-confirmation');
    return response.data;
  },

  listPendingResult: async (): Promise<InterviewListResponse> => {
    const response = await api.get('/api/v1/recruitment/interviews/pending-result');
    return response.data;
  },

  listByDateRange: async (startDate: string, endDate: string, interviewerId?: string): Promise<InterviewListResponse> => {
    const response = await api.get('/api/v1/recruitment/interviews/by-date-range', {
      params: { start_date: startDate, end_date: endDate, interviewer_id: interviewerId },
    });
    return response.data;
  },

  listByApplication: async (applicationId: string, status?: string): Promise<InterviewListResponse> => {
    const response = await api.get(`/api/v1/recruitment/interviews/application/${applicationId}`, {
      params: { status },
    });
    return response.data;
  },

  // Agendamento
  getAvailableSlots: async (interviewerIds: string[], startDate: string, endDate: string, durationMinutes: number = 60): Promise<InterviewSlot[]> => {
    const response = await api.get('/api/v1/recruitment/interviews/available-slots', {
      params: { interviewer_ids: interviewerIds, start_date: startDate, end_date: endDate, duration_minutes: durationMinutes },
    });
    return response.data;
  },

  getCalendar: async (interviewerId: string, month: number, year: number): Promise<InterviewCalendar> => {
    const response = await api.get(`/api/v1/recruitment/interviews/calendar/${interviewerId}`, {
      params: { month, year },
    });
    return response.data;
  },

  // Estatísticas
  getStats: async (applicationId?: string): Promise<InterviewStats> => {
    const response = await api.get('/api/v1/recruitment/interviews/stats', {
      params: { application_id: applicationId },
    });
    return response.data;
  },

  // Workflow
  confirmCandidate: async (interviewId: string): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/confirm-candidate`);
    return response.data;
  },

  confirmInterviewer: async (interviewId: string): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/confirm-interviewer`);
    return response.data;
  },

  start: async (interviewId: string): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/start`);
    return response.data;
  },

  complete: async (interviewId: string, data: InterviewComplete): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/complete`, data);
    return response.data;
  },

  cancel: async (interviewId: string, data: InterviewCancel): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/cancel`, data);
    return response.data;
  },

  reschedule: async (interviewId: string, data: InterviewReschedule): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/reschedule`, data);
    return response.data;
  },

  markNoShow: async (interviewId: string): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/no-show`);
    return response.data;
  },

  addEvaluation: async (interviewId: string, data: InterviewEvaluation): Promise<InterviewResponse> => {
    const response = await api.post(`/api/v1/recruitment/interviews/${interviewId}/evaluation`, data);
    return response.data;
  },

  // IA
  getSuggestedQuestions: async (interviewId: string): Promise<any[]> => {
    const response = await api.get(`/api/v1/recruitment/interviews/${interviewId}/questions`);
    return response.data;
  },
};

// ===================================================================
// EXPORT COMPLETO
// ===================================================================
export const recruitmentService = {
  jobPositions: jobPositionService,
  candidates: candidateService,
  applications: applicationService,
  interviews: interviewService,
};
```

---

## ETAPA 5: CRIAR REACT QUERY HOOKS (4h)

```bash
cd /opt/conecta-pro/frontend
mkdir -p src/hooks/recruitment
```

Criar arquivos de hooks (ver próxima documentação)

---

## ETAPA 6: CRIAR COMPONENTES UI (6h)

```bash
cd /opt/conecta-pro/frontend
mkdir -p src/components/recruitment
```

Criar componentes principais (ver próxima documentação)

---

## ETAPA 7: CRIAR PÁGINA (3h)

```bash
cd /opt/conecta-pro/frontend
mkdir -p src/app/modulos/recrutamento
```

Criar `page.tsx` principal

---

## ETAPA 8: VALIDAR E TESTAR (4h)

```bash
cd /opt/conecta-pro/frontend

# Verificar tipos
npm run types:check

# Build
npm run build

# Testar endpoints manualmente
```

---

## ✅ VALIDAÇÃO FINAL

Checklist:
- [ ] 79 endpoints mapeados
- [ ] Tipos TypeScript gerados sem erros
- [ ] Service com 79 métodos implementados
- [ ] Hooks React Query funcionando
- [ ] Componentes UI renderizando
- [ ] Página principal acessível
- [ ] Build sem erros
- [ ] Testes manuais passando

---

**Criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
