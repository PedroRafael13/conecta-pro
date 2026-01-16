'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Send,
  Bot,
  User,
  Search,
  Filter,
  Calendar,
  Clock,
  Star,
  Trash2,
  Archive,
  MoreVertical,
  Plus,
  ChevronLeft,
  ChevronRight,
  Download,
  Share2,
  Pin,
  Tag,
  Sparkles,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Settings,
  Bookmark,
  History,
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
  EmptyState,
} from '@/design-system/components';

// Types
interface ChatSession {
  id: string;
  title: string;
  preview: string;
  timestamp: string;
  starred: boolean;
  pinned: boolean;
  archived: boolean;
  unread: boolean;
  tags: string[];
  messageCount: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  feedback?: 'positive' | 'negative';
}

// Mock Data
const mockSessions: ChatSession[] = [
  {
    id: '1',
    title: 'Análise de Receitas Janeiro',
    preview: 'A receita do mês de janeiro apresentou crescimento de 12%...',
    timestamp: '2026-01-16T10:30:00',
    starred: true,
    pinned: true,
    archived: false,
    unread: true,
    tags: ['financeiro', 'relatório'],
    messageCount: 24,
  },
  {
    id: '2',
    title: 'Otimização de Escalas',
    preview: 'Sugiro as seguintes alterações nas escalas...',
    timestamp: '2026-01-15T16:45:00',
    starred: false,
    pinned: false,
    archived: false,
    unread: false,
    tags: ['operacional'],
    messageCount: 15,
  },
  {
    id: '3',
    title: 'Contratos Vencendo',
    preview: 'Existem 3 contratos vencendo nos próximos 30 dias...',
    timestamp: '2026-01-15T09:20:00',
    starred: true,
    pinned: false,
    archived: false,
    unread: false,
    tags: ['contratos', 'urgente'],
    messageCount: 8,
  },
  {
    id: '4',
    title: 'Indicadores de RH',
    preview: 'O turnover do último trimestre foi de 3.2%...',
    timestamp: '2026-01-14T14:10:00',
    starred: false,
    pinned: false,
    archived: false,
    unread: false,
    tags: ['rh'],
    messageCount: 12,
  },
  {
    id: '5',
    title: 'Análise de Inadimplência',
    preview: 'Os principais inadimplentes identificados são...',
    timestamp: '2026-01-13T11:00:00',
    starred: false,
    pinned: false,
    archived: true,
    unread: false,
    tags: ['financeiro', 'cobrança'],
    messageCount: 18,
  },
];

const mockMessages: Message[] = [
  {
    id: '1',
    role: 'user',
    content: 'Qual foi a receita do mês de janeiro?',
    timestamp: '2026-01-16T10:00:00',
  },
  {
    id: '2',
    role: 'assistant',
    content: `📊 **Receita de Janeiro 2026**

A receita do mês de janeiro apresentou os seguintes números:

**Total Faturado:** R$ 1.245.678,00
**Recebido:** R$ 987.432,00 (79.3%)
**A Receber:** R$ 258.246,00

**Comparativo:**
- vs Janeiro 2025: +12.5%
- vs Dezembro 2025: -3.2% (sazonalidade)

**Principais Clientes:**
1. Shopping Center Norte - R$ 128.000
2. Tech Park - R$ 89.000
3. Universidade Federal - R$ 67.000

Deseja mais detalhes sobre algum item específico?`,
    timestamp: '2026-01-16T10:00:30',
    feedback: 'positive',
  },
  {
    id: '3',
    role: 'user',
    content: 'Quais são as perspectivas para fevereiro?',
    timestamp: '2026-01-16T10:05:00',
  },
  {
    id: '4',
    role: 'assistant',
    content: `📈 **Projeção para Fevereiro 2026**

Com base nos dados históricos e contratos ativos:

**Receita Projetada:** R$ 1.320.000,00 (+6% vs Janeiro)

**Fatores Positivos:**
✅ 2 novos contratos iniciando (R$ 85.000/mês)
✅ Renovação do contrato Tech Park confirmada
✅ Sazonalidade favorável

**Pontos de Atenção:**
⚠️ Contrato Condomínio Aurora vence dia 28/02
⚠️ 3 clientes com histórico de atraso

**Recomendações:**
1. Iniciar negociação de renovação com Aurora
2. Intensificar cobrança preventiva
3. Preparar proposta de upsell para Tech Park

Posso detalhar algum desses pontos?`,
    timestamp: '2026-01-16T10:05:30',
  },
];

export function ChatPage() {
  const [sessions, setSessions] = useState(mockSessions);
  const [selectedSession, setSelectedSession] = useState<string>(mockSessions[0].id);
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [inputValue, setInputValue] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterView, setFilterView] = useState<'all' | 'starred' | 'archived'>('all');
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [newChatModalOpen, setNewChatModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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

    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Analisando sua solicitação... Estou processando as informações disponíveis para fornecer a melhor resposta possível.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  }, [inputValue]);

  const handleNewChat = useCallback(() => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: 'Nova Conversa',
      preview: '',
      timestamp: new Date().toISOString(),
      starred: false,
      pinned: false,
      archived: false,
      unread: false,
      tags: [],
      messageCount: 0,
    };
    setSessions((prev) => [newSession, ...prev]);
    setSelectedSession(newSession.id);
    setMessages([]);
    setNewChatModalOpen(false);
  }, []);

  const handleCopyMessage = useCallback((id: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  }, []);

  const handleFeedback = useCallback((id: string, feedback: 'positive' | 'negative') => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, feedback } : msg))
    );
  }, []);

  const toggleStar = useCallback((id: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, starred: !s.starred } : s))
    );
  }, []);

  const togglePin = useCallback((id: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, pinned: !s.pinned } : s))
    );
  }, []);

  const archiveSession = useCallback((id: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, archived: !s.archived } : s))
    );
  }, []);

  const deleteSession = useCallback((id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (selectedSession === id) {
      setSelectedSession(sessions[0]?.id || '');
    }
  }, [selectedSession, sessions]);

  const filteredSessions = sessions.filter((session) => {
    const matchesSearch = session.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filterView === 'all'
        ? !session.archived
        : filterView === 'starred'
        ? session.starred && !session.archived
        : session.archived;
    return matchesSearch && matchesFilter;
  });

  const sortedSessions = [...filteredSessions].sort((a, b) => {
    if (a.pinned && !b.pinned) return -1;
    if (!a.pinned && b.pinned) return 1;
    return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
  });

  const currentSession = sessions.find((s) => s.id === selectedSession);

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
              {/* Header */}
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-bold text-text-primary flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-accent-primary" />
                    Histórico de Chat
                  </h2>
                  <Button variant="primary" size="sm" onClick={handleNewChat}>
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>

                {/* Search */}
                <div className="relative mb-3">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                  <Input
                    placeholder="Buscar conversas..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                {/* Filter Tabs */}
                <div className="flex gap-1 p-1 bg-bg-tertiary rounded-lg">
                  {[
                    { value: 'all', label: 'Todas' },
                    { value: 'starred', label: 'Favoritas' },
                    { value: 'archived', label: 'Arquivadas' },
                  ].map((filter) => (
                    <button
                      key={filter.value}
                      onClick={() => setFilterView(filter.value as typeof filterView)}
                      className={`flex-1 px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                        filterView === filter.value
                          ? 'bg-accent-primary text-white'
                          : 'text-text-muted hover:text-text-primary'
                      }`}
                    >
                      {filter.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Sessions List */}
              <div className="flex-1 overflow-y-auto">
                {sortedSessions.length === 0 ? (
                  <div className="p-4 text-center">
                    <p className="text-sm text-text-muted">Nenhuma conversa encontrada</p>
                  </div>
                ) : (
                  <div className="p-2 space-y-1">
                    {sortedSessions.map((session) => (
                      <div
                        key={session.id}
                        onClick={() => setSelectedSession(session.id)}
                        className={`p-3 rounded-lg cursor-pointer transition-all group ${
                          selectedSession === session.id
                            ? 'bg-accent-primary/10 border border-accent-primary/30'
                            : 'hover:bg-bg-tertiary'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              {session.pinned && (
                                <Pin className="w-3 h-3 text-accent-primary" />
                              )}
                              <p className="font-medium text-sm text-text-primary truncate">
                                {session.title}
                              </p>
                              {session.unread && (
                                <div className="w-2 h-2 bg-accent-primary rounded-full" />
                              )}
                            </div>
                            <p className="text-xs text-text-muted truncate mt-1">
                              {session.preview}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className="text-xs text-text-muted">
                                {new Date(session.timestamp).toLocaleDateString('pt-BR')}
                              </span>
                              <span className="text-xs text-text-muted">•</span>
                              <span className="text-xs text-text-muted">
                                {session.messageCount} msgs
                              </span>
                            </div>
                            {session.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {session.tags.map((tag) => (
                                  <Badge key={tag} variant="secondary" size="sm">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleStar(session.id);
                              }}
                              className="p-1 hover:bg-bg-tertiary rounded"
                            >
                              <Star
                                className={`w-3 h-3 ${
                                  session.starred
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-text-muted'
                                }`}
                              />
                            </button>
                            <Dropdown
                              trigger={
                                <button
                                  onClick={(e) => e.stopPropagation()}
                                  className="p-1 hover:bg-bg-tertiary rounded"
                                >
                                  <MoreVertical className="w-3 h-3 text-text-muted" />
                                </button>
                              }
                              items={[
                                {
                                  label: session.pinned ? 'Desafixar' : 'Fixar',
                                  icon: <Pin className="w-4 h-4" />,
                                  onClick: () => togglePin(session.id),
                                },
                                {
                                  label: session.archived ? 'Desarquivar' : 'Arquivar',
                                  icon: <Archive className="w-4 h-4" />,
                                  onClick: () => archiveSession(session.id),
                                },
                                {
                                  label: 'Excluir',
                                  icon: <Trash2 className="w-4 h-4" />,
                                  onClick: () => deleteSession(session.id),
                                },
                              ]}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-border bg-bg-primary flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSidebar(!showSidebar)}
              >
                {showSidebar ? (
                  <ChevronLeft className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </Button>
              <div>
                <h3 className="font-medium text-text-primary">
                  {currentSession?.title || 'Chat IA'}
                </h3>
                <p className="text-xs text-text-muted">
                  {currentSession?.messageCount || 0} mensagens
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {currentSession && (
                <>
                  <Tooltip content={currentSession.starred ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleStar(currentSession.id)}
                    >
                      <Star
                        className={`w-4 h-4 ${
                          currentSession.starred
                            ? 'fill-yellow-400 text-yellow-400'
                            : ''
                        }`}
                      />
                    </Button>
                  </Tooltip>
                  <Tooltip content="Compartilhar">
                    <Button variant="ghost" size="sm">
                      <Share2 className="w-4 h-4" />
                    </Button>
                  </Tooltip>
                  <Tooltip content="Exportar">
                    <Button variant="ghost" size="sm">
                      <Download className="w-4 h-4" />
                    </Button>
                  </Tooltip>
                </>
              )}
              <Dropdown
                trigger={
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="w-4 h-4" />
                  </Button>
                }
                items={[
                  { label: 'Renomear conversa', icon: <Tag className="w-4 h-4" /> },
                  { label: 'Adicionar tags', icon: <Tag className="w-4 h-4" /> },
                  { label: 'Exportar PDF', icon: <Download className="w-4 h-4" /> },
                  { label: 'Configurações', icon: <Settings className="w-4 h-4" /> },
                ]}
              />
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <EmptyState
                icon={<MessageSquare className="w-12 h-12" />}
                title="Inicie uma conversa"
                description="Digite sua pergunta abaixo para começar"
              />
            ) : (
              messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : ''
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-primary to-purple-600 flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div
                    className={`max-w-[70%] ${
                      message.role === 'user'
                        ? 'bg-accent-primary text-white rounded-2xl rounded-tr-sm'
                        : 'bg-bg-tertiary text-text-primary rounded-2xl rounded-tl-sm'
                    } p-4`}
                  >
                    <p className="whitespace-pre-wrap text-sm">{message.content}</p>
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
                              className="p-1 hover:bg-bg-secondary rounded"
                            >
                              {copiedId === message.id ? (
                                <Check className="w-3 h-3 text-green-500" />
                              ) : (
                                <Copy className="w-3 h-3 text-text-muted" />
                              )}
                            </button>
                          </Tooltip>
                          <Tooltip content="Útil">
                            <button
                              onClick={() => handleFeedback(message.id, 'positive')}
                              className={`p-1 hover:bg-bg-secondary rounded ${
                                message.feedback === 'positive' ? 'text-green-500' : ''
                              }`}
                            >
                              <ThumbsUp className="w-3 h-3" />
                            </button>
                          </Tooltip>
                          <Tooltip content="Não útil">
                            <button
                              onClick={() => handleFeedback(message.id, 'negative')}
                              className={`p-1 hover:bg-bg-secondary rounded ${
                                message.feedback === 'negative' ? 'text-red-500' : ''
                              }`}
                            >
                              <ThumbsDown className="w-3 h-3" />
                            </button>
                          </Tooltip>
                          <Tooltip content="Regenerar">
                            <button className="p-1 hover:bg-bg-secondary rounded">
                              <RefreshCw className="w-3 h-3 text-text-muted" />
                            </button>
                          </Tooltip>
                        </div>
                      )}
                    </div>
                  </div>
                  {message.role === 'user' && <Avatar name="Usuário" size="sm" />}
                </motion.div>
              ))
            )}

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

          {/* Input */}
          <div className="p-4 border-t border-border bg-bg-primary">
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <Input
                  placeholder="Digite sua mensagem..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
              </div>
              <Button
                variant="primary"
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs text-text-muted">
                Pressione Enter para enviar
              </p>
              <Badge variant="secondary" size="sm">
                <Sparkles className="w-3 h-3 mr-1" />
                IA Conecta
              </Badge>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}

export default ChatPage;
