'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/layouts';
import {
  Card,
  Button,
  Badge,
  Input,
  StatCard,
  SimpleTabBar,
  DataTable,
  type Column,
  Modal,
  Select
} from '@/design-system/components';
import {
  MessageSquare,
  TrendingUp,
  TrendingDown,
  Heart,
  Frown,
  Meh,
  Smile,
  Search,
  Filter,
  Download,
  RefreshCw,
  Star,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

// Types
interface SentimentAnalysis {
  id: string;
  source: 'email' | 'whatsapp' | 'chat' | 'survey';
  customer: string;
  message: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  score: number;
  topics: string[];
  date: string;
  resolved: boolean;
}

// Mock data
const mockAnalyses: SentimentAnalysis[] = [
  {
    id: '1',
    source: 'email',
    customer: 'João Silva',
    message: 'Excelente atendimento! Muito satisfeito com a rapidez.',
    sentiment: 'positive',
    score: 0.92,
    topics: ['atendimento', 'rapidez'],
    date: '2026-01-15',
    resolved: true
  },
  {
    id: '2',
    source: 'whatsapp',
    customer: 'Maria Santos',
    message: 'O serviço atrasou, mas foi resolvido adequadamente.',
    sentiment: 'neutral',
    score: 0.55,
    topics: ['atraso', 'resolução'],
    date: '2026-01-15',
    resolved: true
  },
  {
    id: '3',
    source: 'survey',
    customer: 'Pedro Lima',
    message: 'Péssimo atendimento, esperei horas sem resposta.',
    sentiment: 'negative',
    score: 0.15,
    topics: ['atendimento', 'tempo de espera'],
    date: '2026-01-14',
    resolved: false
  }
];

// Chart data
const sentimentTrendData = [
  { date: '01/01', positive: 65, neutral: 25, negative: 10 },
  { date: '05/01', positive: 68, neutral: 22, negative: 10 },
  { date: '10/01', positive: 70, neutral: 20, negative: 10 },
  { date: '15/01', positive: 72, neutral: 18, negative: 10 }
];

const sentimentDistribution = [
  { name: 'Positivo', value: 72, color: '#10b981' },
  { name: 'Neutro', value: 18, color: '#f59e0b' },
  { name: 'Negativo', value: 10, color: '#ef4444' }
];

export function AISentimentPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [filterPeriod, setFilterPeriod] = useState('month');
  const [searchTerm, setSearchTerm] = useState('');

  const tabs = [
    { value: 'overview', label: 'Visão Geral', icon: <Heart className="h-4 w-4" /> },
    { value: 'analyses', label: 'Análises', icon: <MessageSquare className="h-4 w-4" /> },
    { value: 'trends', label: 'Tendências', icon: <TrendingUp className="h-4 w-4" /> }
  ];

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <Smile className="h-4 w-4 text-success" />;
      case 'negative': return <Frown className="h-4 w-4 text-danger" />;
      default: return <Meh className="h-4 w-4 text-warning" />;
    }
  };

  const columns: Column<SentimentAnalysis>[] = [
    {
      key: 'customer',
      header: 'Cliente',
      render: (row) => (
        <div className="flex items-center gap-3">
          {getSentimentIcon(row.sentiment)}
          <div>
            <p className="font-medium text-text-primary">{row.customer}</p>
            <p className="text-sm text-text-secondary capitalize">{row.source}</p>
          </div>
        </div>
      )
    },
    {
      key: 'message',
      header: 'Mensagem',
      render: (row) => (
        <p className="text-text-secondary truncate max-w-md">{row.message}</p>
      )
    },
    {
      key: 'score',
      header: 'Score',
      render: (row) => (
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-bg-tertiary rounded-full max-w-[80px]">
            <div
              className={`h-full rounded-full ${
                row.score >= 0.7 ? 'bg-success' :
                row.score >= 0.4 ? 'bg-warning' : 'bg-danger'
              }`}
              style={{ width: `${row.score * 100}%` }}
            />
          </div>
          <span className="text-sm font-medium">{(row.score * 100).toFixed(0)}%</span>
        </div>
      )
    },
    {
      key: 'topics',
      header: 'Tópicos',
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          {row.topics.slice(0, 2).map((topic) => (
            <Badge key={topic} variant="outline" size="sm">{topic}</Badge>
          ))}
        </div>
      )
    },
    {
      key: 'date',
      header: 'Data',
      render: (row) => (
        <span className="text-text-secondary">
          {new Date(row.date).toLocaleDateString('pt-BR')}
        </span>
      )
    },
    {
      key: 'resolved',
      header: 'Status',
      render: (row) => (
        <Badge variant={row.resolved ? 'success' : 'warning'}>
          {row.resolved ? 'Resolvido' : 'Pendente'}
        </Badge>
      )
    }
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary">
              Análise de Sentimento
            </h1>
            <p className="text-text-secondary mt-1">
              Inteligência artificial para análise de feedback
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Select
              value={filterPeriod}
              onChange={setFilterPeriod}
              options={[
                { value: 'week', label: 'Esta semana' },
                { value: 'month', label: 'Este mês' },
                { value: 'quarter', label: 'Este trimestre' }
              ]}
              className="w-40"
            />
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Sentimento Positivo"
            value="72%"
            icon={<ThumbsUp className="h-5 w-5" />}
            iconColor="success"
            change={5}
            changeLabel="vs. mês anterior"
          />
          <StatCard
            title="NPS Score"
            value="68"
            icon={<Star className="h-5 w-5" />}
            iconColor="success"
            change={8}
            changeLabel="pontos"
          />
          <StatCard
            title="Feedbacks Negativos"
            value="10%"
            icon={<ThumbsDown className="h-5 w-5" />}
            iconColor="danger"
            change={-3}
            changeLabel="redução"
          />
          <StatCard
            title="Análises Realizadas"
            value="1,234"
            icon={<MessageSquare className="h-5 w-5" />}
            iconColor="info"
            change={15}
            changeLabel="este mês"
          />
        </div>

        {/* Tabs */}
        <SimpleTabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sentiment Distribution */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Distribuição de Sentimentos
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {sentimentDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>

            {/* Sentiment Trend */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Evolução do Sentimento
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sentimentTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3d" />
                    <XAxis dataKey="date" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#12121a',
                        border: '1px solid #2d2d3d',
                        borderRadius: '8px'
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="positive"
                      name="Positivo"
                      stackId="1"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="neutral"
                      name="Neutro"
                      stackId="1"
                      stroke="#f59e0b"
                      fill="#f59e0b"
                      fillOpacity={0.6}
                    />
                    <Area
                      type="monotone"
                      dataKey="negative"
                      name="Negativo"
                      stackId="1"
                      stroke="#ef4444"
                      fill="#ef4444"
                      fillOpacity={0.6}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
        )}

        {/* Analyses Tab */}
        {activeTab === 'analyses' && (
          <Card className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="flex-1">
                <Input
                  placeholder="Buscar análises..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>
            <DataTable
              columns={columns}
              data={mockAnalyses}
              keyExtractor={(row) => row.id}
            />
          </Card>
        )}

        {/* Trends Tab */}
        {activeTab === 'trends' && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">
              Tópicos Mais Mencionados
            </h3>
            <div className="space-y-4">
              {[
                { topic: 'Atendimento', mentions: 245, sentiment: 'positive' },
                { topic: 'Preço', mentions: 189, sentiment: 'neutral' },
                { topic: 'Qualidade', mentions: 156, sentiment: 'positive' },
                { topic: 'Tempo de Espera', mentions: 98, sentiment: 'negative' },
                { topic: 'Suporte', mentions: 87, sentiment: 'positive' }
              ].map((item) => (
                <div key={item.topic} className="flex items-center gap-4">
                  <span className="w-32 text-sm text-text-secondary">{item.topic}</span>
                  <div className="flex-1 h-3 bg-bg-tertiary rounded-full">
                    <div
                      className={`h-full rounded-full ${
                        item.sentiment === 'positive' ? 'bg-success' :
                        item.sentiment === 'negative' ? 'bg-danger' : 'bg-warning'
                      }`}
                      style={{ width: `${(item.mentions / 245) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-16 text-right">
                    {item.mentions}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
