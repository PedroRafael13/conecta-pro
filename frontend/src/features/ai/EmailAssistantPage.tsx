'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Mail,
  Send,
  Inbox,
  Star,
  Trash2,
  Archive,
  Tag,
  Search,
  Filter,
  Plus,
  Edit,
  Eye,
  Reply,
  ReplyAll,
  Forward,
  Paperclip,
  Clock,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Bot,
  RefreshCw,
  Settings,
  MoreVertical,
  ChevronDown,
  FileText,
  Users,
  Calendar,
  Zap,
} from 'lucide-react';
import { MainLayout } from '@/layouts';
import {
  Card,
  CardHeader,
  CardBody,
  Button,
  Input,
  Badge,
  Modal,
  Tabs,
  Tab,
  StatCard,
  StatGrid,
  Dropdown,
  Avatar,
  Tooltip,
  EmptyState,
} from '@/design-system/components';

// Types
interface Email {
  id: string;
  from: {
    name: string;
    email: string;
  };
  to: string[];
  subject: string;
  preview: string;
  body: string;
  timestamp: string;
  read: boolean;
  starred: boolean;
  hasAttachment: boolean;
  labels: string[];
  category: 'inbox' | 'sent' | 'draft' | 'trash';
  aiSuggestion?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  priority?: 'high' | 'medium' | 'low';
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  category: string;
}

// Mock Data
const mockEmails: Email[] = [
  {
    id: '1',
    from: { name: 'João Silva', email: 'joao@cliente.com' },
    to: ['admin@conectapro.com.br'],
    subject: 'Dúvida sobre faturamento mensal',
    preview: 'Olá, gostaria de entender melhor como funciona o faturamento...',
    body: 'Olá,\n\nGostaria de entender melhor como funciona o faturamento mensal do serviço. Preciso de uma segunda via da última fatura.\n\nAtenciosamente,\nJoão Silva',
    timestamp: '2026-01-16T10:30:00',
    read: false,
    starred: true,
    hasAttachment: false,
    labels: ['cliente', 'financeiro'],
    category: 'inbox',
    aiSuggestion: 'Este email solicita segunda via de fatura. Sugiro responder com link para portal do cliente.',
    sentiment: 'neutral',
    priority: 'medium',
  },
  {
    id: '2',
    from: { name: 'Maria Santos', email: 'maria@empresa.com' },
    to: ['admin@conectapro.com.br'],
    subject: 'Urgente: Problema com acesso ao sistema',
    preview: 'Não estou conseguindo acessar o sistema desde ontem...',
    body: 'Prezados,\n\nNão estou conseguindo acessar o sistema desde ontem às 15h. Já tentei resetar a senha mas não funcionou.\n\nPreciso urgente de suporte.\n\nMaria Santos',
    timestamp: '2026-01-16T09:15:00',
    read: false,
    starred: false,
    hasAttachment: false,
    labels: ['suporte', 'urgente'],
    category: 'inbox',
    aiSuggestion: 'Email urgente sobre problema de acesso. Verificar logs de autenticação e resetar credenciais.',
    sentiment: 'negative',
    priority: 'high',
  },
  {
    id: '3',
    from: { name: 'Pedro Oliveira', email: 'pedro@fornecedor.com' },
    to: ['admin@conectapro.com.br'],
    subject: 'Proposta comercial - Equipamentos',
    preview: 'Conforme solicitado, segue proposta para fornecimento...',
    body: 'Prezados,\n\nConforme solicitado, segue em anexo nossa proposta comercial para fornecimento de equipamentos.\n\nAguardo retorno.\n\nPedro Oliveira',
    timestamp: '2026-01-15T16:45:00',
    read: true,
    starred: true,
    hasAttachment: true,
    labels: ['fornecedor', 'proposta'],
    category: 'inbox',
    aiSuggestion: 'Proposta comercial recebida. Encaminhar para análise do financeiro.',
    sentiment: 'positive',
    priority: 'medium',
  },
  {
    id: '4',
    from: { name: 'Ana Costa', email: 'ana@cliente.com' },
    to: ['admin@conectapro.com.br'],
    subject: 'Agradecimento pelo atendimento',
    preview: 'Gostaria de agradecer pelo excelente atendimento...',
    body: 'Olá,\n\nGostaria de agradecer pelo excelente atendimento prestado ontem. O problema foi resolvido rapidamente.\n\nObrigada!\nAna Costa',
    timestamp: '2026-01-15T11:20:00',
    read: true,
    starred: false,
    hasAttachment: false,
    labels: ['cliente', 'feedback'],
    category: 'inbox',
    aiSuggestion: 'Feedback positivo. Agradecer e registrar no histórico do cliente.',
    sentiment: 'positive',
    priority: 'low',
  },
];

const mockTemplates: EmailTemplate[] = [
  {
    id: '1',
    name: 'Boas-vindas',
    subject: 'Bem-vindo(a) ao Conecta PRO!',
    body: 'Olá {nome},\n\nSeja bem-vindo(a) ao Conecta PRO!\n\nSeu acesso foi criado com sucesso.\n\nAtenciosamente,\nEquipe Conecta PRO',
    category: 'Onboarding',
  },
  {
    id: '2',
    name: 'Lembrete de Pagamento',
    subject: 'Lembrete: Fatura vencendo em breve',
    body: 'Olá {nome},\n\nSua fatura no valor de {valor} vence em {data}.\n\nAtenciosamente,\nEquipe Financeira',
    category: 'Financeiro',
  },
  {
    id: '3',
    name: 'Confirmação de Agendamento',
    subject: 'Agendamento confirmado',
    body: 'Olá {nome},\n\nSeu agendamento foi confirmado para {data} às {hora}.\n\nAtenciosamente,\nEquipe de Atendimento',
    category: 'Agendamento',
  },
];

const sentimentConfig = {
  positive: { label: 'Positivo', color: 'success' as const, icon: '😊' },
  neutral: { label: 'Neutro', color: 'secondary' as const, icon: '😐' },
  negative: { label: 'Negativo', color: 'danger' as const, icon: '😟' },
};

const priorityConfig = {
  high: { label: 'Alta', color: 'danger' as const },
  medium: { label: 'Média', color: 'warning' as const },
  low: { label: 'Baixa', color: 'secondary' as const },
};

export function EmailAssistantPage() {
  const [emails, setEmails] = useState(mockEmails);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [activeTab, setActiveTab] = useState('inbox');
  const [searchQuery, setSearchQuery] = useState('');
  const [composeOpen, setComposeOpen] = useState(false);
  const [replyOpen, setReplyOpen] = useState(false);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [generatedReply, setGeneratedReply] = useState('');

  const stats = {
    unread: emails.filter((e) => !e.read && e.category === 'inbox').length,
    starred: emails.filter((e) => e.starred).length,
    highPriority: emails.filter((e) => e.priority === 'high' && e.category === 'inbox').length,
    todayReceived: emails.filter((e) =>
      new Date(e.timestamp).toDateString() === new Date().toDateString() && e.category === 'inbox'
    ).length,
  };

  const filteredEmails = emails.filter((email) => {
    const matchesSearch =
      email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      email.from.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTab =
      activeTab === 'starred' ? email.starred : email.category === activeTab;
    return matchesSearch && matchesTab;
  });

  const handleGenerateReply = useCallback(async () => {
    if (!selectedEmail) return;
    setAiGenerating(true);

    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    let reply = '';
    if (selectedEmail.sentiment === 'negative') {
      reply = `Prezado(a) ${selectedEmail.from.name},\n\nLamentamos pelo inconveniente relatado. Nossa equipe técnica já está analisando a situação e entraremos em contato em breve com uma solução.\n\nAgradecemos sua paciência.\n\nAtenciosamente,\nEquipe de Suporte`;
    } else if (selectedEmail.sentiment === 'positive') {
      reply = `Prezado(a) ${selectedEmail.from.name},\n\nAgradecemos muito seu feedback positivo! É muito gratificante saber que nosso atendimento foi satisfatório.\n\nEstamos sempre à disposição!\n\nAtenciosamente,\nEquipe Conecta PRO`;
    } else {
      reply = `Prezado(a) ${selectedEmail.from.name},\n\nAgradecemos seu contato. Em relação à sua solicitação, informamos que...\n\n[Completar resposta]\n\nAtenciosamente,\nEquipe Conecta PRO`;
    }

    setGeneratedReply(reply);
    setAiGenerating(false);
  }, [selectedEmail]);

  const handleToggleStar = useCallback((id: string) => {
    setEmails((prev) =>
      prev.map((e) => (e.id === id ? { ...e, starred: !e.starred } : e))
    );
  }, []);

  const handleMarkAsRead = useCallback((id: string) => {
    setEmails((prev) =>
      prev.map((e) => (e.id === id ? { ...e, read: true } : e))
    );
  }, []);

  const handleDelete = useCallback((id: string) => {
    setEmails((prev) =>
      prev.map((e) => (e.id === id ? { ...e, category: 'trash' as const } : e))
    );
  }, []);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <Mail className="w-8 h-8 text-accent-primary" />
              Assistente de Email
            </h1>
            <p className="text-text-secondary mt-1">
              Gestão inteligente de emails com respostas automáticas por IA
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Settings className="w-4 h-4" />}>
              Configurações
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setComposeOpen(true)}
            >
              Novo Email
            </Button>
          </div>
        </div>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Não Lidos"
              value={stats.unread}
              icon={<Inbox className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Favoritos"
              value={stats.starred}
              icon={<Star className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Alta Prioridade"
              value={stats.highPriority}
              icon={<AlertCircle className="w-6 h-6" />}
              iconColor="danger"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Recebidos Hoje"
              value={stats.todayReceived}
              icon={<Calendar className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
        </StatGrid>

        {/* Main Content */}
        <div className="flex gap-6 h-[calc(100vh-340px)]">
          {/* Sidebar */}
          <div className="w-56 space-y-2">
            <Button
              variant="primary"
              className="w-full"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setComposeOpen(true)}
            >
              Compor
            </Button>

            <div className="mt-4 space-y-1">
              {[
                { id: 'inbox', label: 'Caixa de Entrada', icon: Inbox, count: stats.unread },
                { id: 'starred', label: 'Favoritos', icon: Star, count: stats.starred },
                { id: 'sent', label: 'Enviados', icon: Send, count: 0 },
                { id: 'draft', label: 'Rascunhos', icon: FileText, count: 0 },
                { id: 'trash', label: 'Lixeira', icon: Trash2, count: 0 },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'bg-accent-primary/10 text-accent-primary'
                      : 'hover:bg-bg-tertiary text-text-secondary'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-4 h-4" />
                    <span className="text-sm">{item.label}</span>
                  </div>
                  {item.count > 0 && (
                    <Badge variant="secondary" size="sm">
                      {item.count}
                    </Badge>
                  )}
                </button>
              ))}
            </div>

            <div className="pt-4 border-t border-border mt-4">
              <p className="text-xs text-text-muted px-3 mb-2">Labels</p>
              {['cliente', 'fornecedor', 'urgente', 'suporte'].map((label) => (
                <button
                  key={label}
                  className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-bg-tertiary text-text-secondary text-sm"
                >
                  <div className="w-3 h-3 rounded-full bg-accent-primary" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Email List */}
          <Card className="flex-1 overflow-hidden">
            <div className="p-4 border-b border-border">
              <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                  <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                  <Input
                    placeholder="Buscar emails..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Button variant="secondary" leftIcon={<Filter className="w-4 h-4" />}>
                  Filtros
                </Button>
                <Button variant="secondary" leftIcon={<RefreshCw className="w-4 h-4" />}>
                  Atualizar
                </Button>
              </div>
            </div>

            <div className="overflow-y-auto h-full">
              {filteredEmails.length === 0 ? (
                <div className="p-8">
                  <EmptyState
                    icon={<Mail className="w-12 h-12" />}
                    title="Nenhum email"
                    description="Não há emails nesta pasta"
                  />
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {filteredEmails.map((email) => (
                    <div
                      key={email.id}
                      onClick={() => {
                        setSelectedEmail(email);
                        handleMarkAsRead(email.id);
                      }}
                      className={`p-4 cursor-pointer hover:bg-bg-tertiary/50 transition-colors ${
                        !email.read ? 'bg-accent-primary/5' : ''
                      } ${selectedEmail?.id === email.id ? 'bg-bg-tertiary' : ''}`}
                    >
                      <div className="flex items-start gap-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleStar(email.id);
                          }}
                          className="mt-1"
                        >
                          <Star
                            className={`w-4 h-4 ${
                              email.starred
                                ? 'fill-yellow-400 text-yellow-400'
                                : 'text-text-muted hover:text-yellow-400'
                            }`}
                          />
                        </button>
                        <Avatar name={email.from.name} size="sm" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className={`text-sm ${!email.read ? 'font-semibold text-text-primary' : 'text-text-secondary'}`}>
                                {email.from.name}
                              </span>
                              {email.priority && (
                                <Badge variant={priorityConfig[email.priority].color} size="sm">
                                  {priorityConfig[email.priority].label}
                                </Badge>
                              )}
                              {email.sentiment && (
                                <span className="text-sm">
                                  {sentimentConfig[email.sentiment].icon}
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-text-muted">
                              {new Date(email.timestamp).toLocaleTimeString('pt-BR', {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          </div>
                          <p className={`text-sm truncate ${!email.read ? 'font-medium text-text-primary' : 'text-text-secondary'}`}>
                            {email.subject}
                          </p>
                          <p className="text-xs text-text-muted truncate mt-1">
                            {email.preview}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            {email.hasAttachment && (
                              <Paperclip className="w-3 h-3 text-text-muted" />
                            )}
                            {email.labels.map((label) => (
                              <Badge key={label} variant="secondary" size="sm">
                                {label}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {/* Email Detail */}
          {selectedEmail && (
            <Card className="w-[500px] flex flex-col overflow-hidden">
              <div className="p-4 border-b border-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={() => setReplyOpen(true)}>
                      <Reply className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Forward className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Archive className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(selectedEmail.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                  <Dropdown
                    trigger={
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    }
                    items={[
                      { label: 'Marcar como não lido', icon: <Mail className="w-4 h-4" /> },
                      { label: 'Adicionar label', icon: <Tag className="w-4 h-4" /> },
                      { label: 'Mover para', icon: <Archive className="w-4 h-4" /> },
                    ]}
                  />
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4">
                <h2 className="text-lg font-medium text-text-primary mb-4">
                  {selectedEmail.subject}
                </h2>

                <div className="flex items-start gap-3 mb-4">
                  <Avatar name={selectedEmail.from.name} />
                  <div>
                    <p className="font-medium text-text-primary">{selectedEmail.from.name}</p>
                    <p className="text-sm text-text-muted">{selectedEmail.from.email}</p>
                    <p className="text-xs text-text-muted mt-1">
                      {new Date(selectedEmail.timestamp).toLocaleString('pt-BR')}
                    </p>
                  </div>
                </div>

                <div className="prose prose-invert max-w-none mb-6">
                  <p className="whitespace-pre-wrap text-text-secondary">
                    {selectedEmail.body}
                  </p>
                </div>

                {/* AI Suggestion */}
                {selectedEmail.aiSuggestion && (
                  <div className="p-4 bg-accent-primary/10 rounded-lg border border-accent-primary/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Bot className="w-5 h-5 text-accent-primary" />
                      <span className="font-medium text-accent-primary">Sugestão IA</span>
                    </div>
                    <p className="text-sm text-text-secondary">{selectedEmail.aiSuggestion}</p>
                    <div className="flex gap-2 mt-3">
                      <Button
                        variant="primary"
                        size="sm"
                        leftIcon={<Sparkles className="w-4 h-4" />}
                        onClick={() => {
                          setReplyOpen(true);
                          handleGenerateReply();
                        }}
                      >
                        Gerar Resposta com IA
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Compose Modal */}
      <Modal
        isOpen={composeOpen}
        onClose={() => setComposeOpen(false)}
        title="Novo Email"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-text-primary">Para</label>
            <Input placeholder="email@exemplo.com" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Assunto</label>
            <Input placeholder="Assunto do email" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Mensagem</label>
            <textarea
              className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary min-h-[200px]"
              placeholder="Digite sua mensagem..."
            />
          </div>
          <div className="flex items-center justify-between pt-4">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm">
                <Paperclip className="w-4 h-4" />
              </Button>
              <Dropdown
                trigger={
                  <Button variant="ghost" size="sm">
                    <FileText className="w-4 h-4 mr-1" />
                    Templates
                  </Button>
                }
                items={mockTemplates.map((t) => ({
                  label: t.name,
                  description: t.category,
                }))}
              />
            </div>
            <div className="flex items-center gap-2">
              <Button variant="secondary" onClick={() => setComposeOpen(false)}>
                Cancelar
              </Button>
              <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
                Enviar
              </Button>
            </div>
          </div>
        </div>
      </Modal>

      {/* Reply Modal */}
      <Modal
        isOpen={replyOpen}
        onClose={() => {
          setReplyOpen(false);
          setGeneratedReply('');
        }}
        title={`Responder: ${selectedEmail?.subject || ''}`}
        size="lg"
      >
        <div className="space-y-4">
          <div className="p-3 bg-bg-tertiary rounded-lg">
            <p className="text-sm text-text-muted">
              Para: {selectedEmail?.from.email}
            </p>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-text-primary">Mensagem</label>
              <Button
                variant="secondary"
                size="sm"
                leftIcon={<Sparkles className={`w-4 h-4 ${aiGenerating ? 'animate-spin' : ''}`} />}
                onClick={handleGenerateReply}
                disabled={aiGenerating}
              >
                {aiGenerating ? 'Gerando...' : 'Gerar com IA'}
              </Button>
            </div>
            <textarea
              className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary min-h-[200px]"
              placeholder="Digite sua resposta..."
              value={generatedReply}
              onChange={(e) => setGeneratedReply(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setReplyOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary" leftIcon={<Send className="w-4 h-4" />}>
              Enviar Resposta
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}

export default EmailAssistantPage;
