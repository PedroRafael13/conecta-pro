'use client';

import {
  Brain, Activity, Shield, TrendingUp, TrendingDown, AlertTriangle,
  CheckCircle, Users, MapPin, Clock, Target, Zap, RefreshCw,
  BarChart2, ArrowLeft, ChevronRight, Eye
} from 'lucide-react';
import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';

interface RiskItem {
  post_name: string;
  shift_type: string;
  risk_percentage: number;
  risk_level: string;
  risk_factors: string[];
}

interface TopPerformer {
  employee_name: string;
  score: number;
  rank: number;
  highlights: string[];
  eligible_for_promotion: boolean;
}

interface CommandCenterData {
  status: string;
  generated_at: string;
  overview: {
    posts_active: number;
    coverage_score: number;
    active_alerts: number;
    high_risk_shifts_tomorrow: number;
  };
  coverage_prediction: {
    date: string;
    risks: RiskItem[];
  };
  weekly_risk_map: {
    coverage_probability: number;
    high_risk_count: number;
    recommended_actions: string[];
    summary: string;
  };
  agents_status: Record<string, string>;
}

interface PerformanceData {
  team_average_score: number;
  total_analyzed: number;
  top_performers: TopPerformer[];
  score_distribution: Record<string, number>;
}

const RISK_COLORS: Record<string, string> = {
  confiavel: 'text-green-400 bg-green-900/30',
  atencao: 'text-yellow-400 bg-yellow-900/30',
  alto_risco: 'text-orange-400 bg-orange-900/30',
  critico: 'text-red-400 bg-red-900/30',
};

const RISK_LABELS: Record<string, string> = {
  confiavel: 'Confiável',
  atencao: 'Atenção',
  alto_risco: 'Alto Risco',
  critico: 'Crítico',
};

const AGENT_NAMES: Record<string, string> = {
  scale_optimizer: '📅 Otimizador de Escalas',
  coverage_predictor: '🎯 Preditor de Cobertura',
  performance_analyzer: '📊 Analisador de Performance',
  substitution_optimizer: '🔄 Otimizador de Substituições',
  occurrence_analyzer: '⚠️ Classificador de Ocorrências',
  predictive_analyzer: '🔮 Analisador Preditivo',
};

export default function AICommandCenterOperacionalPage() {
  const router = useRouter();
  const { isLoading: authLoading, isAuthenticated } = useAuth();
  const [commandData, setCommandData] = useState<CommandCenterData | null>(null);
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [cmdRes, perfRes] = await Promise.allSettled([
        api.get('/api/v1/operacional/ai/command-center'),
        api.get('/api/v1/operacional/ai/performance-overview'),
      ]);

      if (cmdRes.status === 'fulfilled') {
        setCommandData((cmdRes.value as any).data);
      }
      if (perfRes.status === 'fulfilled') {
        setPerformanceData((perfRes.value as any).data);
      }
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Erro ao carregar AI Command Center:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated, loadData]);

  const overview = commandData?.overview;
  const coverageScore = overview?.coverage_score ?? 0;

  // Bartolo 3.0 Chat
  const [bartoloChatHistory, setBartoloChatHistory] = useState<Array<{role: 'user'|'assistant', content: string}>>([]);
  const [bartoloInput, setBartoloInput] = useState('');
  const [bartoloLoading, setBartoloLoading] = useState(false);
  const [bartoloSuggestions, setBartoloSuggestions] = useState<string[]>(['Como está a operação?', 'Ver alertas', 'Status de cobertura']);

  const handleBartolSend = useCallback(async (message: string) => {
    if (!message.trim()) return;
    const userMsg = message.trim();
    setBartoloInput('');
    setBartoloChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setBartoloLoading(true);
    try {
      const res = await api.post('/api/v1/operacional/ai/bartolo/chat', {
        message: userMsg,
        user_id: 'admin',
        history: bartoloChatHistory.slice(-6),
      });
      const data = (res as any).data;
      setBartoloChatHistory(prev => [...prev, { role: 'assistant', content: data.message }]);
      if (data.suggestions?.length) setBartoloSuggestions(data.suggestions.slice(0, 3));
    } catch {
      setBartoloChatHistory(prev => [...prev, { role: 'assistant', content: 'Desculpe, tive um problema técnico. Tente novamente.' }]);
    } finally {
      setBartoloLoading(false);
    }
  }, [bartoloChatHistory]);

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#111b57] to-[#1a47f5]/20 border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/modulos/operacional">
              <Button variant="ghost" size="sm" className="text-white/70 hover:text-white">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Operacional
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">AI Command Center</h1>
                <p className="text-sm text-white/60">Inteligência Operacional em Tempo Real</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {lastUpdated && (
              <span className="text-xs text-white/40">
                Atualizado: {lastUpdated.toLocaleTimeString('pt-BR')}
              </span>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={loadData}
              disabled={isLoading}
              className="border-white/20 text-white/70 hover:text-white"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Atualizar
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <MapPin className="w-4 h-4 text-cyan-400" />
              <span className="text-xs text-white/60">Postos Ativos</span>
            </div>
            <div className="text-2xl font-bold text-white">
              {isLoading ? '—' : overview?.posts_active ?? 0}
            </div>
            <div className="text-xs text-green-400 mt-1">Operacionais</div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4 text-blue-400" />
              <span className="text-xs text-white/60">Cobertura Prevista</span>
            </div>
            <div className={`text-2xl font-bold ${coverageScore >= 90 ? 'text-green-400' : coverageScore >= 75 ? 'text-yellow-400' : 'text-red-400'}`}>
              {isLoading ? '—' : `${coverageScore}%`}
            </div>
            <div className="text-xs text-white/40 mt-1">Próxima semana</div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-orange-400" />
              <span className="text-xs text-white/60">Alertas Ativos</span>
            </div>
            <div className={`text-2xl font-bold ${(overview?.active_alerts ?? 0) > 0 ? 'text-orange-400' : 'text-green-400'}`}>
              {isLoading ? '—' : overview?.active_alerts ?? 0}
            </div>
            <div className="text-xs text-white/40 mt-1">Requerem atenção</div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart2 className="w-4 h-4 text-purple-400" />
              <span className="text-xs text-white/60">Score da Equipe</span>
            </div>
            <div className="text-2xl font-bold text-purple-400">
              {isLoading ? '—' : performanceData?.team_average_score ?? 0}
            </div>
            <div className="text-xs text-white/40 mt-1">Performance média</div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Previsão de Cobertura */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-400" />
                <h2 className="font-semibold">Previsão de Cobertura</h2>
              </div>
              <span className="text-xs text-white/40 bg-blue-900/30 px-2 py-1 rounded">
                Amanhã
              </span>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : commandData?.coverage_prediction?.risks?.length ? (
              <div className="space-y-3">
                {commandData.coverage_prediction.risks.map((risk, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <div>
                      <div className="text-sm font-medium">{risk.post_name}</div>
                      <div className="text-xs text-white/50">{risk.shift_type}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className="text-sm font-bold">{risk.risk_percentage}%</div>
                        <div className="text-xs text-white/40">risco</div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${RISK_COLORS[risk.risk_level] || 'text-gray-400 bg-gray-800'}`}>
                        {RISK_LABELS[risk.risk_level] || risk.risk_level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-white/40">
                <CheckCircle className="w-6 h-6 mr-2 text-green-400" />
                Cobertura OK para amanhã
              </div>
            )}

            {commandData?.weekly_risk_map?.recommended_actions?.length ? (
              <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/20 rounded-lg">
                <div className="text-xs font-medium text-blue-400 mb-2">Ações Recomendadas:</div>
                {commandData.weekly_risk_map.recommended_actions.slice(0, 2).map((action, idx) => (
                  <div key={idx} className="text-xs text-white/60 flex items-start gap-1 mb-1">
                    <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0 text-blue-400" />
                    {action}
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          {/* Top Performers */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <h2 className="font-semibold">Top Performers</h2>
              </div>
              <span className="text-xs text-white/40 bg-green-900/30 px-2 py-1 rounded">
                Últimos 90 dias
              </span>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-12 bg-white/5 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : performanceData?.top_performers?.length ? (
              <div className="space-y-3">
                {performanceData.top_performers.map((performer) => (
                  <div key={performer.rank} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                      ${performer.rank === 1 ? 'bg-yellow-500/20 text-yellow-400' :
                        performer.rank === 2 ? 'bg-gray-400/20 text-gray-300' :
                        performer.rank === 3 ? 'bg-orange-600/20 text-orange-400' :
                        'bg-white/10 text-white/60'}`}>
                      {performer.rank}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{performer.employee_name}</div>
                      <div className="text-xs text-white/40">
                        {performer.highlights[0] || 'Excelente performance'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-green-400">{performer.score}</div>
                      <div className="text-xs text-white/40">score</div>
                    </div>
                    {performer.eligible_for_promotion && (
                      <div className="text-xs bg-purple-900/40 text-purple-400 px-2 py-0.5 rounded">
                        Promoção
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-white/40">
                <Users className="w-6 h-6 mr-2" />
                Nenhum dado disponível
              </div>
            )}

            {performanceData && (
              <div className="mt-4 grid grid-cols-5 gap-1">
                {Object.entries(performanceData.score_distribution).map(([key, val]) => (
                  <div key={key} className="text-center">
                    <div className={`text-lg font-bold ${
                      key === 'excelente' ? 'text-green-400' :
                      key === 'bom' ? 'text-blue-400' :
                      key === 'satisfatorio' ? 'text-yellow-400' :
                      key === 'atencao' ? 'text-orange-400' : 'text-red-400'
                    }`}>{val}</div>
                    <div className="text-xs text-white/30 capitalize">{key.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Agentes de IA */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-yellow-400" />
            <h2 className="font-semibold">Agentes de IA Ativos</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {commandData?.agents_status ? (
              Object.entries(commandData.agents_status).map(([key, status]) => (
                <div key={key} className="flex flex-col items-center p-3 bg-white/5 rounded-lg text-center">
                  <div className="text-xl mb-1">{AGENT_NAMES[key]?.split(' ')[0] || '🤖'}</div>
                  <div className="text-xs text-white/70 mb-1">
                    {AGENT_NAMES[key]?.split(' ').slice(1).join(' ') || key}
                  </div>
                  <div className={`text-xs px-2 py-0.5 rounded-full ${
                    status === 'active' ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'
                  }`}>
                    {status === 'active' ? 'Ativo' : 'Inativo'}
                  </div>
                </div>
              ))
            ) : (
              [1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="h-20 bg-white/5 rounded-lg animate-pulse" />
              ))
            )}
          </div>
        </div>

        {/* Resumo Semanal */}
        {commandData?.weekly_risk_map?.summary && (
          <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/20 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-5 h-5 text-purple-400" />
              <h2 className="font-semibold">Resumo Semanal da IA</h2>
            </div>
            <p className="text-sm text-white/70">{commandData.weekly_risk_map.summary}</p>
            <div className="mt-3 flex items-center gap-2 text-xs text-white/40">
              <Brain className="w-3 h-3" />
              Análise gerada pelos agentes de IA Conecta PRO
            </div>
          </div>
        )}

        {/* Links rápidos */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { href: '/modulos/operacional/escalas', icon: Clock, label: 'Ver Escalas', color: 'blue' },
            { href: '/modulos/operacional/substituicoes', icon: RefreshCw, label: 'Substituições', color: 'green' },
            { href: '/modulos/operacional/colaboradores', icon: Users, label: 'Colaboradores', color: 'purple' },
            { href: '/modulos/operacional/kpi', icon: BarChart2, label: 'KPI & Métricas', color: 'orange' },
          ].map((link) => (
            <Link key={link.href} href={link.href}>
              <div className={`p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all cursor-pointer flex items-center gap-3`}>
                <link.icon className={`w-5 h-5 text-${link.color}-400`} />
                <span className="text-sm font-medium">{link.label}</span>
                <ChevronRight className="w-4 h-4 text-white/30 ml-auto" />
              </div>
            </Link>
          ))}
        </div>

        {/* Bartolo 3.0 Chat */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-sm">🤖</div>
            <div>
              <h2 className="font-semibold">Bartolo 3.0</h2>
              <p className="text-xs text-white/40">Assistente Operacional Inteligente</p>
            </div>
            <div className="ml-auto flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <span className="text-xs text-green-400">Online</span>
            </div>
          </div>

          {/* Messages */}
          <div className="h-48 overflow-y-auto space-y-3 mb-4 p-3 bg-black/20 rounded-lg">
            {bartoloChatHistory.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] text-sm px-3 py-2 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white/10 text-white/80'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {bartoloLoading && (
              <div className="flex justify-start">
                <div className="bg-white/10 text-white/60 text-sm px-3 py-2 rounded-lg">
                  <span className="animate-pulse">Bartolo está pensando...</span>
                </div>
              </div>
            )}
            {bartoloChatHistory.length === 0 && (
              <div className="flex items-center justify-center h-full text-white/30 text-sm">
                Olá! Pergunte qualquer coisa sobre a operação.
              </div>
            )}
          </div>

          {/* Suggestions */}
          {bartoloSuggestions.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {bartoloSuggestions.map((s, idx) => (
                <button key={idx} onClick={() => handleBartolSend(s)} className="text-xs px-2 py-1 bg-white/10 hover:bg-white/20 rounded-full text-white/60 transition-all">
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={bartoloInput}
              onChange={(e) => setBartoloInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleBartolSend(bartoloInput)}
              placeholder="Pergunte ao Bartolo..."
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/30 focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={() => handleBartolSend(bartoloInput)}
              disabled={!bartoloInput.trim() || bartoloLoading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm text-white transition-all"
            >
              Enviar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
