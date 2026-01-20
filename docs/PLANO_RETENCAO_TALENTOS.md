# Módulo de Retenção de Talentos - Conecta PRO

## Executive Summary

**Problema:** R$ 144.000/ano em custos de turnover (36 demissões × R$ 4.000)
**Solução:** Sistema integrado de onboarding, clima, predição e perfil operacional
**Meta:** Reduzir turnover em 50% = Economia de R$ 72.000/ano
**Timeline:** 6-8 semanas para MVP

---

## PRE-MORTEM ANALYSIS 🔴

### O que pode dar errado e como prevenir:

#### 1. **Baixa Adesão ao Onboarding**
- **Risco:** Funcionários não completam checklist de integração
- **Impacto:** ALTO - Sistema inútil sem dados
- **Prevenção:**
  - Gamificação (progresso visual, badges)
  - Notificações push insistentes mas não invasivas
  - Vincular conclusão a liberação de benefícios
  - Supervisor recebe alerta se não completar
- **Mitigação:** Onboarding simplificado (máximo 10 min por etapa)

#### 2. **Respostas Falsas na Pesquisa de Clima**
- **Risco:** Funcionários respondem o que acham que RH quer ouvir
- **Impacto:** MÉDIO - Dados não confiáveis
- **Prevenção:**
  - Anonimato garantido (sem identificação em respostas)
  - Perguntas indiretas (não "você está feliz?")
  - Validação cruzada com dados objetivos (faltas, atrasos)
  - Escala par (4 opções) para evitar respostas neutras
- **Mitigação:** Peso maior para dados objetivos na predição

#### 3. **Modelo de IA com Viés**
- **Risco:** Predição discrimina por idade, gênero, região
- **Impacto:** CRÍTICO - Problemas legais e éticos
- **Prevenção:**
  - Não usar variáveis demográficas diretamente
  - Auditoria de fairness no modelo
  - Features baseadas apenas em comportamento observável
  - Validação com dados históricos reais
- **Mitigação:** Explicabilidade - mostrar fatores da predição

#### 4. **Falsos Positivos na Predição**
- **Risco:** Sistema alerta risco para funcionários satisfeitos
- **Impacto:** MÉDIO - Perda de credibilidade
- **Prevenção:**
  - Threshold conservador (alertar só acima de 70% risco)
  - Combinar múltiplas fontes de dados
  - Período de calibração de 3 meses
  - Feedback loop para melhorar modelo
- **Mitigação:** Ação é conversa, não decisão automática

#### 5. **Funcionário Descobre Score de Risco**
- **Risco:** Vazamento de que funcionário está "marcado"
- **Impacto:** ALTO - Desmotivação, processo trabalhista
- **Prevenção:**
  - Score visível apenas para RH/Gestão
  - Logs de acesso auditados
  - Treinamento sobre confidencialidade
  - Nunca mencionar score em conversas
- **Mitigação:** Termo de confidencialidade para quem acessa

#### 6. **Questionário de Perfil Muito Longo**
- **Risco:** Candidatos desistem no meio
- **Impacto:** MÉDIO - Dados incompletos
- **Prevenção:**
  - Máximo 20 perguntas (5-7 minutos)
  - Barra de progresso visível
  - Salvamento automático
  - Mobile-first (maioria vai responder no celular)
- **Mitigação:** Versão reduzida (10 perguntas) para casos urgentes

#### 7. **Match Funcionário-Posto Ignora Realidade**
- **Risco:** Algoritmo sugere alocação impossível (distância, horário)
- **Impacto:** MÉDIO - Sugestões ignoradas
- **Prevenção:**
  - Restrições hard (distância máxima, disponibilidade)
  - Score de match considera viabilidade operacional
  - Supervisor pode override com justificativa
- **Mitigação:** Ranking de opções, não decisão única

#### 8. **Sobrecarga de Alertas**
- **Risco:** RH recebe tantos alertas que ignora todos
- **Impacto:** ALTO - Sistema perde utilidade
- **Prevenção:**
  - Limite de alertas/dia (máximo 5)
  - Priorização por severidade
  - Agregação (não alertar cada evento, mas padrão)
  - Dashboard consolidado ao invés de notificações
- **Mitigação:** Configuração de thresholds por empresa

#### 9. **Dados Históricos Insuficientes**
- **Risco:** Modelo de IA não tem dados suficientes para treinar
- **Impacto:** ALTO - Predições ruins no início
- **Prevenção:**
  - Começar com regras heurísticas (sem ML)
  - Coletar dados por 3-6 meses antes de ML
  - Usar benchmarks do setor como baseline
  - Modelo híbrido (regras + ML quando tiver dados)
- **Mitigação:** Período de "shadow mode" (prediz mas não alerta)

#### 10. **Resistência da Gestão**
- **Risco:** Supervisores não usam o sistema
- **Impacto:** ALTO - Investimento perdido
- **Prevenção:**
  - Envolver gestão no design
  - Mostrar ROI com casos reais
  - Treinamento hands-on
  - KPIs de adoção por supervisor
- **Mitigação:** Começar com pilotos em equipes engajadas

---

## ARQUITETURA DO MÓDULO

```
/backend/modules/retention/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── onboarding.py          # OnboardingChecklist, OnboardingStep, OnboardingProgress
│   ├── climate.py             # ClimateSurvey, ClimateResponse, ClimateScore
│   ├── turnover.py            # TurnoverPrediction, RiskFactor, RiskAlert
│   └── profile.py             # OperationalProfile, ProfileDimension, PostMatch
├── schemas/
│   ├── __init__.py
│   ├── onboarding_schemas.py
│   ├── climate_schemas.py
│   ├── turnover_schemas.py
│   └── profile_schemas.py
├── services/
│   ├── __init__.py
│   ├── onboarding_service.py  # Gestão de checklists e progresso
│   ├── climate_service.py     # Aplicação e análise de pesquisas
│   ├── turnover_predictor.py  # Motor de predição com ML
│   └── profile_matcher.py     # Match funcionário-posto
├── controllers/
│   ├── __init__.py
│   ├── onboarding_controller.py
│   ├── climate_controller.py
│   ├── turnover_controller.py
│   └── profile_controller.py
└── ai/
    ├── __init__.py
    ├── turnover_model.py      # Modelo de ML para predição
    ├── risk_analyzer.py       # Análise de fatores de risco
    └── profile_analyzer.py    # Análise de perfil comportamental

/frontend/src/features/retention/
├── onboarding/
│   ├── OnboardingDashboard.tsx
│   ├── OnboardingChecklist.tsx
│   └── OnboardingProgress.tsx
├── climate/
│   ├── ClimateSurvey.tsx
│   ├── ClimateResults.tsx
│   └── ClimateDashboard.tsx
├── turnover/
│   ├── TurnoverDashboard.tsx
│   ├── RiskAlerts.tsx
│   └── EmployeeRiskDetail.tsx
├── profile/
│   ├── ProfileQuestionnaire.tsx
│   ├── ProfileResult.tsx
│   └── PostMatchSuggestions.tsx
└── index.ts
```

---

## FASE 1: ONBOARDING DIGITAL

### Objetivo
Estruturar os primeiros 90 dias de um funcionário para reduzir desistências precoces.

### Funcionalidades
1. **Checklist de Integração**
   - Etapas configuráveis por cargo/função
   - Marcos: 1° dia, 7 dias, 15 dias, 30 dias, 60 dias, 90 dias
   - Tarefas: documentos, treinamentos, apresentações, feedbacks

2. **Acompanhamento Automático**
   - Notificações para funcionário e supervisor
   - Escalação se etapa não completada
   - Questionário de adaptação em cada marco

3. **Dashboard de Onboarding**
   - Visão geral de todos em integração
   - Alertas de atraso
   - Métricas de conclusão

### Modelo de Dados
```python
class OnboardingChecklist:
    id, nome, cargo_id, ativo
    etapas: List[OnboardingStep]

class OnboardingStep:
    id, checklist_id, nome, descricao, dias_após_admissão
    tipo: documento | treinamento | feedback | tarefa
    obrigatório: bool

class OnboardingProgress:
    id, funcionario_id, checklist_id, step_id
    status: pendente | em_andamento | concluido | atrasado
    data_prevista, data_conclusao
    observacoes, supervisor_id
```

---

## FASE 2: PESQUISA DE CLIMA OPERACIONAL

### Objetivo
Medir satisfação e engajamento de forma contínua para detectar problemas cedo.

### Funcionalidades
1. **Pulso Mensal**
   - 5 perguntas rápidas (2 min para responder)
   - Escala 1-4 (sem opção neutra)
   - Anônimo mas rastreável por posto/equipe

2. **Perguntas Padrão**
   - Satisfação com posto atual
   - Relacionamento com supervisor
   - Carga de trabalho
   - Perspectiva de crescimento
   - Recomendaria empresa (eNPS)

3. **Análise e Alertas**
   - Score individual (para predição, não exibido)
   - Score por posto/equipe (exibido)
   - Tendência histórica
   - Alerta se score cair >20%

### Modelo de Dados
```python
class ClimateSurvey:
    id, nome, perguntas: List[str], ativo
    frequencia: semanal | quinzenal | mensal

class ClimateResponse:
    id, survey_id, funcionario_id (nullable para anonimato)
    posto_id, equipe_id, data_resposta
    respostas: Dict[pergunta_id, valor]
    score_calculado: float

class ClimateScore:
    id, entidade_tipo: funcionario | posto | equipe | empresa
    entidade_id, periodo, score, tendencia
    fatores_positivos, fatores_negativos
```

---

## FASE 3: PREDIÇÃO DE TURNOVER

### Objetivo
Identificar funcionários em risco de sair antes que peçam demissão.

### Features para o Modelo
```python
FEATURES = {
    # Comportamentais (peso alto)
    "faltas_ultimo_mes": float,
    "atrasos_ultimo_mes": float,
    "ocorrencias_ultimo_trimestre": int,
    "advertencias_total": int,

    # Engajamento (peso alto)
    "score_clima_atual": float,
    "tendencia_clima": float,  # positiva/negativa
    "dias_desde_ultima_pesquisa": int,

    # Operacionais (peso médio)
    "distancia_casa_posto_km": float,
    "horas_extras_media": float,
    "trocas_posto_ultimo_ano": int,
    "tempo_empresa_meses": int,

    # Contextuais (peso baixo)
    "dias_desde_ultimo_aumento": int,
    "dias_desde_ultima_promocao": int,
}
```

### Regras Heurísticas (antes do ML)
```python
def calcular_risco_heuristico(funcionario):
    score = 0

    # Faltas e atrasos
    if faltas_mes > 2: score += 20
    if atrasos_mes > 5: score += 15

    # Clima
    if score_clima < 2.5: score += 25
    if tendencia_clima < -0.5: score += 15

    # Histórico
    if advertencias > 0: score += 10 * advertencias
    if tempo_empresa < 3: score += 10  # Período crítico

    # Distância
    if distancia_km > 20: score += 10

    return min(score, 100)
```

### Modelo de Dados
```python
class TurnoverPrediction:
    id, funcionario_id, data_calculo
    score_risco: float (0-100)
    nivel: baixo | medio | alto | critico
    fatores: List[RiskFactor]
    modelo_versao: str

class RiskFactor:
    nome, peso, valor_atual, contribuicao_score
    descricao, recomendacao_acao

class RiskAlert:
    id, funcionario_id, prediction_id
    tipo: novo_risco | aumento_risco | risco_critico
    enviado_para: List[user_id]
    visualizado: bool, acao_tomada: str
```

---

## FASE 4: PERFIL OPERACIONAL

### Objetivo
Mapear perfil comportamental para melhor alocação em postos.

### Dimensões do Perfil
```
1. VIGILÂNCIA (0-100)
   - Atenção a detalhes
   - Capacidade de observação
   - Foco prolongado
   → Ideal para: CFTV, Monitoramento, Rondas

2. COMUNICAÇÃO (0-100)
   - Facilidade com público
   - Clareza na expressão
   - Empatia
   → Ideal para: Recepção, Portaria, Atendimento

3. RESILIÊNCIA (0-100)
   - Tolerância a pressão
   - Controle emocional
   - Recuperação de stress
   → Ideal para: Eventos, Postos de risco, Emergências

4. LIDERANÇA (0-100)
   - Iniciativa
   - Tomada de decisão
   - Influência sobre outros
   → Ideal para: Supervisor, Líder de equipe
```

### Questionário (20 perguntas)
```python
PERGUNTAS = [
    # Vigilância
    {"texto": "Quando assisto TV, costumo notar detalhes que outros não percebem", "dimensao": "vigilancia"},
    {"texto": "Consigo manter atenção em uma tarefa por horas sem distração", "dimensao": "vigilancia"},
    {"texto": "Percebo rapidamente quando algo está fora do lugar", "dimensao": "vigilancia"},
    {"texto": "Prefiro trabalhos que exigem observação cuidadosa", "dimensao": "vigilancia"},
    {"texto": "Sou bom em encontrar erros em documentos ou imagens", "dimensao": "vigilancia"},

    # Comunicação
    {"texto": "Me sinto confortável conversando com desconhecidos", "dimensao": "comunicacao"},
    {"texto": "Consigo explicar coisas complexas de forma simples", "dimensao": "comunicacao"},
    {"texto": "As pessoas costumam me procurar para desabafar", "dimensao": "comunicacao"},
    {"texto": "Gosto de trabalhar atendendo pessoas", "dimensao": "comunicacao"},
    {"texto": "Consigo manter a calma mesmo com pessoas difíceis", "dimensao": "comunicacao"},

    # Resiliência
    {"texto": "Mantenho a calma em situações de emergência", "dimensao": "resiliencia"},
    {"texto": "Recupero-me rapidamente de situações estressantes", "dimensao": "resiliencia"},
    {"texto": "Trabalho bem mesmo sob pressão de tempo", "dimensao": "resiliencia"},
    {"texto": "Não me abalo facilmente com críticas", "dimensao": "resiliencia"},
    {"texto": "Consigo tomar decisões difíceis sem hesitar muito", "dimensao": "resiliencia"},

    # Liderança
    {"texto": "Em grupos, naturalmente assumo a coordenação", "dimensao": "lideranca"},
    {"texto": "Gosto de ensinar e orientar outras pessoas", "dimensao": "lideranca"},
    {"texto": "Tomo iniciativa mesmo sem ser solicitado", "dimensao": "lideranca"},
    {"texto": "Consigo motivar pessoas a darem o melhor", "dimensao": "lideranca"},
    {"texto": "Prefiro liderar do que ser liderado", "dimensao": "lideranca"},
]
```

### Match com Postos
```python
PERFIL_IDEAL_POR_TIPO_POSTO = {
    "cftv": {"vigilancia": 90, "comunicacao": 40, "resiliencia": 60, "lideranca": 30},
    "portaria": {"vigilancia": 60, "comunicacao": 85, "resiliencia": 70, "lideranca": 40},
    "recepcao": {"vigilancia": 50, "comunicacao": 95, "resiliencia": 60, "lideranca": 30},
    "ronda": {"vigilancia": 85, "comunicacao": 50, "resiliencia": 80, "lideranca": 50},
    "evento": {"vigilancia": 70, "comunicacao": 70, "resiliencia": 95, "lideranca": 60},
    "supervisor": {"vigilancia": 70, "comunicacao": 80, "resiliencia": 85, "lideranca": 90},
}

def calcular_match(perfil_funcionario, tipo_posto):
    perfil_ideal = PERFIL_IDEAL_POR_TIPO_POSTO[tipo_posto]

    diferenca_total = 0
    for dimensao, ideal in perfil_ideal.items():
        diferenca = abs(perfil_funcionario[dimensao] - ideal)
        diferenca_total += diferenca

    # Match de 0 a 100 (100 = perfeito)
    match = 100 - (diferenca_total / 4)
    return max(0, match)
```

### Modelo de Dados
```python
class OperationalProfile:
    id, funcionario_id, data_avaliacao
    vigilancia, comunicacao, resiliencia, lideranca: int (0-100)
    perfil_predominante: str
    respostas: Dict[pergunta_id, valor]
    versao_questionario: str

class PostMatch:
    id, funcionario_id, posto_id
    score_match: float (0-100)
    fatores_positivos, fatores_negativos: List[str]
    recomendado: bool
```

---

## ENDPOINTS REST

### Onboarding
```
GET    /api/v1/retention/onboarding/checklists
POST   /api/v1/retention/onboarding/checklists
GET    /api/v1/retention/onboarding/funcionario/{id}/progress
POST   /api/v1/retention/onboarding/funcionario/{id}/complete-step
GET    /api/v1/retention/onboarding/dashboard
GET    /api/v1/retention/onboarding/alerts
```

### Clima
```
GET    /api/v1/retention/climate/surveys
POST   /api/v1/retention/climate/surveys
POST   /api/v1/retention/climate/respond
GET    /api/v1/retention/climate/results/posto/{id}
GET    /api/v1/retention/climate/results/empresa
GET    /api/v1/retention/climate/trends
```

### Turnover
```
GET    /api/v1/retention/turnover/predictions
GET    /api/v1/retention/turnover/funcionario/{id}/risk
GET    /api/v1/retention/turnover/alerts
POST   /api/v1/retention/turnover/alerts/{id}/action
GET    /api/v1/retention/turnover/dashboard
GET    /api/v1/retention/turnover/factors
```

### Perfil
```
GET    /api/v1/retention/profile/questionnaire
POST   /api/v1/retention/profile/submit
GET    /api/v1/retention/profile/funcionario/{id}
GET    /api/v1/retention/profile/match/funcionario/{id}/postos
GET    /api/v1/retention/profile/match/posto/{id}/funcionarios
```

---

## MÉTRICAS DE SUCESSO

| Métrica | Baseline | Meta 3 meses | Meta 6 meses |
|---------|----------|--------------|--------------|
| Turnover mensal | 3 | 2.5 | 2 |
| Turnover anual | 36 | 30 | 24 |
| Custo anual | R$ 144k | R$ 120k | R$ 96k |
| Taxa conclusão onboarding | N/A | 80% | 95% |
| Participação pesquisa clima | N/A | 60% | 85% |
| Precisão predição turnover | N/A | 60% | 75% |
| Match perfil-posto | N/A | 70% | 85% |

---

## CRONOGRAMA

```
SEMANA 1-2:   FASE 1 - Onboarding Digital
SEMANA 2-3:   FASE 2 - Pesquisa de Clima
SEMANA 3-5:   FASE 3 - Predição de Turnover
SEMANA 5-7:   FASE 4 - Perfil Operacional
SEMANA 8:     Integração, testes, ajustes
```

---

*Documento criado em Janeiro 2026*
*Sprint: Retenção de Talentos*
