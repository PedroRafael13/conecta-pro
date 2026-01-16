'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  Send,
  Mic,
  MicOff,
  Paperclip,
  Image,
  FileText,
  Settings,
  Sparkles,
  Clock,
  Trash2,
  Download,
  Copy,
  Check,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  ChevronDown,
  Search,
  Filter,
  Star,
  MessageSquare,
  Brain,
  TrendingUp,
  AlertTriangle,
  FileQuestion,
  Calculator,
  Calendar,
  Users,
  Building2,
  BarChart3,
  PieChart,
  Activity,
  Zap,
  History,
  Bookmark,
  Share2,
  MoreVertical,
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
  Tooltip,
  Modal,
  Dropdown,
  Tabs,
  Tab,
  EmptyState,
} from '@/design-system/components';

// Types
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  attachments?: Attachment[];
  feedback?: 'positive' | 'negative';
  isTyping?: boolean;
  suggestions?: string[];
  actions?: MessageAction[];
}

interface Attachment {
  id: string;
  name: string;
  type: 'image' | 'document' | 'audio';
  url: string;
  size: number;
}

interface MessageAction {
  id: string;
  label: string;
  type: 'link' | 'action' | 'report';
  url?: string;
  action?: string;
}

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  unread: boolean;
  starred: boolean;
}

interface QuickAction {
  id: string;
  icon: React.ElementType;
  label: string;
  description: string;
  prompt: string;
  category: string;
}

// Mock Data
const mockConversations: Conversation[] = [
  {
    id: '1',
    title: 'Análise de Contratos',
    lastMessage: 'Encontrei 3 contratos que precisam de atenção...',
    timestamp: '2026-01-16T10:30:00',
    unread: true,
    starred: true,
  },
  {
    id: '2',
    title: 'Previsão de Receitas',
    lastMessage: 'A receita projetada para o próximo trimestre é...',
    timestamp: '2026-01-15T16:45:00',
    unread: false,
    starred: false,
  },
  {
    id: '3',
    title: 'Otimização de Escalas',
    lastMessage: 'Sugiro a seguinte reorganização para reduzir custos...',
    timestamp: '2026-01-15T09:20:00',
    unread: false,
    starred: true,
  },
  {
    id: '4',
    title: 'Análise de Inadimplência',
    lastMessage: 'Os clientes com maior risco de inadimplência são...',
    timestamp: '2026-01-14T14:10:00',
    unread: false,
    starred: false,
  },
  {
    id: '5',
    title: 'Relatório Mensal',
    lastMessage: 'O relatório de janeiro está pronto para revisão...',
    timestamp: '2026-01-13T11:00:00',
    unread: false,
    starred: false,
  },
];

const mockMessages: Message[] = [
  {
    id: '1',
    role: 'system',
    content: 'Olá! Sou o Bartolo, seu assistente virtual inteligente. Como posso ajudar você hoje?',
    timestamp: '2026-01-16T10:00:00',
    suggestions: [
      'Resumo financeiro do mês',
      'Contratos próximos do vencimento',
      'Análise de desempenho operacional',
      'Previsão de fluxo de caixa',
    ],
  },
  {
    id: '2',
    role: 'user',
    content: 'Qual é o resumo financeiro do mês atual?',
    timestamp: '2026-01-16T10:05:00',
  },
  {
    id: '3',
    role: 'assistant',
    content: `📊 **Resumo Financeiro - Janeiro 2026**

**Receitas:**
- Total Faturado: R$ 1.245.678,00
- Recebido: R$ 987.432,00 (79,3%)
- A Receber: R$ 258.246,00

**Despesas:**
- Folha de Pagamento: R$ 456.789,00
- Fornecedores: R$ 123.456,00
- Operacional: R$ 78.901,00

**Resultado Parcial:** R$ 328.286,00 (positivo)

**Destaques:**
✅ Receitas 12% acima do mesmo período do ano anterior
⚠️ 3 clientes com faturas vencidas há mais de 30 dias
📈 Margem operacional em 26,3%

Deseja que eu detalhe algum item específico?`,
    timestamp: '2026-01-16T10:05:30',
    actions: [
      { id: '1', label: 'Ver Detalhes', type: 'link', url: '/financial' },
      { id: '2', label: 'Exportar Relatório', type: 'action', action: 'export_report' },
      { id: '3', label: 'Agendar Análise', type: 'action', action: 'schedule_analysis' },
    ],
    feedback: undefined,
  },
];

const quickActions: QuickAction[] = [
  {
    id: '1',
    icon: TrendingUp,
    label: 'Análise Financeira',
    description: 'Resumo de receitas, despesas e fluxo de caixa',
    prompt: 'Faça uma análise financeira completa do período atual',
    category: 'Financeiro',
  },
  {
    id: '2',
    icon: Users,
    label: 'Performance RH',
    description: 'Métricas de funcionários e produtividade',
    prompt: 'Analise a performance de RH e indicadores de funcionários',
    category: 'RH',
  },
  {
    id: '3',
    icon: AlertTriangle,
    label: 'Alertas Críticos',
    description: 'Situações que precisam de atenção imediata',
    prompt: 'Quais são os alertas críticos que precisam de atenção?',
    category: 'Alertas',
  },
  {
    id: '4',
    icon: FileText,
    label: 'Contratos',
    description: 'Status e vencimentos de contratos',
    prompt: 'Mostre o status dos contratos e quais estão próximos do vencimento',
    category: 'Contratos',
  },
  {
    id: '5',
    icon: Calculator,
    label: 'Previsões',
    description: 'Projeções financeiras e operacionais',
    prompt: 'Gere previsões para os próximos 3 meses',
    category: 'Previsões',
  },
  {
    id: '6',
    icon: Building2,
    label: 'Clientes',
    description: 'Análise de carteira de clientes',
    prompt: 'Faça uma análise da carteira de clientes atual',
    category: 'Comercial',
  },
  {
    id: '7',
    icon: Calendar,
    label: 'Agenda',
    description: 'Compromissos e lembretes importantes',
    prompt: 'Quais são os compromissos e prazos importantes desta semana?',
    category: 'Agenda',
  },
  {
    id: '8',
    icon: BarChart3,
    label: 'KPIs',
    description: 'Indicadores-chave de performance',
    prompt: 'Mostre os principais KPIs do negócio',
    category: 'KPIs',
  },
];

const behavioralInsights = [
  {
    id: '1',
    title: 'Padrão de Consultas',
    description: 'Você costuma consultar dados financeiros nas segundas-feiras',
    icon: Activity,
  },
  {
    id: '2',
    title: 'Tópico Frequente',
    description: 'Análise de contratos é seu assunto mais consultado',
    icon: FileText,
  },
  {
    id: '3',
    title: 'Sugestão Personalizada',
    description: 'Considere automatizar relatórios semanais de receitas',
    icon: Sparkles,
  },
];

export function BartoloPage() {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [conversations, setConversations] = useState(mockConversations);
  const [activeConversation, setActiveConversation] = useState<string>('1');
  const [showSidebar, setShowSidebar] = useState(true);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSendMessage = useCallback(() => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateResponse(inputValue),
        timestamp: new Date().toISOString(),
        suggestions: ['Mais detalhes', 'Exportar dados', 'Nova análise'],
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  }, [inputValue]);

  const generateResponse = (query: string): string => {
    // Simulate different responses based on query
    if (query.toLowerCase().includes('financeiro') || query.toLowerCase().includes('receita')) {
      return `📊 **Análise Financeira Rápida**

Com base nos dados atuais:
- Receita mensal: R$ 1.2M (+8% vs mês anterior)
- Margem líquida: 24.5%
- Inadimplência: 3.2% (dentro do esperado)

Posso detalhar algum aspecto específico?`;
    }
    if (query.toLowerCase().includes('contrato')) {
      return `📋 **Status de Contratos**

**Ativos:** 45 contratos
**Vencendo em 30 dias:** 3 contratos
**Valor total:** R$ 2.8M/mês

Contratos que precisam de atenção:
1. Condomínio Aurora - Vence em 15/02
2. Shopping Norte - Renovação pendente
3. Tech Park - Negociação em andamento

Deseja que eu prepare o relatório completo?`;
    }
    return `Entendi sua solicitação sobre "${query}".

Estou analisando os dados disponíveis para fornecer as informações mais relevantes.

Enquanto isso, posso ajudar com:
- Análises financeiras
- Status de contratos
- Métricas operacionais
- Previsões e projeções

O que você gostaria de explorar?`;
  };

  const handleQuickAction = useCallback((prompt: string) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  }, []);

  const handleFeedback = useCallback((messageId: string, feedback: 'positive' | 'negative') => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, feedback } : msg
      )
    );
  }, []);

  const handleCopyMessage = useCallback((messageId: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedMessageId(messageId);
    setTimeout(() => setCopiedMessageId(null), 2000);
  }, []);

  const toggleConversationStar = useCallback((conversationId: string) => {
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === conversationId ? { ...conv, starred: !conv.starred } : conv
      )
    );
  }, []);

  const handleNewConversation = useCallback(() => {
    const newConv: Conversation = {
      id: Date.now().toString(),
      title: 'Nova Conversa',
      lastMessage: '',
      timestamp: new Date().toISOString(),
      unread: false,
      starred: false,
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveConversation(newConv.id);
    setMessages([mockMessages[0]]); // Reset to welcome message
  }, []);

  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="flex h-[calc(100vh-140px)] bg-bg-secondary rounded-xl overflow-hidden border border-border">
        {/* Sidebar */}
        <AnimatePresence>
          {showSidebar && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 320, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              className="border-r border-border bg-bg-primary flex flex-col"
            >
              {/* Sidebar Header */}
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary to-purple-600 flex items-center justify-center">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="font-bold text-text-primary">Bartolo</h2>
                      <p className="text-xs text-text-muted">Assistente IA</p>
                    </div>
                  </div>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleNewConversation}
                  >
                    <MessageSquare className="w-4 h-4" />
                  </Button>
                </div>

                {/* Search */}
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                  <Input
                    placeholder="Buscar conversas..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Conversations List */}
              <div className="flex-1 overflow-y-auto">
                <div className="p-2">
                  <p className="text-xs text-text-muted px-2 py-1 uppercase font-medium">
                    Conversas Recentes
                  </p>
                  {filteredConversations.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => setActiveConversation(conv.id)}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        activeConversation === conv.id
                          ? 'bg-accent-primary/10 border border-accent-primary/30'
                          : 'hover:bg-bg-tertiary'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-sm text-text-primary truncate">
                              {conv.title}
                            </p>
                            {conv.unread && (
                              <div className="w-2 h-2 bg-accent-primary rounded-full" />
                            )}
                          </div>
                          <p className="text-xs text-text-muted truncate mt-1">
                            {conv.lastMessage}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 ml-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleConversationStar(conv.id);
                            }}
                            className="p-1 hover:bg-bg-tertiary rounded"
                          >
                            <Star
                              className={`w-3 h-3 ${
                                conv.starred
                                  ? 'fill-yellow-400 text-yellow-400'
                                  : 'text-text-muted'
                              }`}
                            />
                          </button>
                        </div>
                      </div>
                      <p className="text-xs text-text-muted mt-2">
                        {new Date(conv.timestamp).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Behavioral Insights */}
                <div className="p-4 border-t border-border">
                  <p className="text-xs text-text-muted uppercase font-medium mb-3">
                    Insights Comportamentais
                  </p>
                  {behavioralInsights.map((insight) => {
                    const Icon = insight.icon;
                    return (
                      <div
                        key={insight.id}
                        className="p-2 rounded-lg hover:bg-bg-tertiary transition-colors mb-2"
                      >
                        <div className="flex items-start gap-2">
                          <div className="p-1.5 rounded bg-accent-primary/10">
                            <Icon className="w-3 h-3 text-accent-primary" />
                          </div>
                          <div>
                            <p className="text-xs font-medium text-text-primary">
                              {insight.title}
                            </p>
                            <p className="text-xs text-text-muted">
                              {insight.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Sidebar Footer */}
              <div className="p-4 border-t border-border">
                <Button
                  variant="secondary"
                  size="sm"
                  className="w-full"
                  leftIcon={<Settings className="w-4 h-4" />}
                  onClick={() => setSettingsOpen(true)}
                >
                  Configurações
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Chat Header */}
          <div className="p-4 border-b border-border bg-bg-primary">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSidebar(!showSidebar)}
                >
                  <ChevronDown
                    className={`w-4 h-4 transition-transform ${
                      showSidebar ? 'rotate-90' : '-rotate-90'
                    }`}
                  />
                </Button>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-purple-600 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium text-text-primary">Bartolo</h3>
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-xs text-text-muted">Online</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Tooltip content="Histórico">
                  <Button variant="ghost" size="sm">
                    <History className="w-4 h-4" />
                  </Button>
                </Tooltip>
                <Tooltip content="Compartilhar">
                  <Button variant="ghost" size="sm">
                    <Share2 className="w-4 h-4" />
                  </Button>
                </Tooltip>
                <Tooltip content="Download">
                  <Button variant="ghost" size="sm">
                    <Download className="w-4 h-4" />
                  </Button>
                </Tooltip>
                <Dropdown
                  trigger={
                    <Button variant="ghost" size="sm">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  }
                  items={[
                    { label: 'Limpar conversa', icon: <Trash2 className="w-4 h-4" /> },
                    { label: 'Exportar PDF', icon: <Download className="w-4 h-4" /> },
                    { label: 'Configurações', icon: <Settings className="w-4 h-4" /> },
                  ]}
                />
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : ''
                }`}
              >
                {message.role !== 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-purple-600 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[70%] ${
                    message.role === 'user'
                      ? 'bg-accent-primary text-white rounded-2xl rounded-tr-sm'
                      : message.role === 'system'
                      ? 'bg-bg-tertiary/50 text-text-primary rounded-2xl'
                      : 'bg-bg-tertiary text-text-primary rounded-2xl rounded-tl-sm'
                  } p-4`}
                >
                  <div className="prose prose-sm prose-invert max-w-none">
                    <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                  </div>

                  {/* Actions */}
                  {message.actions && (
                    <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-white/10">
                      {message.actions.map((action) => (
                        <Button
                          key={action.id}
                          variant="secondary"
                          size="sm"
                          className="!bg-white/10 !text-white hover:!bg-white/20"
                        >
                          {action.label}
                        </Button>
                      ))}
                    </div>
                  )}

                  {/* Suggestions */}
                  {message.suggestions && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {message.suggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleQuickAction(suggestion)}
                          className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
                            message.role === 'user'
                              ? 'bg-white/20 hover:bg-white/30 text-white'
                              : 'bg-accent-primary/10 hover:bg-accent-primary/20 text-accent-primary'
                          }`}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Message Footer */}
                  <div className="flex items-center justify-between mt-3 pt-2">
                    <span
                      className={`text-xs ${
                        message.role === 'user' ? 'text-white/60' : 'text-text-muted'
                      }`}
                    >
                      {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>

                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-1">
                        <Tooltip content="Copiar">
                          <button
                            onClick={() => handleCopyMessage(message.id, message.content)}
                            className="p-1 hover:bg-bg-tertiary rounded"
                          >
                            {copiedMessageId === message.id ? (
                              <Check className="w-3 h-3 text-green-500" />
                            ) : (
                              <Copy className="w-3 h-3 text-text-muted" />
                            )}
                          </button>
                        </Tooltip>
                        <Tooltip content="Útil">
                          <button
                            onClick={() => handleFeedback(message.id, 'positive')}
                            className={`p-1 hover:bg-bg-tertiary rounded ${
                              message.feedback === 'positive' ? 'text-green-500' : ''
                            }`}
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                        </Tooltip>
                        <Tooltip content="Não útil">
                          <button
                            onClick={() => handleFeedback(message.id, 'negative')}
                            className={`p-1 hover:bg-bg-tertiary rounded ${
                              message.feedback === 'negative' ? 'text-red-500' : ''
                            }`}
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>
                        </Tooltip>
                      </div>
                    )}
                  </div>
                </div>
                {message.role === 'user' && <Avatar name="Usuário" size="sm" />}
              </motion.div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3"
              >
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-purple-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-bg-tertiary rounded-2xl rounded-tl-sm p-4">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-text-muted rounded-full animate-bounce" />
                    <span
                      className="w-2 h-2 bg-text-muted rounded-full animate-bounce"
                      style={{ animationDelay: '0.1s' }}
                    />
                    <span
                      className="w-2 h-2 bg-text-muted rounded-full animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          {messages.length <= 2 && (
            <div className="px-6 pb-4">
              <p className="text-sm text-text-muted mb-3">Ações rápidas:</p>
              <div className="grid grid-cols-4 gap-2">
                {quickActions.slice(0, 8).map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.id}
                      onClick={() => handleQuickAction(action.prompt)}
                      className="p-3 rounded-lg bg-bg-tertiary hover:bg-bg-tertiary/80 transition-colors text-left group"
                    >
                      <Icon className="w-5 h-5 text-accent-primary mb-2 group-hover:scale-110 transition-transform" />
                      <p className="text-xs font-medium text-text-primary">
                        {action.label}
                      </p>
                      <p className="text-xs text-text-muted line-clamp-1">
                        {action.description}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="p-4 border-t border-border bg-bg-primary">
            <div className="flex items-end gap-3">
              {/* Attachment Button */}
              <Dropdown
                trigger={
                  <Button variant="ghost" size="sm">
                    <Paperclip className="w-4 h-4" />
                  </Button>
                }
                items={[
                  { label: 'Imagem', icon: <Image className="w-4 h-4" /> },
                  { label: 'Documento', icon: <FileText className="w-4 h-4" /> },
                ]}
              />

              {/* Input */}
              <div className="flex-1 relative">
                <Input
                  ref={inputRef}
                  placeholder="Pergunte algo ao Bartolo..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  className="pr-12"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                  <Tooltip content={isRecording ? 'Parar gravação' : 'Gravar voz'}>
                    <button
                      onClick={() => setIsRecording(!isRecording)}
                      className={`p-1.5 rounded-lg transition-colors ${
                        isRecording
                          ? 'bg-red-500 text-white'
                          : 'hover:bg-bg-tertiary text-text-muted'
                      }`}
                    >
                      {isRecording ? (
                        <MicOff className="w-4 h-4" />
                      ) : (
                        <Mic className="w-4 h-4" />
                      )}
                    </button>
                  </Tooltip>
                </div>
              </div>

              {/* Send Button */}
              <Button
                variant="primary"
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>

            {/* Helper Text */}
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs text-text-muted">
                Pressione Enter para enviar, Shift+Enter para nova linha
              </p>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" size="sm">
                  <Sparkles className="w-3 h-3 mr-1" />
                  GPT-4 Turbo
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Modal */}
      <Modal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        title="Configurações do Bartolo"
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-text-primary">
              Personalidade
            </label>
            <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
              <option>Profissional</option>
              <option>Amigável</option>
              <option>Técnico</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">
              Idioma das respostas
            </label>
            <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
              <option>Português (Brasil)</option>
              <option>English</option>
              <option>Español</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">
              Nível de detalhe
            </label>
            <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
              <option>Resumido</option>
              <option>Normal</option>
              <option>Detalhado</option>
            </select>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-primary">Notificações de insights</span>
            <input type="checkbox" defaultChecked className="toggle" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-primary">Salvar histórico</span>
            <input type="checkbox" defaultChecked className="toggle" />
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}

export default BartoloPage;
