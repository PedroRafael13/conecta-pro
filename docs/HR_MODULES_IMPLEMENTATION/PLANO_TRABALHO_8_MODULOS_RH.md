# PLANO DE TRABALHO: 8 MÓDULOS DE RH AVANÇADO

**Data:** 23/01/2026
**Projeto:** Conecta PRO - Domínio Total RH
**Estimativa Total:** 12-14 Sprints (6-7 meses)

---

## VISÃO GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CONECTA PRO - RH AVANÇADO                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │  CLIMA  │  │  DISC   │  │  360°   │  │NINE BOX │  │   PDI   │  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │
│       │            │            │            │            │        │
│  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐  │
│  │SUCESSÃO │  │RECRUTA- │  │ONBOARD- │  │  METAS  │  │TRILHAS  │  │
│  │         │  │ MENTO   │  │  ING    │  │  OKRs   │  │CARREIRA │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                        CAMADA DE IA                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │
│  │ Agent Clima   │  │ Agent DISC    │  │ Agent Talents │           │
│  │ (Sentimento)  │  │ (Comportam.)  │  │ (Predição)    │           │
│  └───────────────┘  └───────────────┘  └───────────────┘           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │
│  │ Agent Resume  │  │ Agent Coach   │  │ Agent Survey  │           │
│  │ (Parser CV)   │  │ (PDI/Feedback)│  │ (Questionário)│           │
│  └───────────────┘  └───────────────┘  └───────────────┘           │
├─────────────────────────────────────────────────────────────────────┤
│                        MCP SERVERS                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐           │
│  │ MCP LinkedIn  │  │ MCP Psychology│  │ MCP Analytics │           │
│  │ (Jobs API)    │  │ (DISC/Big5)   │  │ (Dashboards)  │           │
│  └───────────────┘  └───────────────┘  └───────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## CRONOGRAMA POR SPRINT

### FASE 1: FUNDAÇÃO (Sprints 34-37)

#### Sprint 34-35: MÓDULO CLIMA
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: surveys, questions, responses, analytics | 3 dias |
| Backend API | CRUD + distribuição + coleta | 3 dias |
| Agent Clima IA | Análise de sentimento NLP | 3 dias |
| Frontend Builder | Drag & drop de questionários | 4 dias |
| Frontend Dashboard | Visualização de resultados | 3 dias |
| MCP Analytics | Dashboards em tempo real | 2 dias |
| Testes E2E | Cobertura completa | 2 dias |

#### Sprint 36-37: MÓDULO DISC
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: assessments, profiles, results | 3 dias |
| Questionário DISC | 48 perguntas validadas | 2 dias |
| Algoritmo DISC | Cálculo D-I-S-C com nuances | 3 dias |
| Agent DISC IA | Interpretação de perfil | 3 dias |
| Frontend Teste | Interface de aplicação | 3 dias |
| Frontend Perfil | Dashboard do colaborador | 3 dias |
| Gerador PDF | Relatório comportamental | 2 dias |
| MCP Psychology | Metodologia e validação | 1 dia |

---

### FASE 2: DESEMPENHO (Sprints 38-41)

#### Sprint 38-39: AVALIAÇÃO 360°
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: cycles, evaluations, evaluators, responses | 4 dias |
| Engine Workflow | Máquina de estados para ciclo | 3 dias |
| Backend API | CRUD + distribuição + calibração | 4 dias |
| Agent 360 IA | Sugestões de feedback, detecção de viés | 3 dias |
| Frontend Ciclos | Configurador de ciclos | 3 dias |
| Frontend Avaliação | Interface de preenchimento | 4 dias |
| Frontend Dashboard | Resultados e comparativos | 3 dias |
| Notificações | Lembretes automáticos | 2 dias |

#### Sprint 40: NINE BOX
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: ninebox_snapshots, positions | 2 dias |
| Algoritmo Nine Box | Cálculo automático P×D | 2 dias |
| Backend API | CRUD + histórico + tendências | 2 dias |
| Frontend Matriz | Visualização interativa drag & drop | 4 dias |
| Frontend Histórico | Evolução ao longo do tempo | 2 dias |
| Integração 360° | Alimentação automática | 2 dias |

#### Sprint 41: PDI
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: pdis, goals, actions, checkins | 3 dias |
| Backend API | CRUD + tracking + alertas | 3 dias |
| Agent Coach IA | Sugestões de metas SMART | 3 dias |
| Frontend PDI | Criação e acompanhamento | 4 dias |
| Frontend Checkins | Micro check-ins periódicos | 2 dias |
| Integração 360° | Gap de competências → PDI | 2 dias |
| Catálogo Ações | Cursos, mentorias, experiências | 1 dia |

---

### FASE 3: RECRUTAMENTO (Sprints 42-44)

#### Sprint 42-43: RECRUTAMENTO AVANÇADO
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: jobs, applications, pipeline_stages, scorecards | 4 dias |
| Backend API | CRUD + pipeline + scoring | 4 dias |
| Agent Resume IA | Parser de CV com NLP | 4 dias |
| MCP LinkedIn | Integração Jobs API | 3 dias |
| Frontend Portal | Careers page pública | 3 dias |
| Frontend Pipeline | Kanban de candidatos | 4 dias |
| Frontend Scoring | Comparativo de candidatos | 2 dias |
| Email Automation | Templates e sequências | 2 dias |

#### Sprint 44: INTEGRAÇÃO DISC + RECRUTAMENTO
| Task | Descrição | Esforço |
|------|-----------|---------|
| Aplicação DISC em R&S | Candidatos fazem teste | 2 dias |
| Matching Perfil-Vaga | IA compara perfil vs requisitos | 3 dias |
| Ranking Inteligente | Ordenação por fit | 2 dias |
| Frontend Comparativo | Visualização de fit | 3 dias |

---

### FASE 4: TALENTOS (Sprints 45-47)

#### Sprint 45: SUCESSÃO
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: key_positions, successors, readiness | 3 dias |
| Backend API | CRUD + mapeamento + alertas | 3 dias |
| Agent Talents IA | Predição de risco de saída | 3 dias |
| Frontend Mapa | Organograma com sucessores | 4 dias |
| Frontend Readiness | Prontidão e gaps | 3 dias |
| Integração Nine Box | Alimentação automática | 2 dias |

#### Sprint 46-47: ONBOARDING ESTRUTURADO
| Task | Descrição | Esforço |
|------|-----------|---------|
| Backend Schema | Tabelas: onboardings, checklists, tasks, surveys | 3 dias |
| Backend API | CRUD + automação + tracking | 3 dias |
| Agent Survey IA | Análise de experiência | 2 dias |
| Frontend Portal | Portal do novo colaborador | 5 dias |
| Frontend Checklists | Interativo com progresso | 3 dias |
| Assinatura Digital | Integração DocuSign ou nativa | 3 dias |
| Pesquisas 30/60/90 | Automação de envio e análise | 2 dias |
| Buddy System | Atribuição de mentores | 1 dia |

---

## AGENTES DE IA DETALHADOS

### 1. AGENT CLIMA (Sentimento)

```python
# /opt/conecta-pro/backend/modules/hr_ai/agents/clima_agent.py

class ClimaAgent:
    """
    Agente de IA para análise de clima organizacional.

    Capabilities:
    - Análise de sentimento em respostas abertas
    - Detecção de temas recorrentes (topic modeling)
    - Identificação de departamentos críticos
    - Geração de planos de ação
    - Comparativo histórico
    """

    def __init__(self):
        self.sentiment_model = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        self.topic_model = "BERTopic"
        self.embeddings = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

    async def analyze_survey(self, responses: List[SurveyResponse]) -> ClimaAnalysis:
        """Analisa todas as respostas de uma pesquisa."""
        pass

    async def detect_critical_areas(self, analysis: ClimaAnalysis) -> List[CriticalArea]:
        """Identifica áreas que precisam de atenção imediata."""
        pass

    async def generate_action_plan(self, critical_areas: List[CriticalArea]) -> ActionPlan:
        """Gera plano de ação baseado nos problemas identificados."""
        pass

    async def compare_with_benchmark(self, analysis: ClimaAnalysis) -> BenchmarkComparison:
        """Compara resultados com benchmark do mercado."""
        pass
```

### 2. AGENT DISC (Comportamental)

```python
# /opt/conecta-pro/backend/modules/hr_ai/agents/disc_agent.py

class DISCAgent:
    """
    Agente de IA para análise comportamental DISC.

    Capabilities:
    - Cálculo de perfil DISC
    - Interpretação de nuances (intensidade, adaptação)
    - Compatibilidade perfil-cargo
    - Compatibilidade de equipe
    - Geração de relatório personalizado
    """

    def __init__(self):
        self.disc_weights = self._load_validated_weights()
        self.interpretation_model = "gpt-4-turbo"  # ou modelo local

    async def calculate_profile(self, responses: List[DISCResponse]) -> DISCProfile:
        """Calcula perfil DISC a partir das respostas."""
        pass

    async def interpret_profile(self, profile: DISCProfile) -> DISCInterpretation:
        """Gera interpretação detalhada do perfil."""
        pass

    async def match_job_profile(
        self,
        candidate_profile: DISCProfile,
        job_profile: JobDISCProfile
    ) -> ProfileMatch:
        """Calcula compatibilidade entre candidato e vaga."""
        pass

    async def team_dynamics(self, team_profiles: List[DISCProfile]) -> TeamDynamics:
        """Analisa dinâmica da equipe e sugere melhorias."""
        pass
```

### 3. AGENT TALENTS (Predição)

```python
# /opt/conecta-pro/backend/modules/hr_ai/agents/talents_agent.py

class TalentsAgent:
    """
    Agente de IA para gestão de talentos.

    Capabilities:
    - Predição de turnover
    - Identificação de high potentials
    - Sugestões de desenvolvimento
    - Alertas de risco
    - Recomendações de retenção
    """

    def __init__(self):
        self.turnover_model = self._load_turnover_model()
        self.potential_model = self._load_potential_model()

    async def predict_turnover_risk(self, employee: Employee) -> TurnoverRisk:
        """Prediz risco de saída de um funcionário."""
        features = self._extract_features(employee)
        return self.turnover_model.predict(features)

    async def identify_high_potentials(
        self,
        employees: List[Employee]
    ) -> List[HighPotential]:
        """Identifica funcionários de alto potencial."""
        pass

    async def suggest_retention_actions(
        self,
        at_risk_employees: List[Employee]
    ) -> List[RetentionAction]:
        """Sugere ações de retenção personalizadas."""
        pass

    async def calculate_nine_box(
        self,
        performance: float,
        potential: float
    ) -> NineBoxPosition:
        """Calcula posição no Nine Box."""
        pass
```

### 4. AGENT RESUME (Parser CV)

```python
# /opt/conecta-pro/backend/modules/hr_ai/agents/resume_agent.py

class ResumeAgent:
    """
    Agente de IA para processamento de currículos.

    Capabilities:
    - OCR de PDFs e imagens
    - Extração estruturada (nome, contato, experiência, formação)
    - NER para skills e tecnologias
    - Scoring vs requisitos da vaga
    - Detecção de red flags
    """

    def __init__(self):
        self.ocr_engine = "pytesseract"
        self.ner_model = "spacy/pt_core_news_lg"
        self.skills_db = self._load_skills_database()

    async def parse_resume(self, file: UploadFile) -> ParsedResume:
        """Extrai informações estruturadas do currículo."""
        pass

    async def extract_skills(self, text: str) -> List[Skill]:
        """Extrai skills do texto do currículo."""
        pass

    async def score_candidate(
        self,
        resume: ParsedResume,
        job: JobPosting
    ) -> CandidateScore:
        """Pontua candidato vs requisitos da vaga."""
        pass

    async def detect_red_flags(self, resume: ParsedResume) -> List[RedFlag]:
        """Detecta possíveis problemas (gaps, inconsistências)."""
        pass
```

### 5. AGENT COACH (PDI/Feedback)

```python
# /opt/conecta-pro/backend/modules/hr_ai/agents/coach_agent.py

class CoachAgent:
    """
    Agente de IA para coaching e desenvolvimento.

    Capabilities:
    - Sugestão de metas SMART
    - Feedback construtivo
    - Recomendação de ações de desenvolvimento
    - Acompanhamento de progresso
    - Motivação personalizada
    """

    def __init__(self):
        self.llm = "gpt-4-turbo"  # ou Claude
        self.courses_db = self._load_courses_database()

    async def suggest_smart_goals(
        self,
        gaps: List[CompetencyGap]
    ) -> List[SMARTGoal]:
        """Sugere metas SMART baseadas nos gaps."""
        pass

    async def improve_feedback(self, raw_feedback: str) -> ImprovedFeedback:
        """Melhora feedback para ser mais construtivo."""
        pass

    async def recommend_development(
        self,
        goals: List[SMARTGoal]
    ) -> List[DevelopmentAction]:
        """Recomenda ações de desenvolvimento."""
        pass

    async def generate_motivation_message(
        self,
        employee: Employee,
        progress: PDIProgress
    ) -> MotivationMessage:
        """Gera mensagem motivacional personalizada."""
        pass
```

### 6. AGENT SURVEY (Questionários)

```python
# /opt/conecta-pro/backend/modules/hr_ai/agents/survey_agent.py

class SurveyAgent:
    """
    Agente de IA para questionários inteligentes.

    Capabilities:
    - Geração de perguntas relevantes
    - Adaptação dinâmica baseada em respostas
    - Validação de qualidade de respostas
    - Detecção de padrões suspeitos
    - Sugestão de melhorias no questionário
    """

    def __init__(self):
        self.question_generator = "gpt-4-turbo"
        self.pattern_detector = self._load_pattern_model()

    async def generate_questions(
        self,
        topic: str,
        context: SurveyContext
    ) -> List[Question]:
        """Gera perguntas relevantes para o tema."""
        pass

    async def adapt_next_question(
        self,
        responses: List[Response]
    ) -> Question:
        """Adapta próxima pergunta baseada nas respostas."""
        pass

    async def validate_response_quality(
        self,
        response: Response
    ) -> ResponseQuality:
        """Valida qualidade da resposta."""
        pass

    async def detect_suspicious_patterns(
        self,
        responses: List[Response]
    ) -> List[SuspiciousPattern]:
        """Detecta padrões suspeitos (straight-lining, etc.)."""
        pass
```

---

## MCP SERVERS

### 1. MCP LinkedIn

```yaml
# /opt/conecta-pro/mcp/linkedin/config.yaml
name: mcp-linkedin
version: 1.0.0
description: Integração com LinkedIn Jobs API

tools:
  - name: search_jobs
    description: Busca vagas publicadas
    parameters:
      - keywords: string
      - location: string
      - experience_level: enum

  - name: post_job
    description: Publica vaga no LinkedIn
    parameters:
      - job: JobPosting

  - name: get_applications
    description: Lista candidaturas recebidas
    parameters:
      - job_id: string

  - name: get_candidate_profile
    description: Obtém perfil público do candidato
    parameters:
      - linkedin_url: string

resources:
  - uri: linkedin://jobs/{job_id}
    description: Detalhes de uma vaga

  - uri: linkedin://candidates/{candidate_id}
    description: Perfil de candidato
```

### 2. MCP Psychology

```yaml
# /opt/conecta-pro/mcp/psychology/config.yaml
name: mcp-psychology
version: 1.0.0
description: Metodologias de psicologia organizacional

tools:
  - name: get_disc_methodology
    description: Retorna metodologia DISC validada

  - name: get_big5_methodology
    description: Retorna metodologia Big Five

  - name: validate_assessment
    description: Valida instrumento de avaliação
    parameters:
      - instrument: AssessmentInstrument

  - name: calculate_reliability
    description: Calcula confiabilidade do instrumento
    parameters:
      - responses: List[Response]

resources:
  - uri: psychology://disc/interpretation
    description: Guia de interpretação DISC

  - uri: psychology://competencies
    description: Dicionário de competências
```

### 3. MCP Analytics

```yaml
# /opt/conecta-pro/mcp/analytics/config.yaml
name: mcp-analytics
version: 1.0.0
description: Analytics e dashboards em tempo real

tools:
  - name: create_dashboard
    description: Cria dashboard customizado
    parameters:
      - widgets: List[Widget]
      - filters: List[Filter]

  - name: run_analysis
    description: Executa análise estatística
    parameters:
      - data: Dataset
      - analysis_type: enum

  - name: generate_report
    description: Gera relatório em PDF
    parameters:
      - template: ReportTemplate
      - data: Dataset

resources:
  - uri: analytics://dashboards/{dashboard_id}
    description: Dashboard salvo

  - uri: analytics://reports/{report_id}
    description: Relatório gerado
```

---

## SKILLS DO CLAUDE CODE

### 1. Skill: hr-clima

```yaml
# /root/.claude/skills/hr-clima.yaml
name: hr-clima
description: Cria e analisa pesquisa de clima organizacional
version: 1.0.0

prompts:
  create:
    description: Cria nova pesquisa de clima
    template: |
      Crie uma pesquisa de clima organizacional com:
      - Perguntas de escala Likert (1-5)
      - Perguntas abertas para comentários
      - Categorias: Liderança, Ambiente, Carreira, Comunicação
      - ENPS (Employee Net Promoter Score)

  analyze:
    description: Analisa resultados da pesquisa
    template: |
      Analise os resultados da pesquisa de clima:
      1. Calcule médias por categoria
      2. Identifique pontos críticos (< 3.0)
      3. Extraia temas das respostas abertas
      4. Compare com pesquisa anterior
      5. Sugira plano de ação

tools:
  - SurveyAgent.create_survey
  - ClimaAgent.analyze_survey
  - ClimaAgent.generate_action_plan
```

### 2. Skill: hr-disc

```yaml
# /root/.claude/skills/hr-disc.yaml
name: hr-disc
description: Aplica e interpreta avaliação DISC
version: 1.0.0

prompts:
  apply:
    description: Aplica teste DISC
    template: |
      Aplique o teste DISC para o funcionário:
      1. Apresente as 48 perguntas
      2. Colete respostas
      3. Calcule perfil D-I-S-C
      4. Gere interpretação
      5. Crie relatório PDF

  match:
    description: Avalia compatibilidade com cargo
    template: |
      Avalie a compatibilidade:
      1. Carregue perfil DISC do funcionário
      2. Carregue perfil ideal do cargo
      3. Calcule fit (0-100%)
      4. Identifique gaps
      5. Sugira desenvolvimento

tools:
  - DISCAgent.calculate_profile
  - DISCAgent.interpret_profile
  - DISCAgent.match_job_profile
```

### 3. Skill: hr-360

```yaml
# /root/.claude/skills/hr-360.yaml
name: hr-360
description: Gerencia ciclos de avaliação 360°
version: 1.0.0

prompts:
  create_cycle:
    description: Cria novo ciclo de avaliação
    template: |
      Crie ciclo de avaliação 360°:
      1. Defina período (início/fim)
      2. Selecione competências por cargo
      3. Configure avaliadores (gestor, pares, subordinados)
      4. Defina pesos
      5. Configure lembretes

  calibrate:
    description: Calibra notas do ciclo
    template: |
      Execute calibração:
      1. Identifique outliers
      2. Normalize por avaliador
      3. Compare com histórico
      4. Sugira ajustes
      5. Gere relatório de calibração

tools:
  - WorkflowEngine.create_evaluation_cycle
  - Agent360.detect_bias
  - Agent360.normalize_scores
```

### 4. Skill: hr-recruit

```yaml
# /root/.claude/skills/hr-recruit.yaml
name: hr-recruit
description: Gerencia processo seletivo com IA
version: 1.0.0

prompts:
  parse_cv:
    description: Processa currículo
    template: |
      Processe o currículo:
      1. Extraia dados estruturados
      2. Identifique skills
      3. Pontue vs requisitos da vaga
      4. Detecte red flags
      5. Recomende próxima etapa

  rank_candidates:
    description: Ranqueia candidatos
    template: |
      Ranqueie os candidatos:
      1. Calcule score técnico
      2. Calcule fit cultural (DISC)
      3. Combine scores com pesos
      4. Ordene por fit geral
      5. Destaque top 5

tools:
  - ResumeAgent.parse_resume
  - ResumeAgent.score_candidate
  - DISCAgent.match_job_profile
```

---

## ESTRUTURA DE ARQUIVOS

```
/opt/conecta-pro/
├── backend/
│   └── modules/
│       └── hr_advanced/
│           ├── __init__.py
│           ├── clima/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   ├── controllers.py
│           │   └── repositories.py
│           ├── disc/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   ├── controllers.py
│           │   ├── algorithm.py
│           │   └── questionnaire.py
│           ├── evaluation_360/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   ├── controllers.py
│           │   └── workflow.py
│           ├── nine_box/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   └── controllers.py
│           ├── pdi/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   └── controllers.py
│           ├── succession/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   └── controllers.py
│           ├── recruitment/
│           │   ├── models.py
│           │   ├── schemas.py
│           │   ├── services.py
│           │   ├── controllers.py
│           │   ├── parser.py
│           │   └── scoring.py
│           └── onboarding/
│               ├── models.py
│               ├── schemas.py
│               ├── services.py
│               └── controllers.py
│
├── backend/modules/hr_ai/
│   ├── agents/
│   │   ├── clima_agent.py
│   │   ├── disc_agent.py
│   │   ├── talents_agent.py
│   │   ├── resume_agent.py
│   │   ├── coach_agent.py
│   │   └── survey_agent.py
│   ├── models/
│   │   ├── sentiment_model.py
│   │   ├── turnover_model.py
│   │   └── skills_extractor.py
│   └── prompts/
│       ├── clima_prompts.py
│       ├── feedback_prompts.py
│       └── coaching_prompts.py
│
├── mcp/
│   ├── linkedin/
│   │   ├── config.yaml
│   │   ├── server.py
│   │   └── client.py
│   ├── psychology/
│   │   ├── config.yaml
│   │   ├── disc_methodology.py
│   │   └── competencies.py
│   └── analytics/
│       ├── config.yaml
│       ├── dashboard_builder.py
│       └── report_generator.py
│
└── frontend/src/
    └── app/modulos/
        └── rh_avancado/
            ├── clima/
            │   ├── page.tsx
            │   ├── builder/page.tsx
            │   └── results/[id]/page.tsx
            ├── disc/
            │   ├── page.tsx
            │   ├── test/page.tsx
            │   └── profile/[id]/page.tsx
            ├── avaliacao-360/
            │   ├── page.tsx
            │   ├── ciclos/page.tsx
            │   └── avaliar/[id]/page.tsx
            ├── nine-box/
            │   └── page.tsx
            ├── pdi/
            │   ├── page.tsx
            │   └── [id]/page.tsx
            ├── sucessao/
            │   └── page.tsx
            ├── recrutamento/
            │   ├── page.tsx
            │   ├── vagas/page.tsx
            │   └── candidatos/page.tsx
            └── onboarding/
                ├── page.tsx
                └── portal/page.tsx
```

---

## BANCO DE DADOS - NOVOS SCHEMAS

### Clima

```sql
-- Pesquisas de Clima
CREATE TABLE climate_surveys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL DEFAULT 'GERAL',
    status VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    data_inicio TIMESTAMP,
    data_fim TIMESTAMP,
    anonimo BOOLEAN DEFAULT true,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE climate_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES climate_surveys(id),
    categoria VARCHAR(50) NOT NULL,
    texto TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL, -- LIKERT, ABERTA, MULTIPLA
    ordem INT NOT NULL,
    obrigatoria BOOLEAN DEFAULT true,
    opcoes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE climate_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES climate_surveys(id),
    question_id UUID NOT NULL REFERENCES climate_questions(id),
    funcionario_id UUID REFERENCES funcionarios(id), -- null se anônimo
    resposta_valor INT,
    resposta_texto TEXT,
    respondido_em TIMESTAMP DEFAULT NOW()
);
```

### DISC

```sql
-- Avaliações DISC
CREATE TABLE disc_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    iniciado_em TIMESTAMP,
    concluido_em TIMESTAMP,
    versao INT DEFAULT 1,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE disc_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES disc_assessments(id),
    questao_numero INT NOT NULL,
    resposta_mais VARCHAR(1) NOT NULL, -- D, I, S, C
    resposta_menos VARCHAR(1) NOT NULL,
    tempo_resposta_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE disc_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES disc_assessments(id),
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    dominancia DECIMAL(5,2) NOT NULL,
    influencia DECIMAL(5,2) NOT NULL,
    estabilidade DECIMAL(5,2) NOT NULL,
    conformidade DECIMAL(5,2) NOT NULL,
    perfil_natural VARCHAR(10) NOT NULL, -- DI, IS, SC, CD, etc.
    perfil_adaptado VARCHAR(10),
    intensidade VARCHAR(20), -- BAIXA, MEDIA, ALTA
    interpretacao JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Avaliação 360°

```sql
-- Ciclos de Avaliação
CREATE TABLE evaluation_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL DEFAULT '360',
    status VARCHAR(20) NOT NULL DEFAULT 'CONFIGURANDO',
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP NOT NULL,
    data_calibracao TIMESTAMP,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    configuracao JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES evaluation_cycles(id),
    avaliado_id UUID NOT NULL REFERENCES funcionarios(id),
    avaliador_id UUID NOT NULL REFERENCES funcionarios(id),
    tipo_avaliador VARCHAR(20) NOT NULL, -- AUTO, GESTOR, PAR, SUBORDINADO
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    peso DECIMAL(3,2) DEFAULT 1.0,
    nota_final DECIMAL(5,2),
    concluido_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE evaluation_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id UUID NOT NULL REFERENCES evaluations(id),
    competencia_id UUID NOT NULL,
    nota DECIMAL(3,1) NOT NULL,
    comentario TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## TESTES E VALIDAÇÃO

### Testes Unitários

```python
# tests/test_disc_algorithm.py
import pytest
from modules.hr_advanced.disc.algorithm import DISCCalculator

class TestDISCCalculator:
    def test_calculate_profile_balanced(self):
        """Testa perfil balanceado."""
        responses = generate_balanced_responses()
        result = DISCCalculator.calculate(responses)

        assert 20 <= result.dominancia <= 30
        assert 20 <= result.influencia <= 30
        assert 20 <= result.estabilidade <= 30
        assert 20 <= result.conformidade <= 30

    def test_calculate_profile_high_d(self):
        """Testa perfil alto D."""
        responses = generate_high_d_responses()
        result = DISCCalculator.calculate(responses)

        assert result.dominancia > 60
        assert result.perfil_natural.startswith('D')
```

### Testes de Integração

```python
# tests/integration/test_clima_workflow.py
@pytest.mark.asyncio
async def test_complete_clima_workflow():
    """Testa workflow completo de pesquisa de clima."""
    # 1. Criar pesquisa
    survey = await create_survey()

    # 2. Adicionar perguntas
    await add_questions(survey.id)

    # 3. Distribuir para funcionários
    await distribute_survey(survey.id)

    # 4. Simular respostas
    await simulate_responses(survey.id, count=50)

    # 5. Analisar resultados
    analysis = await analyze_survey(survey.id)

    assert analysis.taxa_resposta > 0.8
    assert len(analysis.critical_areas) >= 0
    assert analysis.enps is not None
```

---

## CONCLUSÃO

Este plano de trabalho detalha a implementação completa dos 8 módulos de RH necessários para superar o Solides.

**Pontos-chave:**
1. **Ordem de implementação** baseada em dependências e impacto
2. **6 Agentes de IA especializados** para cada domínio
3. **3 MCP Servers** para integrações externas
4. **4 Skills do Claude Code** para automação
5. **Estrutura modular** seguindo padrões do projeto
6. **Schemas de banco** preparados para escala

**Próximo passo imediato:** Iniciar Sprint 34 com o módulo de Clima.

---

**Documento criado por:** Claude Opus 4.5
**Data:** 23/01/2026
**Versão:** 1.0
