# MÓDULO 07: PLANO DE SUCESSÃO

**Sprint:** 45
**Prioridade:** 7 (MÉDIO)
**Esforço:** 1 sprint
**Dependências:** Nine Box, PDI, Avaliação 360°

---

## VISÃO GERAL

O módulo de Sucessão identifica e desenvolve talentos para assumir posições-chave, garantindo continuidade do negócio e retenção de conhecimento.

### Conceitos Principais

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLANO DE SUCESSÃO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  POSIÇÕES-CHAVE              SUCESSORES                        │
│                                                                 │
│  ┌─────────────┐            ┌─────────────────────────────┐   │
│  │ CEO         │            │ Pronto agora    → João      │   │
│  │             │───────────▶│ 1-2 anos        → Maria     │   │
│  │ Risco: ALTO │            │ 2-3 anos        → Pedro     │   │
│  └─────────────┘            └─────────────────────────────┘   │
│                                                                 │
│  ┌─────────────┐            ┌─────────────────────────────┐   │
│  │ Dir. Tecno- │            │ Pronto agora    → Ana       │   │
│  │ logia       │───────────▶│ 1-2 anos        → Carlos    │   │
│  │ Risco: MÉDIO│            │                             │   │
│  └─────────────┘            └─────────────────────────────┘   │
│                                                                 │
│  MÉTRICAS                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Cobertura: 85% | Prontidão média: 65% | Risco: 3 vagas  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Níveis de Prontidão

| Nível | Descrição | Ação |
|-------|-----------|------|
| **Pronto Agora** | Pode assumir imediatamente | Manter engajado |
| **1-2 Anos** | Precisa de desenvolvimento específico | PDI acelerado |
| **2-3 Anos** | Potencial, mas precisa de experiência | Exposição e projetos |
| **Emergência** | Backup temporário em emergência | Documentar processos |

### Funcionalidades Principais

1. **Mapeamento de Posições-Chave**
   - Identificação de cargos críticos
   - Risco de vacância
   - Impacto no negócio
   - Dificuldade de reposição

2. **Pool de Sucessores**
   - Candidatos por posição
   - Nível de prontidão
   - Gaps de desenvolvimento
   - PDI associado

3. **Análise de Risco**
   - Posições sem sucessor
   - Sucessores únicos
   - Risco de turnover do titular
   - Risco de turnover do sucessor

4. **Desenvolvimento Acelerado**
   - PDI específico para sucessão
   - Mentoria com titular
   - Job shadowing
   - Projetos estratégicos

5. **Visualização**
   - Organograma com sucessores
   - Mapa de calor de risco
   - Pipeline de talentos

---

## AGENTE DE IA: TalentsAgent (Sucessão)

```python
class TalentsAgent:
    """
    Agente de gestão de talentos - módulo de sucessão.
    """

    # 1. Identificação de Posições-Chave
    async def identify_key_positions(
        self,
        organization: Organization
    ) -> List[KeyPosition]:
        """
        Identifica posições críticas automaticamente.

        Critérios:
        - Nível hierárquico (gerência+)
        - Especialização única
        - Impacto em receita/operação
        - Tempo para formar substituto
        - Conhecimento institucional
        """

    # 2. Sugestão de Sucessores
    async def suggest_successors(
        self,
        position: KeyPosition,
        candidates: List[Employee]
    ) -> List[SuccessorSuggestion]:
        """
        Sugere sucessores baseado em múltiplos fatores.

        Considera:
        - Nine Box (quadrantes 6, 8, 9)
        - Competências vs requisitos do cargo
        - Perfil DISC
        - Histórico de performance
        - Aspiração de carreira
        - Mobilidade geográfica
        """

    # 3. Cálculo de Prontidão
    async def calculate_readiness(
        self,
        successor: Employee,
        position: KeyPosition
    ) -> ReadinessAssessment:
        """
        Calcula nível de prontidão.

        Retorna:
        - nivel: PRONTO_AGORA, 1_2_ANOS, 2_3_ANOS, EMERGENCIA
        - score: 0-100
        - gaps: competências faltantes
        - acoes_necessarias: lista de ações
        - tempo_estimado: meses para prontidão
        """

    # 4. Análise de Risco de Vacância
    async def analyze_vacancy_risk(
        self,
        position: KeyPosition,
        incumbent: Employee
    ) -> VacancyRisk:
        """
        Analisa risco de vacância.

        Considera:
        - Risco de turnover do titular
        - Idade/aposentadoria
        - Mercado para o perfil
        - Quantidade de sucessores
        - Prontidão dos sucessores
        """

    # 5. Plano de Desenvolvimento para Sucessão
    async def create_succession_pdi(
        self,
        successor: Employee,
        position: KeyPosition,
        target_readiness: str
    ) -> SuccessionPDI:
        """
        Cria PDI específico para sucessão.

        Inclui:
        - Gaps prioritários
        - Experiências necessárias
        - Mentoria com titular
        - Exposição a stakeholders
        - Projetos estratégicos
        """

    # 6. Simulação de Cenários
    async def simulate_scenario(
        self,
        scenario: str  # "CEO_SAIDA_IMEDIATA", "REESTRUTURACAO", etc.
    ) -> ScenarioAnalysis:
        """
        Simula cenários de sucessão.
        """
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Posições-Chave
CREATE TABLE hr_key_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cargo_id UUID NOT NULL REFERENCES cargos(id),
    departamento_id UUID REFERENCES departamentos(id),
    titular_id UUID REFERENCES funcionarios(id),

    -- Classificação
    criticidade VARCHAR(20) NOT NULL DEFAULT 'MEDIA', -- BAIXA, MEDIA, ALTA, CRITICA
    impacto_negocio TEXT,
    tempo_reposicao_meses INT, -- Tempo estimado para contratar/formar

    -- Risco
    risco_vacancia VARCHAR(20), -- BAIXO, MEDIO, ALTO, CRITICO
    risco_turnover_titular DECIMAL(5,2), -- % estimado
    data_aposentadoria_titular DATE,

    -- Requisitos
    competencias_criticas UUID[], -- IDs de competências
    experiencia_minima_anos INT,
    formacao_minima VARCHAR(50),
    disc_ideal VARCHAR(10),

    -- Status
    status VARCHAR(20) DEFAULT 'ATIVO',
    ultima_revisao DATE,
    proxima_revisao DATE,

    notas TEXT,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(cargo_id, departamento_id, condominio_id)
);

-- Sucessores
CREATE TABLE hr_successors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID NOT NULL REFERENCES hr_key_positions(id) ON DELETE CASCADE,
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),

    -- Prontidão
    nivel_prontidao VARCHAR(20) NOT NULL,
    -- PRONTO_AGORA, 1_2_ANOS, 2_3_ANOS, EMERGENCIA
    score_prontidao DECIMAL(5,2), -- 0-100
    data_prontidao_estimada DATE,

    -- Avaliação
    fit_competencias DECIMAL(5,2), -- % match
    fit_disc DECIMAL(5,2),
    gaps JSONB, -- Lista de gaps
    pontos_fortes JSONB,

    -- Status
    status VARCHAR(20) DEFAULT 'ATIVO', -- ATIVO, REMOVIDO, PROMOVIDO
    motivo_remocao TEXT,

    -- Desenvolvimento
    pdi_id UUID REFERENCES hr_pdis(id),
    mentor_id UUID REFERENCES funcionarios(id), -- Geralmente o titular

    -- Ordem de prioridade
    ordem INT NOT NULL DEFAULT 1,

    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(position_id, funcionario_id)
);

-- Ações de Desenvolvimento para Sucessão
CREATE TABLE hr_succession_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    successor_id UUID NOT NULL REFERENCES hr_successors(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    -- MENTORIA, SHADOWING, PROJETO, INTERINIDADE, EXPOSICAO, TREINAMENTO
    descricao TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'PLANEJADA',
    data_inicio DATE,
    data_fim DATE,
    resultado TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Histórico de Mudanças
CREATE TABLE hr_succession_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID REFERENCES hr_key_positions(id),
    successor_id UUID REFERENCES hr_successors(id),
    acao VARCHAR(50) NOT NULL,
    -- TITULAR_MUDOU, SUCESSOR_ADICIONADO, SUCESSOR_REMOVIDO, SUCESSOR_PROMOVIDO,
    -- PRONTIDAO_ATUALIZADA, POSICAO_CRIADA, POSICAO_REMOVIDA
    descricao TEXT,
    dados_anteriores JSONB,
    dados_novos JSONB,
    usuario_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Revisões de Sucessão
CREATE TABLE hr_succession_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_revisao DATE NOT NULL,
    participantes UUID[],
    posicoes_revisadas UUID[],
    decisoes JSONB, -- Lista de decisões tomadas
    proxima_revisao DATE,
    notas TEXT,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_key_positions_cargo ON hr_key_positions(cargo_id);
CREATE INDEX idx_key_positions_titular ON hr_key_positions(titular_id);
CREATE INDEX idx_key_positions_risco ON hr_key_positions(risco_vacancia);
CREATE INDEX idx_successors_position ON hr_successors(position_id);
CREATE INDEX idx_successors_funcionario ON hr_successors(funcionario_id);
CREATE INDEX idx_successors_prontidao ON hr_successors(nivel_prontidao);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/succession", tags=["Sucessão"])

# Posições-Chave
@router.post("/positions", response_model=PositionResponse, status_code=201)
async def create_key_position(...)

@router.get("/positions", response_model=List[PositionListResponse])
async def list_key_positions(...)

@router.get("/positions/{id}", response_model=PositionDetailResponse)
async def get_key_position(...)

@router.put("/positions/{id}")
async def update_key_position(...)

@router.delete("/positions/{id}")
async def remove_key_position(...)

# Identificação automática
@router.post("/positions/identify")
async def identify_key_positions(...)  # IA identifica

# Sucessores
@router.get("/positions/{id}/successors")
async def get_successors(...)

@router.post("/positions/{id}/successors")
async def add_successor(...)

@router.put("/positions/{id}/successors/{succ_id}")
async def update_successor(...)

@router.delete("/positions/{id}/successors/{succ_id}")
async def remove_successor(...)

@router.post("/positions/{id}/successors/suggest")
async def suggest_successors(...)  # IA sugere

# Prontidão
@router.post("/successors/{id}/calculate-readiness")
async def calculate_readiness(...)

@router.post("/successors/{id}/create-pdi")
async def create_succession_pdi(...)

# Ações de Desenvolvimento
@router.get("/successors/{id}/actions")
async def get_successor_actions(...)

@router.post("/successors/{id}/actions")
async def add_action(...)

@router.put("/actions/{id}")
async def update_action(...)

# Análise de Risco
@router.get("/risk-analysis")
async def get_risk_analysis(...)  # Visão geral de risco

@router.get("/positions/{id}/risk")
async def get_position_risk(...)

@router.get("/coverage")
async def get_coverage_metrics(...)  # % posições cobertas

# Visualização
@router.get("/org-chart")
async def get_org_chart_with_succession(...)

@router.get("/talent-pipeline")
async def get_talent_pipeline(...)

# Revisões
@router.post("/reviews")
async def create_review(...)

@router.get("/reviews")
async def list_reviews(...)

@router.get("/reviews/{id}")
async def get_review(...)

# Relatórios
@router.get("/reports/summary")
async def get_succession_summary(...)

@router.get("/reports/positions/{id}")
async def get_position_report(...)  # PDF
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard Sucessão** (`/rh/sucessao`)
   - Métricas de cobertura
   - Posições em risco
   - Alertas

2. **Posições-Chave** (`/rh/sucessao/posicoes`)
   - Lista de posições
   - Filtros por risco/departamento
   - Status de cobertura

3. **Posição Detalhe** (`/rh/sucessao/posicoes/{id}`)
   - Titular atual
   - Pool de sucessores
   - Análise de risco
   - Ações em andamento

4. **Mapa de Sucessão** (`/rh/sucessao/mapa`)
   - Organograma visual
   - Cores por risco
   - Drill-down

5. **Talent Pipeline** (`/rh/sucessao/pipeline`)
   - Visão de talentos por nível
   - Fluxo de desenvolvimento

6. **Revisão de Sucessão** (`/rh/sucessao/revisoes`)
   - Histórico de revisões
   - Criar nova revisão

### Componentes React

```typescript
// components/sucessao/
├── SuccessionDashboard.tsx    // Dashboard principal
├── KeyPositionCard.tsx        // Card de posição-chave
├── SuccessorsList.tsx         // Lista de sucessores
├── SuccessorCard.tsx          // Card de sucessor
├── ReadinessGauge.tsx         // Gauge de prontidão
├── RiskIndicator.tsx          // Indicador de risco
├── SuccessionOrgChart.tsx     // Organograma com sucessão
├── TalentPipeline.tsx         // Pipeline visual
├── CoverageMetrics.tsx        // Métricas de cobertura
├── GapsList.tsx               // Lista de gaps
└── SuccessionTimeline.tsx     // Timeline de ações
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-succession
description: Gerencia planos de sucessão
version: 1.0.0

triggers:
  - "criar plano sucessao"
  - "identificar sucessores"
  - "risco vacancia"
  - "cobertura sucessao"

prompts:
  identify_positions:
    description: Identifica posições-chave
    template: |
      Identifique posições-chave na organização:

      Critérios:
      1. Nível hierárquico (gerência+)
      2. Especialização única
      3. Impacto em receita > R$ X
      4. Tempo de reposição > 6 meses

      Para cada posição, avalie:
      - Criticidade (Baixa/Média/Alta/Crítica)
      - Risco de vacância
      - Quantidade de sucessores necessários

  suggest_successors:
    description: Sugere sucessores para posição
    parameters:
      - position_id: UUID da posição
    template: |
      Sugira sucessores para posição {position_id}:

      1. Busque funcionários nos quadrantes 6, 8, 9 do Nine Box
      2. Compare competências vs requisitos
      3. Avalie fit DISC
      4. Considere aspirações de carreira
      5. Calcule nível de prontidão
      6. Priorize os 3-5 melhores candidatos

  create_succession_pdi:
    description: Cria PDI para sucessão
    parameters:
      - successor_id: UUID do sucessor
      - target_date: Data alvo de prontidão
    template: |
      Crie PDI de sucessão para {successor_id}:

      1. Identifique gaps prioritários
      2. Planeje:
         - Mentoria com titular
         - Job shadowing
         - Projetos estratégicos
         - Exposição a stakeholders
      3. Defina marcos de progresso
      4. Estime data de prontidão

agents:
  - TalentsAgent
  - CoachAgent
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models: key_positions, successors, actions
  - [ ] TalentsAgent (sucessão)
  - [ ] Controllers
  - [ ] Cálculo de risco
  - [ ] Integração Nine Box

- [ ] **Frontend**
  - [ ] Dashboard
  - [ ] Organograma com sucessão
  - [ ] Cards de prontidão
  - [ ] Pipeline visual

- [ ] **Integrações**
  - [ ] Nine Box (fonte de dados)
  - [ ] PDI (desenvolvimento)
  - [ ] Avaliação 360° (competências)

- [ ] **Testes**
  - [ ] Cálculo de prontidão
  - [ ] Análise de risco
  - [ ] Sugestão de sucessores

---

**Próximo módulo:** [MÓDULO 08: ONBOARDING](./MODULO_08_ONBOARDING.md)
