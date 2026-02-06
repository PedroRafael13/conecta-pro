# MÓDULO 02: AVALIAÇÃO COMPORTAMENTAL DISC

**Sprint:** 36-37
**Prioridade:** 2 (CRÍTICO)
**Esforço:** 2 sprints
**Dependências:** Módulo de funcionários

---

## VISÃO GERAL

O módulo DISC permite avaliar o perfil comportamental dos colaboradores usando a metodologia DISC (Dominância, Influência, Estabilidade, Conformidade).

### O que é DISC?

O DISC é uma ferramenta de avaliação comportamental que classifica pessoas em 4 dimensões:

| Dimensão | Característica | Foco |
|----------|---------------|------|
| **D** - Dominância | Direto, Decisivo, Competitivo | Resultados |
| **I** - Influência | Entusiasta, Otimista, Colaborativo | Pessoas |
| **S** - Estabilidade | Paciente, Confiável, Leal | Ritmo |
| **C** - Conformidade | Analítico, Preciso, Sistemático | Processos |

### Funcionalidades Principais

1. **Aplicação do Teste**
   - 48 perguntas de escolha forçada
   - Tempo médio: 15-20 minutos
   - Versão adaptativa com IA (reduz para 24-32 perguntas)

2. **Cálculo do Perfil**
   - Perfil Natural (quem você é)
   - Perfil Adaptado (como você age no trabalho)
   - Intensidade de cada dimensão
   - Combinações (DI, IS, SC, CD, etc.)

3. **Interpretação com IA**
   - Pontos fortes
   - Áreas de desenvolvimento
   - Estilo de comunicação
   - Estilo de liderança
   - Ambiente ideal de trabalho
   - Como lidar com estresse

4. **Relatórios**
   - Relatório individual em PDF
   - Relatório de equipe
   - Matriz de compatibilidade
   - Sugestões de desenvolvimento

5. **Integração**
   - Match com requisitos de cargo
   - Dinâmica de equipe
   - Processo seletivo
   - PDI

---

## AGENTE DE IA: DISCAgent

```python
class DISCAgent:
    """
    Agente especializado em avaliação comportamental DISC.
    """

    def __init__(self):
        self.disc_calculator = DISCCalculator()
        self.interpretation_llm = "claude-3-opus"  # ou local
        self.question_bank = self._load_question_bank()

    # 1. Cálculo do Perfil
    async def calculate_profile(
        self,
        responses: List[DISCResponse]
    ) -> DISCProfile:
        """
        Calcula perfil DISC a partir das respostas.

        Retorna:
        - dominancia: 0-100
        - influencia: 0-100
        - estabilidade: 0-100
        - conformidade: 0-100
        - perfil_natural: "DI", "IS", "SC", "CD", etc.
        - perfil_adaptado: "DI", "IS", etc.
        - intensidade: "BAIXA", "MEDIA", "ALTA"
        """

    # 2. Interpretação do Perfil
    async def interpret_profile(
        self,
        profile: DISCProfile
    ) -> DISCInterpretation:
        """
        Gera interpretação detalhada do perfil.

        Retorna:
        - resumo_executivo
        - pontos_fortes
        - areas_desenvolvimento
        - estilo_comunicacao
        - estilo_lideranca
        - ambiente_ideal
        - sob_pressao
        - dicas_gestao (para o gestor)
        """

    # 3. Match com Cargo
    async def match_job_profile(
        self,
        candidate_profile: DISCProfile,
        job_profile: JobDISCProfile
    ) -> ProfileMatch:
        """
        Calcula compatibilidade entre perfil e cargo.

        Retorna:
        - fit_score: 0-100
        - matches: dimensões que combinam
        - gaps: dimensões com diferença significativa
        - adaptacao_necessaria: nível de adaptação
        - recomendacao: texto
        """

    # 4. Dinâmica de Equipe
    async def team_dynamics(
        self,
        team_profiles: List[DISCProfile]
    ) -> TeamDynamics:
        """
        Analisa dinâmica da equipe.

        Retorna:
        - distribuicao: % de cada perfil
        - equilibrio: pontuação de equilíbrio
        - pontos_fortes_equipe
        - lacunas_equipe
        - potenciais_conflitos
        - sugestoes_melhoria
        """

    # 5. Teste Adaptativo
    async def get_next_question(
        self,
        responses: List[DISCResponse]
    ) -> DISCQuestion:
        """
        Retorna próxima pergunta baseada nas respostas anteriores.
        Usa IA para reduzir número de perguntas mantendo precisão.
        """

    # 6. Geração de Relatório
    async def generate_report(
        self,
        profile: DISCProfile,
        interpretation: DISCInterpretation
    ) -> bytes:
        """
        Gera relatório PDF completo.
        """
```

### Algoritmo DISC

```python
# /backend/modules/hr_advanced/disc/algorithm.py

class DISCCalculator:
    """
    Calculadora do perfil DISC.

    O questionário DISC usa perguntas de escolha forçada onde o
    respondente escolhe a opção "mais" e "menos" como ele.
    """

    # Pesos base para cada dimensão
    DIMENSION_WEIGHTS = {
        'D': {'most': 2, 'least': -1},
        'I': {'most': 2, 'least': -1},
        'S': {'most': 2, 'least': -1},
        'C': {'most': 2, 'least': -1},
    }

    def calculate(
        self,
        responses: List[DISCResponse]
    ) -> DISCProfile:
        """
        Calcula o perfil DISC.

        Cada resposta tem:
        - questao_numero: 1-48
        - resposta_mais: D, I, S ou C
        - resposta_menos: D, I, S ou C
        """
        scores = {'D': 0, 'I': 0, 'S': 0, 'C': 0}

        for response in responses:
            # Soma para "mais como eu"
            scores[response.resposta_mais] += self.DIMENSION_WEIGHTS[response.resposta_mais]['most']
            # Subtrai para "menos como eu"
            scores[response.resposta_menos] += self.DIMENSION_WEIGHTS[response.resposta_menos]['least']

        # Normaliza para 0-100
        total = sum(scores.values())
        normalized = {k: max(0, (v / total) * 100) for k, v in scores.items()}

        # Determina perfil principal
        sorted_dims = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        perfil_natural = sorted_dims[0][0] + sorted_dims[1][0]

        # Calcula intensidade
        max_score = sorted_dims[0][1]
        intensidade = 'ALTA' if max_score > 60 else 'MEDIA' if max_score > 40 else 'BAIXA'

        return DISCProfile(
            dominancia=round(normalized['D'], 1),
            influencia=round(normalized['I'], 1),
            estabilidade=round(normalized['S'], 1),
            conformidade=round(normalized['C'], 1),
            perfil_natural=perfil_natural,
            intensidade=intensidade
        )

    def calculate_adapted_profile(
        self,
        responses: List[DISCResponse],
        context: str = 'work'
    ) -> DISCProfile:
        """
        Calcula perfil adaptado (como age no trabalho).
        Usa subset de perguntas focadas em contexto profissional.
        """
        work_questions = [q for q in responses if q.questao_numero in WORK_CONTEXT_QUESTIONS]
        return self.calculate(work_questions)
```

---

## QUESTIONÁRIO DISC

```python
# /backend/modules/hr_advanced/disc/questionnaire.py

DISC_QUESTIONS = [
    {
        "numero": 1,
        "grupo": [
            {"letra": "D", "texto": "Gosto de assumir o controle"},
            {"letra": "I", "texto": "Gosto de interagir com pessoas"},
            {"letra": "S", "texto": "Prefiro um ambiente estável"},
            {"letra": "C", "texto": "Valorizo precisão e detalhes"}
        ]
    },
    {
        "numero": 2,
        "grupo": [
            {"letra": "D", "texto": "Sou competitivo"},
            {"letra": "I", "texto": "Sou entusiasta"},
            {"letra": "S", "texto": "Sou paciente"},
            {"letra": "C", "texto": "Sou analítico"}
        ]
    },
    # ... 48 perguntas no total
]

# Perguntas focadas em contexto de trabalho (para perfil adaptado)
WORK_CONTEXT_QUESTIONS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Avaliações DISC
CREATE TABLE hr_disc_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    tipo VARCHAR(20) DEFAULT 'COMPLETO', -- COMPLETO, ADAPTATIVO, RAPIDO
    status VARCHAR(20) DEFAULT 'PENDENTE', -- PENDENTE, EM_ANDAMENTO, CONCLUIDO, EXPIRADO
    motivo VARCHAR(50), -- ADMISSAO, PROMOCAO, DESENVOLVIMENTO, EQUIPE
    iniciado_em TIMESTAMP,
    concluido_em TIMESTAMP,
    tempo_total_min INT,
    versao INT DEFAULT 1,
    valido_ate DATE,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    criado_por UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Respostas do teste
CREATE TABLE hr_disc_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES hr_disc_assessments(id) ON DELETE CASCADE,
    questao_numero INT NOT NULL,
    resposta_mais CHAR(1) NOT NULL CHECK (resposta_mais IN ('D', 'I', 'S', 'C')),
    resposta_menos CHAR(1) NOT NULL CHECK (resposta_menos IN ('D', 'I', 'S', 'C')),
    tempo_resposta_ms INT,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_diferentes CHECK (resposta_mais != resposta_menos),
    UNIQUE(assessment_id, questao_numero)
);

-- Perfis calculados
CREATE TABLE hr_disc_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES hr_disc_assessments(id),
    funcionario_id UUID NOT NULL REFERENCES funcionarios(id),
    tipo VARCHAR(20) NOT NULL, -- NATURAL, ADAPTADO

    -- Scores 0-100
    dominancia DECIMAL(5,2) NOT NULL,
    influencia DECIMAL(5,2) NOT NULL,
    estabilidade DECIMAL(5,2) NOT NULL,
    conformidade DECIMAL(5,2) NOT NULL,

    -- Classificação
    perfil_codigo VARCHAR(4) NOT NULL, -- DI, IS, SC, CD, D, I, S, C, etc.
    intensidade VARCHAR(20) NOT NULL, -- BAIXA, MEDIA, ALTA

    -- Interpretação (gerada por IA)
    interpretacao JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_total CHECK (
        dominancia + influencia + estabilidade + conformidade BETWEEN 99 AND 101
    )
);

-- Perfis ideais por cargo
CREATE TABLE hr_disc_job_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cargo_id UUID NOT NULL REFERENCES cargos(id),
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,

    -- Ranges ideais
    dominancia_min DECIMAL(5,2) DEFAULT 0,
    dominancia_max DECIMAL(5,2) DEFAULT 100,
    influencia_min DECIMAL(5,2) DEFAULT 0,
    influencia_max DECIMAL(5,2) DEFAULT 100,
    estabilidade_min DECIMAL(5,2) DEFAULT 0,
    estabilidade_max DECIMAL(5,2) DEFAULT 100,
    conformidade_min DECIMAL(5,2) DEFAULT 0,
    conformidade_max DECIMAL(5,2) DEFAULT 100,

    perfis_ideais VARCHAR(20)[], -- ['DI', 'DC', 'ID']
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    UNIQUE(cargo_id)
);

-- Índices
CREATE INDEX idx_disc_assessments_funcionario ON hr_disc_assessments(funcionario_id);
CREATE INDEX idx_disc_assessments_status ON hr_disc_assessments(status);
CREATE INDEX idx_disc_profiles_funcionario ON hr_disc_profiles(funcionario_id);
CREATE INDEX idx_disc_profiles_perfil ON hr_disc_profiles(perfil_codigo);
```

---

## API ENDPOINTS

```python
router = APIRouter(prefix="/disc", tags=["Avaliação DISC"])

# CRUD Avaliações
@router.post("/assessments", response_model=AssessmentResponse, status_code=201)
async def create_assessment(...)  # Cria nova avaliação para funcionário

@router.get("/assessments", response_model=PaginatedResponse[AssessmentListResponse])
async def list_assessments(...)

@router.get("/assessments/{id}", response_model=AssessmentDetailResponse)
async def get_assessment(...)

@router.delete("/assessments/{id}", status_code=204)
async def cancel_assessment(...)

# Aplicação do Teste
@router.get("/assessments/{id}/start")
async def start_assessment(...)  # Inicia o teste

@router.get("/assessments/{id}/questions/{numero}")
async def get_question(...)  # Retorna pergunta específica

@router.post("/assessments/{id}/responses")
async def submit_response(...)  # Salva resposta

@router.post("/assessments/{id}/complete")
async def complete_assessment(...)  # Finaliza e calcula perfil

# Perfis
@router.get("/profiles/employee/{funcionario_id}")
async def get_employee_profile(...)  # Perfil mais recente

@router.get("/profiles/employee/{funcionario_id}/history")
async def get_profile_history(...)  # Histórico de perfis

@router.get("/profiles/team/{departamento_id}")
async def get_team_profiles(...)  # Perfis da equipe

# Interpretação e Relatórios
@router.get("/profiles/{id}/interpretation")
async def get_interpretation(...)

@router.get("/profiles/{id}/report")
async def generate_report(...)  # PDF

@router.get("/teams/{departamento_id}/dynamics")
async def get_team_dynamics(...)

# Match de Cargo
@router.post("/job-profiles", response_model=JobProfileResponse)
async def create_job_profile(...)

@router.get("/job-profiles/cargo/{cargo_id}")
async def get_job_profile(...)

@router.get("/match/employee/{funcionario_id}/cargo/{cargo_id}")
async def calculate_match(...)
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard DISC** (`/rh/disc`)
   - Testes pendentes
   - Distribuição de perfis na empresa
   - Alertas de validade

2. **Aplicar Teste** (`/rh/disc/aplicar`)
   - Seleção de funcionário(s)
   - Tipo de teste
   - Prazo

3. **Fazer Teste** (`/rh/disc/teste/{token}`)
   - Interface passo a passo
   - 48 perguntas com escolha forçada
   - Barra de progresso

4. **Perfil do Funcionário** (`/rh/disc/perfil/{id}`)
   - Gráfico radar DISC
   - Interpretação
   - Histórico
   - Download PDF

5. **Equipe** (`/rh/disc/equipe/{departamento_id}`)
   - Mapa de perfis
   - Dinâmica da equipe
   - Compatibilidades

6. **Perfis de Cargo** (`/rh/disc/cargos`)
   - CRUD de perfis ideais
   - Match com funcionários

### Componentes React

```typescript
// components/disc/
├── DISCRadarChart.tsx     // Gráfico radar do perfil
├── DISCBars.tsx           // Barras horizontais D-I-S-C
├── QuestionCard.tsx       // Card de pergunta com 4 opções
├── ProfileSummary.tsx     // Resumo do perfil
├── InterpretationCard.tsx // Card de interpretação
├── TeamMap.tsx            // Mapa visual da equipe
├── MatchGauge.tsx         // Gauge de compatibilidade
├── ProfileComparison.tsx  // Comparativo 2 perfis
└── AssessmentProgress.tsx // Progresso do teste
```

---

## SKILL DO CLAUDE CODE

```yaml
name: hr-disc
description: Aplica e interpreta avaliação comportamental DISC
version: 1.0.0

triggers:
  - "aplicar disc"
  - "interpretar perfil disc"
  - "compatibilidade disc"
  - "equipe disc"

prompts:
  apply:
    description: Inicia avaliação DISC
    parameters:
      - funcionario_id: UUID do funcionário
      - tipo: COMPLETO | ADAPTATIVO | RAPIDO
    template: |
      Inicie avaliação DISC para funcionário {funcionario_id}:
      1. Crie assessment no banco
      2. Envie notificação com link
      3. Configure prazo (7 dias padrão)

  interpret:
    description: Interpreta perfil DISC
    parameters:
      - profile_id: UUID do perfil
    template: |
      Interprete o perfil DISC {profile_id}:

      Com base nos scores D={d}, I={i}, S={s}, C={c}:

      1. Identifique o perfil principal
      2. Descreva pontos fortes
      3. Liste áreas de desenvolvimento
      4. Explique estilo de comunicação
      5. Descreva comportamento sob pressão
      6. Sugira ambiente ideal de trabalho
      7. Dê dicas para o gestor lidar com esse perfil

  match_job:
    description: Calcula fit com cargo
    parameters:
      - funcionario_id: UUID funcionário
      - cargo_id: UUID cargo
    template: |
      Calcule compatibilidade DISC:
      1. Carregue perfil do funcionário
      2. Carregue perfil ideal do cargo
      3. Compare dimensões
      4. Calcule fit score (0-100)
      5. Identifique gaps
      6. Recomende ações de adaptação

  team_analysis:
    description: Analisa dinâmica da equipe
    parameters:
      - departamento_id: UUID departamento
    template: |
      Analise equipe {departamento_id}:
      1. Carregue perfis de todos membros
      2. Calcule distribuição D-I-S-C
      3. Identifique lacunas de perfil
      4. Detecte potenciais conflitos
      5. Sugira melhorias na composição
      6. Recomende ajustes de comunicação

agents:
  - DISCAgent
```

---

## INTERPRETAÇÕES POR PERFIL

```python
# Biblioteca de interpretações base
DISC_INTERPRETATIONS = {
    "D": {
        "titulo": "Dominante",
        "resumo": "Orientado a resultados, direto e decisivo",
        "pontos_fortes": [
            "Toma decisões rapidamente",
            "Foco em resultados",
            "Assume riscos calculados",
            "Lidera sob pressão"
        ],
        "areas_desenvolvimento": [
            "Pode parecer impaciente",
            "Tendência a ignorar detalhes",
            "Pode ser percebido como autoritário"
        ],
        "estilo_comunicacao": "Direto, objetivo, sem rodeios",
        "sob_pressao": "Torna-se mais controlador e impaciente",
        "ambiente_ideal": "Desafiador, com autonomia e resultados mensuráveis",
        "dicas_gestao": [
            "Dê autonomia e desafios",
            "Seja direto e objetivo",
            "Reconheça conquistas",
            "Evite microgerenciamento"
        ]
    },
    "I": {
        "titulo": "Influente",
        "resumo": "Entusiasta, otimista e sociável",
        # ...
    },
    "S": {
        "titulo": "Estável",
        "resumo": "Paciente, leal e bom ouvinte",
        # ...
    },
    "C": {
        "titulo": "Conforme",
        "resumo": "Analítico, preciso e sistemático",
        # ...
    },
    # Combinações
    "DI": {
        "titulo": "Dominante-Influente",
        "resumo": "Líder carismático, persuasivo e orientado a resultados",
        # ...
    },
    # ... outras combinações
}
```

---

## TESTES

```python
class TestDISCCalculator:
    def test_balanced_profile(self):
        """Testa perfil equilibrado."""
        responses = self._generate_balanced_responses()
        profile = calculator.calculate(responses)

        assert 20 <= profile.dominancia <= 30
        assert 20 <= profile.influencia <= 30
        assert 20 <= profile.estabilidade <= 30
        assert 20 <= profile.conformidade <= 30
        assert profile.intensidade == "BAIXA"

    def test_high_d_profile(self):
        """Testa perfil alto D."""
        responses = self._generate_high_d_responses()
        profile = calculator.calculate(responses)

        assert profile.dominancia > 50
        assert profile.perfil_natural.startswith("D")
        assert profile.intensidade in ["MEDIA", "ALTA"]

    def test_profile_match(self):
        """Testa match com cargo."""
        candidate = DISCProfile(dominancia=70, influencia=20, estabilidade=5, conformidade=5)
        job = JobDISCProfile(dominancia_min=60, dominancia_max=100, ...)

        match = disc_agent.match_job_profile(candidate, job)
        assert match.fit_score > 80

    def test_team_dynamics(self):
        """Testa análise de equipe."""
        profiles = [
            DISCProfile(dominancia=70, ...),  # Líder D
            DISCProfile(influencia=60, ...),   # Comunicador I
            DISCProfile(estabilidade=70, ...),  # Executor S
            DISCProfile(conformidade=65, ...),  # Analista C
        ]

        dynamics = disc_agent.team_dynamics(profiles)
        assert dynamics.equilibrio > 80  # Equipe balanceada
        assert len(dynamics.lacunas_equipe) == 0
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Models SQLAlchemy
  - [ ] Schemas Pydantic
  - [ ] Repository
  - [ ] DISCCalculator (algoritmo)
  - [ ] DISCAgent (IA)
  - [ ] Controllers
  - [ ] Questionário 48 perguntas

- [ ] **Frontend**
  - [ ] Dashboard DISC
  - [ ] Interface do teste
  - [ ] Gráfico radar
  - [ ] Página de perfil
  - [ ] Análise de equipe
  - [ ] Gerador PDF

- [ ] **Integrações**
  - [ ] Match com recrutamento
  - [ ] PDI
  - [ ] Nine Box

- [ ] **Testes**
  - [ ] Unitários algoritmo
  - [ ] Integração API
  - [ ] E2E fluxo completo

---

**Próximo módulo:** [MÓDULO 03: AVALIAÇÃO 360°](./MODULO_03_360.md)
