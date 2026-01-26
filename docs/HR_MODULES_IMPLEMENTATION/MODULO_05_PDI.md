# MÓDULO 05: PDI - PLANO DE DESENVOLVIMENTO INDIVIDUAL

**Sprint:** 41
**Prioridade:** 4 (CRÍTICO)
**Esforço:** 1 sprint
**Dependências:** Avaliação 360°, Competências por cargo

---

## VISÃO GERAL

O PDI é uma ferramenta estruturada para desenvolvimento profissional, conectando gaps de competências a ações concretas com acompanhamento.

### Estrutura do PDI

```
┌─────────────────────────────────────────────────────────────────┐
│                              PDI                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ORIGEM DOS GAPS                    AÇÕES DE DESENVOLVIMENTO   │
│  ┌──────────────┐                  ┌──────────────────────┐    │
│  │ Avaliação    │                  │ Formal               │    │
│  │ 360°         │─────────────────▶│ - Cursos            │    │
│  └──────────────┘                  │ - Certificações     │    │
│                                    │ - Treinamentos      │    │
│  ┌──────────────┐                  └──────────────────────┘    │
│  │ Nine Box     │                  ┌──────────────────────┐    │
│  │              │─────────────────▶│ Experiencial         │    │
│  └──────────────┘                  │ - Projetos          │    │
│                                    │ - Job rotation      │    │
│  ┌──────────────┐                  │ - Shadowing         │    │
│  │ Feedback     │                  └──────────────────────┘    │
│  │ do Gestor    │─────────────────▶┌──────────────────────┐    │
│  └──────────────┘                  │ Social               │    │
│                                    │ - Mentoria          │    │
│  ┌──────────────┐                  │ - Coaching          │    │
│  │ Autoavaliação│                  │ - Comunidades       │    │
│  │              │─────────────────▶└──────────────────────┘    │
│  └──────────────┘                                              │
│                                                                 │
│  ACOMPANHAMENTO                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ Check-ins periódicos → Ajustes → Conclusão → Avaliação│     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Funcionalidades Principais

1. **Geração Automática**
   - A partir de gaps da avaliação 360°
   - Sugestões de IA baseadas no perfil
   - Templates por competência

2. **Metas SMART**
   - Específicas, Mensuráveis, Atingíveis, Relevantes, Temporais
   - IA ajuda a formular metas

3. **Catálogo de Ações**
   - Cursos internos e externos
   - Livros e artigos
   - Projetos e experiências
   - Mentores disponíveis

4. **Acompanhamento**
   - Check-ins periódicos (semanal/quinzenal)
   - Evidências de progresso
   - Feedback contínuo
   - Alertas de atraso

5. **Métricas**
   - Taxa de conclusão
   - Impacto nas competências
   - ROI de desenvolvimento

---

## AGENTE DE IA: CoachAgent

```python
class CoachAgent:
    """
    Agente de coaching e desenvolvimento profissional.
    """

    def __init__(self):
        self.llm = "claude-3-opus"
        self.courses_db = CoursesDatabase()
        self.mentors_db = MentorsDatabase()

    # 1. Sugestão de Metas SMART
    async def suggest_smart_goals(
        self,
        gaps: List[CompetencyGap],
        employee_profile: EmployeeProfile
    ) -> List[SMARTGoal]:
        """
        Sugere metas SMART baseadas nos gaps.

        Exemplo de entrada:
        - Gap: Comunicação (atual: 2.5, esperado: 4.0)
        - Perfil: Analista Jr, 2 anos, perfil DISC: SC

        Exemplo de saída:
        {
            "competencia": "Comunicação",
            "meta": "Realizar 3 apresentações para a equipe até março/2026",
            "especifica": "Apresentações de 15min sobre projetos em andamento",
            "mensuravel": "3 apresentações concluídas",
            "atingivel": "1 apresentação por mês",
            "relevante": "Desenvolve comunicação verbal essencial para promoção",
            "temporal": "Até 31/03/2026",
            "indicador": "Feedback médio >= 4.0 dos participantes"
        }
        """

    # 2. Recomendação de Ações
    async def recommend_actions(
        self,
        goal: SMARTGoal,
        preferences: LearningPreferences
    ) -> List[DevelopmentAction]:
        """
        Recomenda ações de desenvolvimento.

        Considera:
        - Preferência de aprendizado (visual, auditivo, prático)
        - Disponibilidade de tempo
        - Orçamento disponível
        - Recursos internos vs externos
        """
        actions = []

        # Formal (70-20-10: 10%)
        courses = await self.courses_db.search(goal.competencia)
        actions.extend(self._rank_courses(courses, preferences))

        # Experiencial (70-20-10: 70%)
        experiences = self._suggest_experiences(goal)
        actions.extend(experiences)

        # Social (70-20-10: 20%)
        mentors = await self.mentors_db.find(goal.competencia)
        actions.extend(self._format_mentoring(mentors))

        return self._prioritize(actions)

    # 3. Melhoria de Feedback
    async def improve_feedback(
        self,
        raw_feedback: str,
        context: str
    ) -> ImprovedFeedback:
        """
        Melhora feedback para ser mais construtivo.

        Transforma:
        "Você não sabe se comunicar" →
        "Percebi oportunidades de melhoria na comunicação.
         Especificamente, nas reuniões de status, as informações
         poderiam ser mais estruturadas. Sugiro usar o formato
         STAR (Situação, Tarefa, Ação, Resultado)."
        """

    # 4. Geração de Check-in
    async def generate_checkin_questions(
        self,
        pdi: PDI,
        last_checkin: Optional[CheckIn]
    ) -> List[CheckInQuestion]:
        """
        Gera perguntas para check-in.

        Perguntas dinâmicas baseadas em:
        - Progresso das ações
        - Tempo decorrido
        - Dificuldades anteriores
        """

    # 5. Mensagem Motivacional
    async def generate_motivation(
        self,
        employee: Employee,
        pdi_progress: PDIProgress
    ) -> MotivationMessage:
        """
        Gera mensagem motivacional personalizada.

        Considera:
        - Perfil DISC (D precisa de desafio, S precisa de segurança)
        - Progresso atual
        - Marcos alcançados
        """

    # 6. Análise de Impacto
    async def analyze_impact(
        self,
        pdi: PDI,
        before_scores: Dict[str, float],
        after_scores: Dict[str, float]
    ) -> ImpactAnalysis:
        """
        Analisa impacto do PDI nas competências.
        """
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- PDIs
CREATE TABLE hr_pdis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    gestor_id UUID REFERENCES funcionarios(id),
    ciclo_avaliacao_id UUID REFERENCES hr_evaluation_cycles(id),

    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    -- Status: RASCUNHO, ATIVO, PAUSADO, CONCLUIDO, CANCELADO

    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    data_revisao DATE, -- Próxima revisão formal

    -- Métricas
    progresso_geral DECIMAL(5,2) DEFAULT 0,
    total_metas INT DEFAULT 0,
    metas_concluidas INT DEFAULT 0,

    -- Origem
    gerado_automaticamente BOOLEAN DEFAULT false,
    fonte VARCHAR(50), -- AVALIACAO_360, NINE_BOX, GESTOR, AUTO

    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    CONSTRAINT chk_datas CHECK (data_fim > data_inicio)
);

-- Metas do PDI
CREATE TABLE hr_pdi_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdi_id UUID NOT NULL REFERENCES hr_pdis(id) ON DELETE CASCADE,
    competencia_id UUID, -- Competência relacionada (opcional)

    -- Meta SMART
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    especifica TEXT,
    mensuravel TEXT,
    atingivel TEXT,
    relevante TEXT,
    prazo DATE NOT NULL,
    indicador_sucesso TEXT,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    -- Status: PENDENTE, EM_ANDAMENTO, CONCLUIDA, CANCELADA
    progresso DECIMAL(5,2) DEFAULT 0,
    prioridade VARCHAR(10) DEFAULT 'MEDIA', -- BAIXA, MEDIA, ALTA, CRITICA

    -- Resultado
    resultado TEXT,
    evidencias JSONB, -- Links, arquivos, etc.
    concluida_em TIMESTAMP,
    avaliacao_gestor INT, -- 1-5

    ordem INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Ações de Desenvolvimento
CREATE TABLE hr_pdi_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID NOT NULL REFERENCES hr_pdi_goals(id) ON DELETE CASCADE,

    tipo VARCHAR(50) NOT NULL,
    -- Tipos: CURSO, LIVRO, ARTIGO, VIDEO, PROJETO, MENTORIA, COACHING,
    --        JOB_ROTATION, SHADOWING, COMUNIDADE, CERTIFICACAO, OUTRO

    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    url VARCHAR(500),
    provedor VARCHAR(100), -- Coursera, Udemy, Interno, etc.
    duracao_horas INT,
    custo DECIMAL(10,2),

    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    progresso DECIMAL(5,2) DEFAULT 0,
    prazo DATE,

    -- Resultado
    concluida_em TIMESTAMP,
    nota TEXT, -- Anotações do funcionário
    certificado_url VARCHAR(500),

    ordem INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Check-ins
CREATE TABLE hr_pdi_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdi_id UUID NOT NULL REFERENCES hr_pdis(id) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL, -- AUTO, GESTOR, SISTEMA

    data_checkin TIMESTAMP NOT NULL DEFAULT NOW(),
    respondido_por UUID REFERENCES funcionarios(id),

    -- Respostas
    progresso_relatado TEXT,
    dificuldades TEXT,
    apoio_necessario TEXT,
    proximos_passos TEXT,
    humor INT, -- 1-5, como está se sentindo

    -- Feedback do gestor (se aplicável)
    feedback_gestor TEXT,
    ajustes_sugeridos TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Catálogo de Recursos
CREATE TABLE hr_development_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    url VARCHAR(500),
    provedor VARCHAR(100),
    duracao_horas INT,
    custo DECIMAL(10,2),
    gratuito BOOLEAN DEFAULT false,

    -- Categorização
    competencias VARCHAR(100)[], -- Competências que desenvolve
    niveis VARCHAR(20)[], -- JUNIOR, PLENO, SENIOR, GESTAO
    idioma VARCHAR(10) DEFAULT 'pt-BR',
    rating DECIMAL(3,2), -- Avaliação média

    ativo BOOLEAN DEFAULT true,
    condominio_id UUID REFERENCES condominios(id), -- NULL = global
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Pool de Mentores
CREATE TABLE hr_mentors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    competencias VARCHAR(100)[] NOT NULL,
    disponibilidade VARCHAR(50), -- BAIXA, MEDIA, ALTA
    max_mentorados INT DEFAULT 3,
    mentorados_atuais INT DEFAULT 0,
    bio TEXT,
    ativo BOOLEAN DEFAULT true,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_pdis_funcionario ON hr_pdis(funcionario_id);
CREATE INDEX idx_pdis_status ON hr_pdis(status);
CREATE INDEX idx_pdi_goals_pdi ON hr_pdi_goals(pdi_id);
CREATE INDEX idx_pdi_goals_status ON hr_pdi_goals(status);
CREATE INDEX idx_catalog_competencias ON hr_development_catalog USING GIN(competencias);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/pdi", tags=["PDI"])

# CRUD PDI
@router.post("/", response_model=PDIResponse, status_code=201)
async def create_pdi(...)

@router.get("/", response_model=PaginatedResponse[PDIListResponse])
async def list_pdis(...)

@router.get("/my-pdi", response_model=PDIDetailResponse)
async def get_my_pdi(...)  # PDI do usuário logado

@router.get("/{id}", response_model=PDIDetailResponse)
async def get_pdi(...)

@router.put("/{id}", response_model=PDIResponse)
async def update_pdi(...)

@router.delete("/{id}", status_code=204)
async def delete_pdi(...)

@router.post("/{id}/activate")
async def activate_pdi(...)

@router.post("/{id}/complete")
async def complete_pdi(...)

# Geração Automática
@router.post("/generate", response_model=PDIResponse)
async def generate_pdi(...)  # Gera PDI a partir de gaps

@router.post("/generate/preview")
async def preview_generated_pdi(...)  # Preview antes de criar

# Metas
@router.get("/{pdi_id}/goals", response_model=List[GoalResponse])
async def get_goals(...)

@router.post("/{pdi_id}/goals", response_model=GoalResponse)
async def add_goal(...)

@router.put("/{pdi_id}/goals/{goal_id}")
async def update_goal(...)

@router.delete("/{pdi_id}/goals/{goal_id}")
async def remove_goal(...)

@router.post("/{pdi_id}/goals/{goal_id}/complete")
async def complete_goal(...)

# Ações
@router.get("/{pdi_id}/goals/{goal_id}/actions")
async def get_actions(...)

@router.post("/{pdi_id}/goals/{goal_id}/actions")
async def add_action(...)

@router.put("/actions/{action_id}")
async def update_action(...)

@router.post("/actions/{action_id}/complete")
async def complete_action(...)

# Check-ins
@router.get("/{pdi_id}/checkins")
async def get_checkins(...)

@router.post("/{pdi_id}/checkins")
async def submit_checkin(...)

@router.get("/{pdi_id}/checkins/pending")
async def get_pending_checkin(...)  # Próximo check-in

# IA
@router.post("/suggest-goals")
async def suggest_goals(...)  # IA sugere metas

@router.post("/suggest-actions")
async def suggest_actions(...)  # IA sugere ações

@router.post("/improve-goal")
async def improve_goal(...)  # IA melhora meta SMART

# Catálogo
@router.get("/catalog/search")
async def search_catalog(...)

@router.get("/catalog/courses")
async def list_courses(...)

@router.get("/catalog/mentors")
async def list_mentors(...)

# Relatórios
@router.get("/{id}/report")
async def get_pdi_report(...)  # PDF

@router.get("/stats")
async def get_pdi_stats(...)  # Estatísticas gerais
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Meu PDI** (`/rh/pdi/meu`)
   - Visão geral do PDI ativo
   - Progresso das metas
   - Ações pendentes
   - Próximo check-in

2. **Criar/Editar PDI** (`/rh/pdi/novo` | `/rh/pdi/{id}/editar`)
   - Wizard de criação
   - Sugestões de IA
   - Catálogo de recursos

3. **Detalhes do PDI** (`/rh/pdi/{id}`)
   - Metas e ações
   - Timeline de progresso
   - Check-ins

4. **Check-in** (`/rh/pdi/{id}/checkin`)
   - Formulário de check-in
   - Reflexão guiada
   - Próximos passos

5. **Dashboard de PDIs** (`/rh/pdi/dashboard`)
   - PDIs da equipe (para gestores)
   - Estatísticas
   - Alertas

6. **Catálogo** (`/rh/pdi/catalogo`)
   - Busca de cursos
   - Pool de mentores
   - Recursos recomendados

### Componentes React

```typescript
// components/pdi/
├── PDIOverview.tsx        // Visão geral do PDI
├── GoalCard.tsx           // Card de meta
├── GoalProgress.tsx       // Barra de progresso
├── ActionItem.tsx         // Item de ação
├── CheckInForm.tsx        // Formulário de check-in
├── CheckInHistory.tsx     // Histórico de check-ins
├── SMARTEditor.tsx        // Editor de meta SMART
├── CatalogSearch.tsx      // Busca no catálogo
├── CourseCard.tsx         // Card de curso
├── MentorCard.tsx         // Card de mentor
├── AIAssistant.tsx        // Assistente de IA
├── ProgressTimeline.tsx   // Timeline de progresso
└── PDIReport.tsx          // Relatório do PDI
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-pdi
description: Gerencia Planos de Desenvolvimento Individual
version: 1.0.0

triggers:
  - "criar pdi"
  - "sugerir metas"
  - "acompanhar pdi"
  - "checkin pdi"

prompts:
  create:
    description: Cria PDI a partir de gaps
    parameters:
      - funcionario_id: UUID do funcionário
      - cycle_id: UUID do ciclo de avaliação (opcional)
    template: |
      Crie PDI para {funcionario_id}:

      1. Busque gaps da avaliação 360° (se houver)
      2. Analise perfil DISC
      3. Sugira 3-5 metas SMART priorizadas
      4. Recomende ações do modelo 70-20-10:
         - 70% experiencial
         - 20% social
         - 10% formal
      5. Defina cronograma de check-ins

  suggest_goals:
    description: Sugere metas SMART
    parameters:
      - gap: Competência e scores
      - perfil: Perfil do funcionário
    template: |
      Sugira meta SMART para gap:
      Competência: {gap.competencia}
      Score atual: {gap.atual}
      Score esperado: {gap.esperado}

      Considere o perfil:
      - Cargo: {perfil.cargo}
      - Tempo de casa: {perfil.tempo_casa}
      - DISC: {perfil.disc}

  checkin:
    description: Conduz check-in
    parameters:
      - pdi_id: UUID do PDI
    template: |
      Conduza check-in do PDI {pdi_id}:

      1. Revise progresso das metas
      2. Faça perguntas reflexivas:
         - O que você conquistou desde o último check-in?
         - Quais desafios encontrou?
         - Do que você precisa para avançar?
      3. Ajuste prazos se necessário
      4. Defina próximos passos claros
      5. Ofereça mensagem motivacional

agents:
  - CoachAgent
```

---

## MODELO 70-20-10

```python
class DevelopmentModel:
    """
    Implementa o modelo 70-20-10 de desenvolvimento.
    """

    # 70% Experiencial (on-the-job)
    EXPERIENTIAL_ACTIONS = [
        "projeto_desafiador",
        "job_rotation",
        "shadowing",
        "stretch_assignment",
        "lideranca_projeto",
        "task_force",
        "substituicao_temporaria",
    ]

    # 20% Social (relacionamentos)
    SOCIAL_ACTIONS = [
        "mentoria",
        "coaching",
        "feedback_360",
        "comunidade_pratica",
        "networking",
        "peer_learning",
        "grupo_estudo",
    ]

    # 10% Formal (cursos, treinamentos)
    FORMAL_ACTIONS = [
        "curso_online",
        "curso_presencial",
        "certificacao",
        "workshop",
        "livro",
        "podcast",
        "artigo",
        "video",
    ]

    def suggest_balanced_plan(
        self,
        goal: SMARTGoal,
        available_resources: List[Resource]
    ) -> List[DevelopmentAction]:
        """
        Sugere plano balanceado 70-20-10.
        """
        plan = []

        # 70% Experiencial
        experiential = self._find_experiential(goal, available_resources)
        plan.extend(experiential[:2])  # 2 ações experienciais

        # 20% Social
        social = self._find_social(goal, available_resources)
        plan.extend(social[:1])  # 1 ação social

        # 10% Formal
        formal = self._find_formal(goal, available_resources)
        plan.extend(formal[:1])  # 1 ação formal

        return plan
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models: pdis, goals, actions, checkins
  - [ ] Schemas Pydantic
  - [ ] CoachAgent
  - [ ] Gerador automático de PDI
  - [ ] Controllers
  - [ ] Catálogo de recursos

- [ ] **Frontend**
  - [ ] Meu PDI
  - [ ] Editor de meta SMART
  - [ ] Catálogo de cursos
  - [ ] Check-in interativo
  - [ ] Dashboard de gestão
  - [ ] Assistente IA

- [ ] **Integrações**
  - [ ] Avaliação 360° (gaps)
  - [ ] DISC (perfil)
  - [ ] Notificações (lembretes)

- [ ] **Testes**
  - [ ] Unitários (CoachAgent)
  - [ ] Integração
  - [ ] E2E

---

**Próximo módulo:** [MÓDULO 06: RECRUTAMENTO](./MODULO_06_RECRUTAMENTO.md)
