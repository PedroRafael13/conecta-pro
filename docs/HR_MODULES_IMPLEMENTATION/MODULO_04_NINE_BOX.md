# MÓDULO 04: NINE BOX - MATRIZ DE TALENTOS

**Sprint:** 40
**Prioridade:** 5 (MÉDIO)
**Esforço:** 1 sprint
**Dependências:** Módulo de Avaliação 360°, Metas/OKRs

---

## VISÃO GERAL

O Nine Box é uma ferramenta visual que classifica funcionários em uma matriz 3x3 baseada em dois eixos: **Performance** (resultados) e **Potencial** (capacidade de crescimento).

### A Matriz

```
                         POTENCIAL
           Baixo          Médio           Alto
        ┌─────────────┬─────────────┬─────────────┐
  Alto  │   ENIGMA    │   FORTE     │   ESTRELA   │
        │   (7)       │ DESEMPENHO  │   (9)       │
        │             │   (8)       │             │
        ├─────────────┼─────────────┼─────────────┤
P Médio │  EFICAZ     │    CORE     │   ALTO      │
E       │  (4)        │  PLAYER     │ POTENCIAL   │
R       │             │   (5)       │   (6)       │
F       ├─────────────┼─────────────┼─────────────┤
O Baixo │ PROBLEMA    │  QUESTÃO    │   DIAMANTE  │
R       │  (1)        │   (2)       │   BRUTO     │
M       │             │             │   (3)       │
        └─────────────┴─────────────┴─────────────┘
```

### Classificações

| Posição | Nome | Ação Recomendada |
|---------|------|------------------|
| **9** | Estrela | Desenvolver para liderança, reter |
| **8** | Forte Desempenho | Expandir responsabilidades |
| **7** | Enigma | Investigar barreiras |
| **6** | Alto Potencial | Acelerar desenvolvimento |
| **5** | Core Player | Manter e valorizar |
| **4** | Eficaz | Investir em potencial |
| **3** | Diamante Bruto | PDI intensivo |
| **2** | Questão | Coaching focado |
| **1** | Problema | PIP ou desligamento |

### Funcionalidades Principais

1. **Matriz Visual Interativa**
   - Drag & drop de funcionários
   - Filtros por departamento, cargo, tempo de casa
   - Zoom e navegação
   - Export PNG/PDF

2. **Cálculo Automático**
   - Performance: média das avaliações 360°
   - Potencial: combinação de fatores (DISC, idade, formação, histórico)
   - Configuração de pesos e thresholds

3. **Histórico e Tendências**
   - Evolução ao longo dos ciclos
   - Movimentações na matriz
   - Alertas de regressão

4. **Ações por Quadrante**
   - PDI automático
   - Alertas de risco
   - Plano de sucessão
   - Programas de desenvolvimento

---

## AGENTE DE IA: TalentsAgent (Nine Box)

```python
class TalentsAgent:
    """
    Agente especializado em gestão de talentos e Nine Box.
    """

    # 1. Cálculo de Potencial
    async def calculate_potential(
        self,
        employee: Employee,
        factors: PotentialFactors
    ) -> PotentialScore:
        """
        Calcula potencial do funcionário.

        Fatores considerados:
        - Perfil DISC (adaptabilidade)
        - Idade e fase de carreira
        - Formação e certificações
        - Velocidade de aprendizado
        - Ambição demonstrada
        - Histórico de promoções
        - Feedback de liderança
        """

    # 2. Classificação Nine Box
    async def classify_employee(
        self,
        performance_score: float,
        potential_score: float,
        thresholds: NineBoxThresholds
    ) -> NineBoxPosition:
        """
        Classifica funcionário na matriz.

        Retorna:
        - quadrante: 1-9
        - nome: "Estrela", "Core Player", etc.
        - performance_level: BAIXO, MEDIO, ALTO
        - potential_level: BAIXO, MEDIO, ALTO
        - acoes_recomendadas: List[str]
        """

    # 3. Detecção de Movimentações
    async def detect_movements(
        self,
        current_snapshot: NineBoxSnapshot,
        previous_snapshot: NineBoxSnapshot
    ) -> List[Movement]:
        """
        Detecta movimentações entre ciclos.

        Retorna:
        - progressoes (subiu de quadrante)
        - regressoes (desceu de quadrante)
        - estaveis (mesma posição)
        """

    # 4. Predição de Risco de Turnover
    async def predict_turnover_risk(
        self,
        employee: Employee,
        nine_box_position: int
    ) -> TurnoverRisk:
        """
        Prediz risco de saída.

        Considera:
        - Posição no Nine Box
        - Tempo sem promoção
        - Comparativo salarial
        - Pesquisa de clima
        - Sinais de desengajamento
        """

    # 5. Sugestões de Retenção
    async def suggest_retention_actions(
        self,
        high_risk_employees: List[Employee]
    ) -> List[RetentionAction]:
        """
        Sugere ações de retenção.

        Tipos de ação:
        - Ajuste salarial
        - Promoção
        - Novo desafio/projeto
        - Mentoria com executivo
        - Programa de desenvolvimento
        - Benefício personalizado
        """

    # 6. Identificação de High Potentials
    async def identify_high_potentials(
        self,
        employees: List[Employee],
        criteria: HighPotentialCriteria
    ) -> List[HighPotential]:
        """
        Identifica funcionários de alto potencial.

        Critérios:
        - Quadrantes 6, 8, 9 no Nine Box
        - Performance consistente (2+ ciclos)
        - Perfil de liderança
        - Disponibilidade para mobilidade
        """
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Snapshots do Nine Box
CREATE TABLE hr_nine_box_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    data_referencia DATE NOT NULL,
    cycle_id UUID REFERENCES hr_evaluation_cycles(id), -- Ciclo de avaliação fonte

    -- Configuração de thresholds
    performance_baixo_max DECIMAL(4,2) DEFAULT 2.5,
    performance_medio_max DECIMAL(4,2) DEFAULT 3.5,
    potential_baixo_max DECIMAL(4,2) DEFAULT 2.5,
    potential_medio_max DECIMAL(4,2) DEFAULT 3.5,

    -- Pesos para cálculo de potencial
    peso_disc DECIMAL(3,2) DEFAULT 0.15,
    peso_idade DECIMAL(3,2) DEFAULT 0.10,
    peso_formacao DECIMAL(3,2) DEFAULT 0.15,
    peso_historico DECIMAL(3,2) DEFAULT 0.20,
    peso_lideranca DECIMAL(3,2) DEFAULT 0.25,
    peso_aprendizado DECIMAL(3,2) DEFAULT 0.15,

    status VARCHAR(20) DEFAULT 'RASCUNHO', -- RASCUNHO, ATIVO, ARQUIVADO
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    criado_por UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Posições dos Funcionários
CREATE TABLE hr_nine_box_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id UUID NOT NULL REFERENCES hr_nine_box_snapshots(id) ON DELETE CASCADE,
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),

    -- Scores
    performance_score DECIMAL(4,2) NOT NULL,
    potential_score DECIMAL(4,2) NOT NULL,

    -- Classificação
    quadrante INT NOT NULL CHECK (quadrante BETWEEN 1 AND 9),
    performance_level VARCHAR(10) NOT NULL, -- BAIXO, MEDIO, ALTO
    potential_level VARCHAR(10) NOT NULL,

    -- Origem dos dados
    performance_source VARCHAR(50), -- AVALIACAO_360, MANUAL, METAS
    potential_source VARCHAR(50),

    -- Ajuste manual
    ajustado_manualmente BOOLEAN DEFAULT false,
    justificativa_ajuste TEXT,
    ajustado_por UUID REFERENCES users(id),
    ajustado_em TIMESTAMP,

    -- Comparativo
    quadrante_anterior INT,
    movimento VARCHAR(20), -- SUBIU, DESCEU, ESTAVEL, NOVO

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(snapshot_id, funcionario_id)
);

-- Ações por Quadrante
CREATE TABLE hr_nine_box_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID NOT NULL REFERENCES hr_nine_box_positions(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL, -- PDI, PROMOCAO, RETENCAO, PIP, COACHING, PROJETO
    descricao TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'SUGERIDA', -- SUGERIDA, APROVADA, EM_ANDAMENTO, CONCLUIDA
    responsavel_id UUID REFERENCES funcionarios(id),
    prazo DATE,
    resultado TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Configuração de Potencial por Cargo
CREATE TABLE hr_potential_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cargo_id UUID REFERENCES cargos(id), -- NULL = padrão geral
    fator VARCHAR(50) NOT NULL, -- DISC, IDADE, FORMACAO, etc.
    peso DECIMAL(3,2) NOT NULL,
    config JSONB, -- Configurações específicas do fator
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(cargo_id, fator, condominio_id)
);

-- Índices
CREATE INDEX idx_nine_box_snapshot ON hr_nine_box_positions(snapshot_id);
CREATE INDEX idx_nine_box_funcionario ON hr_nine_box_positions(funcionario_id);
CREATE INDEX idx_nine_box_quadrante ON hr_nine_box_positions(quadrante);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/nine-box", tags=["Nine Box"])

# Snapshots
@router.post("/snapshots", response_model=SnapshotResponse, status_code=201)
async def create_snapshot(...)

@router.get("/snapshots", response_model=List[SnapshotListResponse])
async def list_snapshots(...)

@router.get("/snapshots/{id}", response_model=SnapshotDetailResponse)
async def get_snapshot(...)

@router.put("/snapshots/{id}", response_model=SnapshotResponse)
async def update_snapshot(...)

@router.delete("/snapshots/{id}", status_code=204)
async def delete_snapshot(...)

@router.post("/snapshots/{id}/publish")
async def publish_snapshot(...)

# Cálculo
@router.post("/snapshots/{id}/calculate")
async def calculate_positions(...)  # Calcula todas as posições

@router.post("/snapshots/{id}/calculate/{emp_id}")
async def calculate_employee_position(...)  # Calcula um funcionário

# Posições
@router.get("/snapshots/{id}/positions")
async def get_all_positions(...)  # Retorna matriz completa

@router.get("/snapshots/{id}/positions/{emp_id}")
async def get_employee_position(...)

@router.put("/snapshots/{id}/positions/{emp_id}")
async def adjust_position(...)  # Ajuste manual

@router.get("/snapshots/{id}/quadrant/{quadrant}")
async def get_quadrant_employees(...)

# Análise
@router.get("/snapshots/{id}/movements")
async def get_movements(...)  # Movimentações vs anterior

@router.get("/snapshots/{id}/distribution")
async def get_distribution(...)  # Distribuição por quadrante

@router.get("/snapshots/{id}/high-potentials")
async def get_high_potentials(...)

@router.get("/snapshots/{id}/at-risk")
async def get_at_risk_employees(...)

# Ações
@router.get("/snapshots/{id}/positions/{emp_id}/actions")
async def get_employee_actions(...)

@router.post("/snapshots/{id}/positions/{emp_id}/actions")
async def add_action(...)

@router.put("/actions/{action_id}")
async def update_action(...)

# Histórico
@router.get("/employees/{emp_id}/history")
async def get_employee_history(...)  # Histórico de posições

# Exportação
@router.get("/snapshots/{id}/export")
async def export_snapshot(...)  # PDF/Excel
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard Nine Box** (`/rh/nine-box`)
   - Matriz visual interativa
   - Filtros (departamento, cargo)
   - Legenda e estatísticas

2. **Configurar Snapshot** (`/rh/nine-box/novo`)
   - Seleção de ciclo de avaliação
   - Configuração de thresholds
   - Pesos de potencial

3. **Funcionário no Nine Box** (`/rh/nine-box/funcionario/{id}`)
   - Posição atual
   - Histórico de movimentações
   - Ações sugeridas/em andamento

4. **Análise por Quadrante** (`/rh/nine-box/quadrante/{num}`)
   - Lista de funcionários
   - Ações em massa
   - Estatísticas

### Componentes React

```typescript
// components/nine-box/
├── NineBoxMatrix.tsx      // Matriz 3x3 interativa
├── EmployeeCard.tsx       // Card do funcionário na matriz
├── QuadrantDetails.tsx    // Detalhes do quadrante
├── MovementIndicator.tsx  // Seta de movimentação
├── PositionHistory.tsx    // Histórico de posições
├── ActionsList.tsx        // Lista de ações
├── ThresholdConfig.tsx    // Configurador de thresholds
├── PotentialWeights.tsx   // Configurador de pesos
├── DistributionChart.tsx  // Gráfico de distribuição
└── ExportButton.tsx       // Botão de exportação
```

---

## CÁLCULO DE POTENCIAL

```python
class PotentialCalculator:
    """
    Calcula score de potencial do funcionário.
    """

    async def calculate(
        self,
        employee: Employee,
        weights: Dict[str, float]
    ) -> PotentialScore:
        """
        Fatores e cálculo:

        1. DISC (0-5): Adaptabilidade do perfil
           - DI, ID = 5 (mais adaptáveis)
           - DC, CD, IS, SI = 4
           - D, I = 3.5
           - SC, CS = 3
           - S, C = 2.5

        2. IDADE (0-5): Fase de carreira
           - 20-30 = 5 (início, alto potencial)
           - 30-40 = 4.5
           - 40-50 = 3.5
           - 50+ = 2.5 (ajustar por cargo)

        3. FORMAÇÃO (0-5):
           - Doutorado = 5
           - Mestrado = 4.5
           - Pós/MBA = 4
           - Superior = 3.5
           - Técnico = 3
           - Médio = 2

        4. HISTÓRICO (0-5): Promoções e movimentações
           - 3+ promoções em 5 anos = 5
           - 2 promoções = 4
           - 1 promoção = 3
           - Nenhuma = 2

        5. LIDERANÇA (0-5): Indicação do gestor
           - Resposta direta: 1-5

        6. APRENDIZADO (0-5): Velocidade de adaptação
           - Cursos concluídos / ano
           - Novas responsabilidades assumidas
        """
        scores = {}

        scores['disc'] = self._score_disc(employee.disc_profile)
        scores['idade'] = self._score_idade(employee.data_nascimento)
        scores['formacao'] = self._score_formacao(employee.escolaridade)
        scores['historico'] = await self._score_historico(employee.id)
        scores['lideranca'] = employee.indicacao_lideranca or 3.0
        scores['aprendizado'] = await self._score_aprendizado(employee.id)

        # Média ponderada
        total = sum(scores[k] * weights.get(k, 0) for k in scores)
        total_weight = sum(weights.get(k, 0) for k in scores)

        return PotentialScore(
            score=round(total / total_weight, 2),
            breakdown=scores,
            level=self._classify_level(total / total_weight)
        )

    def _classify_level(self, score: float) -> str:
        if score >= 3.5:
            return 'ALTO'
        elif score >= 2.5:
            return 'MEDIO'
        return 'BAIXO'
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-nine-box
description: Gerencia matriz Nine Box de talentos
version: 1.0.0

triggers:
  - "criar nine box"
  - "calcular potencial"
  - "talentos em risco"
  - "high potentials"

prompts:
  create_snapshot:
    description: Cria novo snapshot do Nine Box
    template: |
      Crie snapshot Nine Box:
      1. Use dados do ciclo de avaliação mais recente
      2. Calcule potencial de todos funcionários
      3. Classifique em quadrantes
      4. Identifique movimentações vs snapshot anterior
      5. Sugira ações por quadrante

  analyze_quadrant:
    description: Analisa quadrante específico
    parameters:
      - quadrant: 1-9
    template: |
      Analise quadrante {quadrant}:
      1. Liste todos funcionários
      2. Identifique padrões (departamento, cargo, tempo de casa)
      3. Priorize por risco/oportunidade
      4. Sugira ações específicas
      5. Estime investimento necessário

  retention_plan:
    description: Plano de retenção para talentos
    template: |
      Crie plano de retenção:
      1. Identifique funcionários quadrantes 6, 8, 9
      2. Calcule risco de turnover
      3. Priorize por criticidade
      4. Sugira ações personalizadas
      5. Estime custo vs custo de reposição

agents:
  - TalentsAgent
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models: snapshots, positions, actions
  - [ ] PotentialCalculator
  - [ ] TalentsAgent (parcial - Nine Box)
  - [ ] Controllers
  - [ ] Integração com 360°

- [ ] **Frontend**
  - [ ] Matriz interativa (drag & drop)
  - [ ] Cards de funcionário
  - [ ] Histórico de movimentações
  - [ ] Configurador de thresholds
  - [ ] Export PDF/Excel

- [ ] **Integrações**
  - [ ] Avaliação 360° (performance)
  - [ ] DISC (potencial)
  - [ ] PDI (ações)
  - [ ] Sucessão (alimentar)

- [ ] **Testes**
  - [ ] Unitários (PotentialCalculator)
  - [ ] Integração
  - [ ] Visual (matriz)

---

**Próximo módulo:** [MÓDULO 05: PDI](./MODULO_05_PDI.md)
