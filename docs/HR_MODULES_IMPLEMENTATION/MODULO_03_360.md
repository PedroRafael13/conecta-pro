# MÓDULO 03: AVALIAÇÃO DE DESEMPENHO 360°

**Sprint:** 38-39
**Prioridade:** 3 (CRÍTICO)
**Esforço:** 2 sprints
**Dependências:** Módulo de funcionários, competências por cargo, hierarquia organizacional

---

## VISÃO GERAL

O módulo de Avaliação 360° permite avaliar o desempenho dos colaboradores de forma completa, coletando feedback de múltiplas fontes: autoavaliação, gestor, pares e subordinados.

### Tipos de Avaliação

| Tipo | Avaliadores | Uso |
|------|-------------|-----|
| **90°** | Gestor apenas | Feedback rápido |
| **180°** | Auto + Gestor | Padrão simples |
| **270°** | Auto + Gestor + Pares | Equipes |
| **360°** | Auto + Gestor + Pares + Subordinados | Completo |

### Funcionalidades Principais

1. **Configuração de Ciclos**
   - Período de avaliação
   - Tipo (90°, 180°, 270°, 360°)
   - Competências por cargo
   - Pesos por avaliador
   - Escala de avaliação (1-5, 1-10)

2. **Seleção de Avaliadores**
   - Automática por hierarquia
   - Manual por gestor/RH
   - Validação de conflitos de interesse
   - Mínimo de avaliadores por categoria

3. **Coleta de Avaliações**
   - Interface mobile-first
   - Competências com descrição comportamental
   - Comentários por competência
   - Feedback geral
   - Lembretes automáticos

4. **Calibração**
   - Reuniões de calibração
   - Normalização de notas por avaliador
   - Detecção de viés por IA
   - Ajuste de outliers

5. **Resultados e Feedback**
   - Dashboard individual
   - Comparativo com período anterior
   - Gap analysis
   - Geração automática de PDI
   - Reunião de feedback estruturada

---

## AGENTE DE IA: Agent360

```python
class Agent360:
    """
    Agente especializado em avaliação de desempenho 360°.
    """

    def __init__(self):
        self.bias_detector = BiasDetector()
        self.calibration_engine = CalibrationEngine()
        self.feedback_enhancer = FeedbackEnhancer()

    # 1. Detecção de Viés
    async def detect_bias(
        self,
        evaluations: List[Evaluation]
    ) -> List[BiasAlert]:
        """
        Detecta viés nas avaliações.

        Tipos de viés detectados:
        - Halo effect (todas notas altas/baixas)
        - Central tendency (todas notas médias)
        - Recency bias (baseado em eventos recentes)
        - Similarity bias (avaliador similar ao avaliado)
        - Leniency/Strictness (sempre generoso/rigoroso)
        """

    # 2. Calibração de Notas
    async def calibrate_scores(
        self,
        evaluations: List[Evaluation],
        method: str = 'z_score'
    ) -> List[CalibratedEvaluation]:
        """
        Calibra notas para eliminar viés de avaliador.

        Métodos:
        - z_score: Normalização estatística
        - forced_distribution: Curva forçada
        - percentile: Ranking percentil
        """

    # 3. Melhoria de Feedback
    async def improve_feedback(
        self,
        raw_feedback: str,
        context: FeedbackContext
    ) -> ImprovedFeedback:
        """
        Melhora feedback para ser mais construtivo.

        Retorna:
        - feedback_original
        - feedback_melhorado
        - sugestoes_acao
        - tom_detectado
        - areas_mencionadas
        """

    # 4. Análise de Gaps
    async def analyze_gaps(
        self,
        evaluation_result: EvaluationResult,
        job_requirements: JobRequirements
    ) -> GapAnalysis:
        """
        Analisa gaps entre resultado e requisitos do cargo.

        Retorna:
        - gaps_criticos (score < esperado - 1)
        - gaps_moderados (score < esperado - 0.5)
        - pontos_fortes (score > esperado + 0.5)
        - prioridades_desenvolvimento
        """

    # 5. Geração de PDI
    async def generate_pdi_suggestions(
        self,
        gaps: GapAnalysis,
        employee_profile: EmployeeProfile
    ) -> List[PDISuggestion]:
        """
        Gera sugestões de PDI baseadas nos gaps.

        Considera:
        - Perfil DISC do funcionário
        - Recursos disponíveis
        - Histórico de desenvolvimento
        - Preferências de aprendizado
        """

    # 6. Sugestão de Avaliadores
    async def suggest_evaluators(
        self,
        employee: Employee,
        evaluation_type: str
    ) -> EvaluatorSuggestions:
        """
        Sugere avaliadores baseado em interações.

        Usa:
        - Hierarquia organizacional
        - Projetos em comum
        - Frequência de interação
        - Histórico de avaliações
        """
```

---

## WORKFLOW DO CICLO

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO DE AVALIAÇÃO 360°                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CONFIGURAÇÃO          2. SELEÇÃO           3. AVALIAÇÃO    │
│  ┌──────────────┐        ┌──────────────┐     ┌──────────────┐ │
│  │ Definir      │───────▶│ Definir      │────▶│ Período de   │ │
│  │ competências │        │ avaliadores  │     │ coleta       │ │
│  │ e pesos      │        │ por pessoa   │     │ (2-4 semanas)│ │
│  └──────────────┘        └──────────────┘     └──────────────┘ │
│                                                      │          │
│                                                      ▼          │
│  6. FEEDBACK              5. RESULTADOS      4. CALIBRAÇÃO     │
│  ┌──────────────┐        ┌──────────────┐     ┌──────────────┐ │
│  │ Reunião      │◀───────│ Consolidação │◀────│ Reunião de   │ │
│  │ 1:1 com      │        │ e análise    │     │ calibração   │ │
│  │ gestor       │        │ de gaps      │     │ (IA + RH)    │ │
│  └──────────────┘        └──────────────┘     └──────────────┘ │
│         │                                                       │
│         ▼                                                       │
│  7. PDI                                                         │
│  ┌──────────────┐                                              │
│  │ Geração      │                                              │
│  │ automática   │                                              │
│  │ de PDI       │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Ciclos de Avaliação
CREATE TABLE hr_evaluation_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(10) NOT NULL DEFAULT '360', -- 90, 180, 270, 360
    status VARCHAR(20) NOT NULL DEFAULT 'CONFIGURANDO',
    -- Status: CONFIGURANDO, SELECAO_AVALIADORES, EM_ANDAMENTO, CALIBRACAO, FEEDBACK, ENCERRADO

    -- Datas
    data_inicio_config DATE NOT NULL,
    data_fim_selecao DATE,
    data_inicio_avaliacao DATE,
    data_fim_avaliacao DATE,
    data_calibracao DATE,
    data_fim_feedback DATE,

    -- Configurações
    escala_min INT DEFAULT 1,
    escala_max INT DEFAULT 5,
    peso_auto DECIMAL(3,2) DEFAULT 0.10,
    peso_gestor DECIMAL(3,2) DEFAULT 0.40,
    peso_pares DECIMAL(3,2) DEFAULT 0.30,
    peso_subordinados DECIMAL(3,2) DEFAULT 0.20,
    min_avaliadores_pares INT DEFAULT 3,
    min_avaliadores_subordinados INT DEFAULT 2,
    permite_anonimo BOOLEAN DEFAULT true,
    requer_comentario BOOLEAN DEFAULT false,

    condominio_id UUID NOT NULL REFERENCES condominios(id),
    criado_por UUID REFERENCES users(id),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    CONSTRAINT chk_pesos CHECK (
        peso_auto + peso_gestor + peso_pares + peso_subordinados = 1.0
    )
);

-- Competências do Ciclo
CREATE TABLE hr_cycle_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES hr_evaluation_cycles(id) ON DELETE CASCADE,
    competencia_id UUID NOT NULL, -- Ref para tabela de competências
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    peso DECIMAL(3,2) DEFAULT 1.0,
    ordem INT NOT NULL,
    cargo_ids UUID[], -- Se vazio, aplica a todos

    -- Comportamentos observáveis por nível
    comportamentos JSONB, -- {"1": "Não demonstra", "3": "Demonstra parcialmente", "5": "Demonstra consistentemente"}

    created_at TIMESTAMP DEFAULT NOW()
);

-- Avaliações
CREATE TABLE hr_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES hr_evaluation_cycles(id),
    avaliado_id UUID NOT NULL REFERENCES funcionarios(id),
    avaliador_id UUID NOT NULL REFERENCES funcionarios(id),
    tipo_avaliador VARCHAR(20) NOT NULL, -- AUTO, GESTOR, PAR, SUBORDINADO
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    -- Status: PENDENTE, EM_ANDAMENTO, CONCLUIDA, INVALIDADA

    -- Controle
    enviado_em TIMESTAMP,
    iniciado_em TIMESTAMP,
    concluido_em TIMESTAMP,
    lembrete_count INT DEFAULT 0,
    ultimo_lembrete TIMESTAMP,

    -- Resultado
    nota_media DECIMAL(4,2),
    nota_calibrada DECIMAL(4,2),
    feedback_geral TEXT,
    pontos_fortes TEXT,
    areas_melhoria TEXT,

    -- Metadados
    tempo_preenchimento_min INT,
    dispositivo VARCHAR(50),
    anonimo BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(cycle_id, avaliado_id, avaliador_id)
);

-- Respostas por Competência
CREATE TABLE hr_evaluation_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id UUID NOT NULL REFERENCES hr_evaluations(id) ON DELETE CASCADE,
    competencia_id UUID NOT NULL REFERENCES hr_cycle_competencies(id),
    nota INT NOT NULL,
    nota_calibrada DECIMAL(4,2),
    comentario TEXT,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(evaluation_id, competencia_id)
);

-- Resultados Consolidados
CREATE TABLE hr_evaluation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES hr_evaluation_cycles(id),
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),

    -- Notas por fonte
    nota_auto DECIMAL(4,2),
    nota_gestor DECIMAL(4,2),
    nota_pares DECIMAL(4,2),
    nota_subordinados DECIMAL(4,2),
    nota_final DECIMAL(4,2),

    -- Comparativos
    nota_ciclo_anterior DECIMAL(4,2),
    variacao DECIMAL(4,2),
    ranking_departamento INT,
    percentil DECIMAL(5,2),

    -- Análise
    gaps JSONB, -- Lista de gaps por competência
    pontos_fortes JSONB,
    recomendacoes JSONB,

    -- PDI gerado
    pdi_id UUID,
    pdi_gerado_em TIMESTAMP,

    -- Feedback
    feedback_realizado BOOLEAN DEFAULT false,
    feedback_data TIMESTAMP,
    feedback_notas TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(cycle_id, funcionario_id)
);

-- Calibração
CREATE TABLE hr_calibration_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES hr_evaluation_cycles(id),
    departamento_id UUID,
    status VARCHAR(20) DEFAULT 'AGENDADA',
    data_sessao TIMESTAMP,
    participantes UUID[],
    notas TEXT,
    ajustes_realizados JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_evaluations_cycle ON hr_evaluations(cycle_id);
CREATE INDEX idx_evaluations_avaliado ON hr_evaluations(avaliado_id);
CREATE INDEX idx_evaluations_avaliador ON hr_evaluations(avaliador_id);
CREATE INDEX idx_evaluations_status ON hr_evaluations(status);
CREATE INDEX idx_results_cycle ON hr_evaluation_results(cycle_id);
CREATE INDEX idx_results_funcionario ON hr_evaluation_results(funcionario_id);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/evaluations", tags=["Avaliação 360°"])

# Ciclos
@router.post("/cycles", response_model=CycleResponse, status_code=201)
async def create_cycle(...)

@router.get("/cycles", response_model=PaginatedResponse[CycleListResponse])
async def list_cycles(...)

@router.get("/cycles/{id}", response_model=CycleDetailResponse)
async def get_cycle(...)

@router.put("/cycles/{id}", response_model=CycleResponse)
async def update_cycle(...)

@router.post("/cycles/{id}/start")
async def start_cycle(...)  # Inicia período de avaliação

@router.post("/cycles/{id}/close")
async def close_cycle(...)  # Encerra coleta

# Competências do Ciclo
@router.get("/cycles/{id}/competencies")
async def get_cycle_competencies(...)

@router.post("/cycles/{id}/competencies")
async def add_competency(...)

@router.put("/cycles/{id}/competencies/{comp_id}")
async def update_competency(...)

# Avaliadores
@router.get("/cycles/{id}/employees/{emp_id}/evaluators")
async def get_evaluators(...)

@router.post("/cycles/{id}/employees/{emp_id}/evaluators")
async def set_evaluators(...)

@router.get("/cycles/{id}/employees/{emp_id}/evaluators/suggestions")
async def suggest_evaluators(...)  # IA sugere

# Avaliações
@router.get("/my-evaluations")
async def get_my_pending_evaluations(...)  # Avaliações que preciso fazer

@router.get("/evaluations/{id}")
async def get_evaluation(...)

@router.post("/evaluations/{id}/start")
async def start_evaluation(...)

@router.post("/evaluations/{id}/responses")
async def submit_responses(...)

@router.post("/evaluations/{id}/complete")
async def complete_evaluation(...)

# Calibração
@router.get("/cycles/{id}/calibration/data")
async def get_calibration_data(...)

@router.post("/cycles/{id}/calibration/detect-bias")
async def detect_bias(...)

@router.post("/cycles/{id}/calibration/apply")
async def apply_calibration(...)

@router.post("/cycles/{id}/calibration/sessions")
async def create_calibration_session(...)

# Resultados
@router.get("/cycles/{id}/results")
async def get_cycle_results(...)

@router.get("/cycles/{id}/results/{emp_id}")
async def get_employee_result(...)

@router.get("/cycles/{id}/results/{emp_id}/gaps")
async def get_gap_analysis(...)

@router.post("/cycles/{id}/results/{emp_id}/generate-pdi")
async def generate_pdi(...)

# Feedback
@router.post("/cycles/{id}/results/{emp_id}/feedback-done")
async def mark_feedback_done(...)

# Relatórios
@router.get("/cycles/{id}/reports/summary")
async def get_summary_report(...)

@router.get("/cycles/{id}/reports/employee/{emp_id}")
async def get_employee_report(...)  # PDF

@router.get("/cycles/{id}/reports/department/{dept_id}")
async def get_department_report(...)
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard 360°** (`/rh/avaliacao`)
   - Ciclos ativos
   - Minhas avaliações pendentes
   - Progresso do ciclo atual

2. **Configurar Ciclo** (`/rh/avaliacao/ciclos/novo`)
   - Wizard de configuração
   - Seleção de competências
   - Definição de pesos e datas

3. **Gerenciar Ciclo** (`/rh/avaliacao/ciclos/{id}`)
   - Status e progresso
   - Lista de avaliadores
   - Ações (enviar lembretes, fechar)

4. **Avaliar** (`/rh/avaliacao/avaliar/{id}`)
   - Interface de avaliação
   - Competências com escala
   - Campos de comentário

5. **Calibração** (`/rh/avaliacao/ciclos/{id}/calibracao`)
   - Grid de notas
   - Alertas de viés (IA)
   - Ajustes manuais

6. **Meus Resultados** (`/rh/avaliacao/meus-resultados`)
   - Dashboard pessoal
   - Histórico de ciclos
   - Comparativo

7. **Resultado Individual** (`/rh/avaliacao/resultados/{emp_id}`)
   - Notas por fonte
   - Radar de competências
   - Gaps e recomendações
   - Link para PDI

### Componentes React

```typescript
// components/avaliacao360/
├── CycleWizard.tsx         // Wizard de criação de ciclo
├── CompetencySelector.tsx  // Seletor de competências
├── EvaluatorList.tsx       // Lista de avaliadores
├── EvaluationForm.tsx      // Formulário de avaliação
├── CompetencyRating.tsx    // Rating de competência
├── CalibrationGrid.tsx     // Grid de calibração
├── BiasAlertCard.tsx       // Alerta de viés
├── ResultsDashboard.tsx    // Dashboard de resultados
├── CompetencyRadar.tsx     // Gráfico radar
├── GapAnalysisCard.tsx     // Card de análise de gaps
├── SourceComparison.tsx    // Comparativo por fonte
└── FeedbackGuide.tsx       // Guia de feedback
```

---

## DETECÇÃO DE VIÉS

```python
class BiasDetector:
    """
    Detecta diferentes tipos de viés em avaliações.
    """

    def detect_halo_effect(self, responses: List[Response]) -> Optional[BiasAlert]:
        """
        Halo Effect: Todas as notas muito similares (alta ou baixa).
        Se std_dev < 0.5, provável halo effect.
        """
        scores = [r.nota for r in responses]
        std_dev = statistics.stdev(scores)

        if std_dev < 0.5:
            avg = statistics.mean(scores)
            direction = "positivo" if avg > 3.5 else "negativo"
            return BiasAlert(
                tipo="HALO_EFFECT",
                severidade="MEDIA",
                descricao=f"Possível halo effect {direction}. Todas as notas muito similares.",
                sugestao="Revisar se as competências foram avaliadas individualmente."
            )
        return None

    def detect_central_tendency(self, responses: List[Response]) -> Optional[BiasAlert]:
        """
        Central Tendency: Todas as notas próximas da média (3).
        """
        scores = [r.nota for r in responses]
        count_mid = sum(1 for s in scores if 2.5 <= s <= 3.5)

        if count_mid / len(scores) > 0.8:
            return BiasAlert(
                tipo="CENTRAL_TENDENCY",
                severidade="ALTA",
                descricao="80%+ das notas são médias. Possível evitação de extremos.",
                sugestao="Encorajar avaliador a diferenciar competências fortes e fracas."
            )
        return None

    def detect_leniency_strictness(
        self,
        evaluator_id: UUID,
        all_evaluations: List[Evaluation]
    ) -> Optional[BiasAlert]:
        """
        Leniency/Strictness: Avaliador sempre generoso ou rigoroso vs média.
        """
        evaluator_evals = [e for e in all_evaluations if e.avaliador_id == evaluator_id]
        evaluator_avg = statistics.mean([e.nota_media for e in evaluator_evals])

        overall_avg = statistics.mean([e.nota_media for e in all_evaluations])

        diff = evaluator_avg - overall_avg

        if diff > 0.8:
            return BiasAlert(
                tipo="LENIENCY",
                severidade="MEDIA",
                descricao=f"Avaliador {diff:.1f} pontos acima da média geral.",
                sugestao="Considerar calibração das notas deste avaliador."
            )
        elif diff < -0.8:
            return BiasAlert(
                tipo="STRICTNESS",
                severidade="MEDIA",
                descricao=f"Avaliador {abs(diff):.1f} pontos abaixo da média geral.",
                sugestao="Considerar calibração das notas deste avaliador."
            )
        return None
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-360
description: Gerencia ciclos de avaliação de desempenho 360°
version: 1.0.0

triggers:
  - "criar ciclo avaliação"
  - "avaliar funcionário"
  - "calibrar notas"
  - "resultado 360"

prompts:
  create_cycle:
    description: Cria novo ciclo de avaliação
    template: |
      Crie ciclo de avaliação 360°:

      1. Defina nome e período
      2. Selecione tipo (90°, 180°, 270°, 360°)
      3. Configure competências por cargo
      4. Defina pesos por fonte de avaliação
      5. Configure datas do workflow
      6. Liste funcionários participantes

  calibrate:
    description: Executa calibração das notas
    template: |
      Execute calibração do ciclo {cycle_id}:

      1. Detecte viés por avaliador (halo, central, leniency)
      2. Calcule z-scores por avaliador
      3. Identifique outliers (>2 std dev)
      4. Proponha ajustes
      5. Gere relatório de calibração

  generate_feedback:
    description: Prepara feedback para funcionário
    template: |
      Prepare feedback para {funcionario_id} no ciclo {cycle_id}:

      1. Consolide notas por competência
      2. Compare com ciclo anterior
      3. Identifique gaps críticos (>1 ponto abaixo esperado)
      4. Destaque pontos fortes
      5. Sugira 3-5 ações de desenvolvimento
      6. Gere roteiro de conversa de feedback

agents:
  - Agent360
  - CoachAgent
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models: cycles, competencies, evaluations, responses, results
  - [ ] Schemas Pydantic
  - [ ] Repository com queries otimizadas
  - [ ] Service com lógica de negócio
  - [ ] Controllers com todos endpoints
  - [ ] Agent360 (IA)
  - [ ] BiasDetector
  - [ ] CalibrationEngine

- [ ] **Frontend**
  - [ ] Dashboard 360°
  - [ ] Wizard de ciclo
  - [ ] Formulário de avaliação
  - [ ] Grid de calibração
  - [ ] Dashboard de resultados
  - [ ] Radar de competências
  - [ ] Gerador PDF

- [ ] **Integrações**
  - [ ] Nine Box (alimentar)
  - [ ] PDI (gerar automaticamente)
  - [ ] Notificações

- [ ] **Testes**
  - [ ] Unitários (BiasDetector, Calibration)
  - [ ] Integração (workflow completo)
  - [ ] E2E (ciclo end-to-end)

---

**Próximo módulo:** [MÓDULO 04: NINE BOX](./MODULO_04_NINE_BOX.md)
