/**
 * EXEMPLOS PRÁTICOS DE USO - ORVAL MONITORING & RETENTION
 * ========================================================
 *
 * Este arquivo contém exemplos práticos de uso dos hooks gerados
 * pelo Orval para os módulos Monitoring e Retention.
 */

// ============================================================================
// MONITORING - DASHBOARD DE MONITORAMENTO
// ============================================================================

import { useGetDashboardMonitoringDashboardGet } from '@/api/generated/monitoring/monitoring/monitoring';

export function MonitoringDashboard() {
  const { data, isLoading, error, refetch } = useGetDashboardMonitoringDashboardGet();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard de Monitoramento</h1>
        <button onClick={() => refetch()}>Atualizar</button>
      </div>

      {/* System Health */}
      <div className="grid grid-cols-4 gap-4">
        <StatusCard
          label="Status Geral"
          value={data.system_health}
          color={getHealthColor(data.system_health)}
        />
        <StatusCard
          label="Alertas Ativos"
          value={data.active_alerts_count}
          color="yellow"
        />
        <StatusCard
          label="Alertas Críticos"
          value={data.critical_alerts_count}
          color="red"
        />
        <StatusCard
          label="Uptime (horas)"
          value={data.system_uptime_hours}
          color="green"
        />
      </div>

      {/* Recent Alerts */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Alertas Recentes</h2>
        <AlertsList alerts={data.recent_alerts} />
      </div>

      {/* Current Metrics */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Métricas em Tempo Real</h2>
        <MetricsGrid metrics={data.current_metrics} />
      </div>
    </div>
  );
}

// ============================================================================
// MONITORING - GERENCIAMENTO DE ALERTAS
// ============================================================================

import {
  useListAlertsMonitoringAlertsGet,
  useAcknowledgeAlertMonitoringAlertsAlertIdAcknowledgePost,
  useResolveAlertMonitoringAlertsAlertIdResolvePost,
} from '@/api/generated/monitoring/monitoring/monitoring';
import type { AlertLevel } from '@/api/generated/monitoring/monitoringAPI.schemas';
import { useState } from 'react';

export function AlertsManagementPage() {
  const [levelFilter, setLevelFilter] = useState<AlertLevel | undefined>();
  const [activeOnly, setActiveOnly] = useState(true);

  const { data: alertsData, refetch } = useListAlertsMonitoringAlertsGet({
    level: levelFilter,
    active_only: activeOnly,
    limit: 100,
  });

  const acknowledgeMutation = useAcknowledgeAlertMonitoringAlertsAlertIdAcknowledgePost();
  const resolveMutation = useResolveAlertMonitoringAlertsAlertIdResolvePost();

  const handleAcknowledge = async (alertId: string, notes: string) => {
    await acknowledgeMutation.mutateAsync({
      alertId,
      data: { notes },
    });
    refetch();
  };

  const handleResolve = async (alertId: string, notes: string) => {
    await resolveMutation.mutateAsync({
      alertId,
      data: { notes },
    });
    refetch();
  };

  return (
    <div className="p-6">
      <div className="mb-6 flex gap-4">
        <select value={levelFilter} onChange={(e) => setLevelFilter(e.target.value as AlertLevel)}>
          <option value="">Todos os níveis</option>
          <option value="red">Crítico</option>
          <option value="orange">Alto</option>
          <option value="yellow">Médio</option>
          <option value="green">Baixo</option>
        </select>

        <label>
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
          />
          Apenas ativos
        </label>
      </div>

      <div className="space-y-4">
        {alertsData?.alerts?.map((alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onAcknowledge={(notes) => handleAcknowledge(alert.id, notes)}
            onResolve={(notes) => handleResolve(alert.id, notes)}
          />
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-600">
        Total: {alertsData?.total} | Ativos: {alertsData?.active} | Críticos: {alertsData?.critical}
      </div>
    </div>
  );
}

// ============================================================================
// MONITORING - REAL-TIME METRICS
// ============================================================================

import {
  useGetCurrentMetricsRealtimeMetricsCurrentGet,
  useSendMetricRealtimeMetricsPost,
} from '@/api/generated/monitoring/real-time-analytics/real-time-analytics';
import { useEffect } from 'react';

export function RealTimeMetricsDisplay() {
  const { data: metrics, refetch } = useGetCurrentMetricsRealtimeMetricsCurrentGet();
  const sendMetricMutation = useSendMetricRealtimeMetricsPost();

  // Atualizar a cada 5 segundos
  useEffect(() => {
    const interval = setInterval(() => {
      refetch();
    }, 5000);

    return () => clearInterval(interval);
  }, [refetch]);

  const handleSendMetric = async (name: string, value: number) => {
    await sendMetricMutation.mutateAsync({
      data: {
        name,
        value,
        metric_type: 'gauge',
        tags: { source: 'manual' },
      },
    });
  };

  return (
    <div className="p-6">
      <div className="mb-4">
        <h2 className="text-xl font-bold">Métricas em Tempo Real</h2>
        <p className="text-sm text-gray-600">
          Última atualização: {metrics?.timestamp}
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {metrics?.metrics?.map((metric) => (
          <MetricCard
            key={metric.name}
            name={metric.name}
            value={metric.value}
            type={metric.type}
            tags={metric.tags}
          />
        ))}
      </div>

      <div className="mt-6">
        <h3 className="font-semibold mb-2">Status do Sistema</h3>
        <SystemHealthBadge health={metrics?.system_health} />
      </div>
    </div>
  );
}

// ============================================================================
// RETENTION - ONBOARDING DIGITAL
// ============================================================================

import {
  useListChecklistsRetentionOnboardingChecklistsGet,
  useCreateChecklistRetentionOnboardingChecklistsPost,
  useIniciarOnboardingRetentionOnboardingFuncionarioFuncionarioIdIniciarPost,
  useGetFuncionarioProgressRetentionOnboardingFuncionarioFuncionarioIdProgressGet,
  useCompletarEtapaRetentionOnboardingProgressProgressIdCompletarPost,
} from '@/api/generated/retention/retention-onboarding-digital/retention-onboarding-digital';
import type { ChecklistCreate } from '@/api/generated/retention/retentionAPI.schemas';

export function OnboardingManagementPage() {
  const condominiumId = 'your-condominium-id';

  const { data: checklistsData } = useListChecklistsRetentionOnboardingChecklistsGet({
    condominium_id: condominiumId,
    limit: 20,
  });

  const createChecklistMutation = useCreateChecklistRetentionOnboardingChecklistsPost();
  const iniciarOnboardingMutation = useIniciarOnboardingRetentionOnboardingFuncionarioFuncionarioIdIniciarPost();

  const handleCreateChecklist = async (data: ChecklistCreate) => {
    const result = await createChecklistMutation.mutateAsync({ data });
    console.log('Checklist criado:', result);
  };

  const handleStartOnboarding = async (funcionarioId: string, checklistId: string) => {
    const result = await iniciarOnboardingMutation.mutateAsync({
      funcionarioId,
      data: {
        checklist_id: checklistId,
        data_admissao: new Date().toISOString(),
        condominium_id: condominiumId,
      },
    });
    console.log('Onboarding iniciado:', result);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Gestão de Onboarding</h1>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">Checklists Disponíveis</h2>
          <div className="space-y-2">
            {checklistsData?.items?.map((checklist) => (
              <ChecklistCard
                key={checklist.id}
                checklist={checklist}
                onStart={(funcionarioId) => handleStartOnboarding(funcionarioId, checklist.id)}
              />
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Criar Novo Checklist</h2>
          <ChecklistForm onSubmit={handleCreateChecklist} />
        </div>
      </div>
    </div>
  );
}

// Componente para acompanhar progresso individual
export function FuncionarioOnboardingProgress({ funcionarioId }: { funcionarioId: string }) {
  const { data: progress, refetch } = useGetFuncionarioProgressRetentionOnboardingFuncionarioFuncionarioIdProgressGet({
    funcionarioId,
  });

  const completarEtapaMutation = useCompletarEtapaRetentionOnboardingProgressProgressIdCompletarPost();

  const handleCompletarEtapa = async (progressId: string, evidencias: string) => {
    await completarEtapaMutation.mutateAsync({
      progressId,
      data: {
        observacoes: 'Etapa concluída',
        evidencias,
      },
    });
    refetch();
  };

  if (!progress) return <div>Carregando...</div>;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Progresso do Onboarding</h2>

      <div className="mb-6">
        <ProgressBar
          current={progress.etapas_concluidas}
          total={progress.total_etapas}
          percentage={progress.percentual_concluido}
        />
      </div>

      <div className="space-y-4">
        {progress.etapas?.map((etapa) => (
          <EtapaCard
            key={etapa.id}
            etapa={etapa}
            onCompletar={(evidencias) => handleCompletarEtapa(etapa.id, evidencias)}
          />
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// RETENTION - CLIMATE SURVEY
// ============================================================================

import {
  useGetActiveSurveyRetentionClimateSurveysAtivaGet,
  useRespondSurveyRetentionClimateRespondPost,
  useGetDashboardRetentionClimateDashboardGet,
  useGetResultsByPostoRetentionClimateResultsPostoPostoIdGet,
} from '@/api/generated/retention/retention-climate-survey/retention-climate-survey';

// Formulário para responder pesquisa
export function ClimateSurveyForm({ funcionarioId }: { funcionarioId: string }) {
  const empresaId = 'your-empresa-id';
  const [respostas, setRespostas] = useState<number[]>([]);

  const { data: survey } = useGetActiveSurveyRetentionClimateSurveysAtivaGet({
    empresa_id: empresaId,
  });

  const submitMutation = useRespondSurveyRetentionClimateRespondPost();

  const handleSubmit = async () => {
    await submitMutation.mutateAsync({
      data: {
        survey_id: survey.id,
        funcionario_id: funcionarioId,
        respostas,
      },
    });
  };

  if (!survey) return <div>Nenhuma pesquisa ativa no momento</div>;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">{survey.nome}</h1>
      <p className="text-gray-600 mb-6">{survey.descricao}</p>

      <div className="space-y-6">
        {survey.perguntas.map((pergunta, index) => (
          <div key={index} className="border-b pb-4">
            <p className="font-medium mb-3">{pergunta.texto}</p>
            <div className="flex gap-4">
              {[1, 2, 3, 4, 5].map((valor) => (
                <label key={valor} className="flex items-center gap-2">
                  <input
                    type="radio"
                    name={`q${index}`}
                    value={valor}
                    onChange={(e) => {
                      const newRespostas = [...respostas];
                      newRespostas[index] = parseInt(e.target.value);
                      setRespostas(newRespostas);
                    }}
                  />
                  {valor}
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={respostas.length !== survey.total_perguntas}
        className="mt-6 px-6 py-2 bg-blue-600 text-white rounded"
      >
        Enviar Respostas
      </button>

      <p className="mt-2 text-sm text-gray-600">
        Tempo estimado: {survey.tempo_estimado_minutos} minutos
      </p>
    </div>
  );
}

// Dashboard de Clima
export function ClimateDashboard() {
  const empresaId = 'your-empresa-id';

  const { data: dashboard } = useGetDashboardRetentionClimateDashboardGet({
    empresa_id: empresaId,
  });

  if (!dashboard) return <div>Carregando...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard de Clima Organizacional</h1>

      {/* Score Geral */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Score Geral"
          value={dashboard.score_geral_empresa}
          unit="/5"
        />
        <MetricCard
          label="Participação"
          value={dashboard.participacao_percentual}
          unit="%"
        />
        <MetricCard
          label="Total Respostas"
          value={dashboard.total_respostas}
        />
        <MetricCard
          label="Tendência"
          value={dashboard.tendencia_geral}
          color={getTrendColor(dashboard.tendencia_geral)}
        />
      </div>

      {/* Piores Postos */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Postos com Menor Score</h2>
        <table className="w-full">
          <thead>
            <tr>
              <th>Posto</th>
              <th>Score Médio</th>
              <th>Participação</th>
              <th>Tendência</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.piores_postos.map((posto) => (
              <tr key={posto.posto_id}>
                <td>{posto.posto_id}</td>
                <td>{posto.score_medio.toFixed(2)}</td>
                <td>{posto.participacao_percentual}%</td>
                <td>{posto.tendencia}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Alertas */}
      {dashboard.alertas_ativos > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
          <p className="font-semibold">⚠️ {dashboard.alertas_ativos} alertas ativos</p>
          <p className="text-sm">Áreas que requerem atenção imediata</p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// RETENTION - PERFIL OPERACIONAL
// ============================================================================

import {
  useGetQuestionnaireRetentionProfileQuestionnaireGet,
  useSubmitResponsesRetentionProfileSubmitPost,
  useGetFuncionarioProfileRetentionProfileFuncionarioFuncionarioIdGet,
  useGetBestPostsForFuncionarioRetentionProfileMatchFuncionarioFuncionarioIdPostosGet,
} from '@/api/generated/retention/retention-perfil-operacional/retention-perfil-operacional';

// Questionário de Perfil
export function ProfileQuestionnaire({ funcionarioId }: { funcionarioId: string }) {
  const condominiumId = 'your-condominium-id';
  const [respostas, setRespostas] = useState<Record<string, number>>({});

  const { data: questionario } = useGetQuestionnaireRetentionProfileQuestionnaireGet({
    versao: '1.0.0',
    condominium_id: condominiumId,
  });

  const submitMutation = useSubmitResponsesRetentionProfileSubmitPost();

  const handleSubmit = async () => {
    await submitMutation.mutateAsync({
      data: {
        funcionario_id: funcionarioId,
        condominium_id: condominiumId,
        versao_questionario: '1.0.0',
        respostas,
      },
    });
  };

  if (!questionario) return <div>Carregando...</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Avaliação de Perfil Operacional</h1>
      <p className="text-gray-600 mb-6">{questionario.descricao}</p>

      <div className="space-y-6">
        {questionario.perguntas.map((pergunta) => (
          <div key={pergunta.id} className="border-b pb-4">
            <p className="font-medium mb-2">{pergunta.texto}</p>
            <p className="text-sm text-gray-600 mb-3">{pergunta.descricao}</p>

            <div className="flex gap-2">
              {[1, 2, 3, 4].map((valor) => (
                <label key={valor} className="flex-1 text-center">
                  <input
                    type="radio"
                    name={pergunta.id}
                    value={valor}
                    onChange={(e) => {
                      setRespostas({
                        ...respostas,
                        [pergunta.id]: parseInt(e.target.value),
                      });
                    }}
                    className="mb-1"
                  />
                  <div className="text-xs">{getScaleLabel(valor)}</div>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleSubmit}
        disabled={Object.keys(respostas).length !== questionario.total_perguntas}
        className="mt-6 px-6 py-2 bg-blue-600 text-white rounded"
      >
        Enviar Avaliação
      </button>
    </div>
  );
}

// Visualização de Perfil e Matches
export function FuncionarioProfileView({ funcionarioId }: { funcionarioId: string }) {
  const { data: profile } = useGetFuncionarioProfileRetentionProfileFuncionarioFuncionarioIdGet({
    funcionarioId,
  });

  const { data: matches } = useGetBestPostsForFuncionarioRetentionProfileMatchFuncionarioFuncionarioIdPostosGet({
    funcionarioId,
    limit: 10,
  });

  if (!profile) return <div>Carregando...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Perfil Operacional</h1>

      {/* Score Total */}
      <div className="mb-6">
        <div className="text-4xl font-bold">{profile.score_total}</div>
        <div className="text-gray-600">Score Total</div>
        <div className="mt-2">
          Perfil Predominante: <span className="font-semibold">{profile.perfil_predominante}</span>
        </div>
      </div>

      {/* Dimensões */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {Object.entries(profile.dimensoes).map(([dimensao, valor]) => (
          <DimensaoCard key={dimensao} nome={dimensao} valor={valor} />
        ))}
      </div>

      {/* Pontos Fortes */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-3">Pontos Fortes</h2>
        <ul className="list-disc list-inside space-y-1">
          {profile.pontos_fortes.map((ponto, i) => (
            <li key={i}>{ponto}</li>
          ))}
        </ul>
      </div>

      {/* Melhores Matches */}
      <div>
        <h2 className="text-xl font-semibold mb-3">Postos Recomendados</h2>
        <div className="space-y-2">
          {matches?.matches.map((match) => (
            <MatchCard
              key={match.posto_id}
              match={match}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// RETENTION - TURNOVER PREDICTION
// ============================================================================

import {
  useGetRiskFuncionarioRetentionTurnoverFuncionarioFuncionarioIdRiskGet,
  useListarPredictionsRetentionTurnoverPredictionsGet,
  useGetDashboardRetentionTurnoverDashboardGet,
  useRecalcularFuncionarioRetentionTurnoverFuncionarioFuncionarioIdRecalcularPost,
} from '@/api/generated/retention/retention-turnover-prediction/retention-turnover-prediction';
import type { NivelRisco } from '@/api/generated/retention/retentionAPI.schemas';

// Dashboard de Turnover
export function TurnoverDashboard() {
  const condominiumId = 'your-condominium-id';

  const { data: dashboard } = useGetDashboardRetentionTurnoverDashboardGet({
    condominium_id: condominiumId,
  });

  if (!dashboard) return <div>Carregando...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard de Turnover</h1>

      {/* Visão Geral */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard
          label="Total Funcionários"
          value={dashboard.total_funcionarios}
        />
        <MetricCard
          label="Risco Crítico"
          value={dashboard.risco_critico}
          color="red"
        />
        <MetricCard
          label="Risco Alto"
          value={dashboard.risco_alto}
          color="orange"
        />
        <MetricCard
          label="Score Médio"
          value={dashboard.score_medio.toFixed(1)}
        />
      </div>

      {/* Principais Fatores de Risco */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Principais Fatores de Risco</h2>
        <div className="space-y-2">
          {dashboard.principais_fatores.map((fator) => (
            <FatorCard
              key={fator.nome}
              nome={fator.nome}
              categoria={fator.categoria}
              contribuicao={fator.contribuicao_media}
              funcionarios_afetados={fator.funcionarios_afetados}
            />
          ))}
        </div>
      </div>

      {/* Alertas Pendentes */}
      {dashboard.alertas_pendentes > 0 && (
        <div className="bg-red-50 border border-red-200 p-4 rounded">
          <p className="font-semibold">🚨 {dashboard.alertas_pendentes} alertas pendentes</p>
          <p className="text-sm">Funcionários que requerem atenção imediata</p>
        </div>
      )}
    </div>
  );
}

// Detalhes de Risco Individual
export function FuncionarioRiskDetail({ funcionarioId }: { funcionarioId: string }) {
  const condominiumId = 'your-condominium-id';

  const { data: risk, refetch } = useGetRiskFuncionarioRetentionTurnoverFuncionarioFuncionarioIdRiskGet({
    funcionarioId,
    condominium_id: condominiumId,
  });

  const recalcularMutation = useRecalcularFuncionarioRetentionTurnoverFuncionarioFuncionarioIdRecalcularPost();

  const handleRecalcular = async () => {
    await recalcularMutation.mutateAsync({
      funcionarioId,
      condominium_id: condominiumId,
      dados: {
        motivo: 'Recálculo manual solicitado',
      },
    });
    refetch();
  };

  if (!risk) return <div>Carregando...</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Análise de Risco de Turnover</h1>
        <button
          onClick={handleRecalcular}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Recalcular
        </button>
      </div>

      {/* Score de Risco */}
      <div className="mb-6">
        <RiskScoreGauge
          score={risk.score_risco}
          nivel={risk.nivel}
          isCritico={risk.is_critico}
        />
      </div>

      {/* Fatores de Risco */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Fatores de Risco</h2>
        <div className="space-y-3">
          {risk.fatores
            .sort((a, b) => b.contribuicao_score - a.contribuicao_score)
            .map((fator) => (
              <FatorRiscoCard
                key={fator.id}
                fator={fator}
              />
            ))}
        </div>
      </div>

      {/* Ações Recomendadas */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Ações Recomendadas</h2>
        <div className="space-y-2">
          {risk.fatores
            .filter((f) => f.is_critico && f.recomendacao_acao)
            .map((fator) => (
              <div
                key={fator.id}
                className="bg-yellow-50 border border-yellow-200 p-4 rounded"
              >
                <p className="font-semibold">{fator.nome}</p>
                <p className="text-sm mt-1">{fator.recomendacao_acao}</p>
              </div>
            ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="mt-6 text-sm text-gray-600">
        <p>Última atualização: {new Date(risk.data_calculo).toLocaleString()}</p>
        <p>Modelo: v{risk.modelo_versao}</p>
      </div>
    </div>
  );
}

// Lista de Funcionários com Risco
export function FuncionariosRiskList() {
  const condominiumId = 'your-condominium-id';
  const [nivelFilter, setNivelFilter] = useState<NivelRisco | undefined>();

  const { data: predictionsData } = useListarPredictionsRetentionTurnoverPredictionsGet({
    condominium_id: condominiumId,
    nivel: nivelFilter,
    apenas_alerta: true,
    limit: 50,
    order_by: 'score_risco',
    order_desc: true,
  });

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Funcionários em Risco</h1>

      <div className="mb-4">
        <select
          value={nivelFilter}
          onChange={(e) => setNivelFilter(e.target.value as NivelRisco)}
        >
          <option value="">Todos os níveis</option>
          <option value="critico">Crítico</option>
          <option value="alto">Alto</option>
          <option value="moderado">Moderado</option>
          <option value="baixo">Baixo</option>
        </select>
      </div>

      <div className="space-y-2">
        {predictionsData?.items?.map((prediction) => (
          <PredictionCard
            key={prediction.id}
            prediction={prediction}
          />
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-600">
        Total: {predictionsData?.total} funcionários
      </div>
    </div>
  );
}

// ============================================================================
// COMPONENTES AUXILIARES (EXEMPLOS)
// ============================================================================

function LoadingSpinner() {
  return <div>Carregando...</div>;
}

function ErrorMessage({ error }: { error: unknown }) {
  return <div className="text-red-600">Erro: {String(error)}</div>;
}

function getHealthColor(health: string) {
  const colors = {
    green: 'green',
    yellow: 'yellow',
    orange: 'orange',
    red: 'red',
  };
  return colors[health] || 'gray';
}

function getTrendColor(trend: string) {
  if (trend.includes('positiva')) return 'green';
  if (trend.includes('negativa')) return 'red';
  return 'gray';
}

function getScaleLabel(valor: number) {
  const labels = {
    1: 'Discordo',
    2: 'Neutro',
    3: 'Concordo',
    4: 'Concordo Muito',
  };
  return labels[valor] || '';
}
