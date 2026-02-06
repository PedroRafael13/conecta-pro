# Cobertura Orval - Módulos MONITORING e RETENTION

**Data:** 2026-01-31
**Status:** ✅ Concluído

---

## 📊 Resumo Executivo

- **Módulo MONITORING:** 22 endpoints → 61 hooks/functions gerados
- **Módulo RETENTION:** 61 endpoints → 165 hooks/functions gerados
- **Total:** 83 endpoints cobertos | 226 hooks TypeScript gerados
- **Código gerado:** ~8.000 linhas TypeScript type-safe

---

## 🎯 Módulos Cobertos

### 1. MONITORING (Early Warning System)

**Backend:** `/opt/conecta-pro/backend/modules/monitoring/controllers/`

**Controllers:**
- `monitoring_controller.py` - Main monitoring (19 endpoints)
- `realtime_controller.py` - Real-time analytics (10 endpoints + WebSocket)

**Endpoints principais:**
- Dashboard completo de monitoramento
- Gerenciamento de alertas (list, get, acknowledge, resolve)
- Thresholds configuráveis (CRUD completo)
- Métricas em tempo real
- WebSocket streaming
- Health checks e admin tools

**Arquivos gerados:**
```
/opt/conecta-pro/frontend/src/api/generated/monitoring/
├── monitoring/monitoring.ts (1,321 linhas, 38 hooks)
├── real-time-analytics/real-time-analytics.ts (803 linhas, 23 hooks)
└── monitoringAPI.schemas.ts (tipos TypeScript)
```

---

### 2. RETENTION (Gestão de Retenção)

**Backend:** `/opt/conecta-pro/backend/modules/retention/`

#### 2.1 Onboarding Digital (24 endpoints)
Gestão completa de checklists e progresso de integração de funcionários.

**Principais features:**
- CRUD de checklists de onboarding
- Gerenciamento de etapas (steps)
- Acompanhamento de progresso por funcionário
- Dashboard e alertas de atrasos
- Duplicação de checklists

#### 2.2 Climate Survey (20 endpoints)
Pesquisas de clima organizacional e análise de resultados.

**Principais features:**
- CRUD de pesquisas de clima
- Coleta de respostas anônimas
- Resultados por posto/equipe/empresa
- Análise de tendências
- Alertas de quedas de clima
- Cálculo de scores agregados

#### 2.3 Perfil Operacional (23 endpoints)
Sistema de avaliação de perfil e match funcionário-posto.

**Principais features:**
- Questionário de 20 perguntas
- Cálculo de perfil operacional (4 dimensões)
- Match funcionário-posto com IA
- Histórico de avaliações
- Dashboard de perfis
- Gestão de perguntas (admin)

#### 2.4 Turnover Prediction (14 endpoints)
Predição de risco de turnover com IA.

**Principais features:**
- Cálculo de score de risco (0-100)
- Análise de fatores de risco
- Alertas automáticos
- Dashboard de turnover
- Histórico de predições
- Recálculo em lote

**Arquivos gerados:**
```
/opt/conecta-pro/frontend/src/api/generated/retention/
├── retention-onboarding-digital/retention-onboarding-digital.ts (1,652 linhas, 47 hooks)
├── retention-climate-survey/retention-climate-survey.ts (1,471 linhas, 42 hooks)
├── retention-perfil-operacional/retention-perfil-operacional.ts (1,653 linhas, 48 hooks)
├── retention-turnover-prediction/retention-turnover-prediction.ts (1,081 linhas, 28 hooks)
└── retentionAPI.schemas.ts (tipos TypeScript)
```

---

## 🔧 Configuração Orval

### Arquivos de configuração criados

**1. orval.config.monitoring.ts**
```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  monitoring: {
    input: {
      target: './openapi/monitoring_openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated/monitoring',
      client: 'react-query',
      mock: false,
      clean: true,
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
```

**2. orval.config.retention.ts**
```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  retention: {
    input: {
      target: './openapi/retention_openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated/retention',
      client: 'react-query',
      mock: false,
      clean: true,
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
```

### Scripts NPM adicionados

```json
{
  "scripts": {
    "orval:monitoring": "orval --config orval.config.monitoring.ts",
    "orval:retention": "orval --config orval.config.retention.ts"
  }
}
```

---

## 📝 Exemplos de Uso

### Monitoring - Dashboard

```typescript
import { useGetDashboardMonitoringDashboardGet } from '@/api/generated/monitoring/monitoring/monitoring';

function MonitoringDashboard() {
  const { data, isLoading, error } = useGetDashboardMonitoringDashboardGet();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h1>Dashboard de Monitoramento</h1>
      <SystemHealth health={data.system_health} />
      <MetricsDisplay metrics={data.metrics} />
      <AlertsList alerts={data.recent_alerts} />
    </div>
  );
}
```

### Monitoring - Gerenciar Alertas

```typescript
import {
  useListAlertsMonitoringAlertsGet,
  useAcknowledgeAlertMonitoringAlertsAlertIdAcknowledgePost
} from '@/api/generated/monitoring/monitoring/monitoring';

function AlertsManager() {
  const { data: alerts } = useListAlertsMonitoringAlertsGet({
    level: 'red',
    active_only: true,
  });

  const acknowledgeMutation = useAcknowledgeAlertMonitoringAlertsAlertIdAcknowledgePost();

  const handleAcknowledge = async (alertId: string) => {
    await acknowledgeMutation.mutateAsync({
      alertId,
      data: { notes: 'Alerta verificado e em tratamento' }
    });
  };

  return (
    <AlertsList
      alerts={alerts?.alerts}
      onAcknowledge={handleAcknowledge}
    />
  );
}
```

### Retention - Onboarding

```typescript
import {
  useListChecklistsRetentionOnboardingChecklistsGet,
  useIniciarOnboardingRetentionOnboardingFuncionarioFuncionarioIdIniciarPost
} from '@/api/generated/retention/retention-onboarding-digital/retention-onboarding-digital';

function OnboardingPage() {
  const { data: checklists } = useListChecklistsRetentionOnboardingChecklistsGet({
    condominium_id: condominiumId,
    limit: 20,
  });

  const iniciarMutation = useIniciarOnboardingRetentionOnboardingFuncionarioFuncionarioIdIniciarPost();

  const handleStartOnboarding = async (funcionarioId: string, checklistId: string) => {
    await iniciarMutation.mutateAsync({
      funcionarioId,
      data: {
        checklist_id: checklistId,
        data_admissao: new Date().toISOString(),
      }
    });
  };

  return (
    <ChecklistSelector
      checklists={checklists?.items}
      onStart={handleStartOnboarding}
    />
  );
}
```

### Retention - Climate Survey

```typescript
import {
  useGetActiveSurveyRetentionClimateSurveysAtivaGet,
  useRespondSurveyRetentionClimateRespondPost
} from '@/api/generated/retention/retention-climate-survey/retention-climate-survey';

function ClimateSurveyForm() {
  const { data: survey } = useGetActiveSurveyRetentionClimateSurveysAtivaGet({
    empresa_id: empresaId
  });

  const submitMutation = useRespondSurveyRetentionClimateRespondPost();

  const handleSubmit = async (respostas: number[]) => {
    await submitMutation.mutateAsync({
      data: {
        survey_id: survey.id,
        funcionario_id: funcionarioId,
        respostas,
      }
    });
  };

  return (
    <SurveyForm
      perguntas={survey?.perguntas}
      onSubmit={handleSubmit}
    />
  );
}
```

### Retention - Turnover Prediction

```typescript
import {
  useGetRiskFuncionarioRetentionTurnoverFuncionarioFuncionarioIdRiskGet,
  useGetDashboardRetentionTurnoverDashboardGet
} from '@/api/generated/retention/retention-turnover-prediction/retention-turnover-prediction';

function TurnoverDashboard() {
  const { data: dashboard } = useGetDashboardRetentionTurnoverDashboardGet({
    condominium_id: condominiumId,
  });

  return (
    <div>
      <RiskOverview
        totalFuncionarios={dashboard.total_funcionarios}
        riscoCritico={dashboard.risco_critico}
        riscoAlto={dashboard.risco_alto}
      />
      <TopRiskFactors fatores={dashboard.principais_fatores} />
      <TrendChart dados={dashboard.tendencia_mensal} />
    </div>
  );
}

function FuncionarioRiskDetail({ funcionarioId }: Props) {
  const { data: risk } = useGetRiskFuncionarioRetentionTurnoverFuncionarioFuncionarioIdRiskGet({
    funcionarioId,
    condominium_id: condominiumId,
  });

  return (
    <div>
      <RiskScore score={risk?.score_risco} nivel={risk?.nivel} />
      <RiskFactors fatores={risk?.fatores} />
      <RecommendedActions fatores={risk?.fatores} />
    </div>
  );
}
```

---

## 🔍 Tipos TypeScript Gerados

### Monitoring - Exemplos

```typescript
export interface AlertResponse {
  id: string;
  metric_name: string;
  level?: AlertLevel;
  current_value: number;
  threshold_value: number;
  title: string;
  message?: string | null;
  status: AlertStatus;
  triggered_at: string;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type AlertLevel = 'green' | 'yellow' | 'orange' | 'red';
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface ThresholdResponse {
  id: string;
  metric_name: string;
  category: string;
  warning_threshold?: number | null;
  critical_threshold?: number | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface SystemHealthResponse {
  overall_status: AlertLevel;
  active_alerts_count: number;
  critical_alerts_count: number;
  system_uptime_hours: number;
  last_check_timestamp: string;
}
```

### Retention - Exemplos

```typescript
// Onboarding
export interface ChecklistDetailResponse {
  id: string;
  nome: string;
  descricao?: string | null;
  departamento?: string | null;
  condominium_id: string;
  etapas: StepResponse[];
  total_etapas: number;
  ativo: boolean;
  created_at: string;
}

export interface StepResponse {
  id: string;
  checklist_id: string;
  tipo: StepType;
  titulo: string;
  descricao?: string | null;
  ordem: number;
  prazo_dias: number;
  obrigatorio: boolean;
  responsavel?: string | null;
}

// Climate
export interface ClimateByPosto {
  posto_id: string;
  score_medio: number;
  participacao_percentual: number;
  total_respostas: number;
  tendencia: string;
  periodo: string;
}

export interface ClimateDashboard {
  score_geral_empresa: number;
  total_respostas: number;
  participacao_percentual: number;
  tendencia_geral: string;
  alertas_ativos: number;
  piores_postos: ClimateByPosto[];
  melhores_equipes: ClimateByEquipe[];
}

// Profile
export interface OperationalProfileDetail {
  id: string;
  funcionario_id: string;
  condominium_id: string;
  score_total: number;
  perfil_predominante: ProfileDimensionEnum;
  dimensoes: ProfileDimensions;
  pontos_fortes: string[];
  areas_desenvolvimento: string[];
  recomendacoes: string[];
  valido: boolean;
  created_at: string;
}

export interface PostMatchResponse {
  match_id?: string | null;
  funcionario_id: string;
  posto_id: string;
  score_match: number;
  nivel: MatchNivelEnum;
  dimensoes_match: DimensionMatchDetail[];
  recomendacao: string;
  created_at?: string | null;
}

// Turnover
export interface PredictionResponse {
  id: string;
  funcionario_id: string;
  condominium_id: string;
  score_risco: number;
  nivel: NivelRisco;
  fatores: RiskFactorResponse[];
  is_alerta_necessario: boolean;
  is_critico: boolean;
  data_calculo: string;
}

export type NivelRisco = 'baixo' | 'moderado' | 'alto' | 'critico';

export interface RiskFactorResponse {
  id: string;
  nome: string;
  categoria: CategoriaFator;
  peso: number;
  valor_atual: number;
  contribuicao_score: number;
  threshold_violado: boolean;
  is_critico: boolean;
  recomendacao_acao?: string | null;
}
```

---

## 🚀 Comandos de Geração

### Gerar tipos do zero

```bash
# Backend: Gerar OpenAPI JSON
cd /opt/conecta-pro/backend
python3 -c "
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json

# Monitoring
from modules.monitoring.controllers.monitoring_controller import router as monitoring_router
from modules.monitoring.controllers.realtime_controller import router as realtime_router

app = FastAPI(title='Monitoring API', version='1.0.0')
app.include_router(monitoring_router)
app.include_router(realtime_router)

openapi_schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
with open('/opt/conecta-pro/frontend/openapi/monitoring_openapi.json', 'w') as f:
    json.dump(openapi_schema, f, indent=2)
"

# Frontend: Gerar hooks TypeScript
cd /opt/conecta-pro/frontend
npm run orval:monitoring
npm run orval:retention
```

### Atualizar após mudanças no backend

```bash
# 1. Regenerar OpenAPI (se backend mudou)
cd /opt/conecta-pro/backend
# ... executar script de geração ...

# 2. Regenerar tipos frontend
cd /opt/conecta-pro/frontend
npm run orval:monitoring  # Ou orval:retention
```

---

## 📊 Estatísticas Finais

| Módulo | Controllers | Endpoints | Hooks Gerados | Linhas TS |
|--------|------------|-----------|---------------|-----------|
| **Monitoring** | 2 | 22 | 61 | ~2,100 |
| **Retention - Onboarding** | 1 | 24 | 47 | ~1,650 |
| **Retention - Climate** | 1 | 20 | 42 | ~1,470 |
| **Retention - Profile** | 1 | 23 | 48 | ~1,650 |
| **Retention - Turnover** | 1 | 14 | 28 | ~1,080 |
| **TOTAL** | **6** | **83** | **226** | **~8,000** |

---

## ✅ Checklist de Validação

- [x] OpenAPI gerado para Monitoring (55KB)
- [x] OpenAPI gerado para Retention (279KB)
- [x] Orval configurado com tags-split
- [x] React Query hooks gerados
- [x] Custom mutator configurado (api-client.ts)
- [x] Tipos TypeScript type-safe
- [x] Scripts NPM adicionados
- [x] Zero erros na geração
- [x] Documentação criada
- [x] Exemplos de uso fornecidos

---

## 📚 Próximos Passos

1. **Integração em componentes React**
   - Criar componentes usando os hooks gerados
   - Testar chamadas de API

2. **Manutenção**
   - Regenerar quando backend mudar
   - Manter sincronizado com evolução da API

3. **Expansão**
   - Adicionar testes unitários para hooks
   - Criar storybook com exemplos

---

**Gerado em:** 2026-01-31
**Autor:** Claude Code Agent
**Versão Orval:** 7.13.2
