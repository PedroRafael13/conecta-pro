'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bot,
  Brain,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Search,
  Send,
  MessageSquare,
  BarChart3,
  Target,
  Lightbulb,
  Zap,
  Clock,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Avatar,
  StatCard,
  StatGrid,
} from '@/design-system/components';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Mock Data
const aiUsageData = [
  { date: '09/01', queries: 45, predictions: 12, automations: 8 },
  { date: '10/01', queries: 62, predictions: 15, automations: 10 },
  { date: '11/01', queries: 58, predictions: 18, automations: 12 },
  { date: '12/01', queries: 71, predictions: 22, automations: 15 },
  { date: '13/01', queries: 85, predictions: 25, automations: 18 },
  { date: '14/01', queries: 92, predictions: 28, automations: 22 },
  { date: '15/01', queries: 78, predictions: 30, automations: 25 },
];

const recentInsights = [
  {
    id: '1',
    type: 'prediction',
    title: 'Risco de churn identificado',
    description: 'Cliente "Tech Park" apresenta sinais de insatisfação. Score de churn: 72%',
    severity: 'warning',
    timestamp: '2026-01-15T14:30:00',
    actionable: true,
  },
  {
    id: '2',
    type: 'optimization',
    title: 'Otimização de escala sugerida',
    description: 'Redução de 15% nos custos de HE possível com reorganização de turnos',
    severity: 'info',
    timestamp: '2026-01-15T12:00:00',
    actionable: true,
  },
  {
    id: '3',
    type: 'anomaly',
    title: 'Anomalia em pagamentos detectada',
    description: 'Padrão incomum de despesas identificado na categoria "Fornecedores"',
    severity: 'danger',
    timestamp: '2026-01-15T10:00:00',
    actionable: true,
  },
  {
    id: '4',
    type: 'forecast',
    title: 'Previsão de receita atualizada',
    description: 'Receita projetada para Fevereiro: R$ 680.000 (+8% vs estimativa anterior)',
    severity: 'success',
    timestamp: '2026-01-15T08:00:00',
    actionable: false,
  },
];

const chatMessages = [
  {
    id: '1',
    role: 'user',
    content: 'Qual o status dos contratos que vencem nos próximos 90 dias?',
    timestamp: '2026-01-15T14:28:00',
  },
  {
    id: '2',
    role: 'assistant',
    content: 'Encontrei 3 contratos com vencimento nos próximos 90 dias:\n\n1. **Condomínio Aurora** - Vence em 01/02/2026 - Valor: R$ 45.000/mês - Auto-renovação: Sim\n2. **Shopping Center Norte** - Vence em 15/03/2026 - Valor: R$ 128.000/mês - Auto-renovação: Sim\n3. **Universidade Federal** - Vence em 31/12/2025 - Valor: R$ 67.000/mês - Auto-renovação: Não (EXPIRADO)\n\nRecomendo priorizar a renovação do contrato da Universidade Federal, que já está expirado.',
    timestamp: '2026-01-15T14:28:30',
  },
];

const aiCapabilities = [
  {
    id: 'bartolo',
    name: 'Bartolo',
    description: 'Assistente virtual inteligente para consultas e análises',
    icon: Bot,
    status: 'active',
    usage: 892,
  },
  {
    id: 'predictions',
    name: 'Previsões',
    description: 'Análise preditiva de receitas, custos e tendências',
    icon: TrendingUp,
    status: 'active',
    usage: 156,
  },
  {
    id: 'anomalies',
    name: 'Detecção de Anomalias',
    description: 'Identificação automática de padrões incomuns',
    icon: AlertTriangle,
    status: 'active',
    usage: 45,
  },
  {
    id: 'optimization',
    name: 'Otimização',
    description: 'Sugestões de melhoria operacional e financeira',
    icon: Target,
    status: 'active',
    usage: 78,
  },
];

const severityConfig = {
  success: { color: 'success' as const, icon: CheckCircle2 },
  info: { color: 'info' as const, icon: Lightbulb },
  warning: { color: 'warning' as const, icon: AlertTriangle },
  danger: { color: 'danger' as const, icon: AlertTriangle },
};

export function AIHubPage() {
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState(chatMessages);

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;

    const newMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: chatInput,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, newMessage]);
    setChatInput('');

    // Simulate AI response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Analisando sua solicitação... Por favor, aguarde enquanto processo as informações.',
          timestamp: new Date().toISOString(),
        },
      ]);
    }, 1000);
  };

  // Stats
  const totalQueries = aiUsageData.reduce((acc, d) => acc + d.queries, 0);
  const totalPredictions = aiUsageData.reduce((acc, d) => acc + d.predictions, 0);
  const totalAutomations = aiUsageData.reduce((acc, d) => acc + d.automations, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Brain className="w-8 h-8 text-accent-primary" />
              Intelligence Hub
            </h1>
            <p className="text-text-secondary mt-1">
              Análises, previsões e automações com IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
              Atualizar Análises
            </Button>
            <Button variant="primary" leftIcon={<Sparkles className="w-4 h-4" />}>
              Gerar Insights
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatCard
              title="Consultas IA"
              value={totalQueries}
              change={18}
              icon={<MessageSquare className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatCard
              title="Previsões Geradas"
              value={totalPredictions}
              change={25}
              icon={<TrendingUp className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatCard
              title="Automações"
              value={totalAutomations}
              change={32}
              icon={<Zap className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatCard
              title="Precisão Média"
              value="94.2%"
              change={2.1}
              icon={<Target className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
        </StatGrid>

        {/* Main Content */}
        <div className="grid grid-cols-3 gap-6">
          {/* AI Chat - Bartolo */}
          <Card className="col-span-2 flex flex-col h-[600px]">
            <CardHeader
              title="Bartolo"
              subtitle="Assistente Virtual Inteligente"
              action={
                <Badge variant="success" leftIcon={<Sparkles className="w-3 h-3" />}>
                  Online
                </Badge>
              }
            />
            <CardBody className="flex-1 flex flex-col p-0">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}
                  >
                    {message.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-accent-primary/20 flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-accent-primary" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] p-4 rounded-2xl ${
                        message.role === 'user'
                          ? 'bg-accent-primary text-white'
                          : 'bg-bg-tertiary text-text-primary'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-white/70' : 'text-text-muted'}`}>
                        {new Date(message.timestamp).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    {message.role === 'user' && (
                      <Avatar name="Usuário" size="sm" />
                    )}
                  </div>
                ))}
              </div>

              {/* Input */}
              <div className="p-4 border-t border-border">
                <div className="flex items-center gap-3">
                  <Input
                    placeholder="Pergunte algo ao Bartolo..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1"
                  />
                  <Button
                    variant="primary"
                    onClick={handleSendMessage}
                    disabled={!chatInput.trim()}
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <Button variant="ghost" size="sm">Resumo financeiro</Button>
                  <Button variant="ghost" size="sm">Contratos vencendo</Button>
                  <Button variant="ghost" size="sm">Análise de desempenho</Button>
                </div>
              </div>
            </CardBody>
          </Card>

          {/* Insights */}
          <Card className="h-[600px] flex flex-col">
            <CardHeader title="Insights Recentes" />
            <CardBody className="flex-1 overflow-y-auto p-0">
              <div className="divide-y divide-border">
                {recentInsights.map((insight) => {
                  const severity = severityConfig[insight.severity];
                  const SeverityIcon = severity.icon;
                  return (
                    <div
                      key={insight.id}
                      className="p-4 hover:bg-bg-tertiary/50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg bg-${severity.color}/10`}>
                          <SeverityIcon className={`w-4 h-4 text-${severity.color}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-text-primary text-sm">
                            {insight.title}
                          </p>
                          <p className="text-xs text-text-secondary mt-1 line-clamp-2">
                            {insight.description}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs text-text-muted">
                              {new Date(insight.timestamp).toLocaleTimeString('pt-BR', {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                            {insight.actionable && (
                              <Badge variant="secondary" size="sm">
                                Ação recomendada
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Usage Chart & Capabilities */}
        <div className="grid grid-cols-3 gap-6">
          {/* Usage Chart */}
          <Card className="col-span-2">
            <CardHeader title="Uso de IA" subtitle="Últimos 7 dias" />
            <CardBody>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={aiUsageData}>
                    <defs>
                      <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorPredictions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px',
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="queries"
                      name="Consultas"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#colorQueries)"
                    />
                    <Area
                      type="monotone"
                      dataKey="predictions"
                      name="Previsões"
                      stroke="#10b981"
                      fillOpacity={1}
                      fill="url(#colorPredictions)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardBody>
          </Card>

          {/* AI Capabilities */}
          <Card>
            <CardHeader title="Capacidades IA" />
            <CardBody>
              <div className="space-y-4">
                {aiCapabilities.map((capability) => {
                  const Icon = capability.icon;
                  return (
                    <div
                      key={capability.id}
                      className="p-3 bg-bg-tertiary rounded-lg hover:bg-bg-tertiary/80 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-accent-primary/10">
                          <Icon className="w-5 h-5 text-accent-primary" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-text-primary text-sm">
                            {capability.name}
                          </p>
                          <p className="text-xs text-text-muted">
                            {capability.usage} usos este mês
                          </p>
                        </div>
                        <Badge variant="success" size="sm">
                          Ativo
                        </Badge>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}
