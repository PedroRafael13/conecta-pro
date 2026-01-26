# MÓDULO 01: PESQUISA DE CLIMA ORGANIZACIONAL

**Sprint:** 34-35
**Prioridade:** 1 (CRÍTICO)
**Esforço:** 2 sprints
**Dependências:** Módulo de funcionários, sistema de notificações

---

## VISÃO GERAL

O módulo de Pesquisa de Clima Organizacional permite criar, distribuir e analisar pesquisas para medir o engajamento e satisfação dos colaboradores.

### Funcionalidades Principais

1. **Builder de Questionários**
   - Drag & drop de perguntas
   - Templates pré-definidos
   - Tipos: Likert, múltipla escolha, texto livre
   - Categorias: Liderança, Ambiente, Carreira, Comunicação, Benefícios

2. **Distribuição Inteligente**
   - Por departamento, cargo, unidade
   - Agendamento de envio
   - Lembretes automáticos
   - Multi-canal (email, push, SMS)

3. **Coleta de Respostas**
   - Interface mobile-first
   - Anonimato garantido (quando configurado)
   - Progresso salvo automaticamente
   - Tempo médio de resposta

4. **Análise com IA**
   - Análise de sentimento em respostas abertas
   - Topic modeling para temas recorrentes
   - Detecção de áreas críticas
   - ENPS (Employee Net Promoter Score)
   - Comparativo histórico e benchmark

5. **Plano de Ação**
   - Geração automática de ações por IA
   - Atribuição de responsáveis
   - Acompanhamento de execução
   - Medição de impacto

---

## AGENTE DE IA: ClimaAgent

### Capabilities

```python
class ClimaAgent:
    """
    Agente especializado em análise de clima organizacional.
    """

    # 1. Análise de Sentimento
    async def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Analisa sentimento de resposta aberta.
        Retorna: positivo/neutro/negativo + score + emoções detectadas
        """

    # 2. Extração de Temas
    async def extract_topics(self, responses: List[str]) -> List[Topic]:
        """
        Extrai temas recorrentes das respostas usando BERTopic.
        Retorna: lista de temas com frequência e exemplos
        """

    # 3. Detecção de Áreas Críticas
    async def detect_critical_areas(
        self,
        survey_results: SurveyResults
    ) -> List[CriticalArea]:
        """
        Identifica áreas com score < 3.0 ou tendência negativa.
        Retorna: lista de áreas com severidade e recomendação
        """

    # 4. Cálculo de ENPS
    async def calculate_enps(self, scores: List[int]) -> ENPSResult:
        """
        Calcula Employee Net Promoter Score.
        Promotores (9-10) - Detratores (0-6) = ENPS
        """

    # 5. Geração de Plano de Ação
    async def generate_action_plan(
        self,
        critical_areas: List[CriticalArea]
    ) -> ActionPlan:
        """
        Gera plano de ação baseado em IA.
        Inclui: ações, responsáveis sugeridos, prazo, KPIs
        """

    # 6. Comparativo e Benchmark
    async def compare_benchmark(
        self,
        results: SurveyResults,
        industry: str
    ) -> BenchmarkComparison:
        """
        Compara com benchmark do setor.
        """
```

### Prompts do Agente

```python
# prompts/clima_prompts.py

SENTIMENT_ANALYSIS_PROMPT = """
Analise o sentimento da seguinte resposta de pesquisa de clima:

Resposta: {response}

Retorne em JSON:
{
    "sentiment": "positivo|neutro|negativo",
    "score": 0.0 a 1.0,
    "emotions": ["satisfação", "frustração", ...],
    "key_points": ["ponto 1", "ponto 2"],
    "action_needed": true|false
}
"""

ACTION_PLAN_PROMPT = """
Com base nas áreas críticas identificadas na pesquisa de clima:

{critical_areas}

Gere um plano de ação estruturado com:
1. Ações imediatas (próximos 30 dias)
2. Ações de médio prazo (60-90 dias)
3. Ações estruturais (próximo ciclo)

Para cada ação, inclua:
- Descrição clara
- Responsável sugerido (cargo)
- Prazo
- KPI de sucesso
- Investimento estimado (baixo/médio/alto)
"""
```

---

## SCHEMA DO BANCO DE DADOS

```sql
-- Pesquisas
CREATE TABLE hr_climate_surveys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) DEFAULT 'GERAL', -- GERAL, PULSO, SAIDA, ONBOARDING
    status VARCHAR(20) DEFAULT 'RASCUNHO', -- RASCUNHO, ATIVO, ENCERRADO, ARQUIVADO
    anonimo BOOLEAN DEFAULT true,
    data_inicio TIMESTAMP,
    data_fim TIMESTAMP,
    tempo_estimado_min INT DEFAULT 10,
    condominio_id UUID NOT NULL REFERENCES condominios(id),
    criado_por UUID REFERENCES users(id),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,

    CONSTRAINT chk_datas CHECK (data_fim > data_inicio)
);

-- Perguntas
CREATE TABLE hr_climate_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES hr_climate_surveys(id) ON DELETE CASCADE,
    categoria VARCHAR(50) NOT NULL, -- LIDERANCA, AMBIENTE, CARREIRA, COMUNICACAO, BENEFICIOS
    texto TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL, -- LIKERT, MULTIPLA, ABERTA, ENPS
    ordem INT NOT NULL,
    obrigatoria BOOLEAN DEFAULT true,
    opcoes JSONB, -- Para múltipla escolha
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_ordem CHECK (ordem >= 0)
);

-- Respostas
CREATE TABLE hr_climate_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES hr_climate_surveys(id),
    question_id UUID NOT NULL REFERENCES hr_climate_questions(id),
    funcionario_id UUID REFERENCES funcionarios(id), -- NULL se anônimo
    session_id UUID NOT NULL, -- Para agrupar respostas anônimas
    valor_numerico INT,
    valor_texto TEXT,
    respondido_em TIMESTAMP DEFAULT NOW(),
    tempo_resposta_ms INT,
    dispositivo VARCHAR(50),

    CONSTRAINT chk_valor CHECK (
        (valor_numerico IS NOT NULL) OR (valor_texto IS NOT NULL)
    )
);

-- Análises (cache de resultados)
CREATE TABLE hr_climate_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES hr_climate_surveys(id),
    tipo VARCHAR(50) NOT NULL, -- GERAL, POR_DEPARTAMENTO, POR_CARGO
    filtro JSONB,
    resultado JSONB NOT NULL,
    enps_score INT,
    taxa_resposta DECIMAL(5,2),
    analisado_em TIMESTAMP DEFAULT NOW(),
    modelo_ia VARCHAR(100)
);

-- Planos de Ação
CREATE TABLE hr_climate_action_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_id UUID NOT NULL REFERENCES hr_climate_surveys(id),
    analysis_id UUID REFERENCES hr_climate_analyses(id),
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    area_critica VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDENTE',
    prioridade VARCHAR(20) DEFAULT 'MEDIA',
    responsavel_id UUID REFERENCES funcionarios(id),
    prazo DATE,
    kpi_sucesso TEXT,
    resultado_obtido TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    concluido_em TIMESTAMP
);

-- Índices
CREATE INDEX idx_climate_surveys_condominio ON hr_climate_surveys(condominio_id);
CREATE INDEX idx_climate_surveys_status ON hr_climate_surveys(status);
CREATE INDEX idx_climate_responses_survey ON hr_climate_responses(survey_id);
CREATE INDEX idx_climate_responses_session ON hr_climate_responses(session_id);
```

---

## API ENDPOINTS

```python
# /backend/modules/hr_advanced/clima/controllers.py

router = APIRouter(prefix="/climate", tags=["Clima Organizacional"])

# CRUD Pesquisas
@router.get("/surveys", response_model=PaginatedResponse[SurveyListResponse])
async def list_surveys(...)

@router.post("/surveys", response_model=SurveyResponse, status_code=201)
async def create_survey(...)

@router.get("/surveys/{survey_id}", response_model=SurveyDetailResponse)
async def get_survey(...)

@router.put("/surveys/{survey_id}", response_model=SurveyResponse)
async def update_survey(...)

@router.delete("/surveys/{survey_id}", status_code=204)
async def delete_survey(...)

# Gerenciamento de Perguntas
@router.get("/surveys/{survey_id}/questions", response_model=List[QuestionResponse])
async def list_questions(...)

@router.post("/surveys/{survey_id}/questions", response_model=QuestionResponse)
async def add_question(...)

@router.put("/surveys/{survey_id}/questions/{question_id}")
async def update_question(...)

@router.delete("/surveys/{survey_id}/questions/{question_id}")
async def remove_question(...)

@router.post("/surveys/{survey_id}/questions/reorder")
async def reorder_questions(...)

# Distribuição e Coleta
@router.post("/surveys/{survey_id}/distribute")
async def distribute_survey(...)

@router.post("/surveys/{survey_id}/remind")
async def send_reminders(...)

@router.get("/surveys/{survey_id}/respond")
async def get_survey_for_response(...)  # Endpoint público/anônimo

@router.post("/surveys/{survey_id}/respond")
async def submit_response(...)

# Análise e Resultados
@router.get("/surveys/{survey_id}/results")
async def get_results(...)

@router.post("/surveys/{survey_id}/analyze")
async def trigger_analysis(...)  # Dispara análise de IA

@router.get("/surveys/{survey_id}/enps")
async def get_enps(...)

@router.get("/surveys/{survey_id}/sentiment")
async def get_sentiment_analysis(...)

# Plano de Ação
@router.post("/surveys/{survey_id}/action-plan/generate")
async def generate_action_plan(...)

@router.get("/surveys/{survey_id}/action-plan")
async def get_action_plan(...)

@router.put("/action-plans/{plan_id}")
async def update_action_plan(...)
```

---

## INTERFACE DO USUÁRIO

### Páginas

1. **Dashboard de Clima** (`/rh/clima`)
   - Cards: pesquisas ativas, ENPS médio, taxa de resposta
   - Gráfico de evolução histórica
   - Alertas de áreas críticas

2. **Builder de Pesquisa** (`/rh/clima/criar`)
   - Drag & drop de perguntas
   - Preview em tempo real
   - Templates disponíveis

3. **Gerenciar Pesquisa** (`/rh/clima/{id}`)
   - Status e progresso
   - Distribuição
   - Lembretes

4. **Resultados** (`/rh/clima/{id}/resultados`)
   - Dashboard interativo
   - Filtros por departamento, cargo
   - Análise de sentimento
   - Word cloud de temas
   - ENPS gauge

5. **Plano de Ação** (`/rh/clima/{id}/acoes`)
   - Lista de ações geradas
   - Status de cada ação
   - Responsáveis e prazos

6. **Responder Pesquisa** (`/responder/{token}`)
   - Interface pública/anônima
   - Mobile-first
   - Progresso salvo

### Componentes React

```typescript
// components/clima/
├── SurveyBuilder.tsx      // Drag & drop builder
├── QuestionCard.tsx       // Card de pergunta editável
├── SurveyPreview.tsx      // Preview da pesquisa
├── ResponseForm.tsx       // Formulário de resposta
├── ResultsDashboard.tsx   // Dashboard de resultados
├── ENPSGauge.tsx          // Gauge do ENPS
├── SentimentChart.tsx     // Gráfico de sentimento
├── TopicsWordCloud.tsx    // Word cloud de temas
├── ActionPlanList.tsx     // Lista de ações
├── ActionPlanCard.tsx     // Card de ação individual
└── DistributionModal.tsx  // Modal de distribuição
```

---

## SKILL DO CLAUDE CODE

```yaml
# /root/.claude/skills/hr-clima.yaml
name: hr-clima
description: Cria e analisa pesquisas de clima organizacional
version: 1.0.0

triggers:
  - "criar pesquisa de clima"
  - "analisar clima"
  - "gerar plano de ação clima"

prompts:
  create:
    description: Cria nova pesquisa de clima
    template: |
      Crie uma pesquisa de clima organizacional completa:

      1. Título e descrição
      2. Perguntas por categoria:
         - Liderança (3-5 perguntas)
         - Ambiente de trabalho (3-5 perguntas)
         - Carreira e desenvolvimento (3-5 perguntas)
         - Comunicação (2-3 perguntas)
         - Benefícios (2-3 perguntas)
      3. Pergunta ENPS obrigatória
      4. 2-3 perguntas abertas

      Use escala Likert 1-5 para perguntas fechadas.

  analyze:
    description: Analisa resultados de pesquisa
    parameters:
      - survey_id: UUID da pesquisa
    template: |
      Analise os resultados da pesquisa {survey_id}:

      1. Calcule médias por categoria
      2. Identifique pontos críticos (score < 3.0)
      3. Analise sentimento das respostas abertas
      4. Extraia temas recorrentes
      5. Compare com pesquisa anterior (se houver)
      6. Calcule ENPS
      7. Sugira 5 ações prioritárias

  action_plan:
    description: Gera plano de ação
    parameters:
      - analysis_id: UUID da análise
    template: |
      Com base na análise {analysis_id}, gere plano de ação:

      Para cada área crítica:
      1. Ação recomendada
      2. Responsável sugerido (por cargo)
      3. Prazo realista
      4. KPI de sucesso
      5. Investimento estimado

agents:
  - ClimaAgent
  - SurveyAgent

tools:
  - documentKitsService
  - notificationService
```

---

## TESTES

```python
# tests/unit/test_clima_service.py

class TestClimaService:
    async def test_create_survey(self):
        """Testa criação de pesquisa."""
        survey = await clima_service.create_survey(
            nome="Pesquisa Q1 2026",
            tipo="GERAL",
            anonimo=True,
            condominio_id=TEST_CONDOMINIO_ID
        )
        assert survey.id is not None
        assert survey.status == "RASCUNHO"

    async def test_calculate_enps(self):
        """Testa cálculo de ENPS."""
        responses = [10, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        # Promotores: 3 (10, 10, 9)
        # Neutros: 2 (8, 7)
        # Detratores: 5 (6, 5, 4, 3, 2)
        # ENPS = (3/10 - 5/10) * 100 = -20
        result = clima_service.calculate_enps(responses)
        assert result.score == -20
        assert result.promotores == 3
        assert result.detratores == 5

    async def test_sentiment_analysis(self):
        """Testa análise de sentimento."""
        text = "O ambiente de trabalho é ótimo, mas a comunicação precisa melhorar."
        result = await clima_agent.analyze_sentiment(text)
        assert result.sentiment == "neutro"
        assert "comunicação" in result.key_points
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

- [ ] **Backend**
  - [ ] Criar models SQLAlchemy
  - [ ] Criar schemas Pydantic
  - [ ] Implementar repository
  - [ ] Implementar service
  - [ ] Implementar controllers
  - [ ] Configurar rotas

- [ ] **Agente de IA**
  - [ ] Implementar ClimaAgent
  - [ ] Configurar modelo de sentimento
  - [ ] Implementar topic modeling
  - [ ] Criar prompts

- [ ] **Frontend**
  - [ ] Dashboard de clima
  - [ ] Survey builder (drag & drop)
  - [ ] Página de resposta
  - [ ] Dashboard de resultados
  - [ ] Plano de ação

- [ ] **Integrações**
  - [ ] Notificações (email, push)
  - [ ] Export PDF/Excel
  - [ ] API pública para resposta

- [ ] **Testes**
  - [ ] Testes unitários
  - [ ] Testes de integração
  - [ ] Testes E2E

---

**Próximo módulo:** [MÓDULO 02: DISC](./MODULO_02_DISC.md)
