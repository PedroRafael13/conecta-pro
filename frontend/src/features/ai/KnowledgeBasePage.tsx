'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpen,
  Search,
  Plus,
  Edit,
  Trash2,
  Eye,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Tag,
  Folder,
  Clock,
  User,
  Star,
  Download,
  Upload,
  Filter,
  MoreVertical,
  ChevronRight,
  Sparkles,
  FileText,
  HelpCircle,
  Lightbulb,
  Target,
  TrendingUp,
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
  EmptyState,
} from '@/design-system/components';

// Types
interface Article {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  author: string;
  createdAt: string;
  updatedAt: string;
  views: number;
  likes: number;
  dislikes: number;
  status: 'published' | 'draft' | 'archived';
}

interface Category {
  id: string;
  name: string;
  icon: string;
  count: number;
  color: string;
}

interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
  views: number;
  helpful: number;
}

// Mock Data
const mockArticles: Article[] = [
  {
    id: '1',
    title: 'Como cadastrar um novo funcionário',
    content: 'Este artigo explica o processo completo de cadastro de funcionários...',
    category: 'RH',
    tags: ['cadastro', 'funcionário', 'onboarding'],
    author: 'Admin',
    createdAt: '2026-01-10T10:00:00',
    updatedAt: '2026-01-15T14:30:00',
    views: 1245,
    likes: 89,
    dislikes: 5,
    status: 'published',
  },
  {
    id: '2',
    title: 'Processo de aprovação de despesas',
    content: 'Guia completo sobre o fluxo de aprovação de despesas...',
    category: 'Financeiro',
    tags: ['despesas', 'aprovação', 'fluxo'],
    author: 'Admin',
    createdAt: '2026-01-08T09:00:00',
    updatedAt: '2026-01-14T11:00:00',
    views: 892,
    likes: 67,
    dislikes: 3,
    status: 'published',
  },
  {
    id: '3',
    title: 'Configurando integrações de hardware',
    content: 'Tutorial de configuração de equipamentos...',
    category: 'Integrações',
    tags: ['hardware', 'configuração', 'equipamentos'],
    author: 'Suporte',
    createdAt: '2026-01-05T14:00:00',
    updatedAt: '2026-01-12T16:00:00',
    views: 567,
    likes: 45,
    dislikes: 2,
    status: 'published',
  },
  {
    id: '4',
    title: 'Gerando relatórios personalizados',
    content: 'Como criar e exportar relatórios customizados...',
    category: 'Relatórios',
    tags: ['relatórios', 'exportação', 'dados'],
    author: 'Admin',
    createdAt: '2026-01-03T11:00:00',
    updatedAt: '2026-01-10T09:00:00',
    views: 723,
    likes: 56,
    dislikes: 4,
    status: 'published',
  },
];

const mockCategories: Category[] = [
  { id: '1', name: 'RH', icon: '👥', count: 24, color: '#6366f1' },
  { id: '2', name: 'Financeiro', icon: '💰', count: 18, color: '#10b981' },
  { id: '3', name: 'Operacional', icon: '⚙️', count: 32, color: '#f59e0b' },
  { id: '4', name: 'Integrações', icon: '🔗', count: 15, color: '#8b5cf6' },
  { id: '5', name: 'Relatórios', icon: '📊', count: 12, color: '#3b82f6' },
  { id: '6', name: 'Segurança', icon: '🔒', count: 8, color: '#ef4444' },
];

const mockFAQs: FAQ[] = [
  {
    id: '1',
    question: 'Como resetar minha senha?',
    answer: 'Clique em "Esqueci minha senha" na tela de login e siga as instruções...',
    category: 'Acesso',
    views: 2345,
    helpful: 456,
  },
  {
    id: '2',
    question: 'Como emitir uma nota fiscal?',
    answer: 'Acesse o módulo Fiscal, clique em "Nova NF" e preencha os dados...',
    category: 'Financeiro',
    views: 1890,
    helpful: 312,
  },
  {
    id: '3',
    question: 'Como cadastrar um novo cliente?',
    answer: 'No menu CRM, selecione "Clientes" e clique em "Novo Cliente"...',
    category: 'CRM',
    views: 1567,
    helpful: 234,
  },
  {
    id: '4',
    question: 'Como gerar relatório de ponto?',
    answer: 'Acesse RH > Ponto > Relatórios e selecione o período desejado...',
    category: 'RH',
    views: 1234,
    helpful: 198,
  },
];

const popularSearches = [
  'cadastro funcionário',
  'emitir nota fiscal',
  'relatório financeiro',
  'configurar equipamento',
  'resetar senha',
];

const statusConfig = {
  published: { label: 'Publicado', color: 'success' as const },
  draft: { label: 'Rascunho', color: 'warning' as const },
  archived: { label: 'Arquivado', color: 'secondary' as const },
};

export function KnowledgeBasePage() {
  const [articles, setArticles] = useState(mockArticles);
  const [faqs, setFaqs] = useState(mockFAQs);
  const [activeTab, setActiveTab] = useState('articles');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [articleModalOpen, setArticleModalOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null);

  const stats = {
    totalArticles: articles.length,
    totalViews: articles.reduce((sum, a) => sum + a.views, 0),
    totalLikes: articles.reduce((sum, a) => sum + a.likes, 0),
    categories: mockCategories.length,
  };

  const filteredArticles = articles.filter((article) => {
    const matchesSearch =
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = !selectedCategory || article.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const filteredFAQs = faqs.filter((faq) =>
    faq.question.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleViewArticle = useCallback((article: Article) => {
    setSelectedArticle(article);
    setArticleModalOpen(true);
  }, []);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-display font-bold text-text-primary flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-accent-primary" />
              Base de Conhecimento
            </h1>
            <p className="text-text-secondary mt-1">
              Documentação, tutoriais e FAQ com busca inteligente
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="secondary" leftIcon={<Upload className="w-4 h-4" />}>
              Importar
            </Button>
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={() => setCreateModalOpen(true)}
            >
              Novo Artigo
            </Button>
          </div>
        </div>

        {/* Search */}
        <Card>
          <CardBody>
            <div className="relative">
              <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" />
              <Input
                placeholder="Buscar artigos, tutoriais, FAQ..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 text-lg"
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <Badge variant="secondary" leftIcon={<Sparkles className="w-3 h-3" />}>
                  IA
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-3">
              <span className="text-sm text-text-muted">Populares:</span>
              {popularSearches.map((term) => (
                <button
                  key={term}
                  onClick={() => setSearchQuery(term)}
                  className="text-sm px-3 py-1 rounded-full bg-bg-tertiary hover:bg-accent-primary/10 text-text-muted hover:text-accent-primary transition-colors"
                >
                  {term}
                </button>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* Stats */}
        <StatGrid columns={4}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <StatCard
              title="Total de Artigos"
              value={stats.totalArticles}
              icon={<FileText className="w-6 h-6" />}
              iconColor="primary"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <StatCard
              title="Visualizações"
              value={stats.totalViews.toLocaleString()}
              icon={<Eye className="w-6 h-6" />}
              iconColor="info"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <StatCard
              title="Reações Positivas"
              value={stats.totalLikes}
              icon={<ThumbsUp className="w-6 h-6" />}
              iconColor="success"
            />
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <StatCard
              title="Categorias"
              value={stats.categories}
              icon={<Folder className="w-6 h-6" />}
              iconColor="warning"
            />
          </motion.div>
        </StatGrid>

        {/* Tabs */}
        <Tabs value={activeTab} onChange={setActiveTab}>
          <Tab value="articles" label="Artigos" />
          <Tab value="faq" label="FAQ" />
          <Tab value="categories" label="Categorias" />
          <Tab value="analytics" label="Analytics" />
        </Tabs>

        {activeTab === 'articles' && (
          <div className="grid grid-cols-4 gap-6">
            {/* Categories Sidebar */}
            <div className="col-span-1 space-y-4">
              <Card>
                <CardHeader title="Categorias" />
                <CardBody className="p-2">
                  <div className="space-y-1">
                    <button
                      onClick={() => setSelectedCategory(null)}
                      className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                        !selectedCategory ? 'bg-accent-primary/10 text-accent-primary' : 'hover:bg-bg-tertiary'
                      }`}
                    >
                      <span className="text-sm">Todas</span>
                      <span className="text-xs text-text-muted">{articles.length}</span>
                    </button>
                    {mockCategories.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.name)}
                        className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                          selectedCategory === category.name
                            ? 'bg-accent-primary/10 text-accent-primary'
                            : 'hover:bg-bg-tertiary'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span>{category.icon}</span>
                          <span className="text-sm">{category.name}</span>
                        </div>
                        <span className="text-xs text-text-muted">{category.count}</span>
                      </button>
                    ))}
                  </div>
                </CardBody>
              </Card>
            </div>

            {/* Articles List */}
            <div className="col-span-3 space-y-4">
              {filteredArticles.length === 0 ? (
                <EmptyState
                  icon={<FileText className="w-12 h-12" />}
                  title="Nenhum artigo encontrado"
                  description="Tente buscar por outros termos"
                />
              ) : (
                filteredArticles.map((article) => (
                  <Card key={article.id} className="hover:border-accent-primary/50 transition-colors">
                    <CardBody>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant="secondary">{article.category}</Badge>
                            <Badge variant={statusConfig[article.status].color}>
                              {statusConfig[article.status].label}
                            </Badge>
                          </div>
                          <h3
                            className="font-medium text-text-primary hover:text-accent-primary cursor-pointer"
                            onClick={() => handleViewArticle(article)}
                          >
                            {article.title}
                          </h3>
                          <p className="text-sm text-text-muted mt-1 line-clamp-2">
                            {article.content}
                          </p>
                          <div className="flex items-center gap-4 mt-3">
                            {article.tags.map((tag) => (
                              <span key={tag} className="text-xs text-text-muted">
                                #{tag}
                              </span>
                            ))}
                          </div>
                          <div className="flex items-center gap-4 mt-3 text-xs text-text-muted">
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {article.views}
                            </span>
                            <span className="flex items-center gap-1">
                              <ThumbsUp className="w-3 h-3" />
                              {article.likes}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(article.updatedAt).toLocaleDateString('pt-BR')}
                            </span>
                            <span className="flex items-center gap-1">
                              <User className="w-3 h-3" />
                              {article.author}
                            </span>
                          </div>
                        </div>
                        <Dropdown
                          trigger={
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="w-4 h-4" />
                            </Button>
                          }
                          items={[
                            { label: 'Editar', icon: <Edit className="w-4 h-4" /> },
                            { label: 'Duplicar', icon: <FileText className="w-4 h-4" /> },
                            { label: 'Arquivar', icon: <Folder className="w-4 h-4" /> },
                            { label: 'Excluir', icon: <Trash2 className="w-4 h-4" /> },
                          ]}
                        />
                      </div>
                    </CardBody>
                  </Card>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'faq' && (
          <Card>
            <CardHeader
              title="Perguntas Frequentes"
              subtitle={`${filteredFAQs.length} perguntas`}
              action={
                <Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                  Nova Pergunta
                </Button>
              }
            />
            <CardBody>
              <div className="space-y-2">
                {filteredFAQs.map((faq) => (
                  <div
                    key={faq.id}
                    className="border border-border rounded-lg overflow-hidden"
                  >
                    <button
                      onClick={() => setExpandedFAQ(expandedFAQ === faq.id ? null : faq.id)}
                      className="w-full flex items-center justify-between p-4 hover:bg-bg-tertiary transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <HelpCircle className="w-5 h-5 text-accent-primary" />
                        <span className="font-medium text-text-primary">{faq.question}</span>
                      </div>
                      <ChevronRight
                        className={`w-5 h-5 text-text-muted transition-transform ${
                          expandedFAQ === faq.id ? 'rotate-90' : ''
                        }`}
                      />
                    </button>
                    {expandedFAQ === faq.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="px-4 pb-4"
                      >
                        <div className="pl-8">
                          <p className="text-text-secondary">{faq.answer}</p>
                          <div className="flex items-center gap-4 mt-4">
                            <span className="text-xs text-text-muted">Esta resposta foi útil?</span>
                            <button className="flex items-center gap-1 text-xs text-text-muted hover:text-green-500">
                              <ThumbsUp className="w-4 h-4" />
                              {faq.helpful}
                            </button>
                            <button className="flex items-center gap-1 text-xs text-text-muted hover:text-red-500">
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                ))}
              </div>
            </CardBody>
          </Card>
        )}

        {activeTab === 'categories' && (
          <div className="grid grid-cols-3 gap-6">
            {mockCategories.map((category) => (
              <Card key={category.id} className="hover:border-accent-primary/50 transition-colors cursor-pointer">
                <CardBody>
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-4xl">{category.icon}</div>
                    <Badge variant="secondary">{category.count} artigos</Badge>
                  </div>
                  <h3 className="font-medium text-text-primary text-lg">{category.name}</h3>
                  <div className="mt-4">
                    <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${(category.count / 32) * 100}%`,
                          backgroundColor: category.color,
                        }}
                      />
                    </div>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Artigos Mais Visualizados" />
              <CardBody>
                <div className="space-y-4">
                  {articles
                    .sort((a, b) => b.views - a.views)
                    .slice(0, 5)
                    .map((article, idx) => (
                      <div key={article.id} className="flex items-center gap-4">
                        <span className="text-2xl font-bold text-text-muted">{idx + 1}</span>
                        <div className="flex-1">
                          <p className="font-medium text-text-primary">{article.title}</p>
                          <p className="text-sm text-text-muted">{article.views.toLocaleString()} visualizações</p>
                        </div>
                        <TrendingUp className="w-5 h-5 text-green-500" />
                      </div>
                    ))}
                </div>
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Buscas Recentes" />
              <CardBody>
                <div className="space-y-3">
                  {[
                    { term: 'como cadastrar funcionário', count: 45 },
                    { term: 'emitir nota fiscal', count: 38 },
                    { term: 'relatório financeiro', count: 32 },
                    { term: 'configurar equipamento', count: 28 },
                    { term: 'alterar senha', count: 25 },
                  ].map((search, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                      <div className="flex items-center gap-3">
                        <Search className="w-4 h-4 text-text-muted" />
                        <span className="text-sm text-text-primary">{search.term}</span>
                      </div>
                      <span className="text-xs text-text-muted">{search.count} buscas</span>
                    </div>
                  ))}
                </div>
              </CardBody>
            </Card>
          </div>
        )}
      </div>

      {/* Article Modal */}
      <Modal
        isOpen={articleModalOpen}
        onClose={() => setArticleModalOpen(false)}
        title={selectedArticle?.title || ''}
        size="lg"
      >
        {selectedArticle && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <Badge variant="secondary">{selectedArticle.category}</Badge>
              {selectedArticle.tags.map((tag) => (
                <span key={tag} className="text-sm text-text-muted">#{tag}</span>
              ))}
            </div>
            <div className="prose prose-invert max-w-none">
              <p className="text-text-secondary">{selectedArticle.content}</p>
            </div>
            <div className="flex items-center justify-between pt-4 border-t border-border">
              <div className="flex items-center gap-4 text-sm text-text-muted">
                <span>Por {selectedArticle.author}</span>
                <span>•</span>
                <span>Atualizado em {new Date(selectedArticle.updatedAt).toLocaleDateString('pt-BR')}</span>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" leftIcon={<ThumbsUp className="w-4 h-4" />}>
                  {selectedArticle.likes}
                </Button>
                <Button variant="ghost" size="sm" leftIcon={<ThumbsDown className="w-4 h-4" />}>
                  {selectedArticle.dislikes}
                </Button>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Create Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Novo Artigo"
        size="lg"
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-text-primary">Título</label>
            <Input placeholder="Digite o título do artigo" className="mt-1" />
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Categoria</label>
            <select className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary">
              {mockCategories.map((cat) => (
                <option key={cat.id} value={cat.name}>{cat.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Conteúdo</label>
            <textarea
              className="w-full mt-1 px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary min-h-[200px]"
              placeholder="Digite o conteúdo do artigo..."
            />
          </div>
          <div>
            <label className="text-sm font-medium text-text-primary">Tags (separadas por vírgula)</label>
            <Input placeholder="tag1, tag2, tag3" className="mt-1" />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setCreateModalOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary" leftIcon={<Sparkles className="w-4 h-4" />}>
              Publicar
            </Button>
          </div>
        </div>
      </Modal>
    </MainLayout>
  );
}

export default KnowledgeBasePage;
