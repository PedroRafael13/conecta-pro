# MÓDULO 08: ONBOARDING ESTRUTURADO

**Sprint:** 46-47
**Prioridade:** 8 (MÉDIO)
**Esforço:** 2 sprints
**Dependências:** GED (documentos), Recrutamento, Sistema de notificações

---

## VISÃO GERAL

O módulo de Onboarding estrutura a integração de novos colaboradores, garantindo uma experiência positiva e produtividade acelerada.

### Jornada do Novo Colaborador

```
┌─────────────────────────────────────────────────────────────────────┐
│                    JORNADA DE ONBOARDING                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PRÉ-ADMISSÃO        DIA 1           SEMANA 1        30/60/90      │
│  (antes de entrar)   (boas-vindas)   (integração)    (avaliação)   │
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐  ┌─────────────┐ ┌───────────┐ │
│  │ Documentos  │───▶│ Welcome     │─▶│ Treinamen-  │▶│ Pesquisa  │ │
│  │ admissionais│    │ kit         │  │ tos obrig.  │ │ 30 dias   │ │
│  └─────────────┘    └─────────────┘  └─────────────┘ └───────────┘ │
│  ┌─────────────┐    ┌─────────────┐  ┌─────────────┐ ┌───────────┐ │
│  │ Assinatura  │───▶│ Tour        │─▶│ Conhecer    │▶│ Pesquisa  │ │
│  │ digital     │    │ empresa     │  │ equipe      │ │ 60 dias   │ │
│  └─────────────┘    └─────────────┘  └─────────────┘ └───────────┘ │
│  ┌─────────────┐    ┌─────────────┐  ┌─────────────┐ ┌───────────┐ │
│  │ Exames      │───▶│ Setup TI    │─▶│ Metas       │▶│ Pesquisa  │ │
│  │ admissionais│    │ (acessos)   │  │ iniciais    │ │ 90 dias   │ │
│  └─────────────┘    └─────────────┘  └─────────────┘ └───────────┘ │
│                                                                     │
│  BUDDY/MENTOR                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Acompanha durante todo o processo - apoio e orientação      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Funcionalidades Principais

1. **Portal do Novo Colaborador**
   - Acesso antes do primeiro dia
   - Informações da empresa
   - Documentos para preencher
   - Vídeos de boas-vindas
   - FAQ

2. **Checklists Interativos**
   - Tarefas do novo colaborador
   - Tarefas do RH
   - Tarefas do gestor
   - Tarefas de TI
   - Progresso visual

3. **Documentos e Assinatura Digital**
   - Kit de documentos de admissão
   - Assinatura digital integrada
   - Validação automática
   - Armazenamento no GED

4. **Buddy System**
   - Atribuição de mentor/buddy
   - Roteiro de acompanhamento
   - Check-ins periódicos

5. **Pesquisas 30/60/90 Dias**
   - Pesquisa de experiência
   - NPS do onboarding
   - Feedback para melhoria

6. **Métricas**
   - Time to productivity
   - Completion rate
   - NPS do onboarding
   - Turnover no período

---

## AGENTE DE IA: OnboardingAgent

```python
class OnboardingAgent:
    """
    Agente especializado em onboarding de colaboradores.
    """

    # 1. Geração de Plano de Onboarding
    async def generate_onboarding_plan(
        self,
        employee: Employee,
        job: Job,
        start_date: date
    ) -> OnboardingPlan:
        """
        Gera plano de onboarding personalizado.

        Considera:
        - Cargo e departamento
        - Nível (júnior, pleno, sênior, gestão)
        - Localização (presencial, remoto, híbrido)
        - Treinamentos obrigatórios
        - Recursos necessários
        """

    # 2. Atribuição de Buddy
    async def suggest_buddy(
        self,
        new_employee: Employee,
        team: List[Employee]
    ) -> BuddySuggestion:
        """
        Sugere buddy ideal.

        Critérios:
        - Mesmo departamento
        - Disponibilidade
        - Perfil DISC compatível
        - Experiência na empresa
        - Histórico como buddy
        """

    # 3. Geração de Checklist
    async def generate_checklist(
        self,
        plan: OnboardingPlan,
        stakeholder: str  # NOVO_COLABORADOR, RH, GESTOR, TI
    ) -> List[ChecklistItem]:
        """
        Gera checklist por stakeholder.
        """

    # 4. Análise de Pesquisa
    async def analyze_survey(
        self,
        responses: List[SurveyResponse],
        milestone: str  # 30, 60, 90
    ) -> SurveyAnalysis:
        """
        Analisa respostas da pesquisa de onboarding.

        Retorna:
        - nps_score
        - pontos_positivos
        - pontos_melhoria
        - alertas (se algo crítico)
        - sugestoes_acao
        """

    # 5. Predição de Risco
    async def predict_early_turnover_risk(
        self,
        employee: Employee,
        onboarding_data: OnboardingData
    ) -> TurnoverRisk:
        """
        Prediz risco de turnover nos primeiros 90 dias.

        Sinais:
        - Baixa participação no onboarding
        - Feedback negativo nas pesquisas
        - Pouca interação com buddy
        - Tarefas não completadas
        """

    # 6. Mensagem de Boas-Vindas
    async def generate_welcome_message(
        self,
        employee: Employee,
        team_lead: Employee
    ) -> WelcomeMessage:
        """
        Gera mensagem de boas-vindas personalizada.
        """
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Templates de Onboarding
CREATE TABLE hr_onboarding_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    cargo_id UUID REFERENCES cargos(id), -- NULL = genérico
    departamento_id UUID REFERENCES departamentos(id),
    nivel VARCHAR(50), -- JUNIOR, PLENO, SENIOR, GESTAO
    duracao_dias INT DEFAULT 90,
    ativo BOOLEAN DEFAULT true,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Itens do Template
CREATE TABLE hr_onboarding_template_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES hr_onboarding_templates(id) ON DELETE CASCADE,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL,
    -- DOCUMENTO, TREINAMENTO, REUNIAO, TAREFA, VIDEO, LEITURA
    responsavel VARCHAR(50) NOT NULL, -- NOVO_COLABORADOR, RH, GESTOR, TI, BUDDY
    fase VARCHAR(20) NOT NULL, -- PRE_ADMISSAO, DIA_1, SEMANA_1, SEMANA_2, MES_1, MES_2, MES_3
    prazo_dias INT, -- Dias a partir do início
    obrigatorio BOOLEAN DEFAULT true,
    ordem INT NOT NULL,
    recursos JSONB, -- URLs, documentos, etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Onboardings (instâncias)
CREATE TABLE hr_onboardings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    template_id UUID REFERENCES hr_onboarding_templates(id),

    -- Datas
    data_inicio DATE NOT NULL, -- Primeiro dia
    data_fim_prevista DATE NOT NULL,
    data_fim_real DATE,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    -- PENDENTE, EM_ANDAMENTO, CONCLUIDO, CANCELADO
    progresso DECIMAL(5,2) DEFAULT 0,

    -- Buddy
    buddy_id UUID REFERENCES funcionarios(id),
    buddy_aceito BOOLEAN,

    -- Gestor
    gestor_id UUID REFERENCES funcionarios(id),

    -- Métricas
    nps_30_dias INT,
    nps_60_dias INT,
    nps_90_dias INT,
    feedback_geral TEXT,

    notas TEXT,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Tarefas do Onboarding
CREATE TABLE hr_onboarding_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    onboarding_id UUID NOT NULL REFERENCES hr_onboardings(id) ON DELETE CASCADE,
    template_item_id UUID REFERENCES hr_onboarding_template_items(id),

    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL,
    responsavel VARCHAR(50) NOT NULL,
    responsavel_id UUID REFERENCES funcionarios(id), -- Se específico

    fase VARCHAR(20) NOT NULL,
    prazo DATE,
    ordem INT NOT NULL,
    obrigatoria BOOLEAN DEFAULT true,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    -- PENDENTE, EM_ANDAMENTO, CONCLUIDA, PULADA
    concluida_em TIMESTAMP,
    concluida_por UUID REFERENCES users(id),

    -- Evidências
    evidencias JSONB, -- Uploads, links, etc.
    notas TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Documentos de Admissão
CREATE TABLE hr_onboarding_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    onboarding_id UUID NOT NULL REFERENCES hr_onboardings(id) ON DELETE CASCADE,
    documento_tipo VARCHAR(50) NOT NULL,
    -- RG, CPF, CTPS, CNH, COMPROVANTE_RESIDENCIA, FOTO, CONTRATO, etc.
    nome VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    -- PENDENTE, ENVIADO, VALIDADO, REJEITADO
    arquivo_url VARCHAR(500),
    arquivo_ged_id UUID, -- Referência ao GED

    -- Assinatura digital
    requer_assinatura BOOLEAN DEFAULT false,
    assinado BOOLEAN DEFAULT false,
    assinado_em TIMESTAMP,
    assinatura_id VARCHAR(100), -- ID do provedor de assinatura

    -- Validação
    validado_por UUID REFERENCES users(id),
    validado_em TIMESTAMP,
    motivo_rejeicao TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Pesquisas de Onboarding (30/60/90)
CREATE TABLE hr_onboarding_surveys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    onboarding_id UUID NOT NULL REFERENCES hr_onboardings(id) ON DELETE CASCADE,
    milestone VARCHAR(10) NOT NULL, -- 30, 60, 90
    status VARCHAR(20) DEFAULT 'PENDENTE',
    enviado_em TIMESTAMP,
    respondido_em TIMESTAMP,
    respostas JSONB,
    nps_score INT,
    sentimento VARCHAR(20), -- POSITIVO, NEUTRO, NEGATIVO (análise IA)
    alertas JSONB, -- Pontos de atenção identificados
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pool de Buddies
CREATE TABLE hr_buddies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    departamentos_id UUID[], -- Departamentos que pode atender
    disponivel BOOLEAN DEFAULT true,
    max_mentorados INT DEFAULT 2,
    mentorados_atuais INT DEFAULT 0,
    rating_medio DECIMAL(3,2),
    total_onboardings INT DEFAULT 0,
    bio TEXT,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(funcionario_id)
);

-- Feedback do Buddy
CREATE TABLE hr_buddy_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    onboarding_id UUID NOT NULL REFERENCES hr_onboardings(id),
    buddy_id UUID NOT NULL REFERENCES hr_buddies(id),
    avaliador VARCHAR(20) NOT NULL, -- NOVO_COLABORADOR, RH
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comentario TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_onboardings_funcionario ON hr_onboardings(funcionario_id);
CREATE INDEX idx_onboardings_status ON hr_onboardings(status);
CREATE INDEX idx_onboardings_data ON hr_onboardings(data_inicio);
CREATE INDEX idx_tasks_onboarding ON hr_onboarding_tasks(onboarding_id);
CREATE INDEX idx_tasks_status ON hr_onboarding_tasks(status);
CREATE INDEX idx_documents_onboarding ON hr_onboarding_documents(onboarding_id);
CREATE INDEX idx_surveys_onboarding ON hr_onboarding_surveys(onboarding_id);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# Templates
@router.post("/templates", response_model=TemplateResponse, status_code=201)
async def create_template(...)

@router.get("/templates", response_model=List[TemplateListResponse])
async def list_templates(...)

@router.get("/templates/{id}", response_model=TemplateDetailResponse)
async def get_template(...)

@router.put("/templates/{id}")
async def update_template(...)

@router.delete("/templates/{id}")
async def delete_template(...)

# Onboardings
@router.post("/", response_model=OnboardingResponse, status_code=201)
async def create_onboarding(...)

@router.get("/", response_model=PaginatedResponse[OnboardingListResponse])
async def list_onboardings(...)

@router.get("/my-onboarding", response_model=OnboardingDetailResponse)
async def get_my_onboarding(...)  # Para novo colaborador

@router.get("/{id}", response_model=OnboardingDetailResponse)
async def get_onboarding(...)

@router.put("/{id}")
async def update_onboarding(...)

@router.post("/{id}/start")
async def start_onboarding(...)

@router.post("/{id}/complete")
async def complete_onboarding(...)

# Tarefas
@router.get("/{id}/tasks", response_model=List[TaskResponse])
async def get_tasks(...)

@router.get("/{id}/tasks/my", response_model=List[TaskResponse])
async def get_my_tasks(...)  # Tarefas do usuário logado

@router.post("/{id}/tasks/{task_id}/complete")
async def complete_task(...)

@router.post("/{id}/tasks/{task_id}/skip")
async def skip_task(...)

# Documentos
@router.get("/{id}/documents", response_model=List[DocumentResponse])
async def get_documents(...)

@router.post("/{id}/documents")
async def upload_document(...)

@router.post("/{id}/documents/{doc_id}/validate")
async def validate_document(...)

@router.post("/{id}/documents/{doc_id}/reject")
async def reject_document(...)

@router.post("/{id}/documents/{doc_id}/sign")
async def request_signature(...)  # Solicita assinatura digital

# Buddy
@router.get("/{id}/buddy", response_model=BuddyResponse)
async def get_buddy(...)

@router.post("/{id}/buddy/suggest")
async def suggest_buddy(...)

@router.post("/{id}/buddy/assign")
async def assign_buddy(...)

@router.post("/{id}/buddy/feedback")
async def submit_buddy_feedback(...)

# Pool de Buddies
@router.get("/buddies", response_model=List[BuddyListResponse])
async def list_buddies(...)

@router.post("/buddies")
async def register_as_buddy(...)

@router.put("/buddies/{id}")
async def update_buddy(...)

# Pesquisas
@router.get("/{id}/surveys", response_model=List[SurveyResponse])
async def get_surveys(...)

@router.post("/{id}/surveys/{milestone}/send")
async def send_survey(...)

@router.post("/{id}/surveys/{milestone}/respond")
async def respond_survey(...)

# Portal do Novo Colaborador (público com token)
@router.get("/portal/{token}", response_model=PortalResponse)
async def get_portal(...)  # Acesso antes do primeiro dia

@router.post("/portal/{token}/documents")
async def portal_upload_document(...)

@router.post("/portal/{token}/form")
async def portal_submit_form(...)

# Métricas
@router.get("/metrics", response_model=OnboardingMetrics)
async def get_metrics(...)

@router.get("/{id}/metrics", response_model=IndividualMetrics)
async def get_individual_metrics(...)

# Relatórios
@router.get("/reports/summary")
async def get_summary_report(...)

@router.get("/{id}/report")
async def get_onboarding_report(...)  # PDF
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard Onboarding** (`/rh/onboarding`)
   - Onboardings em andamento
   - Métricas gerais
   - Alertas

2. **Portal do Novo Colaborador** (`/onboarding/portal/{token}`)
   - Acessível antes do primeiro dia
   - Vídeo de boas-vindas
   - Documentos para enviar
   - Informações úteis

3. **Meu Onboarding** (`/rh/onboarding/meu`)
   - Para o novo colaborador
   - Checklist pessoal
   - Progresso
   - Buddy

4. **Detalhes Onboarding** (`/rh/onboarding/{id}`)
   - Visão completa (RH/Gestor)
   - Todas as tarefas
   - Documentos
   - Histórico

5. **Templates** (`/rh/onboarding/templates`)
   - CRUD de templates
   - Builder de checklist

6. **Buddies** (`/rh/onboarding/buddies`)
   - Pool de buddies
   - Ratings
   - Disponibilidade

### Componentes React

```typescript
// components/onboarding/
├── OnboardingDashboard.tsx    // Dashboard principal
├── OnboardingCard.tsx         // Card de onboarding
├── TaskChecklist.tsx          // Checklist interativo
├── TaskItem.tsx               // Item de tarefa
├── ProgressTracker.tsx        // Tracker de progresso
├── DocumentUploader.tsx       // Uploader de documentos
├── DocumentCard.tsx           // Card de documento
├── SignatureRequest.tsx       // Solicitação de assinatura
├── BuddyCard.tsx              // Card do buddy
├── WelcomePortal.tsx          // Portal de boas-vindas
├── SurveyForm.tsx             // Formulário de pesquisa
├── NPSGauge.tsx               // Gauge de NPS
├── TemplateBuilder.tsx        // Builder de template
├── TimelineView.tsx           // Timeline do onboarding
└── MilestoneCard.tsx          // Card de milestone
```

---

## ASSINATURA DIGITAL

```python
class SignatureService:
    """
    Serviço de assinatura digital.
    Integração com DocuSign, Clicksign ou solução nativa.
    """

    def __init__(self):
        self.provider = settings.SIGNATURE_PROVIDER  # docusign, clicksign, native

    async def request_signature(
        self,
        document_id: UUID,
        signers: List[Signer]
    ) -> SignatureRequest:
        """
        Solicita assinatura de documento.

        Signer:
        - nome
        - email
        - tipo (funcionario, testemunha, empresa)
        """

    async def check_status(
        self,
        request_id: str
    ) -> SignatureStatus:
        """
        Verifica status da assinatura.
        """

    async def get_signed_document(
        self,
        request_id: str
    ) -> bytes:
        """
        Obtém documento assinado.
        """

    async def cancel_request(
        self,
        request_id: str
    ) -> bool:
        """
        Cancela solicitação de assinatura.
        """
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-onboarding
description: Gerencia onboarding de novos colaboradores
version: 1.0.0

triggers:
  - "criar onboarding"
  - "iniciar integracao"
  - "pesquisa 30 dias"
  - "buddy"

prompts:
  create_onboarding:
    description: Cria onboarding para novo funcionário
    parameters:
      - funcionario_id: UUID do funcionário
      - data_inicio: Data do primeiro dia
    template: |
      Crie onboarding para {funcionario_id}:

      1. Identifique template adequado (cargo/departamento)
      2. Gere checklist personalizado
      3. Sugira buddy
      4. Crie tarefas para cada stakeholder
      5. Agende pesquisas 30/60/90
      6. Envie convite para portal

  suggest_buddy:
    description: Sugere buddy ideal
    parameters:
      - onboarding_id: UUID do onboarding
    template: |
      Sugira buddy para onboarding {onboarding_id}:

      1. Busque buddies disponíveis do departamento
      2. Compare perfil DISC
      3. Verifique rating e histórico
      4. Considere disponibilidade
      5. Retorne top 3 sugestões

  analyze_survey:
    description: Analisa pesquisa de onboarding
    parameters:
      - onboarding_id: UUID do onboarding
      - milestone: 30, 60 ou 90
    template: |
      Analise pesquisa {milestone} dias do onboarding {onboarding_id}:

      1. Calcule NPS
      2. Analise sentimento das respostas
      3. Identifique pontos positivos
      4. Identifique pontos de melhoria
      5. Detecte alertas (risco de turnover)
      6. Sugira ações corretivas

agents:
  - OnboardingAgent
  - SurveyAgent
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models: templates, onboardings, tasks, documents, surveys
  - [ ] OnboardingAgent
  - [ ] Controllers
  - [ ] Integração assinatura digital
  - [ ] Integração GED

- [ ] **Frontend**
  - [ ] Dashboard
  - [ ] Portal do novo colaborador
  - [ ] Checklist interativo
  - [ ] Upload de documentos
  - [ ] Pesquisas

- [ ] **Integrações**
  - [ ] GED (documentos)
  - [ ] Assinatura digital
  - [ ] Notificações
  - [ ] Recrutamento (trigger)

- [ ] **Testes**
  - [ ] Fluxo completo
  - [ ] Upload de documentos
  - [ ] Pesquisas

---

## CONCLUSÃO DA DOCUMENTAÇÃO

Com este documento, completamos a especificação dos **8 módulos de RH avançado**:

| # | Módulo | Sprint | Esforço |
|---|--------|--------|---------|
| 1 | Clima | 34-35 | 2 sprints |
| 2 | DISC | 36-37 | 2 sprints |
| 3 | 360° | 38-39 | 2 sprints |
| 4 | Nine Box | 40 | 1 sprint |
| 5 | PDI | 41 | 1 sprint |
| 6 | Recrutamento | 42-44 | 3 sprints |
| 7 | Sucessão | 45 | 1 sprint |
| 8 | Onboarding | 46-47 | 2 sprints |

**Total: 14 sprints (7 meses)**

### Próximo Passo

Iniciar **Sprint 34** com o **Módulo de Clima Organizacional**.

---

**Documentação criada por:** Claude Opus 4.5
**Data:** 23/01/2026
**Versão:** 1.0
