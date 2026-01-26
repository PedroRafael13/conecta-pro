# MÓDULO 06: RECRUTAMENTO AVANÇADO (ATS com IA)

**Sprint:** 42-44
**Prioridade:** 6 (MÉDIO)
**Esforço:** 3 sprints
**Dependências:** DISC (opcional para match), GED (documentos)

---

## VISÃO GERAL

O módulo de Recrutamento é um ATS (Applicant Tracking System) completo com IA para automação de triagem, parsing de currículos e scoring de candidatos.

### Pipeline de Recrutamento

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE RECRUTAMENTO                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ATRAÇÃO          TRIAGEM           SELEÇÃO          CONTRATAÇÃO   │
│                                                                     │
│  ┌─────────┐     ┌─────────┐      ┌─────────┐      ┌─────────┐    │
│  │ Portal  │────▶│ Parser  │─────▶│ Entre-  │─────▶│ Oferta  │    │
│  │ Vagas   │     │ CV (IA) │      │ vistas  │      │         │    │
│  └─────────┘     └─────────┘      └─────────┘      └─────────┘    │
│       │               │                │                 │         │
│       ▼               ▼                ▼                 ▼         │
│  ┌─────────┐     ┌─────────┐      ┌─────────┐      ┌─────────┐    │
│  │LinkedIn │────▶│ Scoring │─────▶│ Teste   │─────▶│ Exames  │    │
│  │ Indeed  │     │ Automát.│      │ DISC    │      │ Admiss. │    │
│  └─────────┘     └─────────┘      └─────────┘      └─────────┘    │
│       │               │                │                 │         │
│       ▼               ▼                ▼                 ▼         │
│  ┌─────────┐     ┌─────────┐      ┌─────────┐      ┌─────────┐    │
│  │ Indica- │────▶│ Ranking │─────▶│ Score-  │─────▶│ Onboard-│    │
│  │ ções    │     │         │      │ card    │      │ ing     │    │
│  └─────────┘     └─────────┘      └─────────┘      └─────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Funcionalidades Principais

1. **Portal de Vagas (Careers Page)**
   - Página pública customizável
   - Listagem de vagas abertas
   - Candidatura simplificada
   - SEO otimizado

2. **Gestão de Vagas**
   - Templates de vaga por cargo
   - Requisitos e benefícios
   - Aprovações (workflow)
   - Publicação multi-canal

3. **Parser de CV com IA**
   - Upload de PDF/Word/Imagem
   - OCR para documentos escaneados
   - Extração estruturada (NER)
   - Detecção de skills

4. **Scoring Automático**
   - Match com requisitos
   - Fit cultural (DISC)
   - Red flags
   - Ranking de candidatos

5. **Pipeline Visual (Kanban)**
   - Etapas customizáveis
   - Drag & drop
   - Automações por etapa
   - SLA por etapa

6. **Entrevistas**
   - Agendamento integrado
   - Scorecards
   - Feedback estruturado
   - Video entrevistas (integração)

7. **Analytics**
   - Time-to-hire
   - Source effectiveness
   - Conversion rates
   - Cost per hire

---

## AGENTE DE IA: ResumeAgent

```python
class ResumeAgent:
    """
    Agente especializado em processamento de currículos.
    """

    def __init__(self):
        self.ocr = pytesseract
        self.ner_model = spacy.load("pt_core_news_lg")
        self.skills_matcher = SkillsMatcher()
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")

    # 1. Parse de Currículo
    async def parse_resume(
        self,
        file: UploadFile
    ) -> ParsedResume:
        """
        Extrai informações estruturadas do currículo.

        Retorna:
        {
            "dados_pessoais": {
                "nome": "João Silva",
                "email": "joao@email.com",
                "telefone": "(11) 99999-9999",
                "linkedin": "linkedin.com/in/joaosilva",
                "cidade": "São Paulo",
                "estado": "SP"
            },
            "resumo": "Profissional com 5 anos de experiência...",
            "experiencias": [
                {
                    "empresa": "Empresa X",
                    "cargo": "Desenvolvedor Senior",
                    "periodo": "2020-2024",
                    "descricao": "Desenvolvimento de sistemas...",
                    "duracao_meses": 48
                }
            ],
            "formacao": [
                {
                    "instituicao": "USP",
                    "curso": "Ciência da Computação",
                    "nivel": "Graduação",
                    "ano_conclusao": 2019
                }
            ],
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "certificacoes": ["AWS Solutions Architect"],
            "idiomas": [{"idioma": "Inglês", "nivel": "Avançado"}]
        }
        """

    # 2. Extração de Skills
    async def extract_skills(
        self,
        text: str,
        job_context: Optional[str] = None
    ) -> List[ExtractedSkill]:
        """
        Extrai skills do texto usando NER + matching.

        Categorias:
        - Técnicas (linguagens, frameworks, ferramentas)
        - Soft skills (comunicação, liderança)
        - Domínio (finanças, RH, logística)
        """

    # 3. Scoring vs Vaga
    async def score_candidate(
        self,
        resume: ParsedResume,
        job: JobPosting
    ) -> CandidateScore:
        """
        Pontua candidato vs requisitos da vaga.

        Retorna:
        {
            "score_total": 78,
            "scores": {
                "experiencia": 85,   # Anos, cargos similares
                "formacao": 70,      # Nível, área
                "skills_tecnicas": 80,
                "skills_soft": 75,
                "fit_cultural": 72   # Se DISC disponível
            },
            "matches": ["Python", "FastAPI", "5+ anos experiência"],
            "gaps": ["Kubernetes", "Inglês fluente"],
            "red_flags": [],
            "recomendacao": "ENTREVISTAR"  # REJEITAR, REVISAR, ENTREVISTAR, PRIORIZAR
        }
        """

    # 4. Detecção de Red Flags
    async def detect_red_flags(
        self,
        resume: ParsedResume
    ) -> List[RedFlag]:
        """
        Detecta possíveis problemas.

        Red flags:
        - Gaps de emprego > 6 meses sem explicação
        - Muitas trocas de emprego (< 1 ano cada)
        - Inconsistências de datas
        - Regressão de cargo
        - Informações faltantes críticas
        """

    # 5. Match com Perfil DISC
    async def match_disc_profile(
        self,
        candidate_disc: Optional[DISCProfile],
        job_disc_profile: JobDISCProfile
    ) -> DISCMatch:
        """
        Calcula fit cultural baseado em DISC.
        """

    # 6. Sugestão de Perguntas
    async def suggest_interview_questions(
        self,
        resume: ParsedResume,
        job: JobPosting,
        gaps: List[str]
    ) -> List[InterviewQuestion]:
        """
        Sugere perguntas de entrevista baseadas no perfil.
        """
```

---

## MCP SERVER: LinkedIn Jobs

```yaml
# /opt/conecta-pro/mcp/linkedin/config.yaml
name: mcp-linkedin-jobs
version: 1.0.0
description: Integração com LinkedIn Jobs API

authentication:
  type: oauth2
  scopes:
    - r_liteprofile
    - r_emailaddress
    - w_member_social
    - r_organization_social

tools:
  - name: post_job
    description: Publica vaga no LinkedIn
    parameters:
      - title: string (required)
      - description: string (required)
      - location: string (required)
      - employment_type: FULL_TIME | PART_TIME | CONTRACT
      - experience_level: ENTRY | ASSOCIATE | MID_SENIOR | DIRECTOR | EXECUTIVE
      - company_id: string (required)

  - name: get_job_applications
    description: Lista candidaturas de uma vaga
    parameters:
      - job_id: string (required)
      - status: ACTIVE | ARCHIVED

  - name: get_candidate_profile
    description: Obtém perfil público do candidato
    parameters:
      - profile_url: string (required)

  - name: search_candidates
    description: Busca candidatos por critérios
    parameters:
      - keywords: string
      - location: string
      - skills: array[string]

  - name: close_job
    description: Encerra uma vaga
    parameters:
      - job_id: string (required)

resources:
  - uri: linkedin://jobs/{job_id}
    description: Detalhes de uma vaga publicada

  - uri: linkedin://applications/{application_id}
    description: Detalhes de uma candidatura

rate_limits:
  requests_per_day: 1000
  requests_per_minute: 60
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Vagas
CREATE TABLE hr_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    requisitos TEXT,
    beneficios TEXT,
    salario_min DECIMAL(12,2),
    salario_max DECIMAL(12,2),
    mostra_salario BOOLEAN DEFAULT false,

    -- Classificação
    departamento_id UUID REFERENCES departamentos(id),
    cargo_id UUID REFERENCES cargos(id),
    nivel VARCHAR(50), -- ESTAGIO, JUNIOR, PLENO, SENIOR, ESPECIALISTA, COORDENADOR, GERENTE, DIRETOR
    tipo_contrato VARCHAR(50), -- CLT, PJ, TEMPORARIO, ESTAGIO, APRENDIZ
    regime VARCHAR(50), -- PRESENCIAL, HIBRIDO, REMOTO
    cidade VARCHAR(100),
    estado VARCHAR(2),

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    -- Status: RASCUNHO, APROVACAO, PUBLICADA, PAUSADA, ENCERRADA, CANCELADA
    publicada_em TIMESTAMP,
    encerrada_em TIMESTAMP,
    prazo_inscricao DATE,

    -- Métricas
    visualizacoes INT DEFAULT 0,
    candidaturas INT DEFAULT 0,
    entrevistas INT DEFAULT 0,
    contratacoes INT DEFAULT 0,

    -- Publicação
    publicar_portal BOOLEAN DEFAULT true,
    publicar_linkedin BOOLEAN DEFAULT false,
    publicar_indeed BOOLEAN DEFAULT false,
    linkedin_job_id VARCHAR(100),
    indeed_job_id VARCHAR(100),

    -- Perfil DISC ideal
    disc_profile_id UUID REFERENCES hr_disc_job_profiles(id),

    -- Workflow
    aprovador_id UUID REFERENCES funcionarios(id),
    aprovado_em TIMESTAMP,

    condominio_id UUID NOT NULL REFERENCES condominios(id),
    criado_por UUID REFERENCES users(id),
    responsavel_id UUID REFERENCES funcionarios(id), -- Recrutador responsável
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Requisitos da Vaga (estruturado)
CREATE TABLE hr_job_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES hr_jobs(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL, -- SKILL_TECNICA, SKILL_SOFT, FORMACAO, EXPERIENCIA, CERTIFICACAO, IDIOMA
    descricao VARCHAR(200) NOT NULL,
    obrigatorio BOOLEAN DEFAULT true,
    peso DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Etapas do Pipeline
CREATE TABLE hr_pipeline_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES hr_jobs(id) ON DELETE CASCADE, -- NULL = template global
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    ordem INT NOT NULL,
    cor VARCHAR(7) DEFAULT '#6B7280',
    is_final BOOLEAN DEFAULT false, -- Etapa final (contratado/rejeitado)
    is_rejection BOOLEAN DEFAULT false,
    sla_dias INT, -- SLA em dias para esta etapa
    automacao JSONB, -- Ações automáticas ao entrar na etapa
    condominio_id UUID REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Candidatos
CREATE TABLE hr_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(200) NOT NULL,
    telefone VARCHAR(20),
    linkedin_url VARCHAR(500),
    cidade VARCHAR(100),
    estado VARCHAR(2),

    -- Currículo parseado
    cv_original_url VARCHAR(500),
    cv_parseado JSONB, -- JSON do ParsedResume
    cv_parseado_em TIMESTAMP,

    -- Skills extraídas
    skills VARCHAR(100)[],

    -- DISC (se fez teste)
    disc_profile_id UUID REFERENCES hr_disc_profiles(id),

    -- Origem
    origem VARCHAR(50), -- PORTAL, LINKEDIN, INDEED, INDICACAO, BANCO_TALENTOS
    indicado_por UUID REFERENCES funcionarios(id),

    -- Status global
    status VARCHAR(20) DEFAULT 'ATIVO', -- ATIVO, BLACKLIST, CONTRATADO
    ultima_atividade TIMESTAMP,

    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(email, condominio_id)
);

-- Candidaturas
CREATE TABLE hr_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES hr_jobs(id),
    candidate_id UUID NOT NULL REFERENCES hr_candidates(id),
    stage_id UUID REFERENCES hr_pipeline_stages(id),

    -- Scores
    score_total DECIMAL(5,2),
    score_experiencia DECIMAL(5,2),
    score_formacao DECIMAL(5,2),
    score_skills DECIMAL(5,2),
    score_fit DECIMAL(5,2),
    scores_detalhados JSONB,

    -- Análise IA
    matches VARCHAR(200)[],
    gaps VARCHAR(200)[],
    red_flags VARCHAR(200)[],
    recomendacao VARCHAR(20), -- REJEITAR, REVISAR, ENTREVISTAR, PRIORIZAR

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'NOVA',
    -- Status: NOVA, EM_ANALISE, ENTREVISTA, TESTE, OFERTA, CONTRATADO, REJEITADO, DESISTIU

    -- Datas
    aplicado_em TIMESTAMP DEFAULT NOW(),
    movido_em TIMESTAMP, -- Última movimentação no pipeline
    rejeitado_em TIMESTAMP,
    motivo_rejeicao TEXT,
    contratado_em TIMESTAMP,

    -- Avaliação
    avaliacao_geral INT, -- 1-5
    notas_recrutador TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(job_id, candidate_id)
);

-- Entrevistas
CREATE TABLE hr_interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES hr_applications(id),
    tipo VARCHAR(50) NOT NULL, -- TRIAGEM, TECNICA, GESTOR, CULTURAL, FINAL
    formato VARCHAR(20) NOT NULL, -- PRESENCIAL, VIDEO, TELEFONE

    -- Agendamento
    data_hora TIMESTAMP NOT NULL,
    duracao_min INT DEFAULT 60,
    local VARCHAR(200),
    link_video VARCHAR(500),

    -- Participantes
    entrevistadores UUID[] NOT NULL, -- IDs de funcionários
    candidato_confirmou BOOLEAN,

    -- Status
    status VARCHAR(20) DEFAULT 'AGENDADA',
    -- Status: AGENDADA, CONFIRMADA, REALIZADA, CANCELADA, NO_SHOW

    -- Avaliação
    scorecard JSONB,
    nota_geral INT, -- 1-5
    feedback TEXT,
    recomendacao VARCHAR(50), -- APROVAR, REPROVAR, PROXIMA_ETAPA

    realizada_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Histórico de Movimentações
CREATE TABLE hr_application_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES hr_applications(id),
    stage_from UUID REFERENCES hr_pipeline_stages(id),
    stage_to UUID REFERENCES hr_pipeline_stages(id),
    acao VARCHAR(50) NOT NULL, -- CRIADA, MOVIDA, REJEITADA, CONTRATADA, NOTA_ADICIONADA
    descricao TEXT,
    usuario_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Templates de Email
CREATE TABLE hr_email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    assunto VARCHAR(200) NOT NULL,
    corpo TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- CANDIDATURA_RECEBIDA, AGENDAMENTO, REJEICAO, OFERTA, etc.
    variaveis VARCHAR(50)[], -- {{candidato_nome}}, {{vaga_titulo}}, etc.
    ativo BOOLEAN DEFAULT true,
    condominio_id UUID REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_jobs_status ON hr_jobs(status);
CREATE INDEX idx_jobs_condominio ON hr_jobs(condominio_id);
CREATE INDEX idx_candidates_email ON hr_candidates(email);
CREATE INDEX idx_candidates_skills ON hr_candidates USING GIN(skills);
CREATE INDEX idx_applications_job ON hr_applications(job_id);
CREATE INDEX idx_applications_candidate ON hr_applications(candidate_id);
CREATE INDEX idx_applications_status ON hr_applications(status);
CREATE INDEX idx_applications_score ON hr_applications(score_total DESC);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/recruitment", tags=["Recrutamento"])

# Vagas
@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(...)

@router.get("/jobs", response_model=PaginatedResponse[JobListResponse])
async def list_jobs(...)

@router.get("/jobs/{id}", response_model=JobDetailResponse)
async def get_job(...)

@router.put("/jobs/{id}")
async def update_job(...)

@router.delete("/jobs/{id}")
async def delete_job(...)

@router.post("/jobs/{id}/publish")
async def publish_job(...)

@router.post("/jobs/{id}/close")
async def close_job(...)

# Portal Público
@router.get("/careers", response_model=List[PublicJobResponse])
async def list_public_jobs(...)  # Sem auth

@router.get("/careers/{job_id}", response_model=PublicJobDetailResponse)
async def get_public_job(...)

@router.post("/careers/{job_id}/apply")
async def apply_to_job(...)  # Candidatura pública

# Candidatos
@router.get("/candidates", response_model=PaginatedResponse[CandidateListResponse])
async def list_candidates(...)

@router.get("/candidates/{id}", response_model=CandidateDetailResponse)
async def get_candidate(...)

@router.post("/candidates/{id}/parse-cv")
async def parse_candidate_cv(...)

@router.post("/candidates/upload-cv")
async def upload_and_parse_cv(...)

# Candidaturas
@router.get("/jobs/{job_id}/applications")
async def list_applications(...)

@router.get("/applications/{id}")
async def get_application(...)

@router.post("/applications/{id}/move")
async def move_application(...)  # Move no pipeline

@router.post("/applications/{id}/reject")
async def reject_application(...)

@router.post("/applications/{id}/hire")
async def hire_candidate(...)

@router.post("/applications/{id}/score")
async def score_application(...)  # Recalcula score

# Pipeline
@router.get("/jobs/{job_id}/pipeline")
async def get_pipeline_view(...)  # Kanban

@router.put("/jobs/{job_id}/stages")
async def update_stages(...)

# Entrevistas
@router.post("/applications/{id}/interviews")
async def schedule_interview(...)

@router.get("/applications/{id}/interviews")
async def list_interviews(...)

@router.put("/interviews/{id}")
async def update_interview(...)

@router.post("/interviews/{id}/feedback")
async def submit_interview_feedback(...)

# IA
@router.post("/jobs/{job_id}/rank-candidates")
async def rank_candidates(...)  # Ranking por IA

@router.post("/applications/{id}/suggest-questions")
async def suggest_questions(...)

# Analytics
@router.get("/analytics/overview")
async def get_recruitment_analytics(...)

@router.get("/analytics/jobs/{job_id}")
async def get_job_analytics(...)

@router.get("/analytics/sources")
async def get_source_analytics(...)

# LinkedIn Integration
@router.post("/jobs/{id}/publish-linkedin")
async def publish_to_linkedin(...)

@router.post("/jobs/{id}/sync-linkedin")
async def sync_linkedin_applications(...)
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard Recrutamento** (`/rh/recrutamento`)
   - Vagas ativas
   - Pipeline geral
   - Métricas principais

2. **Criar Vaga** (`/rh/recrutamento/vagas/nova`)
   - Formulário completo
   - Requisitos estruturados
   - Perfil DISC ideal

3. **Vaga Detalhes** (`/rh/recrutamento/vagas/{id}`)
   - Pipeline Kanban
   - Candidatos
   - Métricas

4. **Pipeline Kanban** (`/rh/recrutamento/vagas/{id}/pipeline`)
   - Drag & drop
   - Filtros
   - Bulk actions

5. **Candidato** (`/rh/recrutamento/candidatos/{id}`)
   - Perfil completo
   - CV parseado
   - Histórico de candidaturas

6. **Entrevista** (`/rh/recrutamento/entrevistas/{id}`)
   - Detalhes
   - Scorecard
   - Feedback

7. **Portal de Vagas** (`/carreiras`)
   - Página pública
   - Listagem de vagas
   - Formulário de candidatura

8. **Analytics** (`/rh/recrutamento/analytics`)
   - Dashboards
   - Funil de conversão
   - Time-to-hire

### Componentes React

```typescript
// components/recrutamento/
├── JobForm.tsx            // Formulário de vaga
├── RequirementsList.tsx   // Lista de requisitos
├── PipelineKanban.tsx     // Kanban de candidatos
├── CandidateCard.tsx      // Card do candidato
├── ApplicationDetail.tsx  // Detalhes da candidatura
├── CVViewer.tsx           // Visualizador de CV parseado
├── ScoreGauge.tsx         // Gauge de score
├── InterviewScheduler.tsx // Agendador de entrevista
├── Scorecard.tsx          // Scorecard de entrevista
├── RecruitmentMetrics.tsx // Métricas
├── SourceChart.tsx        // Gráfico de origens
├── FunnelChart.tsx        // Funil de conversão
└── CareersPage.tsx        // Portal público
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-recruit
description: Gerencia recrutamento e seleção com IA
version: 1.0.0

triggers:
  - "criar vaga"
  - "processar curriculo"
  - "ranquear candidatos"
  - "agendar entrevista"

prompts:
  create_job:
    description: Cria nova vaga
    template: |
      Crie vaga de emprego:
      1. Defina título e descrição atraentes
      2. Liste requisitos obrigatórios vs desejáveis
      3. Defina perfil DISC ideal
      4. Configure pipeline de etapas
      5. Estime salário baseado em mercado

  parse_resume:
    description: Processa currículo
    parameters:
      - file_path: Caminho do arquivo
    template: |
      Processe o currículo:
      1. Extraia dados estruturados
      2. Identifique skills técnicas e soft
      3. Calcule tempo total de experiência
      4. Detecte red flags
      5. Pontue vs vaga (se especificada)

  rank_candidates:
    description: Ranqueia candidatos
    parameters:
      - job_id: UUID da vaga
    template: |
      Ranqueie candidatos da vaga {job_id}:
      1. Calcule score de cada candidato
      2. Ordene por score total
      3. Destaque top 10
      4. Liste matches e gaps de cada um
      5. Recomende próximas ações

  suggest_questions:
    description: Sugere perguntas de entrevista
    parameters:
      - application_id: UUID da candidatura
    template: |
      Sugira perguntas para entrevista:
      1. Analise CV do candidato
      2. Identifique gaps vs vaga
      3. Sugira perguntas técnicas
      4. Sugira perguntas comportamentais
      5. Sugira perguntas sobre gaps específicos

agents:
  - ResumeAgent
  - DISCAgent

mcps:
  - mcp-linkedin-jobs
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models: jobs, candidates, applications, interviews
  - [ ] ResumeAgent (parser, scoring)
  - [ ] Controllers
  - [ ] MCP LinkedIn
  - [ ] Email templates

- [ ] **Frontend**
  - [ ] Dashboard
  - [ ] Pipeline Kanban
  - [ ] Formulário de vaga
  - [ ] Visualizador de CV
  - [ ] Portal de carreiras
  - [ ] Scorecard

- [ ] **Integrações**
  - [ ] LinkedIn Jobs API
  - [ ] Indeed (futuro)
  - [ ] DISC (match)
  - [ ] Email (notificações)
  - [ ] Onboarding

- [ ] **Testes**
  - [ ] Parser de CV
  - [ ] Scoring
  - [ ] Pipeline

---

**Próximo módulo:** [MÓDULO 07: SUCESSÃO](./MODULO_07_SUCESSAO.md)
